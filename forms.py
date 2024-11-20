# Third-Party Imports
from django import forms

# Custom Imports
from attendance_app.models import LeaveRequest
from employees_app.models import Employee


class LeaveRequestForm(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Employee",
    )

    class Meta:
        model = LeaveRequest
        fields = [
            "employee",
            "leave_type",
            "start_date",
            "end_date",
            "return_date",
            "reason",
            "proof",
        ]
        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "return_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        return_date = cleaned_data.get("return_date")
        leave_type = cleaned_data.get("leave_type")
        employee = cleaned_data.get("employee")

        # Validate date range
        if start_date and end_date:
            if end_date < start_date:
                self.add_error("end_date", "End date cannot be before start date.")

            days_requested = (end_date - start_date).days + 1
            cleaned_data["days_requested"] = days_requested

            # Check leave allocation
            leave_allocation = employee.leave_allocations.filter(
                leave_type=leave_type
            ).first()
            if leave_allocation and leave_allocation.available_days() < days_requested:
                self.add_error(None, "Not enough leave days available.")

        # Additional validation for proof documents
        if leave_type in [
            "sick",
            "family",
            "maternity",
            "paternity",
            "study",
        ] and not cleaned_data.get("proof"):
            self.add_error("proof", "Proof document is required for this leave type.")

        return cleaned_data
