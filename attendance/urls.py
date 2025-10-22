from django.urls import path
from . import views

urlpatterns = [
    path('', views.scan_qr, name='scan_qr'),
    path('scan/', views.scan_qr, name='scan_qr'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report/', views.attendance_report, name='attendance_report'),
    path('export/', views.export_attendance, name='export_attendance'),
    path('backup/', views.backup_data, name='backup_data'),
    path('status/', views.system_status, name='system_status'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('qr-codes/', views.student_qr_codes, name='student_qr_codes'),
]