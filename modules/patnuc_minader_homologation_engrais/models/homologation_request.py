# Nouveau fichier sans préfixe fertilizer
from odoo import models, fields, api
from odoo.exceptions import UserError

class HomologationRequest(models.Model):
    _name = 'homologation.request'
    _description = "Dossier d'homologation du produit"

    name = fields.Char(string="Numéro du dossier", required=True)
    applicant_id = fields.Many2one('homologation.applicant', string="Demandeur")
    company_id = fields.Many2one('homologation.company', string="Entreprise")
    product_id = fields.Many2one('homologation.product', string="Produit")
    application_type = fields.Selection([
        ('homologation', 'Homologation'),
        ('renewal', 'Renouvellement')
    ], string="Type de demande", default='homologation')
    stage_id = fields.Many2one('homologation.stage', string="Étape du workflow")
    submission_date = fields.Date(string="Date de soumission")
    approval_date = fields.Date(string="Date d'approbation")
    expiry_date = fields.Date(string="Date d'expiration")
    fees_paid = fields.Boolean(string="Frais payés")
    samples_deposited = fields.Boolean(string="Échantillons déposés")
    document_ids = fields.One2many('homologation.document', 'request_id', string="Documents joints")
    test_ids = fields.One2many('homologation.test', 'request_id', string="Tests réalisés")
    
    def action_submit_dossier(self):
        """Soumettre le dossier pour traitement"""
        for record in self:
            # Vérifier que les informations requises sont remplies
            if not record.applicant_id:
                raise UserError("Le demandeur doit être renseigné.")
            if not record.company_id:
                raise UserError("L'entreprise doit être renseignée.")
            if not record.product_id:
                raise UserError("Le produit doit être renseigné.")
            
            # Passer à l'étape suivante (Soumis)
            next_stage = self.env['homologation.stage'].search([('name', '=', 'Soumis')], limit=1)
            if next_stage:
                record.write({
                    'stage_id': next_stage.id,
                    'submission_date': fields.Date.today()
                })
                record.message_post(body="Dossier soumis pour traitement")
            else:
                raise UserError("L'étape 'Soumis' n'a pas été trouvée dans la configuration.")
    

