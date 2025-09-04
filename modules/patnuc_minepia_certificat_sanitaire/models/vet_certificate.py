import base64

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import datetime


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

    administrative_check_comment = fields.Char(string="Commentaires de l'agent de verification ")
    
    # Champ calculé pour la validation
    can_validate_admin = fields.Boolean(string="Peut valider", compute="_compute_can_validate_admin")

    # Champ de la verification approfondie
    deep_check_date = fields.Date(string="Date de vérification approfondie", readonly=True)
    deep_checker_id = fields.Many2one('res.users', string="Agent de vérification approfondie", readonly=True)
    deeper_check_result = fields.Selection([
        ('favorable', ' Favorable'),
        ('unfavorable', ' Défavorable'),
    ], string="Avis sur la demande", required=False)

    # Signature et délivrance
    signature_date = fields.Date(string="Date de signature", readonly=True)
    signed_by_id = fields.Many2one('res.users', string="Signé par", readonly=True)
    certificate_file = fields.Binary(string="Fichier du certificat délivré", readonly=True, attachment=True)
    certificate_filename = fields.Char(string="Nom du fichier")
    # Champ pour la signature manuscrite
    signed_by_signature = fields.Binary(string="Signature de l'approbateur", attachment=True)

    # Workflow
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('administrative_control', 'Contrôle Administratif'),
        ('deep_check', 'Verification Aprofondie'),
        ('signed', 'Signature'),
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

    def action_deeper_check_ok(self):
        """Action pour valider la vérification approfondie et passer à l'approbation."""
        self.ensure_one()
        if self.deeper_check_result != 'favorable':
            raise ValidationError("La demande ne peut être validée qu'avec un avis favorable.")

        self.state = 'signed'
        self.deep_check_date = fields.Date.today()
        self.deep_checker_id = self.env.user.id
        self.message_post(
            body="Vérification approfondie validée avec un avis favorable. La signature et délivrance en attente.")

    def action_approve(self):
        """Action finale pour approuver et générer le certificat."""
        self.ensure_one()
        # Mettre à jour l'état et les informations de signature
        self.state = 'approved'
        self.signature_date = fields.Date.today()
        self.signed_by_id = self.env.user.id

        # Le certificat est prêt à être généré.
        # La génération sera déclenchée par le bouton de téléchargement.

        self.message_post(body="Le certificat a été approuvé et signé. Il est prêt pour le téléchargement.")

    def action_print_certificate(self):
        """Action pour imprimer le certificat."""
        # Générer un nom de fichier unique avec un horodatage
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f'Certificat_Sanitaire_{self.name}_{now}.pdf'
        report_action= self.env.ref('patnuc_minepia_certificat_sanitaire.action_report_vet_certificate').report_action(self)
        report_action['name'] = report_name
        return report_action
