from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, InternshipPlacement, WeeklyLog, EvaluationCriteria, Evaluation, CriteriaScore


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role',)
    fieldsets = UserAdmin.fieldsets + (
        ('ILES', {'fields': ('role', 'department', 'staff_number', 'student_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('ILES', {'fields': ('role', 'department', 'staff_number', 'student_number')}),
    )


@admin.register(InternshipPlacement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = ('student', 'company_name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)


@admin.register(WeeklyLog)
class WeeklyLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'week_number', 'status', 'submitted_at')
    list_filter = ('status',)


admin.site.register(EvaluationCriteria)
admin.site.register(CriteriaScore)


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('placement', 'academic_supervisor', 'status', 'total_score')
    list_filter = ('status',)