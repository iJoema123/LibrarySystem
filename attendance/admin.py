from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Student, AttendanceLog, UserProfile

@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    list_display = ('school_id_number', 'name', 'education_stage')
    list_filter = ('education_stage',)
    search_fields = ('school_id_number', 'name')
    ordering = ('name',)

@admin.register(AttendanceLog)
class AttendanceLogAdmin(ImportExportModelAdmin):
    list_display = ('student', 'check_in', 'check_out')
    list_filter = ('check_in', 'student__education_stage')
    search_fields = ('student__name', 'student__school_id_number')
    readonly_fields = ('check_in',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username',)