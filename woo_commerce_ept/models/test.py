""" This method use to export selected product in the Woocommerce store.
    @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 15 September 2020 .
    Task_id: 165897
"""
woo_product_tmpl_obj = env['woo.product.template.ept']
common_log_book_obj = env['common.log.book.ept']
woo_instance_obj = env['woo.instance.ept']

instances = woo_instance_obj.search([('active', '=', True)])

woo_product_templates = woo_product_tmpl_obj.search([('exported_in_woo', '=', False)])

for instance in instances:

    woo_templates = woo_product_templates.filtered(lambda x: x.woo_instance_id == instance)
    if not woo_templates:
        continue
    filter_templates = []

    for woo_template in woo_templates:
        if not env['woo.product.product.ept'].search(
                [('woo_template_id', '=', woo_template.id), ('default_code', '=', False)]):
            filter_templates.append(woo_template)
    woo_templates = filter_templates

    common_log_id = common_log_book_obj.woo_create_log_book('export', instance)

    model.import_export_categort_tag(instance, common_log_id)

    woo_product_tmpl_obj.export_products_in_woo(instance, woo_templates,
                                                True, True,
                                                True,
                                                True, common_log_id)
    if common_log_id and not common_log_id.log_lines:
        common_log_id.unlink()

