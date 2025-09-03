from odoo import models, fields, api
from odoo.exceptions import UserError 
import logging
import base64
_logger = logging.getLogger(__name__)

class CertificationRequest(models.Model):
    _name = 'certification.request'
    _description = 'Demande de Certification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    name = fields.Char('Référence', required=True, copy=False, readonly=True,
                      default=lambda self: self.env['ir.sequence'].next_by_code('certification.request'))
    
    # Informations générales
    operator_id = fields.Many2one('certification.operator', string='Opérateur', 
                                 required=True, tracking=True)
    production_site_id = fields.Many2one('certification.production.site', 
                                        string='Site de production', required=True)
    
    # Détails de la demande
    seed_variety = fields.Char('Variété de semence', required=True)
    seed_origin = fields.Text('Origine des semences')
    cultivation_plan = fields.Text('Plan de culture / Itinéraire technique')
    production_area = fields.Float('Superficie de production (ha)')
    
    # Documents requis
    request_form = fields.Binary('Formulaire de demande', required=True)
    request_form_filename = fields.Char('Nom du formulaire')
    professional_card = fields.Binary('Carte professionnelle', required=True)
    professional_card_filename = fields.Char('Nom de la carte professionnelle')
    cultivation_plan_doc = fields.Binary('Plan de culture', required=True)
    cultivation_plan_doc_filename = fields.Char('Nom du plan de culture')
    soil_analysis = fields.Binary('Bulletin d\'analyse du sol', required=True)
    soil_analysis_filename = fields.Char('Nom du bulletin d\'analyse')
    seed_origin_certificate = fields.Binary('Attestation d\'origine des semences', required=True)
    seed_origin_certificate_filename = fields.Char('Nom de l\'attestation')
    cni_copy = fields.Binary('Copie CNI', required=True)
    cni_copy_filename = fields.Char('Nom de la copie CNI')
    location_proof = fields.Binary('Preuve de localisation', required=True)
    location_proof_filename = fields.Char('Nom de la preuve de localisation')
    
    
    # Workflow et suivi
    state = fields.Selection([
        ('draft', 'Déposée'),
        ('submitted', 'Soumise'),
        ('received', 'Reçue'),
        ('field_control', 'Contrôle terrain'),
        ('laboratory_analysis', 'Analyses laboratoire'),
        ('technical_review', 'Examen technique'),
        ('approved', 'Approuvée'),
        ('certificate_issued', 'Certificat délivré'),
        ('rejected', 'Rejetée'),
        ('cancelled', 'Annulée')
    ], string='État', default='draft', tracking=True)
    
    # Dates importantes
    submission_date = fields.Datetime('Date de soumission', tracking=True)
    reception_date = fields.Datetime('Date de réception', tracking=True)
    expected_completion_date = fields.Date('Date prévue de finalisation')
    completion_date = fields.Datetime('Date de finalisation')
    
    
    # Assignations
    regional_officer_id = fields.Many2one('res.users', string='Agent régional assigné')
    technical_reviewer_id = fields.Many2one('res.users', string='Réviseur technique')
    
    # Relations
    field_control_ids = fields.One2many('certification.field.control', 'request_id',
                                       string='Contrôles terrain')
    laboratory_analysis_ids = fields.One2many('certification.laboratory.analysis', 'request_id',
                                            string='Analyses laboratoire')
    technical_exam_ids = fields.One2many('certification.technical.review', 'request_id', string='Technical exam')
    certificate_id = fields.Many2one('certification.certificate', string='Certificat')
    
    # Commentaires et observations
    notes = fields.Text('Notes internes')
    rejection_reason = fields.Text('Motif de rejet')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('certification.request') or 'New'
        return super(CertificationRequest, self).create(vals)
    
    def action_submit(self):
        self.write({
            'state': 'submitted',
            'submission_date': fields.Datetime.now()
        })
        self._create_activity('Nouvelle demande soumise')
        
    def ret_submit(self):
        self.write({'state': 'draft'})
    
    def action_receive(self):
        self.write({
            'state': 'received',
            'reception_date': fields.Datetime.now()
        })
        self._create_activity('Demande reçue - Attente contrôle terrain')
    
    def ret_receive(self):
        self.write({'state': 'submitted'})
    
    def action_start_field_control(self):
        self.ensure_one()
        self.write({'state': 'field_control'})
        if not self.regional_officer_id:
            raise UserError("Veuillez renseigner l'agent régional assigné avant de lancer le contrôle terrain.")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nouveau Contrôle Terrain',
            'res_model': 'certification.field.control',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {
                'default_request_id': self.id,
            },
            'target': 'new',
        }
        
    def ret_field_control(self):
        self.write({'state': 'received'})
    
    def action_start_laboratory_analysis(self):
        self.ensure_one()
        self.write({'state': 'laboratory_analysis'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nouvelle Analyse Laboratoire',
            'res_model': 'certification.laboratory.analysis',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {
                'default_request_id': self.id,
            },
            'target': 'new',  # Ouvre en pop-up
        }
        
    def ret_laboratory_analysis(self):
        self.write({'state': 'field_control'})
    
    def action_start_technical_review(self):
        self.ensure_one()
        self.write({'state': 'technical_review'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nouvel Examen Technique',
            'res_model': 'certification.technical.review',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {
                'default_request_id': self.id,
            },
            'target': 'new',
        }
        
    def ret_technical_review(self):
        self.write({'state': 'laboratory_analysis'})
    
    def action_approve(self):
        self.write({
            'state': 'approved',
            'completion_date': fields.Datetime.now()
        })
        self._generate_certificate()
    
    def action_get_certificat(self):
        """
        Fonction permettant d'imprimer le certificat de semence
        """
        return self.env['ir.actions.report']._get_report_from_name(
            'patnuc_minader_certification_semences.report_certificate_document'
            ).report_action(self)
    
    def action_reject(self):
        self.write({
            'state': 'rejected',
            'completion_date': fields.Datetime.now()
        })
    
    def _update_filename_from_attachment(self, binary_field, filename_field):
        """Méthode utilitaire pour récupérer le nom de fichier depuis les attachments"""
        if self.id:
            # Rechercher l'attachment le plus récent pour ce champ
            attachment = self.env['ir.attachment'].search([
                ('res_model', '=', self._name),
                ('res_id', '=', self.id),
                ('res_field', '=', binary_field)
            ], order='id desc', limit=1)
            
            if attachment and attachment.name:
                # Mettre à jour le nom de fichier directement sans déclencher write à nouveau
                self.env.cr.execute(
                    f"UPDATE {self._table} SET {filename_field} = %s WHERE id = %s",
                    (attachment.name, self.id)
                )
                # Invalider le cache pour ce champ
                self.invalidate_cache([filename_field])
                return attachment.name
        return None
    
    def action_update_filenames(self):
        """Action pour forcer la mise à jour des noms de fichiers"""
        binary_fields = {
            'request_form': 'request_form_filename',
            'professional_card': 'professional_card_filename',
            'cultivation_plan_doc': 'cultivation_plan_doc_filename',
            'soil_analysis': 'soil_analysis_filename',
            'seed_origin_certificate': 'seed_origin_certificate_filename',
            'cni_copy': 'cni_copy_filename',
            'location_proof': 'location_proof_filename',
        }
        
        for binary_field, filename_field in binary_fields.items():
            if getattr(self, binary_field):
                self._update_filename_from_attachment(binary_field, filename_field)
        
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def create(self, vals):
        # Capturer les noms de fichiers depuis le contexte lors de la création
        self._capture_filenames(vals)
        return super(CertificationRequest, self).create(vals)
    
    def write(self, vals):
        # Capturer les noms de fichiers depuis le contexte lors de la modification
        self._capture_filenames(vals)
        result = super(CertificationRequest, self).write(vals)
        
        # Après l'écriture, essayer de récupérer les noms de fichiers depuis les attachments
        binary_fields = {
            'request_form': 'request_form_filename',
            'professional_card': 'professional_card_filename',
            'cultivation_plan_doc': 'cultivation_plan_doc_filename',
            'soil_analysis': 'soil_analysis_filename',
            'seed_origin_certificate': 'seed_origin_certificate_filename',
            'cni_copy': 'cni_copy_filename',
            'location_proof': 'location_proof_filename',
        }
        
        for binary_field, filename_field in binary_fields.items():
            if binary_field in vals and vals[binary_field]:
                # Si un fichier a été uploadé, essayer de récupérer son nom
                if not vals.get(filename_field):
                    self._update_filename_from_attachment(binary_field, filename_field)
        
        return result
    
    def _capture_filenames(self, vals):
        """Méthode pour capturer automatiquement les noms de fichiers"""
        # Mapping des champs Binary vers leurs champs filename correspondants
        binary_fields = {
            'request_form': 'request_form_filename',
            'professional_card': 'professional_card_filename',
            'cultivation_plan_doc': 'cultivation_plan_doc_filename',
            'soil_analysis': 'soil_analysis_filename',
            'seed_origin_certificate': 'seed_origin_certificate_filename',
            'cni_copy': 'cni_copy_filename',
            'location_proof': 'location_proof_filename',
        }
        
        # Vérifier chaque champ Binary pour capturer le nom de fichier
        for binary_field, filename_field in binary_fields.items():
            # Si un fichier est uploadé
            if binary_field in vals and vals[binary_field]:
                # Vérifier si le nom de fichier n'est pas déjà fourni
                if filename_field not in vals or not vals[filename_field]:
                    # Essayer plusieurs méthodes pour récupérer le nom
                    filename = None
                    
                    # 1. Depuis le contexte direct
                    filename = self.env.context.get(f'{binary_field}_filename')
                    
                    # 2. Depuis le contexte avec différentes clés possibles
                    if not filename:
                        for key in [f'default_{filename_field}', filename_field, f'{binary_field}_name']:
                            filename = self.env.context.get(key)
                            if filename:
                                break
                    
                    # 3. Depuis les paramètres de la requête HTTP si disponible
                    if not filename and hasattr(self.env, 'request') and self.env.request:
                        request_files = getattr(self.env.request, 'httprequest', None)
                        if request_files and hasattr(request_files, 'files'):
                            for file_key, file_obj in request_files.files.items():
                                if binary_field in file_key and hasattr(file_obj, 'filename'):
                                    filename = file_obj.filename
                                    break
                    
                    # 4. Si toujours pas de nom, utiliser un nom par défaut descriptif
                    if not filename:
                        default_names = {
                            'request_form': 'formulaire_demande.pdf',
                            'professional_card': 'carte_professionnelle.pdf',
                            'cultivation_plan_doc': 'plan_culture.pdf',
                            'soil_analysis': 'analyse_sol.pdf',
                            'seed_origin_certificate': 'attestation_origine.pdf',
                            'cni_copy': 'copie_cni.pdf',
                            'location_proof': 'preuve_localisation.pdf',
                        }
                        filename = default_names.get(binary_field, f'{binary_field}.pdf')
                    
                    vals[filename_field] = filename

    def _create_activity(self, summary):
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=summary,
            user_id=self.regional_officer_id.id or self.env.user.id
        )
        
    
    def _create_field_control_record(self):
        self.env['certification.field.control'].create({
            'request_id': self.id,
            'scheduled_date': fields.Date.today(),
            'inspector_id': self.regional_officer_id.id
        })
    
    def _create_laboratory_analysis_record(self):
        self.env['certification.laboratory.analysis'].create({
            'request_id': self.id,
            'analysis_date': fields.Date.today(),
            'laboratory_id': self.env.ref('patnuc_minader_certification_semences.lnad_lab').id
        })
        
    
    def _generate_certificate(self):
        certificate = self.env['certification.certificate'].create({
            'request_id': self.id,
            'operator_id': self.operator_id.id,
            'issue_date': fields.Date.today(),
            'name': self.env['ir.sequence'].next_by_code('certification.certificate')
        })
        self.certificate_id = certificate.id
        self.state = 'certificate_issued'