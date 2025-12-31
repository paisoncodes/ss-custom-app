frappe.ui.form.on("Material Request", {
	item_group: function (frm) {
		frm.clear_table("items");
		frm.refresh_field("items");

		frm.fields_dict["items"].grid.get_field("item_code").get_query = function (doc, cdt, cdn) {
			return {
				filters: {
					item_group: frm.doc.item_group,
				},
			};
		};
	},
});
