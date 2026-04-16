frappe.ui.form.on("Task", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		if (frm.doc.status !== "Running") {
			frm.add_custom_button("Run", async () => {
				await frappe.call({
					method: "job_manager.api.run_task",
					args: { task_name: frm.doc.name },
				});

				frappe.show_alert({ message: "Task enqueued", indicator: "green" });
				frm.reload_doc();
			});
		}
	},
});
