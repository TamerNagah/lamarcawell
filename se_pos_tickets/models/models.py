# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class se_pos_tickets(models.Model):
#     _name = 'se_pos_tickets.se_pos_tickets'
#     _description = 'se_pos_tickets.se_pos_tickets'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
