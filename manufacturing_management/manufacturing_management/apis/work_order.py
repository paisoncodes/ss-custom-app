import frappe


def submit_work_orders_for_production_plan(production_plan_id):
    work_orders = frappe.get_all(
        "Work Order",
        filters={"production_plan": production_plan_id, "docstatus": 0},
        fields=["name"],
    )
    for wo in work_orders:
        work_order_doc = frappe.get_doc("Work Order", wo.name)
        work_order_doc.submit()
    return f"Submitted {len(work_orders)} Work Orders for Production Plan {production_plan_id}"
