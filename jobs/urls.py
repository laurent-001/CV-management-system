from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('jobs/', views.job_list_view, name='job_list'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('apply/<int:job_id>/', views.submit_cv_view, name='submit_cv'),
    path('dashboard/', views.applicant_dashboard_view, name='applicant_dashboard'),
    path('hr/dashboard/', views.hr_dashboard_view, name='hr_dashboard'),
    path('hr/update/<int:application_id>/', views.update_application_status_view, name='update_application_status'),
]
