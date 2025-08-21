from odoo import models, fields

class HomologationTest(models.Model):
    _name = 'homologation.test'
    _description = "Test d'analyse réalisé sur le produit"

    name = fields.Char(string="Nom du test", required=True)
    test_type_id = fields.Many2one('homologation.test.type', string="Type de test")
    laboratory_id = fields.Many2one('homologation.laboratory', string="Laboratoire")
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('in_progress', 'En cours'),
        ('done', 'Terminé')
    ], string="État", default='draft')
    start_date = fields.Date(string="Date de début")
    end_date = fields.Date(string="Date de fin")
    result = fields.Text(string="Résultat")
    request_id = fields.Many2one('homologation.request', string="Dossier associé")
