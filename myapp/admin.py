from django.contrib import admin

from .models import Users, Projects, Tasks, Roles

admin.site.register(Users)
admin.site.register(Projects)
admin.site.register(Tasks)
admin.site.register(Roles)