# -*- coding: utf-8 -*-
# from odoo import http


# class PatnucMinepiaPermisPecheArtisanale(http.Controller):
#     @http.route('/patnuc_minepia_permis_peche_artisanale/patnuc_minepia_permis_peche_artisanale', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/patnuc_minepia_permis_peche_artisanale/patnuc_minepia_permis_peche_artisanale/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('patnuc_minepia_permis_peche_artisanale.listing', {
#             'root': '/patnuc_minepia_permis_peche_artisanale/patnuc_minepia_permis_peche_artisanale',
#             'objects': http.request.env['patnuc_minepia_permis_peche_artisanale.patnuc_minepia_permis_peche_artisanale'].search([]),
#         })

#     @http.route('/patnuc_minepia_permis_peche_artisanale/patnuc_minepia_permis_peche_artisanale/objects/<model("patnuc_minepia_permis_peche_artisanale.patnuc_minepia_permis_peche_artisanale"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('patnuc_minepia_permis_peche_artisanale.object', {
#             'object': obj
#         })

