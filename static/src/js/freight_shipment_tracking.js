/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ShipmentTrackingWidget extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            milestones: [],
            currentState: "",
            progress: 0,
        });

        onMounted(() => {
            this.loadTrackingData();
        });
    }

    async loadTrackingData() {
        const shipmentId = this.props.record.resId;
        const data = await this.orm.call(
            "freight.shipment",
            "get_tracking_milestones",
            [shipmentId]
        );
        
        this.state.milestones = data.milestones || [];
        this.state.currentState = data.current_state || "";
        this.state.progress = data.progress || 0;
    }

    getStateClass(state) {
        const stateClasses = {
            draft: "text-secondary",
            booked: "text-info",
            in_operation: "text-primary",
            in_transit: "text-warning",
            arrived: "text-success",
            customs_clearance: "text-info",
            delivered: "text-success",
            completed: "text-success",
        };
        return stateClasses[state] || "text-muted";
    }

    getStateIcon(state) {
        const stateIcons = {
            draft: "fa-file-text-o",
            booked: "fa-check-circle",
            in_operation: "fa-cog",
            in_transit: "fa-ship",
            arrived: "fa-anchor",
            customs_clearance: "fa-shield",
            delivered: "fa-truck",
            completed: "fa-check-circle-o",
        };
        return stateIcons[state] || "fa-circle";
    }
}

ShipmentTrackingWidget.template = "freight_management.ShipmentTracking";
ShipmentTrackingWidget.props = {
    record: Object,
};

registry.category("fields").add("shipment_tracking", ShipmentTrackingWidget);
