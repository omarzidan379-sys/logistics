# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from datetime import datetime, timedelta
import json


class FreightPortalAPI(http.Controller):
    """JSON API endpoints for the premium freight portal dashboard."""

    @http.route('/my/freight/api/dashboard', type='json', auth='user', website=True)
    def get_portal_dashboard_data(self, **kw):
        """Get all dashboard data for the portal freight page."""
        partner = request.env.user.partner_id
        commercial_partner = partner.commercial_partner_id
        today = datetime.now().date()

        Shipment = request.env['freight.shipment'].sudo()
        Quotation = request.env['freight.quotation'].sudo()

        base_domain_ship = [('partner_id', 'child_of', commercial_partner.id)]
        base_domain_quote = [('partner_id', 'child_of', commercial_partner.id)]

        # --- Stats ---
        active_shipments = Shipment.search_count(
            base_domain_ship + [('state', 'not in', ['delivered', 'completed', 'invoiced'])]
        )
        pending_quotes = Quotation.search_count(
            base_domain_quote + [('state', 'in', ['draft', 'quoted'])]
        )
        completed_shipments = Shipment.search_count(
            base_domain_ship + [('state', 'in', ['delivered', 'completed', 'invoiced'])]
        )
        customs_in_progress = Shipment.search_count(
            base_domain_ship + [('state', '=', 'customs_clearance')]
        )
        total_shipments = Shipment.search_count(base_domain_ship)
        total_quotes = Quotation.search_count(base_domain_quote)

        # --- Customs breakdown ---
        customs_submitted = Shipment.search_count(
            base_domain_ship + [('customs_status', '=', 'submitted')]
        )
        customs_under_review = Shipment.search_count(
            base_domain_ship + [('customs_status', '=', 'under_review')]
        )
        customs_cleared = Shipment.search_count(
            base_domain_ship + [('customs_status', '=', 'cleared')]
        )
        customs_held = Shipment.search_count(
            base_domain_ship + [('customs_status', '=', 'held')]
        )

        # --- Monthly KPIs (last 6 months) ---
        monthly_data = []
        for i in range(5, -1, -1):
            month_date = datetime.now() - timedelta(days=i * 30)
            month_start = month_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            month_label = month_date.strftime('%b')

            s_count = Shipment.search_count(
                base_domain_ship + [
                    ('create_date', '>=', month_start),
                    ('create_date', '<=', month_end)
                ]
            )
            q_count = Quotation.search_count(
                base_domain_quote + [
                    ('create_date', '>=', month_start),
                    ('create_date', '<=', month_end)
                ]
            )
            monthly_data.append({
                'month': month_label,
                'shipments': s_count,
                'quotations': q_count,
            })

        # --- Recent shipments ---
        recent_shipments_data = []
        recent_records = Shipment.search(base_domain_ship, limit=10, order='write_date desc')
        state_labels = dict(Shipment._fields['state'].selection)
        progress_map = {
            'draft': 5, 'booked': 15, 'in_operation': 30,
            'in_transit': 50, 'arrived': 65, 'customs_clearance': 75,
            'delivered': 90, 'completed': 100, 'invoiced': 100,
        }

        for rec in recent_records:
            recent_shipments_data.append({
                'id': rec.id,
                'name': rec.name,
                'origin': rec.origin_port_id.name if rec.origin_port_id else 'N/A',
                'destination': rec.destination_port_id.name if rec.destination_port_id else 'N/A',
                'state': rec.state,
                'state_label': state_labels.get(rec.state, rec.state),
                'service_type': rec.service_type,
                'progress': progress_map.get(rec.state, 0),
                'booking_date': rec.booking_date.strftime('%Y-%m-%d') if rec.booking_date else '',
                'customs_status': rec.customs_status or '',
                'has_documents': bool(rec.document_ids),
                'document_count': len(rec.document_ids),
            })

        # --- Notifications / Alerts ---
        alerts = []
        # Shipments in customs with held status
        held_shipments = Shipment.search(
            base_domain_ship + [('customs_status', '=', 'held')], limit=5
        )
        for sh in held_shipments:
            alerts.append({
                'type': 'danger',
                'icon': 'fa-exclamation-triangle',
                'title': f'Customs Hold: {sh.name}',
                'message': 'Shipment is held at customs. Please check required documents.',
            })

        # Quotations awaiting action
        awaiting_quotes = Quotation.search(
            base_domain_quote + [('state', '=', 'quoted')], limit=5
        )
        for q in awaiting_quotes:
            alerts.append({
                'type': 'warning',
                'icon': 'fa-file-text',
                'title': f'Quote Ready: {q.name}',
                'message': f'Amount: {q.total_amount:.2f} — Awaiting your response.',
            })

        return {
            'success': True,
            'stats': {
                'active_shipments': active_shipments,
                'pending_quotes': pending_quotes,
                'completed_shipments': completed_shipments,
                'customs_in_progress': customs_in_progress,
                'total_shipments': total_shipments,
                'total_quotes': total_quotes,
            },
            'customs': {
                'submitted': customs_submitted,
                'under_review': customs_under_review,
                'cleared': customs_cleared,
                'held': customs_held,
            },
            'monthly': monthly_data,
            'recent_shipments': recent_shipments_data,
            'alerts': alerts,
        }

    @http.route('/my/freight/api/shipment/<int:shipment_id>/timeline', type='json', auth='user', website=True)
    def get_shipment_timeline(self, shipment_id, **kw):
        """Get full lifecycle timeline for a shipment."""
        partner = request.env.user.partner_id
        shipment = request.env['freight.shipment'].sudo().browse(shipment_id)

        if not shipment.exists() or shipment.partner_id.commercial_partner_id != partner.commercial_partner_id:
            return {'error': 'Shipment not found'}

        # Define lifecycle stages
        stages = [
            {'key': 'draft', 'label': 'Request', 'icon': 'fa-file-text-o',
             'date': shipment.create_date.strftime('%Y-%m-%d') if shipment.create_date else ''},
            {'key': 'booked', 'label': 'Booked', 'icon': 'fa-calendar-check-o',
             'date': shipment.booking_date.strftime('%Y-%m-%d') if shipment.booking_date else ''},
            {'key': 'in_operation', 'label': 'In Operation', 'icon': 'fa-cogs',
             'date': shipment.gate_in_date.strftime('%Y-%m-%d') if shipment.gate_in_date else ''},
            {'key': 'in_transit', 'label': 'In Transit', 'icon': 'fa-ship',
             'date': shipment.sailing_date.strftime('%Y-%m-%d') if shipment.sailing_date else ''},
            {'key': 'arrived', 'label': 'Arrived', 'icon': 'fa-anchor',
             'date': shipment.arrival_date.strftime('%Y-%m-%d') if shipment.arrival_date else ''},
            {'key': 'customs_clearance', 'label': 'Customs', 'icon': 'fa-institution',
             'date': shipment.customs_clearance_date.strftime('%Y-%m-%d') if shipment.customs_clearance_date else ''},
            {'key': 'delivered', 'label': 'Delivered', 'icon': 'fa-check-circle',
             'date': shipment.delivery_date.strftime('%Y-%m-%d') if shipment.delivery_date else ''},
        ]

        state_order = ['draft', 'booked', 'in_operation', 'in_transit', 'arrived', 'customs_clearance',
                        'delivered', 'completed', 'invoiced']
        current_idx = state_order.index(shipment.state) if shipment.state in state_order else 0

        for i, stage in enumerate(stages):
            stage_idx = state_order.index(stage['key']) if stage['key'] in state_order else 99
            if stage_idx < current_idx:
                stage['status'] = 'completed'
            elif stage_idx == current_idx:
                stage['status'] = 'active'
            else:
                stage['status'] = 'pending'

        # Customs sub-stages
        customs_stages = []
        if shipment.customs_status:
            customs_order = ['pending', 'submitted', 'under_review', 'cleared', 'held', 'rejected']
            customs_labels = {
                'pending': 'Pending', 'submitted': 'Documents Submitted',
                'under_review': 'Under Review', 'cleared': 'Released',
                'held': 'Held', 'rejected': 'Rejected',
            }
            current_customs_idx = customs_order.index(shipment.customs_status) if shipment.customs_status in customs_order else 0

            for i, cs in enumerate(['submitted', 'under_review', 'cleared']):
                cs_idx = customs_order.index(cs)
                status = 'completed' if cs_idx < current_customs_idx else ('active' if cs_idx == current_customs_idx else 'pending')
                customs_stages.append({
                    'key': cs,
                    'label': customs_labels.get(cs, cs),
                    'status': status,
                })

        # Missing documents check
        required_docs = ['customs_declaration', 'packing_list', 'commercial_invoice']
        existing_docs = shipment.document_ids.mapped('document_type')
        missing_docs = [d for d in required_docs if d not in existing_docs]

        return {
            'success': True,
            'shipment': {
                'id': shipment.id,
                'name': shipment.name,
                'state': shipment.state,
                'origin': shipment.origin_port_id.name if shipment.origin_port_id else '',
                'destination': shipment.destination_port_id.name if shipment.destination_port_id else '',
                'service_type': shipment.service_type,
                'carrier': shipment.carrier_id.name if shipment.carrier_id else '',
                'vessel': shipment.vessel_name or '',
                'customs_status': shipment.customs_status or '',
                'customs_broker': shipment.customs_broker_id.name if shipment.customs_broker_id else '',
                'duty_amount': shipment.duty_amount or 0,
            },
            'stages': stages,
            'customs_stages': customs_stages,
            'missing_documents': missing_docs,
        }

    @http.route('/my/freight/api/shipment/<int:shipment_id>/messages', type='json', auth='user', website=True)
    def get_shipment_messages(self, shipment_id, **kw):
        """Get chat messages for a shipment."""
        partner = request.env.user.partner_id
        shipment = request.env['freight.shipment'].sudo().browse(shipment_id)

        if not shipment.exists() or shipment.partner_id.commercial_partner_id != partner.commercial_partner_id:
            return {'error': 'Shipment not found'}

        messages = request.env['mail.message'].sudo().search([
            ('res_id', '=', shipment_id),
            ('model', '=', 'freight.shipment'),
            ('message_type', 'in', ['comment', 'notification']),
        ], order='date asc', limit=50)

        msg_list = []
        for msg in messages:
            msg_list.append({
                'id': msg.id,
                'body': msg.body,
                'author': msg.author_id.name if msg.author_id else 'System',
                'date': msg.date.strftime('%Y-%m-%d %H:%M') if msg.date else '',
                'is_customer': msg.author_id.id == partner.id if msg.author_id else False,
            })

        return {'success': True, 'messages': msg_list}

    @http.route('/my/freight/api/shipment/<int:shipment_id>/message', type='json', auth='user', website=True)
    def post_shipment_message(self, shipment_id, message='', **kw):
        """Post a chat message on a shipment."""
        partner = request.env.user.partner_id
        shipment = request.env['freight.shipment'].sudo().browse(shipment_id)

        if not shipment.exists() or shipment.partner_id.commercial_partner_id != partner.commercial_partner_id:
            return {'error': 'Shipment not found'}

        if not message.strip():
            return {'error': 'Message cannot be empty'}

        shipment.message_post(
            body=message,
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
            author_id=partner.id,
        )

        return {'success': True}

    @http.route('/my/freight/api/quote/submit', type='json', auth='user', website=True)
    def submit_quote_ajax(self, **post):
        """Submit a quote request via AJAX (multi-step wizard)."""
        partner = request.env.user.partner_id

        def safe_float(value, default=0.0):
            try:
                return float(value) if value and str(value).strip() else default
            except (ValueError, AttributeError):
                return default

        def safe_int(value, default=0):
            try:
                return int(value) if value and str(value).strip() else default
            except (ValueError, AttributeError):
                return default

        # Validate required fields
        errors = []
        if not post.get('service_type'):
            errors.append('Service type is required')
        if not post.get('origin_port_id'):
            errors.append('Origin port is required')
        if not post.get('destination_port_id'):
            errors.append('Destination port is required')
        if not post.get('cargo_description'):
            errors.append('Cargo description is required')

        if errors:
            return {'error': ', '.join(errors)}

        try:
            quotation_vals = {
                'partner_id': partner.commercial_partner_id.id,
                'service_type': post.get('service_type', 'fcl'),
                'shipment_direction': post.get('shipment_direction', 'export'),
                'cargo_description': post.get('cargo_description', ''),
                'container_type': post.get('container_type') if post.get('service_type') == 'fcl' else False,
                'container_qty': safe_int(post.get('container_qty'), 1),
                'total_weight': safe_float(post.get('total_weight'), 0),
                'total_volume': safe_float(post.get('total_volume'), 0),
                'is_dangerous_goods': post.get('is_dangerous_goods', False),
                'is_temperature_controlled': post.get('is_temperature_controlled', False),
                'special_instructions': post.get('special_instructions', ''),
            }

            if post.get('origin_port_id'):
                quotation_vals['origin_port_id'] = safe_int(post.get('origin_port_id'))
            if post.get('destination_port_id'):
                quotation_vals['destination_port_id'] = safe_int(post.get('destination_port_id'))

            quotation = request.env['freight.quotation'].sudo().create(quotation_vals)

            # Add note about customs clearance request
            customs_note = ''
            if post.get('customs_clearance_required'):
                customs_note = '\n🏛 Customer requires customs clearance service.'
            if post.get('customs_notes'):
                customs_note += f'\nCustoms notes: {post.get("customs_notes")}'

            quotation.message_post(
                body=f"Quote request submitted via customer portal (wizard).{customs_note}",
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

            return {
                'success': True,
                'message': 'Your quote request has been submitted successfully!',
                'quotation_id': quotation.id,
                'quotation_name': quotation.name,
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/my/freight/api/locations', type='json', auth='user', website=True)
    def get_locations(self, **kw):
        """Get available locations for quote form."""
        locations = request.env['freight.location'].sudo().search([
            ('location_type', 'in', ['port', 'airport'])
        ], order='name')

        ports = []
        airports = []
        for loc in locations:
            data = {'id': loc.id, 'name': loc.name, 'code': loc.code or ''}
            if loc.location_type == 'port':
                ports.append(data)
            else:
                airports.append(data)

        return {'ports': ports, 'airports': airports, 'all': ports + airports}
