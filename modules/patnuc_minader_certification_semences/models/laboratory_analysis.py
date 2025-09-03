from odoo import models, fields, api
import base64

class LaboratoryAnalysis(models.Model):
    _name = 'certification.laboratory.analysis'
    _description = 'Analyse Laboratoire'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Référence', compute='_compute_name', store=True)
    request_id = fields.Many2one('certification.request', string='Demande', required=True)
    
    # Laboratoire
    laboratory_id = fields.Many2one('certification.laboratory', string='Laboratoire', 
                                   required=True)
    analysis_date = fields.Date('Date d\'analyse', required=True)
    analyst_id = fields.Many2one('res.users', string='Analyste')
    
    # Tests réalisés
    germination_test = fields.Boolean('Test de germination')
    germination_rate = fields.Float('Taux de germination (%)')
    
    humidity_test = fields.Boolean('Test d\'humidité')
    humidity_rate = fields.Float('Taux d\'humidité (%)')
    
    purity_test = fields.Boolean('Test de pureté')
    purity_rate = fields.Float('Taux de pureté (%)')
    
    varietal_purity = fields.Boolean('Pureté variétale')
    varietal_purity_rate = fields.Float('Taux pureté variétale (%)')
    
    # Résultats
    state = fields.Selection([
        ('pending', 'En attente'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string='État', default='pending', tracking=True)
    
    result = fields.Selection([
        ('compliant', 'Conforme'),
        ('non_compliant', 'Non conforme'),
        ('requires_additional_tests', 'Tests supplémentaires requis')
    ], string='Résultat global')
    
    # Documents
    analysis_report = fields.Binary('Rapport d\'analyse', required=True)
    analysis_report_filename = fields.Char('Nom du rapport d\'analyse')
    technical_opinion = fields.Text('Avis technique')
    
    @api.depends('request_id', 'analysis_date')
    def _compute_name(self):
        for record in self:
            record.name = f"Analyse {record.request_id.name} - {record.analysis_date}"
    
    # def action_complete(self):
    #     self.write({'state': 'completed'})
    #     self.request_id.write({'state': 'technical_review'})
    
    def action_validate(self):
        # ... ta logique de validation ...
        if self.request_id:
            self.request_id.write({'state': 'technical_review'})

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
            'analysis_report': 'analysis_report_filename',
        }
        
        for binary_field, filename_field in binary_fields.items():
            if getattr(self, binary_field):
                self._update_filename_from_attachment(binary_field, filename_field)
        
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def create(self, vals):
        # Capturer les noms de fichiers depuis le contexte lors de la création
        self._capture_filenames(vals)
        return super(LaboratoryAnalysis, self).create(vals)
    
    def write(self, vals):
        # Capturer les noms de fichiers depuis le contexte lors de la modification
        self._capture_filenames(vals)
        result = super(LaboratoryAnalysis, self).write(vals)
        
        # Après l'écriture, essayer de récupérer les noms de fichiers depuis les attachments
        binary_fields = {
            'analysis_report': 'analysis_report_filename',
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
            'analysis_report': 'analysis_report_filename',
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
                            'analysis_report': 'rapport_analyse_laboratoire.pdf',
                        }
                        filename = default_names.get(binary_field, f'{binary_field}.pdf')
                    
                    vals[filename_field] = filename