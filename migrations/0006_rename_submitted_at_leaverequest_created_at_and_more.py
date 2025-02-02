# Generated by Django 5.1.3 on 2024-11-19 21:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0005_alter_leaverequest_employee'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='leaverequest',
            old_name='submitted_at',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='leaverequest',
            old_name='proof_document',
            new_name='proof',
        ),
        migrations.RemoveField(
            model_name='leaverequest',
            name='days_requested',
        ),
        migrations.RemoveField(
            model_name='leaverequest',
            name='reviewed_at',
        ),
        migrations.RemoveField(
            model_name='leaverequest',
            name='reviewed_by',
        ),
        migrations.AlterField(
            model_name='leaverequest',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to=settings.AUTH_USER_MODEL, verbose_name='Employee'),
        ),
        migrations.AlterField(
            model_name='leaverequest',
            name='leave_type',
            field=models.CharField(choices=[('annual', 'Annual Leave'), ('sick', 'Sick Leave'), ('family', 'Family Responsibility Leave'), ('maternity', 'Maternity Leave'), ('paternity', 'Paternity Leave'), ('study', 'Study Leave')], max_length=20),
        ),
        migrations.AlterField(
            model_name='leaverequest',
            name='reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='leaverequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
    ]
