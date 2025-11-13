from odoo import http
from odoo.http import request
import logging
import random
import string

_logger = logging.getLogger(__name__)

class WebsiteNewClientForm(http.Controller):

    @http.route(['/nuevo_cliente'], type='http', auth="public", website=True)
    def nuevo_cliente_form(self, **kw):
        # Buscar país Argentina
        argentina = request.env['res.country'].sudo().search([('code', '=', 'AR')], limit=1)

        # Provincias de Argentina
        states = request.env['res.country.state'].sudo().search([('country_id', '=', argentina.id)])

        # Responsabilidad ante AFIP
        afip_responsabilities = request.env['l10n_ar.afip.responsibility.type'].sudo().search([])

        return request.render('exe_create_contact_website.template_nuevo_cliente_form', {
            'states': states,
            'afip_responsabilities': afip_responsabilities
        })

    @http.route(['/nuevo_cliente/enviar'], type='http', auth="public", website=True, csrf=False)
    def nuevo_cliente_enviar(self, **post):
        # comment = f"""
        # Nombre del local: {post.get('local_name')}
        # Transporte preferido: {post.get('transporte')}
        # Horario de entrega: {post.get('horario_transporte')}
        # ¿Trabaja con nuestra mercadería?: {post.get('trabaja_mercaderia')}
        # """

        # if post.get('trabaja_mercaderia') == 'Sí':
        #     comment += f"A quién le compra o compraba repuestos: {post.get('origen_producto_si')}\n"
        # elif post.get('trabaja_mercaderia') == 'No':
        #     comment += f"¿Cómo conoció los productos?: {post.get('origen_producto_no')}\n"
        
        #agregado de pais
        countries = request.env['res.country'].sudo().search([], order='name ASC')

        # 🔒 Validación del CUIT
        cuit = post.get('vat', '').strip()
        #if not cuit.isdigit() or len(cuit) != 11:
        if len(cuit) != 11:    
            argentina = request.env['res.country'].sudo().search([('code', '=', 'AR')], limit=1)
            states = request.env['res.country.state'].sudo().search([('country_id', '=', argentina.id)])
            afip_responsabilities = request.env['l10n_ar.afip.responsibility.type'].sudo().search([])

            return request.render('exe_create_contact_website.template_nuevo_cliente_form', {
                'error': "El CUIT debe tener exactamente 11 dígitos numéricos sin guiones.",
                'states': states,
                'afip_responsabilities': afip_responsabilities,
                'form_data': post
            })

        try:
            # ✅ Si el CUIT es válido, se crea el partner
            # Determinar country_id: intentar usar el campo `country` pasado por formulario,
            # si no viene, usar Argentina por defecto (si existe)
            country_id = False
            if post.get('country'):
                country = request.env['res.country'].sudo().search(['|', ('name', '=', post.get('country')), ('code', '=', post.get('country'))], limit=1)
                country_id = country.id if country else False
            if not country_id:
                argentina = request.env['res.country'].sudo().search([('code', '=', 'AR')], limit=1)
                country_id = argentina.id if argentina else False

            partner_vals = {
                'name': post.get('name'),
                'city': post.get('city'),
                'state_id': int(post.get('state_id')) if post.get('state_id') else False,
                'country_id': country_id,
                'street': post.get('street'),
                'zip': post.get('zip'),
                'mobile': post.get('mobile'),
                'phone': post.get('phone'),
                'email': post.get('email'),
                'vat': cuit,
                'l10n_latam_identification_type_id': request.env['l10n_latam.identification.type'].sudo().search([('name', '=', 'CUIT')], limit=1).id,

                # Campos personalizados
                'how_met_us': post.get('how_met_us'),
                'how_met_us_other': post.get('how_met_us_other'),
                'interest_products': post.get('interest_products'),
                'how_met_us_other_products': post.get('how_met_us_other_products'),
                'client_type': post.get('client_type'),
                'has_experience': post.get('has_experience') == 'on' or post.get('has_experience') == '1',
                'motivation_text': post.get('motivation_text'),
                'website_url': post.get('website_url'),
                'social_url': post.get('social_url'),
                'business_activity': post.get('business_activity'),
                'business_years': int(post.get('business_years')) if post.get('business_years') else False,
                'employee_count': int(post.get('employee_count')) if post.get('employee_count') else False,
                'store_count': post.get('store_count'),
                'product_categories_other': post.get('product_categories_other'),
                'text_others_products_categories': post.get('text_others_products_categories'),
                'additional_comments': post.get('additional_comments'),
            }

            partner = request.env['res.partner'].sudo().create(partner_vals)

        except Exception:
            _logger.exception('Error creando partner desde formulario web')
            argentina = request.env['res.country'].sudo().search([('code', '=', 'AR')], limit=1)
            states = request.env['res.country.state'].sudo().search([('country_id', '=', argentina.id)])
            afip_responsabilities = request.env['l10n_ar.afip.responsibility.type'].sudo().search([])
            return request.render('exe_create_contact_website.template_nuevo_cliente_form', {
                'error': 'Ocurrió un error al registrar el contacto. Por favor intentá nuevamente más tarde.',
                'states': states,
                'afip_responsabilities': afip_responsabilities,
                'form_data': post
            })

        # if post.get('entrega_street'):
        #     request.env['res.partner'].sudo().create({
        #         'name': post.get('name') + ' (Entrega)',
        #         'parent_id': partner.id,
        #         'type': 'delivery',
        #         'street': post.get('entrega_street'),
        #         'zip': post.get('entrega_zip'),
        #         'city': post.get('entrega_city'),
        #         'state_id': int(post.get('entrega_state_id')) if post.get('entrega_state_id') else False,
        #     })

        #Datos para poder registrar el cliente
        # Verificá si ya existe un usuario con ese email
        existing_user = request.env['res.users'].sudo().search([('login', '=', partner.email)], limit=1)

        if not existing_user:
            try:
                portal_group = request.env.ref('base.group_portal')
                # Generar una contraseña temporal aleatoria
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                new_user = request.env['res.users'].sudo().create({
                    'name': partner.name,
                    'login': partner.email,
                    'email': partner.email,
                    'partner_id': partner.id,
                    'password': password,
                    'groups_id': [(6, 0, [portal_group.id])],
                })

                # Intentar autenticar la sesión para loguear al usuario inmediatamente
                db = False
                try:
                    db = request.session.db
                except Exception:
                    db = None
                if not db:
                    try:
                        db = request.env.cr.dbname
                    except Exception:
                        db = None

                if db:
                    try:
                        request.session.authenticate(db, new_user.login, password)
                    except Exception:
                        _logger.exception('No se pudo autenticar automáticamente al nuevo usuario')

            except Exception:
                _logger.exception('Error creando usuario portal desde formulario web')

        # Redirigir a página de gracias / inicio; el usuario debería quedar autenticado si la autenticación automática funcionó
        try:
            return request.redirect('/shop')
        except Exception:
            return request.redirect('/')
