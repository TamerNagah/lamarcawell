# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Import Inventario",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Extra Tools",
    "summary": "Import Customers From Csv,Import Suppliers,Import Product image,Import Sale Order from excel,Import Stock,Import Inventory,import purchase order,Import Invoice,Import Bill of Material,Import Lead,Import Task,Import Vendor Detail,Import bank statement",
    "description": """This module is useful to import data from CSV/excel file.
 All In One Import - Sales, Purchase, Account, Inventory, BOM, CRM Odoo
 Import Partner From Csv, Import Partner From Excel, Import Partner From XLS, Import Partner From XLSX, Import Product From Csv, Import Product From Excel, Import Product From XLS, Import Product From XLSX,  Import Sales From Csv, Import Sale Order From Excel, Import Quotation From XLS, Import so From XLSX, Import Purchase From Csv, Import Purchase Order From Excel, Import Request For Quotation From XLS, Import RFQ From XLSX, Import Account From Csv, Import Invoice From Excel, Import Invoice From XLS, Import Account From XLSX, Import Inventory From Csv, Import Stock From Excel, Import Inventory From XLS, Import Stock From XLSX, Import BOM From Csv, Import Bill Of Material From Excel, Import BOM From XLS, Import Bill Of Material From XLSX, Import CRM From Csv, Import CRM From Excel, Import Lead From XLS, Import Lead From XLSX, Import Bill Of Material From XLSX, Import CRM From Csv, Import CRM From Excel, Import Lead From XLS, Import Lead From XLSX,  Import Project From XLSX, Import Project From Csv, Import Task From Excel, Import Reordering Rules From XLS, Import Lead From XLSX Odoo. 
 Import Partner From Csv, Import Product From Excel,  Import Sale Order From Csv ,Import Purchase Order From Excel Module,Import Account From Csv, Import Invoice From Excel,Import Inventory From Xls, Import Stock From Xlsx, Import Bill Of Material From CSV, Import CRM From Csv, Import Lead From XLS,Import Project From XLSX, Import Task From Excel, Import Reordering Rules From XLS Odoo. """,
    "version": "14.0.1",
    "depends": [
        "sh_message",           
            "stock",           
    ],
    "application": True,
    "data": [
       
        "sh_import_inventory_with_lot_serial/security/import_inventory_with_lot_serial_security.xml",
        "sh_import_inventory_with_lot_serial/security/ir.model.access.csv",
        "sh_import_inventory_with_lot_serial/wizard/import_inventory_with_lot_serial_wizard.xml",
        "sh_import_inventory_with_lot_serial/views/stock_view.xml",     

        "sh_import_int_transfer/security/import_int_transfer_security.xml",
        "sh_import_int_transfer/security/ir.model.access.csv",
        "sh_import_int_transfer/wizard/import_int_transfer_wizard.xml",
        "sh_import_int_transfer/views/stock_view.xml",

    ],
    "external_dependencies": {
        "python": ["xlrd"],
    },

    "images": ["static/description/background.gif", ],
    "auto_install": False,
    "installable": True,
    "price": 80,
    "currency": "EUR"
}
