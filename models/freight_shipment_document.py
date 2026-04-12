# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FreightShipmentDocument(models.Model):
    _name = 'freight.shipment.document'
    _description = 'Freight Shipment Document'
    _order = 'upload_date desc, id desc'

    shipment_id = fields.Many2one('freight.shipment', string='Shipment', required=True, ondelete='cascade')
    name = fields.Char(string='Document Name', required=True)
    document_type = fields.Selection([
        ('bl', 'Bill of Lading'),
        ('commercial_invoice', 'Commercial Invoice'),
        ('packing_list', 'Packing List'),
        ('certificate_origin', 'Certificate of Origin'),
        ('customs_declaration', 'Customs Declaration'),
        ('insurance_certificate', 'Insurance Certificate'),
        ('delivery_order', 'Delivery Order'),
        ('pod', 'Proof of Delivery'),
        ('vgm_certificate', 'VGM Certificate'),
        ('fumigation_certificate', 'Fumigation Certificate'),
        ('phytosanitary_certificate', 'Phytosanitary Certificate'),
        ('other', 'Other')
    ], string='Document Type', required=True)
    document_file = fields.Binary(string='File', required=True, attachment=True)
    file_name = fields.Char(string='File Name')
    upload_date = fields.Datetime(string='Upload Date', default=fields.Datetime.now, readonly=True)
    uploaded_by = fields.Many2one('res.users', string='Uploaded By', default=lambda self: self.env.user,
                                   readonly=True)
    notes = fields.Text(string='Notes')
    
    @api.onchange('document_type')
    def _onchange_document_type(self):
        if self.document_type:
            type_names = dict(self._fields['document_type'].selection)
            self.name = type_names.get(self.document_type, '')
    
    @api.model
    def create(self, vals):
        """Override create to send notification when document is uploaded"""
        document = super(FreightShipmentDocument, self).create(vals)
        
        # Send notification to customer
        if document.shipment_id and document.shipment_id.partner_id:
            preference = self.env['freight.notification.preference'].sudo().get_or_create_preference(
                document.shipment_id.partner_id.id
            )
            
            if preference.should_notify('document_uploaded'):
                # Post message to shipment
                document.shipment_id.message_post(
                    body=f"New document uploaded: {document.name}",
                    subject="New Document Available",
                    partner_ids=[document.shipment_id.partner_id.id],
                    message_type='notification',
                    subtype_xmlid='mail.mt_comment'
                )
        
        return document
