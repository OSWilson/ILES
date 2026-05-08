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