from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry
import frappe
from datetime import datetime


def sales_invoice_before_insert(doc, _):
    if doc.pos_profile and doc.update_stock:
        pos_profile = frappe.get_doc("POS Profile", doc.pos_profile)
        if pos_profile.warehouse:
            doc.set_warehouse = pos_profile.warehouse


def sales_invoice_on_update(doc, _):
    if doc.set_warehouse and doc.packed_items:
        for item in doc.packed_items:
            if item.warehouse != doc.set_warehouse:
                frappe.db.set_value(
                    "Packed Item", item.name, "warehouse", doc.set_warehouse
                )


def work_order_before_insert(doc, _):
    if "cake" in doc.branch.lower() or "bread" in doc.branch.lower():
        found_source_warehouse = frappe.get_all(
            "Warehouse",
            fields=["name"],
            filters=[
                ["branch", "=", doc.branch],
                ["name", "like", "%factory%"],
            ],
            limit=1,
        )

        found_target_warehouse = frappe.get_all(
            "Warehouse",
            fields=["name"],
            filters=[
                ["branch", "=", doc.branch],
                ["name", "like", "%store%"],
            ],
            limit=1,
        )
    else:
        found_source_warehouse = frappe.get_all(
            "Warehouse",
            fields=["name"],
            filters=[
                ["branch", "=", doc.branch],
                ["name", "like", "%outlet%"],
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
        frappe.throw("Branch on Work Order not is linked to any Outlet")
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
    doc_data = make_stock_entry(doc.name, "Manufacture", qty=doc.qty)
    del doc_data["name"]
    del doc_data["__islocal"]
    del doc_data["__unsaved"]
    del doc_data["owner"]
    doc_data.custom_stock_entry_purpose = "MANUFACTURING"
    doc_data.stock_entry_type = "Manufacture"
    doc_data.from_warehouse = doc.source_warehouse
    doc_data.to_warehouse = doc.fg_warehouse
    doc_data.cost_center = doc.cost_center
    doc_data.business_segment = doc.business_segment
    manufacture_doc = frappe.get_doc(doc_data)
    manufacture_doc.insert(ignore_permissions=True)


SOURCE_WAREHOUSES = [
    "Bread Factory - SSC",
    "Bread Store - SSC",
    "Bread Store - SSC",
    "Cake Factory - SSC",
    "Cake Store - SSC",
    "Central Kitchen - SSC",
    "Central Warehouse - SSC",
    "Factory - SSC",
    "Food Processing Unit - SSC",
    "Home Kitchen/Spice Center - SSC",
]


def stock_entry_validate(doc, _):
    for item in doc.items:
        item.cost_center = doc.cost_center
        item.business_segment = doc.business_segment
        if doc.stock_entry_type in ["Material Transfer", "Manufacture"]:
            item.difference_account = "522116 - Stock Adjustment - SSC"


def override_difference_account(doc, method):
    if doc.stock_entry_type == "Manufacture":
        for item in doc.items:
            item.difference_account = "522116 - Stock Adjustment - SSC"

def stock_entry_on_update(doc, _):
    for item in doc.items:
        if (
            doc.stock_entry_type in ["Material Transfer", "Manufacture"]
            and item.difference_account != "522116 - Stock Adjustment - SSC"
        ):
            item.difference_account = "522116 - Stock Adjustment - SSC"


def purchase_order_validate(doc, _):
    for item in doc.items:
        item.cost_center = doc.cost_center
        item.business_segment = doc.business_segment


def purchase_receipt_validate(doc, _):
    for item in doc.items:
        item.cost_center = doc.cost_center
        item.business_segment = doc.business_segment


def purchase_invoice_validate(doc, _):
    for item in doc.items:
        item.cost_center = doc.cost_center
        item.business_segment = doc.business_segment


def expense_claim_validate(doc, _):
    for expense in doc.expenses:
        expense.cost_center = doc.cost_center
        expense.business_segment = doc.business_segment


# def journal_entry_validate(doc, _):
#     for expense in doc.accounts:
#         expense.cost_center = doc.cost_center
#         expense.business_segment = doc.business_segment

def journal_entry_validate(doc, _):
    for expense in doc.accounts:
        if not expense.cost_center:
            expense.cost_center = doc.cost_center
        if not expense.business_segment:
            expense.business_segment = doc.business_segment


# Leave Allowance Automation
LEAVE_POLICY_ALLOWANCE_PERCENT = {
    "HR-LPOL-2026-00001": 70,
    "HR-LPOL-2026-00002": 60,
    "HR-LPOL-2026-00003": 50,
}


def leave_application_on_update(doc, _):
    if doc.status != "Approved":
        return

    employee = doc.employee
    leave_from = doc.from_date

    # Get the employee's leave policy from their active Leave Policy Assignment
    leave_policy_assignment = frappe.get_all(
        "Leave Policy Assignment",
        filters={
            "employee": employee,
            "docstatus": 1,
            "effective_from": ["<=", leave_from],
            "effective_to": [">=", leave_from],
        },
        fields=["leave_policy", "effective_from", "effective_to"],
        order_by="effective_from desc",
        limit=1,
    )

    if not leave_policy_assignment:
        return

    assignment = leave_policy_assignment[0]
    leave_policy = assignment.leave_policy
    period_from = assignment.effective_from
    period_to = assignment.effective_to

    if leave_policy not in LEAVE_POLICY_ALLOWANCE_PERCENT:
        return

    # Check if leave allowance Additional Salary already exists for this employee
    # within the same leave period
    existing = frappe.get_all(
        "Additional Salary",
        filters={
            "employee": employee,
            "salary_component": "Leave Allowance",
            "payroll_date": ["between", [period_from, period_to]],
            "docstatus": ["!=", 2],
        },
        limit=1,
    )

    if existing:
        return

    # Get employee's monthly gross from Salary Structure Assignment
    salary_assignment = frappe.get_all(
        "Salary Structure Assignment",
        filters={
            "employee": employee,
            "docstatus": 1,
            "from_date": ["<=", leave_from],
        },
        fields=["base"],
        order_by="from_date desc",
        limit=1,
    )

    if not salary_assignment:
        frappe.throw(
            f"No active Salary Structure Assignment found for employee {employee}. "
            "Cannot calculate leave allowance."
        )

    monthly_gross = salary_assignment[0].base
    percent = LEAVE_POLICY_ALLOWANCE_PERCENT[leave_policy]
    allowance_amount = monthly_gross * percent / 100

    additional_salary = frappe.new_doc("Additional Salary")
    additional_salary.employee = employee
    additional_salary.salary_component = "Leave Allowance"
    additional_salary.amount = allowance_amount
    additional_salary.payroll_date = leave_from
    additional_salary.company = doc.company
    additional_salary.overwrite_salary_structure_amount = 0
    additional_salary.ref_doctype = "Leave Application"
    additional_salary.ref_docname = doc.name
    additional_salary.insert(ignore_permissions=True)
    additional_salary.submit()

    frappe.msgprint(
        f"Leave Allowance of {allowance_amount:,.2f} ({percent}% of monthly gross) "
        f"has been generated for {doc.employee_name}.",
        title="Leave Allowance Created",
        indicator="green",
    )


def stock_entry_on_cancel(doc, _):
    try:
        linked_journal_entries = frappe.get_all(
            "Journal Entry",
            filters={"stock_entry": doc.name},
            fields=["name"],
        )
        for je in linked_journal_entries:
            je_doc = frappe.get_doc("Journal Entry", je.name)
            je_doc.cancel()
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Stock Entry on_cancel Error",
            reference_doctype=doc.doctype,
            reference_name=doc.name,
        )


def stock_entry_on_submit(doc, _):
    try:
        if (
            doc.from_warehouse in SOURCE_WAREHOUSES
            and (
                "outlet" in doc.to_warehouse.lower()
                or "restaurant" in doc.to_warehouse.lower()
            )
            and doc.stock_entry_type == "Material Transfer"
        ):
            source_warehouse = frappe.get_doc("Warehouse", doc.from_warehouse)
            target_warehouse = frappe.get_doc("Warehouse", doc.to_warehouse)
            journal_doc = frappe.new_doc("Journal Entry")
            journal_doc.voucher_type = "Journal Entry"
            journal_doc.naming_series = "ACC-JV-.YYYY.-"
            journal_doc.company = doc.company
            journal_doc.posting_date = datetime.now().date()
            journal_doc.is_opening = "No"
            journal_doc.cost_center = doc.cost_center
            journal_doc.business_segment = doc.business_segment
            journal_doc.remark = f"Stock Transfer from {source_warehouse.warehouse_name} to {target_warehouse.warehouse_name} via Stock Entry {doc.name}"
            journal_doc.stock_entry = doc.name

            for i in range(2):
                if i == 0:
                    journal_doc.append(
                        "accounts",
                        {
                            "account": target_warehouse.custom_stock_recovery_ledger,
                            "debit_in_account_currency": doc.total_outgoing_value,
                        },
                    )
                else:
                    journal_doc.append(
                        "accounts",
                        {
                            "account": source_warehouse.custom_stock_recovery_ledger,
                            "credit_in_account_currency": doc.total_outgoing_value,
                        },
                    )

            journal_doc.insert(ignore_permissions=True)
            journal_doc.submit()
        else:
            frappe.log_error(
                "Journal Entry not created",
                "Stock Entry - Warehouse Condition not met",
                reference_doctype=doc.doctype,
                reference_name=doc.name,
            )
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Stock Entry on_submit Error",
            reference_doctype=doc.doctype,
            reference_name=doc.name,
        )
