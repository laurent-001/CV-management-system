from django.contrib import admin
from .models import CompanyInfo, JobPosition, Applicant, CVApplication

admin.site.register(CompanyInfo)
admin.site.register(JobPosition)
admin.site.register(Applicant)
admin.site.register(CVApplication)
