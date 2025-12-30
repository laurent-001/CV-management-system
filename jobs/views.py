from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail
from .models import JobPosition, Applicant, CVApplication
from .forms import (
    UserRegistrationForm,
    ApplicantProfileForm,
    CVApplicationForm,
    ApplicationStatusForm,
    JobPositionForm
)
from django.contrib.auth.models import User

# Home view
def home_view(request):
    """Displays the company introduction/home page."""
    return render(request, 'jobs/home.html')

# Job list view
def job_list_view(request):
    """Lists all available job positions."""
    jobs = JobPosition.objects.all().order_by('-created_at')
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

# User registration view
def register_view(request):
    """Handles user registration."""
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ApplicantProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            applicant = profile_form.save(commit=False)
            applicant.user = user
            applicant.save()

            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        user_form = UserRegistrationForm()
        profile_form = ApplicantProfileForm()
    return render(request, 'jobs/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

# User login view
def login_view(request):
    """Handles user login."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('hr_dashboard')
                return redirect('applicant_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'jobs/login.html', {'form': form})

# User logout view
def logout_view(request):
    """Handles user logout."""
    logout(request)
    return redirect('home')

# CV submission view
@login_required
def submit_cv_view(request, job_id):
    """Allows an applicant to submit their CV for a job."""
    job = get_object_or_404(JobPosition, id=job_id)
    applicant, created = Applicant.objects.get_or_create(user=request.user)

    if CVApplication.objects.filter(applicant=applicant, job_position=job).exists():
        messages.warning(request, 'You have already applied for this position.')
        return redirect('job_list')

    if request.method == 'POST':
        form = CVApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = applicant
            application.job_position = job
            application.save()
            messages.success(request, 'Your application has been submitted successfully.')
            return redirect('applicant_dashboard')
    else:
        form = CVApplicationForm()
    return render(request, 'jobs/submit_cv.html', {'form': form, 'job': job})

# Applicant dashboard view
@login_required
def applicant_dashboard_view(request):
    """Displays the applications submitted by the logged-in applicant."""
    applicant = get_object_or_404(Applicant, user=request.user)
    applications = CVApplication.objects.filter(applicant=applicant).order_by('-submitted_at')
    return render(request, 'jobs/applicant_dashboard.html', {'applications': applications})


# Helper for checking if a user is staff
def is_staff(user):
    return user.is_staff

# HR dashboard view
@user_passes_test(is_staff)
@login_required
def hr_dashboard_view(request):
    """Displays all CV applications for HR staff."""
    applications = CVApplication.objects.all().order_by('-submitted_at')
    return render(request, 'jobs/hr_dashboard.html', {'applications': applications})

# Update application status view
@user_passes_test(is_staff)
@login_required
def update_application_status_view(request, application_id):
    """Allows HR to update the status of a CV application and notify the applicant."""
    application = get_object_or_404(CVApplication, id=application_id)
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            original_status = application.status
            updated_application = form.save()

            # Send email notification if status changes to 'Interview' or 'Rejected'
            if updated_application.status != original_status and updated_application.status in ['Interview', 'Rejected']:
                subject = f'Update on your application for {application.job_position.title}'
                message = (
                    f'Dear {application.applicant.user.username},\n\n'
                    f'The status of your application for the position of {application.job_position.title} '
                    f'has been updated to: {updated_application.status}.\n\n'
                    f'Thank you for your interest in our company.\n\n'
                    f'Best regards,\n'
                    f'The HR Team'
                )
                from_email = 'hr@recruitmentportal.com' # Sender email
                to_email = [application.applicant.user.email] # Recipient email

                # The console email backend will print the email to the console.
                send_mail(subject, message, from_email, to_email)

            messages.success(request, 'Application status updated successfully.')
            return redirect('hr_dashboard')
    else:
        form = ApplicationStatusForm(instance=application)
    return render(request, 'jobs/update_status.html', {'form': form, 'application': application})
