from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    
    # Users
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    
    # Opportunities
    path('opportunities/', views.opportunity_list, name='opportunity_list'),
    path('opportunities/<int:opportunity_id>/', views.opportunity_detail, name='opportunity_detail'),
    path('opportunities/<int:opportunity_id>/applicants/', views.get_applicants, name='get_applicants'),
    
    # Applications
    path('applications/', views.create_application, name='create_application'),
    path('applications/user/<int:user_id>/', views.get_user_applications, name='get_user_applications'),
    path('applications/<int:application_id>/', views.cancel_application, name='cancel_application'),
    path('applications/<int:application_id>/status/', views.update_application_status, name='update_application_status'),
    
    # Admin
    path('admin/dashboard/', views.admin_dashboard_stats, name='admin_dashboard'),
    path('admin/applications/', views.get_all_applications_admin, name='admin_applications'),
]