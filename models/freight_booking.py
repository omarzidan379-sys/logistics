# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class FreightBooking(models.Model):
    _name = 'freight.booking'
    _description = 'Freight Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'create_date desc, name desc'

    name = fields.Char(string='Booking Number', required=True, copy=False, readonly=True,
                       default=lambda self: 'New')
    quotation_id = fields.Many2one('freight.quotation', string='Quotation', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    booking_date = fields.Date(string='Booking Date', required=True, default=fields.Date.today,
                                tracking=True)
    
    # Service Details
    service_type = fields.Selection([
        ('fcl', 'FCL (Full Container Load)'),
        ('lcl', 'LCL (Less than Container Load)'),
        ('air', 'Air Freight'),
        ('road', 'Road Transport'),
        ('rail', 'Rail Transport')
    ], string='Service Type', required=True, default='fcl', tracking=True)
    carrier_id = fields.Many2one('res.partner', string='Carrier', required=True,
                                  domain=[('is_carrier', '=', True)], tracking=True)
    
    # Vessel/Flight Information
    vessel_name = fields.Char(string='Vessel/Flight Name', tracking=True)
    voyage_number = fields.Char(string='Voyage/Flight Number', tracking=True)
    booking_reference = fields.Char(string='Carrier Booking Reference', tracking=True)
    
    # Schedule
    etd = fields.Datetime(string='ETD (Estimated Time of Departure)', required=True, tracking=True)
    eta = fields.Datetime(string='ETA (Estimated Time of Arrival)', required=True, tracking=True)
    
    # Container Details
    container_type = fields.Selection([
        ('20gp', "20' GP"),
        ('40gp', "40' GP"),
        ('40hc', "40' HC"),
        ('45hc', "45' HC"),
        ('20rf', "20' Reefer"),
        ('40rf', "40' Reefer"),
        ('20ot', "20' Open Top"),
        ('40ot', "40' Open Top"),
        ('20fr', "20' Flat Rack"),
        ('40fr', "40' Flat Rack")
    ], string='Container Type')
    container_qty = fields.Integer(string='Container Quantity', default=1)
    teu = fields.Float(string='TEU', compute='_compute_teu', store=True, digits=(12, 2))
    
    # Free Time and Charges
    free_time_days = fields.Integer(string='Free Time (Days)', default=7)
    demurrage_rate = fields.Monetary(string='Demurrage Rate/Day', currency_field='currency_id')
    detention_rate = fields.Monetary(string='Detention Rate/Day', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                   default=lambda self: self.env.company.currency_id)
    
    # State Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('allocated', 'Containers Allocated'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Relations
    container_ids = fields.One2many('freight.container', 'booking_id', string='Containers')
    shipment_ids = fields.One2many('freight.shipment', 'booking_id', string='Shipments')
    
    # Additional Info
    notes = fields.Text(string='Notes')
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user,
                              tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                  default=lambda self: self.env.company)
    
    # Smart Buttons
    container_count = fields.Integer(string='Containers', compute='_compute_container_count')
    shipment_count = fields.Integer(string='Shipments', compute='_compute_shipment_count')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('freight.booking') or 'New'
        return super(FreightBooking, self).create(vals)
    
    @api.depends('container_type', 'container_qty')
    def _compute_teu(self):
        teu_mapping = {
            '20gp': 1.0, '20rf': 1.0, '20ot': 1.0, '20fr': 1.0,
            '40gp': 2.0, '40hc': 2.0, '40rf': 2.0, '40ot': 2.0, '40fr': 2.0,
            '45hc': 2.25
        }
        for record in self:
            record.teu = teu_mapping.get(record.container_type, 0) * record.container_qty
    
    def _compute_container_count(self):
        for record in self:
            record.container_count = len(record.container_ids)
    
    def _compute_shipment_count(self):
        for record in self:
            record.shipment_count = len(record.shipment_ids)
    
    @api.constrains('etd', 'eta')
    def _check_dates(self):
        for record in self:
            if record.eta < record.etd:
                raise ValidationError('ETA must be after ETD.')
            if record.etd < fields.Datetime.now():
                raise ValidationError('ETD cannot be in the past.')
    
    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'
        self._send_confirmation_email()
        return True
    
    def _send_confirmation_email(self):
        """Send booking confirmation email to customer"""
        self.ensure_one()
        template = self.env.ref('freight_management.email_template_booking_confirmed', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        return True
    
    def _get_portal_return_action(self):
        """Return action for portal"""
        return {
            'type': 'ir.actions.act_url',
            'url': '/my/bookings/%s' % self.id,
            'target': 'self',
        }
    
    # Portal-specific fields
    origin_location_id = fields.Many2one('freight.location', string='Origin Location', 
                                         related='quotation_id.origin_port_id', store=True, readonly=True)
    destination_location_id = fields.Many2one('freight.location', string='Destination Location',
                                              related='quotation_id.destination_port_id', store=True, readonly=True)
    
    def action_allocate_containers(self):
        self.ensure_one()
        if not self.container_qty:
            raise ValidationError('Please specify container quantity.')
        
        # Check container availability
        available_containers = self.env['freight.container'].search_count([
            ('container_type', '=', self.container_type),
            ('state', '=', 'available'),
            ('company_id', '=', self.company_id.id)
        ])
        
        if available_containers < self.container_qty:
            raise ValidationError(
                f'Insufficient containers available. '
                f'Requested: {self.container_qty}, Available: {available_containers}. '
                f'Please check container inventory or use SOC (Shipper Owned Containers).'
            )
        
        # Allocate available containers
        Container = self.env['freight.container']
        available = Container.search([
            ('container_type', '=', self.container_type),
            ('state', '=', 'available'),
            ('company_id', '=', self.company_id.id)
        ], limit=self.container_qty)
        
        for container in available:
            container.write({
                'booking_id': self.id,
                'state': 'allocated',
            })
        
        self.state = 'allocated'
        return True
    
    def action_create_shipment(self):
        self.ensure_one()
        shipment = self.env['freight.shipment'].create({
            'booking_id': self.id,
            'quotation_id': self.quotation_id.id if self.quotation_id else False,
            'partner_id': self.partner_id.id,
            'service_type': self.service_type,
            'carrier_id': self.carrier_id.id,
            'vessel_name': self.vessel_name,
            'voyage_number': self.voyage_number,
        })
        
        return {
            'name': 'Shipment',
            'type': 'ir.actions.act_window',
            'res_model': 'freight.shipment',
            'view_mode': 'form',
            'res_id': shipment.id,
            'target': 'current',
        }
    
    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'
        return True
    
    def action_view_containers(self):
        self.ensure_one()
        return {
            'name': 'Containers',
            'type': 'ir.actions.act_window',
            'res_model': 'freight.container',
            'view_mode': 'tree,form',
            'domain': [('booking_id', '=', self.id)],
            'context': {'default_booking_id': self.id}
        }
    
    def action_view_shipments(self):
        self.ensure_one()
        return {
            'name': 'Shipments',
            'type': 'ir.actions.act_window',
            'res_model': 'freight.shipment',
            'view_mode': 'tree,form',
            'domain': [('booking_id', '=', self.id)],
            'context': {'default_booking_id': self.id}
        }

    @api.model
    def create_from_wizard(self, quotation_id, carrier_id, vessel_name, voyage_number, 
                          booking_reference, etd, eta, container_qty):
        """Create booking from wizard data"""
        quotation = self.env['freight.quotation'].browse(quotation_id)
        
        vals = {
            'quotation_id': quotation_id,
            'partner_id': quotation.partner_id.id,
            'booking_date': fields.Date.today(),
            'service_type': quotation.service_type,
            'carrier_id': carrier_id,
            'vessel_name': vessel_name,
            'voyage_number': voyage_number,
            'booking_reference': booking_reference,
            'etd': etd,
            'eta': eta,
            'container_type': quotation.container_type,
            'container_qty': container_qty,
            'state': 'draft',
        }
        
        booking = self.create(vals)
        return booking.id
