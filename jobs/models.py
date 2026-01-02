from django.contrib.auth.models import User
from django.db import models


class CompanyInfo(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="company/")
    banner_image = models.ImageField(upload_to="company/", null=True, blank=True)
    facebook_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    ROLE_CHOICES = (("POSTER", "Job Poster"), ("APPLICANT", "Job Applicant"))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to="profiles/", default="profiles/default.png", null=True, blank=True
    )
    cv = models.FileField(upload_to="cvs/", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class JobPosition(models.Model):
    JOB_TYPE_CHOICES = (
        ("Full-time", "Full-time"),
        ("Part-time", "Part-time"),
        ("Internship", "Internship"),
    )
    STATUS_CHOICES = (
        ("Open", "Open"),
        ("Closed", "Closed"),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.TextField()
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    application_deadline = models.DateField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class JobApplication(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Interview", "Interview"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    )
    job = models.ForeignKey(JobPosition, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    skills = models.TextField()
    work_experience = models.TextField()
    education = models.TextField()
    cv_file = models.FileField(upload_to="cvs/")
    additional_documents = models.FileField(
        upload_to="documents/", null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    feedback = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.job.title}"


class Notification(models.Model):
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}"
