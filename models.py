# Standard Library Imports
import logging

# Third-Party Imports
from django.db import models
from django.forms import ValidationError
from django.utils.timezone import now

# Custom Imports
from employees_app.models import Employee


logger = logging.getLogger(__name__)


class LeaveAllocation(models.Model):
    """Tracks pre-allocated and used leave for employees."""

    LEAVE_TYPES = [
        ("annual", "Annual Leave"),
        ("sick_with_note", "Sick Leave (With Note)"),
        ("sick_without_note", "Sick Leave (Without Note)"),
        ("family", "Family Responsibility Leave"),
        ("maternity", "Maternity Leave"),
        ("paternity", "Paternity Leave"),
        ("study", "Study Leave"),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="leave_allocations"
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    allocated_days = models.PositiveIntegerField(default=0)
    used_days = models.PositiveIntegerField(default=0)
    allocation_cycle_start = models.DateField(null=True, blank=True)
    allocation_cycle_end = models.DateField(null=True, blank=True)

    def available_days(self):
        return self.allocated_days - self.used_days

    def __str__(self):
        return f"{self.leave_type} - {self.employee.full_name} ({self.available_days()} days available)"


class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ("annual", "Annual Leave"),
        ("sick", "Sick Leave"),
        ("family", "Family Responsibility Leave"),
        ("maternity", "Maternity Leave"),
        ("paternity", "Paternity Leave"),
        ("study", "Study Leave"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leave_requests",
        verbose_name="Employee",
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    return_date = models.DateField(null=True)
    reason = models.TextField(blank=True, null=True)
    proof = models.FileField(upload_to="leave_proofs/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def days_requested(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} ({self.status})"


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("LATE", "Late"),
        ("EXCUSED", "Excused"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_records",
    )
    date = models.DateField(default=now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PRESENT")
    leave_type = models.ForeignKey(
        LeaveAllocation, on_delete=models.SET_NULL, null=True, blank=True
    )

    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PRESENT")
    remarks = models.TextField(default="", blank=True)
    proof_document = models.FileField(upload_to="leave_proofs/", null=True, blank=True)

    class Meta:
        ordering = ["-date", "employee"]  # Default sorting by date and employee

    def clean(self):
        """Validate check-in and check-out times."""
        if self.check_in_time and self.check_out_time:
            if self.check_in_time >= self.check_out_time:
                raise ValidationError("Check-in time must be before check-out time.")

    def save(self, *args, **kwargs):
        # Check if this is a new record
        if not self.pk and not kwargs.get("force_insert", False):
            super().save(*args, **kwargs)

        if not self.pk:
            raise ValidationError("Attendance record must have a valid primary key.")

        # Call the parent save method for further processing
        super().save(*args, **kwargs)

    def __str__(self):
        """String representation of the attendance record."""
        employee_name = self.employee.full_name if self.employee else "Deleted Employee"
        return f"{employee_name} - {self.date} ({self.status})"


class AttendanceAuditLog(models.Model):
    """Model to store audit logs for attendance changes."""

    attendance = models.ForeignKey(
        AttendanceRecord, on_delete=models.CASCADE, related_name="audit_logs"
    )
    user = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=50)
    old_status = models.CharField(max_length=10, null=True, blank=True)
    new_status = models.CharField(max_length=10, null=True, blank=True)
    remarks = models.TextField(default="", blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} by {self.user or 'System'} on {self.timestamp}"
