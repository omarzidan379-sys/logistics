# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta


class FreightDashboardController(http.Controller):

    @http.route('/freight/dashboard_data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        try:
            # Models
            Quotation = request.env['freight.quotation']
            Shipment = request.env['freight.shipment']
            Booking = request.env['freight.booking']
            Container = request.env['freight.container']

            # 1. KPI Stats
            today = datetime.now().date()
            month_start = today.replace(day=1)

            # Quotations
            draft_quotations = Quotation.search_count([('state', '=', 'draft')])
            sent_quotations = Quotation.search_count([('state', '=', 'sent')])
            approved_quotations = Quotation.search_count([('state', '=', 'approved')])
            
            # Calculate total quotation amount
            quotation_data = Quotation.search_read(
                [('state', 'in', ['sent', 'approved'])],
                ['total_amount']
            )
            total_quotation_value = sum(
                item.get('total_amount', 0) or 0 for item in quotation_data
            )

            # Shipments
            active_shipments = Shipment.search_count([('state', 'not in', ['delivered', 'cancelled'])])
            in_transit = Shipment.search_count([('state', '=', 'in_transit')])
            delivered_today = Shipment.search_count([('actual_delivery_date', '=', today)])
            
            # Bookings
            pending_bookings = Booking.search_count([('state', '=', 'confirmed')])
            
            # Containers
            active_containers = Container.search_count([('state', 'not in', ['returned', 'cancelled'])])
            containers_in_yard = Container.search_count([('state', '=', 'in_yard')])
            
            # Revenue (from confirmed bookings this month)
            monthly_revenue_data = Booking.search_read(
                [('create_date', '>=', month_start), ('state', '=', 'confirmed')],
                ['total_freight_cost']
            )
            monthly_revenue = sum(
                item.get('total_freight_cost', 0) or 0 for item in monthly_revenue_data
            )
            currency = request.env.company.currency_id.symbol or '$'

            # 2. Status Chart Data - Shipments by Status
            states = Shipment._fields['state'].selection
            status_labels = []
            status_values = []
            for state_code, state_label in states:
                count = Shipment.search_count([('state', '=', state_code)])
                if count > 0:
                    status_labels.append(state_label)
                    status_values.append(count)

            # 3. Monthly Chart Data (last 6 months of shipments)
            monthly_labels = []
            monthly_quotations = []
            monthly_shipments = []
            
            for i in range(5, -1, -1):
                month_date = datetime.now() - timedelta(days=i*30)
                month_name = month_date.strftime('%b')
                monthly_labels.append(month_name)
                
                month_start_calc = month_date.replace(day=1)
                month_end_calc = (month_start_calc + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                # Quotations created that month
                q_count = Quotation.search_count([
                    ('create_date', '>=', month_start_calc),
                    ('create_date', '<=', month_end_calc)
                ])
                monthly_quotations.append(q_count)
                
                # Shipments created that month
                s_count = Shipment.search_count([
                    ('create_date', '>=', month_start_calc),
                    ('create_date', '<=', month_end_calc)
                ])
                monthly_shipments.append(s_count)

            # 4. Recent Shipments Table
            recent_shipments = []
            records = Shipment.search([], limit=10, order='write_date desc')
            for rec in records:
                # Map state to progress %
                progress_map = {
                    'draft': 10,
                    'confirmed': 25,
                    'in_transit': 50,
                    'customs_hold': 60,
                    'at_destination': 75,
                    'out_for_delivery': 85,
                    'delivered': 100,
                    'cancelled': 0
                }
                
                # Calculate transport legs info
                leg_count = len(rec.transport_leg_ids) if rec.transport_leg_ids else 0
                completed_legs = len([leg for leg in rec.transport_leg_ids if leg.status == 'completed']) if rec.transport_leg_ids else 0
                
                recent_shipments.append({
                    'id': rec.id,
                    'name': rec.name,
                    'partner_name': rec.partner_id.name if rec.partner_id else 'N/A',
                    'origin': rec.origin_location_id.name if rec.origin_location_id else 'N/A',
                    'destination': rec.destination_location_id.name if rec.destination_location_id else 'N/A',
                    'state': rec.state,
                    'state_label': dict(states).get(rec.state, ''),
                    'progress': progress_map.get(rec.state, 0),
                    'shipment_date': rec.shipment_date.strftime('%Y-%m-%d') if rec.shipment_date else '',
                    'estimated_delivery': rec.estimated_delivery_date.strftime('%Y-%m-%d') if rec.estimated_delivery_date else '',
                    'legs': f"{completed_legs}/{leg_count}"
                })

            # 5. Notifications - Check for urgent items
            notifications = []
            
            # Shipments delayed (>7 days in transit without delivery)
            delayed_shipments = Shipment.search([
                ('state', 'in', ['in_transit', 'customs_hold']),
                ('expected_delivery_date', '<', today),
                ('expected_delivery_date', '!=', False)
            ], limit=5)
            
            for shipment in delayed_shipments:
                days_delayed = (today - shipment.expected_delivery_date).days
                notifications.append({
                    'type': 'delayed',
                    'title': f"Delayed: {shipment.name}",
                    'message': f"{shipment.partner_id.name} - {days_delayed} days overdue",
                    'id': shipment.id,
                    'icon': '🕐'
                })
            
            # Draft quotations older than 7 days
            old_drafts = Quotation.search([
                ('state', '=', 'draft'),
                ('create_date', '<', datetime.now() - timedelta(days=7))
            ], limit=3)
            
            for quote in old_drafts:
                notifications.append({
                    'type': 'urgent',
                    'title': f"Draft: {quote.name}",
                    'message': f"{quote.partner_id.name} - needs follow up",
                    'id': quote.id,
                    'icon': '⚠️'
                })

            return {
                'success': True,
                'stats': {
                    'draft_quotations': draft_quotations,
                    'sent_quotations': sent_quotations,
                    'approved_quotations': approved_quotations,
                    'total_quotation_value': f"{total_quotation_value:,.2f}",
                    'active_shipments': active_shipments,
                    'in_transit': in_transit,
                    'delivered_today': delivered_today,
                    'pending_bookings': pending_bookings,
                    'active_containers': active_containers,
                    'containers_in_yard': containers_in_yard,
                    'monthly_revenue': f"{monthly_revenue:,.2f}",
                    'currency': currency
                },
                'chart_data': {
                    'status': {
                        'labels': status_labels,
                        'values': status_values
                    },
                    'monthly': {
                        'labels': monthly_labels,
                        'quotations': monthly_quotations,
                        'shipments': monthly_shipments
                    }
                },
                'recent_shipments': recent_shipments,
                'notifications': notifications,
                'notification_count': len(notifications)
            }
            
        except Exception as e:
            # Return fallback data if models are not ready
            return {
                'success': False,
                'error': str(e),
                'stats': {
                    'draft_quotations': 0,
                    'sent_quotations': 0,
                    'approved_quotations': 0,
                    'total_quotation_value': "0.00",
                    'active_shipments': 0,
                    'in_transit': 0,
                    'delivered_today': 0,
                    'pending_bookings': 0,
                    'active_containers': 0,
                    'containers_in_yard': 0,
                    'monthly_revenue': "0.00",
                    'currency': '$'
                },
                'chart_data': {
                    'status': {
                        'labels': ['Draft', 'Confirmed', 'In Transit', 'Delivered'],
                        'values': [0, 0, 0, 0]
                    },
                    'monthly': {
                        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                        'quotations': [0, 0, 0, 0, 0, 0],
                        'shipments': [0, 0, 0, 0, 0, 0]
                    }
                },
                'recent_shipments': [],
                'notifications': [],
                'notification_count': 0
            }
