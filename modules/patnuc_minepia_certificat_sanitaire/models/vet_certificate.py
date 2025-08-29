from odoo import models, fields, api

class VeterinaryCertificate(models.Model):
    _name = 'vet.certificate'
    _description = 'Demande de Certificat Sanitaire Vétérinaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Numéro de demande', required=True, copy=False, readonly=True, default='Nouveau')
    initiateur_id = fields.Many2one('res.partner', string='Initiateur', required=True)
    date_demande = fields.Date(string='Date de la demande', default=fields.Date.today(), readonly=True)
    delai_imparti = fields.Integer(string='Délai de traitement (jours)', default=2, readonly=True)

    type_demande = fields.Selection([
        ('animaux', 'Animaux'),
        ('denrees', 'Denrées d\'origine animale'),
        ('halieutique', 'Denrées halieutiques')
    ], string='Objet de la demande', required=True)



    # Pièces à fournir
    declaration_denrees = fields.Binary(string="Déclaration des Animaux ou denréé d'origine animale ou halieutique", attachment=True)
    carnet_vaccination = fields.Binary(string='Carnet de vaccination', attachment=True)
    photocopie_cni = fields.Binary(string='Photocopie de CNI', attachment=True)
    recu_paiement = fields.Binary(string='Reçu de paiement de la taxe', attachment=True)


    # Motif de rejet
    rejection_reason = fields.Text(string='Motif de rejet')

    # Administrative verification fields
    administrative_check_date = fields.Date(string="Date de vérification administrative", readonly=True)
    administrative_checker_id = fields.Many2one('res.users', string="Agent vérificateur", readonly=True)

    # Document validation fields
    declaration_ok = fields.Boolean(string="Déclaration des animaux valide")
    certificat_sanitaire_ok = fields.Boolean(string="Certificat sanitaire valide")
    cni_ok = fields.Boolean(string="CNI valide")
    recu_paiement_ok = fields.Boolean(string="Reçu de paiement valide")

    administrative_check_comment = fields.Text(string="Commentaires de l'agent")
    
    # Champ calculé pour la validation
    can_validate_admin = fields.Boolean(string="Peut valider", compute="_compute_can_validate_admin")

    # Workflow
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('administrative_control', 'Contrôle Administratif'),
        ('deep_check', 'Verification Aprofondie'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
    ], string='Statut', default='draft')

    @api.depends('declaration_ok', 'cni_ok', 'recu_paiement_ok', 'certificat_sanitaire_ok', 'type_demande','administrative_check_comment')
    def _compute_can_validate_admin(self):
        for record in self:
            record.can_validate_admin = record._all_documents_validated()

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('vet.certificate') or 'Nouveau'
        return super(VeterinaryCertificate, self).create(vals)

    def action_submit(self):
        """Action pour soumettre la demande."""
        self.state = 'administrative_control'
        self.message_post(body="La demande a été soumise et la verification administrative en attente")

    def _all_documents_validated(self):
        """Vérifie si tous les documents requis sont validés."""
        required_fields = ['declaration_ok', 'cni_ok', 'recu_paiement_ok','administrative_check_comment']
        if self.type_demande == 'animaux':
            required_fields.append('certificat_sanitaire_ok')
        
        return all(getattr(self, field) for field in required_fields)

    def action_technical_inspection(self):
        """Action pour valider le contrôle administratif et lancer l'inspection sanitaire."""
        if not self._all_documents_validated():
            from odoo.exceptions import ValidationError
            raise ValidationError("Impossible de valider. Tous les documents doivent être vérifiés et approuvés.")
        
        self.state = 'deep_check'
        self.administrative_check_date = fields.Date.today()
        self.administrative_checker_id = self.env.user.id
        self.message_post(body="Vérification administrative effectuée et approuvée. La demande passe à l'inspection technique.")



    def action_approve(self):
        """Action pour approuver et délivrer le certificat."""
        self.state = 'approved'
        self.message_post(body="Le certificat sanitaire a été approuvé et délivré.")

