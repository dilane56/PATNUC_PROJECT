# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class patnuc_minader_certification_appareils_phytosanitaires(models.Model):
#     _name = 'patnuc_minader_certification_appareils_phytosanitaires.patnuc_minader_certification_appareils_phytosanitaires'
#     _description = 'patnuc_minader_certification_appareils_phytosanitaires.patnuc_minader_certification_appareils_phytosanitaires'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

