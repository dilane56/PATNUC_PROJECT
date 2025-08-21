
from odoo import models, fields , api

class CertificationRequest(models.Model):
    _name = 'certification.request'
    _description = 'Demande de certification phytosanitaire'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Ajout des fonctionnalités de suivi

    name = fields.Char(string='Request Name', required=True, readonly = True, default=lambda  self: self.env['ir.sequence'].next_by_code('certification.request'))
    demandeur_id = fields.Many2one('res.partner', string='Demandeur', required=True)
    date_demande = fields.Date(string='Date de depôt de la demande', default=fields.Date.today)

    appareil_marque = fields.Char(string='Appareil Marque', required=True)
    appareil_type = fields.Selection([
        ('pulverisateurs_dos_pression_entretenue', 'Pulvérisateurs à dos à pression entretenue'),
        ('pulverisateurs_dos_moteur', 'Pulvérisateurs à dos à moteur'),
        ('pulverisateurs_dos_pression_prealable', 'Pulvérisateurs à dos à pression préalable'),
        ('Pulvérisateurs centrifuges', 'Pulvérisateurs centrifuges'),
        ('Appareils de nébulisation thermique', 'Appareils de nébulisation thermique'),
        ('Poudreuses', 'Poudreuses'),
        ('Applicateurs de granules', 'Applicateurs de granules'),
        ('Nébulisateurs à froid', 'Nébulisateurs à froid'),
        ('Appareils tractés', 'Appareils tractés')
    ], string='Type d\'appareil', required=True)

    caracteristiques_techniques = fields.Text(string='Caractéristiques techniques', required=True)
    manuel_utilisation = fields.Binary(string='Manuel d\'utilisation', attachment=True)
    rapports_tests_techniques = fields.Binary(string='Rapports de test techniques', attachment=True)
    rapports_tests_champ = fields.Binary(string='Rapports de tests sur le terrain', attachment=True)
    engagement_apres_vente = fields.Text(string='Engagement de service après-vente', required=True)
    demande_timbree = fields.Binary(string='Demande timbrée', attachment=True)
    photocopie_carte_identite = fields.Binary(string='Photocopie de la carte d\'identité', attachment=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumise'),
        ('in_review', 'En revue'),
        ('certified', 'Certifiée'),
        ('rejected', 'Rejetée'),
    ], string='Statut', default='draft')

    @api.model
    def create(self, vals):
        """
        Génère un numéro de séquence unique pour chaque nouvelle demande.
        """
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('certification.phytosanitaire') or 'Nouveau'
        return super(CertificationRequest, self).create(vals)

    def action_submit(self):
        """
        Passe la demande de l'état 'Brouillon' à 'Soumise'.
        """
        for rec in self:
            rec.state = 'submitted'

    def action_review(self):
        """
        Passe la demande de l'état 'Soumise' à 'En revue'.
        """
        for rec in self:
            rec.state = 'in_review'

    def action_certify(self):
        """
        Passe la demande à l'état 'Certifiée'.
        """
        for rec in self:
            rec.state = 'certified'

    def action_reject(self):
        """
        Passe la demande à l'état 'Rejetée'.
        """
        for rec in self:
            rec.state = 'rejected'