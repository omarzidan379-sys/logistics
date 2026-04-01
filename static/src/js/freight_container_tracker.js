/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ContainerTrackerWidget extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({
            containers: [],
            selectedContainer: null,
            demurrageInfo: null,
            loading: true,
        });

        onMounted(() => {
            this.loadContainers();
        });
    }

    async loadContainers() {
        const shipmentId = this.props.record.resId;
        try {
            const containers = await this.orm.searchRead(
                "freight.container",
                [["shipment_id", "=", shipmentId]],
                ["name", "container_type", "state", "vgm_weight", "demurrage_days", "demurrage_amount"]
            );
            this.state.containers = containers;
        } catch (error) {
            this.notification.add("Error loading containers", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async selectContainer(containerId) {
        this.state.selectedContainer = containerId;
        try {
            const demurrage = await this.orm.call(
                "freight.container",
                "get_demurrage_info",
                [containerId]
            );
            this.state.demurrageInfo = demurrage;
        } catch (error) {
            this.notification.add("Error loading demurrage info", { type: "danger" });
        }
    }

    getStateColor(state) {
        const colors = {
            available: "secondary",
            allocated: "info",
            gate_in: "primary",
            loaded: "warning",
            in_transit: "warning",
            discharged: "info",
            gate_out: "success",
            returned: "success",
        };
        return colors[state] || "secondary";
    }

    getStateBadge(state) {
        return `badge bg-${this.getStateColor(state)}`;
    }
}

ContainerTrackerWidget.template = "freight_management.ContainerTracker";
ContainerTrackerWidget.props = {
    record: Object,
};

registry.category("fields").add("container_tracker", ContainerTrackerWidget);
