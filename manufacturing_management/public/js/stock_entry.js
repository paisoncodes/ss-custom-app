frappe.ui.form.on("Stock Entry", {
	before_save: function (frm) {
		if (!frm.doc.branch) {
			return frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Employee",
					filters: { user_id: frappe.session.user },
					fieldname: ["branch"],
				},
				callback: function (r) {
					if (r.message && r.message.branch) {
						frm.set_value("branch", r.message.branch);
					}
				},
			});
		}
	},
	validate(frm) {
		frm.doc.items.forEach(function (item) {
			if (["Material Transfer", "Manufacture"].includes(frm.doc.stock_entry_type)) {
				item.difference_account = "522116 - Stock Adjustment - SSC";
			}
		});
	}
});
