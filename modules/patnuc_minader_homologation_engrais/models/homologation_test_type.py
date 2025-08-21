from odoo import models, fields

class HomologationTestType(models.Model):
    _name = 'homologation.test.type'
    _description = "Type de test d'analyse"

    name = fields.Char(string="Nom du test", required=True)
    description = fields.Text(string="Description")
    laboratory_ids = fields.Many2many('homologation.laboratory', string="Laboratoires réalisant ce test")
    test_ids = fields.One2many('homologation.test', 'test_type_id', string="Tests réalisés")
