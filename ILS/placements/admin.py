from django.contrib import admin
from .models import InternshipPlacement, WeeklyLog, EvaluationCriteria,Evaluation

# Register your models here.
admin.site.register(InternshipPlacement)
admin.site.register(WeeklyLog)
admin.site.register(EvaluationCriteria)
admin.site.register(Evaluation)