# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Freight-specific partner types
    is_carrier = fields.Boolean('Is Carrier', help='Check if this partner is a shipping carrier')
    is_shipper = fields.Boolean('Is Shipper', help='Check if this partner is a shipper')
    is_consignee = fields.Boolean('Is Consignee', help='Check if this partner is a consignee')
    is_agent = fields.Boolean('Is Agent', help='Check if this partner is a freight agent')
    is_customs_broker = fields.Boolean('Is Customs Broker', help='Check if this partner is a customs broker')
    is_insurance_company = fields.Boolean('Is Insurance Company', help='Check if this partner is an insurance company')
    
    # Freight-specific fields
    freight_customer_code = fields.Char('Customer Code', help='Internal customer code for freight operations')
    credit_limit = fields.Monetary('Credit Limit', currency_field='currency_id')
    
    # Carrier Performance Metrics
    carrier_on_time_rate = fields.Float('On-Time Delivery %', compute='_compute_carrier_performance',
                                        digits=(5, 2), help='Percentage of on-time deliveries')
    carrier_total_legs = fields.Integer('Total Legs Completed', compute='_compute_carrier_performance')
    carrier_rating = fields.Selection([
        ('1', '⭐ Poor'),
        ('2', '⭐⭐ Fair'),
        ('3', '⭐⭐⭐ Good'),
        ('4', '⭐⭐⭐⭐ Very Good'),
        ('5', '⭐⭐⭐⭐⭐ Excellent')
    ], string='Carrier Rating', compute='_compute_carrier_performance')
    
    def _compute_carrier_performance(self):
        """Calculate carrier performance metrics"""
        for partner in self:
            if partner.is_carrier:
                completed_legs = self.env['freight.transport.leg'].search([
                    ('carrier_id', '=', partner.id),
                    ('state', '=', 'completed'),
                    ('actual_arrival', '!=', False)
                ])
                
                partner.carrier_total_legs = len(completed_legs)
                
                if completed_legs:
                    on_time_legs = completed_legs.filtered('is_on_time')
                    partner.carrier_on_time_rate = (len(on_time_legs) / len(completed_legs)) * 100
                    
                    # Auto-rate based on performance
                    if partner.carrier_on_time_rate >= 95:
                        partner.carrier_rating = '5'
                    elif partner.carrier_on_time_rate >= 85:
                        partner.carrier_rating = '4'
                    elif partner.carrier_on_time_rate >= 75:
                        partner.carrier_rating = '3'
                    elif partner.carrier_on_time_rate >= 60:
                        partner.carrier_rating = '2'
                    else:
                        partner.carrier_rating = '1'
                else:
                    partner.carrier_on_time_rate = 0
                    partner.carrier_rating = False
            else:
                partner.carrier_on_time_rate = 0
                partner.carrier_total_legs = 0
                partner.carrier_rating = False
    
    # Customs broker specific
    broker_license_number = fields.Char('Broker License Number')
    broker_license_expiry = fields.Date('License Expiry Date')
