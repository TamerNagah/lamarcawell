# -*- coding: utf-8 -*-
# from odoo import http


# class SeRepositoryManagement(http.Controller):
#     @http.route('/se_repository_management/se_repository_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/se_repository_management/se_repository_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('se_repository_management.listing', {
#             'root': '/se_repository_management/se_repository_management',
#             'objects': http.request.env['se_repository_management.se_repository_management'].search([]),
#         })

#     @http.route('/se_repository_management/se_repository_management/objects/<model("se_repository_management.se_repository_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('se_repository_management.object', {
#             'object': obj
#         })
