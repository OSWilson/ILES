from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from .models import CustomUser, InternshipPlacement, WeeklyLog, EvaluationCriteria, Evaluation


def make_user(username, role, **kwargs):
   
    return CustomUser.objects.create_user(
        username=username,
        password='testpass123',
        first_name='Test',
        last_name='User',
        email=f'{username}@test.com',
        role=role,
        **kwargs
    )


def make_placement(student, workplace=None, academic=None):
   
    today = date.today()
    return InternshipPlacement.objects.create(
        student=student,
        workplace_supervisor=workplace,
        academic_supervisor=academic,
        company_name='Test Company Ltd',
        start_date=today,
        end_date=today + timedelta(weeks=12),
    )
