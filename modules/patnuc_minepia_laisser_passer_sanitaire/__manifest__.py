{
    'name': "patnuc_minepia_laisser_passer_sanitaire",
    'version': '1.0',
    'depends': ['base', 'mail'],
    'author': "Votre Nom",
    'category': 'Administration',
    'description': """
    Module de gestion du processus d'obtention d'un laissez-passer sanitaire.
    """,
    'installable': True,
    'application': True,
    'auto_install': False,
    'data': [
        'security/laisser_passer_security.xml',
        'security/ir.model.access.csv',
        'views/laiser_passer_reject_wizard_views.xml',
        'views/laisser_passer_views.xml'
    ],
}