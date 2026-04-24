from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, InternshipPlacement, WeeklyLog, EvaluationCriteria, Evaluation, CriteriaScore


class CustomTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'full_name': self.user.full_name,
            'role': self.user.role,
        }
        return data
        
        
        


class WeeklyLogSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='placement.student.full_name', read_only=True)
    company_name = serializers.CharField(source='placement.company_name', read_only=True)

    class Meta:
        model = WeeklyLog
        fields = [
            'id', 
            'placement', 
            'student_name',
            'company_name',
            'week_number', 
            'start_date', 
            'end_date', 
            'log_content', 
            'status', 
            'created_at', 
            'updated_at',
            'submitted_at'
        ]
        read_only_fields = ['status', 'submitted_at', 'created_at', 'updated_at']