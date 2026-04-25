# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, InternshipPlacement, WeeklyLog, EvaluationCriteria, Evaluation, CriteriaScore

admin.site.register(EvaluationCriteria)
admin.site.register(CriteriaScore)

@admin.register(WeeklyLog)
class WeeklyLogAdmin(admin.ModelAdmin):
    list_display = ('week_number', 'get_student', 'status', 'start_date', 'end_date', 'submitted_at')    
    list_filter = ('status', 'week_number')       
    search_fields = ('placement__student__username', 'placement__student__first_name', 'log_content')

    def get_student(self, obj):
        return obj.placement.student.full_name
    get_student.short_description = 'Student'

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role',)
    fieldsets = UserAdmin.fieldsets + (('ILES', {'fields': ('role', 'department', 'staff_number', 'student_number')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('ILES', {'fields': ('role', 'department', 'staff_number', 'student_number')})


