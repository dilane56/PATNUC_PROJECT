# -*- coding: utf-8 -*-
{
    'name': "patnuc_minepia_certificat_sanitaire",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
    Module de gestion du processus d'obtention d'un certificat sanitaire vétérinaire au Cameroun.
    """,

    'author': "KAMGAING FOTSO ROMARIC",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],
    'installable': True,
    'application': True,
    'auto_install': False,

    # always loaded
    'data': [
       'security/vet_vertificate_security.xml',
        'security/ir.model.access.csv',
        'views/vet_reject_wizard_views.xml',
        'reports/vet_certificate_report.xml',
        'views/vet_certificate_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

