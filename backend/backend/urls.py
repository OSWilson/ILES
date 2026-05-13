from django.contrib import admin
from django.urls import path, include
from iles.views import (LoginView, RegisterView, ProfileView, UserListView, 
                        PlacementListCreateView, PlacementDetailView, MyPlacementView,
                        LogListCreateView, LogDetailView, submit_log, review_log, 
                        EvaluationListCreateView, EvaluationDetailView, finalize_evaluation, 
                        add_score, CriteriaListView)
from rest_framework_simplejwt.views import TokenRefreshView

api_patterns = [
    # auth
    path('auth/login/', LoginView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/register/', RegisterView.as_view()),
    path('auth/profile/', ProfileView.as_view()),
    # users
    path('users/', UserListView.as_view()),
    # placements
    path('placements/', PlacementListCreateView.as_view()),
    path('placements/<int:pk>/', PlacementDetailView.as_view()),
    path('placements/mine/', MyPlacementView.as_view()),
    # logs
    path('logs/', LogListCreateView.as_view()),
    path('logs/<int:pk>/', LogDetailView.as_view()),
    path('logs/<int:pk>/submit/', submit_log),
    path('logs/<int:pk>/review/', review_log),
    # evaluations
    path('evaluations/', EvaluationListCreateView.as_view()),
    path('evaluations/<int:pk>/', EvaluationDetailView.as_view()),
    path('evaluations/<int:pk>/finalize/', finalize_evaluation),
    path('evaluations/<int:eval_id>/scores/', add_score),
    path('criteria/', CriteriaListView.as_view()),
]

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/', include(api_patterns)),
]
