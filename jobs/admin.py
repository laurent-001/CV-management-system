from django.contrib import admin
from .models import CompanyInfo, JobPosition, Profile, JobApplication

class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'logo', 'banner_image')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'linkedin_url', 'twitter_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(CompanyInfo, CompanyInfoAdmin)
admin.site.register(JobPosition)
admin.site.register(Profile)
admin.site.register(JobApplication)
