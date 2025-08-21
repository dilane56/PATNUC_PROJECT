# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class patnuc_minader_homologation_engrais(models.Model):
#     _name = 'patnuc_minader_homologation_engrais.patnuc_minader_homologation_engrais'
#     _description = 'patnuc_minader_homologation_engrais.patnuc_minader_homologation_engrais'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

