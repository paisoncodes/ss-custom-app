app_name = "manufacturing_management"
app_title = "Manufacturing Management"
app_publisher = "Olatunji Komolafe"
app_description = "App to Manage Manufacturing flow"
app_email = "iamkomolafe.o.s@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "manufacturing_management",
# 		"logo": "/assets/manufacturing_management/logo.png",
# 		"title": "Manufacturing Management",
# 		"route": "/manufacturing_management",
# 		"has_permission": "manufacturing_management.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/manufacturing_management/css/manufacturing_management.css"
# app_include_js = "/assets/manufacturing_management/js/manufacturing_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/manufacturing_management/css/manufacturing_management.css"
# web_include_js = "/assets/manufacturing_management/js/manufacturing_management.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "manufacturing_management/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Stock Entry": "public/js/stock_entry.js",
    "Production Plan": "public/js/production_plan.js",
    "Material Request": "public/js/material_request.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "manufacturing_management/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "manufacturing_management.utils.jinja_methods",
# 	"filters": "manufacturing_management.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "manufacturing_management.install.before_install"
# after_install = "manufacturing_management.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "manufacturing_management.uninstall.before_uninstall"
# after_uninstall = "manufacturing_management.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "manufacturing_management.utils.before_app_install"
# after_app_install = "manufacturing_management.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "manufacturing_management.utils.before_app_uninstall"
# after_app_uninstall = "manufacturing_management.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "manufacturing_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Work Order": {
        "before_insert": "manufacturing_management.utils.server_scripts.work_order_before_insert",
    },
    "Warehouse": {
        "before_save": "manufacturing_management.utils.server_scripts.warehouse_before_save",
    },
    "Stock Entry": {
        "on_submit": "manufacturing_management.utils.server_scripts.stock_entry_on_submit",
        "validate": "manufacturing_management.utils.server_scripts.stock_entry_validate",
    },
    "Purchase Order": {
        "validate": "manufacturing_management.utils.server_scripts.purchase_order_validate",
    },
    "Purchase Receipt": {
        "validate": "manufacturing_management.utils.server_scripts.purchase_receipt_validate",
    },
    "Purchase Invoice": {
        "validate": "manufacturing_management.utils.server_scripts.purchase_invoice_validate",
    },
    "Expense Claim": {
        "validate": "manufacturing_management.utils.server_scripts.expense_claim_validate",
    },
    "Journal Entry": {
        "validate": "manufacturing_management.utils.server_scripts.journal_entry_validate",
    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"manufacturing_management.tasks.all"
# 	],
# 	"daily": [
# 		"manufacturing_management.tasks.daily"
# 	],
# 	"hourly": [
# 		"manufacturing_management.tasks.hourly"
# 	],
# 	"weekly": [
# 		"manufacturing_management.tasks.weekly"
# 	],
# 	"monthly": [
# 		"manufacturing_management.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "manufacturing_management.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "manufacturing_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "manufacturing_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["manufacturing_management.utils.before_request"]
# after_request = ["manufacturing_management.utils.after_request"]

# Job Events
# ----------
# before_job = ["manufacturing_management.utils.before_job"]
# after_job = ["manufacturing_management.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"manufacturing_management.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
