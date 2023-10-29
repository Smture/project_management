# myapp/urls.py

from rest_framework import routers
from .views import ItemViewSet, obtain_jwt_token, home, get_user, create_user, change_email,delete_user
from .views import fetch_projects, find_project, create_project, update_project_status, delete_project

from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'items', ItemViewSet)


urlpatterns = [
    path('auth-token/', obtain_jwt_token),
    path('', home),

    path('users', get_user),
    path('users/create', create_user),
    path('users/update_email', change_email),
    path('users/delete', delete_user),

    path('projects/fetch', fetch_projects),
    path('projects/find', find_project),
    path('projects/create', create_project),
    path('projects/update_status', update_project_status),
    path('projects/delete', delete_project),
    #
    # path('tasks', fetch_tasks_by_project_id),
    # path('tasks/create', create_task),
    # path('tasks/update_status', update_task_status),
    # path('tasks/delete', delete_task),
    #
]

