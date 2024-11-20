# Third-Party Imports
from django.contrib import admin

# Custom Imports
from .models import AttendanceRecord, AttendanceAuditLog, LeaveAllocation, LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ["employee", "leave_type", "start_date", "end_date", "status"]
    list_filter = ["leave_type", "status"]
    search_fields = ["employee__username", "reason"]


@admin.register(LeaveAllocation)
class LeaveAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "leave_type",
        "allocated_days",
        "used_days",
        "available_days",
    )
    list_filter = ("leave_type",)
    search_fields = ("employee__full_name", "leave_type")


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "date",
        "status",
        "leave_type",
        "check_in_time",
        "check_out_time",
        "remarks",
    )

    actions = ["mark_excused"]
    list_filter = ("status", "leave_type")
    search_fields = ("employee__full_name", "date", "status")
    ordering = ("-date",)

    def mark_excused(self, request, queryset):
        updated = queryset.update(status="EXCUSED")
        self.message_user(request, f"{updated} records marked as excused.")

    mark_excused.short_description = "Mark selected records as Excused"


@admin.register(AttendanceAuditLog)
class AttendanceAuditLogAdmin(admin.ModelAdmin):
    list_display = ("attendance", "user", "action", "timestamp")
    list_filter = ("action", "timestamp")
    search_fields = ("attendance__employee__full_name", "user__username", "action")
    ordering = ("-timestamp",)
