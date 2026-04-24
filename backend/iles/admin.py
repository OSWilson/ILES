# Register your models here.

from django.contrib import admin
from .models import CustomUser, InternshipPlacement, WeeklyLog




@admin.register(WeeklyLog)
class WeeklyLogAdmin(admin.ModelAdmin):
   
    list_display = ('week_number', 'get_student', 'status', 'start_date', 'end_date', 'submitted_at')    
    list_filter = ('status', 'week_number')       
    search_fields = ('placement__student__username', 'placement__student__first_name', 'log_content')


    def get_student(self, obj):
        return obj.placement.student.full_name
    get_student.short_description = 'Student'