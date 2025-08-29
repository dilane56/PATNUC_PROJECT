# -*- coding: utf-8 -*-
# from odoo import http


# class PatnucMinepiaCarteTranshumance(http.Controller):
#     @http.route('/patnuc_minepia_carte_transhumance/patnuc_minepia_carte_transhumance', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/patnuc_minepia_carte_transhumance/patnuc_minepia_carte_transhumance/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('patnuc_minepia_carte_transhumance.listing', {
#             'root': '/patnuc_minepia_carte_transhumance/patnuc_minepia_carte_transhumance',
#             'objects': http.request.env['patnuc_minepia_carte_transhumance.patnuc_minepia_carte_transhumance'].search([]),
#         })

#     @http.route('/patnuc_minepia_carte_transhumance/patnuc_minepia_carte_transhumance/objects/<model("patnuc_minepia_carte_transhumance.patnuc_minepia_carte_transhumance"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('patnuc_minepia_carte_transhumance.object', {
#             'object': obj
#         })

