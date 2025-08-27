from odoo import models, fields, api, _


class CertificationRequest(models.Model):
    _name = 'certification.request'
    _description = 'Demande de certification phytosanitaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Numéro de la demande', required=True, copy=False, readonly=True, default='Nouveau')

   #demandeur
    demandeur_id = fields.Many2one('res.partner', string='Demandeur', required=True)
    demandeur_compagny = fields.Char(string="Structure/ Entreprise")
    date_demande = fields.Date(string='Date de dépôt de la demande', default=fields.Date.today)

    # Par ce champ de liaison
    appareil_id = fields.Many2one('certification.appareil', string='Appareil', required=True)

    # ... (Ajoutez ces deux champs calculés pour plus de facilité d'accès à l'information)
    appareil_marque = fields.Char(string='Marque de l\'appareil', related='appareil_id.marque', readonly=True)
    appareil_type = fields.Selection(related='appareil_id.type_appareil', readonly=True)

    #documents
    caracteristiques_techniques = fields.Binary(string='fiche techniques', required=True)
    manuel_utilisation = fields.Binary(string='Manuel d\'utilisation', attachment=True, required=True)
    rapports_tests_techniques = fields.Binary(string='Rapports de test techniques', attachment=True)
    rapports_tests_champ = fields.Binary(string='Rapports de tests sur le terrain', attachment=True)
    engagement_apres_vente = fields.Binary(string='Engagement de service après-vente', required=True)
    demande_timbree = fields.Binary(string='Demande timbrée', attachment=True, required=True)
    cni_avant = fields.Binary(string="Scan CNI (recto)", attachment=True, required=True)
    cni_arriere = fields.Binary(string="Scan CNI (verso)", attachment=True, required=True)

    #Motif de rejet
    rejection_reason = fields.Text(string='Motif de rejet')

    # Champs pour la vérification administrative
    admin_verification_date = fields.Date(string="Date de vérification administrative", readonly=True)
    admin_verification_agent_id = fields.Many2one('res.users', string="Agent vérificateur", readonly=True)

    # Champs pour valider chaque document
    caracteristiques_techniques_ok = fields.Boolean(string="Fiche techniques valide")
    manuel_utilisation_ok = fields.Boolean(string="Manuel d'utilisation valide")
    rapports_tests_techniques_ok = fields.Boolean(string="Rapports de test techniques valide")
    demande_timbree_ok = fields.Boolean(string="Demande timbrée valide")
    rapports_tests_champ_ok = fields.Boolean(string="Rapports de tests sur le terrain valide")
    cni_avant_ok = fields.Boolean(string="CNI avant valide")
    cni_arriere_ok = fields.Boolean(string="CNI arrière valide")
    engagement_apres_vente_ok = fields.Boolean(string="Engagement après-vente valide")

    admin_verification_comment = fields.Text(string="Commentaires de l'agent")

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('admin_check', 'Vérification administrative'),
        ('lab_tests', 'Tests de spécifications (labo)'),
        ('field_tests', 'Tests de performance (champ)'),
        ('synthesis', 'Synthèse'),
        ('decision', 'Décision de la Commission'),
        ('minister_sign', 'Signature du Ministre'),
        ('certified', 'Certificat émis'),
        ('rejected', 'Rejetée'),
    ], string='Statut', default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('certification.phytosanitaire')
        result = super(CertificationRequest, self).create(vals)
        return result

    def action_submit(self):
        """Passe la demande de l'état 'Brouillon' à 'Soumise' et envoie une notification."""
        for rec in self:
            rec.state = 'admin_check'
            rec.message_post(body="La demande de certification a été soumise.")


        # Mettez à jour les méthodes de workflow pour inclure ces champs

    def action_admin_check_ok(self):
        """Action pour valider la demande après vérification administrative."""
        self.state = 'lab_tests'
        self.admin_verification_date = fields.Date.today()
        self.admin_verification_agent_id = self.env.user.id
        self.message_post(
            body="La vérification administrative est conforme. La demande passe à l'étape des tests de spécifications.")

    def action_admin_check_rejected(self):
        """Action pour rejeter la demande après vérification administrative."""
        self.state = 'rejected'
        self.admin_verification_date = fields.Date.today()
        self.admin_verification_agent_id = self.env.user.id
        self.message_post(body="La demande a été rejetée lors de la vérification administrative.")




    def action_field_tests(self):
        for rec in self:
            rec.state = 'field_tests'
            rec.message_post(body="Les tests de performance (champ) ont été effectués.")


    def action_synthesis(self):
        for rec in self:
            rec.state = 'synthesis'
            rec.message_post(body="La synthèse a été effectuée.")

    def action_decision(self):
        for rec in self:
            rec.state = 'decision'
            rec.message_post(body="La décision de la Commission a été prise.")

    def action_minister_sign(self):
        for rec in self:
            rec.state = 'minister_sign'
            rec.message_post(body="La signature du Ministre a été effectuée.")

    def action_certify(self):
        for rec in self:
            rec.state = 'certified'
            rec.message_post(body="Le certificat a été émis.")

    def action_reject(self):
        if self.state == 'admin_check':
            self.admin_verification_date = fields.Date.today()
            self.admin_verification_agent_id = self.env.user.id
            self.state = 'rejected'
            for rec in self:
                rec.state = 'rejected'
                rec.message_post(body="La demande a été rejetée lors de la vérification administrative.")

        for rec in self:
            rec.state = 'rejected'
            rec.message_post(body="La demande a été rejetée.")