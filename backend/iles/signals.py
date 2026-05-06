
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import WeeklyLog, InternshipPlacement, Evaluation




@receiver(post_save, sender=WeeklyLog)
def notify_log_status_change(sender, instance, created, **kwargs):
    """
    Fires every time a WeeklyLog is saved.

    sender   = the model class that triggered the signal (WeeklyLog)
    instance = the actual WeeklyLog object that was saved
    created  = True if this is a NEW record, False if it's an UPDATE
    **kwargs = extra keyword arguments (always include this)
    """


    if created:
        return

    student_email = instance.student.email
    if not student_email:
        return  # no email on file — skip silently

    if instance.status == 'approved':
        send_mail(
            subject=f'[ILES] Week {instance.week_number} Log Approved',
            message=(
                f'Dear {instance.student.full_name},\n\n'
                f'Your Week {instance.week_number} internship log has been approved '
                f'by your workplace supervisor.\n\n'
                f'Log in to ILES to view your feedback.\n\n'
                f'ILES System'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student_email],
            fail_silently=True,  # don't crash the app if email fails
        )

    elif instance.status == 'rejected':
        send_mail(
            subject=f'[ILES] Week {instance.week_number} Log Needs Revision',
            message=(
                f'Dear {instance.student.full_name},\n\n'
                f'Your Week {instance.week_number} log requires revision.\n\n'
                f'Supervisor comment: {instance.supervisor_comment}\n\n'
                f'Please log in to ILES, edit your log, and resubmit.\n\n'
                f'ILES System'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student_email],
            fail_silently=True,
        )




@receiver(post_save, sender=InternshipPlacement)
def notify_placement_assigned(sender, instance, created, **kwargs):
    """Fires when a new placement is created."""
    if not created:
        return  

    student_email = instance.student.email
    if not student_email:
        return

    send_mail(
        subject='[ILES] Internship Placement Assigned',
        message=(
            f'Dear {instance.student.full_name},\n\n'
            f'You have been assigned an internship placement at {instance.company_name}.\n\n'
            f'Duration: {instance.start_date} to {instance.end_date}\n\n'
            f'Log in to ILES to start submitting your weekly logs.\n\n'
            f'ILES System'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[student_email],
        fail_silently=True,
    )




@receiver(post_save, sender=Evaluation)
def notify_evaluation_finalized(sender, instance, created, **kwargs):
    """Fires when an evaluation is saved."""
    if created:
        return

    if instance.status == 'finalized':
        student_email = instance.placement.student.email
        if not student_email:
            return

        send_mail(
            subject='[ILES] Your Internship Evaluation is Finalized',
            message=(
                f'Dear {instance.placement.student.full_name},\n\n'
                f'Your internship evaluation for {instance.placement.company_name} '
                f'has been finalized.\n\n'
                f'Total Score: {instance.total_score}/100\n\n'
                f'Log in to ILES to view your full evaluation.\n\n'
                f'ILES System'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student_email],
            fail_silently=True,
        )