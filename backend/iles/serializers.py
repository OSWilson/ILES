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
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name',
                  'role', 'department', 'staff_number', 'student_number',
                  'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return CustomUser.objects.create_user(**validated_data)

class WeeklyLogSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='placement.student.full_name', read_only=True)
    company_name = serializers.CharField(source='placement.company_name', read_only=True)

    class Meta:
        model = WeeklyLog
        fields = [
            'id', 'placement', 'student_name','company_name',
            'week_number', 'start_date', 'end_date', 'log_content', 
            'status', 'created_at', 'updated_at','submitted_at'
        ]
        read_only_fields = ['status', 'submitted_at', 'created_at', 'updated_at']
