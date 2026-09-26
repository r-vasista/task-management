from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Project, Task

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        read_only_fields = ('id',)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'owner', 'created_at')
        read_only_fields = ('id', 'owner', 'created_at')


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            'id',
            'project',
            'title',
            'description',
            'status',
            'due_date',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_project(self, project):
        request = self.context.get('request')
        if project and request and project.owner_id != request.user.id:
            raise serializers.ValidationError('Choose a project that you own.')
        return project