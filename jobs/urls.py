from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('jobs/', views.job_list_view, name='job_list'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('apply/<int:job_id>/', views.apply_for_job_view, name='apply_for_job'),
    path('dashboard/applicant/', views.applicant_dashboard_view, name='applicant_dashboard'),
    path('dashboard/employer/', views.employer_dashboard_view, name='employer_dashboard'),
    path('dashboard/employer/job/create/', views.create_job_view, name='create_job'),
    path('dashboard/employer/job/<int:job_id>/edit/', views.edit_job_view, name='edit_job'),
    path('dashboard/employer/job/<int:job_id>/delete/', views.delete_job_view, name='delete_job'),
    path('dashboard/employer/job/<int:job_id>/applicants/', views.view_applicants_view, name='view_applicants'),
    path('dashboard/employer/applicant/<int:application_id>/update/', views.update_application_status_view, name='update_application_status'),
]
