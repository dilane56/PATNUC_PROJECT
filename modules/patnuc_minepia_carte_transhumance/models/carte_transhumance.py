from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CarteTranshumance(models.Model):
    _name = 'carte.transhumance'
    _description = 'Demande de Carte de Transhumance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Numéro de demande', required=True, copy=False, readonly=True, default='Nouveau')
    initiateur_id = fields.Many2one('res.partner', string='Initiateur', required=True)
    date_demande = fields.Date(string='Date de la demande', default=fields.Date.today(), readonly=True)
    delai_imparti = fields.Integer(string='Délai de traitement (jours)', default=2, readonly=True)

    # Informations sur les acteurs et le trajet
    proprietaire = fields.Char(string='Nom complet du Propriétaire', required=True)
    destination = fields.Char(string='Destination', required=True)

    # Document requis
    document_ids = fields.One2many("carte.document", "request_id", string="Documents")
    required_missing_count = fields.Integer(string="Docs requis manquants", compute="_compute_required_missing",
                                            store=False)
    # Motiif de rejet
    rejection_reason = fields.Text(string="Motif de rejet", readonly=True)




    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('administrative_check', 'Vérification Administrative'),
        ('deeper_check', 'Vérification Approfondie'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
    ], string='Statut', default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('carte.transhumance') or 'Nouveau'
        return super(CarteTranshumance, self).create(vals)

        # Comptage des documents obligatoires manquants

    def _compute_required_missing(self):
        for rec in self:
            required_types = self.env["carte.document.type"] .search([("required", "=", True)])
            provided_type_ids = set(rec.document_ids.mapped("type_id").ids)
            missing = required_types.filtered(lambda dt: dt.id not in provided_type_ids)
            rec.required_missing_count = len(missing)

    def action_submit(self):
        """Action pour soumettre la demande."""
        if self.required_missing_count > 0:
            required_types = self.env["carte.document.type"].search([("required", "=", True)])
            provided_type_ids = set(self.document_ids.mapped("type_id").ids)
            missing_docs = required_types.filtered(lambda dt: dt.id not in provided_type_ids)
            missing_names = missing_docs.mapped('name')
            raise ValidationError("Impossible de soumettre la demande. Documents manquants :\n• %s" % '\n• '.join(missing_names))
        
        self.state = 'administrative_check'
        self.message_post(body="La demande de carte de transhumance a été soumise et la verification administrative est en attente.")



    def action_deeper_check(self):
        """Action pour lancer la vérification approfondie."""
        self.state = 'deeper_check'
        self.message_post(body="La demande est passée à l'étape de vérification approfondie.")

    def action_approve(self):
        """Action pour approuver la carte."""
        self.state = 'approved'
        self.message_post(body="La carte de transhumance a été approuvée et délivrée.")