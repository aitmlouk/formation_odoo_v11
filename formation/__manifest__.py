# -*- coding: utf-8 -*-
{
    'name': 'Formation Technique Odoo v11',
    'version': '1.0',
    'author': 'Ait-Mlouk Addi',
    'website': 'https://www.sdatacave.com',
    'support': 'aitmlouk@gmail.com',
    'license': "AGPL-3",
    'complexity': 'easy',
    'sequence': 1,
    'category': 'category',
    'description': """
        Put your description here for your module:
            - model1
            - model2
            - model3
    """,
    'depends': ['base','mail','hr','website','sale'],
    'summary': 'formation, odoo 11, erp, ',
    'data': [
        'security/formation.xml',
        'security/ir.model.access.csv',
        'views/formation_views.xml',
        'views/formation_inherit.xml',
        'data/sequence.xml',
        'demo/demo.xml',
        'controllers/formation.xml',
        'controllers/claim.xml',
        'controllers/bulletin.xml',
        'report/report.xml',
        'report/registration.xml',
        'report/bulletin_template.xml',
        'views/snippet.xml',
        'wizard/wiz_views.xml',
        'menu.xml',
    ],
    'demo': [
        'demo/demo.xml'
    ],
    'css': [
        #'static/src/css/ModuleName_style.css'
    ],
    
    'installable': True,
    'application': True,
}