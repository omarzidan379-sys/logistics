/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.FreightQuote = publicWidget.Widget.extend({
    selector: '#quote_form',
    events: {
        'submit': '_onSubmitQuote',
    },

    _onSubmitQuote: function (ev) {
        ev.preventDefault();
        
        const formData = {
            partner_name: this.$('#partner_name').val(),
            partner_email: this.$('#partner_email').val(),
            partner_phone: this.$('#partner_phone').val(),
            origin_id: this.$('#origin_id').val(),
            destination_id: this.$('#destination_id').val(),
            cargo_type: this.$('#cargo_type').val(),
            weight: this.$('#weight').val(),
            volume: this.$('#volume').val(),
        };

        if (!formData.partner_name || !formData.partner_email || !formData.origin_id || !formData.destination_id) {
            this._showError('Please fill all required fields');
            return;
        }

        jsonrpc('/freight/quote/submit', formData).then((result) => {
            if (result.error) {
                this._showError(result.error);
            } else {
                this._showSuccess(result.message, result.quotation_ref);
                this.$('form')[0].reset();
            }
        });
    },

    _showSuccess: function (message, ref) {
        const resultDiv = this.$('#quote_result');
        resultDiv.html(`
            <div class="alert alert-success">
                <h5>Success!</h5>
                <p>${message}</p>
                <p><strong>Reference:</strong> ${ref}</p>
            </div>
        `).show();
    },

    _showError: function (message) {
        const resultDiv = this.$('#quote_result');
        resultDiv.html(`<div class="alert alert-danger">${message}</div>`).show();
    },
});

export default publicWidget.registry.FreightQuote;
