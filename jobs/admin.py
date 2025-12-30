from django.contrib import admin
from .models import JobPosition, Applicant, CVApplication

admin.site.register(JobPosition)
admin.site.register(Applicant)
admin.site.register(CVApplication)
