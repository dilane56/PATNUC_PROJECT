# -*- coding: utf-8 -*-
{
    'name': "patnuc_minepia_carte_transhumance",

    'version': '1.0',
    'depends': ['base', 'mail'],
    'author': "KAMGAING FOTSO ROMARIC",
    'category': 'Administration',
    'description': """
    Module de gestion du processus d'obtention d'une carte de transhumance.
    """,
    'installable': True,
    'application': True,
    'auto_install': False,
    'data': [
        'security/carte_transhumance_security.xml',
        'security/ir.model.access.csv',
        'views/carte_reject_wizard_views.xml',
        # 'data/carte_trans_document_type.xml',  # ANCIENNE APPROCHE - Commenté temporairement
        'reports/carte_transhumance_report.xml',
        'views/carte_tanshumance_views.xml'
    ],
}