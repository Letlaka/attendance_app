# Generated by Django 5.1.3 on 2024-11-19 20:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0004_leaverequest'),
        ('employees_app', '0004_delete_ppeauditlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaverequest',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to='employees_app.employee', verbose_name='Employee'),
        ),
    ]
