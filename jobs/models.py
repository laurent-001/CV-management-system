from django.db import models
from django.contrib.auth.models import User

class CompanyInfo(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company/')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class JobPosition(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Applicant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def __str__(self):
        return self.user.username

class CVApplication(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Interview', 'Interview'),
        ('Rejected', 'Rejected'),
    )

    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    job_position = models.ForeignKey(JobPosition, on_delete=models.CASCADE)
    skills = models.TextField()
    work_experience = models.TextField()
    cv_file = models.FileField(upload_to='cvs/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.applicant.user.username} - {self.job_position.title}'
