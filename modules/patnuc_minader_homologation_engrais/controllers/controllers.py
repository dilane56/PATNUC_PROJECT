# -*- coding: utf-8 -*-
# from odoo import http


# class PatnucMinaderHomologationEngrais(http.Controller):
#     @http.route('/patnuc_minader_homologation_engrais/patnuc_minader_homologation_engrais', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/patnuc_minader_homologation_engrais/patnuc_minader_homologation_engrais/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('patnuc_minader_homologation_engrais.listing', {
#             'root': '/patnuc_minader_homologation_engrais/patnuc_minader_homologation_engrais',
#             'objects': http.request.env['patnuc_minader_homologation_engrais.patnuc_minader_homologation_engrais'].search([]),
#         })

#     @http.route('/patnuc_minader_homologation_engrais/patnuc_minader_homologation_engrais/objects/<model("patnuc_minader_homologation_engrais.patnuc_minader_homologation_engrais"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('patnuc_minader_homologation_engrais.object', {
#             'object': obj
#         })

