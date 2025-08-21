from odoo import models, fields

class HomologationDocument(models.Model):
    _name = 'homologation.document'
    _description = "Document joint au dossier"

    name = fields.Char(string="Nom du document", required=True)
    document_type_id = fields.Many2one('homologation.document.type', string="Type de document")
    filename = fields.Char(string="Nom du fichier")
    file_size = fields.Integer(string="Taille du fichier (octets)")
    request_id = fields.Many2one('homologation.request', string="Dossier associé")
