from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class CertificationRequest(models.Model):
    _name = 'phytosanitary.certification.request'
    _description = 'Demande de Certification Appareils Phytosanitaires'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Champs de base
    name = fields.Char('Numéro de demande', required=True, copy=False, 
                       default=lambda self: _('Nouveau'))
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Déposée'),
        ('admin_check', 'Vérification Administrative'),
        ('technical_review', 'Instruction Technique'),
        ('technical_eval', 'Évaluation Technique'),
        ('technical_report', 'Rapport Technique'),
        ('final_decision', 'Décision Finale'),
        ('certificate_signed', 'Certificat Signé'),
        ('notified', 'Notifiée'),
        ('rejected', 'Rejetée'),
        ('cancelled', 'Annulée')
    ], string='État', default='draft', tracking=True)

    # Informations demandeur
    partner_id = fields.Many2one('res.partner', string='Demandeur', required=True)
    company_type = fields.Selection(related='partner_id.company_type')
   
    
    # Informations appareil
    equipment_id = fields.Many2one('phytosanitary.equipment', string='Appareil', required=True)
    equipment_type = fields.Selection([
        ('Pulvérisateurs à dos à pression entretenue', 'Pulvérisateurs à dos à pression entretenue'),
        ('Pulvérisateurs à dos à moteur', 'Pulvérisateurs à dos à moteur'),
        ('Pulvérisateurs à dos à pression préalable', 'Pulvérisateurs à dos à pression préalable'),
        ('Pulvérisateurs centrifuges', 'Pulvérisateurs centrifuges'),
        ('Appareils de nébulisation thermique','Appareils de nébulisation thermique'),
        ('Poudreuses', 'Poudreuses'), 
        ('Applicateurs de granules', 'Applicateurs de granules'),
        ('Nébulisateurs à froid', 'Nébulisateurs à froid'),
        ('Appareils tractés', 'Appareils tractés')
        
    ], string='Type d\'appareil', required=True)
    
    # Dates et délais
    submission_date = fields.Datetime('Date de soumission', tracking=True)
    expected_completion_date = fields.Date('Date prévue de fin', compute='_compute_expected_date')
    actual_completion_date = fields.Date('Date réelle de fin')
    
    # Documents
    document_ids = fields.One2many('phytosanitary.document', 'request_id', string='Documents')
    required_documents_complete = fields.Boolean('Documents requis complets', 
                                                 compute='_compute_documents_status')
    
    # Évaluations
    admin_evaluation_id = fields.Many2one('phytosanitary.admin.evaluation', 
                                          string='Évaluation Administrative')
    technical_evaluation_id = fields.Many2one('phytosanitary.technical.evaluation', 
                                              string='Évaluation Technique')
    
    # Résultats
    certificate_number = fields.Char('Numéro de certificat')
    certificate_validity_start = fields.Date('Début validité certificat')
    certificate_validity_end = fields.Date('Fin validité certificat')
    rejection_reason = fields.Text('Motif de rejet')
    
    # Frais
    fees_amount = fields.Float('Montant des frais')
    fees_paid = fields.Boolean('Frais payés', default=False)
    payment_receipt = fields.Binary('Reçu de paiement')
    
    # Acteurs responsables
    responsible_agent_id = fields.Many2one('res.users', string='Agent responsable')
    dripa_validator_id = fields.Many2one('res.users', string='Validateur DRIPA')
    minister_signer_id = fields.Many2one('res.users', string='Signataire Ministre')

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('phytosanitary.certification.request')
        return super().create(vals)

    @api.depends('submission_date')
    def _compute_expected_date(self):
        for record in self:
            if record.submission_date:
                # Calcul basé sur les délais de la procédure (environ 20 jours ouvrés)
                record.expected_completion_date = record.submission_date.date() + timedelta(days=30)
            else:
                record.expected_completion_date = False

    @api.depends('document_ids', 'document_ids.document_type', 'document_ids.is_provided')
    def _compute_documents_status(self):
        required_docs = [
            'demande_timbrée au tarif en vigueur',
            'manuel d’utilisation ',
            'rapports des tests de contrôle des spécifications techniques ',
            'rapport des tests de performance en champ',
            'engagement à assurer le service après vente ', 
            'justificatif_paiement',  'piece_identite'
        ]
        
        for record in self:
            provided_docs = record.document_ids.filtered('is_provided').mapped('document_type')
            record.required_documents_complete = all(doc in provided_docs for doc in required_docs)

    def action_submit(self):
        """Étape 1: Dépôt de la demande"""
        if not self.required_documents_complete:
            raise ValidationError("Tous les documents requis doivent être fournis avant la soumission.")
        
        self.write({
            'state': 'submitted',
            'submission_date': fields.Datetime.now()
        })
        self._send_notification('submitted')

    def action_admin_check(self):
        """Étape 2: Vérification administrative"""
        self.write({'state': 'admin_check'})
        self._create_admin_evaluation()
        self._send_notification('admin_check')

    def action_technical_review(self):
        """Étape 3: Instruction technique"""
        if not self.admin_evaluation_id.is_compliant:
            raise ValidationError("La vérification administrative doit être favorable.")
        
        self.write({'state': 'technical_review'})
        self._send_notification('technical_review')

    def action_technical_evaluation(self):
        """Étape 4: Évaluation technique"""
        self.write({'state': 'technical_eval'})
        self._create_technical_evaluation()
        self._send_notification('technical_eval')

    def action_technical_report(self):
        """Étape 5: Rapport technique"""
        if not self.technical_evaluation_id.recommendation == 'favorable':
            raise ValidationError("L'évaluation technique doit être favorable.")
        
        self.write({'state': 'technical_report'})
        self._generate_technical_report()
        self._send_notification('technical_report')

    def action_final_decision(self):
        """Étape 6: Décision finale"""
        self.write({'state': 'final_decision'})
        self._send_notification('final_decision')

    def action_sign_certificate(self):
        """Étape 7: Signature du certificat"""
        self.write({
            'state': 'certificate_signed',
            'certificate_number': self._generate_certificate_number(),
            'certificate_validity_start': fields.Date.today(),
            'certificate_validity_end': fields.Date.today() + timedelta(days=1825)  # 5 ans
        })
        self._generate_certificate()
        self._send_notification('certificate_signed')

    def action_notify_decision(self):
        """Étape 8: Notification de la décision"""
        self.write({
            'state': 'notified',
            'actual_completion_date': fields.Date.today()
        })
        self._send_final_notification()

    def action_reject(self):
        """Rejeter la demande"""
        return {
            'name': 'Motif de rejet',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'phytosanitary.rejection.wizard',
            'target': 'new',
            'context': {'default_request_id': self.id}
        }

    def _create_admin_evaluation(self):
        """Créer l'évaluation administrative"""
        eval_obj = self.env['phytosanitary.admin.evaluation']
        evaluation = eval_obj.create({
            'request_id': self.id,
            'evaluator_id': self.env.user.id,
            'evaluation_date': fields.Date.today()
        })
        self.admin_evaluation_id = evaluation.id

    def _create_technical_evaluation(self):
        """Créer l'évaluation technique"""
        eval_obj = self.env['phytosanitary.technical.evaluation']
        evaluation = eval_obj.create({
            'request_id': self.id,
            'equipment_id': self.equipment_id.id,
            'evaluator_id': self.env.user.id,
            'evaluation_date': fields.Date.today()
        })
        self.technical_evaluation_id = evaluation.id

    def _generate_certificate_number(self):
        """Générer le numéro de certificat"""
        year = fields.Date.today().year
        sequence = self.env['ir.sequence'].next_by_code('phytosanitary.certificate')
        return f"CERT-PHYTO-{year}-{sequence}"

    def _generate_technical_report(self):
        """Générer le rapport technique"""
        # Logique pour générer le rapport technique
        pass

    def _generate_certificate(self):
        """Générer le certificat officiel"""
        # Logique pour générer le certificat PDF
        pass

    def _send_notification(self, stage):
        """Envoyer les notifications selon l'étape"""
        template_mapping = {
            'submitted': 'phytosanitary_certification_submitted',
            'admin_check': 'phytosanitary_certification_admin_check',
            'technical_review': 'phytosanitary_certification_technical_review',
            'technical_eval': 'phytosanitary_certification_technical_eval',
            'technical_report': 'phytosanitary_certification_technical_report',
            'final_decision': 'phytosanitary_certification_final_decision',
            'certificate_signed': 'phytosanitary_certification_signed',
        }
        
        template_name = template_mapping.get(stage)
        if template_name:
            template = self.env.ref(f'phytosanitary_certification.{template_name}', raise_if_not_found=False)
            if template:
                template.send_mail(self.id, force_send=True)

    def _send_final_notification(self):
        """Notification finale avec certificat"""
        template = self.env.ref('patnuc_minader_certification_appareils_phytosanitaires.phytosanitary_certification_final_notification')
        template.send_mail(self.id, force_send=True)
        
    def action_view_documents(self):
        """Afficher les documents de la demande"""
        return {
            'name': 'Documents',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'phytosanitary.document',
            'domain': [('request_id', '=', self.id)],
            'context': {'default_request_id': self.id}
        }