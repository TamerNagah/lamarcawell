14.0.1
----------------------------
Initial release

14.0.2 (Date : 4 Dec 2020)
----------------------------
==> Import product.product + product.template custom field also.

14.0.3 (11 Feb 2021)
========================
==> [ADD] Create new record in dynamic Many2many field if does not exist.
==> [ADD] Create new record in Product Category field if does not exist.


14.0.4 (6 May 2021)
=======================
==> currected below code.

if row[4].strip() == 'Service':
    tmpl_vals.update({'type' : 'service'})                                          
elif row[4].strip() == 'Storable Product':
    tmpl_vals.update({'type' : 'product'})                                                                            
elif row[4].strip() == 'Consumable':
    tmpl_vals.update({'type' : 'consu'})

14.0.5 (Date 15th June 2021)
=============================
[UPDATE] add variant wise cost column in xls and csv sheet and update that variant wise.


==> [UPDATE] remove 'store' in wizard

14.0.6 (Date : 10th August 2021)
------------------------------------
[UPDATE] update attributes columns like use "#" instead of "," for differentiate variant. 
