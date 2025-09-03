
from odoo import models, fields, api, _
from . import carte_transhumance


class CarteDocumentType(models.Model):
    _name = "carte.document.type"
    _description = "Type de document - Procédure Obtention d'un carte de Transhumance"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, help="Code stable (ex: DEMANDE_TIMBREE)")
    required = fields.Boolean(string="Obligatoire", default=True)
    sequence = fields.Integer(default=10)


class CarteDocument(models.Model):
    _name = "carte.document"
    _description = "Document joint - Demande de carte de transhumance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "type_id, id"

    request_id = fields.Many2one("carte.transhumance", string="Demande", required=True, ondelete="cascade")
    type_id = fields.Many2one("carte.document.type", string="Type", required=True)
    file = fields.Binary(string="Fichier", attachment=True)
    filename = fields.Char(string="Nom du fichier")
    provided = fields.Boolean(string="Fourni", compute="_compute_provided", store=True)
    note = fields.Text(string="Commentaire")

    # Nouveaux champs pour la validation administrative
    is_valid = fields.Boolean(string="Validé", default=False)
    validation_note = fields.Char(string="Note de l'agent")

    @api.depends("file")
    def _compute_provided(self):
        for rec in self:
            rec.provided = bool(rec.file)




