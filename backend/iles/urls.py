from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ChangePasswordView
from .views import student_dashboard_stats, admin_dashboard_stats, supervisor_dashboard_stats

from .views import (
    LoginView, RegisterView, ProfileView,
    UserListView,
    PlacementListCreateView, PlacementDetailView, MyPlacementView,
    LogListCreateView, LogDetailView, submit_log, review_log,
    EvaluationListCreateView, EvaluationDetailView, CriteriaListView,
    add_score, finalize_evaluation,
)

urlpatterns = [
    
    path('api/auth/login/', LoginView.as_view()),
    path('api/auth/refresh/', TokenRefreshView.as_view()),
    path('api/auth/register/', RegisterView.as_view()),
    path('api/auth/profile/', ProfileView.as_view()),
    path('api/auth/change-password/', ChangePasswordView.as_view()),

    
    path('api/users/', UserListView.as_view()),

    
    path('api/placements/', PlacementListCreateView.as_view()),
    path('api/placements/<int:pk>/', PlacementDetailView.as_view()),
    path('api/placements/mine/', MyPlacementView.as_view()),

    
    path('api/logs/', LogListCreateView.as_view()),
    path('api/logs/<int:pk>/', LogDetailView.as_view()),
    path('api/logs/<int:pk>/submit/', submit_log),
    path('api/logs/<int:pk>/review/', review_log),
    
    path('api/evaluations/', EvaluationListCreateView.as_view()),
    path('api/evaluations/<int:pk>/', EvaluationDetailView.as_view()),
    path('api/evaluations/<int:pk>/finalize/', finalize_evaluation),
    path('api/evaluations/<int:eval_id>/scores/', add_score),
    path('api/criteria/', CriteriaListView.as_view()),

    path('api/stats/student/', student_dashboard_stats),
    path('api/stats/admin/', admin_dashboard_stats),
    path('api/stats/supervisor/', supervisor_dashboard_stats),
    path('', include('iles.urls')),
]