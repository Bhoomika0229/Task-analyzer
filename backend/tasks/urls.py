from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.AnalyzeTasksView.as_view(), name='analyze-tasks'),
    path('suggest/', views.SuggestTasksView.as_view(), name='suggest-tasks'),
]
