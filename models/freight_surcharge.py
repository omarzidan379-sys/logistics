# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FreightSurcharge(models.Model):
    _name = 'freight.surcharge'
    _description = 'Freight Surcharge'
    _order = 'name'

    name = fields.Char(string='Surcharge Name', required=True)
    surcharge_type = fields.Selection([
        ('fuel', 'Fuel Surcharge (BAF/CAF)'),
        ('security', 'Security Surcharge'),
        ('peak_season', 'Peak Season Surcharge'),
        ('war_risk', 'War Risk Surcharge'),
        ('congestion', 'Port Congestion Surcharge'),
        ('currency', 'Currency Adjustment Factor'),
        ('other', 'Other')
    ], string='Surcharge Type', required=True, default='fuel')
    carrier_id = fields.Many2one('res.partner', string='Carrier',
                                  domain=[('is_carrier', '=', True)])
    calculation_method = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Base Rate')
    ], string='Calculation Method', required=True, default='fixed')
    amount = fields.Monetary(string='Amount', currency_field='currency_id')
    percentage = fields.Float(string='Percentage (%)', digits=(5, 2))
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                   default=lambda self: self.env.company.currency_id)
    valid_from = fields.Date(string='Valid From', required=True, default=fields.Date.today)
    valid_to = fields.Date(string='Valid To', required=True)
    service_type = fields.Selection([
        ('fcl', 'FCL'),
        ('lcl', 'LCL'),
        ('air', 'Air'),
        ('road', 'Road'),
        ('rail', 'Rail'),
        ('all', 'All Services')
    ], string='Applicable To', default='all')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
