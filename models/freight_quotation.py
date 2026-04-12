# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class FreightQuotation(models.Model):
    _name = 'freight.quotation'
    _description = 'Freight Quotation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'create_date desc, name desc'

    name = fields.Char(string='Quotation Number', required=True, copy=False, readonly=True,
                       default=lambda self: 'New')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    contact_id = fields.Many2one('res.partner', string='Contact Person',
                                  domain="[('parent_id', '=', partner_id)]")
    quotation_date = fields.Date(string='Quotation Date', required=True, 
                                  default=fields.Date.today, tracking=True)
    validity_date = fields.Date(string='Valid Until', required=True,
                                 default=lambda self: fields.Date.today() + timedelta(days=30))
    
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
    ], string='Direction', required=True, default='export')
    
    # Route Information
    origin_port_id = fields.Many2one('freight.location', string='Origin Port', required=True,
                                      domain=[('location_type', 'in', ['port', 'airport'])])
    destination_port_id = fields.Many2one('freight.location', string='Destination Port', required=True,
                                          domain=[('location_type', 'in', ['port', 'airport'])])
    origin_address = fields.Text(string='Origin Address')
    destination_address = fields.Text(string='Destination Address')
    
    # Cargo Details
    cargo_description = fields.Text(string='Cargo Description', required=True)
    commodity_id = fields.Many2one('product.product', string='Commodity')
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
    container_qty = fields.Integer(string='Container Quantity', default=1)
    total_weight = fields.Float(string='Total Weight (KG)', digits=(12, 2))
    total_volume = fields.Float(string='Total Volume (CBM)', digits=(12, 3))
    total_packages = fields.Integer(string='Total Packages')
    chargeable_weight = fields.Float(string='Chargeable Weight (KG)', compute='_compute_chargeable_weight',
                                      store=True, digits=(12, 2))
    
    # Special Cargo
    is_dangerous_goods = fields.Boolean(string='Dangerous Goods')
    is_temperature_controlled = fields.Boolean(string='Temperature Controlled')
    special_instructions = fields.Text(string='Special Instructions')
    
    # Pricing
    line_ids = fields.One2many('freight.quotation.line', 'quotation_id', string='Quotation Lines')
    subtotal_amount = fields.Monetary(string='Subtotal', compute='_compute_amounts', store=True,
                                       currency_field='currency_id')
    tax_amount = fields.Monetary(string='Tax Amount', compute='_compute_amounts', store=True,
                                  currency_field='currency_id')
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_amounts', store=True,
                                    currency_field='currency_id', tracking=True)
    total_cost = fields.Monetary(string='Total Cost', compute='_compute_amounts', store=True,
                                  currency_field='currency_id')
    profit_amount = fields.Monetary(string='Profit', compute='_compute_profit', store=True,
                                     currency_field='currency_id')
    profit_margin = fields.Float(string='Profit Margin (%)', compute='_compute_profit', store=True,
                                  digits=(5, 2))
    minimum_profit_margin = fields.Float(string='Minimum Profit Margin (%)', default=15.0,
                                         help='Minimum acceptable profit margin for this quotation')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                   default=lambda self: self.env.company.currency_id)
    
    def action_auto_calculate_rates(self):
        """Automatically calculate rates from rate tables and add quotation lines"""
        self.ensure_one()
        
        if not self.origin_port_id or not self.destination_port_id:
            raise ValidationError('Please specify origin and destination ports first.')
        
        # Clear existing lines
        self.line_ids.unlink()
        
        # Get base freight rate
        rate_result = self.env['freight.rate'].calculate_freight_rate(
            self.origin_port_id.id,
            self.destination_port_id.id,
            self.service_type,
            self.container_type,
            self.total_weight,
            self.total_volume
        )
        
        if not rate_result.get('success'):
            raise ValidationError(rate_result.get('message', 'No rates found'))
        
        # Create freight charge line
        freight_charge_type = self.env['freight.charge.type'].search([
            ('code', '=', 'FREIGHT')
        ], limit=1)
        
        if not freight_charge_type:
            freight_charge_type = self.env['freight.charge.type'].create({
                'name': 'Ocean/Air Freight',
                'code': 'FREIGHT',
                'charge_category': 'freight'
            })
        
        self.env['freight.quotation.line'].create({
            'quotation_id': self.id,
            'sequence': 10,
            'charge_type_id': freight_charge_type.id,
            'description': f"Freight Charge - {self.origin_port_id.code} to {self.destination_port_id.code}",
            'quantity': self.container_qty or 1,
            'unit_price': rate_result['base_amount'],
            'cost_price': rate_result['base_amount'] * 0.85,  # Assume 15% markup
        })
        
        # Add surcharges
        if rate_result.get('surcharge_amount', 0) > 0:
            surcharge_type = self.env['freight.charge.type'].search([
                ('code', '=', 'SURCHARGE')
            ], limit=1)
            
            if not surcharge_type:
                surcharge_type = self.env['freight.charge.type'].create({
                    'name': 'Surcharges',
                    'code': 'SURCHARGE',
                    'charge_category': 'surcharge'
                })
            
            self.env['freight.quotation.line'].create({
                'quotation_id': self.id,
                'sequence': 20,
                'charge_type_id': surcharge_type.id,
                'description': 'Fuel & Other Surcharges',
                'quantity': 1,
                'unit_price': rate_result['surcharge_amount'],
                'cost_price': rate_result['surcharge_amount'],
            })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Rates Calculated',
                'message': f"Base rate: {rate_result['base_amount']} {rate_result['currency']}. Transit time: {rate_result.get('transit_time_days', 'N/A')} days.",
                'type': 'success',
                'sticky': False,
            }
        }
    
    # State Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('quoted', 'Quoted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Customer Action Fields
    customer_action_date = fields.Datetime(string='Customer Action Date', readonly=True, tracking=True)
    rejection_reason = fields.Text(string='Rejection Reason', readonly=True)
    
    # Additional Info
    incoterm_id = fields.Many2one('account.incoterms', string='Incoterm')
    notes = fields.Text(string='Terms and Conditions')
    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user,
                              tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                  default=lambda self: self.env.company)
    
    # Multi-Modal Support
    is_multimodal = fields.Boolean(string='Multi-Modal Quote', default=False,
                                    help='Quote for multi-modal transport')
    
    def action_create_multimodal_shipment(self):
        """Create shipment with multi-modal legs from quotation"""
        self.ensure_one()
        
        if not self.is_multimodal:
            # Standard single-leg shipment creation
            return self.action_create_shipment()
        
        # Create multi-modal shipment
        shipment = self.env['freight.shipment'].create({
            'quotation_id': self.id,
            'partner_id': self.partner_id.id,
            'shipper_id': self.partner_id.id,  # Default, user can change
            'consignee_id': self.partner_id.id,  # Default, user can change
            'service_type': self.service_type,
            'shipment_direction': self.shipment_direction,
            'origin_port_id': self.origin_port_id.id,
            'destination_port_id': self.destination_port_id.id,
            'cargo_description': self.cargo_description,
            'total_weight': self.total_weight,
            'total_volume': self.total_volume,
            'is_multimodal': True,
            'quoted_cost': self.total_amount,
        })
        
        return {
            'name': 'Multi-Modal Shipment',
            'type': 'ir.actions.act_window',
            'res_model': 'freight.shipment',
            'view_mode': 'form',
            'res_id': shipment.id,
            'target': 'current',
        }
    
    def action_create_shipment(self):
        """Create standard shipment from quotation"""
        self.ensure_one()
        
        shipment = self.env['freight.shipment'].create({
            'quotation_id': self.id,
            'partner_id': self.partner_id.id,
            'shipper_id': self.partner_id.id,
            'consignee_id': self.partner_id.id,
            'service_type': self.service_type,
            'shipment_direction': self.shipment_direction,
            'origin_port_id': self.origin_port_id.id,
            'destination_port_id': self.destination_port_id.id,
            'cargo_description': self.cargo_description,
            'total_weight': self.total_weight,
            'total_volume': self.total_volume,
            'quoted_cost': self.total_amount,
        })
        
        return {
            'name': 'Shipment',
            'type': 'ir.actions.act_window',
            'res_model': 'freight.shipment',
            'view_mode': 'form',
            'res_id': shipment.id,
            'target': 'current',
        }
    
    # Smart Buttons
    booking_count = fields.Integer(string='Bookings', compute='_compute_booking_count')
    shipment_count = fields.Integer(string='Shipments', compute='_compute_shipment_count')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('freight.quotation') or 'New'
        return super(FreightQuotation, self).create(vals)
    
    @api.depends('total_weight', 'total_volume', 'service_type')
    def _compute_chargeable_weight(self):
        for record in self:
            if record.service_type == 'air':
                # Air freight: volumetric weight = volume (CBM) * 167
                volumetric_weight = record.total_volume * 167
                record.chargeable_weight = max(record.total_weight, volumetric_weight)
            elif record.service_type == 'lcl':
                # LCL: volumetric weight = volume (CBM) * 1000
                volumetric_weight = record.total_volume * 1000
                record.chargeable_weight = max(record.total_weight, volumetric_weight)
            else:
                record.chargeable_weight = record.total_weight
    
    @api.depends('line_ids.subtotal', 'line_ids.tax_amount', 'line_ids.total')
    def _compute_amounts(self):
        for record in self:
            record.subtotal_amount = sum(line.subtotal for line in record.line_ids)
            record.tax_amount = sum(line.tax_amount for line in record.line_ids)
            record.total_amount = sum(line.total for line in record.line_ids)
            record.total_cost = sum(line.cost_price * line.quantity for line in record.line_ids)
    
    @api.depends('total_amount', 'total_cost')
    def _compute_profit(self):
        for record in self:
            record.profit_amount = record.total_amount - record.total_cost
            if record.total_amount:
                record.profit_margin = (record.profit_amount / record.total_amount) * 100
            else:
                record.profit_margin = 0.0
    
    def _compute_booking_count(self):
        for record in self:
            record.booking_count = self.env['freight.booking'].search_count([('quotation_id', '=', record.id)])
    
    def _compute_shipment_count(self):
        for record in self:
            record.shipment_count = self.env['freight.shipment'].search_count([('quotation_id', '=', record.id)])
    
    def action_send(self):
        self.ensure_one()
        
        # Validate minimum profit margin
        if self.profit_margin < self.minimum_profit_margin:
            raise ValidationError(
                f'Profit margin ({self.profit_margin:.2f}%) is below minimum acceptable margin '
                f'({self.minimum_profit_margin:.2f}%). Please adjust pricing or get manager approval.'
            )
        
        self.state = 'quoted'
        self._send_quotation_email()
        return True
    
    def _send_quotation_email(self):
        """Send quotation email to customer with portal access"""
        self.ensure_one()
        
        # Check notification preferences
        preference = self.env['freight.notification.preference'].sudo().get_or_create_preference(self.partner_id.id)
        if not preference.should_notify('quotation_sent'):
            return False
        
        template = self.env.ref('freight_management.email_template_quotation', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        return True
    
    def action_confirm(self):
        """Confirm quotation from portal"""
        self.ensure_one()
        if self.state != 'quoted':
            raise ValidationError('Only quoted quotations can be confirmed.')
        self.state = 'accepted'
        self._send_confirmation_email()
        return True
    
    def action_customer_accept(self):
        """Customer accepts quotation via portal"""
        self.ensure_one()
        
        if self.state != 'quoted':
            raise ValidationError('Only quoted quotations can be accepted.')
        
        # Check if user is authorized
        if not self.env.user.partner_id or self.env.user.partner_id.commercial_partner_id != self.partner_id.commercial_partner_id:
            raise AccessError('You are not authorized to accept this quotation.')
        
        self.write({
            'state': 'accepted',
            'customer_action_date': fields.Datetime.now()
        })
        
        # Log activity
        self.message_post(
            body=f"Quotation accepted by {self.env.user.partner_id.name} via customer portal.",
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
        
        # Send notification to sales team
        self._send_acceptance_notification()
        
        return True
    
    def action_customer_reject(self, reason=None):
        """Customer rejects quotation via portal"""
        self.ensure_one()
        
        if self.state != 'quoted':
            raise ValidationError('Only quoted quotations can be rejected.')
        
        # Check if user is authorized
        if not self.env.user.partner_id or self.env.user.partner_id.commercial_partner_id != self.partner_id.commercial_partner_id:
            raise AccessError('You are not authorized to reject this quotation.')
        
        self.write({
            'state': 'rejected',
            'customer_action_date': fields.Datetime.now(),
            'rejection_reason': reason or ''
        })
        
        # Log activity
        rejection_msg = f"Quotation rejected by {self.env.user.partner_id.name} via customer portal."
        if reason:
            rejection_msg += f"\n\nReason: {reason}"
        
        self.message_post(
            body=rejection_msg,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
        
        # Send notification to sales team
        self._send_rejection_notification(reason)
        
        return True
    
    def _send_acceptance_notification(self):
        """Send email notification to sales team when customer accepts"""
        self.ensure_one()
        
        template = self.env.ref('freight_management.email_template_quotation_accepted', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        return True
    
    def _send_rejection_notification(self, reason=None):
        """Send email notification to sales team when customer rejects"""
        self.ensure_one()
        
        template = self.env.ref('freight_management.email_template_quotation_rejected', raise_if_not_found=False)
        if template:
            # Add reason to context for email template
            ctx = dict(self.env.context, rejection_reason=reason or 'No reason provided')
            template.with_context(ctx).send_mail(self.id, force_send=True)
        return True
    
    def _send_confirmation_email(self):
        """Send confirmation email to sales team"""
        self.ensure_one()
        
        # Always send to sales team (internal notification)
        template = self.env.ref('freight_management.email_template_quotation_confirmed', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        return True
    
    def _get_portal_return_action(self):
        """Return action for portal"""
        return {
            'type': 'ir.actions.act_url',
            'url': '/my/quotations/%s' % self.id,
            'target': 'self',
        }
    
    def action_approve(self):
        self.ensure_one()
        
        # Check customer credit limit
        if self.partner_id.credit_limit > 0:
            # Get total outstanding invoices
            outstanding_invoices = self.env['account.move'].search([
                ('partner_id', '=', self.partner_id.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial'])
            ])
            
            outstanding_amount = sum(outstanding_invoices.mapped('amount_residual'))
            
            if outstanding_amount + self.total_amount > self.partner_id.credit_limit:
                raise ValidationError(
                    f'Customer credit limit exceeded! '
                    f'Outstanding: {outstanding_amount:.2f}, '
                    f'Credit Limit: {self.partner_id.credit_limit:.2f}, '
                    f'This Quote: {self.total_amount:.2f}'
                )
        
        self.state = 'accepted'
        return True
    
    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'
        return True
    
    def action_set_to_draft(self):
        self.ensure_one()
        self.state = 'draft'
        return True
    
    @api.constrains('validity_date', 'quotation_date')
    def _check_validity_date(self):
        for record in self:
            if record.validity_date < record.quotation_date:
                raise ValidationError('Validity date must be after quotation date.')
    
    def action_view_bookings(self):
        self.ensure_one()
        return {
            'name': 'Bookings',
            'type': 'ir.actions.act_window',
            'res_model': 'freight.booking',
            'view_mode': 'tree,form',
            'domain': [('quotation_id', '=', self.id)],
            'context': {'default_quotation_id': self.id}
        }
    
    def action_view_shipments(self):
        self.ensure_one()
        return {
            'name': 'Shipments',
            'type': 'ir.actions.act_window',
            'res_model': 'freight.shipment',
            'view_mode': 'tree,form',
            'domain': [('quotation_id', '=', self.id)],
            'context': {'default_quotation_id': self.id}
        }
    
    def action_create_booking(self):
        """Create booking from approved quotation"""
        self.ensure_one()
        
        if self.state != 'accepted':
            raise ValidationError('Only accepted quotations can be converted to bookings.')
        
        # Check if booking already exists
        existing_booking = self.env['freight.booking'].search([
            ('quotation_id', '=', self.id)
        ], limit=1)
        
        if existing_booking:
            return {
                'name': 'Booking',
                'type': 'ir.actions.act_window',
                'res_model': 'freight.booking',
                'view_mode': 'form',
                'res_id': existing_booking.id,
                'target': 'current',
            }
        
        # Create new booking
        booking = self.env['freight.booking'].create({
            'quotation_id': self.id,
            'partner_id': self.partner_id.id,
            'service_type': self.service_type,
            'container_type': self.container_type,
            'container_qty': self.container_qty,
        })
        
        return {
            'name': 'Booking',
            'type': 'ir.actions.act_window',
            'res_model': 'freight.booking',
            'view_mode': 'form',
            'res_id': booking.id,
            'target': 'current',
        }
    
    @api.model
    def _cron_check_expired_quotations(self):
        """Scheduled action to mark expired quotations"""
        today = fields.Date.today()
        expired_quotations = self.search([
            ('state', 'in', ['draft', 'quoted']),
            ('validity_date', '<', today)
        ])
        
        for quotation in expired_quotations:
            quotation.write({'state': 'expired'})
            quotation.message_post(
                body=f"Quotation expired on {quotation.validity_date}",
                subject="Quotation Expired"
            )
        
        return True

    @api.model
    def get_dashboard_data(self):
        """Get dashboard statistics for quotations"""
        draft_count = self.search_count([('state', '=', 'draft')])
        quoted_count = self.search_count([('state', '=', 'quoted')])
        accepted_count = self.search_count([('state', '=', 'accepted')])
        
        total_amount = sum(self.search([('state', '=', 'accepted')]).mapped('total_amount'))
        
        return {
            'draft': draft_count,
            'quoted': quoted_count,
            'accepted': accepted_count,
            'total_amount': total_amount,
        }
