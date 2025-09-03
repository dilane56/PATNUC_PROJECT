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

    # Ajout des champs pour la vérification administrative
    administrative_check_date = fields.Datetime(string="Date de vérification administrative", readonly=True)
    administrative_checker_id = fields.Many2one('res.users', string="Agent vérificateur", readonly=True)
    administrative_check_comment = fields.Char(string="Commentaires de l'agent")

    # Champ pour la validation globale
    is_admin_check_ok = fields.Boolean(string="Vérification administrative validée",
                                       compute="_compute_is_admin_check_ok", store=True)

    # Champs pour la vérification approfondie
    deeper_check_date = fields.Datetime(string="Date de la vérification approfondie", readonly=True)
    deeper_checker_id = fields.Many2one('res.users', string="Agent de la vérification approfondie", readonly=True)
    deeper_check_result = fields.Selection([
        ('favorable', ' Favorable'),
        ('unfavorable', ' Défavorable'),
    ], string="Avis sur la demande", required=False)


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



    @api.depends("document_ids.is_valid")
    def _compute_is_admin_check_ok(self):
        """Vérifie si tous les documents requis et fournis sont valides."""
        for rec in self:
            # On vérifie que le document est fourni ET qu'il a été validé par l'agent
            rec.is_admin_check_ok = all(doc.is_valid for doc in rec.document_ids.filtered(lambda d: d.provided))
            # On pourrait aussi ajouter une contrainte pour s'assurer que tous les documents requis sont présents
            # et que required_missing_count == 0. C'est déjà géré par la soumission, mais c'est une bonne pratique.

    def action_administrative_check_ok(self):
        """Action pour valider la vérification administrative et passer à l'étape suivante."""
        self.ensure_one()
        # On peut ajouter ici une validation finale avant de changer d'état
        if self.administrative_check_comment is False:
            raise ValidationError("Veuillez ajouter un commentaire avant de valider la vérification administrative.")
        if not self.is_admin_check_ok:
            raise ValidationError("Veuillez valider tous les documents fournis avant de continuer.")

        self.write({
            'state': 'deeper_check',
            'administrative_check_date': fields.Datetime.now(),
            'administrative_checker_id': self.env.user.id,
        })
        self.message_post(body="Vérification administrative effectuée et validée. La demande passe à l'étape de vérification approfondie.")



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

    def action_deeper_check_ok(self):
        """Action pour valider la vérification approfondie et passer à l'approbation."""
        self.ensure_one()
        if self.deeper_check_result != 'favorable':
            raise ValidationError("La demande ne peut être validée qu'avec un avis favorable.")

        self.state = 'approved'
        self.deeper_check_date = fields.Datetime.now()
        self.deeper_checker_id = self.env.user.id
        self.message_post(
            body="Vérification approfondie validée avec un avis favorable. La carte est prête à être délivrée.")


