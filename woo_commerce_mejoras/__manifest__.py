# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Odoo WooCommerce Connector Mejoras',
    'version': '14.0.5.1',
    'license': 'OPL-1',
    'category': 'Sales',
    'summary': 'Odoo Woocommerce Connector helps you automate your vital business processes at Odoo by enabling '
               'bi-directional data exchange between WooCommerce & Odoo.',


    'depends': ['woo_commerce_ept', ],
    'data': [
             'views/product_template_view.xml',
             ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,


}
