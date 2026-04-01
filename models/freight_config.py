# -*- coding: utf-8 -*-
from odoo import models, fields


class FreightConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Freight settings - renamed to avoid default_ prefix requirement
    freight_free_time_days = fields.Integer(
        'Default Free Time (Days)', 
        default=7,
        config_parameter='freight_management.default_free_time_days'
    )
    freight_demurrage_rate = fields.Float(
        'Default Demurrage Rate per Day',
        config_parameter='freight_management.default_demurrage_rate'
    )
    freight_detention_rate = fields.Float(
        'Default Detention Rate per Day',
        config_parameter='freight_management.default_detention_rate'
    )
    
    # EDI Configuration
    edi_enabled = fields.Boolean(
        'Enable EDI Integration',
        config_parameter='freight_management.edi_enabled'
    )
    edi_endpoint = fields.Char(
        'EDI Endpoint URL',
        config_parameter='freight_management.edi_endpoint'
    )
    edi_username = fields.Char(
        'EDI Username',
        config_parameter='freight_management.edi_username'
    )
    edi_password = fields.Char(
        'EDI Password',
        config_parameter='freight_management.edi_password'
    )
    
    # API Configuration
    api_rate_limit = fields.Integer(
        'API Rate Limit (requests/minute)', 
        default=100,
        config_parameter='freight_management.api_rate_limit'
    )
