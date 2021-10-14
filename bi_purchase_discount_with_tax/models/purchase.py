# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare, float_is_zero
from itertools import groupby
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class purchase_order(models.Model):
    _inherit = 'purchase.order'
    

    @api.depends('order_line','order_line.price_total','order_line.price_subtotal',\
        'order_line.product_qty','discount_amount',\
        'discount_method','discount_type' ,'order_line.discount_amount',\
        'order_line.discount_method')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        # res_config = self.env['res.config.settings'].search([],order="id desc", limit=1)
        res_config= self.env.company
        cur_obj = self.env['res.currency']
        for order in self:
            applied_discount = 0.0
            line_discount = 0.0
            sums = 0.0 
            order_discount = 0.0  
            amount_untaxed = 0.0 
            amount_tax  = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                applied_discount += line.discount_amt
                if line.discount_method == 'fix':
                    line_discount += line.discount_amount
                elif line.discount_method == 'per':
                    tax = line.com_tax()
                    line_discount += (line.price_subtotal+tax) * (line.discount_amount/ 100)
            if res_config:
                if res_config.tax_discount_policy == 'tax':
                    if order.discount_type == 'line':
                        order.discount_amt = 0.00
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax - line_discount,
                            'discount_amt_line' : line_discount,
                        })
                    elif order.discount_type == 'global':
                        order.discount_amt_line = 0.00
                        if order.discount_method == 'per':
                            order_discount = (amount_untaxed + amount_tax) * (order.discount_amount / 100)  
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax - order_discount,
                                'discount_amt' : order_discount,
                            })
                        elif order.discount_method == 'fix':
                            order_discount = order.discount_amount
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax - order_discount,
                                'discount_amt' : order_discount,
                            })
                        else:
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax ,
                            })
                    else:
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax ,
                            })
                elif res_config.tax_discount_policy == 'untax':
                    if order.discount_type == 'line':
                        order.discount_amt = 0.00
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax - applied_discount,
                            'discount_amt_line' : applied_discount,
                        })
                    elif order.discount_type == 'global':
                        order.discount_amt_line = 0.00
                        if order.discount_method == 'per':
                            order_discount = amount_untaxed * (order.discount_amount / 100)
                            if order.order_line:
                                for line in order.order_line:
                                    if line.taxes_id:
                                        final_discount = 0.0
                                        try:
                                            final_discount = ((order.discount_amount*line.price_subtotal)/100.0)
                                        except ZeroDivisionError:
                                            pass
                                        discount = line.price_subtotal - final_discount
                                        taxes = line.taxes_id.compute_all(discount, \
                                                            order.currency_id,1.0, product=line.product_id, \
                                                            partner=order.partner_id)
                                        sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': sums,
                                'amount_total': amount_untaxed + sums - order_discount,
                                'discount_amt' : order_discount,  
                            })
                        elif order.discount_method == 'fix':
                            order_discount = order.discount_amount
                            if order.order_line:
                                for line in order.order_line:
                                    if line.taxes_id:
                                        final_discount = 0.0
                                        try:
                                            final_discount = ((order.discount_amount*line.price_subtotal)/amount_untaxed)
                                        except ZeroDivisionError:
                                            pass
                                        discount = line.price_subtotal - final_discount
                                        taxes = line.taxes_id._origin.compute_all(discount, \
                                                            order.currency_id,1.0, product=line.product_id, \
                                                            partner=order.partner_id,)
                                        sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': sums,
                                'amount_total': amount_untaxed + sums - order_discount,
                                'discount_amt' : order_discount,
                            })
                        else:
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax ,
                            })
                    else:
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax ,
                            })
                else:
                    order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax ,
                            })         
            else:
                order.update({
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': amount_tax,
                    'amount_total': amount_untaxed + amount_tax ,
                    })

    def _calculate_discount(self):
        res = discount = 0.0
        for self_obj in self:
            if self_obj.discount_type == 'global':
                if self_obj.discount_method == 'fix':
                    res = self_obj.discount_amount
                elif self_obj.discount_method == 'per':
                    res = (self_obj.amount_untaxed +self_obj.amount_tax) * (self_obj.discount_amount/ 100)
            elif self_obj.discount_type == 'line':
                total = 0
                for line in self_obj.order_line:
                    if line.discount_method == 'fix':
                        res += line.discount_amount
                    elif line.discount_method == 'per':
                        res += line.price_subtotal * (line.discount_amount/ 100)
            else:
                res = discount
        return res


    def _prepare_invoice(self):
        invoice_vals = super(purchase_order, self)._prepare_invoice()
        invoice_vals.update({
            'discount_method' : self.discount_method , 
            'discount_amt' : self.discount_amt,
            'discount_amount' : self.discount_amount ,
            'discount_type' : self.discount_type,
            'discount_amt_line' : self.discount_amt_line,
            'amount_untaxed' : self.amount_untaxed,
            'amount_total': self.amount_total,
            })
        return invoice_vals


    def action_create_invoice(self):
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        for order in self:
            if order.invoice_status != 'to invoice':
                continue

            order = order.with_company(order.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            taxes = []
            res_config= self.env.company
            for ln in order.order_line:
                for tx in ln.taxes_id:
                    if tx.id not in taxes:
                        taxes.append(tx.id)
            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    if pending_section:
                        invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_account_move_line()))
                        pending_section = None
                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_account_move_line()))
            if self.discount_amt > 0 or self.discount_amt_line > 0:
                if self.discount_type == 'global':
                    if res_config.tax_discount_policy == "tax":
                       invoice_vals['invoice_line_ids'].append((0, 0,{
                                'quantity': 1,
                                'name': 'Global Discount',
                                'is_global_disc' : True,
                                'exclude_from_invoice_tab' : True,
                                'price_unit': - self.discount_amt,
                                'price_subtotal' : - self.discount_amt,
                                'account_id': res_config.purchase_account_id.id,   
                                'currency_id' : self.currency_id.id or self.company_id.currency_id.id
                                }))
                    else:
                        invoice_vals['invoice_line_ids'].append((0, 0, {
                                'quantity': 1,
                                'name': 'Global Discount',
                                'is_global_disc' : True,
                                'exclude_from_invoice_tab' : True,
                                'price_unit': - self.discount_amt,
                                'price_subtotal' : - self.discount_amt,
                                'account_id': res_config.purchase_account_id.id,   
                                'tax_ids' : [(6,0,taxes)],
                                'currency_id' : self.currency_id.id or self.company_id.currency_id.id
                            }))
                else:

                    if res_config.tax_discount_policy == "tax":
                        invoice_vals['invoice_line_ids'].append((0, 0, {
                                'quantity': 1,
                                'name': 'Lines Discount',
                                'is_global_disc' : True,
                                'exclude_from_invoice_tab' : True,
                                'price_unit': - self.discount_amt_line,
                                'price_subtotal' : - self.discount_amt_line,
                                'account_id': res_config.purchase_account_id.id,   
                                'currency_id' : self.currency_id.id or self.company_id.currency_id.id
                            }))
                    else:
                        invoice_vals['invoice_line_ids'].append((0, 0, {
                                'quantity': 1,
                                'name': 'Lines Discount',
                                'is_global_disc' : True,
                                'exclude_from_invoice_tab' : True,
                                'price_unit': - self.discount_amt_line,
                                'price_subtotal' : - self.discount_amt_line,
                                'account_id': res_config.purchase_account_id.id,   
                                'tax_ids' : [(6,0,taxes)],
                                'currency_id' : self.currency_id.id or self.company_id.currency_id.id
                            }))
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('company_id'), x.get('partner_id'), x.get('currency_id'))):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                origins.add(invoice_vals['invoice_origin'])
                payment_refs.add(invoice_vals['payment_reference'])
                refs.add(invoice_vals['ref'])
            ref_invoice_vals.update({
                'ref': ', '.join(refs)[:2000],
                'invoice_origin': ', '.join(origins),
                'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
            })
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice' , default_discount_type=order.discount_type)
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        moves.filtered(lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_invoice_into_refund_credit_note()
        return self.action_view_invoice(moves)

    def action_view_invoice(self, invoices=False):
        """This function returns an action that display existing vendor bills of
        given purchase order ids. When only one found, show the vendor bill
        immediately.
        """
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            self.sudo()._read(['invoice_ids'])
            invoices = self.invoice_ids

        action = self.env.ref('account.action_move_in_invoice_type').sudo()
        result = action.read()[0]
        invoices.write({
            'discount_method' : self.discount_method , 
            'discount_amt' : self.discount_amt,
            'discount_amount' : self.discount_amount ,
            'discount_type' : self.discount_type,
            'discount_amt_line' : self.discount_amt_line,
            'amount_untaxed' : self.amount_untaxed,
            'amount_total': self.amount_total,
        })
        invoices.onc_tax_change()
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

        
    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method',default='fix')
    discount_amount = fields.Float('Discount Amount',default=0.0)
    discount_amt = fields.Monetary(compute='_amount_all',store=True,string='- Discount',readonly=True)
    discount_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')],string='Discount Applies to',default='global')
    discount_amt_line = fields.Float(compute='_amount_all', string='- Line Discount', digits='Line Discount', store=True, readonly=True)


class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    
    discount_method = fields.Selection(
            [('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
    discount_type = fields.Selection(related='order_id.discount_type', string="Discount Applies to")
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Float('Discount Final Amount')


    @api.depends('product_qty','price_unit','taxes_id','discount_amount')
    def com_tax(self):
        tax_total = 0.0
        tax = 0.0
        for line in self:
            for tax in line.taxes_id:
                tax_total += (tax.amount/100)*line.price_subtotal
            tax = tax_total
            return tax
    @api.depends('product_qty', 'price_unit', 'taxes_id','discount_method','discount_amount','discount_type')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            # res_config= self.env['res.config.settings'].search([],order="id desc", limit=1)
            res_config= self.env.company
            if res_config:
                if res_config.tax_discount_policy == 'untax':
                    if line.discount_type == 'line':
                        if line.discount_method == 'fix':
                            price = (vals['price_unit'] * vals['product_qty']) - line.discount_amount
                            taxes = line.taxes_id.compute_all(price,vals['currency_id'],1,vals['product'],vals['partner'])
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'] + line.discount_amount,
                                'price_subtotal': taxes['total_excluded'] + line.discount_amount,
                                'discount_amt' : line.discount_amount,
                            })

                        elif line.discount_method == 'per':
                            price = (vals['price_unit'] * vals['product_qty']) * (1 - (line.discount_amount or 0.0) / 100.0)
                            price_x = ((vals['price_unit'] * vals['product_qty'])-((vals['price_unit'] * vals['product_qty']) * (1 - (line.discount_amount or 0.0) / 100.0)))
                            taxes = line.taxes_id.compute_all(price,vals['currency_id'],1,vals['product'],vals['partner'])
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'] + price_x,
                                'price_subtotal': taxes['total_excluded'] + price_x,
                                'discount_amt' : price_x,
                            })
                        else:
                            taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency_id'],vals['product_qty'],vals['product'],vals['partner'])
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'],
                                'price_subtotal': taxes['total_excluded'],
                            })
                    else:
                        taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency_id'],vals['product_qty'],vals['product'],vals['partner'])
                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                        })
                elif res_config.tax_discount_policy == 'tax':
                    price_x = 0.0
                    if line.discount_type == 'line':
                        taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency_id'],vals['product_qty'],vals['product'],vals['partner'])
                        if line.discount_method == 'fix':
                            price_x = (taxes['total_included']) - (taxes['total_included'] - line.discount_amount)
                        elif line.discount_method == 'per':
                            price_x = (taxes['total_included']) - (taxes['total_included'] * (1 - (line.discount_amount or 0.0) / 100.0))                        

                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                            'discount_amt' : price_x,
                        })
                    else:
                        taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency_id'],vals['product_qty'],vals['product'],vals['partner'])
                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                        })
                else:
                    taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency_id'],vals['product_qty'],vals['product'],vals['partner'])
                    line.update({
                        'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })
            else:
                taxes = line.taxes_id.compute_all(vals['price_unit'],vals['currency_id'],vals['product_qty'],vals['product'],vals['partner'])
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

    def _prepare_account_move_line(self, move=False):

        res =super(purchase_order_line,self)._prepare_account_move_line(move)
        res.update({'discount_method':self.discount_method,'discount_amount':self.discount_amount,'quantity':self.qty_to_invoice,'discount_amt':self.discount_amt})
        return res            


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tax_discount_policy = fields.Selection([('tax', 'Taxed Amount'), ('untax', 'Untaxed Amount')],string='Discount Applies On',
        default_model='sale.order',related='company_id.tax_discount_policy', readonly=False)
    purchase_account_id = fields.Many2one('account.account', 'Purchase Discount Account',domain=[('user_type_id.internal_group','=','income'), ('discount_account','=',True)],related='company_id.purchase_account_id', readonly=False)


class Company(models.Model):
    _inherit = 'res.company'

    tax_discount_policy = fields.Selection([('tax', 'Taxed Amount'), ('untax', 'Untaxed Amount')],string='Discount Applies On',
        default_model='sale.order')
    purchase_account_id = fields.Many2one('account.account', 'Purchase Discount Account',domain=[('user_type_id.internal_group','=','income'), ('discount_account','=',True)])
