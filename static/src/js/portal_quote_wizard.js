/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.FreightQuoteWizard = publicWidget.Widget.extend({
    selector: '.fp-wizard',
    events: {
        'click .fp-wizard-next': '_onNext',
        'click .fp-wizard-prev': '_onPrev',
        'click .fp-wizard-submit': '_onSubmit',
        'click .fp-type-option': '_onTypeSelect',
        'click .fp-wizard-step': '_onStepClick',
        'click .fp-save-draft': '_onSaveDraft',
        'change #fp_service_type': '_onServiceTypeChange',
        'change #fp_shipment_direction': '_onDirectionChange',
        'input .fp-form-control': '_onFieldInput',
    },

    start: function () {
        this._super.apply(this, arguments);
        this.currentStep = 0;
        this.totalSteps = 5;
        this.formData = {};
        this._loadDraft();
        this._updateWizard();
        this._initTypeSelector();
    },

    // ---- Step Navigation ----
    _onNext: function (ev) {
        ev.preventDefault();
        if (this._validateStep(this.currentStep)) {
            this._collectStepData(this.currentStep);
            if (this.currentStep < this.totalSteps - 1) {
                this.currentStep++;
                this._updateWizard();
                if (this.currentStep === this.totalSteps - 1) {
                    this._buildReview();
                }
            }
        }
    },

    _onPrev: function (ev) {
        ev.preventDefault();
        if (this.currentStep > 0) {
            this.currentStep--;
            this._updateWizard();
        }
    },

    _onStepClick: function (ev) {
        var targetStep = parseInt($(ev.currentTarget).data('step'));
        if (targetStep < this.currentStep) {
            this.currentStep = targetStep;
            this._updateWizard();
        }
    },

    _updateWizard: function () {
        var self = this;
        // Update panels
        this.$('.fp-wizard-panel').removeClass('active');
        this.$('.fp-wizard-panel[data-step="' + this.currentStep + '"]').addClass('active');

        // Update progress dots
        this.$('.fp-wizard-step').each(function (i) {
            var $step = $(this);
            $step.removeClass('active completed');
            if (i < self.currentStep) {
                $step.addClass('completed');
                $step.find('.fp-wizard-step-dot').html('<i class="fa fa-check"></i>');
            } else if (i === self.currentStep) {
                $step.addClass('active');
                $step.find('.fp-wizard-step-dot').html(i + 1);
            } else {
                $step.find('.fp-wizard-step-dot').html(i + 1);
            }
        });

        // Update progress fill
        var progressWidth = (this.currentStep / (this.totalSteps - 1)) * 100;
        this.$('.fp-wizard-progress-fill').css('width', progressWidth + '%');

        // Update nav buttons
        this.$('.fp-wizard-prev').toggle(this.currentStep > 0);
        this.$('.fp-wizard-next').toggle(this.currentStep < this.totalSteps - 1);
        this.$('.fp-wizard-submit').toggle(this.currentStep === this.totalSteps - 1);

        // Scroll to top of wizard
        this.$el[0].scrollIntoView({ behavior: 'smooth', block: 'start' });
    },

    // ---- Type Selector ----
    _initTypeSelector: function () {
        var savedType = this.formData.shipment_type || 'sea';
        this.$('.fp-type-option[data-type="' + savedType + '"]').addClass('selected');
        this._updateDynamicFields(savedType);
    },

    _onTypeSelect: function (ev) {
        var $opt = $(ev.currentTarget);
        this.$('.fp-type-option').removeClass('selected');
        $opt.addClass('selected');
        var type = $opt.data('type');
        this.formData.shipment_type = type;

        // Map type to service_type
        var typeMap = { 'sea': 'fcl', 'air': 'air', 'land': 'road' };
        this.$('#fp_service_type').val(typeMap[type] || 'fcl');
        this._updateDynamicFields(type);
    },

    _onServiceTypeChange: function () {
        var val = this.$('#fp_service_type').val();
        var typeMap = { 'fcl': 'sea', 'lcl': 'sea', 'air': 'air', 'road': 'land', 'rail': 'land' };
        this._updateDynamicFields(typeMap[val] || 'sea');
    },

    _onDirectionChange: function () {
        var dir = this.$('#fp_shipment_direction').val();
        // Auto-show customs clearance option for imports
        if (dir === 'import') {
            this.$('#fp_customs_group').slideDown(300);
            this.$('#fp_customs_clearance').prop('checked', true);
        } else {
            this.$('#fp_customs_group').slideUp(300);
        }
    },

    _updateDynamicFields: function (type) {
        // Show/hide container fields for sea
        if (type === 'sea') {
            this.$('.fp-sea-fields').slideDown(300);
            this.$('.fp-air-fields').slideUp(300);
        } else if (type === 'air') {
            this.$('.fp-sea-fields').slideUp(300);
            this.$('.fp-air-fields').slideDown(300);
        } else {
            this.$('.fp-sea-fields').slideUp(300);
            this.$('.fp-air-fields').slideUp(300);
        }
    },

    // ---- Validation ----
    _validateStep: function (step) {
        var valid = true;
        var self = this;

        this.$('.fp-wizard-panel[data-step="' + step + '"] .fp-form-control[required]').each(function () {
            var $field = $(this);
            var val = $field.val();
            if (!val || val.trim() === '') {
                self._showFieldError($field, 'This field is required');
                valid = false;
            } else {
                self._clearFieldError($field);
            }
        });

        // Step-specific validation
        if (step === 0) {
            if (!this.$('.fp-type-option.selected').length) {
                this._showToast('Please select a shipment type', 'error');
                valid = false;
            }
        }

        if (step === 1) {
            var origin = this.$('#fp_origin_port').val();
            var dest = this.$('#fp_destination_port').val();
            if (origin && dest && origin === dest) {
                this._showFieldError(this.$('#fp_destination_port'), 'Destination must differ from origin');
                valid = false;
            }
        }

        if (step === 2) {
            var weight = parseFloat(this.$('#fp_total_weight').val());
            var volume = parseFloat(this.$('#fp_total_volume').val());
            if (weight && weight < 0) {
                this._showFieldError(this.$('#fp_total_weight'), 'Weight must be positive');
                valid = false;
            }
            if (volume && volume < 0) {
                this._showFieldError(this.$('#fp_total_volume'), 'Volume must be positive');
                valid = false;
            }
        }

        return valid;
    },

    _showFieldError: function ($field, msg) {
        $field.addClass('error');
        var $error = $field.siblings('.fp-form-error');
        if ($error.length) {
            $error.text(msg).addClass('show');
        } else {
            $field.after('<div class="fp-form-error show">' + msg + '</div>');
        }
    },

    _clearFieldError: function ($field) {
        $field.removeClass('error');
        $field.siblings('.fp-form-error').removeClass('show');
    },

    _onFieldInput: function (ev) {
        this._clearFieldError($(ev.currentTarget));
    },

    // ---- Data Collection ----
    _collectStepData: function (step) {
        var self = this;
        this.$('.fp-wizard-panel[data-step="' + step + '"] .fp-form-control').each(function () {
            var $f = $(this);
            var name = $f.attr('name');
            if (name) {
                if ($f.attr('type') === 'checkbox') {
                    self.formData[name] = $f.is(':checked');
                } else {
                    self.formData[name] = $f.val();
                }
            }
        });

        // Collect type selection
        if (step === 0) {
            var selected = this.$('.fp-type-option.selected');
            if (selected.length) {
                this.formData.shipment_type = selected.data('type');
            }
        }
    },

    // ---- Review ----
    _buildReview: function () {
        this._collectStepData(this.currentStep - 1);

        var typeLabels = { 'sea': 'Sea Freight', 'air': 'Air Freight', 'land': 'Land Transport' };
        var serviceLabels = {
            'fcl': 'FCL (Full Container)', 'lcl': 'LCL (Less Container)',
            'air': 'Air Freight', 'road': 'Road Transport', 'rail': 'Rail Transport'
        };
        var dirLabels = { 'import': 'Import', 'export': 'Export' };

        var origin = this.$('#fp_origin_port option:selected').text().trim() || 'Not set';
        var dest = this.$('#fp_destination_port option:selected').text().trim() || 'Not set';

        var html = '';
        html += this._reviewItem('Shipment Type', typeLabels[this.formData.shipment_type] || this.formData.shipment_type);
        html += this._reviewItem('Service', serviceLabels[this.formData.service_type] || this.formData.service_type);
        html += this._reviewItem('Direction', dirLabels[this.formData.shipment_direction] || 'Export');
        html += this._reviewItem('Origin', origin);
        html += this._reviewItem('Destination', dest);
        html += this._reviewItem('Weight (KG)', this.formData.total_weight || '—');
        html += this._reviewItem('Volume (CBM)', this.formData.total_volume || '—');
        html += this._reviewItem('Cargo', this.formData.cargo_description || '—');

        if (this.formData.customs_clearance_required) {
            html += this._reviewItem('Customs Clearance', '<span class="fp-badge fp-badge-info">Required</span>');
        }
        if (this.formData.is_dangerous_goods) {
            html += this._reviewItem('Dangerous Goods', '<span class="fp-badge fp-badge-danger">Yes</span>');
        }
        if (this.formData.special_instructions) {
            html += '<div class="fp-review-item" style="grid-column:1/-1"><div class="fp-review-label">Special Instructions</div><div class="fp-review-value">' + this._escapeHtml(this.formData.special_instructions) + '</div></div>';
        }

        this.$('.fp-review-grid').html(html);
    },

    _reviewItem: function (label, value) {
        return '<div class="fp-review-item"><div class="fp-review-label">' + label + '</div><div class="fp-review-value">' + (value || '—') + '</div></div>';
    },

    // ---- Submit ----
    _onSubmit: function (ev) {
        ev.preventDefault();
        this._collectStepData(this.currentStep);
        var self = this;

        // Build payload
        var payload = {
            service_type: this.formData.service_type || 'fcl',
            shipment_direction: this.formData.shipment_direction || 'export',
            origin_port_id: this.formData.origin_port_id || '',
            destination_port_id: this.formData.destination_port_id || '',
            cargo_description: this.formData.cargo_description || '',
            container_type: this.formData.container_type || '',
            container_qty: this.formData.container_qty || 1,
            total_weight: this.formData.total_weight || 0,
            total_volume: this.formData.total_volume || 0,
            is_dangerous_goods: this.formData.is_dangerous_goods || false,
            is_temperature_controlled: this.formData.is_temperature_controlled || false,
            special_instructions: this.formData.special_instructions || '',
            customs_clearance_required: this.formData.customs_clearance_required || false,
            customs_notes: this.formData.customs_notes || '',
        };

        // Show loading
        var $btn = this.$('.fp-wizard-submit');
        var origText = $btn.html();
        $btn.html('<span class="fp-spinner"></span> Submitting...').prop('disabled', true);

        this._rpc({
            route: '/my/freight/api/quote/submit',
            params: payload
        }).then(function (result) {
            if (result.error) {
                self._showToast(result.error, 'error');
                $btn.html(origText).prop('disabled', false);
            } else {
                self._clearDraft();
                self._showToast('Quote request submitted! Ref: ' + result.quotation_name, 'success');
                setTimeout(function () {
                    window.location.href = '/my/quotations';
                }, 2000);
            }
        }).catch(function () {
            self._showToast('Network error. Please try again.', 'error');
            $btn.html(origText).prop('disabled', false);
        });
    },

    // ---- Draft Save/Load ----
    _onSaveDraft: function (ev) {
        ev.preventDefault();
        this._collectStepData(this.currentStep);
        try {
            localStorage.setItem('fp_quote_draft', JSON.stringify(this.formData));
            localStorage.setItem('fp_quote_draft_step', this.currentStep);
            this._showToast('Draft saved successfully', 'success');
        } catch (e) {
            this._showToast('Could not save draft', 'error');
        }
    },

    _loadDraft: function () {
        try {
            var draft = localStorage.getItem('fp_quote_draft');
            if (draft) {
                this.formData = JSON.parse(draft);
                var savedStep = parseInt(localStorage.getItem('fp_quote_draft_step')) || 0;
                this.currentStep = savedStep;
                this._restoreFormFields();
            }
        } catch (e) { /* ignore */ }
    },

    _restoreFormFields: function () {
        var self = this;
        $.each(this.formData, function (name, val) {
            var $f = self.$('[name="' + name + '"]');
            if ($f.length) {
                if ($f.attr('type') === 'checkbox') {
                    $f.prop('checked', val);
                } else {
                    $f.val(val);
                }
            }
        });
    },

    _clearDraft: function () {
        try {
            localStorage.removeItem('fp_quote_draft');
            localStorage.removeItem('fp_quote_draft_step');
        } catch (e) { /* ignore */ }
    },

    // ---- Utilities ----
    _showToast: function (message, type) {
        var $toast = $('<div class="fp-toast ' + type + '"><i class="fa fa-' + (type === 'success' ? 'check-circle' : 'exclamation-circle') + '"></i> ' + message + '</div>');
        $('body').append($toast);
        setTimeout(function () { $toast.remove(); }, 4000);
    },

    _escapeHtml: function (text) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(text));
        return div.innerHTML;
    },
});

export default publicWidget.registry.FreightQuoteWizard;
