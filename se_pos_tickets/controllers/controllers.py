# -*- coding: utf-8 -*-
# from odoo import http


# class SePosTickets(http.Controller):
#     @http.route('/se_pos_tickets/se_pos_tickets/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/se_pos_tickets/se_pos_tickets/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('se_pos_tickets.listing', {
#             'root': '/se_pos_tickets/se_pos_tickets',
#             'objects': http.request.env['se_pos_tickets.se_pos_tickets'].search([]),
#         })

#     @http.route('/se_pos_tickets/se_pos_tickets/objects/<model("se_pos_tickets.se_pos_tickets"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('se_pos_tickets.object', {
#             'object': obj
#         })
