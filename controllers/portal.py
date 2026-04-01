# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.tools import groupby as groupbyelem
from operator import itemgetter


class FreightCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        if 'shipment_count' in counters:
            values['shipment_count'] = request.env['freight.shipment'].search_count([
                ('partner_id', 'child_of', partner.commercial_partner_id.id)
            ]) if request.env['freight.shipment'].check_access_rights('read', raise_exception=False) else 0

        if 'quotation_count' in counters:
            values['quotation_count'] = request.env['freight.quotation'].search_count([
                ('partner_id', 'child_of', partner.commercial_partner_id.id)
            ]) if request.env['freight.quotation'].check_access_rights('read', raise_exception=False) else 0

        if 'booking_count' in counters:
            values['booking_count'] = request.env['freight.booking'].search_count([
                ('partner_id', 'child_of', partner.commercial_partner_id.id)
            ]) if request.env['freight.booking'].check_access_rights('read', raise_exception=False) else 0

        return values

    # Shipments Portal
    @http.route(['/my/shipments', '/my/shipments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_shipments(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        Shipment = request.env['freight.shipment']
        partner = request.env.user.partner_id

        domain = [('partner_id', 'child_of', partner.commercial_partner_id.id)]

        searchbar_sortings = {
            'date': {'label': _('Booking Date'), 'order': 'booking_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'status': {'label': _('Status'), 'order': 'state'},
        }

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'confirmed': {'label': _('Confirmed'), 'domain': [('state', '=', 'confirmed')]},
            'in_transit': {'label': _('In Transit'), 'domain': [('state', '=', 'in_transit')]},
            'delivered': {'label': _('Delivered'), 'domain': [('state', '=', 'delivered')]},
        }

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        shipment_count = Shipment.search_count(domain)
        pager = portal_pager(
            url="/my/shipments",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=shipment_count,
            page=page,
            step=self._items_per_page
        )

        shipments = Shipment.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_shipments_history'] = shipments.ids[:100]

        values.update({
            'date': date_begin,
            'shipments': shipments,
            'page_name': 'shipment',
            'pager': pager,
            'default_url': '/my/shipments',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
        })
        return request.render("freight_management.portal_my_shipments", values)

    @http.route(['/my/shipments/<int:shipment_id>'], type='http', auth="user", website=True)
    def portal_my_shipment_detail(self, shipment_id, access_token=None, **kw):
        try:
            shipment_sudo = self._document_check_access('freight.shipment', shipment_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'shipment': shipment_sudo,
            'page_name': 'shipment',
        }
        return request.render("freight_management.portal_my_shipment_detail", values)

    # Quotations Portal
    @http.route(['/my/quotations', '/my/quotations/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotations(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        Quotation = request.env['freight.quotation']
        partner = request.env.user.partner_id

        domain = [('partner_id', 'child_of', partner.commercial_partner_id.id)]

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'quotation_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'validity': {'label': _('Valid Until'), 'order': 'validity_date desc'},
        }

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'sent': {'label': _('Sent'), 'domain': [('state', '=', 'sent')]},
            'confirmed': {'label': _('Confirmed'), 'domain': [('state', '=', 'confirmed')]},
        }

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        quotation_count = Quotation.search_count(domain)
        pager = portal_pager(
            url="/my/quotations",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )

        quotations = Quotation.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'quotations': quotations,
            'page_name': 'quotation',
            'pager': pager,
            'default_url': '/my/quotations',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
        })
        return request.render("freight_management.portal_my_quotations", values)

    @http.route(['/my/quotations/<int:quotation_id>'], type='http', auth="user", website=True)
    def portal_my_quotation_detail(self, quotation_id, access_token=None, **kw):
        try:
            quotation_sudo = self._document_check_access('freight.quotation', quotation_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'quotation': quotation_sudo,
            'page_name': 'quotation',
        }
        return request.render("freight_management.portal_my_quotation_detail", values)

    @http.route(['/my/quotations/<int:quotation_id>/accept'], type='http', auth="user", website=True)
    def portal_quotation_accept(self, quotation_id, access_token=None, **kw):
        try:
            quotation_sudo = self._document_check_access('freight.quotation', quotation_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if quotation_sudo.state == 'sent':
            quotation_sudo.action_confirm()

        return request.redirect('/my/quotations/%s?message=accepted' % quotation_id)

    @http.route(['/my/quotations/<int:quotation_id>/reject'], type='http', auth="user", website=True)
    def portal_quotation_reject(self, quotation_id, access_token=None, reason=None, **kw):
        try:
            quotation_sudo = self._document_check_access('freight.quotation', quotation_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if quotation_sudo.state == 'sent':
            quotation_sudo.action_cancel()
            if reason:
                quotation_sudo.message_post(
                    body=f"Customer rejected quotation. Reason: {reason}",
                    message_type='comment',
                    subtype_xmlid='mail.mt_note'
                )

        return request.redirect('/my/quotations/%s?message=rejected' % quotation_id)

    @http.route(['/my/quotations/<int:quotation_id>/download'], type='http', auth="user", website=True)
    def portal_quotation_download(self, quotation_id, access_token=None, **kw):
        try:
            quotation_sudo = self._document_check_access('freight.quotation', quotation_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # Generate PDF report
        pdf = request.env.ref('freight_management.action_report_freight_quotation').sudo()._render_qweb_pdf([quotation_id])[0]
        
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment; filename="Quotation_%s.pdf"' % quotation_sudo.name)
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

    # Bookings Portal
    @http.route(['/my/bookings', '/my/bookings/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_bookings(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Booking = request.env['freight.booking']
        partner = request.env.user.partner_id

        domain = [('partner_id', 'child_of', partner.commercial_partner_id.id)]

        searchbar_sortings = {
            'date': {'label': _('Booking Date'), 'order': 'booking_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
        }

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        booking_count = Booking.search_count(domain)
        pager = portal_pager(
            url="/my/bookings",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=booking_count,
            page=page,
            step=self._items_per_page
        )

        bookings = Booking.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'bookings': bookings,
            'page_name': 'booking',
            'pager': pager,
            'default_url': '/my/bookings',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("freight_management.portal_my_bookings", values)

    @http.route(['/my/bookings/<int:booking_id>'], type='http', auth="user", website=True)
    def portal_my_booking_detail(self, booking_id, access_token=None, **kw):
        try:
            booking_sudo = self._document_check_access('freight.booking', booking_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'booking': booking_sudo,
            'page_name': 'booking',
        }
        return request.render("freight_management.portal_my_booking_detail", values)

    @http.route(['/my/bookings/<int:booking_id>/cancel'], type='http', auth="user", website=True)
    def portal_booking_cancel(self, booking_id, access_token=None, reason=None, **kw):
        try:
            booking_sudo = self._document_check_access('freight.booking', booking_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if booking_sudo.state in ['draft', 'confirmed']:
            booking_sudo.action_cancel()
            if reason:
                booking_sudo.message_post(
                    body=f"Customer cancelled booking. Reason: {reason}",
                    message_type='comment',
                    subtype_xmlid='mail.mt_note'
                )

        return request.redirect('/my/bookings/%s?message=cancelled' % booking_id)

    # Document Download
    @http.route(['/my/shipments/<int:shipment_id>/document/<int:document_id>/download'], type='http', auth="user", website=True)
    def portal_shipment_document_download(self, shipment_id, document_id, access_token=None, **kw):
        try:
            shipment_sudo = self._document_check_access('freight.shipment', shipment_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        document = request.env['freight.shipment.document'].sudo().browse(document_id)
        if document.shipment_id.id != shipment_id:
            return request.redirect('/my')

        if not document.document_file:
            return request.redirect('/my/shipments/%s' % shipment_id)

        return request.make_response(
            document.document_file,
            headers=[
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', 'attachment; filename=%s' % document.document_name)
            ]
        )

    # Notification Preferences
    @http.route(['/my/freight/settings'], type='http', auth="user", website=True)
    def portal_freight_settings(self, **kw):
        partner = request.env.user.partner_id
        preference = request.env['freight.notification.preference'].sudo().get_or_create_preference(partner.id)
        
        values = {
            'preference': preference,
            'page_name': 'freight_settings',
        }
        return request.render("freight_management.portal_freight_settings", values)

    @http.route(['/my/freight/settings/save'], type='http', auth="user", website=True, methods=['POST'], csrf=False)
    def portal_freight_settings_save(self, **post):
        partner = request.env.user.partner_id
        preference = request.env['freight.notification.preference'].sudo().get_or_create_preference(partner.id)
        
        # Update preferences
        preference.sudo().write({
            'notify_quotation_sent': post.get('notify_quotation_sent') == 'on',
            'notify_booking_confirmed': post.get('notify_booking_confirmed') == 'on',
            'notify_shipment_booked': post.get('notify_shipment_booked') == 'on',
            'notify_shipment_departed': post.get('notify_shipment_departed') == 'on',
            'notify_shipment_in_transit': post.get('notify_shipment_in_transit') == 'on',
            'notify_shipment_arrived': post.get('notify_shipment_arrived') == 'on',
            'notify_shipment_delivered': post.get('notify_shipment_delivered') == 'on',
            'notify_document_uploaded': post.get('notify_document_uploaded') == 'on',
            'digest_frequency': post.get('digest_frequency', 'realtime'),
        })
        
        return request.redirect('/my/freight/settings?saved=1')

    @http.route(['/my/shipments/<int:shipment_id>/message'], type='http', auth="user", website=True, methods=['POST'], csrf=False)
    def portal_shipment_message(self, shipment_id, message=None, access_token=None, **kw):
        try:
            shipment_sudo = self._document_check_access('freight.shipment', shipment_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if message:
            shipment_sudo.message_post(
                body=message,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
                author_id=request.env.user.partner_id.id
            )

        return request.redirect('/my/shipments/%s?message=sent' % shipment_id)

    @http.route(['/my/shipments/<int:shipment_id>/request_document'], type='json', auth="user", website=True)
    def portal_shipment_request_document(self, shipment_id, document_type=None, notes=None, **kw):
        try:
            shipment_sudo = self._document_check_access('freight.shipment', shipment_id, access_token=None)
        except (AccessError, MissingError):
            return {'error': 'Access denied'}

        if document_type:
            message = f"Customer requested document: {document_type}"
            if notes:
                message += f"\nNotes: {notes}"
            
            shipment_sudo.message_post(
                body=message,
                message_type='comment',
                subtype_xmlid='mail.mt_note',
                author_id=request.env.user.partner_id.id
            )
            
            return {'success': True, 'message': 'Document request submitted successfully'}
        
        return {'error': 'Document type is required'}
