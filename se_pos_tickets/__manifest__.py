# -*- coding: utf-8 -*-
{
    'name': "se_pos_tickets",

    'summary': """
        Modulo para emprimir por separado vaucher y recibo de regalo
       en el punto de venta.
       """,

    'description': """
        Imprimir Voucher y Recibo de Regalo
    """,

    'author': "Odoonext",
    'website': "http://www.odoonext.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/asset.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        'static/src/xml/OrderReceipt.xml',
        'static/src/xml/ReceiptScreen.xml',
        'static/src/xml/ReprintReceiptScreen.xml',
        'static/src/xml/GiftReceipt.xml',
        'static/src/xml/VoucherReceipt.xml',
    ],
    'installable': True,
}
