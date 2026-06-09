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


    def get_role_display_name(self):

        role_names = {
        'student': 'Student Intern',
        'workplace': 'Workplace Supervisor',
        'academic': 'Academic Supervisor',
        'admin': 'Internship Administrator',
        }
        return role_names.get(self.role, self.role)    


class InternshipPlacement(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='placements', limit_choices_to={'role': 'student'}
    )
    workplace_supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='workplace_supervisions',
        limit_choices_to={'role': 'workplace'}
    )
    academic_supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='academic_supervisions',
        limit_choices_to={'role': 'academic'}
    )
    company_name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({'end_date': 'End date must be after start date.'})
        if self.student_id:
            overlap = InternshipPlacement.objects.filter(
                student=self.student_id, is_active=True,
                start_date__lt=self.end_date, end_date__gt=self.start_date,
            ).exclude(pk=self.pk)
            if overlap.exists():
                raise ValidationError('Student already has an overlapping placement.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} @ {self.company_name}"
    


class WeeklyLog(models.Model):
    STATUS = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='weekly_logs', limit_choices_to={'role': 'student'}
    )
    placement = models.ForeignKey(
        InternshipPlacement, on_delete=models.CASCADE, related_name='weekly_logs'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_logs'
    )
    week_number = models.PositiveIntegerField()
    week_start_date = models.DateField()
    activities = models.TextField()
    skills_gained = models.TextField(blank=True)
    challenges = models.TextField(blank=True)
    next_week_plan = models.TextField(blank=True)
    supervisor_comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_edit(self):
        return self.status in ('draft', 'rejected')

    def submit(self):
        if not self.can_edit():
            raise ValidationError("Only draft or rejected logs can be submitted.")
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.save()

    def approve(self, reviewer):
        self.status = 'approved'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()

    def reject(self, reviewer, comment):
        self.status = 'rejected'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.supervisor_comment = comment
        self.save()

    def clean(self):
        dup = WeeklyLog.objects.filter(
            student=self.student_id, placement=self.placement_id,
            week_number=self.week_number
        ).exclude(pk=self.pk)
        if dup.exists():
            raise ValidationError({'week_number': f'Log for week {self.week_number} already exists.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Week {self.week_number} — {self.student} [{self.status}]"

    class Meta:
        ordering = ['-week_start_date']
        unique_together = ('student', 'placement', 'week_number')    
        



class EvaluationCriteria(models.Model):
    name = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.weight}%)"

    class Meta:
        verbose_name_plural = 'Evaluation Criteria'



class Evaluation(models.Model):
    STATUS = (
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('finalized', 'Finalized'),
    )
    placement = models.OneToOneField(
        InternshipPlacement, on_delete=models.CASCADE, related_name='evaluation'
    )
    academic_supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='evaluations_given'
    )
    status = models.CharField(max_length=20, choices=STATUS, default='not_started')
    general_comments = models.TextField(blank=True)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def compute_total(self):
        total = Decimal('0.00')
        for s in self.criteria_scores.all():
            total += (s.score / 10) * s.criteria.weight
        self.total_score = total
        self.save()
        return total

    def __str__(self):
        return f"Evaluation: {self.placement}"


class CriteriaScore(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='criteria_scores')
    criteria = models.ForeignKey(EvaluationCriteria, on_delete=models.PROTECT)
    score = models.DecimalField(max_digits=4, decimal_places=2,validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('10'))])
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ('evaluation', 'criteria')

    def __str__(self):
        return f"{self.criteria.name}: {self.score}/10"
        
    def compute_total(self):
        total = Decimal('0.00')
        for s in self.criteria_scores.all():
        
            total += (s.score / 10) * s.criteria.weight
        self.total_score = total
        self.save()
        return total    
        


