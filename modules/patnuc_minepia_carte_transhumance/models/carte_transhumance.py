import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CarteTranshumance(models.Model):
    _name = 'carte.transhumance'
    _description = 'Demande de Carte de Transhumance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Numéro de demande', required=True, copy=False, readonly=True, default='Nouveau')
    initiateur_id = fields.Many2one('res.partner', string='Initiateur', required=True)
    date_demande = fields.Date(string='Date de la demande', default=fields.Date.today(), readonly=True)
    delai_imparti = fields.Integer(string='Délai de traitement (jours)', default=2, readonly=True)

    # Informations sur les acteurs et le trajet
    proprietaire = fields.Char(string='Nom complet du Propriétaire', required=True)
    destination = fields.Char(string='Destination', required=True)

    # Document requis
    document_ids = fields.One2many("carte.document", "request_id", string="Documents")
    required_missing_count = fields.Integer(string="Docs requis manquants", compute="_compute_required_missing",
                                            store=False)

    # Ajout des champs pour la vérification administrative
    administrative_check_date = fields.Datetime(string="Date de vérification administrative", readonly=True)
    administrative_checker_id = fields.Many2one('res.users', string="Agent vérificateur", readonly=True)
    administrative_check_comment = fields.Char(string="Commentaires de l'agent")

    # Champ pour la validation globale
    is_admin_check_ok = fields.Boolean(string="Vérification administrative validée",
                                       compute="_compute_is_admin_check_ok", store=True)


    # Inspection sanitaire
    inspection_agent_id = fields.Many2one('res.users', string='Agent d\'inspection', default=lambda self: self.env.user,  readonly=True)
    inspection_date = fields.Date(string='Date d\'inspection', default=fields.Date.today())
    location = fields.Char(string='Lieu de l\'inspection')

    # Critères d'inspection
    # Nouveaux champs pour l'inspection sur le terrain
    inspection_date = fields.Date(string="Date d'inspection")
    inspector_id = fields.Many2one('res.users', string="Agent d'inspection", readonly=True)
    inspection_report = fields.Text(string="Rapport d'inspection")
    # Rapport détaillé
    inspection_report_doc = fields.Binary(string='Rapport d\'inspection détaillé')

    # Checklist de l'inspection (exemple)
    animal_health_ok = fields.Boolean(string='Santé des animaux vérifiée')
    facilities_clean_ok = fields.Boolean(string='Installations conformes')
    vaccination_status_ok = fields.Boolean(string='Statut vaccinal conforme')
    transport_ok = fields.Boolean(string='Moyen de transport validé')
    # Champ de conclusion
    result = fields.Selection([
        ('favorable', 'Favorable'),
        ('unfavorable', 'Défavorable'),
    ], string='Conclusion de l\'inspection')





    # Signature et délivrance
    signature_date = fields.Date(string="Date de signature", readonly=True)
    signed_by_id = fields.Many2one('res.users', string="Signé par", readonly=True)
    certificate_file = fields.Binary(string="Fichier du certificat délivré", readonly=True, attachment=True)
    certificate_filename = fields.Char(string="Nom du fichier")
    # Champ pour la signature manuscrite
    signed_by_signature = fields.Binary(string="Signature de l'approbateur", attachment=True)


    # Motiif de rejet
    rejection_reason = fields.Text(string="Motif de rejet", readonly=True)




    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('administrative_check', 'Vérification Administrative'),
        ('inspection', 'Inspection Sanitaire'),
        ('signed', 'Signature'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
    ], string='Statut', default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('carte.transhumance') or 'Nouveau'
        return super(CarteTranshumance, self).create(vals)

        # Comptage des documents obligatoires manquants

    def _compute_required_missing(self):
        for rec in self:
            required_types = self.env["carte.document.type"] .search([("required", "=", True)])
            provided_type_ids = set(rec.document_ids.mapped("type_id").ids)
            missing = required_types.filtered(lambda dt: dt.id not in provided_type_ids)
            rec.required_missing_count = len(missing)



    @api.depends("document_ids.is_valid")
    def _compute_is_admin_check_ok(self):
        """Vérifie si tous les documents requis et fournis sont valides."""
        for rec in self:
            # On vérifie que le document est fourni ET qu'il a été validé par l'agent
            rec.is_admin_check_ok = all(doc.is_valid for doc in rec.document_ids.filtered(lambda d: d.provided))
            # On pourrait aussi ajouter une contrainte pour s'assurer que tous les documents requis sont présents
            # et que required_missing_count == 0. C'est déjà géré par la soumission, mais c'est une bonne pratique.

    def action_administrative_check_ok(self):
        """Action pour valider la vérification administrative et passer à l'étape suivante."""
        self.ensure_one()
        # On peut ajouter ici une validation finale avant de changer d'état
        if self.administrative_check_comment is False:
            raise ValidationError("Veuillez ajouter un commentaire avant de valider la vérification administrative.")
        if not self.is_admin_check_ok:
            raise ValidationError("Veuillez valider tous les documents fournis avant de continuer.")

        self.write({
            'state': 'inspection',
            'administrative_check_date': fields.Datetime.now(),
            'administrative_checker_id': self.env.user.id,
        })
        self.message_post(body="Vérification administrative effectuée et validée. La demande passe à l'étape de vérification approfondie.")



    def action_submit(self):
        """Action pour soumettre la demande."""
        if self.required_missing_count > 0:
            required_types = self.env["carte.document.type"].search([("required", "=", True)])
            provided_type_ids = set(self.document_ids.mapped("type_id").ids)
            missing_docs = required_types.filtered(lambda dt: dt.id not in provided_type_ids)
            missing_names = missing_docs.mapped('name')
            raise ValidationError("Impossible de soumettre la demande. Documents manquants :\n• %s" % '\n• '.join(missing_names))
        
        self.state = 'administrative_check'
        self.message_post(body="La demande de carte de transhumance a été soumise et la verification administrative est en attente.")



    def action_complete_inspection(self):
        """Action pour valider la fin de l'inspection sur le terrain."""
        self.ensure_one()
        self.inspector_id=self.env.user.id
        # Valider si tous les champs requis pour l'inspection sont remplis
        if self.result != 'favorable':
            raise ValidationError("La demande ne peut être validée qu'avec un avis favorable.")
        if not self.inspection_date or not self.inspection_report:
            raise ValidationError("Veuillez remplir la date, le rapport et l'agent d'inspection.")

        self.state = 'signed'
        self.message_post(body="L'inspection sur le terrain est terminée ")




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

    def action_print_certificate_ct(self):
        """Action pour imprimer le certificat."""
        # Générer un nom de fichier unique avec un horodatage
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f'Certificat_Sanitaire_{self.name}_{now}.pdf'
        report_action= self.env.ref('patnuc_minepia_carte_transhumance.action_report_carte_transhumance').report_action(self)
        report_action['name'] = report_name
        return report_action



