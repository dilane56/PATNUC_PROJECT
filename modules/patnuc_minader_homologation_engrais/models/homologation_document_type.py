from odoo import models, fields

class HomologationDocumentType(models.Model):
    _name = 'homologation.document.type'
    _description = "Type de document requis"

    name = fields.Char(string="Nom du document", required=True)
    description = fields.Text(string="Description")
    stage_required = fields.Many2one('homologation.stage', string="Étape requise")
