import frappe
from frappe.utils import now

# 🔹 Item list with Batch
@frappe.whitelist()
def get_items():
    return frappe.db.sql("""
        SELECT 
            i.item_code,
            i.item_name,
            b.name as batch_no
        FROM `tabItem` i
        LEFT JOIN `tabBatch` b
        ON b.item = i.name
    """, as_dict=True)


# 🔹 Stock data with Batch
@frappe.whitelist()
def get_stock():
    return frappe.db.sql("""
        SELECT 
            b.item_code,
            b.warehouse,
            b.batch_no,
            b.actual_qty
        FROM `tabBin` b
        WHERE b.actual_qty > 0
    """, as_dict=True)


# 🔹 Called after RFID scan
@frappe.whitelist()
def update_stock_from_rfid(epc, warehouse, batch_no=None):

    item_code = epc   # mapping logic change kar sakte ho

    item_row = {
        "item_code": item_code,
        "qty": 1,
        "t_warehouse": warehouse
    }

    # batch add only if available
    if batch_no:
        item_row["batch_no"] = batch_no

    se = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": "Material Receipt",
        "items": [item_row]
    })

    se.insert()
    se.submit()

    log(epc, item_code, batch_no, "Scan", warehouse, "Success")
    return "Stock Updated"


def log(epc, item_code, batch_no, action, warehouse, status):
    frappe.get_doc({
        "doctype": "RFID Log",
        "epc": epc,
        "item_code": item_code,
        "batch_no": batch_no,
        "action": action,
        "warehouse": warehouse,
        "status": status,
        "datetime": now()
    }).insert(ignore_permissions=True)
