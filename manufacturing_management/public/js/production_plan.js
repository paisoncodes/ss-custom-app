frappe.ui.form.on("Production Plan", {
	refresh(frm) {
		frm.toggle_display("get_material_request", false);
		frm.add_custom_button("Submit Work Orders", () => {
			frappe.call({
				method: "manufacturing_management.manufacturing_management.apis.work_order.submit_work_orders_for_production_plan",
				args: { production_plan_id: frm.doc.name },
				freeze: true,
				freeze_message: __("Submitting Work Orders..."),
				callback: function (r) {
					if (r.message) {
						frappe.show_alert(
							{
								message: __(r.message),
								indicator: "green",
							},
							5
						);
					}
				},
			});
		});
	},

	fetch_material_request(frm) {
		if (!frm.doc.branch) {
			frappe.msgprint(__("Please select a Branch first."));
			return;
		}

		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Material Request",
				filters: {
					branch: frm.doc.branch,
					docstatus: 1,
					status: "Pending",
				},
				fields: ["name", "transaction_date"],
			},
			callback: function (r) {
				if (r.message && r.message.length > 0) {
					frm.clear_table("material_requests");

					r.message.forEach((req) => {
						let row = frm.add_child("material_requests");
						row.material_request = req.name;
						row.material_request_date = req.transaction_date;
					});

					frm.refresh_field("material_requests");
				} else {
					frappe.msgprint(__("No Material Requests found for this Branch."));
				}
			},
		});
	},
});
