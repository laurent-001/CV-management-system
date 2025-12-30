from django import forms
from django.contrib.auth.models import User
from .models import Applicant, CVApplication, JobPosition

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm password')

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

class ApplicantProfileForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ('phone_number',)

class CVApplicationForm(forms.ModelForm):
    class Meta:
        model = CVApplication
        fields = ('skills', 'work_experience', 'cv_file')
        widgets = {
            'job_position': forms.HiddenInput(),
        }

    def clean_cv_file(self):
        cv_file = self.cleaned_data.get('cv_file', False)
        if cv_file:
            if not cv_file.name.endswith('.pdf') and not cv_file.name.endswith('.doc') and not cv_file.name.endswith('.docx'):
                raise forms.ValidationError("Only PDF, DOC, and DOCX files are allowed.")
        return cv_file


class JobPositionForm(forms.ModelForm):
    class Meta:
        model = JobPosition
        fields = ('title', 'description', 'location')

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = CVApplication
        fields = ('status',)
