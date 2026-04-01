# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FreightRate(models.Model):
    _name = 'freight.rate'
    _description = 'Freight Rate'
    _order = 'valid_from desc, name'

    name = fields.Char(string='Rate Name', required=True)
    origin_port_id = fields.Many2one('freight.location', string='Origin Port', required=True, 
                                      domain=[('location_type', 'in', ['port', 'airport'])])
    destination_port_id = fields.Many2one('freight.location', string='Destination Port', required=True,
                                          domain=[('location_type', 'in', ['port', 'airport'])])
    carrier_id = fields.Many2one('res.partner', string='Carrier', required=True,
                                  domain=[('is_carrier', '=', True)])
    service_type = fields.Selection([
        ('fcl', 'FCL (Full Container Load)'),
        ('lcl', 'LCL (Less than Container Load)'),
        ('air', 'Air Freight'),
        ('road', 'Road Transport'),
        ('rail', 'Rail Transport')
    ], string='Service Type', required=True, default='fcl')
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
    rate_amount = fields.Monetary(string='Rate Amount', required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                   default=lambda self: self.env.company.currency_id)
    valid_from = fields.Date(string='Valid From', required=True, default=fields.Date.today)
    valid_to = fields.Date(string='Valid To', required=True)
    rate_type = fields.Selection([
        ('standard', 'Standard Rate'),
        ('contract', 'Contract Rate'),
        ('spot', 'Spot Rate')
    ], string='Rate Type', required=True, default='standard')
    transit_time_days = fields.Integer(string='Transit Time (Days)')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    
    @api.constrains('valid_from', 'valid_to')
    def _check_validity_dates(self):
        for record in self:
            if record.valid_to < record.valid_from:
                raise ValidationError('Valid To date must be after Valid From date.')
    
    def name_get(self):
        result = []
        for record in self:
            name = f'{record.origin_port_id.code} → {record.destination_port_id.code} ({record.carrier_id.name})'
            result.append((record.id, name))
        return result

    @api.model
    def calculate_freight_rate(self, origin_id, destination_id, service_type, container_type=None, weight=0, volume=0):
        """Calculate freight rate based on parameters"""
        domain = [
            ('origin_port_id', '=', origin_id),
            ('destination_port_id', '=', destination_id),
            ('service_type', '=', service_type),
            ('valid_from', '<=', fields.Date.today()),
            ('valid_to', '>=', fields.Date.today()),
            ('active', '=', True),
        ]
        
        if container_type:
            domain.append(('container_type', '=', container_type))
        
        rates = self.search(domain, order='rate_amount asc', limit=1)
        
        if not rates:
            return {
                'success': False,
                'message': 'No rates found for the selected route and service type',
            }
        
        rate = rates[0]
        base_amount = rate.rate_amount
        
        # Calculate surcharges
        surcharges = self.env['freight.surcharge'].search([
            ('carrier_id', '=', rate.carrier_id.id),
            ('service_type', 'in', [service_type, 'all']),
            ('valid_from', '<=', fields.Date.today()),
            ('valid_to', '>=', fields.Date.today()),
            ('active', '=', True),
        ])
        
        surcharge_amount = 0
        for surcharge in surcharges:
            if surcharge.calculation_method == 'fixed':
                surcharge_amount += surcharge.amount
            else:
                surcharge_amount += (base_amount * surcharge.percentage / 100)
        
        total_amount = base_amount + surcharge_amount
        
        return {
            'success': True,
            'base_amount': base_amount,
            'surcharge_amount': surcharge_amount,
            'total_amount': total_amount,
            'currency': rate.currency_id.name,
            'transit_time_days': rate.transit_time_days,
            'carrier': rate.carrier_id.name,
        }
