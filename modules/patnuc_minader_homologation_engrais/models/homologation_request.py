# homologation_engrais/models/homologation_demande.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HomologationRequest(models.Model):
    _name = 'homologation.request'
    _description = "Demande d'Homologation d'Engrais"
    _inherit = ['mail.thread']

    name = fields.Char("Référence", required=True, copy=False, default="Nouvelle")
    demandeur_id = fields.Many2one('res.partner', string="Demandeur", required=True, default=lambda self: self.env.user)
    produit_id = fields.Many2one('homologation.produit', string="Engrais", required=True)

    date_demande = fields.Date("Date de Soumission", default=fields.Date.today)

    # documents requis
    notice_utilisation = fields.Binary(string='Notice d\'utilisation', attachment=True, required=True)
    demande_timbree = fields.Binary(string='Demande timbrée', attachment=True, required=True)
    dossier_technique = fields.Binary(string='Dossier technique', attachment=True, required=True)
    justificatif_frais = fields.Binary(string='Justificatif des frais', attachment=True, required=True)
    cni_avant = fields.Binary(string="Scan CNI (recto)", attachment=True, required=True)
    cni_arriere = fields.Binary(string="Scan CNI (verso)", attachment=True, required=True)

    #motif de rejet
    rejection_reason = fields.Text(string='Motif de rejet')

    # champ pour la verification administrative
    admin_verification_date = fields.Date(string='Date de vérification administrative')
    admin_verification_agent_id = fields.Many2one('res.users', string='Agent de vérification administrative')
    admin_verification_notes = fields.Text(string='Notes de vérification administrative')

    # champs pour valider chaque document
    notice_utilisation_valid = fields.Boolean(string='Notice d\'utilisation validée')
    demande_timbree_valid = fields.Boolean(string='Demande timbrée validée')
    dossier_technique_valid = fields.Boolean(string='Dossier technique validé')
    justificatif_frais_valid = fields.Boolean(string='Justificatif des frais validé')
    cni_avant_valid = fields.Boolean(string='Scan CNI (recto) validé')
    cni_arriere_valid = fields.Boolean(string='Scan CNI (verso) validé')

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('admin_check', 'Vérification administrative'),
        ('conformity_control', 'Contrôle de conformité'),
        ('quality_control', 'Contrôle de qualité'),
        ('agronomic_tests', 'Tests d\'efficacité agronomique'),
        ('evaluation', 'Évaluation agro-économique'),
        ('final_validation', 'Validation finale'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
    ], string='Statut', default='draft')



    # Actions workflow
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('homologation.engrais') or 'Nouveau'
        return super(HomologationRequest, self).create(vals)

    def action_submit(self):
        """Passe la demande de l'état 'Brouillon' à 'Soumise' et envoie une notification."""
        for rec in self:
            rec.state = 'admin_check'
            rec.message_post(body="La demande a été soumise. Vérification administrative en attente.")



    def action_conformity_control(self):
        """Action pour valider la demande après vérification administrative."""
        self.state = 'conformity_control'
        self.admin_verification_date = fields.Date.today()
        self.admin_verification_agent_id = self.env.user.id
        self.message_post(
            body="La vérification administrative est conforme. Contrôle de qualité en attente.")


    def action_quality_control(self):
        pass

    def action_agronomic_tests(self):
        pass

    def action_evaluation(self):
        pass

    def action_final_validation(self):
        pass

    def action_approve(self):
        """Passe la demande à l'état 'Approuvée' et envoie une notification."""
        for rec in self:
            rec.state = 'approved'
            rec.message_post(body="La demande a été approuvée.")

    def action_reject(self, motif=""):
        """Passe la demande à l'état 'Rejetée' et envoie une notification."""
        for rec in self:
            rec.state = 'rejected'
            rec.message_post(body="La demande a été rejetée.")
            self.write({'state': 'rejected', 'rejection_reason': motif})


    def action_valider(self):
        next_state = {
            'soumis': 'analyse',
            'analyse': 'test',
            'test': 'evaluation',
            'evaluation': 'valide'
        }
        if self.state in next_state:
            self.write({'state': next_state[self.state]})
        else:
            raise UserError("Impossible de valider depuis cet état.")

