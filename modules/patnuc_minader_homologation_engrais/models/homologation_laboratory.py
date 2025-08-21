from odoo import models, fields

class HomologationLaboratory(models.Model):
    _name = 'homologation.laboratory'
    _description = "Laboratoire d'analyse"

    name = fields.Char(string="Nom du laboratoire", required=True)
    address = fields.Char(string="Adresse")
    contact_person = fields.Char(string="Personne de contact")
    contact_email = fields.Char(string="Email de contact")
    contact_phone = fields.Char(string="Téléphone de contact")
    analysis_capabilities = fields.Many2many('homologation.test.type', string="Capacités d'analyse")
    test_ids = fields.One2many('homologation.test', 'laboratory_id', string="Tests effectués")
