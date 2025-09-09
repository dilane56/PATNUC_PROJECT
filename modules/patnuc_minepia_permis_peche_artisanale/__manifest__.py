# -*- coding: utf-8 -*-
{
    'name': "patnuc_minepia_permis_peche_artisanale",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
        'data/sequences.xml',
        'security/fishing_permit_security.xml',
        'security/ir.model.access.csv',
        'reports/fishing_permit_report.xml',
        'views/fishing_permit_reject_views.xml',
        'views/views.xml',
        'views/fishing_permit_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

