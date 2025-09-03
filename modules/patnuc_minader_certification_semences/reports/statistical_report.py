from odoo import models, fields, api
from odoo import tools

class CertificationStatisticalReport(models.Model):
    _name = 'certification.statistical.report'
    _description = 'Rapport Statistique Certification'
    _auto = False
    
    operator_id = fields.Many2one('certification.operator', string='Opérateur')
    seed_variety = fields.Char('Variété')
    request_count = fields.Integer('Nombre de demandes')
    approved_count = fields.Integer('Nombre approuvées')
    rejected_count = fields.Integer('Nombre rejetées')
    average_processing_time = fields.Float('Temps moyen de traitement (jours)')
    total_certified_quantity = fields.Float('Quantité totale certifiée (kg)')
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT 
                    ROW_NUMBER() OVER() AS id,
                    cr.operator_id,
                    cr.seed_variety,
                    COUNT(*) as request_count,
                    SUM(CASE WHEN cr.state IN ('approved', 'certificate_issued') THEN 1 ELSE 0 END) as approved_count,
                    SUM(CASE WHEN cr.state = 'rejected' THEN 1 ELSE 0 END) as rejected_count,
                    AVG(CASE WHEN cr.completion_date IS NOT NULL 
                        THEN EXTRACT(EPOCH FROM (cr.completion_date - cr.submission_date))/86400 
                        ELSE NULL END) as average_processing_time,
                    SUM(COALESCE(cc.certified_quantity, 0)) as total_certified_quantity
                FROM certification_request cr
                LEFT JOIN certification_certificate cc ON cc.request_id = cr.id
                GROUP BY cr.operator_id, cr.seed_variety
            )
        """ % self._table)