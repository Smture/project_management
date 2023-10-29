from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models

import enum

# Fields used to create an index in the DB and sort the tasks in the Admin
TASK_PRIORITY_FIELDS = ('state', '-priority', '-deadline')


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Users(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    status = models.CharField(max_length=20)
    role = models.ForeignKey('ROLES', on_delete=models.CASCADE)
    assigned_task_id = models.ManyToManyField('TASKS', blank=True)
    assigned_project = models.ForeignKey('PROJECTS', on_delete=models.CASCADE, related_name='assigned_users', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'USERS'


class Roles(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ROLES'


class Tasks(models.Model):
    name = models.CharField(max_length=255)
    project_id = models.ForeignKey('PROJECTS', on_delete=models.CASCADE)
    priority = models.CharField(max_length=20)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'TASKS'


class Projects(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    status_choices = (
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Archieved', 'Archieved'),
        ('Delayed', 'Delayed')
    )
    status = models.CharField(max_length=20, choices=status_choices, default='Not Started')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    class Meta:
        db_table = 'PROJECTS'


class TaskHistory(models.Model):
    task_id = models.ForeignKey('TASKS', on_delete=models.CASCADE)
    task_name = models.CharField(max_length=255)
    edited_by = models.ForeignKey('USERS', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'TASK_HISTORY'


Users.add_to_class('is_admin', models.BooleanField(default=False))