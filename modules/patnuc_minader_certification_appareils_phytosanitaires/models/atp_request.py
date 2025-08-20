# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# Types d'appareils (Article 17)
ATP_DEVICE_TYPES = [
    ("dos_pression_entretenue", "Pulvérisateur à dos à pression entretenue"),
    ("dos_moteur", "Pulvérisateur à dos à moteur"),
    ("dos_pression_prealable", "Pulvérisateur à dos à pression préalable"),
    ("centrifuge", "Pulvérisateur centrifuge"),
    ("nebulisation_thermique", "Appareil de nébulisation thermique"),
    ("poudreuse", "Poudreuse"),
    ("applicateur_granules", "Applicateur de granules"),
    ("nebulisateur_froid", "Nébulisateur à froid"),
    ("appareil_tracte", "Appareil tracté"),
]

ENERGY_SOURCES = [
    ("manuelle", "Manuelle"),
    ("electrique", "Électrique"),
    ("essence", "Essence"),
    ("batterie", "Batterie"),
]

REQUEST_STATES = [
    ("draft", "Brouillon"),
    ("submitted", "Soumise"),
    ("admin_check", "Vérification administrative"),
    ("lab_tests", "Tests de spécifications (labo)"),
    ("field_tests", "Tests de performance (champ)"),
    ("synthesis", "Synthèse"),
    ("decision", "Décision de la Commission"),
    ("minister_sign", "Signature du Ministre"),
    ("certified", "Certificat émis"),
    ("rejected", "Rejetée"),
]


class AtpDocumentType(models.Model):
    _name = "atp.document.type"
    _description = "Type de document - Procédure ATP"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, help="Code stable (ex: DEMANDE_TIMBREE)")
    required = fields.Boolean(string="Obligatoire", default=True)
    sequence = fields.Integer(default=10)


class AtpDocument(models.Model):
    _name = "atp.document"
    _description = "Document joint - Demande ATP"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "type_id, id"

    request_id = fields.Many2one("atp.request", string="Demande", required=True, ondelete="cascade")
    type_id = fields.Many2one("atp.document.type", string="Type", required=True)
    file = fields.Binary(string="Fichier", attachment=True)
    filename = fields.Char(string="Nom du fichier")
    provided = fields.Boolean(string="Fourni", compute="_compute_provided", store=True)
    note = fields.Text(string="Commentaire")

    @api.depends("file")
    def _compute_provided(self):
        for rec in self:
            rec.provided = bool(rec.file)


class AtpRequest(models.Model):
    _name = "atp.request"
    _description = "Demande de certification d'appareil de traitement phytosanitaire"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    # Identité / Référence
    name = fields.Char(string="Référence", default="Nouveau", copy=False, readonly=True, tracking=True)
    state = fields.Selection(REQUEST_STATES, default="draft", tracking=True)

    # Demandeur
    applicant_name = fields.Char(string="Représentant légal", required=True, tracking=True)
    applicant_email = fields.Char(string="Email")
    applicant_phone = fields.Char(string="Téléphone")
    applicant_company = fields.Char(string="Structure / Entreprise")
    applicant_cni = fields.Char(string="N° CNI")
    cni_front = fields.Binary(string="Scan CNI (recto)", attachment=True)
    cni_back = fields.Binary(string="Scan CNI (verso)", attachment=True)

    # Appareil (Article 17 + infos techniques de base)
    device_name = fields.Char(string="Nom de l'appareil", required=True)
    brand = fields.Char(string="Marque")
    model = fields.Char(string="Modèle")
    device_type = fields.Selection(ATP_DEVICE_TYPES, string="Type d'appareil", required=True)
    energy_source = fields.Selection(ENERGY_SOURCES, string="Source d'énergie")
    capacity = fields.Float(string="Capacité nominale")
    max_pressure = fields.Float(string="Pression maximale")
    flow_rate = fields.Float(string="Débit")
    manufacture_date = fields.Date(string="Date de fabrication")

    # Pièces (Article 18)
    document_ids = fields.One2many("atp.document", "request_id", string="Documents")
    required_missing_count = fields.Integer(string="Docs requis manquants", compute="_compute_required_missing", store=False)

    # Dates / Certificat / Paiement
    submit_date = fields.Datetime(string="Date de soumission", readonly=True, tracking=True)
    planned_end_date = fields.Date(string="Date prévue de fin")
    end_date = fields.Date(string="Date réelle de fin")
    certificate_number = fields.Char(string="N° Certificat")
    certificate_start = fields.Date(string="Début validité")
    rejection_reason = fields.Text(string="Motif de rejet")

    fees_amount = fields.Float(string="Montant frais des tests")
    fee_receipt = fields.Binary(string="Reçu de paiement", attachment=True)

    # Auto: séquence
    @api.model
    def create(self, vals):
        if vals.get("name", "Nouveau") == "Nouveau":
            vals["name"] = self.env["ir.sequence"].next_by_code("atp.request") or "Nouveau"
        return super().create(vals)

    # Comptage des documents obligatoires manquants
    def _compute_required_missing(self):
        for rec in self:
            required_types = self.env["atp.document.type"].search([("required", "=", True)])
            provided_type_ids = set(rec.document_ids.mapped("type_id").ids)
            missing = required_types.filtered(lambda dt: dt.id not in provided_type_ids)
            rec.required_missing_count = len(missing)

    # Actions de workflow (v1 minimale)
    def action_submit(self):
        for rec in self:
            # Vérifications minimales avant soumission
            if not rec.applicant_name or not rec.device_name or not rec.device_type:
                raise ValidationError(_("Veuillez renseigner le représentant légal, le nom et le type d'appareil."))

            # Exiger au moins la Demande timbrée (Article 18-a)
            demande_type = self.env["atp.document.type"].search([("code", "=", "DEMANDE_TIMBREE")], limit=1)
            has_demande = any(d.type_id.id == demande_type.id and d.provided for d in rec.document_ids) if demande_type else False
            if not has_demande:
                raise ValidationError(_("La 'Demande timbrée' (Article 18-a) est requise pour soumettre."))

            rec.write({
                "state": "submitted",
                "submit_date": fields.Datetime.now(),
            })

    # (Placeholders pour les étapes suivantes — on les implémentera à l'Étape 2+)
    def action_admin_check(self):
        self.write({"state": "admin_check"})

    def action_lab_tests(self):
        self.write({"state": "lab_tests"})

    def action_field_tests(self):
        self.write({"state": "field_tests"})

    def action_synthesis(self):
        self.write({"state": "synthesis"})

    def action_decision(self):
        self.write({"state": "decision"})

    def action_minister_sign(self):
        self.write({"state": "minister_sign"})

    def action_certify(self):
        self.write({"state": "certified"})
