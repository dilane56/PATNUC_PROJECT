# -*- coding: utf-8 -*-


{
    "name": "Certification Appareils Phytosanitaires (MINADER)",
    "summary": "Procédure de certification des appareils de traitement phytosanitaire",
    "version": "17.0.1.0.0",
    "author": "PATNUC / MINADER",
    "website": "",
    "license": "LGPL-3",
    "category": "Government",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "data/atp_document_types.xml",
        "views/atp_request_views.xml",
    ],
    "application": True,
    "installable": True,
}
