import json

import frappe


MAX_RETRIES = 3


def enqueue_task(task_name: str) -> dict:
	task = frappe.get_doc("Task", task_name)

	if task.status == "Running":
		frappe.throw("Task is already running")

	if task.status == "Failed" and (task.attempts or 0) >= MAX_RETRIES:
		frappe.throw("Task reached maximum retry limit")

	task.status = "Pending"
	task.error_message = None
	task.save(ignore_permissions=True)

	frappe.enqueue(
		"job_manager.workers.execute_task",
		queue="default",
		task_name=task.name,
		enqueue_after_commit=True,
	)

	return {"task": task.name, "status": task.status}


def get_stats() -> dict:
	rows = frappe.db.sql(
		"""
		select status, count(*) as count
		from `tabTask`
		group by status
		""",
		as_dict=True,
	)

	stats = {"Pending": 0, "Running": 0, "Done": 0, "Failed": 0}
	for row in rows:
		stats[row.status] = int(row.count)

	total = sum(stats.values())
	done = stats["Done"]
	failed = stats["Failed"]

	return {
		"total": total,
		"status_counts": stats,
		"success_rate": (done / total) if total else 0,
		"failure_rate": (failed / total) if total else 0,
	}


def parse_payload(payload: str | None) -> dict:
	if not payload:
		return {}

	try:
		data = json.loads(payload)
	except json.JSONDecodeError as exc:
		frappe.throw(f"Invalid JSON payload: {exc}")

	if not isinstance(data, dict):
		frappe.throw("Payload must be a JSON object")

	return data
