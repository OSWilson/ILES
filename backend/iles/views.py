from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser, InternshipPlacement, WeeklyLog, EvaluationCriteria
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

class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

# --- Internship Placement Views ---

class PlacementListCreateView(generics.ListCreateAPIView):
    queryset = InternshipPlacement.objects.all()
    serializer_class = PlacementSerializer
    permission_classes = [permissions.IsAuthenticated]

class PlacementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InternshipPlacement.objects.all()
    serializer_class = PlacementSerializer
    permission_classes = [permissions.IsAuthenticated]

class MyPlacementView(generics.RetrieveAPIView):
    """Returns the placement for the currently logged-in student."""
    serializer_class = PlacementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return InternshipPlacement.objects.filter(student=self.request.user).first()



class LogListCreateView(generics.ListCreateAPIView):
    """Renamed from WeeklyLogListCreateView to match urls.py"""
    serializer_class = WeeklyLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return WeeklyLog.objects.filter(placement__student=user)
        return WeeklyLog.objects.all()

class LogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WeeklyLog.objects.all()
    serializer_class = WeeklyLogSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_log(request, pk):
    """Action to submit a specific log."""
    try:
        log = WeeklyLog.objects.get(pk=pk, placement__student=request.user)
        log.status = 'submitted'
        log.save()
        return Response({'status': 'log submitted'})
    except WeeklyLog.DoesNotExist:
        return Response({'error': 'Log not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def review_log(request, pk):
    
    if request.user.role not in ['staff', 'supervisor']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        log = WeeklyLog.objects.get(pk=pk)
        log.status = request.data.get('status', 'approved')
        log.save()
        return Response({'status': f'log {log.status}'})
    except WeeklyLog.DoesNotExist:
        return Response({'error': 'Log not found'}, status=status.HTTP_404_NOT_FOUND)


class CriteriaListView(generics.ListAPIView):
    queryset = EvaluationCriteria.objects.all()
    serializer_class = CriteriaSerializer
    permission_classes = [permissions.IsAuthenticated]

class EvaluationCreateView(generics.CreateAPIView):
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]