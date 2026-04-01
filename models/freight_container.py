# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta

class FreightContainer(models.Model):
    _name = 'freight.container'
    _description = 'Freight Container'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Container Number', required=True, tracking=True)
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
    ], string='Container Type', required=True, tracking=True)
    size = fields.Selection([
        ('20', "20'"),
        ('40', "40'"),
        ('45', "45'")
    ], string='Size', compute='_compute_size', store=True)
    owner = fields.Selection([
        ('soc', 'SOC (Shipper Owned Container)'),
        ('coc', 'COC (Carrier Owned Container)')
    ], string='Owner', default='coc', tracking=True)
    
    # State Management
    state = fields.Selection([
        ('available', 'Available'),
        ('allocated', 'Allocated'),
        ('gate_in', 'Gate In'),
        ('loaded', 'Loaded'),
        ('in_transit', 'In Transit'),
        ('discharged', 'Discharged'),
        ('gate_out', 'Gate Out'),
        ('returned', 'Returned')
    ], string='Status', default='available', required=True, tracking=True)
    
    # Tracking Information
    booking_id = fields.Many2one('freight.booking', string='Booking', tracking=True)
    shipment_id = fields.Many2one('freight.shipment', string='Shipment', tracking=True)
    seal_number = fields.Char(string='Seal Number', tracking=True)
    vgm_weight = fields.Float(string='VGM Weight (KG)', digits=(12, 2), 
                              help='Verified Gross Mass', tracking=True)
    
    # Empty Return Tracking
    return_depot_id = fields.Many2one('freight.location', string='Return Depot',
                                      domain=[('location_type', '=', 'warehouse')],
                                      help='Depot where empty container should be returned')
    is_empty_returned = fields.Boolean(string='Empty Returned', default=False,
                                       compute='_compute_empty_returned', store=True)
    
    @api.depends('state', 'return_date', 'return_depot_id')
    def _compute_empty_returned(self):
        for record in self:
            record.is_empty_returned = (record.state == 'returned' and 
                                        bool(record.return_date) and 
                                        bool(record.return_depot_id))
    
    # Date Tracking
    gate_in_date = fields.Datetime(string='Gate In Date', tracking=True)
    gate_out_date = fields.Datetime(string='Gate Out Date', tracking=True)
    return_date = fields.Datetime(string='Return Date', tracking=True)
    
    # Condition
    condition = fields.Selection([
        ('good', 'Good Condition'),
        ('damaged', 'Damaged')
    ], string='Condition', default='good', tracking=True)
    damage_description = fields.Text(string='Damage Description')
    damage_photos = fields.Binary(string='Damage Photos', attachment=True)
    
    # Demurrage & Detention
    free_time_days = fields.Integer(string='Free Time (Days)', default=7)
    free_time_expiry_date = fields.Date(string='Free Time Expiry', compute='_compute_free_time_expiry',
                                         store=True)
    demurrage_days = fields.Integer(string='Demurrage Days', compute='_compute_demurrage', store=True)
    demurrage_amount = fields.Monetary(string='Demurrage Amount', compute='_compute_demurrage',
                                        store=True, currency_field='currency_id')
    detention_days = fields.Integer(string='Detention Days', compute='_compute_detention', store=True)
    detention_amount = fields.Monetary(string='Detention Amount', compute='_compute_detention',
                                        store=True, currency_field='currency_id')
    demurrage_rate = fields.Monetary(string='Demurrage Rate/Day', currency_field='currency_id')
    detention_rate = fields.Monetary(string='Detention Rate/Day', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                   default=lambda self: self.env.company.currency_id)
    
    # Additional Info
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                  default=lambda self: self.env.company)
    
    @api.depends('container_type')
    def _compute_size(self):
        for record in self:
            if record.container_type:
                if record.container_type.startswith('20'):
                    record.size = '20'
                elif record.container_type.startswith('45'):
                    record.size = '45'
                else:
                    record.size = '40'
            else:
                record.size = False
    
    @api.depends('gate_in_date', 'free_time_days')
    def _compute_free_time_expiry(self):
        for record in self:
            if record.gate_in_date and record.free_time_days:
                record.free_time_expiry_date = (record.gate_in_date + timedelta(days=record.free_time_days)).date()
            else:
                record.free_time_expiry_date = False
    
    @api.depends('gate_in_date', 'gate_out_date', 'free_time_expiry_date', 'demurrage_rate')
    def _compute_demurrage(self):
        for record in self:
            if record.gate_in_date and record.gate_out_date and record.free_time_expiry_date:
                gate_out_date = record.gate_out_date.date()
                if gate_out_date > record.free_time_expiry_date:
                    record.demurrage_days = (gate_out_date - record.free_time_expiry_date).days
                    record.demurrage_amount = record.demurrage_days * (record.demurrage_rate or 0)
                else:
                    record.demurrage_days = 0
                    record.demurrage_amount = 0
            else:
                record.demurrage_days = 0
                record.demurrage_amount = 0
    
    @api.depends('gate_out_date', 'return_date', 'free_time_days', 'detention_rate')
    def _compute_detention(self):
        for record in self:
            if record.gate_out_date and record.return_date:
                days_out = (record.return_date.date() - record.gate_out_date.date()).days
                if days_out > record.free_time_days:
                    record.detention_days = days_out - record.free_time_days
                    record.detention_amount = record.detention_days * (record.detention_rate or 0)
                else:
                    record.detention_days = 0
                    record.detention_amount = 0
            else:
                record.detention_days = 0
                record.detention_amount = 0
    
    def action_gate_in(self):
        self.ensure_one()
        self.write({
            'state': 'gate_in',
            'gate_in_date': fields.Datetime.now()
        })
        return True
    
    def action_gate_out(self):
        self.ensure_one()
        self.write({
            'state': 'gate_out',
            'gate_out_date': fields.Datetime.now()
        })
        return True
    
    def action_return(self):
        self.ensure_one()
        
        if not self.return_depot_id:
            raise ValidationError('Please specify the return depot location before marking container as returned.')
        
        self.write({
            'state': 'returned',
            'return_date': fields.Datetime.now()
        })
        
        # After return, make container available again
        self.write({
            'state': 'available',
            'booking_id': False,
            'shipment_id': False,
            'seal_number': False,
        })
        
        return True

    def get_demurrage_info(self):
        """Get detailed demurrage information for container"""
        self.ensure_one()
        
        return {
            'container_number': self.name,
            'free_time_days': self.free_time_days,
            'free_time_expiry': self.free_time_expiry_date,
            'demurrage_days': self.demurrage_days,
            'demurrage_amount': self.demurrage_amount,
            'demurrage_rate': self.demurrage_rate,
            'detention_days': self.detention_days,
            'detention_amount': self.detention_amount,
            'detention_rate': self.detention_rate,
            'gate_in_date': self.gate_in_date,
            'gate_out_date': self.gate_out_date,
            'return_date': self.return_date,
        }
