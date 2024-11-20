from datetime import timedelta, timezone
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    TemplateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from attendance_app.models import (
    AttendanceRecord,
    AttendanceAuditLog,
    LeaveAllocation,
    LeaveRequest,
)
from attendance_app.forms import LeaveRequestForm
from django.urls import reverse_lazy
from django.contrib import messages

logger = logging.getLogger(__name__)


class LeaveRequestCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = "attendance_app/leave_request_form.html"
    success_url = reverse_lazy("attendance_app:leave_request_list")

    def form_valid(self, form):
        form.instance.employee = self.request.user
        logger.info(f"Leave request created by {self.request.user.username}")
        return super().form_valid(form)


class LeaveRequestListView(LoginRequiredMixin, ListView):
    model = LeaveRequest
    template_name = "attendance_app/leave_request_list.html"
    context_object_name = "leave_requests"

    def get_queryset(self):
        return LeaveRequest.objects.filter(employee=self.request.user)


class LeaveRequestApprovalListView(PermissionRequiredMixin, ListView):
    permission_required = "attendance_app.can_approve_leave"
    model = LeaveRequest
    template_name = "attendance_app/leave_request_approval_list.html"
    context_object_name = "leave_requests"

    def get_queryset(self):
        return LeaveRequest.objects.filter(status="pending")


class LeaveRequestApproveView(PermissionRequiredMixin, UpdateView):
    permission_required = "attendance_app.can_approve_leave"
    model = LeaveRequest
    fields = []
    template_name = "attendance_app/leave_request_confirm.html"
    success_url = reverse_lazy("attendance_app:leave_request_approval_list")

    def form_valid(self, form):
        leave_request = form.instance
        leave_request.status = "approved"
        leave_request.reviewed_by = self.request.user
        leave_request.reviewed_at = timezone.now()

        # Update LeaveAllocation
        leave_allocation = leave_request.leave_type
        if leave_allocation.leave_type != "study":
            leave_allocation.used_days += leave_request.days_requested
            leave_allocation.save()

        # Optionally, create an AttendanceRecord for the leave period
        for single_date in (
            leave_request.start_date + timedelta(n)
            for n in range(leave_request.days_requested)
        ):
            AttendanceRecord.objects.create(
                employee=leave_request.employee,
                date=single_date,
                status="LEAVE",
                leave_type=leave_allocation,
                remarks=leave_request.reason,
            )

        return super().form_valid(form)


class LeaveRequestView(CreateView):
    model = AttendanceRecord
    template_name = "attendance_app/leave_request_form.html"
    form_class = LeaveRequestForm

    def form_valid(self, form):
        leave_allocation = get_object_or_404(
            LeaveAllocation,
            employee=self.request.user.employee,
            leave_type=form.cleaned_data["leave_type"],
        )

        if leave_allocation.available_days() < form.cleaned_data["days_requested"]:
            form.add_error("days_requested", "Not enough leave days available.")
            return self.form_invalid(form)

        leave_allocation.used_days += form.cleaned_data["days_requested"]
        leave_allocation.save()
        return super().form_valid(form)


class AttendanceListView(LoginRequiredMixin, ListView):
    model = AttendanceRecord
    template_name = "attendance_app/attendance_list.html"
    context_object_name = "attendance_records"
    paginate_by = 10

    def get_queryset(self):
        try:
            logger.info(f"Attendance list viewed by {self.request.user}")
            return AttendanceRecord.objects.filter(
                pk__isnull=False
            )  # Exclude invalid records
        except Exception as e:
            logger.error(f"Error fetching attendance list: {e}")
            raise ValidationError("Unable to fetch attendance records.")


class AttendanceDetailView(LoginRequiredMixin, DetailView):
    model = AttendanceRecord
    template_name = "attendance_app/attendance_detail.html"
    context_object_name = "attendance_record"

    def get(self, request, *args, **kwargs):
        logger.info(
            f"Attendance details viewed for record {self.get_object().id} by {request.user}"
        )
        return super().get(request, *args, **kwargs)


class AttendanceCreateView(LoginRequiredMixin, CreateView):
    model = AttendanceRecord
    template_name = "attendance_app/attendance_form.html"
    fields = [
        "employee",
        "date",
        "check_in_time",
        "check_out_time",
        "status",
        "remarks",
    ]
    success_url = reverse_lazy("attendance_app:attendance_list")

    def form_valid(self, form):
        try:
            form.instance.user = self.request.user
            logger.info(f"Attendance created by {self.request.user}")
            return super().form_valid(form)
        except Exception as e:
            logger.error(f"Error creating attendance: {e}")
            form.add_error(None, "An error occurred while saving the record.")
            return self.form_invalid(form)


class AttendanceUpdateView(LoginRequiredMixin, UpdateView):
    model = AttendanceRecord
    template_name = "attendance_app/attendance_form.html"
    fields = ["check_in_time", "check_out_time", "status", "remarks"]
    success_url = reverse_lazy("attendance_app:attendance_list")

    def form_valid(self, form):
        form.instance.user = self.request.user  # Pass user to save method
        logger.info(f"Attendance updated by {self.request.user}")
        return super().form_valid(form)


class AttendanceAuditLogListView(LoginRequiredMixin, ListView):
    model = AttendanceAuditLog
    template_name = "attendance_app/audit_logs.html"
    context_object_name = "audit_logs"
    paginate_by = 10


class AttendanceDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = AttendanceRecord
    template_name = "attendance_app/attendance_confirm_delete.html"
    success_url = reverse_lazy("attendance_app:attendance_list")
    success_message = "Attendance record deleted successfully."

    def delete(self, request, *args, **kwargs):
        """Override delete to log the user and create an audit trail."""
        attendance = self.get_object()
        logger.warning(
            f"Attendance record for {attendance.employee.full_name} on {attendance.date} deleted by {self.request.user}"
        )

        # Create an audit log entry
        AttendanceAuditLog.objects.create(
            attendance=attendance,
            user=self.request.user,
            action="Deleted",
            old_status=attendance.status,
            new_status="N/A",
            remarks=f"Deleted attendance record for {attendance.employee.full_name} on {attendance.date}",
        )

        messages.warning(request, self.success_message)
        return super().delete(request, *args, **kwargs)


class ManagerDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "attendance_app.can_approve_leave"
    template_name = "attendance_app/manager_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pending_leave_requests"] = LeaveRequest.objects.filter(
            status="pending"
        )
        context["leave_summary"] = LeaveAllocation.objects.all()
        return context
