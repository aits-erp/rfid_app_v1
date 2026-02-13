import frappe
from frappe.utils import now

# 🔹 Item list with Batch
@frappe.whitelist(allow_guest=True)
def get_items():
    return frappe.db.sql("""
        SELECT 
            i.item_code,
            i.item_name,
            IFNULL(b.name, '') as batch_no
        FROM `tabItem` i
        LEFT JOIN `tabBatch` b
        ON b.item = i.name
    """, as_dict=True)


# 🔹 Stock data with Batch
@frappe.whitelist(allow_guest=True)
def get_stock():
    return frappe.db.sql("""
        SELECT 
            item_code,
            warehouse,
            batch_no,
            actual_qty
        FROM `tabBin`
        WHERE actual_qty > 0
    """, as_dict=True)


# 🔹 Called after RFID scan
@frappe.whitelist(allow_guest=True)
def update_stock_from_rfid(epc, warehouse, batch_no=None):

    item_code = epc

    item_row = {
        "item_code": item_code,
        "qty": 1,
        "t_warehouse": warehouse
    }

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

    return "OK"   # simple string enough


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


# 🔹 Tagway direct items (NO WRAPPER)
@frappe.whitelist(allow_guest=True)
def tagway_items():
    data = frappe.db.sql("""
        SELECT 
            i.item_code as RFID,
            i.item_name as NAME,
            IFNULL(b.name, '') as BATCH
        FROM `tabItem` i
        LEFT JOIN `tabBatch` b
        ON b.item = i.name
    """, as_dict=True)

    return data   # <-- DIRECT LIST




@frappe.whitelist(allow_guest=True)
def tagway_dump():
    import json, os
    data = frappe.db.sql("""
        SELECT item_code as RFID, item_name as NAME FROM tabItem
    """, as_dict=True)

    path = "/home/frappe/frappe-bench/sites/aits/public/tagway.json"
    with open(path, "w") as f:
        json.dump({"message": data}, f)

    return "OK"
