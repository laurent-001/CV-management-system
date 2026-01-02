from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    ApplicationStatusForm,
    JobApplicationForm,
    JobForm,
    UserRegistrationForm,
)
from .models import CompanyInfo, JobApplication, JobPosition, Profile


# Permission helpers
def is_poster(user):
    return user.is_authenticated and hasattr(user, "profile") and user.profile.role == "POSTER"


def is_applicant(user):
    return (
        user.is_authenticated and hasattr(user, "profile") and user.profile.role == "APPLICANT"
    )


# Home view
def home_view(request):
    company_info = CompanyInfo.objects.first()
    latest_jobs = JobPosition.objects.all().order_by("-created_at")[:5]
    return render(
        request,
        "jobs/home.html",
        {"company_info": company_info, "latest_jobs": latest_jobs},
    )


# Job list view
def job_list_view(request):
    jobs = JobPosition.objects.all().order_by("-created_at")
    return render(request, "jobs/job_list.html", {"jobs": jobs})


# User registration view
def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            Profile.objects.create(user=user, role=form.cleaned_data["role"])
            messages.success(request, "Registration successful. You can now log in.")
            return redirect("login")
    else:
        form = UserRegistrationForm()
    return render(request, "jobs/register.html", {"form": form})


# User login view
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if is_poster(user):
                    return redirect("employer_dashboard")
                return redirect("applicant_dashboard")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "jobs/login.html", {"form": form})


# User logout view
def logout_view(request):
    logout(request)
    return redirect("home")


# Job application view (replaces submit_cv_view)
@user_passes_test(is_applicant)
def apply_for_job_view(request, job_id):
    job = get_object_or_404(JobPosition, id=job_id)
    if JobApplication.objects.filter(applicant=request.user, job=job).exists():
        messages.warning(request, "You have already applied for this position.")
        return redirect("job_list")
    if request.method == "POST":
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.job = job
            application.save()
            messages.success(request, "Your application has been submitted successfully.")
            return redirect("applicant_dashboard")
    else:
        form = JobApplicationForm()
    return render(request, "jobs/apply_job.html", {"form": form, "job": job})


# Applicant dashboard view
@user_passes_test(is_applicant)
def applicant_dashboard_view(request):
    applications = JobApplication.objects.filter(applicant=request.user).order_by(
        "-submitted_at"
    )
    company_info = CompanyInfo.objects.first()
    return render(
        request,
        "jobs/applicant_dashboard.html",
        {"applications": applications, "company_info": company_info},
    )


# Employer dashboard view
@user_passes_test(is_poster)
def employer_dashboard_view(request):
    jobs = JobPosition.objects.filter(posted_by=request.user).order_by("-created_at")
    return render(request, "jobs/employer_dashboard.html", {"jobs": jobs})


# Job creation view
@user_passes_test(is_poster)
def create_job_view(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, "Job posted successfully.")
            return redirect("employer_dashboard")
    else:
        form = JobForm()
    return render(request, "jobs/post_job.html", {"form": form})


# Job edit view
@user_passes_test(is_poster)
def edit_job_view(request, job_id):
    job = get_object_or_404(JobPosition, id=job_id, posted_by=request.user)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully.")
            return redirect("employer_dashboard")
    else:
        form = JobForm(instance=job)
    return render(request, "jobs/edit_job.html", {"form": form})


# Job delete view
@user_passes_test(is_poster)
def delete_job_view(request, job_id):
    job = get_object_or_404(JobPosition, id=job_id, posted_by=request.user)
    if request.method == "POST":
        job.delete()
        messages.success(request, "Job deleted successfully.")
        return redirect("employer_dashboard")
    return render(request, "jobs/confirm_delete_job.html", {"job": job})


# View applicants for a job
@user_passes_test(is_poster)
def view_applicants_view(request, job_id):
    job = get_object_or_404(JobPosition, id=job_id, posted_by=request.user)
    applications = JobApplication.objects.filter(job=job).order_by("-submitted_at")
    return render(
        request,
        "jobs/view_applicants.html",
        {"job": job, "applications": applications},
    )


# Update application status view
@user_passes_test(is_poster)
def update_application_status_view(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    # Ensure the poster owns the job associated with the application
    if application.job.posted_by != request.user:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect("employer_dashboard")
    if request.method == "POST":
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            original_status = application.status
            updated_application = form.save()
            if (
                updated_application.status != original_status
                and updated_application.status in ["Interview", "Rejected"]
            ):
                subject = f"Update on your application for {application.job.title}"
                message = f"Dear {application.applicant.username},\n\nThe status of your application for the position of {application.job.title} has been updated to: {updated_application.status}.\n\nThank you for your interest in our company.\n\nBest regards,\nThe HR Team"
                from_email = "hr@recruitmentportal.com"
                to_email = [application.applicant.email]
                send_mail(subject, message, from_email, to_email)
            messages.success(request, "Application status updated successfully.")
            return redirect("view_applicants", job_id=application.job.id)
    else:
        form = ApplicationStatusForm(instance=application)
    return render(
        request, "jobs/update_status.html", {"form": form, "application": application}
    )
