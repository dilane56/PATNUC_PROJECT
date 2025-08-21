from odoo import models, fields

class HomologationStage(models.Model):
    _name = 'homologation.stage'
    _description = "Étape du workflow d'homologation"

    name = fields.Char(string="Nom de l'étape", required=True)
    sequence = fields.Integer(string="Ordre")
    description = fields.Text(string="Description")
    is_final = fields.Boolean(string="Étape finale")
    color = fields.Integer(string="Couleur")  # Ajouté pour compatibilité XML
    request_ids = fields.One2many('homologation.request', 'stage_id', string="Dossiers à cette étape")
