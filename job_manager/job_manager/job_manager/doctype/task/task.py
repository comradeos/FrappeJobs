import frappe
from frappe.model.document import Document


VALID_STATUSES = {"Pending", "Running", "Done", "Failed"}
VALID_TASK_TYPES = {"fetch_weather", "fetch_currency", "custom"}


class Task(Document):
	def validate(self):
		if self.status not in VALID_STATUSES:
			frappe.throw(f"Unsupported status: {self.status}")

		if self.task_type not in VALID_TASK_TYPES:
			frappe.throw(f"Unsupported task type: {self.task_type}")

		if (self.attempts or 0) < 0:
			frappe.throw("Attempts cannot be negative")
