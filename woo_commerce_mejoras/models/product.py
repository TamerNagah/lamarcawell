# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields,api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    category_extra_ids = fields.Many2many(comodel_name="product.category",  string="Categorias Extras", )

class PrepareProductForExport(models.TransientModel):
    """
    Model for adding Odoo products into Woo Layer.
    @author: Haresh Mori on Date 13-Apr-2020.
    """
    _inherit = "woo.prepare.product.for.export.ept"


    def create_update_woo_template(self, variant, woo_instance, woo_template_id, woo_category_dict):
        """ This method is used create/update woo template.
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 9 November 2020 .
            Task_id: 168189 - Woo Commerce Wizard py files refactor
        """
        woo_template_obj = self.env["woo.product.template.ept"]
        product_template = variant.product_tmpl_id

        if product_template.attribute_line_ids and len(
                product_template.attribute_line_ids.filtered(lambda x: x.attribute_id.create_variant == "always")) > 0:
            product_type = 'variable'
        else:
            product_type = 'simple'

        woo_template = woo_template_obj.search([
            ("woo_instance_id", "=", woo_instance.id),
            ("product_tmpl_id", "=", product_template.id)])

        woo_template_vals = self.prepare_woo_template_layer_vals(woo_instance, product_template, product_type)

        if product_template.categ_id:
            self.create_categ_in_woo(product_template.categ_id, woo_instance.id, woo_category_dict)
            for cat_extra in product_template.category_extra_ids:
                self.create_categ_in_woo(cat_extra, woo_instance.id, woo_category_dict)
                woo_categ_id=self.update_category_info(cat_extra, woo_instance.id)
            woo_categ_id|= self.update_category_info(product_template.categ_id, woo_instance.id)

            woo_template_vals.update({'woo_categ_ids': [(6, 0, woo_categ_id.ids)]})

        if not woo_template:
            woo_template = woo_template_obj.create(woo_template_vals)
            woo_template_id = woo_template.id
        else:
            if woo_template_id != woo_template.id:
                woo_template.write(woo_template_vals)
                woo_template_id = woo_template.id

        return woo_template_id