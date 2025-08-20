# -*- coding: utf-8 -*-
# from odoo import http


# class PatnucMinaderCertificationAppareilsPhytosanitaires(http.Controller):
#     @http.route('/patnuc_minader_certification_appareils_phytosanitaires/patnuc_minader_certification_appareils_phytosanitaires', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/patnuc_minader_certification_appareils_phytosanitaires/patnuc_minader_certification_appareils_phytosanitaires/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('patnuc_minader_certification_appareils_phytosanitaires.listing', {
#             'root': '/patnuc_minader_certification_appareils_phytosanitaires/patnuc_minader_certification_appareils_phytosanitaires',
#             'objects': http.request.env['patnuc_minader_certification_appareils_phytosanitaires.patnuc_minader_certification_appareils_phytosanitaires'].search([]),
#         })

#     @http.route('/patnuc_minader_certification_appareils_phytosanitaires/patnuc_minader_certification_appareils_phytosanitaires/objects/<model("patnuc_minader_certification_appareils_phytosanitaires.patnuc_minader_certification_appareils_phytosanitaires"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('patnuc_minader_certification_appareils_phytosanitaires.object', {
#             'object': obj
#         })

