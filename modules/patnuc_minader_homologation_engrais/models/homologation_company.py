from odoo import models, fields

class HomologationCompany(models.Model):
    _name = 'homologation.company'
    _description = "Entreprise liée à l'homologation"

    name = fields.Char(string="Nom de l'entreprise", required=True)
    code = fields.Char(string="Code interne")
    company_type = fields.Selection([
        ('manufacturer', 'Fabricant'),
        ('importer', 'Importateur'),
        ('distributor', 'Distributeur'),
        ('research_institute', 'Institut de recherche'),
        ('university', 'Université'),
        ('cooperative', 'Coopérative')
    ], string="Type d'entreprise")
    legal_form = fields.Char(string="Forme juridique")
    country_id = fields.Many2one('res.country', string="Pays")
    contact_person = fields.Char(string="Personne de contact")
    contact_email = fields.Char(string="Email de contact")
    contact_phone = fields.Char(string="Téléphone de contact")
    registration_number = fields.Char(string="Numéro d'enregistrement")
    tax_id = fields.Char(string="Identifiant fiscal")
    phone = fields.Char(string="Téléphone")
    email = fields.Char(string="Email")
    website = fields.Char(string="Site web")
    address = fields.Char(string="Adresse")
    city = fields.Char(string="Ville")
    registration_certificate = fields.Binary(string="Certificat d'enregistrement")
    registration_certificate_filename = fields.Char(string="Nom du fichier certificat")
    tax_certificate = fields.Binary(string="Certificat fiscal")
    tax_certificate_filename = fields.Char(string="Nom du fichier fiscal")
    import_license = fields.Binary(string="Licence d'importation")
    import_license_filename = fields.Char(string="Nom du fichier import")
    manufacturing_license = fields.Binary(string="Licence de fabrication")
    manufacturing_license_filename = fields.Char(string="Nom du fichier fabrication")
    research_authorization = fields.Binary(string="Autorisation de recherche")
    research_authorization_filename = fields.Char(string="Nom du fichier recherche")
    homologation_ids = fields.One2many('homologation.request', 'company_id', string="Dossiers d'homologation")