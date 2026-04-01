# Bugfix Requirements Document

## Introduction

The freight_management module fails to install in Odoo 17.0+ due to the use of deprecated `attrs` and `states` attributes in XML view files. Odoo 17.0 introduced breaking changes that removed support for these attributes in favor of new syntax using `invisible`, `readonly`, `required`, and `column_invisible` attributes with domain expressions. This bugfix ensures the module is compatible with Odoo 17.0+ by migrating all view files to use the new attribute syntax.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN attempting to install the freight_management module in Odoo 17.0+ THEN the system raises an error "Since 17.0, the 'attrs' and 'states' attributes are no longer used" and prevents installation

1.2 WHEN the module loader parses res_partner_views.xml at line 24 THEN the system detects the deprecated `attrs` attribute and fails validation

1.3 WHEN the module loader parses view files containing `states` attributes on buttons THEN the system detects deprecated syntax and fails validation

1.4 WHEN the module loader parses view files containing `attrs` attributes on fields THEN the system detects deprecated syntax and fails validation

### Expected Behavior (Correct)

2.1 WHEN attempting to install the freight_management module in Odoo 17.0+ THEN the system SHALL successfully install the module without errors

2.2 WHEN the module loader parses res_partner_views.xml THEN the system SHALL accept the new `invisible` attribute syntax with domain expressions

2.3 WHEN the module loader parses view files containing buttons with state-based visibility THEN the system SHALL accept the new `invisible` attribute with state domain expressions

2.4 WHEN the module loader parses view files containing fields with conditional visibility, readonly, or required attributes THEN the system SHALL accept the new attribute syntax with domain expressions

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a partner has is_customs_broker set to False THEN the system SHALL CONTINUE TO hide the "Customs Broker Information" group

3.2 WHEN a partner has is_customs_broker set to True THEN the system SHALL CONTINUE TO show the "Customs Broker Information" group with broker_license_number and broker_license_expiry fields

3.3 WHEN a freight surcharge has calculation_method set to 'fixed' THEN the system SHALL CONTINUE TO show the amount and currency_id fields and hide the percentage field

3.4 WHEN a freight surcharge has calculation_method set to 'percentage' THEN the system SHALL CONTINUE TO show the percentage field and hide the amount and currency_id fields

3.5 WHEN a freight shipment has is_insured set to False THEN the system SHALL CONTINUE TO hide the insurance_policy_number and insurance_amount fields

3.6 WHEN a freight shipment has is_insured set to True THEN the system SHALL CONTINUE TO show the insurance_policy_number and insurance_amount fields

3.7 WHEN a freight rate has service_type not equal to 'fcl' THEN the system SHALL CONTINUE TO hide the container_type field

3.8 WHEN a freight rate has service_type equal to 'fcl' THEN the system SHALL CONTINUE TO show and require the container_type field

3.9 WHEN a freight quotation has service_type not equal to 'fcl' THEN the system SHALL CONTINUE TO hide the container_type and container_qty fields

3.10 WHEN a freight quotation has service_type equal to 'fcl' THEN the system SHALL CONTINUE TO show the container_type and container_qty fields

3.11 WHEN a freight container has condition not equal to 'damaged' THEN the system SHALL CONTINUE TO hide the damage_description field

3.12 WHEN a freight container has condition equal to 'damaged' THEN the system SHALL CONTINUE TO show the damage_description field

3.13 WHEN a freight shipment is in 'draft' state THEN the system SHALL CONTINUE TO show the "Book" button and hide other action buttons

3.14 WHEN a freight shipment is in 'booked' state THEN the system SHALL CONTINUE TO show the "Start Operation" button and hide other action buttons

3.15 WHEN a freight shipment is in 'in_operation' state THEN the system SHALL CONTINUE TO show the "In Transit" button and hide other action buttons

3.16 WHEN a freight shipment is in 'in_transit' state THEN the system SHALL CONTINUE TO show the "Arrived" button and hide other action buttons

3.17 WHEN a freight shipment is in 'arrived' state THEN the system SHALL CONTINUE TO show the "Customs Clearance" button and hide other action buttons

3.18 WHEN a freight shipment is in 'customs_clearance' state THEN the system SHALL CONTINUE TO show the "Delivered" button and hide other action buttons

3.19 WHEN a freight shipment is in 'delivered' state THEN the system SHALL CONTINUE TO show the "Complete" button and hide other action buttons

3.20 WHEN a freight quotation is in 'draft' state THEN the system SHALL CONTINUE TO show the "Send to Customer" and "Cancel" buttons

3.21 WHEN a freight quotation is in 'sent' state THEN the system SHALL CONTINUE TO show the "Approve" and "Cancel" buttons

3.22 WHEN a freight quotation is in 'cancelled' state THEN the system SHALL CONTINUE TO show the "Set to Draft" button

3.23 WHEN a freight container is in 'allocated' state THEN the system SHALL CONTINUE TO show the "Gate In" button

3.24 WHEN a freight container is in 'gate_in', 'loaded', 'in_transit', or 'discharged' state THEN the system SHALL CONTINUE TO show the "Gate Out" button

3.25 WHEN a freight container is in 'gate_out' state THEN the system SHALL CONTINUE TO show the "Return" button

3.26 WHEN a freight booking is in 'draft' state THEN the system SHALL CONTINUE TO show the "Confirm" and "Cancel" buttons

3.27 WHEN a freight booking is in 'confirmed' state THEN the system SHALL CONTINUE TO show the "Allocate Containers" and "Cancel" buttons

3.28 WHEN a freight booking is in 'allocated' state THEN the system SHALL CONTINUE TO show the "Create Shipment" button

3.29 WHEN freight_config has edi_enabled set to False THEN the system SHALL CONTINUE TO hide the EDI configuration section

3.30 WHEN freight_config has edi_enabled set to True THEN the system SHALL CONTINUE TO show the EDI configuration section
