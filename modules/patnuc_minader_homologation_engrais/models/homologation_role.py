from odoo import models, fields

class HomologationRole(models.Model):
    _name = 'homologation.role'
    _description = "Rôle dans le processus d'homologation"

    name = fields.Char(string="Nom du rôle", required=True)
    description = fields.Text(string="Description")
