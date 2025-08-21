# -*- coding: utf-8 -*-
# from odoo import http


# class MinaderProcédure(http.Controller):
#     @http.route('/minader_procédure/minader_procédure', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/minader_procédure/minader_procédure/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('minader_procédure.listing', {
#             'root': '/minader_procédure/minader_procédure',
#             'objects': http.request.env['minader_procédure.minader_procédure'].search([]),
#         })

#     @http.route('/minader_procédure/minader_procédure/objects/<model("minader_procédure.minader_procédure"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('minader_procédure.object', {
#             'object': obj
#         })

