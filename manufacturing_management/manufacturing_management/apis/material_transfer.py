import frappe
from datetime import datetime

MATERIAL_TRANSFER_WAREHOUSE_SQL_QUERY = """
    SELECT name
    FROM `tabWarehouse`
    WHERE branch = %s
    AND LOWER(name) LIKE %s
    AND name != %s
    LIMIT 1
"""

@frappe.whitelist()
def create_material_transfer_from_production_plan(production_plan_id):
    production_plan = frappe.get_doc("Production Plan", production_plan_id)
    branch = production_plan.branch
    today = datetime.now()
    source_warehouse = frappe.db.sql(
        MATERIAL_TRANSFER_WAREHOUSE_SQL_QUERY,
        (branch, "%outlet%", production_plan.name),
    )
    if not source_warehouse:
        frappe.throw("Branch on Production Plan not is linked to any Outlet")

    target_warehouse = frappe.db.sql(
        MATERIAL_TRANSFER_WAREHOUSE_SQL_QUERY,
        (branch, "%production%", production_plan.name),
    )
    if not target_warehouse:
        frappe.throw(
            "Branch on Production Plan not is linked to any Production Warehouse"
        )

    material_transfer = frappe.new_doc("Stock Entry")
    material_transfer.production_plan = production_plan.name
    material_transfer.transfer_type = "Material Transfer"
    material_transfer.from_warehouse = source_warehouse[0][0]
    material_transfer.to_warehouse = target_warehouse[0][0]
    material_transfer.posting_date = today.date()
    material_transfer.posting_time = today.time()
    material_transfer.custom_stock_entry_purpose = "INTRA OUTLET TRANSFER"

    for item in production_plan.mr_items:
        valuation_rate = frappe.db.get_value(
            "Bin",
            {
                "item_code": item.item_code,
                "warehouse": material_transfer.from_warehouse,
            },
            "valuation_rate",
        )
        material_transfer.append(
            "items",
            {
                "item_code": item.item_code,
                "qty": item.quantity,
                "uom": item.uom,
                "s_warehouse": material_transfer.from_warehouse,
                "t_warehouse": material_transfer.to_warehouse,
                "basic_rate": valuation_rate or 0,
            },
        )

    material_transfer.insert(ignore_permissions=True)
    return f"Material Transfer Created with ID: {material_transfer.name}"
