/* ========================================== */
/* PREMIUM FREIGHT DASHBOARD - INTERACTIVE */
/* ========================================== */

(function() {
    'use strict';

    // Dashboard App
    class FreightDashboard {
        constructor() {
            this.data = null;
            this.charts = {};
            this.theme = localStorage.getItem('dashboard-theme') || 'dark';
            this.init();
        }

        init() {
            this.loadData();
            this.setupEventListeners();
            this.applyTheme();
            this.startAutoRefresh();
        }

        loadData() {
            const dataElement = document.getElementById('dashboard-data');
            if (dataElement) {
                try {
                    this.data = JSON.parse(dataElement.textContent);
                    this.render();
                } catch (e) {
                    console.error('Failed to parse dashboard data:', e);
                    this.showError('Failed to load dashboard data');
                }
            }
        }

        render() {
            const container = document.getElementById('freight_dashboard_app');
            if (!container) return;

            container.innerHTML = `
                <div class="dashboard-container">
                    ${this.renderNavbar()}
                    ${this.renderStats()}
                    ${this.renderMainContent()}
                </div>
                <div class="toast-container" id="toast-container"></div>
            `;

            this.initializeCharts();
            this.setupInteractions();
        }

        renderNavbar() {
            const user = this.data.user || {};
            const notificationCount = this.data.notifications?.filter(n => !n.read).length || 0;

            return `
                <div class="dashboard-navbar">
                    <div class="navbar-left">
                        <div class="navbar-logo">
                            <i class="fa fa-ship"></i> Freight Portal
                        </div>
                        <div class="navbar-search">
                            <i class="fa fa-search navbar-search-icon"></i>
                            <input type="text" placeholder="Search shipments, quotes..." id="dashboard-search">
                        </div>
                    </div>
                    <div class="navbar-right">
                        <div class="theme-toggle" id="theme-toggle">
                            <div class="theme-option ${this.theme === 'light' ? 'active' : ''}" data-theme="light">
                                <i class="fa fa-sun"></i>
                            </div>
                            <div class="theme-option ${this.theme === 'dark' ? 'active' : ''}" data-theme="dark">
                                <i class="fa fa-moon"></i>
                            </div>
                        </div>
                        <div class="navbar-icon-btn" id="notifications-btn">
                            <i class="fa fa-bell"></i>
                            ${notificationCount > 0 ? `<span class="badge">${notificationCount}</span>` : ''}
                        </div>
                        <div class="navbar-icon-btn" id="messages-btn">
                            <i class="fa fa-envelope"></i>
                        </div>
                        <div class="navbar-profile" id="profile-menu">
                            <img src="${user.avatar || '/web/static/img/user_menu_avatar.png'}" alt="${user.name}" class="navbar-avatar">
                            <div class="navbar-user-info">
                                <div class="navbar-user-name">${user.name || 'User'}</div>
                                <div class="navbar-user-role">Customer Portal</div>
                            </div>
                            <i class="fa fa-chevron-down"></i>
 