# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class FreightTransportLeg(models.Model):
    _name = 'freight.transport.leg'
    _description = 'Transport Leg'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'shipment_id, sequence, id'

    name = fields.Char(string='Leg Reference', compute='_compute_name', store=True)
    shipment_id = fields.Many2one('freight.shipment', string='Shipment', required=True, 
                                   ondelete='cascade', tracking=True)
    sequence = fields.Integer(string='Sequence', required=True, default=10,
                              help='Order of this leg in the multi-modal route')
    
    # Transport Mode
    transport_mode = fields.Selection([
        ('sea', 'Sea Freight'),
        ('air', 'Air Freight'),
        ('road', 'Road Transport'),
        ('rail', 'Rail Transport')
    ], string='Transport Mode', required=True, tracking=True)
    
    # Route
    origin_location_id = fields.Many2one('freight.location', string='Origin', required=True,
                                          tracking=True)
    destination_location_id = fields.Many2one('freight.location', string='Destination', 
                                              required=True, tracking=True)
    distance_km = fields.Float(string='Distance (KM)', digits=(12, 2))
    
    # Carrier Information
    carrier_id = fields.Many2one('res.partner', string='Carrier', required=True,
                                  domain=[('is_carrier', '=', True)], tracking=True)
    vessel_name = fields.Char(string='Vessel/Flight/Vehicle Name', tracking=True)
    voyage_number = fields.Char(string='Voyage/Flight Number', tracking=True)
    booking_reference = fields.Char(string='Booking Reference', tracking=True)
    
    # Performance Tracking
    is_on_time = fields.Boolean(string='On Time Delivery', compute='_compute_performance', store=True)
    delay_days = fields.Float(string='Delay (Days)', compute='_compute_performance', store=True, digits=(5, 2))
    
    @api.depends('estimated_arrival', 'actual_arrival')
    def _compute_performance(self):
        for record in self:
            if record.actual_arrival and record.estimated_arrival:
                delta = record.actual_arrival - record.estimated_arrival
                delay_days = delta.total_seconds() / 86400
                record.delay_days = delay_days if delay_days > 0 else 0
                record.is_on_time = delay_days <= 0.5  # On time if within 12 hours
            else:
                record.delay_days = 0
                record.is_on_time = False
    
    def write(self, vals):
        """Track carrier performance when leg completes"""
        res = super(FreightTransportLeg, self).write(vals)
        
        # When leg is completed, update carrier performance stats
        if vals.get('state') == 'completed':
            for record in self:
                if record.carrier_id:
                    record._update_carrier_performance()
        
        return res
    
    def _update_carrier_performance(self):
        """Update carrier performance statistics"""
        self.ensure_one()
        
        # Calculate carrier's on-time performance
        completed_legs = self.search([
            ('carrier_id', '=', self.carrier_id.id),
            ('state', '=', 'completed'),
            ('actual_arrival', '!=', False)
        ])
        
        if completed_legs:
            on_time_count = len(completed_legs.filtered('is_on_time'))
            total_count = len(completed_legs)
            on_time_percentage = (on_time_count / total_count) * 100
            
            # Store in carrier partner record (you can add these fields to res.partner)
            self.carrier_id.message_post(
                body=f"Performance Update: {on_time_percentage:.1f}% on-time delivery rate "
                     f"({on_time_count}/{total_count} legs)",
                subject="Carrier Performance"
            )
    
    # Schedule
    estimated_departure = fields.Datetime(string='Estimated Departure', required=True, tracking=True)
    estimated_arrival = fields.Datetime(string='Estimated Arrival', required=True, tracking=True)
    actual_departure = fields.Datetime(string='Actual Departure', tracking=True)
    actual_arrival = fields.Datetime(string='Actual Arrival', tracking=True)
    
    # Transit Time
    estimated_transit_days = fields.Float(string='Est. Transit (Days)', 
                                          compute='_compute_transit_time', store=True, 
                                          digits=(5, 2))
    actual_transit_days = fields.Float(string='Actual Transit (Days)', 
                                       compute='_compute_transit_time', store=True,
                                       digits=(5, 2))
    transit_variance_days = fields.Float(string='Transit Variance (Days)',
                                         compute='_compute_transit_time', store=True,
                                         digits=(5, 2))
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('booked', 'Booked'),
        ('ready', 'Ready to Load'),
        ('loaded', 'Loaded'),
        ('in_transit', 'In Transit'),
        ('arrived', 'Arrived'),
        ('discharged', 'Discharged'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Milestones
    booking_confirmed_date = fields.Datetime(string='Booking Confirmed', tracking=True)
    cargo_loaded_date = fields.Datetime(string='Cargo Loaded', tracking=True)
    departed_date = fields.Datetime(string='Departed', tracking=True)
    arrived_date = fields.Datetime(string='Arrived', tracking=True)
    cargo_discharged_date = fields.Datetime(string='Cargo Discharged', tracking=True)
    
    # Cost Tracking
    estimated_cost = fields.Monetary(string='Estimated Cost', currency_field='currency_id',
                                      tracking=True)
    actual_cost = fields.Monetary(string='Actual Cost', currency_field='currency_id',
                                   tracking=True)
    cost_variance = fields.Monetary(string='Cost Variance', compute='_compute_cost_variance',
                                     store=True, currency_field='currency_id')
    cost_variance_percentage = fields.Float(string='Cost Variance %', 
                                            compute='_compute_cost_variance',
                                            store=True, digits=(5, 2))
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                   default=lambda self: self.env.company.currency_id)
    
    # Cost Breakdown
    freight_charge = fields.Monetary(string='Freight Charge', currency_field='currency_id')
    fuel_surcharge = fields.Monetary(string='Fuel Surcharge', currency_field='currency_id')
    handling_fee = fields.Monetary(string='Handling Fee', currency_field='currency_id')
    other_charges = fields.Monetary(string='Other Charges', currency_field='currency_id')
    
    @api.onchange('freight_charge', 'fuel_surcharge', 'handling_fee', 'other_charges')
    def _onchange_cost_breakdown(self):
        """Auto-calculate estimated cost from breakdown"""
        self.estimated_cost = (self.freight_charge or 0) + (self.fuel_surcharge or 0) + \
                             (self.handling_fee or 0) + (self.other_charges or 0)
    
    # Transshipment
    is_transshipment_point = fields.Boolean(string='Is Transshipment Point',
                                            compute='_compute_transshipment', store=True)
    handling_time_hours = fields.Float(string='Handling Time (Hours)', digits=(5, 2),
                                       help='Time required for cargo transfer at transshipment point')
    handling_cost = fields.Monetary(string='Handling Cost', currency_field='currency_id')
    transfer_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Transfer Status')
    
    # Containers
    container_ids = fields.Many2many('freight.container', 'freight_leg_container_rel',
                                     'leg_id', 'container_id', string='Containers')
    container_count = fields.Integer(string='Containers', compute='_compute_container_count')
    
    @api.constrains('container_ids', 'transport_mode')
    def _check_container_compatibility(self):
        """Validate container types are compatible with transport mode"""
        for record in self:
            if record.container_ids and record.transport_mode:
                # Reefer containers need special handling
                reefer_containers = record.container_ids.filtered(
                    lambda c: 'rf' in c.container_type
                )
                if reefer_containers and record.transport_mode == 'rail':
                    raise ValidationError(
                        'Reefer containers may not be compatible with rail transport. '
                        'Please verify with carrier.'
                    )
                
                # Open top and flat rack have restrictions
                special_containers = record.container_ids.filtered(
                    lambda c: c.container_type in ['20ot', '40ot', '20fr', '40fr']
                )
                if special_containers and record.transport_mode == 'air':
                    raise ValidationError(
                        'Open top and flat rack containers cannot be transported by air.'
                    )
    
    # Documents
    document_ids = fields.One2many('freight.leg.document', 'leg_id', string='Documents')
    document_count = fields.Integer(string='Documents', compute='_compute_document_count')
    
    # Delays
    is_delayed = fields.Boolean(string='Delayed', compute='_compute_delay_status', store=True)
    delay_hours = fields.Float(string='Delay (Hours)', compute='_compute_delay_status',
                                store=True, digits=(5, 2))
    delay_reason = fields.Text(string='Delay Reason')
    affects_next_leg = fields.Boolean(string='Affects Next Leg', 
                                      compute='_compute_delay_impact', store=True)
    
    # Additional Info
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                  default=lambda self: self.env.company)
    
    @api.depends('shipment_id', 'sequence', 'transport_mode')
    def _compute_name(self):
        for record in self:
            if record.shipment_id and record.transport_mode:
                mode_name = dict(record._fields['transport_mode'].selection).get(record.transport_mode)
                record.name = f"{record.shipment_id.name} - Leg {record.sequence} ({mode_name})"
            else:
                record.name = 'New Leg'
    
    @api.depends('estimated_departure', 'estimated_arrival', 'actual_departure', 'actual_arrival')
    def _compute_transit_time(self):
        for record in self:
            # Estimated transit time
            if record.estimated_departure and record.estimated_arrival:
                delta = record.estimated_arrival - record.estimated_departure
                record.estimated_transit_days = delta.total_seconds() / 86400
            else:
                record.estimated_transit_days = 0.0
            
            # Actual transit time
            if record.actual_departure and record.actual_arrival:
                delta = record.actual_arrival - record.actual_departure
                record.actual_transit_days = delta.total_seconds() / 86400
                record.transit_variance_days = record.actual_transit_days - record.estimated_transit_days
            else:
                record.actual_transit_days = 0.0
                record.transit_variance_days = 0.0
    
    @api.depends('estimated_cost', 'actual_cost')
    def _compute_cost_variance(self):
        for record in self:
            record.cost_variance = record.actual_cost - record.estimated_cost
            if record.estimated_cost:
                record.cost_variance_percentage = (record.cost_variance / record.estimated_cost) * 100
            else:
                record.cost_variance_percentage = 0.0
    
    @api.depends('sequence', 'shipment_id.leg_ids')
    def _compute_transshipment(self):
        for record in self:
            # A location is a transshipment point if it's the destination of one leg
            # and the origin of the next leg
            next_leg = self.search([
                ('shipment_id', '=', record.shipment_id.id),
                ('sequence', '>', record.sequence)
            ], order='sequence', limit=1)
            
            record.is_transshipment_point = bool(next_leg and 
                                                 record.destination_location_id == next_leg.origin_location_id)
    
    def _compute_container_count(self):
        for record in self:
            record.container_count = len(record.container_ids)
    
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)
    
    @api.depends('estimated_arrival', 'actual_arrival', 'state')
    def _compute_delay_status(self):
        for record in self:
            if record.actual_arrival and record.estimated_arrival:
                delta = record.actual_arrival - record.estimated_arrival
                delay_hours = delta.total_seconds() / 3600
                record.is_delayed = delay_hours > 2  # More than 2 hours is considered delayed
                record.delay_hours = delay_hours if delay_hours > 0 else 0.0
            elif record.state in ['in_transit', 'arrived'] and record.estimated_arrival:
                # Check if we're past estimated arrival
                now = fields.Datetime.now()
                if now > record.estimated_arrival:
                    delta = now - record.estimated_arrival
                    delay_hours = delta.total_seconds() / 3600
                    record.is_delayed = delay_hours > 2
                    record.delay_hours = delay_hours
                else:
                    record.is_delayed = False
                    record.delay_hours = 0.0
            else:
                record.is_delayed = False
                record.delay_hours = 0.0
    
    @api.depends('is_delayed', 'delay_hours', 'sequence', 'shipment_id.leg_ids')
    def _compute_delay_impact(self):
        for record in self:
            if record.is_delayed and record.delay_hours > 0:
                # Check if there's a next leg
                next_leg = self.search([
                    ('shipment_id', '=', record.shipment_id.id),
                    ('sequence', '>', record.sequence)
                ], order='sequence', limit=1)
                
                if next_leg:
                    # Calculate if delay causes missed connection
                    if record.actual_arrival:
                        arrival_time = record.actual_arrival
                    else:
                        arrival_time = fields.Datetime.now()
                    
                    # Add handling time
                    if record.handling_time_hours:
                        arrival_time = arrival_time + timedelta(hours=record.handling_time_hours)
                    
                    # Check if we can make the next leg departure
                    record.affects_next_leg = arrival_time >= next_leg.estimated_departure
                else:
                    record.affects_next_leg = False
            else:
                record.affects_next_leg = False
    
    @api.constrains('origin_location_id', 'destination_location_id')
    def _check_locations(self):
        for record in self:
            if record.origin_location_id == record.destination_location_id:
                raise ValidationError('Origin and destination cannot be the same.')
    
    @api.constrains('estimated_departure', 'estimated_arrival')
    def _check_dates(self):
        for record in self:
            if record.estimated_arrival <= record.estimated_departure:
                raise ValidationError('Estimated arrival must be after estimated departure.')
    
    @api.constrains('sequence', 'shipment_id')
    def _check_leg_continuity(self):
        """Validate that destination of leg N matches origin of leg N+1"""
        for record in self:
            if not record.shipment_id:
                continue
                
            # Check continuity with next leg
            next_leg = self.search([
                ('shipment_id', '=', record.shipment_id.id),
                ('sequence', '>', record.sequence)
            ], order='sequence', limit=1)
            
            if next_leg and record.destination_location_id != next_leg.origin_location_id:
                raise ValidationError(
                    f'Leg continuity error: Destination of leg {record.sequence} '
                    f'must match origin of leg {next_leg.sequence}.'
                )
            
            # Validate first leg matches shipment origin
            first_leg = self.search([
                ('shipment_id', '=', record.shipment_id.id)
            ], order='sequence', limit=1)
            
            if first_leg.id == record.id and record.shipment_id.is_multimodal:
                if record.shipment_id.origin_port_id and \
                   record.origin_location_id != record.shipment_id.origin_port_id:
                    raise ValidationError(
                        'First leg origin must match shipment origin port.'
                    )
            
            # Validate last leg matches shipment destination
            last_leg = self.search([
                ('shipment_id', '=', record.shipment_id.id)
            ], order='sequence desc', limit=1)
            
            if last_leg.id == record.id and record.shipment_id.is_multimodal:
                if record.shipment_id.destination_port_id and \
                   record.destination_location_id != record.shipment_id.destination_port_id:
                    raise ValidationError(
                        'Last leg destination must match shipment destination port.'
                    )
    
    def action_book(self):
        self.ensure_one()
        self.write({
            'state': 'booked',
            'booking_confirmed_date': fields.Datetime.now()
        })
        return True
    
    def action_load(self):
        self.ensure_one()
        self.write({
            'state': 'loaded',
            'cargo_loaded_date': fields.Datetime.now()
        })
        return True
    
    def action_depart(self):
        self.ensure_one()
        self.write({
            'state': 'in_transit',
            'actual_departure': fields.Datetime.now(),
            'departed_date': fields.Datetime.now()
        })
        return True
    
    def action_arrive(self):
        self.ensure_one()
        self.write({
            'state': 'arrived',
            'actual_arrival': fields.Datetime.now(),
            'arrived_date': fields.Datetime.now()
        })
        
        # Check if this affects next leg
        if self.affects_next_leg:
            # Send notification
            self.message_post(
                body=f"Delay of {self.delay_hours:.1f} hours may affect next leg connection.",
                subject="Connection at Risk"
            )
        
        # Auto-start next leg if this is a transshipment point
        if self.is_transshipment_point:
            next_leg = self.search([
                ('shipment_id', '=', self.shipment_id.id),
                ('sequence', '>', self.sequence)
            ], order='sequence', limit=1)
            
            if next_leg and next_leg.state == 'booked':
                # Auto-transition to ready for loading
                next_leg.write({'state': 'ready'})
                next_leg.message_post(
                    body=f"Cargo arrived from previous leg. Ready for loading.",
                    subject="Ready for Next Leg"
                )
        
        return True
    
    def action_discharge(self):
        self.ensure_one()
        self.write({
            'state': 'discharged',
            'cargo_discharged_date': fields.Datetime.now()
        })
        
        # If this is a transshipment point, mark transfer as in progress
        if self.is_transshipment_point:
            self.write({'transfer_status': 'in_progress'})
        
        return True
    
    def action_complete(self):
        self.ensure_one()
        
        # If transshipment point, mark transfer as completed
        if self.is_transshipment_point:
            self.write({'transfer_status': 'completed'})
        
        self.state = 'completed'
        
        # Check if all legs are completed, then complete shipment
        all_legs = self.shipment_id.leg_ids
        if all(leg.state == 'completed' for leg in all_legs):
            self.shipment_id.write({'state': 'completed'})
        
        return True
    
    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'
        
        # If any leg is cancelled, notify on shipment
        self.shipment_id.message_post(
            body=f"Transport leg {self.name} has been cancelled.",
            subject="Leg Cancelled"
        )
        
        return True
    
    def action_view_containers(self):
        self.ensure_one()
        return {
            'name': 'Containers',
            'type': 'ir.actions.act_window',
            'res_model': 'freight.container',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.container_ids.ids)],
        }
    
    def action_view_documents(self):
        self.ensure_one()
        return {
            'name': 'Documents',
            'type': 'ir.actions.act_window',
            'res_model': 'freight.leg.document',
            'view_mode': 'tree,form',
            'domain': [('leg_id', '=', self.id)],
            'context': {'default_leg_id': self.id}
        }
    
    def get_milestone_data(self):
        """Get milestone data for this leg"""
        self.ensure_one()
        
        milestones = [
            {'name': 'Booked', 'date': self.booking_confirmed_date, 'completed': bool(self.booking_confirmed_date)},
            {'name': 'Loaded', 'date': self.cargo_loaded_date, 'completed': bool(self.cargo_loaded_date)},
            {'name': 'Departed', 'date': self.departed_date, 'completed': bool(self.departed_date)},
            {'name': 'In Transit', 'date': None, 'completed': self.state in ['in_transit', 'arrived', 'discharged', 'completed']},
            {'name': 'Arrived', 'date': self.arrived_date, 'completed': bool(self.arrived_date)},
            {'name': 'Discharged', 'date': self.cargo_discharged_date, 'completed': bool(self.cargo_discharged_date)},
            {'name': 'Completed', 'date': None, 'completed': self.state == 'completed'},
        ]
        
        return milestones


class FreightLegDocument(models.Model):
    _name = 'freight.leg.document'
    _description = 'Transport Leg Document'
    _order = 'create_date desc'

    name = fields.Char(string='Document Name', required=True)
    leg_id = fields.Many2one('freight.transport.leg', string='Transport Leg', required=True,
                             ondelete='cascade')
    document_type = fields.Selection([
        ('bill_of_lading', 'Bill of Lading'),
        ('air_waybill', 'Air Waybill'),
        ('cmr', 'CMR (Road Transport)'),
        ('rail_consignment', 'Rail Consignment Note'),
        ('customs_declaration', 'Customs Declaration'),
        ('packing_list', 'Packing List'),
        ('certificate_of_origin', 'Certificate of Origin'),
        ('insurance_certificate', 'Insurance Certificate'),
        ('other', 'Other')
    ], string='Document Type', required=True)
    document_file = fields.Binary(string='File', required=True, attachment=True)
    file_name = fields.Char(string='File Name')
    upload_date = fields.Datetime(string='Upload Date', default=fields.Datetime.now, readonly=True)
    uploaded_by = fields.Many2one('res.users', string='Uploaded By', 
                                   default=lambda self: self.env.user, readonly=True)
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                  default=lambda self: self.env.company)
