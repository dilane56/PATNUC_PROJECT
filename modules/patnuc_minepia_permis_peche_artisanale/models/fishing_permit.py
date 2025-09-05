from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FishingPermit(models.Model):
    _name = 'fishing.permit'
    _description = 'Demande de Permis de Pêche Artisanale'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Numéro de demande', required=True, copy=False, readonly=True, default='Nouveau')
    applicant_id = fields.Many2one('res.partner', string='Demandeur', required=True, tracking=True)
    date_demande = fields.Date(string='Date de la demande', default=fields.Date.today(), readonly=True, tracking=True)
    duree_traitement = fields.Integer(string='Durée de traitement (en jours)',default=14,readonly=True)

    # Pièces à fournir
    stamped_request = fields.Binary(string="Demande timbrée", attachment=True, required=True)
    photos = fields.Binary(string="Deux photos d'identité 4x4", attachment=True, required=True)
    fishing_gear_info = fields.Binary(string="Désignation des engins de pêche", attachment=True, required=True)
    boat_info = fields.Binary(string="Désignation des embarcations et zones de pêche", attachment=True, required=True)

    # Champs pour la vérification administrative
    admin_check_date = fields.Date(string="Date de vérification administrative", readonly=True, tracking=True)
    admin_checker_id = fields.Many2one('res.users', string="Agent de vérification", readonly=True, tracking=True)
    admin_check_comment = fields.Char(string="Commentaires de l'agent de vérification", tracking=True)

    # Validation des documents administratifs
    stamped_request_ok = fields.Boolean(string="Demande timbrée validée", tracking=True)
    photos_ok = fields.Boolean(string="Photos d'identité validées", tracking=True)
    fishing_gear_ok = fields.Boolean(string="Désignation des engins validée", tracking=True)
    boat_info_ok = fields.Boolean(string="Désignation des embarcations validée", tracking=True)

    # Champ pour l'analyse approfondie
    deep_analysis_date = fields.Date(string="Date d'analyse approfondie", readonly=True, tracking=True)
    deep_analyzer_id = fields.Many2one('res.users', string="Agent d'analyse", readonly=True, tracking=True)
    deep_analysis_result = fields.Selection([
        ('favorable', 'Favorable'),
        ('unfavorable', 'Défavorable')
    ], string="Avis sur la demande", tracking=True)
    rapport_analyse = fields.Binary(string="Rapport d'inspection", attachment=True)
    deep_analysis_comment = fields.Text(string="Rapport d'inspection detailleé", tracking=True)

    # Signature et délivrance
    signed_by_id = fields.Many2one('res.users', string="Signé par", readonly=True, tracking=True)
    signature_date = fields.Date(string="Date de signature", readonly=True, tracking=True)
    signed_by_signature = fields.Binary(string="Signature de l'approbateur", attachment=True)
    permit_file = fields.Binary(string="Fichier du permis délivré", readonly=True, attachment=True)
    permit_filename = fields.Char(string="Nom du fichier")

    # Motif de rejet
    rejection_reason = fields.Text(string='Motif de rejet')

    # Workflow
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('admin_check', 'Contrôle Administratif'),
        ('deep_analysis', 'Instruction technique'),
        ('approved', 'Signature et Delivrance'),
        ('rejected', 'Rejetée'),
    ], string='Statut', default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('fishing.permit') or 'Nouveau'
        return super(FishingPermit, self).create(vals)

    def action_submit(self):
        self.state = 'admin_check'
        self.message_post(body="La demande a été soumise pour contrôle administratif.")

    def action_admin_approve(self):
        required_fields = ['stamped_request_ok', 'photos_ok', 'fishing_gear_ok', 'boat_info_ok']
        if not all(getattr(self, field) for field in required_fields):
            raise ValidationError("Veuillez valider tous les documents requis ")
        if not self.admin_check_comment:
            raise ValidationError("Veuillez fournir un commentaire pour la vérification administrative.")

        self.state = 'deep_analysis'
        self.admin_check_date = fields.Date.today()
        self.admin_checker_id = self.env.user.id
        self.message_post(body="Contrôle administratif validé. La demande passe à l'analyse approfondie.")

    def action_deep_analysis_approve(self):
        if self.deep_analysis_result != 'favorable':
            raise ValidationError("La demande ne peut être approuvée qu'avec un avis favorable.")
        if not self.deep_analysis_comment and not self.rapport_analyse:
            raise ValidationError("Veuillez fournir un rapport d'inspection.")
        self.state = 'approved'
        self.deep_analysis_date = fields.Date.today()
        self.deep_analyzer_id = self.env.user.id
        self.signed_by_id = self.env.user.id
        self.signature_date = fields.Date.today()
        self.message_post(body="Analyse approfondie validée. Le permis a été approuvé.")

    def action_reject(self):
        self.state = 'rejected'
        self.message_post(body=f"La demande a été rejetée. Motif : {self.rejection_reason}")

    def action_print_permit(self):
        return self.env.ref('patnuc_minepia_permis_peche_artisanale.action_report_fishing_permit').report_action(self)

    def action_back_to_previous_state(self):
        """Retourner à l'état précédent"""
        state_transitions = {
            'admin_check': 'draft',
            'deep_analysis': 'admin_check',
            'approved': 'deep_analysis',
        }
        
        if self.state in state_transitions:
            previous_state = state_transitions[self.state]
            self.state = previous_state
            self.message_post(body=f"Retour à l'état précédent : {dict(self._fields['state'].selection)[previous_state]}")
        else:
            raise ValidationError("Impossible de retourner à l'état précédent depuis cet état.")