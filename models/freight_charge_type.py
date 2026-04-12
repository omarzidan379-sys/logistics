# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FreightChargeType(models.Model):
    _name = 'freight.charge.type'
    _description = 'Freight Charge Type'
    _order = 'sequence, name'

    name = fields.Char(string='Charge Name', required=True, translate=True)
    code = fields.Char(string='Charge Code', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    charge_category = fields.Selection([
        ('freight', 'Freight Charge'),
        ('surcharge', 'Surcharge'),
        ('handling', 'Handling Charge'),
        ('documentation', 'Documentation Fee'),
        ('customs', 'Customs Charge'),
        ('storage', 'Storage Charge'),
        ('other', 'Other')
    ], string='Charge Category', required=True, default='freight')
    description = fields.Text(string='Description', translate=True)
    active = fields.Boolean(string='Active', default=True)
    
    # Default pricing for auto-population
    default_price = fields.Monetary(string='Default Price', currency_field='currency_id',
                                     help='Default selling price for this charge type')
    default_cost = fields.Monetary(string='Default Cost', currency_field='currency_id',
                                    help='Default cost for this charge type')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                   default=lambda self: self.env.company.currency_id)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Charge code must be unique!')
    ]
    
    def name_get(self):
        result = []
        for record in self:
            name = f'[{record.code}] {record.name}'
            result.append((record.id, name))
        return result
