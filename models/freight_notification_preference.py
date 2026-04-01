# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FreightNotificationPreference(models.Model):
    _name = 'freight.notification.preference'
    _description = 'Freight Notification Preferences'
    
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, ondelete='cascade')
    
    # Email Notifications
    notify_quotation_sent = fields.Boolean(string='Quotation Sent', default=True)
    notify_booking_confirmed = fields.Boolean(string='Booking Confirmed', default=True)
    notify_shipment_booked = fields.Boolean(string='Shipment Booked', default=True)
    notify_shipment_departed = fields.Boolean(string='Shipment Departed', default=True)
    notify_shipment_in_transit = fields.Boolean(string='Shipment In Transit', default=True)
    notify_shipment_arrived = fields.Boolean(string='Shipment Arrived', default=True)
    notify_shipment_delivered = fields.Boolean(string='Shipment Delivered', default=True)
    notify_document_uploaded = fields.Boolean(string='Document Uploaded', default=True)
    
    # SMS Notifications (if SMS module is installed)
    sms_shipment_departed = fields.Boolean(string='SMS: Shipment Departed', default=False)
    sms_shipment_delivered = fields.Boolean(string='SMS: Shipment Delivered', default=False)
    
    # Notification Frequency
    digest_frequency = fields.Selection([
        ('realtime', 'Real-time'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
    ], string='Notification Frequency', default='realtime')
    
    company_id = fields.Many2one('res.company', string='Company', 
                                  default=lambda self: self.env.company)
    
    @api.model
    def get_or_create_preference(self, partner_id):
        """Get or create notification preference for partner"""
        preference = self.search([('partner_id', '=', partner_id)], limit=1)
        if not preference:
            preference = self.create({'partner_id': partner_id})
        return preference
    
    def should_notify(self, notification_type):
        """Check if notification should be sent"""
        self.ensure_one()
        field_name = f'notify_{notification_type}'
        return getattr(self, field_name, False)
