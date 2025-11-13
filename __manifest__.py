{
    'name': 'Web Site Date',
    'version': '16.0',
    'category': 'Tools',
    'author':'Mauro Bogado,Exemax',
    'summary': 'Modulo para poder realizar la carga de datos del futuro contacto desde el entorno de la web y replicarlo en el entorno de Odoo',
    'depends': ['base','sale','web', 'website'],
    'data': [
        #'security/ir.model.access.csv',
        'views/website_date.xml',
        'views/res_partner_view.xml',
        
        
    ],
    'assets': {
    'web.assets_frontend': [
        'exe_create_contact_website/views/website_date.xml',
    ],
    },

    'installable': True,
    'application': False,
}   