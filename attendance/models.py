from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    EDUCATION_CHOICES = [
        ('ELEMENTARY', 'Elementary'),
        ('HIGHSCHOOL', 'High School'),
        ('COLLEGE', 'College'),
    ]
    
    id_number = models.CharField(max_length=50, unique=True)
    school_id_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    education_stage = models.CharField(max_length=20, choices=EDUCATION_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.school_id_number})"

class AttendanceLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    check_in = models.DateTimeField(auto_now_add=True)
    check_out = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        status = "IN" if self.check_out is None else "OUT"
        return f"{self.student.name} - {status} at {self.check_in}"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('LIBRARIAN', 'Librarian'),
        ('VIEWER', 'Viewer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='VIEWER')
    
    def is_librarian(self):
        return self.role in ['ADMIN', 'LIBRARIAN']

    def __str__(self):
        return f"{self.user.username} ({self.role})"