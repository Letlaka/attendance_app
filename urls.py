# Third-Party Imports
from django.urls import path

# Custom Imports
from attendance_app.views import (
    AttendanceListView,
    AttendanceDetailView,
    AttendanceCreateView,
    AttendanceUpdateView,
    AttendanceAuditLogListView,
    AttendanceDeleteView,
    LeaveRequestView,
    LeaveRequestCreateView,
    LeaveRequestListView,
    LeaveRequestApprovalListView,
    LeaveRequestApproveView,
    ManagerDashboardView,
)

app_name = "attendance_app"

urlpatterns = [
    path('list/', AttendanceListView.as_view(), name='attendance_list'),
    path('<int:pk>/', AttendanceDetailView.as_view(), name='attendance_detail'),
    path('create/', AttendanceCreateView.as_view(), name='attendance_create'),
    path('<int:pk>/update/', AttendanceUpdateView.as_view(), name='attendance_update'),
    path('audit-logs/', AttendanceAuditLogListView.as_view(), name='audit_logs'),
    path('<int:pk>/delete/', AttendanceDeleteView.as_view(), name='attendance_delete'),
    path('leave/request/', LeaveRequestView.as_view(), name='leave_request'),
    path('leave/create/', LeaveRequestCreateView.as_view(), name='leave_request_create'),
    path('leave/requests/', LeaveRequestListView.as_view(), name='leave_request_list'),
    path('leave/approvals/', LeaveRequestApprovalListView.as_view(), name='leave_request_approvals'),
    path('leave/approve/<int:pk>/', LeaveRequestApproveView.as_view(), name='leave_request_approve'),
    path('dashboard/', ManagerDashboardView.as_view(), name='manager_dashboard'),



]
