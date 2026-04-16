import frappe

from job_manager import services


@frappe.whitelist()
def run_task(task_name: str | None = None):
	task_name = task_name or frappe.form_dict.get("task_name")
	if not task_name:
		frappe.throw("task_name is required")

	return services.enqueue_task(task_name)


@frappe.whitelist(allow_guest=True)
def stats():
	return services.get_stats()
