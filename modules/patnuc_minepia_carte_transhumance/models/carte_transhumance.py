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

    # ANCIENNE APPROCHE - Document requis avec modèle séparé (commenté temporairement)
    # document_ids = fields.One2many("carte.document", "request_id", string="Documents")
    # required_missing_count = fields.Integer(string="Docs requis manquants", compute="_compute_required_missing", store=False)
    
    # NOUVELLE APPROCHE - Champs directs pour les documents
    demande_timbree = fields.Binary(string="Demande timbrée au tarif en vigueur", attachment=True, required=True)
    photocopie_cni_proprietaire = fields.Binary(string="Photocopie CNI Propriétaire", attachment=True, required=True)
    photocopie_cni_berger = fields.Binary(string="Photocopie CNI Berger", attachment=True, required=True)
    certificat_sanitaire = fields.Binary(string="Certificat Sanitaire", attachment=True, required=True)
    laisser_passer_sanitaire = fields.Binary(string="Laisser Passer Sanitaire", attachment=True, required=True)
    recu_paiement_taxe = fields.Binary(string="Reçu de paiement de la taxe d'inspection sanitaire", attachment=True, required=True)

    # Ajout des champs pour la vérification administrative
    administrative_check_date = fields.Datetime(string="Date de vérification administrative", readonly=True)
    administrative_checker_id = fields.Many2one('res.users', string="Agent vérificateur", readonly=True)
    administrative_check_comment = fields.Char(string="Commentaires de l'agent")

    # ANCIENNE APPROCHE - Validation globale basée sur les documents (commenté temporairement)
    # is_admin_check_ok = fields.Boolean(string="Vérification administrative validée",
    #                                    compute="_compute_is_admin_check_ok", store=True)
    
    # NOUVELLE APPROCHE - Validation des documents individuels
    demande_timbree_ok = fields.Boolean(string="Demande timbrée validée")
    demande_timbree_filename = fields.Char(string="Nom du fichier de la demande timbrée")
    photocopie_cni_proprietaire_ok = fields.Boolean(string="Photocopie CNI Propriétaire validée")
    photocopie_cni_proprietaire_filename = fields.Char(string="Nom du fichier de la photocopie CNI Propriétaire")
    photocopie_cni_berger_ok = fields.Boolean(string="Photocopie CNI Berger validée")
    photocopie_cni_berger_filename = fields.Char(string="Nom du fichier de la photocopie CNI Berger")
    certificat_sanitaire_ok = fields.Boolean(string="Certificat Sanitaire validé")
    certificat_sanitaire_filename = fields.Char(string="Nom du fichier du certificat sanitaire")
    laisser_passer_sanitaire_ok = fields.Boolean(string="Laisser Passer Sanitaire validé")
    laisser_passer_sanitaire_filename = fields.Char(string="Nom du fichier du laisser passer sanitaire")
    recu_paiement_taxe_ok = fields.Boolean(string="Reçu de paiement validé")
    recu_paiement_taxe_filename = fields.Char(string="Nom du fichier du reçu de paiement")
    
    # Champ calculé pour la validation globale
    is_admin_check_ok = fields.Boolean(string="Vérification administrative validée",
                                       compute="_compute_is_admin_check_ok_new", store=True)


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
        ('draft', 'Depot dossier'),
        ('admin_check', 'Contrôle Administratif'),
        ('deep_check', 'Inspection Sanitaire'),
        ('approved', 'Signature et delivrance'),
        ('rejected', 'Rejetée'),
    ], string='Statut', default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('carte.transhumance') or 'Nouveau'
        return super(CarteTranshumance, self).create(vals)

    # ANCIENNE APPROCHE - Comptage des documents obligatoires manquants (commenté temporairement)
    # def _compute_required_missing(self):
    #     for rec in self:
    #         required_types = self.env["carte.document.type"] .search([("required", "=", True)])
    #         provided_type_ids = set(rec.document_ids.mapped("type_id").ids)
    #         missing = required_types.filtered(lambda dt: dt.id not in provided_type_ids)
    #         rec.required_missing_count = len(missing)

    # @api.depends("document_ids.is_valid")
    # def _compute_is_admin_check_ok(self):
    #     """Vérifie si tous les documents requis et fournis sont valides."""
    #     for rec in self:
    #         # On vérifie que le document est fourni ET qu'il a été validé par l'agent
    #         rec.is_admin_check_ok = all(doc.is_valid for doc in rec.document_ids.filtered(lambda d: d.provided))
    
    # NOUVELLE APPROCHE - Validation basée sur les champs individuels
    @api.depends("demande_timbree_ok", "photocopie_cni_proprietaire_ok", "photocopie_cni_berger_ok", 
                 "certificat_sanitaire_ok", "laisser_passer_sanitaire_ok", "recu_paiement_taxe_ok")
    def _compute_is_admin_check_ok_new(self):
        """Vérifie si tous les documents requis sont validés."""
        for rec in self:
            rec.is_admin_check_ok = all([
                rec.demande_timbree_ok,
                rec.photocopie_cni_proprietaire_ok,
                rec.photocopie_cni_berger_ok,
                rec.certificat_sanitaire_ok,
                rec.laisser_passer_sanitaire_ok,
                rec.recu_paiement_taxe_ok
            ])

    def action_administrative_check_ok(self):
        """Action pour valider la vérification administrative et passer à l'étape suivante."""
        self.ensure_one()
        # On peut ajouter ici une validation finale avant de changer d'état
        if self.administrative_check_comment is False:
            raise ValidationError("Veuillez ajouter un commentaire avant de valider la vérification administrative.")
        if not self.is_admin_check_ok:
            raise ValidationError("Veuillez valider tous les documents fournis avant de continuer.")

        self.write({
            'state': 'deep_check',
            'administrative_check_date': fields.Datetime.now(),
            'administrative_checker_id': self.env.user.id,
        })
        self.message_post(body="Vérification administrative effectuée et validée. La demande passe à l'étape de vérification approfondie.")



    def action_submit(self):
        """Action pour soumettre la demande."""
        # ANCIENNE APPROCHE - Vérification avec modèle document (commenté temporairement)
        # if self.required_missing_count > 0:
        #     required_types = self.env["carte.document.type"].search([("required", "=", True)])
        #     provided_type_ids = set(self.document_ids.mapped("type_id").ids)
        #     missing_docs = required_types.filtered(lambda dt: dt.id not in provided_type_ids)
        #     missing_names = missing_docs.mapped('name')
        #     raise ValidationError("Impossible de soumettre la demande. Documents manquants :\n• %s" % '\n• '.join(missing_names))
        
        # NOUVELLE APPROCHE - Vérification des champs directs
        missing_docs = []
        if not self.demande_timbree:
            missing_docs.append("Demande timbrée au tarif en vigueur")
        if not self.photocopie_cni_proprietaire:
            missing_docs.append("Photocopie CNI Propriétaire")
        if not self.photocopie_cni_berger:
            missing_docs.append("Photocopie CNI Berger")
        if not self.certificat_sanitaire:
            missing_docs.append("Certificat Sanitaire")
        if not self.laisser_passer_sanitaire:
            missing_docs.append("Laisser Passer Sanitaire")
        if not self.recu_paiement_taxe:
            missing_docs.append("Reçu de paiement de la taxe d'inspection sanitaire")
            
        if missing_docs:
            raise ValidationError("Impossible de soumettre la demande. Documents manquants :\n• %s" % '\n• '.join(missing_docs))
        
        self.state = 'admin_check'
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

        self.state = 'approved'
        self.message_post(body="L'inspection sur le terrain est terminée ")






    def action_print_certificate_ct(self):
        """Action pour imprimer le certificat."""
        self.ensure_one()
        # Mettre à jour l'état et les informations de signature
        self.state = 'approved'
        self.signature_date = fields.Date.today()
        self.signed_by_id = self.env.user.id
        # Générer un nom de fichier unique avec un horodatage
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f'Certificat_Sanitaire_{self.name}_{now}.pdf'
        report_action= self.env.ref('patnuc_minepia_carte_transhumance.action_report_carte_transhumance').report_action(self)
        report_action['name'] = report_name
        return report_action

    def action_back_to_previous_state(self):
        """Retourner à l'état précédent"""
        state_transitions = {
            'admin_check': 'draft',
            'deep_check': 'admin_check',
            'approved': 'deep_analysis',
        }

        if self.state in state_transitions:
            previous_state = state_transitions[self.state]
            self.state = previous_state
            self.message_post(
                body=f"Retour à l'état précédent : {dict(self._fields['state'].selection)[previous_state]}")
        else:
            raise ValidationError("Impossible de retourner à l'état précédent depuis cet état.")



