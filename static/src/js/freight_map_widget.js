/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class FreightMapWidget extends Component {
    setup() {
        this.orm = useService("orm");
        this.mapRef = useRef("map");
        
        this.state = useState({
            origin: null,
            destination: null,
            route: [],
            loading: true,
        });

        onMounted(() => {
            this.loadMapData();
        });
    }

    async loadMapData() {
        const shipmentId = this.props.record.resId;
        try {
            const data = await this.orm.call(
                "freight.shipment",
                "get_map_data",
                [shipmentId]
            );
            
            this.state.origin = data.origin;
            this.state.destination = data.destination;
            this.state.route = data.route || [];
            this.state.loading = false;
            
            this.renderMap();
        } catch (error) {
            console.error("Error loading map data:", error);
            this.state.loading = false;
        }
    }

    renderMap() {
        // Simple SVG-based route visualization
        const mapElement = this.mapRef.el;
        if (!mapElement || !this.state.origin || !this.state.destination) return;

        const svg = `
            <svg width="100%" height="400" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
                <!-- Background -->
                <rect width="800" height="400" fill="#e3f2fd"/>
                
                <!-- Route Line -->
                <line x1="100" y1="200" x2="700" y2="200" 
                      stroke="#2196f3" stroke-width="3" stroke-dasharray="10,5"/>
                
                <!-- Origin Port -->
                <circle cx="100" cy="200" r="15" fill="#4caf50"/>
                <text x="100" y="240" text-anchor="middle" font-size="14" fill="#333">
                    ${this.state.origin.name}
                </text>
                
                <!-- Destination Port -->
                <circle cx="700" cy="200" r="15" fill="#f44336"/>
                <text x="700" y="240" text-anchor="middle" font-size="14" fill="#333">
                    ${this.state.destination.name}
                </text>
                
                <!-- Ship Icon (animated) -->
                <g transform="translate(400, 200)">
                    <path d="M-15,-5 L15,-5 L20,5 L-20,5 Z" fill="#ff9800"/>
                    <rect x="-5" y="-15" width="10" height="10" fill="#ff9800"/>
                    <animate attributeName="transform" 
                             type="translate" 
                             from="100 200" 
                             to="700 200" 
                             dur="10s" 
                             repeatCount="indefinite"/>
                </g>
            </svg>
        `;
        
        mapElement.innerHTML = svg;
    }
}

FreightMapWidget.template = "freight_management.MapWidget";
FreightMapWidget.props = {
    record: Object,
};

registry.category("fields").add("freight_map", FreightMapWidget);
