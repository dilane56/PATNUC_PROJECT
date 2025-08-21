# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class PhytosanitaryEquipment(models.Model):
    _name = 'phytosanitary.equipment'
    _description = 'Appareil de Traitement Phytosanitaire'

    name = fields.Char('Nom de l\'appareil', required=True)
    brand = fields.Char('Marque')
    model = fields.Char('Modèle')
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
    ], string='Type', required=True)
    
    # Spécifications techniques
    capacity = fields.Float('Capacité (L)')
    pressure_max = fields.Float('Pression maximale (bar)')
    flow_rate = fields.Float('Débit (L/min)')
    power_source = fields.Selection([
        ('manual', 'Manuel'),
        ('electric', 'Électrique'),
        ('gasoline', 'Essence'),
        ('battery', 'Batterie')
    ], string='Source d\'énergie')
    
    # Documents techniques
    technical_sheet = fields.Binary('Fiche technique')
    user_manual = fields.Binary('Manuel d\'utilisation')
    #safety_datasheet = fields.Binary('Fiche de sécurité')
    
    # Informations fabricant
    manufacturer_id = fields.Many2one('res.partner', string='Fabricant')
    country_origin = fields.Many2one('res.country', string='Pays d\'origine')
    manufacturing_date = fields.Date('Date de fabrication')
    
    # Certifications existantes
    #foreign_certifications = fields.Text('Certifications étrangères')
    #compliance_certificate = fields.Binary('Certificat de conformité')
    
    # Historique des demandes
    certification_request_ids = fields.One2many('phytosanitary.certification.request', 
                                                'equipment_id', string='Demandes de certification')
    
    def _get_equipment_types(self):
        """Méthode extensible pour les types d'équipements"""
        return [
            ('Pulvérisateurs à dos à pression entretenue', 'Pulvérisateurs à dos à pression entretenue'),
        ('Pulvérisateurs à dos à moteur', 'Pulvérisateurs à dos à moteur'),
        ('Pulvérisateurs à dos à pression préalable', 'Pulvérisateurs à dos à pression préalable'),
        ('Pulvérisateurs centrifuges', 'Pulvérisateurs centrifuges'),
        ('Appareils de nébulisation thermique','Appareils de nébulisation thermique'),
        ('Poudreuses', 'Poudreuses'), 
        ('Applicateurs de granules', 'Applicateurs de granules'),
        ('Nébulisateurs à froid', 'Nébulisateurs à froid'),
        ('Appareils tractés', 'Appareils tractés')
        ]

    equipment_type = fields.Selection(_get_equipment_types, string='Type', required=True)
    
    def action_view_certifications(self):
        """Afficher les certifications de l'appareil"""
        return {
            'name': 'Certifications',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'phytosanitary.certification.request',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id}
        }