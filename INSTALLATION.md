# Freight Management System - Installation Guide

## ✅ MODULE IS NOW COMPLETE!

All files have been created and the module is ready to install in Odoo 17.

## Installation Steps

1. **Copy Module to Addons Directory**
   ```
   Copy the entire `freight_management` folder to your Odoo addons directory
   Example: /opt/odoo/addons/freight_management
   ```

2. **Restart Odoo Server**
   ```bash
   sudo systemctl restart odoo
   # OR
   python3 odoo-bin -c /etc/odoo/odoo.conf
   ```

3. **Update Apps List**
   - Log in to Odoo
   - Go to Apps menu
   - Click "Update Apps List" button
   - Click "Update" in the confirmation dialog

4. **Install the Module**
   - In Apps menu, remove the "Apps" filter
   - Search for "Freight Management System"
   - Click "Install"

## Module Structure

```
freight_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── freight_location.py
│   ├── res_partner.py
│   ├── freight_charge_type.py
│   ├── freight_config.py
│   ├── freight_rate.py
│   ├── freight_surcharge.py
│   ├── freight_quotation.py
│   ├── freight_quotation_line.py
│   ├── freight_booking.py
│   ├── freight_container.py
│   ├── freight_shipment.py
│   └── freight_shipment_document.py
├── views/
│   ├── freight_location_views.xml
│   ├── res_partner_views.xml
│   ├── freight_charge_type_views.xml
│   ├── freight_config_views.xml
│   ├── freight_rate_views.xml
│   ├── freight_surcharge_views.xml
│   ├── freight_quotation_views.xml
│   ├── freight_booking_views.xml
│   ├── freight_container_views.xml
│   ├── freight_shipment_views.xml
│   ├── freight_shipment_document_views.xml
│   └── freight_menu.xml
├── reports/
│   └── quotation_report.xml
├── security/
│   ├── freight_security.xml
│   └── ir.model.access.csv
├── data/
│   ├── freight_charge_type_data.xml
│   ├── freight_quotation_sequence.xml
│   ├── freight_booking_sequence.xml
│   └── freight_shipment_sequence.xml
└── static/
    └── description/
        └── index.html
```

## Features Included

### Core Features
- ✅ Freight locations (ports, airports, warehouses)
- ✅ Partner extensions (carriers, shippers, consignees, agents, customs brokers)
- ✅ Charge types and pricing components
- ✅ System configuration

### Pricing Features
- ✅ Freight quotations with approval workflow
- ✅ Rate tables and surcharge management
- ✅ Automatic pricing calculations
- ✅ PDF quotation reports
- ✅ Chargeable weight calculations (volumetric vs actual)

### Operations Features
- ✅ Booking management with carrier allocation
- ✅ Shipment tracking with milestone management
- ✅ Container tracking with demurrage/detention calculations
- ✅ Document management
- ✅ State machine workflow

## Dependencies

The module requires these Odoo modules (automatically installed):
- base
- mail
- web
- sale_management
- account

## After Installation

1. **Configure Settings**
   - Go to Freight → Configuration → Settings
   - Set default free time days
   - Set demurrage and detention rates
   - Configure EDI if needed

2. **Set Up Master Data**
   - Create freight locations (ports, airports)
   - Set up partners (carriers, shippers, consignees)
   - Configure charge types (already pre-loaded with defaults)

3. **Create Rate Tables**
   - Go to Freight → Pricing → Rates
   - Add your freight rates

4. **Start Using**
   - Create quotations
   - Convert to bookings
   - Track shipments
   - Manage containers

## Troubleshooting

If the module doesn't appear in the apps list:
1. Check Odoo logs for errors: `tail -f /var/log/odoo/odoo.log`
2. Verify all files are in the correct location
3. Ensure file permissions are correct: `chmod -R 755 freight_management`
4. Restart Odoo server again

## Support

For issues or questions, refer to the design documents in:
`.kiro/specs/odoo-freight-forwarding-system/`

## License

LGPL-3
