from odoo import models, fields

class HomologationApplicant(models.Model):
    _name = 'homologation.applicant'
    _description = "Demandeur d'homologation"

    name = fields.Char(string="Nom du demandeur", required=True)
    identification_number = fields.Char(string="Numéro d'identification")
    company_name = fields.Char(string="Nom de l'entreprise")
    email = fields.Char(string="Email")
    applicant_type = fields.Selection([
        ('private_company', 'Entreprise privée'),
        ('manufacturer', 'Fabricant'),
        ('importer', 'Importateur'),
        ('research_institute', 'Institut de recherche'),
        ('university', 'Université'),
        ('cooperative', 'Coopérative')
    ], string="Type de demandeur")
    nationality = fields.Char(string="Nationalité")
    homologation_ids = fields.One2many('homologation.request', 'applicant_id', string="Dossiers d'homologation")