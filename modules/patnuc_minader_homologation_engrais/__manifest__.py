# -*- coding: utf-8 -*-
{
    'name': "PATNUC - MINADER_Homologation Engrais",
    'version': '17.0.1.0.0',
    'summary': "Module de soumission et gestion des dossiers d'homologation des engrais selon la loi n°2003/007",
    'description': """
        Module pour la digitalisation de la procédure d'homologation des engrais au Cameroun.
        Conforme à la loi n°2003/007 du 10 juillet 2003 et le décret n°2005/118 du 15 avril 2005.
        
        Étapes de la procédure :
        1. Soumission du dossier
        2. Contrôle de conformité
        3. Analyses chimiques
        4. Tests d'efficacité biologique
        5. Tests de prévulgarisation
        6. Évaluation agro-économique
        7. Homologation
        
        Documents requis :
        - Demande d'homologation timbrée
        - Justificatif de versement d'échantillons
        - Dossier technique du produit
        - Récépissé de dépôt d'échantillons
        - Pièces d'identification du demandeur
        
        Acteurs autorisés :
        - Entreprises privées (fabricants, importateurs, distributeurs)
        - Laboratoires ou représentants autorisés
        - Coopératives agricoles agréées
        - Instituts de recherche (cas particuliers)
    """,
    'author': "KAMGAING FOTSO ROMARIC",
    'website': "https://www.patnuc.com",
    'category': 'Agriculture',
    'depends': [
        'base',
        'mail',
        'portal',
        'hr',       # Pour les employés/agents MINADER
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/fertilizer_stages.xml',
        'views/fertilizer_applicant_views.xml',
        'views/fertilizer_company_views.xml',
        'views/fertilizer_product_views.xml',
        'views/fertilizer_homologation_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

