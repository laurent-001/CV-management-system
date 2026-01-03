from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('jobs/', views.job_list_view, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail_view, name='job_detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('apply/<int:job_id>/', views.apply_for_job_view, name='apply_for_job'),

    # Applicant Dashboard
    path('dashboard/applicant/', views.applicant_dashboard_view, name='applicant_dashboard'),
    path('dashboard/applicant/profile/', views.applicant_profile_view, name='applicant_profile'),
    path('dashboard/applicant/profile/edit/', views.applicant_profile_edit_view, name='applicant_profile_edit'),
    path('dashboard/applicant/application/<int:application_id>/withdraw/', views.withdraw_application_view, name='withdraw_application'),

    # Employer Dashboard
    path('dashboard/employer/', views.employer_dashboard_view, name='employer_dashboard'),
    path('dashboard/employer/job/create/', views.create_job_view, name='create_job'),
    path('dashboard/employer/job/<int:job_id>/edit/', views.edit_job_view, name='edit_job'),
    path('dashboard/employer/job/<int:job_id>/delete/', views.delete_job_view, name='delete_job'),
    path('dashboard/employer/job/<int:job_id>/applicants/', views.view_applicants_view, name='view_applicants'),
    path('dashboard/employer/applicant/<int:applicant_id>/profile/', views.view_applicant_profile_view, name='view_applicant_profile'),
    path('dashboard/employer/applicant/<int:application_id>/update/', views.update_application_status_view, name='update_application_status'),
    path('dashboard/employer/applicant/<int:application_id>/feedback/', views.provide_feedback_view, name='provide_feedback'),
    # Profile image management
    path("profile/upload-image/", views.profile_image_upload_view, name="profile_image_upload"),
    path("profile/remove-image/", views.profile_image_remove_view, name="profile_image_remove"),
]
