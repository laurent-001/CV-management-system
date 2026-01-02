from django import forms
from django.contrib.auth.models import User
from .models import JobApplication, JobPosition, Profile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm password")
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        widget=forms.RadioSelect,
        label="I want to:",
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError("Passwords don't match.")
        return cd["password2"]

class JobForm(forms.ModelForm):
    class Meta:
        model = JobPosition
        fields = [
            "title",
            "description",
            "required_skills",
            "location",
            "job_type",
            "application_deadline",
            "status",
        ]
        widgets = {
            "application_deadline": forms.DateInput(attrs={"type": "date"}),
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            "full_name",
            "email",
            "phone_number",
            "skills",
            "work_experience",
            "education",
            "cv_file",
            "additional_documents",
        ]

    def clean_cv_file(self):
        cv_file = self.cleaned_data.get("cv_file", False)
        if cv_file and not cv_file.name.lower().endswith((".pdf", ".doc", ".docx")):
            raise forms.ValidationError("Only PDF, DOC, and DOCX files are allowed.")
        return cv_file

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ("status",)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio", "profile_picture", "cv")

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ("feedback",)
