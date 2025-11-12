# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    how_met_us = fields.Selection([
        ('recommendation', 'Recomendaciones'),
        ('google', 'Búsqueda en Google'),
        ('social', 'Redes sociales'),
        ('ads', 'Publicidad'),
        ('other', 'Otro')
    ], string="¿Cómo nos conociste?")

    how_met_us_other = fields.Char("Especificar otro")

    product_interests = fields.Many2many(
    'product.category',
    'res_partner_product_interest_rel',  # nombre único de la tabla relacional
    'partner_id',
    'category_id',
    string="Productos que te interesan"
    )

    product_categories = fields.Many2many(
        'product.category',
        'res_partner_product_category_rel',  # nombre distinto de la tabla relacional
        'partner_id',
        'category_id',
        string="Categorías de interés"
    )
    product_interest_other = fields.Char("Otros productos")

    client_type = fields.Selection([
        ('entrepreneur', 'Quiero emprender'),
        ('business_owner', 'Tengo un negocio')
    ], string="Tipo de cliente")

    # Campos para emprendedores
    has_experience = fields.Boolean("¿Tenés experiencia previa?")
    motivation_text = fields.Text("¿Qué te motiva a emprender?")

    # Campos para negocios
    website_url = fields.Char("URL Sitio web")
    social_url = fields.Char("URL Red social")
    business_activity = fields.Char("Rubro / actividad")
    business_years = fields.Integer("Años operando")
    employee_count = fields.Integer("Cantidad de empleados")
    store_count = fields.Selection([
        ('1', '1'),
        ('2_plus', '2 o más'),
        ('traveler', 'Soy viajante')
    ], string="Cantidad de locales")

    
    product_categories_other = fields.Text("Otros productos")
    additional_comments = fields.Text("Comentarios adicionales")