from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import (
    ApplicationStatusForm,
    FeedbackForm,
    JobApplicationForm,
    JobForm,
    ProfileForm,
    ProfileImageForm,
    UserRegistrationForm,
)
from .models import JobApplication, JobPosition, Notification, Profile


# Permission helpers
def is_poster(user):
    return user.is_authenticated and hasattr(user, "profile") and user.profile.role == "POSTER"


def is_applicant(user):
    return (
        user.is_authenticated and hasattr(user, "profile") and user.profile.role == "APPLICANT"
    )


# Home view
def home_view(request):
    latest_jobs = JobPosition.objects.filter(status="Open").order_by("-created_at")[:5]
    return render(
        request,
        "jobs/home.html",
        {"latest_jobs": latest_jobs},
    )


# Job list view
def job_list_view(request):
    jobs = JobPosition.objects.filter(status="Open").order_by("-created_at")
    return render(request, "jobs/job_list.html", {"jobs": jobs})

# Job detail view
def job_detail_view(request, job_id):
    job = get_object_or_404(JobPosition, id=job_id)
    return render(request, "jobs/job_detail.html", {"job": job})


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


# Job application view
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
    applications = JobApplication.objects.filter(
        applicant=request.user, is_active=True
    ).order_by("-submitted_at")
    total_applications = applications.count()
    interviews_scheduled = applications.filter(status="Interview").count()
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    return render(
        request,
        "jobs/applicant_dashboard.html",
        {
            "applications": applications,
            "total_applications": total_applications,
            "interviews_scheduled": interviews_scheduled,
            "notifications": notifications,
        },
    )


# Employer dashboard view
@user_passes_test(is_poster)
def employer_dashboard_view(request):
    jobs = JobPosition.objects.filter(posted_by=request.user).order_by("-created_at")
    total_jobs = jobs.count()
    total_applications = JobApplication.objects.filter(job__in=jobs).count()
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    new_applications = JobApplication.objects.filter(
        job__in=jobs, submitted_at__gte=seven_days_ago
    ).count()
    return render(
        request,
        "jobs/employer_dashboard.html",
        {
            "jobs": jobs,
            "total_jobs": total_jobs,
            "total_applications": total_applications,
            "new_applications": new_applications,
        },
    )


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
    if application.job.posted_by != request.user:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect("employer_dashboard")
    if request.method == "POST":
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save()
            Notification.objects.create(
                recipient=application.applicant,
                message=f"The status of your application for {application.job.title} has been updated to {application.status}.",
            )
            messages.success(request, "Application status updated successfully.")
            return redirect("view_applicants", job_id=application.job.id)
    else:
        form = ApplicationStatusForm(instance=application)
    return render(
        request, "jobs/update_status.html", {"form": form, "application": application}
    )


# Provide feedback to applicant
@user_passes_test(is_poster)
def provide_feedback_view(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    if application.job.posted_by != request.user:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect("employer_dashboard")
    if request.method == "POST":
        form = FeedbackForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            Notification.objects.create(
                recipient=application.applicant,
                message=f"You have received feedback on your application for {application.job.title}.",
            )
            messages.success(request, "Feedback submitted successfully.")
            return redirect("view_applicants", job_id=application.job.id)
    else:
        form = FeedbackForm(instance=application)
    return render(
        request, "jobs/provide_feedback.html", {"form": form, "application": application}
    )


from PIL import Image
from django.core.files.base import ContentFile
import io

# Applicant profile management
@login_required
def profile_image_upload_view(request):
    if request.method == "POST":
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            profile = form.save(commit=False)

            if 'profile_picture' in request.FILES:
                image = Image.open(request.FILES['profile_picture'])

                # Crop to a square
                width, height = image.size
                if width != height:
                    min_dim = min(width, height)
                    left = (width - min_dim) / 2
                    top = (height - min_dim) / 2
                    right = (width + min_dim) / 2
                    bottom = (height + min_dim) / 2
                    image = image.crop((left, top, right, bottom))

                # Resize to 300x300
                image = image.resize((300, 300), Image.LANCZOS)

                # Save the processed image
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                profile.profile_picture.save(request.FILES['profile_picture'].name, ContentFile(buffer.getvalue()))

            profile.save()
            return JsonResponse({"success": True, "profile_image_url": profile.profile_picture.url})
        else:
            return JsonResponse({"success": False, "errors": form.errors})
    return JsonResponse({"success": False, "errors": "Invalid request method"})


@login_required
def profile_image_remove_view(request):
    if request.method == "POST":
        profile = request.user.profile
        profile.profile_picture.delete(save=False)
        profile.profile_picture = None
        profile.save()

        # Get the URL of the default image
        from django.templatetags.static import static
        default_image_url = static('images/default-profile.svg')

        return JsonResponse({"success": True, "profile_image_url": default_image_url})
    return JsonResponse({"success": False, "errors": "Invalid request method"})


@user_passes_test(is_applicant)
def applicant_profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, "jobs/applicant_profile.html", {"profile": profile})

# View applicant profile (for employers)
@user_passes_test(is_poster)
def view_applicant_profile_view(request, applicant_id):
    profile = get_object_or_404(Profile, id=applicant_id)
    return render(request, "jobs/applicant_profile.html", {"profile": profile})


@user_passes_test(is_applicant)
def applicant_profile_edit_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("applicant_profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "jobs/applicant_profile_edit.html", {"form": form})


# Withdraw application
@user_passes_test(is_applicant)
def withdraw_application_view(request, application_id):
    application = get_object_or_404(
        JobApplication, id=application_id, applicant=request.user
    )
    if request.method == "POST":
        application.is_active = False
        application.save()
        messages.success(request, "Application withdrawn successfully.")
        return redirect("applicant_dashboard")
    return render(request, "jobs/confirm_withdraw.html", {"application": application})

# Error handler views
def custom_400_view(request, exception):
    """
    Custom view to handle 400 Bad Request errors.
    """
    return render(request, 'jobs/400.html', status=400)

def custom_403_view(request, exception):
    """
    Custom view to handle 403 Forbidden errors.
    """
    return render(request, 'jobs/403.html', status=403)

def custom_404_view(request, exception):
    """
    Custom view to handle 404 Page Not Found errors.
    """
    return render(request, 'jobs/404.html', status=404)

def custom_500_view(request):
    """
    Custom view to handle 500 Internal Server Error.
    """
    return render(request, 'jobs/500.html', status=500)
