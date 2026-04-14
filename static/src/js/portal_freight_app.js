/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.FreightPortalApp = publicWidget.Widget.extend({
    selector: '.fp-portal',
    events: {
        'click .fp-filter-btn': '_onFilterClick',
        'input .fp-search input': '_onSearchInput',
        'click .fp-shipment-item[data-id]': '_onShipmentClick',
        'click .fp-refresh-btn': '_onRefresh',
        'click .fp-tab-btn': '_onTabClick',
    },

    start: function () {
        this._super.apply(this, arguments);
        this.currentFilter = 'all';
        this.searchQuery = '';
        this._animateCounters();
        this._loadAlerts();
        this._startAutoRefresh();
    },

    destroy: function () {
        if (this._refreshInterval) {
            clearInterval(this._refreshInterval);
        }
        this._super.apply(this, arguments);
    },

    // ---- Counter Animation ----
    _animateCounters: function () {
        this.$('.fp-stat-number[data-target]').each(function () {
            var $el = $(this);
            var target = parseInt($el.data('target')) || 0;
            var duration = 1200;
            var start = 0;
            var increment = target / (duration / 16);
            var current = start;

            if (target === 0) {
                $el.text('0');
                return;
            }

            var timer = setInterval(function () {
                current += increment;
                if (current >= target) {
                    $el.text(target);
                    clearInterval(timer);
                } else {
                    $el.text(Math.floor(current));
                }
            }, 16);
        });
    },

    // ---- Filtering ----
    _onFilterClick: function (ev) {
        var $btn = $(ev.currentTarget);
        this.$('.fp-filter-btn').removeClass('active');
        $btn.addClass('active');
        this.currentFilter = $btn.data('filter');
        this._applyFilters();
    },

    _onSearchInput: function (ev) {
        this.searchQuery = $(ev.currentTarget).val().toLowerCase().trim();
        this._applyFilters();
    },

    _applyFilters: function () {
        var self = this;
        this.$('.fp-shipment-item').each(function () {
            var $item = $(this);
            var state = $item.data('state') || '';
            var text = $item.text().toLowerCase();

            var filterMatch = (self.currentFilter === 'all') || (state === self.currentFilter);
            var searchMatch = !self.searchQuery || text.indexOf(self.searchQuery) !== -1;

            if (filterMatch && searchMatch) {
                $item.slideDown(200);
            } else {
                $item.slideUp(200);
            }
        });
    },

    // ---- Shipment Click → Timeline ----
    _onShipmentClick: function (ev) {
        ev.preventDefault();
        var shipmentId = $(ev.currentTarget).data('id');
        if (shipmentId) {
            window.location.href = '/my/shipments/' + shipmentId;
        }
    },

    // ---- Tab Switching ----
    _onTabClick: function (ev) {
        ev.preventDefault();
        var $btn = $(ev.currentTarget);
        var tab = $btn.data('tab');

        this.$('.fp-tab-btn').removeClass('active');
        $btn.addClass('active');

        this.$('.fp-tab-content').hide();
        this.$('.fp-tab-content[data-tab="' + tab + '"]').fadeIn(300);
    },

    // ---- Alerts Loading ----
    _loadAlerts: function () {
        var self = this;
        this._rpc({
            route: '/my/freight/api/dashboard',
            params: {}
        }).then(function (result) {
            if (result.success && result.alerts && result.alerts.length > 0) {
                var $container = self.$('.fp-alerts-container');
                if ($container.length) {
                    var html = '';
                    result.alerts.forEach(function (alert) {
                        html += '<div class="fp-alert-item ' + alert.type + '">';
                        html += '<div class="fp-alert-icon"><i class="fa ' + alert.icon + '"></i></div>';
                        html += '<div><div class="fp-alert-title">' + alert.title + '</div>';
                        html += '<div class="fp-alert-msg">' + alert.message + '</div></div>';
                        html += '</div>';
                    });
                    $container.html(html);

                    // Update notification badge
                    var $badge = self.$('.fp-notification-badge');
                    if ($badge.length) {
                        $badge.text(result.alerts.length).show();
                    }
                }

                // Update monthly chart
                if (result.monthly) {
                    self._renderMonthlyChart(result.monthly);
                }
            }
        }).catch(function () {
            // Silently fail – dashboard still shows server-rendered data
        });
    },

    // ---- Monthly Chart ----
    _renderMonthlyChart: function (monthlyData) {
        var $chart = this.$('.fp-chart-bars');
        if (!$chart.length || !monthlyData.length) return;

        var maxVal = Math.max.apply(null, monthlyData.map(function (d) {
            return Math.max(d.shipments, d.quotations);
        })) || 1;

        var html = '';
        monthlyData.forEach(function (d) {
            var shipH = Math.max(4, (d.shipments / maxVal) * 100);
            var quoteH = Math.max(4, (d.quotations / maxVal) * 100);
            html += '<div class="fp-chart-bar-wrap">';
            html += '<div class="fp-chart-bar" style="height:' + shipH + '%" title="' + d.shipments + ' shipments"></div>';
            html += '<div class="fp-chart-bar accent" style="height:' + quoteH + '%" title="' + d.quotations + ' quotes"></div>';
            html += '<div class="fp-chart-bar-label">' + d.month + '</div>';
            html += '</div>';
        });
        $chart.html(html);
    },

    // ---- Auto-refresh ----
    _startAutoRefresh: function () {
        var self = this;
        this._refreshInterval = setInterval(function () {
            self._loadAlerts();
        }, 60000); // refresh every 60s
    },

    _onRefresh: function (ev) {
        ev.preventDefault();
        var $btn = $(ev.currentTarget);
        $btn.find('i').addClass('fa-spin');
        var self = this;
        this._loadAlerts();
        setTimeout(function () {
            $btn.find('i').removeClass('fa-spin');
        }, 1000);
    },
});

export default publicWidget.registry.FreightPortalApp;
