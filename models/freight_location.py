# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FreightLocation(models.Model):
    _name = 'freight.location'
    _description = 'Freight Location'
    _order = 'name'
    
    name = fields.Char('Location Name', required=True, index=True)
    code = fields.Char('Location Code', required=True, index=True)
    location_type = fields.Selection([
        ('port', 'Port'),
        ('airport', 'Airport'),
        ('warehouse', 'Warehouse'),
        ('city', 'City')
    ], string='Location Type', required=True, default='port')
    
    country_id = fields.Many2one('res.country', 'Country', required=True)
    state_id = fields.Many2one('res.country.state', 'State')
    city = fields.Char('City')
    address = fields.Text('Address')
    
    latitude = fields.Float('Latitude', digits=(10, 7))
    longitude = fields.Float('Longitude', digits=(10, 7))
    
    active = fields.Boolean('Active', default=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Location code must be unique!'),
    ]
    
    def name_get(self):
        result = []
        for location in self:
            name = f"[{location.code}] {location.name}"
            result.append((location.id, name))
        return result
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, order=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', operator, name), ('name', operator, name)]
        return self._search(domain + args, limit=limit, order=order)
