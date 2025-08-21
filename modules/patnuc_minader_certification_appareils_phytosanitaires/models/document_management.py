# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class PhytosanitaryDocument(models.Model):
    _name = 'phytosanitary.document'
    _description = 'Documents de Certification Phytosanitaire'

    request_id = fields.Many2one('phytosanitary.certification.request', 
                                 string='Demande', required=True)
    
    document_type = fields.Selection([
        # Documents requis
        #('demande_officielle', 'Lettre de demande officielle'),
        #('formulaire_homologation', 'Formulaire de demande d\'homologation'),
        #('fiche_technique', 'Fiche technique du produit/appareil'),
        #('certificat_analyse', 'Certificat d\'analyse de laboratoire agréé'),
        #('fiche_securite', 'Fiche de sécurité (FDS)'),
        #('attestation_homologation_etranger', 'Attestation d\'homologation à l\'étranger'),
        #('attestation_conformite', 'Attestation de conformité nationale'),
        #('justificatif_paiement', 'Justificatif de paiement des frais'),
        #('agrement_importation', 'Copie de l\'agrément d\'importation'),
        ('piece_identite', 'Photocopie pièce d\'identité'),
        ('Demande timbrée au tarif en vigeur', ''),
        ('Manuel utilisation', 'Manuel d\'utilisation'),
        ('Rapport des test de contôle des specifications techniques', 'Rapport des tests de contrôle des spécifications techniques'),
        ('Rapport des tests de performance en champ', 'Rapport des tests de performance en champ'),
        ('Engagement a assurer le service après-vente', 'Engagement à assurer le service après-vente'),
        ('Recepicissé de dépôt des échantillons', 'Reçu de dépôt des échantillons'),

        
        # Documents générés
        #('fiche_controle_technique', 'Fiche de contrôle technique'),
        #('rapport_expertise', 'Rapport d\'expertise scientifique'),
        #('note_synthese', 'Note de synthèse'),
        #('projet_certificat', 'Projet de certificat d\'homologation'),
        
        # Document final
        #('certificat_homologation', 'Certificat d\'homologation'),
        #('notification_decision', 'Notification de la décision')
    ], string='Type de document', required=True)
    
    name = fields.Char('Nom du document', required=True)
    file_data = fields.Binary('Fichier', required=True)
    file_name = fields.Char('Nom du fichier')
    
    is_required = fields.Boolean('Obligatoire', default=False)
    is_provided = fields.Boolean('Fourni', default=False)
    is_valid = fields.Boolean('Valide', default=False)
    
    upload_date = fields.Datetime('Date de téléchargement', default=fields.Datetime.now)
    uploaded_by = fields.Many2one('res.users', string='Téléchargé par', 
                                  default=lambda self: self.env.user)
    
    validation_date = fields.Datetime('Date de validation')
    validated_by = fields.Many2one('res.users', string='Validé par')
    validation_comments = fields.Text('Commentaires de validation')
    
    @api.model
    def create(self, vals):
        if vals.get('document_type') in [
            'demande_officielle', 'formulaire_homologation', 'fiche_technique',
            'certificat_analyse', 'fiche_securite', 'attestation_conformite',
            'justificatif_paiement', 'agrement_importation', 'piece_identite'
        ]:
            vals['is_required'] = True
        
        if vals.get('file_data'):
            vals['is_provided'] = True
            
        return super().create(vals)