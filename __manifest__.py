# -*- coding: utf-8 -*-
{
    'name': 'Freight Management System',
    'version': '17.0.1.0.0',
    'category': 'Operations/Freight',
    'summary': 'Complete Freight Forwarding Management System for Odoo 17',
    'description': """
        Freight Management System
        =========================
        Complete freight forwarding and logistics management solution.
        
        Core Features:
        * Freight locations (ports, airports, warehouses)
        * Partner extensions for freight operations
        * Charge types and pricing components
        * System configuration
        
        Pricing Features:
        * Freight quotations with approval workflow
        * Rate tables and surcharge management
        * Automatic pricing calculations
        * PDF quotation reports
        * Chargeable weight calculations
        
        Operations Features:
        * Booking management with carrier allocation
        * Shipment tracking with milestone management
        * Container tracking and demurrage calculation
        * Document management
        * State machine workflow
        
        This module provides end-to-end freight forwarding operations including
        quotations, bookings, shipments, container tracking, and financial management.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'mail', 'web', 'sale_management', 'account', 'portal', 'website'],
    'data': [
        # Security
        'security/freight_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/freight_charge_type_data.xml',
        'data/freight_quotation_sequence.xml',
        'data/freight_booking_sequence.xml',
        'data/freight_shipment_sequence.xml',
        'data/freight_demo_data.xml',
        'data/email_templates.xml',
        'data/freight_cron.xml',
        
        # Views - Core
        'views/freight_location_views.xml',
        'views/res_partner_views.xml',
        'views/freight_charge_type_views.xml',
        'views/freight_config_views.xml',
        
        # Views - Pricing
        'views/freight_rate_views.xml',
        'views/freight_surcharge_views.xml',
        'views/freight_quotation_views.xml',
        
        # Views - Operations
        'views/freight_booking_views.xml',
        'views/freight_transport_leg_views.xml',
        'views/freight_container_views.xml',
        'views/freight_shipment_views.xml',
        'views/freight_shipment_document_views.xml',
        
        # Reports
        'reports/quotation_report.xml',
        
        # Menus (load after all views with actions but before dashboard)
        'views/freight_menu.xml',
        
        # Dashboard (references menu items, must load after menus)
        'views/freight_dashboard_views.xml',
        
        # Portal
        'views/portal_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'freight_management/static/src/css/freight_management.css',
            'freight_management/static/src/css/freight_dashboard_enhanced.css',
            'freight_management/static/src/js/freight_background_animations.js',
            'freight_management/static/src/js/freight_quotation.js',
            'freight_management/static/src/js/freight_dashboard_enhanced.js',
            'freight_management/static/src/js/freight_shipment_tracking.js',
            'freight_management/static/src/js/freight_rate_calculator.js',
            'freight_management/static/src/js/freight_container_tracker.js',
            'freight_management/static/src/js/freight_booking_wizard.js',
            'freight_management/static/src/js/freight_map_widget.js',
            'freight_management/static/src/xml/freight_templates.xml',
            'freight_management/static/src/xml/freight_dashboard_enhanced.xml',
        ],
        'web.assets_frontend': [
            'freight_management/static/src/css/freight_management.css',
            'freight_management/static/src/css/portal_freight.css',
            'freight_management/static/src/js/portal_tracking.js',
            'freight_management/static/src/js/portal_quote.js',
            'freight_management/static/src/js/portal_dashboard.js',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
