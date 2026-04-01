/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.FreightPortalDashboard = publicWidget.Widget.extend({
    selector: '.freight_portal_dashboard',
    
    start: function () {
        this._super.apply(this, arguments);
        this._loadDashboardData();
    },
    
    _loadDashboardData: function () {
        // Load real-time dashboard statistics
        const shipmentCount = this.$('.shipment_count').text();
        const quotationCount = this.$('.quotation_count').text();
        const bookingCount = this.$('.booking_count').text();
        
        // Animate counters
        this._animateCounter('.shipment_count', shipmentCount);
        this._animateCounter('.quotation_count', quotationCount);
        this._animateCounter('.booking_count', bookingCount);
    },
    
    _animateCounter: function (selector, target) {
        const element = this.$(selector);
        const duration = 1000;
        const start = 0;
        const end = parseInt(target) || 0;
        const increment = end / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= end) {
                element.text(end);
                clearInterval(timer);
            } else {
                element.text(Math.floor(current));
            }
        }, 16);
    },
});

export default publicWidget.registry.FreightPortalDashboard;
