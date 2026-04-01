/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class FreightQuotationDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            quotations: {
                draft: 0,
                sent: 0,
                approved: 0,
                total_amount: 0,
            },
            loading: true,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        const data = await this.orm.call(
            "freight.quotation",
            "get_dashboard_data",
            []
        );
        Object.assign(this.state.quotations, data);
        this.state.loading = false;
    }

    openQuotations(state) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Quotations",
            res_model: "freight.quotation",
            views: [[false, "list"], [false, "form"]],
            domain: state ? [["state", "=", state]] : [],
            context: { create: true },
        });
    }
}

FreightQuotationDashboard.template = "freight_management.QuotationDashboard";

registry.category("actions").add("freight_quotation_dashboard", FreightQuotationDashboard);
