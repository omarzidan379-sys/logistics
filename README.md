# Freight Management System - Odoo 17

## ✅ MODULE STATUS: COMPLETE AND READY TO INSTALL!

This is a unified, complete Odoo 17 module for freight forwarding management.

## Quick Start

1. Copy `freight_management` folder to your Odoo addons directory
2. Restart Odoo server
3. Update Apps List in Odoo
4. Search for "Freight Management System"
5. Click Install

See `INSTALLATION.md` for detailed instructions.

## What's Included

### ✅ All Models (15 models)
- freight.location - Ports, airports, warehouses
- res.partner (extended) - Freight-specific partner types
- freight.charge.type - Pricing components
- freight.config - System settings
- freight.rate - Rate tables
- freight.surcharge - Additional charges
- freight.quotation - Customer quotations
- freight.quotation.line - Pricing breakdown
- freight.booking - Booking management
- **freight.transport.leg - Multi-modal transport legs (NEW!)**
- **freight.leg.document - Leg-specific documents (NEW!)**
- freight.container - Container tracking
- freight.shipment - Shipment operations
- freight.shipment.document - Document management
- account.move (extended) - Invoice integration

### ✅ All Views
- Form, tree, kanban, and search views for all models
- Complete menu structure
- Smart buttons and counters
- State management workflows

### ✅ All Data Files
- Security groups and access rights
- Sequences for all documents
- Default charge types

### ✅ Reports
- PDF quotation report

## Features

### Core Features
- Freight locations (ports, airports, warehouses)
- Partner extensions for freight operations
- Charge types and pricing components
- System configuration

### Pricing Features
- Freight quotations with approval workflow
- Rate tables and surcharge management
- Automatic pricing calculations
- PDF quotation reports
- Chargeable weight calculations (volumetric vs actual)

### Operations Features
- Booking management with carrier allocation
- **Multi-Modal Transport with multiple legs (NEW!)**
  - Support for Sea, Air, Road, and Rail transport modes
  - Multiple transport legs per shipment
  - Transshipment point management
  - Independent leg tracking and status
  - Cost aggregation across all legs
  - Transit time calculation
  - Delay impact analysis
  - Leg-specific document management
- Shipment tracking with milestone management
- Container tracking with demurrage/detention calculations
- Document management
- State machine workflow

## Complete Workflow

Quotation → Booking → Shipment → Container Tracking → Document Management → Invoicing

## Module Structure

All files are properly organized:
- `/models` - 13 Python models
- `/views` - 12 XML view files + menu
- `/reports` - PDF report templates
- `/security` - Groups and access rights
- `/data` - Sequences and default data
- `/static` - Module description

## Dependencies
- base
- mail
- web
- sale_management
- account

## Installation

See `INSTALLATION.md` for complete installation instructions.

## Support

For detailed specifications, see:
- `.kiro/specs/odoo-freight-forwarding-system/requirements.md`
- `.kiro/specs/odoo-freight-forwarding-system/design.md`
- `.kiro/specs/odoo-freight-forwarding-system/tasks.md`
