{
    'name': "Certification Phytosanitaire PATNUC MINADER",
    'version': '1.0',
    'depends': ['base', 'mail'],
    'author': "Votre Nom",
    'category': 'Administration',
    'description': """
    Module de gestion du processus de certification des appareils de traitement phytosanitaire.
    """,
    'installable': True,
    'application': True,  # 👈 Cette ligne est cruciale
    'auto_install': False,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/reject_wizard_views.xml',
        'views/menu_views.xml',
        'views/appareil_views.xml',
        'views/certification_request_views.xml'
    ],
}