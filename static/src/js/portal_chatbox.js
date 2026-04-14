/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.FreightChatBox = publicWidget.Widget.extend({
    selector: '.fp-chatbox',
    events: {
        'click .fp-chat-send': '_onSendMessage',
        'keypress .fp-chat-input input': '_onInputKeypress',
        'click .fp-quote-accept': '_onAcceptQuote',
        'click .fp-quote-reject': '_onRejectQuote',
    },

    start: function () {
        this._super.apply(this, arguments);
        this.shipmentId = this.$el.data('shipment-id');
        this.quotationId = this.$el.data('quotation-id');
        if (this.shipmentId) {
            this._loadMessages();
            this._startPolling();
        }
    },

    destroy: function () {
        if (this._pollInterval) {
            clearInterval(this._pollInterval);
        }
        this._super.apply(this, arguments);
    },

    // ---- Load Messages ----
    _loadMessages: function () {
        var self = this;
        this._rpc({
            route: '/my/freight/api/shipment/' + this.shipmentId + '/messages',
            params: {}
        }).then(function (result) {
            if (result.success) {
                self._renderMessages(result.messages);
            }
        }).catch(function () { /* silent */ });
    },

    _renderMessages: function (messages) {
        var $container = this.$('.fp-chat-messages');
        if (!$container.length) return;

        if (!messages || messages.length === 0) {
            $container.html('<div class="fp-empty" style="padding:20px"><i class="fa fa-comments-o" style="font-size:24px"></i><p style="margin-top:8px;font-size:13px;color:#718096">No messages yet. Start the conversation!</p></div>');
            return;
        }

        var html = '';
        messages.forEach(function (msg) {
            var cssClass = msg.is_customer ? 'customer' : 'company';
            html += '<div class="fp-chat-msg ' + cssClass + '">';
            html += '<div class="fp-chat-body">' + msg.body + '</div>';
            html += '<div class="fp-chat-meta">' + msg.author + ' · ' + msg.date + '</div>';
            html += '</div>';
        });
        $container.html(html);

        // Auto-scroll to bottom
        $container.scrollTop($container[0].scrollHeight);
    },

    // ---- Send Message ----
    _onSendMessage: function (ev) {
        ev.preventDefault();
        this._sendMessage();
    },

    _onInputKeypress: function (ev) {
        if (ev.which === 13) {
            ev.preventDefault();
            this._sendMessage();
        }
    },

    _sendMessage: function () {
        var $input = this.$('.fp-chat-input input');
        var message = $input.val().trim();
        if (!message || !this.shipmentId) return;

        var self = this;
        var $btn = this.$('.fp-chat-send');
        $btn.prop('disabled', true);

        // Optimistically add message
        var $container = this.$('.fp-chat-messages');
        $container.find('.fp-empty').remove();
        $container.append(
            '<div class="fp-chat-msg customer">' +
            '<div class="fp-chat-body">' + this._escapeHtml(message) + '</div>' +
            '<div class="fp-chat-meta">You · just now</div>' +
            '</div>'
        );
        $container.scrollTop($container[0].scrollHeight);
        $input.val('');

        this._rpc({
            route: '/my/freight/api/shipment/' + this.shipmentId + '/message',
            params: { message: message }
        }).then(function (result) {
            $btn.prop('disabled', false);
            if (result.error) {
                self._showToast(result.error, 'error');
            }
        }).catch(function () {
            $btn.prop('disabled', false);
            self._showToast('Failed to send message', 'error');
        });
    },

    // ---- Quote Actions ----
    _onAcceptQuote: function (ev) {
        ev.preventDefault();
        if (!this.quotationId) return;

        var self = this;
        var $btn = $(ev.currentTarget);
        $btn.html('<span class="fp-spinner"></span>').prop('disabled', true);

        this._rpc({
            route: '/my/quotations/' + this.quotationId + '/accept',
            params: {}
        }).then(function (result) {
            if (result.success) {
                self._showToast('Quotation accepted!', 'success');
                setTimeout(function () { location.reload(); }, 1500);
            } else {
                self._showToast(result.error || 'Error', 'error');
                $btn.html('<i class="fa fa-check me-1"></i>Accept').prop('disabled', false);
            }
        }).catch(function () {
            self._showToast('Network error', 'error');
            $btn.html('<i class="fa fa-check me-1"></i>Accept').prop('disabled', false);
        });
    },

    _onRejectQuote: function (ev) {
        ev.preventDefault();
        if (!this.quotationId) return;

        var reason = prompt('Please provide a reason for rejection (optional):');
        var self = this;
        var $btn = $(ev.currentTarget);
        $btn.html('<span class="fp-spinner"></span>').prop('disabled', true);

        this._rpc({
            route: '/my/quotations/' + this.quotationId + '/reject',
            params: { reason: reason || '' }
        }).then(function (result) {
            if (result.success) {
                self._showToast('Quotation rejected.', 'info');
                setTimeout(function () { location.reload(); }, 1500);
            } else {
                self._showToast(result.error || 'Error', 'error');
                $btn.html('<i class="fa fa-times me-1"></i>Reject').prop('disabled', false);
            }
        }).catch(function () {
            self._showToast('Network error', 'error');
            $btn.html('<i class="fa fa-times me-1"></i>Reject').prop('disabled', false);
        });
    },

    // ---- Polling ----
    _startPolling: function () {
        var self = this;
        this._pollInterval = setInterval(function () {
            self._loadMessages();
        }, 30000); // 30s
    },

    // ---- Utils ----
    _showToast: function (message, type) {
        var icon = type === 'success' ? 'fa-check-circle' : (type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle');
        var $toast = $('<div class="fp-toast ' + type + '"><i class="fa ' + icon + '"></i> ' + message + '</div>');
        $('body').append($toast);
        setTimeout(function () { $toast.remove(); }, 4000);
    },

    _escapeHtml: function (text) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(text));
        return div.innerHTML;
    },
});

export default publicWidget.registry.FreightChatBox;
