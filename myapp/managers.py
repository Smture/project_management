import logging

from django.contrib.auth.models import User
from .models import Projects
from django.db.models import Q
import json
from .serializers import ProjectSerializer

class UserManager:
    @staticmethod
    def get_user(user_id):
        try:
            user = User.objects.get(id=user_id)
            user_details = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
            return user_details
        except User.DoesNotExist:
            return None

    @staticmethod
    def create_user(username, email, password, **kwargs):
        try:
            user = User.objects.create_user(username, email, password, **kwargs)
            return user
        except Exception as e:
            print(e)
            return None


    @staticmethod
    def change_email(user_id, new_email):
        user = User.objects.get(id=user_id)
        if user:
            user.email = new_email
            user.save()
            return user
        return None

    @staticmethod
    def delete_user(user_id):
        user = User.objects.get(id=user_id)
        if user:
            user.delete()
            return True
        return False


class ProjectManager:
    @staticmethod
    def fetch_projects():
        projects = Projects.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return serializer.data

    @staticmethod
    def find_project(project_id):
        try:
            project = Projects.objects.get(id=project_id)
            serializer = ProjectSerializer(project)
            return serializer.data
        except Projects.DoesNotExist:
            return {'error': 'Project not found'}

    @staticmethod
    def create_project(name, description, priority, start_date, end_date):
        try:
            project = Projects.objects.create(
                name=name,
                description=description,
                priority=priority,
                start_date=start_date,
                end_date=end_date
            )

            serializer = ProjectSerializer(project)
            project_data = serializer.data
            return project_data

        except Exception as e:
            logging.error(e)
            return None

    @staticmethod
    def update_project_status(project_id, status):
        try:
            project = Projects.objects.get(id=project_id)
            project.status = status
            project.save()
            return {'message': 'Project status updated successfully'}
        except Projects.DoesNotExist:
            return {'error': 'Project not found'}

    @staticmethod
    def delete_project_from_system(project_id):
        try:
            project = Projects.objects.get(id=project_id)
            project.status = "Archieved"
            project.save()
            return {'message': 'Project deleted successfully'}
        except Projects.DoesNotExist:
            return {'error': 'Project not found'}