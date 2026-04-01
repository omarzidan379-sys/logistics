# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    shipment_id = fields.Many2one('freight.shipment', string='Shipment', tracking=True,
                                   help='Related freight shipment for this invoice/bill')
    quotation_id = fields.Many2one('freight.quotation', string='Quotation', tracking=True,
                                    help='Related freight quotation')
    booking_id = fields.Many2one('freight.booking', string='Booking', tracking=True,
                                  help='Related freight booking')
