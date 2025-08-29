# -*- coding: utf-8 -*-
# from odoo import http


# class PatnucMinepiaLaisserPasserSanitaire(http.Controller):
#     @http.route('/patnuc_minepia_laisser_passer_sanitaire/patnuc_minepia_laisser_passer_sanitaire', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/patnuc_minepia_laisser_passer_sanitaire/patnuc_minepia_laisser_passer_sanitaire/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('patnuc_minepia_laisser_passer_sanitaire.listing', {
#             'root': '/patnuc_minepia_laisser_passer_sanitaire/patnuc_minepia_laisser_passer_sanitaire',
#             'objects': http.request.env['patnuc_minepia_laisser_passer_sanitaire.patnuc_minepia_laisser_passer_sanitaire'].search([]),
#         })

#     @http.route('/patnuc_minepia_laisser_passer_sanitaire/patnuc_minepia_laisser_passer_sanitaire/objects/<model("patnuc_minepia_laisser_passer_sanitaire.patnuc_minepia_laisser_passer_sanitaire"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('patnuc_minepia_laisser_passer_sanitaire.object', {
#             'object': obj
#         })

