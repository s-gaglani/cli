"""
URL configuration for the evaluation app.
"""
from django.urls import path
from .views import EvaluateView, EvaluateBulkView, EvaluationLogListView

app_name = 'evaluation'

urlpatterns = [
    path('evaluate/', EvaluateView.as_view(), name='evaluate'),
    path('evaluate/bulk/', EvaluateBulkView.as_view(), name='evaluate-bulk'),
    path('logs/', EvaluationLogListView.as_view(), name='evaluation-logs'),
]
