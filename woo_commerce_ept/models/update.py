start = time.time()
woo_instance_obj = env['woo.instance.ept']
common_log_book_obj = env['common.log.book.ept']
woo_product_tmpl_obj = env['woo.product.template.ept']
export_stock_from_date = datetime.now() - timedelta(30)
t=str(datetime.strftime(from_datetime, '%Y-%m-%d %H:%M:%S'))
woo_tmpl_ids=woo_product_tmpl_obj.search([('updated_at', '<', t)])

instances = woo_instance_obj.search([('active', '=', True)])
woo_tmpl_ids = woo_product_tmpl_obj.browse(woo_tmpl_ids)
for instance in instances:
    woo_templates = woo_tmpl_ids.filtered(lambda x: x.woo_instance_id.id == instance.id and x.exported_in_woo)
    for woo_template in woo_tmpl_ids:
        if woo_template.woo_categ_ids.parent_id:
            woo_template.woo_categ_ids |= woo_template.woo_categ_ids.parent_id
            if woo_template.woo_categ_ids.parent_id.parent_id:
                woo_template.woo_categ_ids |= woo_template.woo_categ_ids.parent_id.parent_id
                if woo_template.woo_categ_ids.parent_id.parent_id.parent_id:
                    woo_template.woo_categ_ids |= woo_template.woo_categ_ids.parent_id.parent_id.parent_id
    if not woo_templates:
        continue
    common_log_id = common_log_book_obj.woo_create_log_book('export', instance)
    model.import_export_categort_tag(instance, common_log_id)
    woo_product_tmpl_obj.update_products_in_woo(instance, woo_templates, True,
                                                True, True, True,
                                                common_log_id)
    if not common_log_id.log_lines:
        common_log_id.unlink()

