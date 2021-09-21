# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "POS Barcode Lot Selection",
    "version": "14.0.0.5",
    "category": "",
    'summary': 'POS Barcode Lot Selection',
    "description": """POS Barcode Lot Selection.""",
    "author": "BrowseInfo",
    "website": "www.browseinfo.in",
    "price": 000,
    "currency": 'EUR',
    "depends": ['base', 'pos_orders_all', 'product_expiry'],
    "data": [
        'report/product_label.xml',
        'views/assets.xml',
        'views/product_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url": 'youtube link',
    "images": ["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
