from odoo import models, fields, api
import base64

class SeedOperator(models.Model):
    _name = 'certification.operator'
    _description = 'Opérateur Semencier'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Nom/Raison sociale', required=True, tracking=True)
    operator_type = fields.Selection([
        ('individual', 'Personne physique'),
        ('cooperative', 'Coopérative'),
        ('company', 'Entreprise'),
        ('approved_producer', 'Producteur agréé')
    ], string='Type d\'opérateur', required=True, tracking=True)
    
    # Informations d'identification
    professional_card = fields.Char('Carte professionnelle')
    technical_approval = fields.Char('Agrément technique')
    cni_number = fields.Char('Numéro CNI')
    
    # Coordonnées
    phone = fields.Char('Téléphone')
    email = fields.Char('Email')
    address = fields.Text('Adresse')
    
    # Localisation des sites
    production_sites = fields.One2many('certification.production.site', 'operator_id', 
                                     string='Sites de production')
    
    # Statut
    active = fields.Boolean('Actif', default=True)
    state = fields.Selection([
        ('draft', 'Initié'),
        ('approved', 'Agréé'),
        ('suspended', 'Suspendu'),
        ('cancelled', 'Annulé')
    ], string='Statut', default='draft', tracking=True)
    
    # Statistiques
    certification_count = fields.Integer('Nombre de certifications', 
                                       compute='_compute_certification_count')
    
    @api.depends('certification_requests')
    def _compute_certification_count(self):
        for operator in self:
            operator.certification_count = len(operator.certification_requests)
    
    certification_requests = fields.One2many('certification.request', 'operator_id',
                                           string='Demandes de certification')

class ProductionSite(models.Model):
    _name = 'certification.production.site'
    _description = 'Site de production'
    
    name = fields.Char('Nom du site', required=True)
    operator_id = fields.Many2one('certification.operator', string='Opérateur')
    location = fields.Text('Localisation')
    surface_area = fields.Float('Superficie (ha)')
    coordinates = fields.Char('Coordonnées GPS')
    
    # Documents
    land_title = fields.Binary('Titre foncier', required=True)
    land_title_filename = fields.Char('Nom du titre foncier')
    land_lease = fields.Binary('Bail', required=True)
    land_lease_filename = fields.Char('Nom du bail')
    location_proof = fields.Binary('Preuve de localisation', required=True)
    location_proof_filename = fields.Char('Nom de la preuve de localisation')

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
            'land_title': 'land_title_filename',
            'land_lease': 'land_lease_filename',
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
        return super(ProductionSite, self).create(vals)
    
    def write(self, vals):
        # Capturer les noms de fichiers depuis le contexte lors de la modification
        self._capture_filenames(vals)
        result = super(ProductionSite, self).write(vals)
        
        # Après l'écriture, essayer de récupérer les noms de fichiers depuis les attachments
        binary_fields = {
            'land_title': 'land_title_filename',
            'land_lease': 'land_lease_filename',
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
            'land_title': 'land_title_filename',
            'land_lease': 'land_lease_filename',
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
                            'land_title': 'titre_foncier.pdf',
                            'land_lease': 'bail_terrain.pdf',
                            'location_proof': 'preuve_localisation.pdf',
                        }
                        filename = default_names.get(binary_field, f'{binary_field}.pdf')
                    
                    vals[filename_field] = filename