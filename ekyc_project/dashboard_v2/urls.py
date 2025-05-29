from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    
    path('view-records/', views.view_records_view, name='view_records'),
    path('export-data/', views.export_data_view, name='export_data'),

    path('aadhaar-list/', views.aadhaar_list, name='aadhaar_list'),
    path('pan-list/', views.pan_list, name='pan_list'),
    path('passport-list/', views.passport_list, name='passport_list'),

    path('delete-entry/<int:entry_id>/', views.delete_entry, name='delete_entry'),
]