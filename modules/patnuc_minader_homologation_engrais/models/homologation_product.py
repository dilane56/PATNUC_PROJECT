from odoo import models, fields

class HomologationProduct(models.Model):
    _name = 'homologation.product'
    _description = "Produit à homologuer"

    name = fields.Char(string="Nom du produit", required=True)
    code = fields.Char(string="Code produit")
    composition = fields.Text(string="Composition")
    manufacturer = fields.Char(string="Fabricant")
    homologation_ids = fields.One2many('homologation.request', 'product_id', string="Dossiers d'homologation")
