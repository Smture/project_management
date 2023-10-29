from rest_framework import viewsets
from .models import Item
from .serializers import ItemSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, admin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template.loader import render_to_string
import requests
from .managers import UserManager, ProjectManager
from functools import wraps
import jwt
from django.conf import settings
import json



class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


# @csrf_exempt
# def obtain_jwt_token(request):
#     if request.method == 'GET':
#         username = request.GET.get('username')
#         password = request.GET.get('password')
#
#         if username and password:
#             user = authenticate(username=username, password=password)
#
#             if user:
#                 refresh = RefreshToken.for_user(user)
#                 return JsonResponse({
#                     'access_token': str(refresh.access_token),
#                     'refresh_token': str(refresh)
#                 })
#
#         return JsonResponse({'error': 'Invalid credentials'}, status=400)
#
#     return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def obtain_jwt_token(request):
    if request.method == 'GET':
        username = request.GET.get('username')
        password = request.GET.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                payload = {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email
                }
                access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

                return JsonResponse({
                    'access_token': access_token,
                })

        return JsonResponse({'error': 'Invalid credentials'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def verify_token_and_user(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        access_token = request.META.get('HTTP_AUTH_TOKEN')

        if access_token:
            try:
                decoded_payload = jwt.decode(access_token, algorithms=['HS256'], key=settings.SECRET_KEY)
                user_id = decoded_payload.get('user_id')

                response_data = {
                    'id': user_id,
                    'username': decoded_payload.get('username'),
                    'email': decoded_payload.get('email'),
                }

                return JsonResponse(response_data)

            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token has expired'}, status=401)
            except jwt.DecodeError:
                return JsonResponse({'error': 'Token is invalid'}, status=401)

        return JsonResponse({'error': 'Authentication token is required'}, status=401)

    return _wrapped_view


@login_required
def home(request):
    if request.user.groups.filter(name='Admins').exists():
        token_response = obtain_jwt_token(request)
        if token_response.status_code == 200:
            token_data = token_response.json()
            access_token = token_data.get('access_token')

            response = HttpResponse()
            response.set_cookie('auth_token', access_token)

        return render(request, 'admin_landing.html')
    elif request.user.groups.filter(name='Devs').exists():
        token_response = obtain_jwt_token(request)
        if token_response.status_code == 200:
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            response = HttpResponse()
            response.set_cookie('auth_token', access_token)

        return render(request, 'user_landing.html')
    else:
        token_response = obtain_jwt_token(request)
        if token_response.status_code == 200:
            token_data = token_response.json()
            access_token = token_data.get('access_token')

            response = HttpResponse()
            response.set_cookie('auth_token', access_token)

        return render(request, 'pm_landing.html')

    return response


@csrf_exempt
@verify_token_and_user
def get_user(request):
    user_id = request.GET.get('user_id')

    if user_id:
        user = UserManager.get_user(user_id)

        if user:
            response_data = {
                'user_id': user.id,
                'username': user.username,
                'email': user.email
            }
            return JsonResponse(response_data)

    return JsonResponse({'error': 'User not found'}, status=404)


@csrf_exempt
def create_user(request):
    response_data = verify_token(request)
    json_data = json.loads(response_data.content.decode('utf-8'))
    user_id = json_data.get('id')

    # create custom model by extending auth_user to make this role based.
    if user_id in (2, 3):
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            user = UserManager.create_user(username, email, password, first_name=first_name, last_name=last_name)
            if user:
                return JsonResponse({'message': 'User created successfully'})
        return JsonResponse({'error': 'User creation failed'}, status=400)
    else:
        return JsonResponse({'error': 'Not Authorized to create user.'}, status=401)


@csrf_exempt
def change_email(request):
    if request.method == 'PUT':

        response_data = verify_token(request)
        json_data = json.loads(response_data.content.decode('utf-8'))
        user_id = json_data.get('id')

        # Get the request body data
        data = json.loads(request.body)

        # Access specific fields from the data
        new_email = data.get('new_email')
        response = UserManager.change_email(user_id, new_email)
        if response:
            return JsonResponse({'message': 'Email changed successfully'})
    return JsonResponse({'error': 'Email change failed'}, status=400)

@csrf_exempt
def delete_user(request, user_id):
    if request.method == 'DELETE':
        deleted = UserManager.delete_user(user_id)
        if deleted:
            return JsonResponse({'message': 'User deleted successfully'})
    return JsonResponse({'error': 'User deletion failed'}, status=400)


def verify_token(request):
    access_token = request.META.get('HTTP_AUTH_TOKEN')

    if access_token:
        try:
            decoded_payload = jwt.decode(access_token, algorithms=['HS256'], key=settings.SECRET_KEY)
            response_data = {
                'id':decoded_payload.get('user_id'),
                'username': decoded_payload.get('username'),
                'email': decoded_payload.get('email'),
            }

            return JsonResponse(response_data)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.DecodeError:
            return JsonResponse({'error': 'Token is invalid'}, status=401)

    return JsonResponse({'error': 'Authentication token is required'}, status=401)



@csrf_exempt
def fetch_projects(request):
    token_details = verify_token(request)
    json_data = json.loads(token_details.content.decode('utf-8'))
    user_id = json_data.get('id')

    if user_id in (1,3):
        project_data = ProjectManager.fetch_projects()
        return JsonResponse(project_data, safe=False)
    else:
        return JsonResponse({'error': 'Not Authorized.'}, status=401)

@csrf_exempt
def find_project(request):
    token_details = verify_token(request)
    json_data = json.loads(token_details.content.decode('utf-8'))
    user_id = json_data.get('id')

    if user_id in (1, 3):
        if request.method == 'GET':
            project_id = request.GET.get('id')
            project_data = ProjectManager.find_project(project_id)
            return JsonResponse(project_data, safe=False)
        else:
            return JsonResponse({'error': 'No Project Found'}, status=400)

    else:
        return JsonResponse({'error': 'Not Authorized.'}, status=401)

@csrf_exempt
def create_project(request):

    token_details = verify_token(request)
    json_data = json.loads(token_details.content.decode('utf-8'))
    user_id = json_data.get('id')

    if user_id in (1, 3):

        if request.method == 'POST':
            name = request.POST.get('name')
            description = request.POST.get('description')
            priority = request.POST.get('priority')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

        result = ProjectManager.create_project(name, description, priority, start_date, end_date)
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({'error': 'Not Authorized.'}, status=401)

@csrf_exempt
def update_project_status(request):
        response_data = verify_token(request)
        json_data = json.loads(response_data.content.decode('utf-8'))
        user_id = json_data.get('id')
        if user_id in (1, 3):
            if request.method == 'PUT':
                data = json.loads(request.body)
                status = data.get('status')
                project_id = data.get('project_id')
                result = ProjectManager.update_project_status(project_id, status)
            return JsonResponse(result)
        else:
            return JsonResponse({'error': 'Not Authorized.'}, status=401)


@csrf_exempt
def delete_project(request, project_id):
    # Validate the user's authorization using the auth token in the headers
    response_data = verify_token(request)
    json_data = json.loads(response_data.content.decode('utf-8'))
    user_id = json_data.get('id')

    # Check if the user is authorized (assuming 1 and 3 are authorized user IDs)
    if user_id in (1, 3):
        if request.method == 'DELETE':
            # Use the project_id parameter directly, no need to parse request body
            result = ProjectManager.delete_project(project_id)
            return JsonResponse(result)
    return JsonResponse({'error': 'Not Authorized.'}, status=401)

