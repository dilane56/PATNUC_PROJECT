# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class PhytosanitaryTechnicalEvaluation(models.Model):
    _name = 'phytosanitary.technical.evaluation'
    _description = 'Évaluation Technique des Appareils Phytosanitaires'

    name = fields.Char('Référence', required=True, default=lambda self: _('Nouveau'))
    request_id = fields.Many2one('phytosanitary.certification.request', 
                                 string='Demande', required=True)
    equipment_id = fields.Many2one('phytosanitary.equipment', string='Appareil', required=True)
    evaluator_id = fields.Many2one('res.users', string='Évaluateur', required=True)
    evaluation_date = fields.Date('Date d\'évaluation', required=True)
    
    # Critères d'évaluation
    functionality_score = fields.Float('Score Fonctionnalité', default=0.0)
    safety_score = fields.Float('Score Sécurité', default=0.0)
    compliance_score = fields.Float('Score Conformité', default=0.0)
    overall_score = fields.Float('Score Global', compute='_compute_overall_score')
    
    # Évaluation détaillée
    functionality_comments = fields.Text('Commentaires Fonctionnalité')
    safety_comments = fields.Text('Commentaires Sécurité')
    compliance_comments = fields.Text('Commentaires Conformité')
    
    # Tests effectués
    field_test_performed = fields.Boolean('Test terrain effectué')
    field_test_date = fields.Date('Date test terrain')
    field_test_results = fields.Text('Résultats test terrain')
    
    # Recommandation
    recommendation = fields.Selection([
        ('favorable', 'Favorable'),
        ('conditional', 'Favorable sous conditions'),
        ('unfavorable', 'Défavorable')
    ], string='Recommandation')
    conditions = fields.Text('Conditions (si applicable)')
    
    # Rapport technique
    technical_report = fields.Text('Rapport technique')
    technical_report_file = fields.Binary('Fichier rapport technique')
    
    environmental_impact_score = fields.Float('Score Impact Environnemental')
    durability_score = fields.Float('Score Durabilité')
    maintenance_score = fields.Float('Score Facilité de Maintenance')
    
    # État de l’évaluation
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('in_progress', 'En cours'),
        ('done', 'Validé'),
    ], string='Statut', default='draft', tracking=True)
    
    @api.depends('functionality_score', 'safety_score', 'compliance_score',
                 'environmental_impact_score', 'durability_score', 'maintenance_score')
    def _compute_overall_score(self):
        """Calcul étendu du score global"""
        for record in self:
            scores = [
                record.functionality_score,
                record.safety_score, 
                record.compliance_score,
                record.environmental_impact_score,
                record.durability_score,
                record.maintenance_score
            ]
            valid_scores = [s for s in scores if s > 0]
            record.overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
    
    # @api.depends('functionality_score', 'safety_score', 'compliance_score')
    # def _compute_overall_score(self):
    #     for record in self:
    #         if record.functionality_score or record.safety_score or record.compliance_score:
    #             record.overall_score = (record.functionality_score + 
    #                                     record.safety_score + 
    #                                     record.compliance_score) / 3
    #         else:
    #             record.overall_score = 0.0
    
    def action_set_in_progress(self):
        for record in self:
            record.state = 'in_progress'

    def action_set_done(self):
        for record in self:
            record.state = 'done'

class PhytosanitaryAdminEvaluation(models.Model):
    _name = 'phytosanitary.admin.evaluation'
    _description = 'Évaluation Administrative'

    request_id = fields.Many2one('phytosanitary.certification.request', 
                                 string='Demande', required=True)
    evaluator_id = fields.Many2one('res.users', string='Évaluateur', required=True)
    evaluation_date = fields.Date('Date d\'évaluation', required=True)
    
    # Vérifications documentaires
    documents_complete = fields.Boolean('Documents complets')
    documents_valid = fields.Boolean('Documents valides')
    fees_verified = fields.Boolean('Frais vérifiés')
    
    # Résultat
    is_compliant = fields.Boolean('Conforme')
    non_compliance_reasons = fields.Text('Motifs de non-conformité')
    
    # Actions requises
    additional_documents_needed = fields.Text('Documents supplémentaires requis')
    corrections_needed = fields.Text('Corrections nécessaires')
    
    # État de l’évaluation
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('in_progress', 'En cours'),
        ('done', 'Validé'),
    ], string='Statut', default='draft', tracking=True)
    
    
    def action_set_in_progress(self):
        self.state = 'in_progress'

    def action_set_done(self):
        self.state = 'done'