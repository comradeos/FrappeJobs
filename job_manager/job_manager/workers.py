import json
import time
from datetime import UTC, datetime

import frappe

from job_manager.services import MAX_RETRIES, parse_payload


def execute_task(task_name: str):
	task = frappe.get_doc("Task", task_name)

	try:
		_set_running(task)
		payload = parse_payload(task.payload)
		result = _run_task(task.task_type, payload)
		_set_done(task, result)
	except Exception:
		frappe.log_error(frappe.get_traceback(), f"Task execution failed: {task_name}")
		_set_failed(task)
		if (task.attempts or 0) < MAX_RETRIES:
			frappe.enqueue(
				"job_manager.workers.execute_task",
				queue="default",
				task_name=task.name,
				enqueue_after_commit=True,
			)


def _set_running(task):
	task.status = "Running"
	task.error_message = None
	task.save(ignore_permissions=True)


def _set_done(task, result: dict):
	task.status = "Done"
	task.result = json.dumps(result, ensure_ascii=True)
	task.error_message = None
	task.save(ignore_permissions=True)


def _set_failed(task):
	task.status = "Failed"
	task.attempts = (task.attempts or 0) + 1
	task.error_message = frappe.get_traceback(with_context=True)
	task.save(ignore_permissions=True)


def _run_task(task_type: str, payload: dict) -> dict:
	if task_type == "fetch_weather":
		return _fetch_weather(payload)
	if task_type == "fetch_currency":
		return _fetch_currency(payload)
	if task_type == "custom":
		return _run_custom(payload)

	raise ValueError(f"Unsupported task type: {task_type}")


def _fetch_weather(payload: dict) -> dict:
	city = payload.get("city", "Kyiv")
	units = payload.get("units", "metric")
	return {
		"provider": "mock",
		"city": city,
		"units": units,
		"temperature": 22.5,
		"condition": "clear",
		"fetched_at": datetime.now(UTC).isoformat(),
	}


def _fetch_currency(payload: dict) -> dict:
	base = payload.get("base", "USD")
	target = payload.get("target", "EUR")
	return {
		"provider": "mock",
		"base": base,
		"target": target,
		"rate": 0.92,
		"fetched_at": datetime.now(UTC).isoformat(),
	}


def _run_custom(payload: dict) -> dict:
	delay = int(payload.get("sleep_seconds", 1))
	delay = min(max(delay, 0), 10)
	time.sleep(delay)
	return {
		"provider": "custom",
		"sleep_seconds": delay,
		"completed_at": datetime.now(UTC).isoformat(),
	}
