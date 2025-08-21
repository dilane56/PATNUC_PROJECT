# -*- coding: utf-8 -*-
{
    'name': "PATNUC - LOGIN",

    'summary': """
        Customise l'interface de connexion pour le Projet d'accélération de la transformation numérique au Cameroun""",

    'description': """
        # Edit l'interface d'authentification Odoo
        * Ajout de l'image
        * Modification de la position du formulaire
        * Refonte des couleur
    """,

    'author': "Francesca MBOUEMBE - MFD",
    'website': "https://www.exemple.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Theme',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['web','muk_web_theme','base_setup'],

    # always loaded
    'data': [
        # 'views/patnuc_login_assets.xml',
        'views/webclient_templates.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_frontend': [
            'patnuc_login/static/src/css/web_login_style.css',
            # 'patnuc_login/static/src/js/**/*.js',
            'patnuc_login/static/src/js/session_timeout.js',
        ],
    },
    'license': 'LGPL-3',
}
