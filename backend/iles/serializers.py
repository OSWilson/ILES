from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, InternshipPlacement, WeeklyLog, EvaluationCriteria, CriteriaScore, Evaluation

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

        if not validated_data.get('staff_number'):
            validated_data['staff_number'] = None
        if not validated_data.get('student_number'):
            validated_data['student_number'] = None

        return CustomUser.objects.create_user(**validated_data)
    
class WeeklyLogSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='placement.student.full_name', read_only=True)
    company_name = serializers.CharField(source='placement.company_name', read_only=True)
    can_edit = serializers.ReadOnlyField()

    class Meta:
        model = WeeklyLog
        fields = '__all__'
        read_only_fields = ['student', 'placement', 'status', 'submitted_at', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    class Meta:
         model = CustomUser
         fields = [ 'id', 'username' , 'email', 'first_name', 'last_name', 'full_name',
         'role', 'department', 'staff_number', 'student_number'
         ]
         read_only_fields =['username', 'role']
        

class PlacementSerializer(serializers.ModelSerializer):
    student_detail = UserSerializer(source='student', read_only=True)
    workplace_supervisor_detail = UserSerializer(source='workplace_supervisor', read_only=True)
    academic_supervisor_detail = UserSerializer(source='academic_supervisor', read_only=True)
    is_active = serializers.ReadOnlyField() 

    class Meta:
        model = InternshipPlacement
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class CriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCriteria
        fields = '__all__'

class CriteriaScoreSerializer(serializers.ModelSerializer):
    criteria_name = serializers.CharField(source='criteria.name', read_only=True)
    criteria_weight = serializers.DecimalField(source='criteria.weight', max_digits=5, decimal_places=2, read_only=True)
    class Meta:
        model = CriteriaScore
        fields = '__all__'
        read_only_fields = ['id']

class EvaluationSerializer(serializers.ModelSerializer):
    criteria_scores = CriteriaScoreSerializer(many=True, read_only=True)

    class Meta:
        model = Evaluation
        fields = '__all__'
        read_only_fields = ['id', 'total_score', 'created_at', 'updated_at']

class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password', 'new_password2']

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password': 'New passwords do not match.'})
        return attrs
