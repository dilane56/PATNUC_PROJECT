from odoo import models, fields

class HomologationProduit(models.Model):
    _name = 'homologation.produit'
    _description = "produit Engrais/Fertilisant"

    name = fields.Char("Nom / Marque du produit", required=True)
    poids_net = fields.Float("Poids Net (Kg)", required=True)
    fabricant = fields.Char("Nom du fabriquant ou Distributeur", required=True)
    specificites_qualite = fields.Text("Specifications Qualité & garantie")
    toxicite = fields.Text("Dégré de toxicité")
    risques = fields.Text("Risques sur la santé et l'environement")
    principe_actif = fields.Char("Principe Actif")
    notice_utilisation = fields.Text("Notice d'utilisation")
    type_produit = fields.Selection([
        ('organique', 'Engrais Organique'),
        ('mineraux', 'Engrais mineraux'),
        ('organo_mineraux', 'Engrais organo-mineraux'),
    ], string="Type d'engrais", required=True)
