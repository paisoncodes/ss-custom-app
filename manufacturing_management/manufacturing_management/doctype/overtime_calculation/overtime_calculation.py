import calendar

import frappe
from frappe.model.document import Document


class OvertimeCalculation(Document):
    def validate(self):
        self.fetch_monthly_gross()
        self.calculate_hourly_rate()
        self.calculate_total_overtime()

    def fetch_monthly_gross(self):
        salary_assignment = frappe.get_all(
            "Salary Structure Assignment",
            filters={
                "employee": self.employee,
                "docstatus": 1,
                "from_date": ["<=", self.payroll_date],
            },
            fields=["base"],
            order_by="from_date desc",
            limit=1,
        )

        if not salary_assignment:
            frappe.throw(
                f"No active Salary Structure Assignment found for employee {self.employee}."
            )

        self.monthly_gross = salary_assignment[0].base

    def calculate_hourly_rate(self):
        # Days in the month of the payroll date
        payroll_date = self.payroll_date
        if isinstance(payroll_date, str):
            payroll_date = frappe.utils.getdate(payroll_date)

        days_in_month = calendar.monthrange(payroll_date.year, payroll_date.month)[1]

        # Hourly rate = (monthly gross / days in month) / 8
        self.hourly_rate = (self.monthly_gross / days_in_month) / 8

    def calculate_total_overtime(self):
        self.total_overtime = self.hourly_rate * self.overtime_hours
