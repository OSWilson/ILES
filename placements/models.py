from django.db import models
from accounts.models import CustomUser

# Create your models here.
class InternshipPlacement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('under_review', 'Under Review'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='placements')
    workplace_supervisor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='supervised_placements')
    academic_supervisor= models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='academic_placements')
    company_name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')


class WeeklyLog(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed')
    ]

    placement = models.ForeignKey(InternshipPlacement, on_delete=models.CASCADE, related_name='weekly_logs')
    week_number = models.IntegerField()
    description = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    supervisor_comment = models.TextField(blank=True, null=True)

class EvaluationCriteria(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    max_score = models.IntegerField()

class Evaluation(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In progress'),
        ('submitted', 'Submitted'),
        ('finalised', 'Funalised')
    ]

    placement = models.ForeignKey(InternshipPlacement, on_delete=models.CASCADE, related_name = 'evaluations')
    evaluator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name = 'evaluations')
    criteria = models.ForeignKey(EvaluationCriteria, on_delete= models.CASCADE, related_name ='Evaluations')
    score = models.IntegerField()
    comments = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    submitted_at = models.DateTimeField(auto_now_add=True)
