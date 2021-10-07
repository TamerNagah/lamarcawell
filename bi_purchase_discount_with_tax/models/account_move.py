# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang, format_date, get_lang


class account_account(models.Model):
	_inherit = 'account.account'
	
	discount_account = fields.Boolean('Discount Account')


class account_move(models.Model):
	_inherit = 'account.move'

	# @api.model
 # 	def default_get(self,fields):  		
 # 		res = super(account_move,self).default_get(fields)

	def calc_discount(self):
		for calculate in self:
			calculate._calculate_discount()

	@api.depends('discount_amount')
	def _calculate_discount(self):
		res = 0.0
		discount = 0.0
		for self_obj in self:
			if self_obj.discount_type == 'global':
				if self_obj.discount_method == 'fix':
					res = self_obj.discount_amount
				else:
					res = ((self_obj.amount_untaxed + self_obj.amount_tax) * (self_obj.discount_amount/ 100))
			else:
				total = 0
				for line in self_obj.invoice_line_ids:
					if line.discount_method == 'fix':
						res += line.discount_amount
					else:
						res += (line.price_subtotal * (line.discount_amount/ 100))
		return res

	def _check_balanced(self):
		''' Assert the move is fully balanced debit = credit.
		An error is raised if it's not the case.
		'''
		moves = self.filtered(lambda move: move.line_ids)
		if not moves:
			return

		# /!\ As this method is called in create / write, we can't make the assumption the computed stored fields
		# are already done. Then, this query MUST NOT depend of computed stored fields (e.g. balance).
		# It happens as the ORM makes the create with the 'no_recompute' statement.
		self.env['account.move.line'].flush(self.env['account.move.line']._fields)
		self.env['account.move'].flush(['journal_id'])
		self._cr.execute('''
			SELECT line.move_id, ROUND(SUM(line.debit - line.credit), currency.decimal_places) , SUM(line.debit) , SUM(line.credit)
			FROM account_move_line line
			JOIN account_move move ON move.id = line.move_id
			JOIN account_journal journal ON journal.id = move.journal_id
			JOIN res_company company ON company.id = journal.company_id
			JOIN res_currency currency ON currency.id = company.currency_id
			WHERE line.move_id IN %s
			GROUP BY line.move_id, currency.decimal_places
			HAVING ROUND(SUM(line.debit - line.credit), currency.decimal_places) != 0.0;
		''', [tuple(self.ids)])

		query_res = self._cr.fetchall()
		if query_res:
			ids = [res[0] for res in query_res]
			sums = [res[1] for res in query_res]
			if sums and sums[0] > 0.2 :
				raise UserError(_("Cannot create unbalanced journal entry. Ids: %s\nDifferences debit - credit: %s") % (ids, sums))




	@api.depends(
		'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
		'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
		'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
		'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
		'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
		'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
		'line_ids.debit',
		'line_ids.credit',
		'line_ids.currency_id',
		'line_ids.amount_currency',
		'line_ids.amount_residual',
		'line_ids.amount_residual_currency',
		'line_ids.payment_id.state',
		'line_ids.full_reconcile_id',
		'discount_method',
		'discount_type',
		'discount_amount',
		'discount_amt_line'
		)
	def _compute_amount(self):
		for move in self:

			if move.payment_state == 'invoicing_legacy':
				# invoicing_legacy state is set via SQL when setting setting field
				# invoicing_switch_threshold (defined in account_accountant).
				# The only way of going out of this state is through this setting,
				# so we don't recompute it here.
				move.payment_state = move.payment_state
				continue

			total_untaxed = 0.0
			total_untaxed_currency = 0.0
			total_tax = 0.0
			total_tax_currency = 0.0
			total_to_pay = 0.0
			total_residual = 0.0
			total_residual_currency = 0.0
			total = 0.0
			total_currency = 0.0
			currencies = move._get_lines_onchange_currency().currency_id
			res_config= self.env.company
			for line in move.line_ids:
				if move.is_invoice(include_receipts=True):
					# === Invoices ===
					if not line.exclude_from_invoice_tab:
						# Untaxed amount.
						total_untaxed += line.balance
						total_untaxed_currency += line.amount_currency
						total += line.balance
						total_currency += line.amount_currency
					elif line.tax_line_id:
						# Tax amount.
						total_tax += line.balance
						total_tax_currency += line.amount_currency
						total += line.balance
						total_currency += line.amount_currency
					elif line.account_id.user_type_id.type in ('receivable', 'payable'):
						# Residual amount.
						total_to_pay += line.balance
						total_residual += line.amount_residual
						total_residual_currency += line.amount_residual_currency
				else:
					# === Miscellaneous journal entry ===
					if line.debit:
						total += line.balance
						total_currency += line.amount_currency

			if move.move_type == 'entry' or move.is_outbound():
				sign = 1
			else:
				sign = -1
			convert_disc = move.currency_id._convert(move.discount_amt, move.company_currency_id, move.company_id, move.date)
			total_currency = total_currency - move.discount_amt
			
			if  move.discount_amt_line:
				total = total - convert_disc
				total_currency = total_currency - move.discount_amt_line
			elif move.discount_amt:
				total = total - convert_disc
				total_currency = total_currency - move.discount_amt
			else:
				total = total
				total_currency = total_currency
			move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
			move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
			

			if res_config.tax_discount_policy == 'tax':
				if move.discount_type == 'line':
					move.discount_amt = 0.00
					total = 0
					for line in self.invoice_line_ids:
						if line.discount_method == 'per':
							tax = line.com_tax()
							total += (line.price_subtotal+tax) * (line.discount_amount/ 100)
						elif line.discount_method == 'fix':
							total += line.discount_amount
					move.discount_amt_line = total
					move.amount_total = sign * (move.amount_tax + move.amount_untaxed - move.discount_amt_line)
				elif move.discount_type == 'global':
					if move.discount_method == 'fix':
						move.discount_amt = move.discount_amount
						move.amount_total =sign *(move.amount_tax + move.amount_untaxed - move.discount_amt) 
					elif move.discount_method == 'per':
						move.discount_amt =((move.amount_tax + move.amount_untaxed) * (move.discount_amount / 100.0))
						move.amount_total =sign * ((move.amount_tax + move.amount_untaxed) - move.discount_amt) 
					else:
						move.amount_total = sign * (move.amount_tax + move.amount_untaxed)
				else:
					move.amount_total = sign * (move.amount_tax + move.amount_untaxed)
			elif res_config.tax_discount_policy == 'untax':
				sums = 0.00
				if move.discount_type == 'line':
					total = 0
					for line in self.invoice_line_ids:
						if line.discount_method == 'per':
							total += line.price_subtotal * (line.discount_amount/ 100)
						elif line.discount_method == 'fix':
							total += line.discount_amount
					move.discount_amt_line = total
					move.amount_total =sign *(move.amount_tax + move.amount_untaxed - move.discount_amt_line)         
					move.discount_amt = 0.00
				elif move.discount_type == 'global':
					if move.discount_method == 'fix':
						move.discount_amt = move.discount_amount
						if move.invoice_line_ids:
							for line in move.invoice_line_ids:
								if line.tax_ids:
									if move.amount_untaxed:
										final_discount = ((move.discount_amt*line.price_subtotal)/move.amount_untaxed)
										discount = line.price_subtotal - final_discount
										taxes = line.tax_ids.compute_all(discount, move.currency_id, 1.0,
																		line.product_id,move.partner_id)                                            
										sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
						move.amount_total =sign *(sums + move.amount_untaxed - move.discount_amt)
						move.update({'amount_tax':sign *(sums) })
				
					elif move.discount_method == 'per':
						# move.discount_amt = 0.0
						discount_amt = 0.0
						if move.invoice_line_ids:
							for line in move.invoice_line_ids:
								if line.tax_ids:
									final_discount = ((move.discount_amount*line.price_subtotal)/100.0)
									discount = line.price_subtotal - final_discount
									discount_amt += final_discount
									taxes = line.tax_ids._origin.compute_all(discount, move.currency_id, 1.0,
																	line.product_id,move.partner_id)
									sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
						move.discount_amt = discount_amt
						move.amount_total = sign * (sums + move.amount_untaxed - move.discount_amt)
						move.update({'amount_tax':sign *(sums)})
				else:
					move.amount_total =sign * (move.amount_tax + move.amount_untaxed)
			else:
				move.amount_total = sign * (move.amount_tax + move.amount_untaxed)
			move.discount_account_id = False    
			move.onc_tax_change()
			if move.move_type == 'in_invoice':
				if res_config.purchase_account_id:
					move.discount_account_id = res_config.purchase_account_id.id
				else:
					account_id = False
					account_id = move.env['account.account'].search([('user_type_id.name','=','Income'), ('discount_account','=',True)],limit=1)
					move.discount_account_id = account_id.id
			else:
				pass  

			# move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
			move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
			move.amount_untaxed_signed = -total_untaxed
			move.amount_tax_signed = -total_tax
			move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
			move.amount_residual_signed = total_residual

			currency = len(currencies) == 1 and currencies or move.company_id.currency_id

			# Compute 'payment_state'.
			new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

			if move.is_invoice(include_receipts=True) and move.state == 'posted':

				if currency.is_zero(move.amount_residual):
					reconciled_payments = move._get_reconciled_payments()
					if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
						new_pmt_state = 'paid'
					else:
						new_pmt_state = move._get_invoice_in_payment_state()
				elif currency.compare_amounts(total_to_pay, total_residual) != 0:
					new_pmt_state = 'partial'

			if new_pmt_state == 'paid' and move.move_type in ('in_invoice', 'out_invoice', 'entry'):
				reverse_type = move.move_type == 'in_invoice' and 'in_refund' or move.move_type == 'out_invoice' and 'out_refund' or 'entry'
				reverse_moves = self.env['account.move'].search([('reversed_entry_id', '=', move.id), ('state', '=', 'posted'), ('move_type', '=', reverse_type)])

				# We only set 'reversed' state in cas of 1 to 1 full reconciliation with a reverse entry; otherwise, we use the regular 'paid' state
				reverse_moves_full_recs = reverse_moves.mapped('line_ids.full_reconcile_id')
				if reverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambda x: x not in (reverse_moves + reverse_moves_full_recs.mapped('exchange_move_id'))) == move:
					new_pmt_state = 'reversed'

			move.payment_state = new_pmt_state


	@api.depends('discount_method','discount_amount','line_ids','invoice_line_ids','discount_type','invoice_line_ids.discount_amount','invoice_line_ids.discount_type')
	def onc_tax_change(self):
		# for move in self:
		move = self
		# glob_disc = move._calculate_discount()
		is_global_line_ids = False
		taxes = []
		sign = 1 if move.is_inbound() else - 1
		for ln in move.line_ids:
			if not ln.is_global_disc:
				for tx in ln.tax_ids:
					if tx.id not in taxes:
						taxes.append(tx.id)
		is_global_line_ids = self.line_ids.filtered(lambda l: l.is_global_disc)
		res_config= self.env.company
		if is_global_line_ids:
			if self.discount_type == "global":
				is_global_line_ids.name = 'Global Discount'
				is_global_line_ids.price_unit = sign * self.discount_amt
				is_global_line_ids.price_subtotal = sign * self.discount_amt
			else:
				is_global_line_ids.name = 'Lines Discount'
				is_global_line_ids.price_unit = sign * self.discount_amt_line
				is_global_line_ids.price_subtotal = sign * self.discount_amt_line
			is_global_line_ids.is_global_disc = True
			is_global_line_ids._onchange_product_id()
			self._move_autocomplete_invoice_lines_values()

		else:
			if self.discount_amt > 0 or self.discount_amt_line > 0:
				if self.discount_type == 'global':
					if res_config.tax_discount_policy == "tax":
						move.update({
							'invoice_line_ids': [(0, 0,{
								'quantity': 1,
								'name': 'Global Discount',
								'is_global_disc' : True,
								'exclude_from_invoice_tab' : True,
								'price_unit': sign * self.discount_amt,
								'price_subtotal' : sign * self.discount_amt,
								'account_id': res_config.purchase_account_id.id,   
								'currency_id' : move.currency_id.id or move.company_id.currency_id.id
								})]		
						})
					else:
						move.update({
							'invoice_line_ids': [(0, 0, {
								'move_id': move.id,
								'quantity': 1,
								'name': 'Global Discount',
								'is_global_disc' : True,
								'exclude_from_invoice_tab' : True,
								'price_unit': sign * self.discount_amt,
								'price_subtotal' : sign * self.discount_amt,
								'account_id': res_config.purchase_account_id.id,   
								'tax_ids' : [(6,0,taxes)],
								'currency_id' : move.currency_id.id or move.company_id.currency_id.id
							})]
						})
				else:

					if res_config.tax_discount_policy == "tax":
						move.update({
							'invoice_line_ids': [(0, 0, {
								'move_id': move.id,
								'quantity': 1,
								'name': 'Lines Discount',
								'is_global_disc' : True,
								'exclude_from_invoice_tab' : True,
								'price_unit': sign * self.discount_amt_line,
								'price_subtotal' : sign * self.discount_amt_line,
								'account_id': res_config.purchase_account_id.id,   
								'currency_id' : move.currency_id.id or move.company_id.currency_id.id
							})]
						})
					else:
						move.update({
							'invoice_line_ids': [(0, 0, {
								'move_id': move.id,
								'quantity': 1,
								'name': 'Lines Discount',
								'is_global_disc' : True,
								'exclude_from_invoice_tab' : True,
								'price_unit': sign * self.discount_amt_line,
								'price_subtotal' : sign * self.discount_amt_line,
								'account_id': res_config.purchase_account_id.id,   
								'tax_ids' : [(6,0,taxes)],
								'currency_id' : move.currency_id.id or move.company_id.currency_id.id
							})]
						})
			for ln in move.line_ids:
				if ln.is_global_disc :
					is_global_line_ids = ln
					is_global_line_ids.is_global_disc = True
					is_global_line_ids._onchange_product_id()
					self._move_autocomplete_invoice_lines_values()

	discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')],'Discount Method')
	discount_amount = fields.Float('Discount Amount')
	discount_amt = fields.Float(string='- Discount', readonly=True,)
	amount_untaxed = fields.Float(string='Subtotal', digits='Account',store=True, readonly=True, compute='_compute_amount',tracking=True)
	amount_tax = fields.Float(string='Tax', digits='Account',store=True, readonly=True, compute='_compute_amount')
	amount_total = fields.Float(string='Total', digits='Account',store=True, readonly=True, compute='_compute_amount')
	discount_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')], 'Discount Applies to',default='global')
	discount_account_id = fields.Many2one('account.account', 'Discount Account',compute='_compute_amount',store=True)
	discount_amt_line = fields.Float(compute='_compute_amount', string='- Line Discount', digits='Discount' , store=True, readonly=True)





class account_move_line(models.Model):
	_inherit = 'account.move.line'
 
	discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
	discount_type = fields.Selection(related='move_id.discount_type', string="Discount Applies to")
	discount_amount = fields.Float('Discount Amount')
	discount_amt = fields.Float('Discount Final Amount')    
	is_global_disc = fields.Boolean(string = "Global Discount")
	# price_unit = fields.Float(string='Unit Price', digits=(12,6))

	@api.depends('quantity','price','tax_ids')
	def com_tax(self):
		tax_total = 0.0
		tax = 0.0
		for line in self:
			for tax in line.tax_ids:
				tax_total += (tax.amount/100)*line.price_subtotal
			tax = tax_total
			return tax

