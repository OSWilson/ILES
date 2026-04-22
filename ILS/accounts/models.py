from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES= [('student','Student'),
    ('workplace_supervisor', 'Workplace_supervisor'),
    ('academic_supervisor', 'Academic_supervisor'),
    ('admin', 'Admin')
    ]

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100)
    staff_number = models.CharField(max_length=20, blank=True, null=True)
    student_number = models.CharField(max_length=20, blank=True, null=True)
    