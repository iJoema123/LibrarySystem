from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Q
import csv
import json
from datetime import datetime, timedelta
from .models import Student, AttendanceLog, UserProfile
import qrcode
import base64
from io import BytesIO



# Helper functions
def is_librarian(user):
    """Check if user is librarian or admin"""
    if not user.is_authenticated:
        return False
    try:
        return user.userprofile.is_librarian() or user.is_superuser
    except UserProfile.DoesNotExist:
        # Create default profile for users without one
        UserProfile.objects.create(user=user, role='VIEWER')
        return False

librarian_required = user_passes_test(is_librarian, login_url='/attendance/login/')

# Authentication Views
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'attendance/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('scan_qr')

# Public Views
def scan_qr(request):
    """QR Code scanner for check-in/check-out"""
    today = timezone.now().date()
    
    # Get statistics for display
    today_count = AttendanceLog.objects.filter(check_in__date=today).count()
    current_in_library = AttendanceLog.objects.filter(check_out__isnull=True).count()
    
    if request.method == 'POST':
        school_id = request.POST.get('school_id_number', '').strip()
        
        if school_id:
            try:
                student = Student.objects.get(school_id_number=school_id)
                
                # Check for open attendance record
                open_log = AttendanceLog.objects.filter(
                    student=student, 
                    check_out__isnull=True
                ).first()
                
                if open_log:
                    # Check out
                    open_log.check_out = timezone.now()
                    open_log.save()
                    messages.success(request, f'✅ {student.name} checked out at {open_log.check_out.strftime("%H:%M:%S")}')
                else:
                    # Check in
                    AttendanceLog.objects.create(student=student)
                    messages.success(request, f'✅ {student.name} checked in successfully!')
                    
            except Student.DoesNotExist:
                messages.error(request, f'❌ Student with ID {school_id} not found.')
        
        return redirect('scan_qr')
    
    return render(request, 'attendance/scan_qr.html', {
        'today_count': today_count,
        'current_in_library': current_in_library,
    })

# Protected Views (Librarian required)
@login_required
@librarian_required
def dashboard(request):
    """Dashboard with statistics and charts"""
    today = timezone.now().date()
    
    # Last 7 days data
    dates = []
    counts = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = AttendanceLog.objects.filter(check_in__date=date).count()
        dates.append(date.strftime('%Y-%m-%d'))
        counts.append(count)
    
    # Education stage statistics
    stage_stats = Student.objects.values('education_stage').annotate(
        total=Count('attendancelog')
    ).order_by('education_stage')
    
    # Current visitors
    current_visitors = AttendanceLog.objects.filter(
        check_out__isnull=True
    ).select_related('student')
    
    context = {
        'dates_json': json.dumps(dates),
        'counts_json': json.dumps(counts),
        'stage_stats': stage_stats,
        'current_visitors': current_visitors,
        'total_students': Student.objects.count(),
        'total_visits_today': counts[-1] if counts else 0,
    }
    
    return render(request, 'attendance/dashboard.html', context)

@login_required
@librarian_required
def attendance_report(request):
    """Attendance reports with filtering"""
    today = timezone.now().date()  # This was missing!
    
    # Get filter parameters
    date_filter = request.GET.get('date', '')
    stage_filter = request.GET.get('stage', '')
    search_query = request.GET.get('search', '')
    
    # Build query
    attendance_logs = AttendanceLog.objects.all().select_related('student')
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            attendance_logs = attendance_logs.filter(check_in__date=filter_date)
        except ValueError:
            pass
    
    if stage_filter:
        attendance_logs = attendance_logs.filter(student__education_stage=stage_filter)
    
    if search_query:
        attendance_logs = attendance_logs.filter(
            Q(student__name__icontains=search_query) |
            Q(student__school_id_number__icontains=search_query)
        )
    
    # If no date filter, show today's records
    if not date_filter:
        attendance_logs = attendance_logs.filter(check_in__date=today)
    
    context = {
        'attendance_logs': attendance_logs,
        'selected_date': date_filter,
        'selected_stage': stage_filter,
        'search_query': search_query,
        'education_stages': Student.EDUCATION_CHOICES,
    }
    
    return render(request, 'attendance/report.html', context)

@login_required
@librarian_required
def export_attendance(request):
    """Export attendance data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Name', 'Education Stage', 'Check-in', 'Check-out'])
    
    logs = AttendanceLog.objects.select_related('student').all()
    
    for log in logs:
        writer.writerow([
            log.student.school_id_number,
            log.student.name,
            log.student.get_education_stage_display(),
            log.check_in.strftime('%Y-%m-%d %H:%M:%S'),
            log.check_out.strftime('%Y-%m-%d %H:%M:%S') if log.check_out else ''
        ])
    
    return response

@login_required
@librarian_required
def backup_data(request):
    """Simple backup functionality"""
    messages.success(request, 'Backup functionality will be implemented here.')
    return redirect('dashboard')

@login_required
@librarian_required
def system_status(request):
    """System status page"""
    context = {
        'total_students': Student.objects.count(),
        'total_logs': AttendanceLog.objects.count(),
        'logs_today': AttendanceLog.objects.filter(check_in__date=timezone.now().date()).count(),
        'current_visitors': AttendanceLog.objects.filter(check_out__isnull=True).count(),
        'server_time': timezone.now(),
    }
    return render(request, 'attendance/system_status.html', context)



def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()

@login_required
@librarian_required
def student_qr_codes(request):
    """Generate QR codes for all students"""
    students = Student.objects.all()
    
    # Generate QR codes
    for student in students:
        student.qr_code = generate_qr_code(student.school_id_number)
    
    context = {
        'students': students,
    }
    return render(request, 'attendance/student_qr_codes.html', context)