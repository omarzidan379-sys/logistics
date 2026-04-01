/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class FreightRateCalculator extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({
            origin: null,
            destination: null,
            serviceType: "fcl",
            containerType: "40hc",
            weight: 0,
            volume: 0,
            calculating: false,
            result: null,
        });
    }

    async calculateRate() {
        if (!this.state.origin || !this.state.destination) {
            this.notification.add("Please select origin and destination", {
                type: "warning",
            });
            return;
        }

        this.state.calculating = true;
        try {
            const result = await this.orm.call(
                "freight.rate",
                "calculate_freight_rate",
                [],
                {
                    origin_id: this.state.origin,
                    destination_id: this.state.destination,
                    service_type: this.state.serviceType,
                    container_type: this.state.containerType,
                    weight: this.state.weight,
                    volume: this.state.volume,
                }
            );
            
            this.state.result = result;
            this.notification.add("Rate calculated successfully", {
                type: "success",
            });
        } catch (error) {
            this.notification.add("Error calculating rate: " + error.message, {
                type: "danger",
            });
        } finally {
            this.state.calculating = false;
        }
    }

    clearCalculation() {
        this.state.result = null;
        this.state.weight = 0;
        this.state.volume = 0;
    }
}

FreightRateCalculator.template = "freight_management.RateCalculator";

registry.category("actions").add("freight_rate_calculator", FreightRateCalculator);
