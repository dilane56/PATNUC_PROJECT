from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LaissezPasserSanitaire(models.Model):
    _name = 'laissez.passer'
    _description = 'Demande de Laissez-passer Sanitaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Numéro de demande', required=True, copy=False, readonly=True, default='Nouveau')
    initiateur_id = fields.Many2one('res.partner', string='Initiateur', required=True)
    date_demande = fields.Date(string='Date de la demande', default=fields.Date.today(), readonly=True)

    type_demande = fields.Selection([
        ('animaux', 'Animaux'),
        ('denrees', 'Denrées d\'origine animale'),
        ('halieutique', 'Denrées halieutiques')
    ], string='Objet de la demande', required=True)



    # Pièces à fournir
    certificat_sanitaire = fields.Binary(string='Certificat Sanitaire Vétérinaire', attachment=True)
    photocopie_cni = fields.Binary(string='Photocopie de CNI', attachment=True)
    recu_paiement = fields.Binary(string='Reçu de paiement de la taxe', attachment=True)
    declaration_denree = fields.Binary(string='Déclaration des animaux/denrées', required=True)

    delai_imparti = fields.Integer(string='Délai de traitement (jours)', default=2, readonly=True)

    # Champs pour la vérification administrative
    administrative_check_date = fields.Date(string="Date de vérification administrative", readonly=True)
    administrative_checker_id = fields.Many2one('res.users', string="Agent vérificateur", readonly=True)

    # Champs de validation des documents
    declaration_ok = fields.Boolean(string="Déclaration des animaux valide")
    certificat_sanitaire_ok = fields.Boolean(string="Certificat sanitaire valide")
    cni_ok = fields.Boolean(string="CNI valide")
    recu_paiement_ok = fields.Boolean(string="Reçu de paiement valide")

    administrative_check_comment = fields.Char(string="Commentaires de l'agent de verification admin")
    
    # Champ calculé pour la validation
    can_validate_admin = fields.Boolean(string="Peut valider", compute="_compute_can_validate_admin")

    # Verification approfondie
    deeper_check_date = fields.Date(string="Date de la vérification approfondie", readonly=True)
    deeper_checker_id = fields.Many2one('res.users', string="Agent de la vérification approfondie", readonly=True)
    deeper_check_result = fields.Selection([
        ('favorable', ' Favorable'),
        ('unfavorable', ' Défavorable'),
    ], string="Avis sur la demande", required=False)

    #Motif de rejet
    rejection_reason = fields.Text(string='Motif de rejet')

    # Workflow
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('administrative_control', 'Contrôle Administratif'),
        ('deeper_check', 'Vérification Approfondie'),
        ('approved', 'Signature et delivrance'),
        ('rejected', 'Rejetée'),
    ], string='Statut', default='draft', tracking=True)

    @api.depends('declaration_ok', 'cni_ok', 'recu_paiement_ok', 'certificat_sanitaire_ok','administrative_check_comment')
    def _compute_can_validate_admin(self):
        for record in self:
            record.can_validate_admin = record._all_documents_validated()

    def _all_documents_validated(self):
        """Vérifie si tous les documents requis sont validés."""
        required_fields = ['declaration_ok', 'cni_ok', 'recu_paiement_ok', 'certificat_sanitaire_ok','administrative_check_comment']
        return all(getattr(self, field) for field in required_fields)

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('laissez.passer') or 'Nouveau'
        return super(LaissezPasserSanitaire, self).create(vals)

    def action_submit(self):
        """Action pour soumettre la demande."""
        self.state = 'administrative_control'
        self.message_post(body="La demande de laissez-passer a et la verification administrative est en attente.")


    def action_admin_check_ok(self):
        """Action pour valider la demande après vérification administrative."""
        if not self._all_documents_validated():
            from odoo.exceptions import ValidationError
            raise ValidationError("Impossible de valider. Tous les documents doivent être vérifiés et approuvés.")
        
        self.ensure_one()
        self.state = 'deeper_check'
        self.administrative_check_date = fields.Date.today()
        self.administrative_checker_id = self.env.user.id
        self.message_post(body="Vérification administrative effectuée et approuvée. Vérification approfondie en attente.")

    def action_deeper_check_ok(self):
        """Action pour valider la vérification approfondie et passer à l'approbation."""
        self.ensure_one()
        if self.deeper_check_result != 'favorable':
            raise ValidationError("La demande ne peut être validée qu'avec un avis favorable.")

        self.state = 'approved'
        self.deeper_check_date = fields.Date.today()
        self.deeper_checker_id = self.env.user.id
        self.message_post(
            body="Vérification approfondie validée avec un avis favorable. La demande passe à l'approbation.")



    def action_approve(self):
        """Action pour approuver et délivrer le laissez-passer."""
        self.state = 'approved'
        self.message_post(body="Le laissez-passer a été approuvé et est en attente de signature par le delegue Régionale.")