# Generated by Django 4.2.6 on 2023-10-28 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_rename_role_id_users_role_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='assigned_task_id',
            field=models.ManyToManyField(blank=True, to='myapp.tasks'),
        ),
    ]
