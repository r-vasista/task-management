from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Task
from .serializers import RegistrationSerializer, TaskSerializer


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            RegistrationSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)


class TaskListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        tasks = Task.objects.filter(owner=request.user).select_related('project')
        return Response(TaskSerializer(tasks, many=True, context={'request': request}).data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, request, task_id):
        return get_object_or_404(Task, id=task_id, owner=request.user)

    def get(self, request, task_id):
        task = self.get_object(request, task_id)
        return Response(TaskSerializer(task, context={'request': request}).data)

    def put(self, request, task_id):
        task = self.get_object(request, task_id)
        serializer = TaskSerializer(
            task,
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, task_id):
        task = self.get_object(request, task_id)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)