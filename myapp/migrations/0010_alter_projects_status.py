# Generated by Django 4.2.6 on 2023-10-29 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_alter_projects_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projects',
            name='status',
            field=models.CharField(choices=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Completed', 'Completed'), ('Archieved', 'Archieved'), ('Delayed', 'Delayed')], default='Not Started', max_length=20),
        ),
    ]