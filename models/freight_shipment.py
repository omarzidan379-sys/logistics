# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FreightShipment(models.Model):
    _name = 'freight.shipment'
    _description = 'Freight Shipment'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'create_date desc, name desc'

    name = fields.Char(string='Shipment Number', required=True, copy=False, readonly=True,
                       default=lambda self: 'New')
    quotation_id = fields.Many2one('freight.quotation', string='Quotation', tracking=True)
    booking_id = fields.Many2one('freight.booking', string='Booking', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    
    # Parties
    shipper_id = fields.Many2one('res.partner', string='Shipper', required=True,
                                  domain=[('is_shipper', '=', True)], tracking=True)
    consignee_id = fields.Many2one('res.partner', string='Consignee', required=True,
                                    domain=[('is_consignee', '=', True)], tracking=True)
    notify_party_id = fields.Many2one('res.partner', string='Notify Party', tracking=True)
    
    # Service Details
    service_type = fields.Selection([
        ('fcl', 'FCL (Full Container Load)'),
        ('lcl', 'LCL (Less than Container Load)'),
        ('air', 'Air Freight'),
        ('road', 'Road Transport'),
        ('rail', 'Rail Transport')
    ], string='Service Type', required=True, default='fcl', tracking=True)
    shipment_direction = fields.Selection([
        ('import', 'Import'),
        ('export', 'Export')
    ], string='Direction', required=True, default='export', tracking=True)
    incoterm_id = fields.Many2one('account.incoterms', string='Incoterm', tracking=True)
    carrier_id = fields.Many2one('res.partner', string='Carrier', required=True,
                                  domain=[('is_carrier', '=', True)], tracking=True)
    
    # Vessel/Transport Information
    vessel_name = fields.Char(string='Vessel/Flight/Vehicle Name', tracking=True)
    voyage_number = fields.Char(string='Voyage/Flight Number', tracking=True)
    bl_number = fields.Char(string='B/L Number', tracking=True)
    bl_type = fields.Selection([
        ('original', 'Original B/L'),
        ('seaway', 'Sea Waybill'),
        ('express', 'Express B/L')
    ], string='B/L Type', tracking=True)
    hbl_number = fields.Char(string='HBL Number', help='House Bill of Lading', tracking=True)
    mbl_number = fields.Char(string='MBL Number', help='Master Bill of Lading', tracking=True)
    
    # Route Information
    origin_port_id = fields.Many2one('freight.location', string='Origin Port', required=True,
                                      domain=[('location_type', 'in', ['port', 'airport'])], tracking=True)
    destination_port_id = fields.Many2one('freight.location', string='Destination Port', required=True,
                                          domain=[('location_type', 'in', ['port', 'airport'])], tracking=True)
    origin_address = fields.Text(string='Origin Address')
    destination_address = fields.Text(string='Destination Address')
    
    # Portal compatibility fields
    origin_location_id = fields.Many2one('freight.location', string='Origin Location', 
                                         related='origin_port_id', store=True, readonly=True)
    destination_location_id = fields.Many2one('freight.location', string='Destination Location',
                                              related='destination_port_id', store=True, readonly=True)
    
    # Cargo Details
    cargo_description = fields.Text(string='Cargo Description', required=True)
    commodity_id = fields.Many2one('product.product', string='Commodity')
    hs_code = fields.Char(string='HS Code')
    total_weight = fields.Float(string='Total Weight (KG)', digits=(12, 2))
    total_volume = fields.Float(string='Total Volume (CBM)', digits=(12, 3))
    chargeable_weight = fields.Float(string='Chargeable Weight (KG)', digits=(12, 2))
    total_packages = fields.Integer(string='Total Packages')
    
    # Special Cargo
    is_dangerous_goods = fields.Boolean(string='Dangerous Goods', tracking=True)
    is_temperature_controlled = fields.Boolean(string='Temperature Controlled', tracking=True)
    special_instructions = fields.Text(string='Special Instructions')
    
    # Insurance
    is_insured = fields.Boolean(string='Insured', tracking=True)
    insurance_policy_number = fields.Char(string='Insurance Policy Number')
    insurance_amount = fields.Monetary(string='Insurance Amount', currency_field='currency_id')
    insurance_company_id = fields.Many2one('res.partner', string='Insurance Company',
                                           domain=[('is_insurance_company', '=', True)])
    
    # Proof of Delivery
    pod_received = fields.Boolean(string='POD Received', tracking=True,
                                   help='Proof of Delivery document received')
    pod_date = fields.Date(string='POD Date', tracking=True)
    pod_signed_by = fields.Char(string='POD Signed By')
    pod_document_id = fields.Many2one('freight.shipment.document', string='POD Document',
                                      domain="[('shipment_id', '=', id), ('document_type', '=', 'pod')]")
    
    # Payment Tracking
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')
    payment_status = fields.Selection([
        ('not_invoiced', 'Not Invoiced'),
        ('invoiced', 'Invoiced'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('overdue', 'Overdue')
    ], string='Payment Status', compute='_compute_payment_status', store=True, tracking=True)
    invoice_ids = fields.One2many('account.move', 'shipment_id', string='Customer Invoices',
                                   domain=[('move_type', '=', 'out_invoice')])
    vendor_bill_ids = fields.One2many('account.move', 'shipment_id', string='Vendor Bills',
                                      domain=[('move_type', '=', 'in_invoice')])
    total_invoiced = fields.Monetary(string='Total Invoiced', compute='_compute_payment_status',
                                     store=True, currency_field='currency_id')
    total_paid = fields.Monetary(string='Total Paid', compute='_compute_payment_status',
                                 store=True, currency_field='currency_id')
    
    # Vendor Bill Tracking
    vendor_bills_created = fields.Boolean(string='Vendor Bills Created', default=False)
    total_vendor_cost = fields.Monetary(string='Total Vendor Cost', compute='_compute_vendor_costs',
                                        store=True, currency_field='currency_id')
    
    # State Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('booked', 'Booked'),
        ('in_operation', 'In Operation'),
        ('in_transit', 'In Transit'),
        ('arrived', 'Arrived'),
        ('customs_clearance', 'Customs Clearance'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('invoiced', 'Invoiced')
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Customs Clearance
    customs_broker_id = fields.Many2one('res.partner', string='Customs Broker',
                                        domain=[('is_customs_broker', '=', True)],
                                        tracking=True,
                                        help='Customs broker assigned for clearance')
    customs_entry_number = fields.Char(string='Customs Entry Number', tracking=True)
    customs_value = fields.Monetary(string='Customs Declared Value', currency_field='currency_id')
    duty_amount = fields.Monetary(string='Duty Amount', currency_field='currency_id')
    customs_status = fields.Selection([
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('cleared', 'Cleared'),
        ('held', 'Held'),
        ('rejected', 'Rejected')
    ], string='Customs Status', tracking=True)
    
    # Milestone Dates
    booking_date = fields.Date(string='Booking Date', tracking=True)
    gate_in_date = fields.Date(string='Gate In Date', tracking=True)
    loading_date = fields.Date(string='Loading Date', tracking=True)
    sailing_date = fields.Date(string='Sailing Date', tracking=True)
    arrival_date = fields.Date(string='Arrival Date', tracking=True)
    customs_clearance_date = fields.Date(string='Customs Clearance Date', tracking=True)
    delivery_date = fields.Date(string='Delivery Date', tracking=True)
    
    # Cost Tracking
    quoted_cost = fields.Monetary(string='Quoted Cost', currency_field='currency_id')
    actual_cost = fields.Monetary(string='Actual Cost', currency_field='currency_id')
    cost_variance = fields.Monetary(string='Cost Variance', compute='_compute_cost_variance',
                                     store=True, currency_field='currency_id')
    cost_variance_percentage = fields.Float(string='Cost Variance %', compute='_compute_cost_variance',
                                             store=True, digits=(5, 2))
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                   default=lambda self: self.env.company.currency_id)
    
    # Multi-Modal Transport
    is_multimodal = fields.Boolean(string='Multi-Modal Transport', default=False,
                                    help='Enable multi-modal transport with multiple legs')
    leg_ids = fields.One2many('freight.transport.leg', 'shipment_id', string='Transport Legs')
    leg_count = fields.Integer(string='Legs', compute='_compute_leg_count')
    total_transit_days = fields.Float(string='Total Transit Time (Days)', 
                                      compute='_compute_total_transit', store=True, digits=(5, 2))
    total_estimated_cost = fields.Monetary(string='Total Estimated Cost',
                                           compute='_compute_total_costs', store=True,
                                           currency_field='currency_id')
    total_actual_cost = fields.Monetary(string='Total Actual Cost',
                                        compute='_compute_total_costs', store=True,
                                        currency_field='currency_id')
    
    @api.constrains('is_multimodal', 'leg_ids')
    def _check_multimodal_legs(self):
        """Validate multi-modal shipments have at least 2 legs"""
        for record in self:
            if record.is_multimodal and record.state not in ['draft', 'booked']:
                if len(record.leg_ids) < 2:
                    raise ValidationError(
                        'Multi-modal shipments must have at least 2 transport legs.'
                    )
    
    @api.onchange('is_multimodal')
    def _onchange_is_multimodal(self):
        """When enabling multi-modal, create first leg from shipment data"""
        if self.is_multimodal and not self.leg_ids and self.origin_port_id and self.destination_port_id:
            # Auto-create first leg suggestion
            self.leg_ids = [(0, 0, {
                'sequence': 10,
                'transport_mode': 'sea' if self.service_type == 'fcl' else 'air',
                'origin_location_id': self.origin_port_id.id,
                'destination_location_id': self.destination_port_id.id,
                'carrier_id': self.carrier_id.id if self.carrier_id else False,
                'estimated_departure': fields.Datetime.now(),
                'estimated_arrival': fields.Datetime.now(),
            })]
    
    # Relations
    container_ids = fields.One2many('freight.container', 'shipment_id', string='Containers')
    document_ids = fields.One2many('freight.shipment.document', 'shipment_id', string='Documents')
    
    # Additional Info
    notes = fields.Text(string='Notes')
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user,
                              tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                  default=lambda self: self.env.company)
    
    # Smart Buttons
    container_count = fields.Integer(string='Containers', compute='_compute_container_count')
    document_count = fields.Integer(string='Documents', compute='_compute_document_count')
    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoice_count')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('freight.shipment') or 'New'
        return super(FreightShipment, self).create(vals)
    
    @api.depends('quoted_cost', 'actual_cost')
    def _compute_cost_variance(self):
        for record in self:
            record.cost_variance = record.actual_cost - record.quoted_cost
            if record.quoted_cost:
                record.cost_variance_percentage = (record.cost_variance / record.quoted_cost) * 100
            else:
                record.cost_variance_percentage = 0.0
    
    def _compute_container_count(self):
        for record in self:
            record.container_count = len(record.container_ids)
    
    def _compute_leg_count(self):
        for record in self:
            record.leg_count = len(record.leg_ids)
    
    @api.depends('leg_ids.estimated_transit_days', 'leg_ids.handling_time_hours')
    def _compute_total_transit(self):
        for record in self:
            if record.is_multimodal and record.leg_ids:
                # Sum transit days of all legs plus handling time at transshipment points
                transit_days = sum(record.leg_ids.mapped('estimated_transit_days'))
                handling_hours = sum(record.leg_ids.mapped('handling_time_hours'))
                record.total_transit_days = transit_days + (handling_hours / 24)
            else:
                record.total_transit_days = 0.0
    
    @api.depends('leg_ids.estimated_cost', 'leg_ids.actual_cost', 'leg_ids.handling_cost')
    def _compute_total_costs(self):
        for record in self:
            if record.is_multimodal and record.leg_ids:
                record.total_estimated_cost = sum(record.leg_ids.mapped('estimated_cost')) + \
                                             sum(record.leg_ids.mapped('handling_cost'))
                record.total_actual_cost = sum(record.leg_ids.mapped('actual_cost')) + \
                                          sum(record.leg_ids.mapped('handling_cost'))
            else:
                record.total_estimated_cost = record.quoted_cost
                record.total_actual_cost = record.actual_cost
    
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)
    
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = self.env['account.move'].search_count([
                ('move_type', '=', 'out_invoice'),
                ('shipment_id', '=', record.id)
            ])
    
    @api.depends('invoice_ids', 'invoice_ids.payment_state', 'invoice_ids.amount_total', 'invoice_ids.amount_residual')
    def _compute_payment_status(self):
        for record in self:
            invoices = record.invoice_ids.filtered(lambda inv: inv.state == 'posted')
            
            if not invoices:
                record.payment_status = 'not_invoiced'
                record.total_invoiced = 0
                record.total_paid = 0
            else:
                record.total_invoiced = sum(invoices.mapped('amount_total'))
                record.total_paid = record.total_invoiced - sum(invoices.mapped('amount_residual'))
                
                # Check if all invoices are paid
                if all(inv.payment_state == 'paid' for inv in invoices):
                    record.payment_status = 'paid'
                elif any(inv.payment_state in ['paid', 'in_payment', 'partial'] for inv in invoices):
                    record.payment_status = 'partial'
                elif any(inv.invoice_date_due and inv.invoice_date_due < fields.Date.today() for inv in invoices):
                    record.payment_status = 'overdue'
                else:
                    record.payment_status = 'invoiced'
    
    @api.depends('vendor_bill_ids', 'vendor_bill_ids.amount_total')
    def _compute_vendor_costs(self):
        for record in self:
            vendor_bills = record.vendor_bill_ids.filtered(lambda bill: bill.state == 'posted')
            record.total_vendor_cost = sum(vendor_bills.mapped('amount_total'))
    
    def action_book(self):
        self.ensure_one()
        self.write({
            'state': 'booked',
            'booking_date': fields.Date.today()
        })
        
        # If multi-modal, update shipment state based on legs
        if self.is_multimodal and self.leg_ids:
            # If all legs are booked or beyond, move shipment to booked
            if all(leg.state != 'draft' for leg in self.leg_ids):
                self.state = 'booked'
        
        return True
    
    def action_start_operation(self):
        self.ensure_one()
        self.state = 'in_operation'
        self._send_status_update_notification()
        
        # If multi-modal, book all legs automatically
        if self.is_multimodal and self.leg_ids:
            draft_legs = self.leg_ids.filtered(lambda l: l.state == 'draft')
            for leg in draft_legs:
                leg.action_book()
        
        return True
    
    def action_in_transit(self):
        self.ensure_one()
        self.write({
            'state': 'in_transit',
            'sailing_date': fields.Date.today()
        })
        
        # If multi-modal, start first leg
        if self.is_multimodal and self.leg_ids:
            first_leg = self.leg_ids.sorted('sequence')[0]
            if first_leg.state in ['booked', 'ready', 'loaded']:
                first_leg.action_depart()
        
        return True
    
    def action_arrived(self):
        self.ensure_one()
        self.write({
            'state': 'arrived',
            'arrival_date': fields.Date.today()
        })
        return True
    
    def action_customs_clearance(self):
        self.ensure_one()
        
        # Validate customs broker is assigned
        if not self.customs_broker_id:
            raise ValidationError(
                'Please assign a customs broker before proceeding with customs clearance.'
            )
        
        # Validate required customs documents
        required_docs = ['customs_declaration', 'packing_list', 'commercial_invoice']
        
        if self.is_multimodal:
            # Check documents across all legs
            all_doc_types = []
            for leg in self.leg_ids:
                all_doc_types.extend(leg.document_ids.mapped('document_type'))
        else:
            all_doc_types = self.document_ids.mapped('document_type')
        
        missing_docs = [doc for doc in required_docs if doc not in all_doc_types]
        
        if missing_docs:
            raise ValidationError(
                f'Missing required customs documents: {", ".join(missing_docs)}. '
                f'Please upload all required documents before customs clearance.'
            )
        
        self.write({
            'state': 'customs_clearance',
            'customs_clearance_date': fields.Date.today(),
            'customs_status': 'submitted'
        })
        
        # Notify customs broker
        if self.customs_broker_id:
            self.message_post(
                body=f"Shipment ready for customs clearance. Broker: {self.customs_broker_id.name}",
                subject="Customs Clearance Required",
                partner_ids=[self.customs_broker_id.id]
            )
        
        return True
    
    def action_delivered(self):
        self.ensure_one()
        
        # Validate POD is received for completed delivery
        if not self.pod_received:
            raise ValidationError(
                'Please confirm Proof of Delivery (POD) is received before marking as delivered.'
            )
        
        self.write({
            'state': 'delivered',
            'delivery_date': fields.Date.today()
        })
        self._send_delivery_notification()
        return True
    
    def action_receive_pod(self):
        """Mark POD as received"""
        self.ensure_one()
        self.write({
            'pod_received': True,
            'pod_date': fields.Date.today()
        })
        
        # Auto-create POD document if not exists
        if not self.pod_document_id:
            self.message_post(
                body="Proof of Delivery marked as received. Please upload POD document.",
                subject="POD Received"
            )
        
        return True
    
    def _send_delivery_notification(self):
        """Send delivery notification to customer"""
        self.ensure_one()
        template = self.env.ref('freight_management.email_template_shipment_delivered', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        return True
    
    def _send_status_update_notification(self):
        """Send status update notification to customer"""
        self.ensure_one()
        template = self.env.ref('freight_management.email_template_shipment_status_update', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        return True
    
    def _get_portal_return_action(self):
        """Return action for portal"""
        return {
            'type': 'ir.actions.act_url',
            'url': '/my/shipments/%s' % self.id,
            'target': 'self',
        }
    
    def action_complete(self):
        self.ensure_one()
        self.state = 'completed'
        return True
    
    def action_generate_invoice(self):
        self.ensure_one()
        
        # Validate shipment is delivered
        if self.state not in ['delivered', 'completed']:
            raise ValidationError('Shipment must be delivered before generating invoice.')
        
        # Validate POD is received
        if not self.pod_received:
            raise ValidationError('Proof of Delivery must be received before invoicing.')
        
        # Create invoice from actual costs
        invoice_lines = []
        
        if self.is_multimodal and self.leg_ids:
            # Create invoice lines from leg costs
            for leg in self.leg_ids:
                if leg.actual_cost > 0:
                    invoice_lines.append((0, 0, {
                        'name': f"{leg.name} - {leg.transport_mode}",
                        'quantity': 1,
                        'price_unit': leg.actual_cost,
                        'account_id': self.env['account.account'].search([
                            ('code', '=like', '4%')
                        ], limit=1).id,
                    }))
                
                # Add handling costs
                if leg.handling_cost > 0:
                    invoice_lines.append((0, 0, {
                        'name': f"{leg.name} - Handling Charges",
                        'quantity': 1,
                        'price_unit': leg.handling_cost,
                        'account_id': self.env['account.account'].search([
                            ('code', '=like', '4%')
                        ], limit=1).id,
                    }))
        else:
            # Single leg - use actual cost
            if self.actual_cost > 0:
                invoice_lines.append((0, 0, {
                    'name': f"Freight Charges - {self.name}",
                    'quantity': 1,
                    'price_unit': self.actual_cost,
                    'account_id': self.env['account.account'].search([
                        ('code', '=like', '4%')
                    ], limit=1).id,
                }))
        
        # Add customs duty if applicable
        if self.duty_amount > 0:
            invoice_lines.append((0, 0, {
                'name': 'Customs Duty',
                'quantity': 1,
                'price_unit': self.duty_amount,
                'account_id': self.env['account.account'].search([
                    ('code', '=like', '4%')
                ], limit=1).id,
            }))
        
        # Add insurance if applicable
        if self.is_insured and self.insurance_amount > 0:
            invoice_lines.append((0, 0, {
                'name': 'Freight Insurance',
                'quantity': 1,
                'price_unit': self.insurance_amount,
                'account_id': self.env['account.account'].search([
                    ('code', '=like', '4%')
                ], limit=1).id,
            }))
        
        if not invoice_lines:
            raise ValidationError('No costs to invoice. Please enter actual costs first.')
        
        # Create invoice
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines,
            'ref': self.name,
            'shipment_id': self.id,
            'payment_term_id': self.payment_term_id.id if self.payment_term_id else False,
        })
        
        self.state = 'invoiced'
        
        return {
            'name': 'Customer Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }
    
    def action_create_vendor_bills(self):
        """Create vendor bills for carrier and service provider costs"""
        self.ensure_one()
        
        if self.vendor_bills_created:
            raise ValidationError('Vendor bills have already been created for this shipment.')
        
        bills_created = []
        
        if self.is_multimodal and self.leg_ids:
            # Create vendor bills per carrier/leg
            for leg in self.leg_ids:
                if leg.carrier_id and leg.actual_cost > 0:
                    bill = self.env['account.move'].create({
                        'move_type': 'in_invoice',
                        'partner_id': leg.carrier_id.id,
                        'invoice_date': fields.Date.today(),
                        'ref': f"{self.name} - {leg.name}",
                        'shipment_id': self.id,
                        'invoice_line_ids': [(0, 0, {
                            'name': f"Freight Service - {leg.name}",
                            'quantity': 1,
                            'price_unit': leg.actual_cost,
                            'account_id': self.env['account.account'].search([
                                ('code', '=like', '6%')
                            ], limit=1).id,
                        })]
                    })
                    bills_created.append(bill.id)
        else:
            # Single carrier bill
            if self.carrier_id and self.actual_cost > 0:
                bill = self.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'partner_id': self.carrier_id.id,
                    'invoice_date': fields.Date.today(),
                    'ref': self.name,
                    'shipment_id': self.id,
                    'invoice_line_ids': [(0, 0, {
                        'name': f"Freight Service - {self.name}",
                        'quantity': 1,
                        'price_unit': self.actual_cost,
                        'account_id': self.env['account.account'].search([
                            ('code', '=like', '6%')
                        ], limit=1).id,
                    })]
                })
                bills_created.append(bill.id)
        
        # Create customs broker bill if applicable
        if self.customs_broker_id and self.duty_amount > 0:
            bill = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': self.customs_broker_id.id,
                'invoice_date': fields.Date.today(),
                'ref': f"{self.name} - Customs",
                'shipment_id': self.id,
                'invoice_line_ids': [(0, 0, {
                    'name': f"Customs Clearance - {self.name}",
                    'quantity': 1,
                    'price_unit': self.duty_amount,
                    'account_id': self.env['account.account'].search([
                        ('code', '=like', '6%')
                    ], limit=1).id,
                })]
            })
            bills_created.append(bill.id)
        
        if not bills_created:
            raise ValidationError('No vendor costs to bill. Please enter actual costs and assign carriers.')
        
        self.vendor_bills_created = True
        
        return {
            'name': 'Vendor Bills',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bills_created)],
            'target': 'current',
        }
    
    def action_view_containers(self):
        self.ensure_one()
        return {
            'name': 'Containers',
            'type': 'ir.actions.act_window',
            'res_model': 'freight.container',
            'view_mode': 'tree,form',
            'domain': [('shipment_id', '=', self.id)],
            'context': {'default_shipment_id': self.id}
        }
    
    def action_view_documents(self):
        self.ensure_one()
        return {
            'name': 'Documents',
            'type': 'ir.actions.act_window',
            'res_model': 'freight.shipment.document',
            'view_mode': 'tree,form',
            'domain': [('shipment_id', '=', self.id)],
            'context': {'default_shipment_id': self.id}
        }
    
    def action_view_invoices(self):
        self.ensure_one()
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('move_type', '=', 'out_invoice'), ('shipment_id', '=', self.id)],
            'context': {'default_shipment_id': self.id, 'default_move_type': 'out_invoice'}
        }
    
    def action_view_legs(self):
        self.ensure_one()
        return {
            'name': 'Transport Legs',
            'type': 'ir.actions.act_window',
            'res_model': 'freight.transport.leg',
            'view_mode': 'tree,form',
            'domain': [('shipment_id', '=', self.id)],
            'context': {'default_shipment_id': self.id}
        }
    
    def action_add_leg(self):
        """Add a new transport leg"""
        self.ensure_one()
        
        # Get the last leg to set defaults
        last_leg = self.leg_ids.sorted('sequence', reverse=True)[:1]
        
        # Auto-calculate next sequence
        next_sequence = (last_leg.sequence + 10) if last_leg else 10
        
        vals = {
            'shipment_id': self.id,
            'sequence': next_sequence,
        }
        
        # If there's a last leg, set origin as its destination
        if last_leg:
            vals['origin_location_id'] = last_leg.destination_location_id.id
            vals['estimated_departure'] = last_leg.estimated_arrival
            vals['carrier_id'] = last_leg.carrier_id.id  # Suggest same carrier
        else:
            # First leg - use shipment origin
            if self.origin_port_id:
                vals['origin_location_id'] = self.origin_port_id.id
        
        # If this will be the last leg, set destination to shipment destination
        if self.destination_port_id and not last_leg:
            vals['destination_location_id'] = self.destination_port_id.id
        
        return {
            'name': 'Add Transport Leg',
            'type': 'ir.actions.act_window',
            'res_model': 'freight.transport.leg',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_shipment_id': self.id, **vals}
        }
    
    def action_optimize_route(self):
        """Suggest optimized multi-modal routes"""
        self.ensure_one()
        
        # TODO: Implement route optimization algorithm
        # This would analyze available carriers, schedules, costs, and transit times
        # to suggest optimal multi-modal routes
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Route Optimization',
                'message': 'Route optimization feature coming soon!',
                'type': 'info',
                'sticky': False,
            }
        }

    def get_tracking_milestones(self):
        """Get tracking milestones for shipment"""
        self.ensure_one()
        
        if self.is_multimodal and self.leg_ids:
            # For multi-modal, return leg-based milestones
            milestones = []
            for leg in self.leg_ids.sorted('sequence'):
                leg_milestones = leg.get_milestone_data()
                milestones.append({
                    'leg_sequence': leg.sequence,
                    'leg_name': leg.name,
                    'transport_mode': leg.transport_mode,
                    'origin': leg.origin_location_id.name,
                    'destination': leg.destination_location_id.name,
                    'status': leg.state,
                    'milestones': leg_milestones,
                    'is_delayed': leg.is_delayed,
                    'delay_hours': leg.delay_hours,
                })
            
            # Calculate overall progress
            total_legs = len(self.leg_ids)
            completed_legs = len(self.leg_ids.filtered(lambda l: l.state == 'completed'))
            progress = int((completed_legs / total_legs) * 100) if total_legs > 0 else 0
            
            return {
                'is_multimodal': True,
                'legs': milestones,
                'progress': progress,
                'current_state': self.state,
            }
        else:
            # Original single-leg tracking
            milestones = [
                {'id': 1, 'name': 'Draft', 'state': 'draft', 'completed': self.state != 'draft', 'date': self.create_date},
                {'id': 2, 'name': 'Booked', 'state': 'booked', 'completed': self.state not in ['draft'], 'date': self.booking_date},
                {'id': 3, 'name': 'In Operation', 'state': 'in_operation', 'completed': self.state not in ['draft', 'booked'], 'date': ''},
                {'id': 4, 'name': 'In Transit', 'state': 'in_transit', 'completed': self.state not in ['draft', 'booked', 'in_operation'], 'date': self.sailing_date},
                {'id': 5, 'name': 'Arrived', 'state': 'arrived', 'completed': self.state not in ['draft', 'booked', 'in_operation', 'in_transit'], 'date': self.arrival_date},
                {'id': 6, 'name': 'Customs Clearance', 'state': 'customs_clearance', 'completed': self.state not in ['draft', 'booked', 'in_operation', 'in_transit', 'arrived'], 'date': ''},
                {'id': 7, 'name': 'Delivered', 'state': 'delivered', 'completed': self.state not in ['draft', 'booked', 'in_operation', 'in_transit', 'arrived', 'customs_clearance'], 'date': self.delivery_date},
                {'id': 8, 'name': 'Completed', 'state': 'completed', 'completed': self.state == 'completed', 'date': ''},
            ]
            
            # Calculate progress percentage
            state_order = ['draft', 'booked', 'in_operation', 'in_transit', 'arrived', 'customs_clearance', 'delivered', 'completed']
            current_index = state_order.index(self.state) if self.state in state_order else 0
            progress = int((current_index / (len(state_order) - 1)) * 100)
            
            return {
                'is_multimodal': False,
                'milestones': milestones,
                'current_state': self.state,
                'progress': progress,
            }

    def get_map_data(self):
        """Get map data for route visualization"""
        self.ensure_one()
        
        if self.is_multimodal and self.leg_ids:
            # Multi-modal route with multiple legs
            legs_data = []
            for leg in self.leg_ids.sorted('sequence'):
                legs_data.append({
                    'sequence': leg.sequence,
                    'transport_mode': leg.transport_mode,
                    'origin': {
                        'name': leg.origin_location_id.name,
                        'code': leg.origin_location_id.code,
                        'lat': leg.origin_location_id.latitude,
                        'lng': leg.origin_location_id.longitude,
                    },
                    'destination': {
                        'name': leg.destination_location_id.name,
                        'code': leg.destination_location_id.code,
                        'lat': leg.destination_location_id.latitude,
                        'lng': leg.destination_location_id.longitude,
                    },
                    'status': leg.state,
                    'is_transshipment': leg.is_transshipment_point,
                })
            
            return {
                'is_multimodal': True,
                'legs': legs_data,
            }
        else:
            # Single leg route
            return {
                'is_multimodal': False,
                'origin': {
                    'name': self.origin_port_id.name,
                    'code': self.origin_port_id.code,
                    'lat': self.origin_port_id.latitude,
                    'lng': self.origin_port_id.longitude,
                },
                'destination': {
                    'name': self.destination_port_id.name,
                    'code': self.destination_port_id.code,
                    'lat': self.destination_port_id.latitude,
                    'lng': self.destination_port_id.longitude,
                },
                'route': [],
            }


    @api.model
    def _cron_send_payment_reminders(self):
        """Scheduled action to send payment reminders for overdue invoices"""
        overdue_shipments = self.search([
            ('payment_status', '=', 'overdue'),
            ('state', 'in', ['delivered', 'completed', 'invoiced'])
        ])
        
        for shipment in overdue_shipments:
            overdue_invoices = shipment.invoice_ids.filtered(
                lambda inv: inv.state == 'posted' and 
                inv.payment_state in ['not_paid', 'partial'] and
                inv.invoice_date_due and 
                inv.invoice_date_due < fields.Date.today()
            )
            
            if overdue_invoices:
                # Send reminder email
                shipment.message_post(
                    body=f"Payment reminder: {len(overdue_invoices)} overdue invoice(s) for shipment {shipment.name}",
                    subject="Payment Reminder",
                    partner_ids=[shipment.partner_id.id]
                )
        
        return True
    
    @api.model
    def _cron_update_shipment_status(self):
        """Scheduled action to update shipment status from carrier API"""
        # TODO: Implement carrier API integration
        # This would fetch real-time tracking updates from carrier systems
        active_shipments = self.search([
            ('state', 'in', ['in_transit', 'in_operation'])
        ])
        
        for shipment in active_shipments:
            # Placeholder for API integration
            pass
        
        return True
