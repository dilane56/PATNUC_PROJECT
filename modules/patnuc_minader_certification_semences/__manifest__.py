# -*- coding: utf-8 -*-
{
    'name': 'PATNUC - MINADER_Certification des Semences et Plants',
    'version': '17.0.1.0.0',
    'category': 'Agriculture',
    'summary': 'Procédure de Suivi des opérations et certification des semences et plants - MINADER',
    'description': """
        Module de gestion de la procédure de Suivi des opération et certification des semences et plants
        pour le Ministère de l'Agriculture et du Développement Rural (MINADER).
        
        Fonctionnalités:
        - Suivi complet des demandes de certification
        - Gestion des acteurs (opérateurs, laboratoires, services)
        - Workflow automatisé avec validations
        - Génération de certificats officiels
        - Traçabilité complète des opérations
        - Interface dédiée pour chaque type d'acteur
    """,
    'author': 'Francesca MBOUEMBE',
    'depends': ['base', 'mail', 'portal', 'hr'],
    'data': [
        #sécurity
        'security/security.xml',
        'security/ir.model.access.csv',
        
        
        #datas
        'data/sequences.xml',
        'data/workflow_data.xml',
        
        #views
        'views/certification_request_views.xml',
        'views/operator_views.xml',
        'views/laboratory_analysis_views.xml',
        'views/field_control_views.xml',
        'views/certificate_views.xml',
        'views/laboratory_views.xml',
        'views/production_site_views.xml',
        'views/technical_review_views.xml',
        'views/menu_views.xml',
        
        #reports
        'reports/certificate_report.xml',
        'reports/certificate_template.xml',
        
        
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}