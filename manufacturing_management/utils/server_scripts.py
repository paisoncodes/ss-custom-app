import frappe
from datetime import datetime


def work_order_before_insert(doc, _):
    found_source_warehouse = frappe.get_all(
        "Warehouse",
        fields=["name"],
        filters=[
            ["branch", "=", doc.branch],
            ["name", "like", "%production%"],
        ],
        limit=1,
    )

    found_target_warehouse = frappe.get_all(
        "Warehouse",
        fields=["name"],
        filters=[
            ["branch", "=", doc.branch],
            ["name", "like", "%restaurant%"],
        ],
        limit=1,
    )
    if not found_source_warehouse:
        frappe.throw("Branch on Work Order not is linked to any Production Warehouse")
    if not found_target_warehouse:
        frappe.throw("Branch on Work Order not is linked to any Restaurant")

    source_wh = found_source_warehouse[0].name
    target_wh = found_target_warehouse[0].name

    doc.source_warehouse = source_wh
    doc.fg_warehouse = target_wh

    if source_wh:
        for row in doc.required_items:
            row.source_warehouse = source_wh


WAREHOUSE_SQL_QUERY = """
    SELECT name
    FROM `tabWarehouse`
    WHERE branch = %s
    AND LOWER(name) LIKE %s
    AND name != %s
    LIMIT 1
"""


def warehouse_before_save(doc, _):
    if "outlet" in doc.warehouse_name.lower():
        exists = frappe.db.sql(
            WAREHOUSE_SQL_QUERY,
            (doc.branch, "%outlet%", doc.name),
        )
        if exists:
            frappe.throw(
                "An outlet already exists with this branch.\nBranches should be unique by outlets"
            )

    elif "production" in doc.warehouse_name.lower():
        exists = frappe.db.sql(
            WAREHOUSE_SQL_QUERY,
            (doc.branch, "%production%", doc.name),
        )
        if exists:
            frappe.throw(
                "An production warehouse already exists with this branch.\nBranches should be unique by production warehouses"
            )

    elif "transit" in doc.warehouse_name.lower():
        exists = frappe.db.sql(
            WAREHOUSE_SQL_QUERY,
            (doc.branch, "%transit%", doc.name),
        )
        if exists:
            frappe.throw(
                "A transit warehouse already exists with this branch.\nBranches should be unique by transit warehouses"
            )

    elif "restaurant" in doc.warehouse_name.lower():
        exists = frappe.db.sql(
            WAREHOUSE_SQL_QUERY,
            (doc.branch, "%restaurant%", doc.name),
        )
        if exists:
            frappe.throw(
                "A restaurant already exists with this branch.\nBranches should be unique by restaurants"
            )


def create_manufacture_document_from_work_order(doc, _):
    response = frappe.call(
        "erpnext.manufacturing.doctype.work_order.work_order.make_stock_entry",
        args={
            "work_order_id": doc.name,
            "purpose": "Manufacture",
            "qty": doc.qty,
        },
    )
    if response and response.message:
        doc_data = response.message
        del doc_data["name"]
        del doc_data["__islocal"]
        del doc_data["__unsaved"]
        del doc_data["owner"]
        doc_data.custom_stock_entry_purpose = "MANUFACTURING"
        doc_data.stock_entry_type = "Manufacture"
        manufacture_doc = frappe.get_doc(doc_data)
        manufacture_doc.insert(ignore_permissions=True)
    else:
        frappe.throw("Could not create Manufacture Stock Entry from Work Order")


SOURCE_WAREHOUSES = [
    "Bread Factory - SSC",
    "Bread Store - SSC",
    "Cake Factory - SSC",
    "Cake Store - SSC",
    "Central Kitchen - SSC",
    "Central Warehouse - SSC",
    "Factory - SSC",
    "Food Processing Unit - SSC",
    "Home Kitchen/Spice Center - SSC",
]


def stock_entry_on_submit(doc, _):
    if doc.from_warehouse in SOURCE_WAREHOUSES and (
        "outlet" in doc.to_warehouse.lower() or "restaurant" in doc.to_warehouse.lower()
    ):
        source_warehouse = frappe.get_doc("Warehouse", doc.from_warehouse)
        target_warehouse = frappe.get_doc("Warehouse", doc.from_warehouse)
        journal_doc = frappe.new_doc("Journal Entry")
        journal_doc.voucher_type = "Journal Entry"
        journal_doc.naming_series = "ACC-JV-.YYYY.-"
        journal_doc.company = doc.company
        journal_doc.posting_date = datetime.now().date()
        journal_doc.is_opening = "No"
        journal_doc.cost_center = source_warehouse.cost_center
        journal_doc.business_segment = "Restaurant"

        for i in range(2):
            if i == 0:
                journal_doc.append(
                    "accounts",
                    {
                        "account": source_warehouse.custom_stock_recovery_ledger,
                        "debit_in_account_currency": doc.total_outgoing_value,
                    },
                )
            else:
                journal_doc.append(
                    "accounts",
                    {
                        "account": target_warehouse.custom_stock_recovery_ledger,
                        "credit_in_account_currency": doc.total_outgoing_value,
                    },
                )

        journal_doc.insert(ignore_permissions=True)
        journal_doc.submit()
