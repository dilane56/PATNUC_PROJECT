from odoo import models, fields, api

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

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('laissez.passer') or 'Nouveau'
        return super(LaissezPasserSanitaire, self).create(vals)

    def action_submit(self):
        """Action pour soumettre la demande."""
        self.state = 'administrative_control'
        self.message_post(body="La demande de laissez-passer a et la verification administrative est en attente.")


    def action_deeper_check(self):
        """Action pour lancer la vérification approfondie."""
        self.state = 'deeper_check'
        self.message_post(body="La demande est passée à l'étape de vérification approfondie.")

    def action_approve(self):
        """Action pour approuver et délivrer le laissez-passer."""
        self.state = 'approved'
        self.message_post(body="Le laissez-passer a été approuvé et est en attente de signature par le delegue Régionale.")