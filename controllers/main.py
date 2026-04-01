# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class FreightWebsite(http.Controller):

    @http.route(['/freight/track'], type='http', auth="public", website=True)
    def freight_tracking_page(self, **kw):
        """Public shipment tracking page"""
        return request.render("freight_management.freight_tracking_page", {})

    @http.route(['/freight/track/search'], type='json', auth="public", website=True)
    def freight_track_search(self, tracking_number=None, **kw):
        """Search for shipment by tracking number"""
        if not tracking_number:
            return {'error': 'Please provide a tracking number'}

        shipment = request.env['freight.shipment'].sudo().search([
            ('name', '=', tracking_number)
        ], limit=1)

        if not shipment:
            return {'error': 'Shipment not found'}

        return {
            'success': True,
            'shipment': {
                'name': shipment.name,
                'state': shipment.state,
                'origin': shipment.origin_location_id.name,
                'destination': shipment.destination_location_id.name,
                'shipment_date': shipment.shipment_date.strftime('%Y-%m-%d') if shipment.shipment_date else '',
                'estimated_delivery': shipment.estimated_delivery_date.strftime('%Y-%m-%d') if shipment.estimated_delivery_date else '',
                'transport_legs': [{
                    'sequence': leg.sequence,
                    'transport_mode': leg.transport_mode,
                    'origin': leg.origin_location_id.name,
                    'destination': leg.destination_location_id.name,
                    'status': leg.status,
                } for leg in shipment.transport_leg_ids]
            }
        }

    @http.route(['/freight/quote'], type='http', auth="public", website=True)
    def freight_quote_page(self, **kw):
        """Public quotation request page"""
        locations = request.env['freight.location'].sudo().search([])
        return request.render("freight_management.freight_quote_page", {
            'locations': locations,
        })

    @http.route(['/freight/quote/submit'], type='json', auth="public", website=True, csrf=False)
    def freight_quote_submit(self, **kw):
        """Submit quotation request"""
        partner_name = kw.get('partner_name')
        partner_email = kw.get('partner_email')
        partner_phone = kw.get('partner_phone')
        origin_id = kw.get('origin_id')
        destination_id = kw.get('destination_id')
        cargo_type = kw.get('cargo_type')
        weight = kw.get('weight')
        volume = kw.get('volume')

        if not all([partner_name, partner_email, origin_id, destination_id]):
            return {'error': 'Please fill all required fields'}

        # Create or find partner
        partner = request.env['res.partner'].sudo().search([
            ('email', '=', partner_email)
        ], limit=1)

        if not partner:
            partner = request.env['res.partner'].sudo().create({
                'name': partner_name,
                'email': partner_email,
                'phone': partner_phone,
            })

        # Create quotation
        quotation = request.env['freight.quotation'].sudo().create({
            'partner_id': partner.id,
            'origin_location_id': int(origin_id),
            'destination_location_id': int(destination_id),
            'cargo_type': cargo_type,
            'total_weight': float(weight) if weight else 0,
            'total_volume': float(volume) if volume else 0,
            'state': 'draft',
        })

        return {
            'success': True,
            'message': 'Your quotation request has been submitted. We will contact you soon.',
            'quotation_ref': quotation.name
        }
