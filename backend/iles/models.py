from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal




class CustomUser(AbstractUser):
    ROLES = (
        ('student', 'Student'),
        ('workplace', 'Workplace Supervisor'),
        ('academic', 'Academic Supervisor'),
        ('admin', 'Administrator'),
    )
    role = models.CharField(max_length=20, choices=ROLES)
    department = models.CharField(max_length=150, blank=True, null=True)
    staff_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    student_number = models.CharField(max_length=50, unique=True, blank=True, null=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def __str__(self):
        return f"{self.full_name} ({self.role})"

