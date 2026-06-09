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
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='placements', limit_choices_to={'role': 'student'})
    workplace_supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,null=True, blank=True, related_name='workplace_supervisions',limit_choices_to={'role': 'workplace'})
    academic_supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,null=True, blank=True, related_name='academic_supervisions',limit_choices_to={'role': 'academic'})
    company_name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({'end_date': 'End date must be after start date.'})
        if self.student_id:
            overlap = InternshipPlacement.objects.filter(student=self.student_id, is_active=True,start_date__lt=self.end_date, end_date__gt=self.start_date,).exclude(pk=self.pk)
        if overlap.exists():
            raise ValidationError('Student already has an overlapping placement.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} @ {self.company_name}"
        
    @property
    def duration_weeks(self):
    #Calculate how many weeks the placement lasts
    if self.start_date and self.end_date:
        delta = self.end_date - self.start_date
        return delta.days // 7
    return 0
        
class WeeklyLog(models.Model):       
    STATUS_CHOICES = (
        ('draft' , 'Draft'),
        ('submitted' , 'Submitted'), 
        ('reviewed' , 'Reviewed'),
        ('approved' , 'Approved'),
        ('rejected', 'Rejected'),    
    )
    
    placement = models.ForeignKey(InternshipPlacement, on_delete= models.CASCADE, related_name= 'weekly_logs')
    week_number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    log_content = models.TextField (help_text = "describe activities you have done this week")
    
    status = models.CharField(max_length = 20, choices = STATUS_CHOICES, default ='draft')
    
    created_at = models.DateTimeField(auto_now_add = True)
     
    updated_at = models.DateTimeField(auto_now=True)     
    submitted_at = models.DateTimeField(null=True, blank=True)
    """
    Represents a student's weekely internship activity report
    workflow states draft>submitted>approved
                    draft>rejected>(edit)>submitted
    Business rules:-Only draft and rejected logs can be edited
                   -Supervisor comment is required when rejecting
                   -Week number must be unique per student per placement
    """

    def clean(self):   # to prevent status being changed when made
        
        if self.pk:
            original = WeeklyLog.objects.get(pk=self.pk)
            if original.status == 'approved' and self.status == 'approved':
       
                if original.log_content != self.log_content or original.week_number != self.week_number:
                    raise ValidationError("You cannot edit a log that has already been approved.")
        
        # if end date is not valid
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({'end_date': 'End date must be after the start date.'})
    
    def save (self, *args, **kwargs):
    
        if self.status == 'submitted' and not self.submitted_at:
            from django.utils import timezone
            self.submitted_at = timezone.now()
            
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Week {self.week_number} Log - {self.placement.student.username}"


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
        
        
        


