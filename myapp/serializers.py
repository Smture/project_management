# myapp/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Projects

class ItemSerializer(serializers.ModelSerializer):
    pass


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'username', 'role')


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ['id', 'name', 'description', 'priority', 'start_date', 'end_date', 'created_at']