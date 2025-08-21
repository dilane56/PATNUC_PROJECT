from odoo import models, fields

class Appareil(models.Model):
    _name = "certification.appareil"
    _description = "Appareil de traitement phytosanitaire"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom de l\'appareil', required=True)
    marque = fields.Char(string='Marque', required=True)
    model = fields.Char(string="Modèle")
    energy_source = fields.Selection([
        ("manuelle", "Manuelle"),
        ("electrique", "Électrique"),
        ("essence", "Essence"),
        ("batterie", "Batterie"),
    ], string="Source d'énergie")
    capacity = fields.Float(string="Capacité nominale")
    max_pressure = fields.Float(string="Pression maximale")
    flow_rate = fields.Float(string="Débit")
    manufacture_date = fields.Date(string="Date de fabrication")
    type_appareil = fields.Selection([
        ('pulverisateurs_dos_pression_entretenue', 'Pulvérisateurs à dos à pression entretenue'),
        ('pulverisateurs_dos_moteur', 'Pulvérisateurs à dos à moteur'),
        ('pulverisateurs_dos_pression_prealable', 'Pulvérisateurs à dos à pression préalable'),
        ('Pulvérisateurs centrifuges', 'Pulvérisateurs centrifuges'),
        ('Appareils de nébulisation thermique', 'Appareils de nébulisation thermique'),
        ('Poudreuses', 'Poudreuses'),
        ('Applicateurs de granules', 'Applicateurs de granules'),
        ('Nébulisateurs à froid', 'Nébulisateurs à froid'),
        ('Appareils tractés', 'Appareils tractés')
    ], string='Type d\'appareil', required=True)

