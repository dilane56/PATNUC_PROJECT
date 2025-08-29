# -*- coding: utf-8 -*-
# from odoo import http


# class PatnucMinepiaCertificatSanitaire(http.Controller):
#     @http.route('/patnuc_minepia_certificat_sanitaire/patnuc_minepia_certificat_sanitaire', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/patnuc_minepia_certificat_sanitaire/patnuc_minepia_certificat_sanitaire/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('patnuc_minepia_certificat_sanitaire.listing', {
#             'root': '/patnuc_minepia_certificat_sanitaire/patnuc_minepia_certificat_sanitaire',
#             'objects': http.request.env['patnuc_minepia_certificat_sanitaire.patnuc_minepia_certificat_sanitaire'].search([]),
#         })

#     @http.route('/patnuc_minepia_certificat_sanitaire/patnuc_minepia_certificat_sanitaire/objects/<model("patnuc_minepia_certificat_sanitaire.patnuc_minepia_certificat_sanitaire"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('patnuc_minepia_certificat_sanitaire.object', {
#             'object': obj
#         })

