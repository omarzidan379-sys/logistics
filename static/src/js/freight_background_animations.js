/** @odoo-module **/

// Professional Logistics Background Animations
// Visible and smooth animations

document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        initProfessionalBackground();
    }, 1000);
});

function initProfessionalBackground() {
    const container = document.querySelector('.o_action_manager') || document.body;
    
    // Check if background already exists
    if (document.querySelector('.freight-professional-background')) {
        return;
    }

    // Create professional background with visible animations
    const bgContainer = document.createElement('div');
    bgContainer.className = 'freight-professional-background';
    bgContainer.innerHTML = `
        <!-- Subtle Gradient Background -->
        <div class="professional-gradient"></div>
        
        <!-- Visible Animated Elements -->
        <div class="logistics-corner-animation">
            <!-- Container Icons - Floating -->
            <div class="container-icon" style="left: 5%; bottom: 8%; animation-delay: 0s;">
                <svg width="50" height="50" viewBox="0 0 50 50">
                    <rect x="5" y="10" width="40" height="30" fill="#667eea" opacity="0.8" rx="3" stroke="#5a67d8" stroke-width="2"/>
                    <rect x="5" y="10" width="40" height="4" fill="#5a67d8" opacity="0.9"/>
                    <line x1="25" y1="10" x2="25" y2="40" stroke="#5a67d8" stroke-width="1" opacity="0.5"/>
                </svg>
            </div>
            <div class="container-icon" style="left: 10%; bottom: 5%; animation-delay: 3s;">
                <svg width="50" height="50" viewBox="0 0 50 50">
                    <rect x="5" y="10" width="40" height="30" fill="#4facfe" opacity="0.8" rx="3" stroke="#3b9ae1" stroke-width="2"/>
                    <rect x="5" y="10" width="40" height="4" fill="#3b9ae1" opacity="0.9"/>
                    <line x1="25" y1="10" x2="25" y2="40" stroke="#3b9ae1" stroke-width="1" opacity="0.5"/>
                </svg>
            </div>
            <div class="container-icon" style="left: 15%; bottom: 10%; animation-delay: 6s;">
                <svg width="50" height="50" viewBox="0 0 50 50">
                    <rect x="5" y="10" width="40" height="30" fill="#43e97b" opacity="0.8" rx="3" stroke="#38c766" stroke-width="2"/>
                    <rect x="5" y="10" width="40" height="4" fill="#38c766" opacity="0.9"/>
                    <line x1="25" y1="10" x2="25" y2="40" stroke="#38c766" stroke-width="1" opacity="0.5"/>
                </svg>
            </div>
            <div class="container-icon" style="left: 3%; bottom: 15%; animation-delay: 9s;">
                <svg width="50" height="50" viewBox="0 0 50 50">
                    <rect x="5" y="10" width="40" height="30" fill="#f093fb" opacity="0.8" rx="3" stroke="#d77fe8" stroke-width="2"/>
                    <rect x="5" y="10" width="40" height="4" fill="#d77fe8" opacity="0.9"/>
                    <line x1="25" y1="10" x2="25" y2="40" stroke="#d77fe8" stroke-width="1" opacity="0.5"/>
                </svg>
            </div>
            
            <!-- Plane Icon - Flying Across -->
            <div class="plane-icon">
                <svg width="80" height="40" viewBox="0 0 80 40">
                    <!-- Plane body -->
                    <ellipse cx="40" cy="20" rx="25" ry="6" fill="#667eea" opacity="0.8"/>
                    <!-- Wings -->
                    <ellipse cx="40" cy="20" rx="35" ry="3" fill="#5a67d8" opacity="0.7"/>
                    <!-- Cockpit -->
                    <circle cx="55" cy="20" r="5" fill="#4facfe" opacity="0.9"/>
                    <!-- Tail -->
                    <path d="M 20 20 L 15 12 L 18 20 Z" fill="#5a67d8" opacity="0.8"/>
                    <path d="M 20 20 L 15 28 L 18 20 Z" fill="#5a67d8" opacity="0.8"/>
                    <!-- Windows -->
                    <circle cx="50" cy="19" r="2" fill="#ffffff" opacity="0.8"/>
                    <circle cx="45" cy="19" r="2" fill="#ffffff" opacity="0.8"/>
                    <circle cx="40" cy="19" r="2" fill="#ffffff" opacity="0.8"/>
                </svg>
            </div>
            
            <!-- Ship Icon - Sailing Across -->
            <div class="ship-icon">
                <svg width="100" height="60" viewBox="0 0 100 60">
                    <!-- Hull -->
                    <path d="M 15 35 L 10 50 L 90 50 L 85 35 Z" fill="#c62828" opacity="0.8"/>
                    <path d="M 15 35 L 85 35 L 85 50 L 15 50 Z" fill="#d32f2f" opacity="0.7"/>
                    <!-- Deck -->
                    <rect x="15" y="32" width="70" height="3" fill="#9e9e9e" opacity="0.8"/>
                    <!-- Containers -->
                    <rect x="20" y="20" width="12" height="12" fill="#ff5722" opacity="0.8" stroke="#bf360c" stroke-width="1"/>
                    <rect x="35" y="20" width="12" height="12" fill="#2196f3" opacity="0.8" stroke="#0d47a1" stroke-width="1"/>
                    <rect x="50" y="20" width="12" height="12" fill="#4caf50" opacity="0.8" stroke="#1b5e20" stroke-width="1"/>
                    <rect x="65" y="20" width="12" height="12" fill="#ffc107" opacity="0.8" stroke="#f57f17" stroke-width="1"/>
                    <!-- Bridge -->
                    <rect x="75" y="22" width="10" height="13" fill="#37474f" opacity="0.8"/>
                    <rect x="76" y="24" width="8" height="6" fill="#546e7a" opacity="0.7"/>
                    <!-- Windows -->
                    <rect x="77" y="26" width="2" height="2" fill="#ffeb3b" opacity="0.9"/>
                    <rect x="80" y="26" width="2" height="2" fill="#ffeb3b" opacity="0.9"/>
                    <!-- Chimney -->
                    <rect x="80" y="15" width="3" height="7" fill="#263238" opacity="0.8"/>
                    <!-- Smoke -->
                    <circle cx="81" cy="12" r="2" fill="#90a4ae" opacity="0.6"/>
                    <circle cx="82" cy="9" r="3" fill="#b0bec5" opacity="0.5"/>
                </svg>
            </div>
        </div>
        
        <!-- Subtle Grid Pattern -->
        <div class="grid-pattern"></div>
    `;
    
    container.insertBefore(bgContainer, container.firstChild);
    
    console.log('Freight animations initialized successfully!');
}

// Re-initialize on route changes
if (window.odoo) {
    const originalPushState = history.pushState;
    history.pushState = function() {
        originalPushState.apply(history, arguments);
        setTimeout(() => initProfessionalBackground(), 500);
    };
}
