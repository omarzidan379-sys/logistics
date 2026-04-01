/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.FreightTracking = publicWidget.Widget.extend({
    selector: '#tracking_form',
    events: {
        'submit': '_onSubmitTracking',
    },

    _onSubmitTracking: function (ev) {
        ev.preventDefault();
        const trackingNumber = this.$('#tracking_number').val();
        
        if (!trackingNumber) {
            this._showError('Please enter a tracking number');
            return;
        }

        jsonrpc('/freight/track/search', {
            tracking_number: trackingNumber,
        }).then((result) => {
            if (result.error) {
                this._showError(result.error);
            } else {
                this._showTrackingResult(result.shipment);
            }
        });
    },

    _showTrackingResult: function (shipment) {
        const resultDiv = this.$('#tracking_result');
        let html = `
            <div class="alert alert-success">
                <h5>Shipment Found: ${shipment.name}</h5>
                <p><strong>Status:</strong> ${this._formatStatus(shipment.state)}</p>
                <p><strong>Origin:</strong> ${shipment.origin}</p>
                <p><strong>Destination:</strong> ${shipment.destination}</p>
                <p><strong>Shipment Date:</strong> ${shipment.shipment_date}</p>
                ${shipment.estimated_delivery ? `<p><strong>Estimated Delivery:</strong> ${shipment.estimated_delivery}</p>` : ''}
            </div>
        `;

        if (shipment.transport_legs && shipment.transport_legs.length > 0) {
            html += '<h6>Transport Journey:</h6><div class="list-group">';
            shipment.transport_legs.forEach((leg) => {
                html += `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">Leg ${leg.sequence}: ${leg.transport_mode}</h6>
                            <small>${this._formatStatus(leg.status)}</small>
                        </div>
                        <p class="mb-1">${leg.origin} → ${leg.destination}</p>
                    </div>
                `;
            });
            html += '</div>';
        }

        resultDiv.html(html).show();
    },

    _showError: function (message) {
        const resultDiv = this.$('#tracking_result');
        resultDiv.html(`<div class="alert alert-danger">${message}</div>`).show();
    },

    _formatStatus: function (status) {
        const statusMap = {
            'draft': '<span class="badge bg-secondary">Draft</span>',
            'confirmed': '<span class="badge bg-info">Confirmed</span>',
            'in_transit': '<span class="badge bg-primary">In Transit</span>',
            'delivered': '<span class="badge bg-success">Delivered</span>',
            'pending': '<span class="badge bg-secondary">Pending</span>',
            'in_progress': '<span class="badge bg-primary">In Progress</span>',
            'completed': '<span class="badge bg-success">Completed</span>',
        };
        return statusMap[status] || status;
    },
});

export default publicWidget.registry.FreightTracking;
