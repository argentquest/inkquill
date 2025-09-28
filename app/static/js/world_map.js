// /ai_rag_story_app/app/static/js/world_map.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("World Map: DOMContentLoaded event fired.");

    const API_BASE_URL = "/api/v1";
    const worldId = window.location.pathname.match(/\/worlds\/(\d+)/)?.[1];
    
    if (!worldId) {
        console.error("World ID not found in URL");
        return;
    }

    // DOM elements
    const networkContainer = document.getElementById('network-map');
    const layoutModeSelect = document.getElementById('layout-mode');
    const zoomFitBtn = document.getElementById('zoom-fit');
    const showConnectionsCheckbox = document.getElementById('show-connections');
    const mapInfo = document.getElementById('map-info');
    const infoTitle = document.getElementById('info-title');
    const infoContent = document.getElementById('info-content');
    
    // Sidebar and resize elements
    const sidebar = document.getElementById('map-sidebar');
    const resizeHandle = document.getElementById('resize-handle');
    
    // Connection management elements
    const addConnectionBtn = document.getElementById('add-connection-btn');
    const connectionForm = document.getElementById('connection-form');
    const connectionCreateForm = document.getElementById('connection-create-form');
    const cancelConnectionBtn = document.getElementById('cancel-connection');
    const fromLocationSelect = document.getElementById('from-location');
    const toLocationSelect = document.getElementById('to-location');
    const connectionsList = document.getElementById('connections-list');

    // Vis.js network variables
    let network = null;
    let nodes = new vis.DataSet([]);
    let edges = new vis.DataSet([]);
    let locations = [];
    let connections = [];

    // Color mapping for location scales
    const scaleColors = {
        'REGION': '#e74c3c',
        'CITY': '#3498db',
        'BUILDING': '#f39c12',
        'ROOM': '#2ecc71',
        'AREA': '#9b59b6',
        'OBJECT': '#95a5a6',
        'OTHER': '#95a5a6'
    };

    // Initialize the map
    async function initializeMap() {
        try {
            await loadLocations();
            await loadConnections();
            createNetwork();
            setupEventListeners();
            populateLocationSelects();
        } catch (error) {
            console.error("Error initializing map:", error);
            if (typeof showToast === 'function') {
                showToast("Failed to load world map data", "error");
            }
        }
    }

    // Load locations from API
    async function loadLocations() {
        console.log("Loading locations for world:", worldId);
        
        try {
            const response = await fetch(`${API_BASE_URL}/worlds/${worldId}/locations`, {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`Failed to load locations: ${response.status}`);
            }

            locations = await response.json();
            console.log("Loaded locations:", locations);
            
            // Create nodes from locations
            const networkNodes = locations.map(location => {
                const scale = location.scale || 'OTHER';
                const color = scaleColors[scale] || scaleColors['OTHER'];
                
                return {
                    id: location.id,
                    label: location.name,
                    title: `${location.name}\nType: ${scale.replace('_', ' ')}\n${location.description || 'No description'}`,
                    color: {
                        background: color,
                        border: '#2c3e50',
                        highlight: {
                            background: color,
                            border: '#34495e'
                        }
                    },
                    font: {
                        color: '#ffffff',
                        size: 12,
                        face: 'arial'
                    },
                    x: location.map_x || undefined,
                    y: location.map_y ? -location.map_y : undefined, // Invert Y for proper orientation
                    physics: location.map_x === null || location.map_y === null,
                    location: location
                };
            });

            nodes.clear();
            nodes.add(networkNodes);
            
        } catch (error) {
            console.error("Error loading locations:", error);
            throw error;
        }
    }

    // Load connections from API
    async function loadConnections() {
        console.log("Loading connections for world:", worldId);
        
        try {
            const response = await fetch(`${API_BASE_URL}/worlds/${worldId}/location-connections`, {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`Failed to load connections: ${response.status}`);
            }

            connections = await response.json();
            console.log("Loaded connections:", connections);
            
            // Create edges from connections
            const networkEdges = connections.map(connection => ({
                id: `${connection.from_location_id}-${connection.to_location_id}`,
                from: connection.from_location_id,
                to: connection.to_location_id,
                label: connection.path_description || '',
                title: `From: ${connection.from_location?.name || 'Unknown'}\nTo: ${connection.to_location?.name || 'Unknown'}\nPath: ${connection.path_description || 'No description'}`,
                arrows: {
                    to: {
                        enabled: true,
                        scaleFactor: 0.8
                    }
                },
                color: {
                    color: '#7f8c8d',
                    highlight: '#34495e'
                },
                font: {
                    size: 10,
                    align: 'middle'
                },
                connection: connection
            }));

            // Add reverse connections for bidirectional paths
            const reverseEdges = connections
                .filter(conn => conn.is_bidirectional)
                .map(connection => ({
                    id: `${connection.to_location_id}-${connection.from_location_id}`,
                    from: connection.to_location_id,
                    to: connection.from_location_id,
                    label: connection.reverse_path_description || '',
                    title: `From: ${connection.to_location?.name || 'Unknown'}\nTo: ${connection.from_location?.name || 'Unknown'}\nPath: ${connection.reverse_path_description || 'No description'}`,
                    arrows: {
                        to: {
                            enabled: true,
                            scaleFactor: 0.8
                        }
                    },
                    color: {
                        color: '#7f8c8d',
                        highlight: '#34495e'
                    },
                    font: {
                        size: 10,
                        align: 'middle'
                    },
                    connection: connection,
                    isReverse: true
                }));

            edges.clear();
            edges.add([...networkEdges, ...reverseEdges]);
            
        } catch (error) {
            console.error("Error loading connections:", error);
            throw error;
        }
    }

    // Create the Vis.js network
    function createNetwork() {
        const data = {
            nodes: nodes,
            edges: edges
        };

        const options = {
            layout: {
                improvedLayout: true,
                hierarchical: false
            },
            physics: {
                enabled: true,
                stabilization: {
                    enabled: true,
                    iterations: 100,
                    updateInterval: 25
                },
                barnesHut: {
                    gravitationalConstant: -2000,
                    centralGravity: 0.3,
                    springLength: 95,
                    springConstant: 0.04,
                    damping: 0.09
                }
            },
            interaction: {
                hover: true,
                dragNodes: true,
                dragView: true,
                zoomView: true
            },
            nodes: {
                shape: 'circle',
                size: 25,
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                shadow: true,
                smooth: {
                    enabled: true,
                    type: "continuous",
                    roundness: 0.2
                }
            }
        };

        network = new vis.Network(networkContainer, data, options);

        // Network event listeners
        network.on("click", function (params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const location = locations.find(loc => loc.id === nodeId);
                if (location) {
                    showLocationInfo(location);
                }
            } else {
                hideLocationInfo();
            }
        });

        network.on("hoverNode", function (params) {
            const location = locations.find(loc => loc.id === params.node);
            if (location) {
                networkContainer.style.cursor = 'pointer';
            }
        });

        network.on("blurNode", function (params) {
            networkContainer.style.cursor = 'default';
        });

        console.log("Network created successfully");
    }

    // Setup event listeners
    function setupEventListeners() {
        // Layout mode change
        layoutModeSelect.addEventListener('change', (e) => {
            const mode = e.target.value;
            updateLayoutMode(mode);
        });

        // Zoom fit button
        zoomFitBtn.addEventListener('click', () => {
            network.fit();
        });

        // Show/hide connections
        showConnectionsCheckbox.addEventListener('change', (e) => {
            const show = e.target.checked;
            edges.forEach(edge => {
                edges.update({id: edge.id, hidden: !show});
            });
        });

        // Sidebar resizing
        setupSidebarResize();

        // Connection management
        addConnectionBtn.addEventListener('click', () => {
            connectionForm.style.display = 'block';
            addConnectionBtn.style.display = 'none';
        });

        cancelConnectionBtn.addEventListener('click', () => {
            connectionForm.style.display = 'none';
            addConnectionBtn.style.display = 'block';
            connectionCreateForm.reset();
        });

        connectionCreateForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await createConnection();
        });
    }

    // Setup sidebar resizing functionality
    function setupSidebarResize() {
        let isResizing = false;

        // Drag resize handle
        resizeHandle.addEventListener('mousedown', (e) => {
            isResizing = true;
            document.body.style.cursor = 'col-resize';
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;

            const containerRect = sidebar.parentElement.getBoundingClientRect();
            const newWidth = containerRect.right - e.clientX;
            const clampedWidth = Math.max(250, Math.min(600, newWidth));
            
            sidebar.style.width = clampedWidth + 'px';

            if (network) {
                setTimeout(() => network.fit(), 10);
            }
        });

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                document.body.style.cursor = '';
            }
        });
    }

    // Update layout mode
    function updateLayoutMode(mode) {
        const options = {
            physics: {
                enabled: mode === 'auto'
            }
        };

        if (mode === 'grid') {
            // Position nodes based on coordinates or in a grid
            const nodeUpdates = locations.map(location => {
                const node = nodes.get(location.id);
                let x = location.map_x || (location.id % 10) * 150;
                let y = location.map_y ? -location.map_y : Math.floor(location.id / 10) * 150;
                
                return {
                    id: location.id,
                    x: x,
                    y: y,
                    physics: false
                };
            });
            nodes.update(nodeUpdates);
        } else {
            // Enable physics for auto layout
            const nodeUpdates = locations.map(location => ({
                id: location.id,
                physics: true
            }));
            nodes.update(nodeUpdates);
        }

        network.setOptions(options);
    }

    // Show location info panel
    function showLocationInfo(location) {
        infoTitle.textContent = location.name;
        infoContent.innerHTML = `
            <div><strong>Type:</strong> ${location.scale ? location.scale.replace('_', ' ') : 'Unknown'}</div>
            ${location.description ? `<div><strong>Description:</strong> ${location.description}</div>` : ''}
            ${location.atmosphere ? `<div><strong>Atmosphere:</strong> ${location.atmosphere}</div>` : ''}
            ${location.map_x !== null && location.map_y !== null ? `<div><strong>Coordinates:</strong> ${location.map_x}, ${location.map_y}</div>` : ''}
            <div class="mt-2">
                <a href="/ui/worlds/locations/${location.id}/edit" class="btn btn-sm btn-primary">Edit Location</a>
            </div>
        `;
        mapInfo.style.display = 'block';
    }

    // Hide location info panel
    function hideLocationInfo() {
        mapInfo.style.display = 'none';
    }

    // Populate location select dropdowns
    function populateLocationSelects() {
        const options = locations.map(location => 
            `<option value="${location.id}">${location.name}${location.scale ? ` (${location.scale.replace('_', ' ')})` : ''}</option>`
        ).join('');

        fromLocationSelect.innerHTML = '<option value="">-- Select Location --</option>' + options;
        toLocationSelect.innerHTML = '<option value="">-- Select Location --</option>' + options;

        updateConnectionsList();
    }

    // Create new connection
    async function createConnection() {
        const fromLocationId = parseInt(fromLocationSelect.value);
        const toLocationId = parseInt(toLocationSelect.value);
        const pathDescription = document.getElementById('path-description').value.trim();
        const reverseDescription = document.getElementById('reverse-description').value.trim();
        const isBidirectional = document.getElementById('is-bidirectional').checked;

        if (!fromLocationId || !toLocationId) {
            if (typeof showToast === 'function') {
                showToast("Please select both from and to locations", "error");
            }
            return;
        }

        if (fromLocationId === toLocationId) {
            if (typeof showToast === 'function') {
                showToast("Cannot create connection from a location to itself", "error");
            }
            return;
        }

        try {
            const connectionData = {
                from_location_id: fromLocationId,
                to_location_id: toLocationId,
                path_description: pathDescription || null,
                reverse_path_description: reverseDescription || null,
                is_bidirectional: isBidirectional
            };

            const response = await fetch(`${API_BASE_URL}/worlds/${worldId}/location-connections/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(connectionData),
                credentials: 'include'
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Failed to create connection: ${response.status}`);
            }

            const newConnection = await response.json();
            console.log("Created connection:", newConnection);

            if (typeof showToast === 'function') {
                showToast("Connection created successfully", "success");
            }

            // Refresh connections and update display
            await loadConnections();
            updateConnectionsList();

            // Hide form and reset
            connectionForm.style.display = 'none';
            addConnectionBtn.style.display = 'block';
            connectionCreateForm.reset();

        } catch (error) {
            console.error("Error creating connection:", error);
            if (typeof showToast === 'function') {
                showToast(error.message, "error");
            }
        }
    }

    // Update connections list
    function updateConnectionsList() {
        if (connections.length === 0) {
            connectionsList.innerHTML = '<div class="text-muted small text-center py-3">No connections yet</div>';
            return;
        }

        const connectionsHtml = connections.map(connection => {
            const fromName = connection.from_location?.name || 'Unknown';
            const toName = connection.to_location?.name || 'Unknown';
            const description = connection.path_description || 'No description';

            return `
                <div class="connection-item">
                    <div class="connection-actions">
                        <button class="btn btn-sm btn-danger" onclick="deleteConnection(${connection.from_location_id}, ${connection.to_location_id})" title="Delete connection">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                    <div>
                        <strong class="small">${fromName} → ${toName}</strong>
                        ${connection.is_bidirectional ? '<span class="badge bg-info ms-2">Bidirectional</span>' : ''}
                        <div class="connection-path">${description}</div>
                        ${connection.reverse_path_description && connection.is_bidirectional ? 
                            `<div class="connection-path"><em>Return:</em> ${connection.reverse_path_description}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');

        connectionsList.innerHTML = connectionsHtml;
    }

    // Delete connection (global function)
    window.deleteConnection = async function(fromLocationId, toLocationId) {
        if (!confirm('Are you sure you want to delete this connection?')) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/location-connections/${fromLocationId}/${toLocationId}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`Failed to delete connection: ${response.status}`);
            }

            if (typeof showToast === 'function') {
                showToast("Connection deleted successfully", "success");
            }

            // Refresh connections and update display
            await loadConnections();
            updateConnectionsList();

        } catch (error) {
            console.error("Error deleting connection:", error);
            if (typeof showToast === 'function') {
                showToast("Failed to delete connection", "error");
            }
        }
    };

    // Initialize the map when DOM is ready
    initializeMap();

    console.log("World map JS initialized");
});