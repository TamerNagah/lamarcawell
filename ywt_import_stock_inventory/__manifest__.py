# -*- coding: utf-8 -*-
# Part of YoungWings Technologies.See the License file for full copyright and licensing details.

{
    # Product Info
    'name': 'Import Stock Inventory Adjustment From CSV/Xlsx/Xls',
    'category': 'stock',
    'version': '14.0.0.1',
    'license': 'OPL-1',
    'sequence': 1,
    'summary': 'Import Stock Inventory Adjustment Which Help You To Adjust Your Inventory Adjustments With In Few Minutes. You Can Prepare The CSV/Xlsx/Xls File For The Import Time.',
    
    # Writer
    'author': 'YoungWings Technologies',
    'maintainer': 'YoungWings Technologies',
    'website':'https://www.youngwingstechnologies.in/',
    'support':'youngwingstechnologies@gmail.com',
    
   # Dependencies
    'depends': ['stock'],
    
    # Views
    'data': ['security/ywt_import_stock_inventory_security.xml',
            'security/ir.model.access.csv',
            'data/stock_invenotry_seq.xml',
            'view/main_menu.xml',
            'wizard_view/ywt_import_stock_inventory_views.xml',
            'view/ywt_import_stock_inventory_log_views.xml'],
     
    # Banner     
    "images": ["static/description/banner.png"],
    
    # Technical 
    'installable': True,
    'auto_install': False,
    'application': True,
    'price':15.50,
    'currency': 'USD',
    
    'description': """
        Import Stock from CSV and Excel file.
        Import Stock inventory from CSV and Excel File.
        Import Inventory Adjustment, stock import from CSV,Inventory adjustment import
       
         
    
    """
    
}
