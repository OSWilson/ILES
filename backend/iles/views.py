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
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = CustomUser.objects.all()
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role)
        return qs

# --- Internship Placement Views ---

class PlacementListCreateView(generics.ListCreateAPIView):
    serializer_class = PlacementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return InternshipPlacement.objects.filter(student=user)
        if user.role == 'workplace':
            return InternshipPlacement.objects.filter(workplace_supervisor=user)
        if user.role == 'academic':
            return InternshipPlacement.objects.filter(academic_supervisor=user)
        return InternshipPlacement.objects.all()

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
            return WeeklyLog.objects.filter(student=user)
        if user.role == 'workplace':
            return WeeklyLog.objects.filter(placement__workplace_supervisor=user).exclude(status='draft')
        return WeeklyLog.objects.all()

    def perform_create(self, serializer):
        placement = self.request.user.placements.filter(is_active=True).first()
        serializer.save(student=self.request.user, placement=placement)
        
class LogDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WeeklyLogSerializer
    permission_classes = [permissions.IsAuthenticated]
        
    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return WeeklyLog.objects.filter(student=user)
        return WeeklyLog.objects.all()

    def update(self, request, *args, **kwargs):
        log = self.get_object()
        if not log.can_edit():
            return Response(
                {'error': 'This log cannot be edited in its current state.'},status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_log(request, pk):
    log = WeeklyLog.objects.get(pk=pk, student=request.user)
    log.submit()
    return Response({'status': 'submitted'})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def review_log(request, pk):
    log = WeeklyLog.objects.get(pk=pk)
    action = request.data.get('action')
    comment = request.data.get('comment', '')
    if action == 'approve':
        log.approve(request.user)
    elif action == 'reject':
        if not comment:
            return Response({'error': 'Comment required for rejection.'}, status=400)log.reject(request.user, comment)
    else:
        return Response({'error': 'Invalid action.'}, status=400)
    return Response({'status': log.status})


class CriteriaListView(generics.ListAPIView):
    queryset = EvaluationCriteria.objects.all()
    serializer_class = CriteriaSerializer
    permission_classes = [permissions.IsAuthenticated]

class EvaluationDetailView(generics.RetrieveUpdateAPIView):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]

class EvaluationListCreateView(generics.CreateAPIView):
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]
        
    def get_queryset(self):
        user = self.request.user
        if user.role == 'academic':
            return Evaluation.objects.filter(academic_supervisor=user)
        if user.role == 'student':
            return Evaluation.objects.filter(placement__student=user)
        return Evaluation.objects.all()

    def perform_create(self, serializer):
        serializer.save(academic_supervisor=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_score(request, eval_id):
    evaluation = Evaluation.objects.get(pk=eval_id)
    serializer = CriteriaScoreSerializer(data={**request.data, 'evaluation': eval_id})
    if serializer.is_valid():
        serializer.save()
        evaluation.compute_total()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def finalize_evaluation(request, pk):
    evaluation = Evaluation.objects.get(pk=pk)
    evaluation.status = 'finalized'
    evaluation.compute_total()
    return Response({'status': 'finalized', 'total_score': str(evaluation.total_score)})
