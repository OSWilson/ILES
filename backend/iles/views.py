from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser, InternshipPlacement, WeeklyLog, EvaluationCriteria, Evaluation, CriteriaScore
from .serializers import (
    CustomTokenSerializer, RegisterSerializer, UserSerializer,
    PlacementSerializer, WeeklyLogSerializer,
    CriteriaSerializer, CriteriaScoreSerializer, EvaluationSerializer
)




class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user