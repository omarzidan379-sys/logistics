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

        this._showLoading();

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

    _showLoading: function () {
        const resultDiv = this.$('#tracking_result');
        const skeletonHtml = `
            <div class="shimmer-skeleton shimmer-card animate-fadeInUp"></div>
            <div class="freight-progress-container mt-4 animate-fadeInUp delay-1">
                <div class="shimmer-skeleton shimmer-line long"></div>
                <div class="shimmer-skeleton shimmer-line medium"></div>
            </div>
            <div class="gw-right-column mt-4 animate-fadeInUp delay-2">
                <div class="shimmer-skeleton shimmer-card"></div>
                <div class="shimmer-skeleton shimmer-card"></div>
            </div>
        `;
        resultDiv.html(skeletonHtml).show();
    },

    _showTrackingResult: function (shipment) {
        const resultDiv = this.$('#tracking_result');
        
        let currentState = shipment.state;
        let progressPct = 0;
        if (currentState === 'draft' || currentState === 'quoted') progressPct = 20;
        else if (currentState === 'confirmed' || currentState === 'booked') progressPct = 40;
        else if (currentState === 'in_transit') progressPct = 60;
        else if (currentState === 'customs_clearance') progressPct = 80;
        else if (currentState === 'delivered' || currentState === 'completed') progressPct = 100;
        else progressPct = 10;

        let html = `
            <div class="card animate-fadeInUp">
                <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
                    <h4 class="mb-0"><i class="fa fa-ship me-2"></i> ${shipment.name}</h4>
                    ${this._formatBadge(shipment.state)}
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <p class="mb-1 text-muted">Origin</p>
                            <h5 class="fw-bold text-primary">${shipment.origin}</h5>
                        </div>
                        <div class="col-md-6 mb-3 text-md-end">
                            <p class="mb-1 text-muted">Destination</p>
                            <h5 class="fw-bold text-primary">${shipment.destination}</h5>
                        </div>
                    </div>
                    <div class="row border-top pt-3">
                        <div class="col-md-6">
                            <p><strong>Shipment Date:</strong> ${shipment.shipment_date || 'N/A'}</p>
                        </div>
                        <div class="col-md-6 text-md-end">
                            ${shipment.estimated_delivery ? `<p><strong>Estimated Delivery:</strong> ${shipment.estimated_delivery}</p>` : ''}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Progress Tracker -->
            <div class="freight-progress-container mt-4 animate-fadeInUp delay-1">
                <h5 class="mb-3 fw-bold" style="color: #0c4a6e;"><i class="fa fa-tasks me-2"></i> Shipment Progress</h5>
                
                <div class="freight-workflow-steps">
                    <div class="freight-workflow-step ${progressPct >= 20 ? 'completed' : ''}">
                        <div class="step-circle">${progressPct > 20 ? '<i class="fa fa-check"></i>' : '1'}</div>
                        <div class="step-label">Booking</div>
                    </div>
                    <div class="freight-workflow-step ${progressPct >= 40 ? 'completed' : (progressPct == 20 ? 'active' : '')}">
                        <div class="step-circle">${progressPct > 40 ? '<i class="fa fa-check"></i>' : '2'}</div>
                        <div class="step-label">Confirmed</div>
                    </div>
                    <div class="freight-workflow-step ${progressPct >= 60 ? 'completed' : (progressPct == 40 ? 'active' : '')}">
                        <div class="step-circle">${progressPct > 60 ? '<i class="fa fa-check"></i>' : '3'}</div>
                        <div class="step-label">In Transit</div>
                    </div>
                    <div class="freight-workflow-step ${progressPct >= 80 ? 'completed' : (progressPct == 60 ? 'active' : '')}">
                        <div class="step-circle">${progressPct > 80 ? '<i class="fa fa-check"></i>' : '4'}</div>
                        <div class="step-label">Customs</div>
                    </div>
                    <div class="freight-workflow-step ${progressPct >= 100 ? 'completed' : (progressPct == 80 ? 'active' : '')}">
                        <div class="step-circle">${progressPct >= 100 ? '<i class="fa fa-check"></i>' : '5'}</div>
                        <div class="step-label">Delivered</div>
                    </div>
                </div>

                <div class="freight-progress-bar mt-3">
                    <div class="progress-fill ${progressPct >= 100 ? 'completed' : ''}" style="width: ${progressPct}%;"></div>
                </div>
                <div class="freight-progress-label">
                    <span>Overall Status</span>
                    <span class="progress-percentage">${progressPct}%</span>
                </div>
            </div>
        `;

        if (shipment.transport_legs && shipment.transport_legs.length > 0) {
            html += `
                <h5 class="mt-4 mb-3 fw-bold animate-fadeInUp delay-2" style="color: #0c4a6e;">
                    <i class="fa fa-route me-2"></i> Transport Journey
                </h5>
                <div class="gw-right-column animate-fadeInUp delay-3">
            `;
            
            shipment.transport_legs.forEach((leg, index) => {
                const animDelay = parseInt(index) + 3;
                html += `
                    <div class="gw-action-card d-flex align-items-center text-start p-3" style="animation-delay: 0.${animDelay}s;">
                        <div class="gw-ac-icon me-3 mb-0 text-primary" style="font-size: 24px;">
                            ${leg.transport_mode === 'sea' ? '<i class="fa fa-ship"></i>' : leg.transport_mode === 'air' ? '<i class="fa fa-plane"></i>' : '<i class="fa fa-truck"></i>'}
                        </div>
                        <div class="flex-grow-1">
                            <h6 class="mb-1 text-dark fw-bold">Leg ${leg.sequence}: ${leg.transport_mode.toUpperCase()}</h6>
                            <p class="mb-0 text-muted small">${leg.origin} <i class="fa fa-arrow-right mx-1"></i> ${leg.destination}</p>
                        </div>
                        <div>
                            ${this._formatBadge(leg.status)}
                        </div>
                        <div class="gw-ac-bg"></div>
                    </div>
                `;
            });
            html += '</div>';
        }

        resultDiv.html(html).show();
    },

    _showError: function (message) {
        const resultDiv = this.$('#tracking_result');
        resultDiv.html(`
            <div class="alert alert-danger animate-fadeInUp shadow-sm text-center">
                <i class="fa fa-exclamation-triangle fa-2x mb-2 d-block"></i>
                <span class="fw-bold d-block">${message}</span>
                <span class="d-block small mt-1">Please check the number and try again.</span>
            </div>
        `).show();
    },

    _formatBadge: function (status) {
        const statusMap = {
            'draft': '<span class="badge badge-draft px-3 py-2">Draft</span>',
            'confirmed': '<span class="badge badge-info px-3 py-2">Confirmed</span>',
            'in_transit': '<span class="badge badge-primary px-3 py-2">In Transit</span>',
            'delivered': '<span class="badge badge-success px-3 py-2">Delivered</span>',
            'pending': '<span class="badge badge-secondary px-3 py-2">Pending</span>',
            'in_progress': '<span class="badge badge-primary px-3 py-2">In Progress</span>',
            'completed': '<span class="badge badge-success px-3 py-2">Completed</span>',
            'customs_clearance': '<span class="badge badge-customs_clearance px-3 py-2">Customs</span>',
        };
        return statusMap[status] || `<span class="badge badge-secondary px-3 py-2">${status}</span>`;
    },
});

export default publicWidget.registry.FreightTracking;
