# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FreightQuotationLine(models.Model):
    _name = 'freight.quotation.line'
    _description = 'Freight Quotation Line'
    _order = 'sequence, id'

    quotation_id = fields.Many2one('freight.quotation', string='Quotation', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    charge_type_id = fields.Many2one('freight.charge.type', string='Charge Type', required=True)
    description = fields.Text(string='Description', required=True)
    quantity = fields.Float(string='Quantity', default=1.0, digits=(12, 2))
    unit_price = fields.Monetary(string='Unit Price', required=True, currency_field='currency_id')
    cost_price = fields.Monetary(string='Cost Price', currency_field='currency_id')
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_amounts', store=True,
                                currency_field='currency_id')
    tax_amount = fields.Monetary(string='Tax Amount', compute='_compute_amounts', store=True,
                                  currency_field='currency_id')
    total = fields.Monetary(string='Total', compute='_compute_amounts', store=True,
                            currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='quotation_id.currency_id', store=True)
    
    @api.depends('quantity', 'unit_price', 'tax_ids')
    def _compute_amounts(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
            if line.tax_ids:
                taxes = line.tax_ids.compute_all(line.unit_price, line.currency_id, line.quantity)
                line.tax_amount = sum(t.get('amount', 0.0) for t in taxes['taxes'])
                line.total = taxes['total_included']
            else:
                line.tax_amount = 0.0
                line.total = line.subtotal
    
    @api.onchange('charge_type_id')
    def _onchange_charge_type_id(self):
        if self.charge_type_id:
            self.description = self.charge_type_id.name
