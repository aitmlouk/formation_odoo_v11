# -*- coding: utf-8 -*-
from odoo import http

class Formation(http.Controller):
    @http.route('/formation', type='http', auth='public', website=True)
    def render_web_page(self):
        return http.request.render('formation.formation_page', {})
    
    @http.route('/formation/claim', type='http', auth='public', website=True)
    def navigate_to_another_page(self):
        claim_ids = http.request.env['claim.claim'].sudo().search([])
        return http.request.render('formation.claim_page', {'claim_ids': claim_ids})