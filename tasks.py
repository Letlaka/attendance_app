# Standard Library Imports
from datetime import datetime

# Third-Party Imports
from celery import shared_task
# Custom Imports
from .models import LeaveAllocation

@shared_task
def accumulate_annual_leave():
    today = datetime.now().date()
    if today.day == 1:  # On the first day of the month
        allocations = LeaveAllocation.objects.filter(leave_type='annual')
        for allocation in allocations:
            # Check if the employee hasn't exceeded 45 days
            if allocation.allocated_days < 45:
                allocation.allocated_days += 2
                allocation.save()
