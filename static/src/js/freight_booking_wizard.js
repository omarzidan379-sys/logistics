/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class BookingWizard extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");
        
        this.state = useState({
            step: 1,
            quotationId: null,
            carrierId: null,
            vesselName: "",
            voyageNumber: "",
            bookingReference: "",
            etd: null,
            eta: null,
            containerQty: 1,
            processing: false,
        });
    }

    nextStep() {
        if (this.validateCurrentStep()) {
            this.state.step++;
        }
    }

    prevStep() {
        this.state.step--;
    }

    validateCurrentStep() {
        switch (this.state.step) {
            case 1:
                if (!this.state.quotationId) {
                    this.notification.add("Please select a quotation", {
                        type: "warning",
                    });
                    return false;
                }
                break;
            case 2:
                if (!this.state.carrierId || !this.state.vesselName) {
                    this.notification.add("Please fill in carrier and vessel details", {
                        type: "warning",
                    });
                    return false;
                }
                break;
        }
        return true;
    }

    async createBooking() {
        if (!this.validateCurrentStep()) return;

        this.state.processing = true;
        try {
            const bookingId = await this.orm.call(
                "freight.booking",
                "create_from_wizard",
                [],
                {
                    quotation_id: this.state.quotationId,
                    carrier_id: this.state.carrierId,
                    vessel_name: this.state.vesselName,
                    voyage_number: this.state.voyageNumber,
                    booking_reference: this.state.bookingReference,
                    etd: this.state.etd,
                    eta: this.state.eta,
                    container_qty: this.state.containerQty,
                }
            );

            this.notification.add("Booking created successfully", {
                type: "success",
            });

            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "freight.booking",
                res_id: bookingId,
                views: [[false, "form"]],
                target: "current",
            });
        } catch (error) {
            this.notification.add("Error creating booking: " + error.message, {
                type: "danger",
            });
        } finally {
            this.state.processing = false;
        }
    }

    getStepClass(stepNumber) {
        if (stepNumber < this.state.step) return "completed";
        if (stepNumber === this.state.step) return "active";
        return "pending";
    }
}

BookingWizard.template = "freight_management.BookingWizard";

registry.category("actions").add("freight_booking_wizard", BookingWizard);
