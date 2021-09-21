# -*- coding: utf-8 -*-
{
    'name': "SE Repository Management",

    'summary': 'Manage Repositories.',

    'description': """
        Long description of module's purpose
    """,

    'author': "David Montero Crespo",
    'website': "https://softwareescarlata.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '14.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
       'data/data.xml',
        'security/ir.model.access.csv',
        'views/repository_repository_view.xml',
        'views/panel_tool.xml',
    ],
    'application': True,
    'price': 40,
    'images': ['static/description/imagen.png'],
    'currency': 'EUR',
    'license': 'AGPL-3',
}
