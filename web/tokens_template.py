TOKENS_MAP_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>NFC Token Map</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; }
        
        /* Hamburger Menu */
        .hamburger {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1001;
            background: white;
            border-radius: 8px;
            padding: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            cursor: pointer;
        }
        .hamburger div {
            width: 25px;
            height: 3px;
            background: #333;
            margin: 5px 0;
            transition: 0.3s;
        }
        
        /* Dropdown Menu */
        .menu {
            position: fixed;
            top: 70px;
            right: 20px;
            z-index: 1000;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.3);
            display: none;
            min-width: 200px;
        }
        .menu.active { display: block; }
        .menu a {
            display: block;
            padding: 15px 20px;
            text-decoration: none;
            color: #333;
            border-bottom: 1px solid #eee;
        }
        .menu a:last-child { border-bottom: none; }
        .menu a:hover { background: #f5f5f5; }
        
        /* Map Container */
        #map {
            height: 100vh;
            width: 100%;
        }
        
        /* Stats Panel */
        .stats {
            position: fixed;
            bottom: 20px;
            left: 20px;
            z-index: 1000;
            background: white;
            border-radius: 8px;
            padding: 15px 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            max-width: 300px;
        }
        .stats h3 { margin-bottom: 10px; font-size: 16px; }
        .stats .stat { 
            display: flex; 
            justify-content: space-between; 
            padding: 5px 0;
            font-size: 14px;
        }
        .stat-label { font-weight: bold; }
        
        /* Popup Styles */
        .leaflet-popup-content {
            margin: 10px;
            min-width: 200px;
        }
        .popup-title {
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 8px;
            color: #333;
        }
        .popup-detail {
            margin: 5px 0;
            font-size: 13px;
        }
        .popup-img {
            width: 64px;
            height: 64px;
            object-fit: contain;
            display: block;
            margin: 10px auto;
        }
        .action-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .action-summon { background: #e3f2fd; color: #1976d2; }
        .action-give { background: #fff3e0; color: #f57c00; }
        .action-time { background: #f3e5f5; color: #7b1fa2; }
    </style>
</head>
<body>
    <!-- Hamburger Menu -->
    <div class="hamburger" onclick="toggleMenu()">
        <div></div>
        <div></div>
        <div></div>
    </div>
    
    <!-- Dropdown Menu -->
    <div class="menu" id="menu">
        <a href="/">Home</a>
        <a href="/log">All Mobs</a>
        <a href="/tokens">Token Map</a>
    </div>
    
    <!-- Map Container -->
    <div id="map"></div>
    
    <!-- Stats Panel -->
    <div class="stats">
        <h3>📍 Token Statistics</h3>
        <div class="stat">
            <span class="stat-label">Total Tokens:</span>
            <span>{{ total_tokens }}</span>
        </div>
        <div class="stat">
            <span class="stat-label">Summon Entities:</span>
            <span>{{ summon_count }}</span>
        </div>
        <div class="stat">
            <span class="stat-label">Give Items:</span>
            <span>{{ give_count }}</span>
        </div>
        <div class="stat">
            <span class="stat-label">Set Time:</span>
            <span>{{ time_count }}</span>
        </div>
    </div>

    <script>
        // Toggle menu
        function toggleMenu() {
            document.getElementById('menu').classList.toggle('active');
        }
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            const menu = document.getElementById('menu');
            const hamburger = document.querySelector('.hamburger');
            if (!menu.contains(event.target) && !hamburger.contains(event.target)) {
                menu.classList.remove('active');
            }
        });
        
        // Token data from server
        let tokens = {{ tokens_json|safe }};
        let markers = {};  // Track markers by token_id
        
        // Initialize map (centered on average of all token positions)
        const centerLat = {{ center_lat }};
        const centerLon = {{ center_lon }};
        const map = L.map('map').setView([centerLat, centerLon], 13);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        // Define marker icons by action type
        const summonIcon = L.divIcon({
            className: 'custom-marker',
            html: '<div style="background: #1976d2; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">👹</div>',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });
        
        const giveIcon = L.divIcon({
            className: 'custom-marker',
            html: '<div style="background: #f57c00; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">🎁</div>',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });
        
        const timeIcon = L.divIcon({
            className: 'custom-marker',
            html: '<div style="background: #7b1fa2; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">⏰</div>',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });
        
        // Function to create marker for a token
        function createMarker(token) {
            let icon = summonIcon;
            if (token.action_type === 'give_item') icon = giveIcon;
            if (token.action_type === 'set_time') icon = timeIcon;
            
            const marker = L.marker([token.lat, token.lon], { icon: icon }).addTo(map);
            
            // Build popup content
            let actionBadgeClass = 'action-summon';
            if (token.action_type === 'give_item') actionBadgeClass = 'action-give';
            if (token.action_type === 'set_time') actionBadgeClass = 'action-time';
            
            let popupContent = `
                <div class="action-badge ${actionBadgeClass}">${token.action_type}</div>
                <div class="popup-title">${token.name || token.entity || token.item || 'Unknown'}</div>
            `;
            
            if (token.image_url) {
                popupContent += `<img src="${token.image_url}" class="popup-img" alt="${token.name}">`;
            }
            
            popupContent += `
                <div class="popup-detail"><strong>Written by:</strong> ${token.written_by || 'Unknown'}</div>
                <div class="popup-detail"><strong>Location:</strong> ${token.lat.toFixed(4)}, ${token.lon.toFixed(4)}</div>
                <div class="popup-detail"><strong>Date:</strong> ${new Date(token.written_at).toLocaleString()}</div>
            `;
            
            if (token.rarity) {
                popupContent += `<div class="popup-detail"><strong>Rarity:</strong> ${token.rarity}</div>`;
            }
            
            if (token.mob_type) {
                popupContent += `<div class="popup-detail"><strong>Type:</strong> ${token.mob_type}</div>`;
            }
            
            marker.bindPopup(popupContent);
            return marker;
        }
        
        // Add initial markers
        tokens.forEach(token => {
            markers[token.token_id] = createMarker(token);
        });
        
        // Fit map to show all markers
        if (tokens.length > 0) {
            const bounds = L.latLngBounds(tokens.map(t => [t.lat, t.lon]));
            map.fitBounds(bounds, { padding: [50, 50] });
        }
        
        // Function to update stats panel
        function updateStats(newTokens) {
            const summonCount = newTokens.filter(t => t.action_type === 'summon_entity').length;
            const giveCount = newTokens.filter(t => t.action_type === 'give_item').length;
            const timeCount = newTokens.filter(t => t.action_type === 'set_time').length;
            
            document.querySelector('.stats .stat:nth-child(2) span:last-child').textContent = newTokens.length;
            document.querySelector('.stats .stat:nth-child(3) span:last-child').textContent = summonCount;
            document.querySelector('.stats .stat:nth-child(4) span:last-child').textContent = giveCount;
            document.querySelector('.stats .stat:nth-child(5) span:last-child').textContent = timeCount;
        }
        
        // Poll for new tokens every 5 seconds
        setInterval(async () => {
            try {
                const response = await fetch('/api/tokens-data');
                const data = await response.json();
                
                // Check for new tokens
                data.tokens.forEach(token => {
                    if (!markers[token.token_id]) {
                        // New token - add marker
                        markers[token.token_id] = createMarker(token);
                        console.log('Added new token:', token.token_id);
                    }
                });
                
                // Update stats
                updateStats(data.tokens);
                tokens = data.tokens;
                
            } catch (error) {
                console.error('Error fetching token updates:', error);
            }
        }, 5000);
    </script>
</body>
</html>
'''
