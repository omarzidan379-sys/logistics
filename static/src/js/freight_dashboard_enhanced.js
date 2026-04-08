/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class FreightDashboardEnhanced extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = {
            quotations: {
                draft: 0,
                sent: 0,
                approved: 0,
                total_amount: 0
            },
            shipments: {
                draft: 0,
                confirmed: 0,
                in_transit: 0,
                delivered: 0
            },
            bookings: {
                draft: 0,
                confirmed: 0,
                total: 0
            }
        };
        this.loadData();
    }

    async loadData() {
        try {
            // Load quotation stats
            const quotationData = await this.orm.call(
                "freight.quotation",
                "get_dashboard_data",
                []
            );
            this.state.quotations = quotationData;

            // Load shipment stats
            const shipmentDraft = await this.orm.searchCount("freight.shipment", [["state", "=", "draft"]]);
            const shipmentConfirmed = await this.orm.searchCount("freight.shipment", [["state", "=", "confirmed"]]);
            const shipmentInTransit = await this.orm.searchCount("freight.shipment", [["state", "=", "in_transit"]]);
            const shipmentDelivered = await this.orm.searchCount("freight.shipment", [["state", "=", "delivered"]]);
            
            this.state.shipments = {
                draft: shipmentDraft,
                confirmed: shipmentConfirmed,
                in_transit: shipmentInTransit,
                delivered: shipmentDelivered
            };

            // Load booking stats
            const bookingDraft = await this.orm.searchCount("freight.booking", [["state", "=", "draft"]]);
            const bookingConfirmed = await this.orm.searchCount("freight.booking", [["state", "=", "confirmed"]]);
            const bookingTotal = await this.orm.searchCount("freight.booking", []);
            
            this.state.bookings = {
                draft: bookingDraft,
                confirmed: bookingConfirmed,
                total: bookingTotal
            };

            this.render();
        } catch (error) {
            console.error("Error loading dashboard data:", error);
        }
    }

    openQuotations(state) {
        const domain = state ? [["state", "=", state]] : [];
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Quotations",
            res_model: "freight.quotation",
            views: [[false, "list"], [false, "form"]],
            domain: domain,
            context: {}
        });
    }

    openShipments(state) {
        const domain = state ? [["state", "=", state]] : [];
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Shipments",
            res_model: "freight.shipment",
            views: [[false, "list"], [false, "form"]],
            domain: domain,
            context: {}
        });
    }

    openBookings(state) {
        const domain = state ? [["state", "=", state]] : [];
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Bookings",
            res_model: "freight.booking",
            views: [[false, "list"], [false, "form"]],
            domain: domain,
            context: {}
        });
    }
}

FreightDashboardEnhanced.template = "freight_management.DashboardEnhanced";

registry.category("actions").add("freight_management.dashboard_enhanced", FreightDashboardEnhanced);
