from rest_framework import serializers
from .models import Internship, Application 

class InternshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internship
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
 
    internship_details = InternshipSerializer(source='internship', read_only=True)

    class Meta:
        model = Application
       
        fields = ['id', 'status', 'applied_on', 'internship_details']