/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.FreightTimeline = publicWidget.Widget.extend({
    selector: '.fp-timeline-container',
    events: {
        'click .fp-timeline-item': '_onStageClick',
    },

    start: function () {
        this._super.apply(this, arguments);
        this.shipmentId = this.$el.data('shipment-id');
        if (this.shipmentId) {
            this._loadTimeline();
        } else {
            this._animateExistingTimeline();
        }
    },

    // ---- Load Timeline via AJAX ----
    _loadTimeline: function () {
        var self = this;
        this._rpc({
            route: '/my/freight/api/shipment/' + this.shipmentId + '/timeline',
            params: {}
        }).then(function (result) {
            if (result.success) {
                self._renderTimeline(result.stages);
                if (result.customs_stages && result.customs_stages.length) {
                    self._renderCustomsStages(result.customs_stages);
                }
                if (result.missing_documents && result.missing_documents.length) {
                    self._renderDocumentAlerts(result.missing_documents);
                }
            }
        }).catch(function () {
            // Timeline is already rendered server-side as fallback
        });
    },

    // ---- Render Timeline ----
    _renderTimeline: function (stages) {
        var $timeline = this.$('.fp-timeline');
        if (!$timeline.length) return;

        var html = '';
        stages.forEach(function (stage, idx) {
            html += '<div class="fp-timeline-item ' + stage.status + '" data-stage="' + stage.key + '" style="animation-delay:' + (idx * 0.1) + 's">';
            html += '<div class="fp-timeline-dot"><i class="fa ' + (stage.status === 'completed' ? 'fa-check' : stage.icon) + '"></i></div>';
            html += '<div class="fp-timeline-content">';
            html += '<div class="fp-timeline-title"><i class="fa ' + stage.icon + ' me-2"></i>' + stage.label + '</div>';
            if (stage.date) {
                html += '<div class="fp-timeline-date"><i class="fa fa-calendar me-1"></i>' + stage.date + '</div>';
            }
            html += '</div>';
            html += '</div>';
        });
        $timeline.html(html);

        // Animate entry
        $timeline.find('.fp-timeline-item').each(function (i) {
            var $item = $(this);
            setTimeout(function () {
                $item.css({ opacity: 0, transform: 'translateX(-20px)' });
                $item.animate({ opacity: 1 }, 400);
                $item.css('transform', 'translateX(0)');
            }, i * 120);
        });
    },

    // ---- Customs Sub-stages ----
    _renderCustomsStages: function (customsStages) {
        var $container = this.$('.fp-customs-stages');
        if (!$container.length) return;

        var icons = {
            'submitted': 'fa-file-text',
            'under_review': 'fa-search',
            'cleared': 'fa-check-circle',
        };

        var html = '';
        customsStages.forEach(function (cs) {
            html += '<div class="fp-customs-stage ' + cs.status + '">';
            html += '<div class="fp-customs-icon"><i class="fa ' + (icons[cs.key] || 'fa-circle') + '"></i></div>';
            html += '<div class="fp-customs-label">' + cs.label + '</div>';
            html += '</div>';
        });
        $container.html(html);
    },

    // ---- Document Alerts ----
    _renderDocumentAlerts: function (missingDocs) {
        var $container = this.$('.fp-doc-alerts');
        if (!$container.length) return;

        var docLabels = {
            'customs_declaration': 'Customs Declaration',
            'packing_list': 'Packing List',
            'commercial_invoice': 'Commercial Invoice',
        };

        var html = '<div class="fp-alert-item danger">';
        html += '<div class="fp-alert-icon"><i class="fa fa-exclamation-triangle"></i></div>';
        html += '<div>';
        html += '<div class="fp-alert-title">Missing Documents</div>';
        html += '<div class="fp-alert-msg">The following documents are required: ';
        html += missingDocs.map(function (d) { return docLabels[d] || d; }).join(', ');
        html += '</div></div></div>';
        $container.html(html);
    },

    // ---- Stage Click ----
    _onStageClick: function (ev) {
        var $item = $(ev.currentTarget);
        var stage = $item.data('stage');

        // Toggle detail expansion
        $item.find('.fp-timeline-detail').toggle(300);

        // Highlight
        this.$('.fp-timeline-item').removeClass('highlighted');
        $item.addClass('highlighted');
    },

    // ---- Animate server-rendered timeline ----
    _animateExistingTimeline: function () {
        this.$('.fp-timeline-item').each(function (i) {
            var $item = $(this);
            $item.css('opacity', 0);
            setTimeout(function () {
                $item.animate({ opacity: 1 }, 400);
            }, i * 100);
        });
    },
});

export default publicWidget.registry.FreightTimeline;
