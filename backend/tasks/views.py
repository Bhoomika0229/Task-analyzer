from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import TaskInputSerializer
from . import scoring

def home(request):
    return render(request, "index.html")

class AnalyzeTasksView(APIView):
    def post(self, request):
        strategy = request.data.get('strategy', 'smart_balance')
        tasks_data = request.data.get('tasks', [])

        serializer = TaskInputSerializer(data=tasks_data, many=True)
        serializer.is_valid(raise_exception=True)
        tasks = serializer.validated_data

        analyzed = scoring.analyze_tasks(tasks, strategy=strategy)

        return Response(analyzed, status=status.HTTP_200_OK)


class SuggestTasksView(APIView):
    def get(self, request):
        # In a real app you might pull tasks from DB.
        # For this assignment, assume client will hit /analyze/ instead,
        # or you can accept tasks via query/body if you want.
        return Response(
            {
                "detail": "Suggestion endpoint expects tasks to be provided via /api/tasks/analyze/ in this implementation."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
