/* ═══════════════════════════════════════════
   track.js  —  Track Now Page
   Map + Search + Filter + Distance
═══════════════════════════════════════════ */

// ── All vaccination centers data ──
const CENTERS = [
    { name: "DHQ Teaching Hospital",        lat: 32.1617, lng: 74.1883, hours: "8am–4pm", distId: "dist1", type: "govt",  area: "Gujranwala City" },
    { name: "Civil Hospital Vaccination",   lat: 32.1877, lng: 74.1945, hours: "9am–3pm", distId: "dist2", type: "govt",  area: "Satellite Town"  },
    { name: "MCH Center Gujranwala",        lat: 32.1712, lng: 74.2021, hours: "8am–2pm", distId: "dist3", type: "mch",   area: "Model Town"      },
    { name: "EPI Centre — Kamoke Road",     lat: 32.1750, lng: 74.1760, hours: "8am–3pm", distId: "dist4", type: "epi",   area: "Kamoke Road"     },
    { name: "District Health Office",       lat: 32.1550, lng: 74.1920, hours: "9am–4pm", distId: "dist5", type: "govt",  area: "Wazirabad Road"  },
    { name: "THQ Hospital Nowshera Virkan", lat: 32.1980, lng: 74.1700, hours: "8am–2pm", distId: "dist6", type: "govt",  area: "Nowshera Virkan" }
];

// ── Global state ──
let map        = null;
let userLat    = null;
let userLng    = null;
let routeLine  = null;
let activeCard = null;

// ── Custom map icons ──
const centerIcon = L.divIcon({
    className: '',
    html: `<div style="background:#6884d3;color:white;width:38px;height:38px;
                border-radius:50% 50% 50% 0;transform:rotate(-45deg);
                display:flex;align-items:center;justify-content:center;
                box-shadow:0 3px 12px rgba(104,132,211,.5);border:3px solid white;">
             <span style="transform:rotate(45deg);font-size:17px;">🏥</span>
           </div>`,
    iconSize: [38, 38], iconAnchor: [19, 38], popupAnchor: [0, -42]
});

const userIcon = L.divIcon({
    className: '',
    html: `<div style="background:#f06272;color:white;width:40px;height:40px;
                border-radius:50%;display:flex;align-items:center;justify-content:center;
                box-shadow:0 3px 14px rgba(240,98,114,.5);border:3px solid white;font-size:18px;">
             📍
           </div>`,
    iconSize: [40, 40], iconAnchor: [20, 20]
});


/* ════════════════════════════════════
   buildMap(lat, lng, isUser)
════════════════════════════════════ */
function buildMap(lat, lng, isUser) {
    // Hide overlay
    var prompt = document.getElementById('locPrompt');
    if (prompt) prompt.style.display = 'none';

    // Destroy old map
    if (map) { map.remove(); map = null; }

    // Create map
    map = L.map('tig-map', { zoomControl: true, scrollWheelZoom: false })
            .setView([lat, lng], 13);

    // OpenStreetMap tiles (free, no API key)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        //attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        maxZoom: 18
    }).addTo(map);

    // Add hospital markers
    CENTERS.forEach(function(c) {
        var marker = L.marker([c.lat, c.lng], { icon: centerIcon }).addTo(map);

        marker.bindPopup(
            `<div style="font-family:'Open Sans',sans-serif;min-width:170px;padding:4px 0">
               <strong style="color:#526fc0;font-size:13px;">${c.name}</strong><br>
               <span style="font-size:11px;color:#6b7db3;">
                 🕐 ${c.hours}&nbsp;&nbsp;📍 ${c.area}
               </span>
               ${isUser ? `<br><span style="font-size:12px;font-weight:700;color:#526fc0;
                 margin-top:6px;display:block;">
                 📏 ${getDistance(lat, lng, c.lat, c.lng)} km away</span>` : ''}
             </div>`
        );

        // Click on marker → draw line from user
        marker.on('click', function() {
            if (isUser) {
                drawLineTo(lat, lng, c.lat, c.lng, c.name);
                highlightCard(c.distId);
            }
        });
    });

    // User marker + circle
    if (isUser) {
        userLat = lat;
        userLng = lng;

        L.marker([lat, lng], { icon: userIcon })
         .addTo(map)
         .bindPopup('<div style="font-family:\'Open Sans\',sans-serif"><strong style="color:#f06272">📍 You are here</strong></div>')
         .openPopup();

        L.circle([lat, lng], {
            color: '#6884d3',
            fillColor: '#e8ecff',
            fillOpacity: 0.3,
            radius: 700,
            weight: 2
        }).addTo(map);

        document.getElementById('locStatusText').textContent = '✓ Live location active';

        // Show all distances
        showAllDistances(lat, lng);

    } else {
        document.getElementById('locStatusText').textContent = 'Showing Gujranwala — enable location for distances';
        CENTERS.forEach(function(c) {
            var el = document.getElementById(c.distId);
            if (el) el.innerHTML = '<i class="fas fa-route me-1"></i><span style="color:#f06272">Enable location for distance</span>';
        });
    }
}


/* ════════════════════════════════════
   showAllDistances
════════════════════════════════════ */
function showAllDistances(uLat, uLng) {
    CENTERS.forEach(function(c) {
        var dist = getDistance(uLat, uLng, c.lat, c.lng);
        var el   = document.getElementById(c.distId);
        if (el) {
            el.innerHTML = '<i class="fas fa-route me-1"></i>' +
                '<span style="color:#526fc0;font-weight:700;">' + dist + ' km away</span>';
            el.classList.add('has-distance');
        }
    });
}


/* ════════════════════════════════════
   getDistance — Haversine formula
════════════════════════════════════ */
function getDistance(lat1, lng1, lat2, lng2) {
    var R    = 6371;
    var dLat = toRad(lat2 - lat1);
    var dLng = toRad(lng2 - lng1);
    var a    = Math.sin(dLat/2) * Math.sin(dLat/2) +
               Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
               Math.sin(dLng/2) * Math.sin(dLng/2);
    return (R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))).toFixed(1);
}

function toRad(deg) { return deg * (Math.PI / 180); }


/* ════════════════════════════════════
   drawLineTo — dashed line on map
════════════════════════════════════ */
function drawLineTo(uLat, uLng, cLat, cLng, centerName) {
    if (!map) return;

    // Remove previous line
    if (routeLine) { map.removeLayer(routeLine); routeLine = null; }

    // Draw dashed line
    routeLine = L.polyline(
        [[uLat, uLng], [cLat, cLng]],
        { color: '#6884d3', weight: 3, opacity: 0.85, dashArray: '8, 6' }
    ).addTo(map);

    // Fit view
    map.fitBounds(L.latLngBounds([uLat, uLng], [cLat, cLng]), { padding: [50, 50] });

    // Distance popup at midpoint
    var midLat = (uLat + cLat) / 2;
    var midLng = (uLng + cLng) / 2;
    var dist   = getDistance(uLat, uLng, cLat, cLng);

    L.popup({ closeButton: true, className: 'dist-popup' })
     .setLatLng([midLat, midLng])
     .setContent(
         `<div style="font-family:'Open Sans',sans-serif;text-align:center;padding:4px 8px">
            <strong style="color:#526fc0;font-size:13px;">📏 ${dist} km</strong><br>
            <span style="font-size:11px;color:#6b7db3;">to ${centerName}</span>
          </div>`
     )
     .openOn(map);
}


/* ════════════════════════════════════
   flyTo — called from card click
════════════════════════════════════ */
function flyTo(lat, lng, distId) {
    if (!map) { loadDefaultMap(); return; }

    var center = CENTERS.find(function(c) { return c.distId === distId; });
    if (!center) return;

    highlightCard(distId);

    if (userLat !== null && userLng !== null) {
        drawLineTo(userLat, userLng, lat, lng, center.name);
    } else {
        map.flyTo([lat, lng], 16, { animate: true, duration: 1.0 });
    }
}


/* ════════════════════════════════════
   highlightCard
════════════════════════════════════ */
function highlightCard(distId) {
    // Remove previous highlight
    if (activeCard) {
        activeCard.classList.remove('active-card');
    }

    // Find and highlight new card
    var cardEl = document.getElementById('card-' + distId);
    if (cardEl) {
        cardEl.classList.add('active-card');
        activeCard = cardEl;

        // Smooth scroll to card
        cardEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}


/* ════════════════════════════════════
   requestLocation
════════════════════════════════════ */
function requestLocation() {
    var prompt = document.getElementById('locPrompt');
    if (prompt) prompt.style.display = 'none';

    document.getElementById('locStatusText').textContent = 'Detecting location…';

    if (!navigator.geolocation) {
        loadDefaultMap();
        return;
    }

    navigator.geolocation.getCurrentPosition(
        function(pos) {
            buildMap(pos.coords.latitude, pos.coords.longitude, true);
        },
        function(err) {
            console.warn('Location error:', err.message);
            document.getElementById('locStatusText').textContent = 'Location unavailable — showing Gujranwala';
            loadDefaultMap();
        },
        { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
    );
}


/* ════════════════════════════════════
   loadDefaultMap — fallback to Gujranwala center
════════════════════════════════════ */
function loadDefaultMap() {
    buildMap(32.1617, 74.1883, false);
}


/* ════════════════════════════════════
   SEARCH FUNCTIONALITY
════════════════════════════════════ */
var searchInput    = document.getElementById('hospitalSearch');
var suggestionsBox = document.getElementById('suggestionsBox');

// Show suggestions while typing
if (searchInput) {
    searchInput.addEventListener('input', function() {
        var query = this.value.trim().toLowerCase();

        if (query.length < 2) {
            suggestionsBox.classList.remove('open');
            suggestionsBox.innerHTML = '';
            return;
        }

        // Build suggestions from CENTERS data
        var matches = CENTERS.filter(function(c) {
            return c.name.toLowerCase().includes(query) ||
                   c.area.toLowerCase().includes(query) ||
                   c.type.toLowerCase().includes(query);
        });

        if (matches.length === 0) {
            suggestionsBox.classList.remove('open');
            return;
        }

        suggestionsBox.innerHTML = matches.map(function(c) {
            return `<div class="suggestion-item" onclick="selectSuggestion('${c.distId}', '${c.name}')">
                      <i class="fas fa-hospital"></i>
                      <div>
                        <div style="font-weight:600;font-size:13px;">${c.name}</div>
                        <div style="font-size:11px;color:#9aa5c4;">${c.area} · ${c.hours}</div>
                      </div>
                    </div>`;
        }).join('');

        suggestionsBox.classList.add('open');
    });

    // Close suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.classList.remove('open');
        }
    });

    // Enter key triggers search
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') doSearch();
    });
}


/* ════════════════════════════════════
   selectSuggestion — click from dropdown
════════════════════════════════════ */
function selectSuggestion(distId, name) {
    searchInput.value = name;
    suggestionsBox.classList.remove('open');

    var center = CENTERS.find(function(c) { return c.distId === distId; });
    if (center) {
        // Filter cards to show only this one
        filterBySearch(name);
        // Fly map to it
        flyTo(center.lat, center.lng, distId);
    }
}


/* ════════════════════════════════════
   doSearch — Search button click
════════════════════════════════════ */
function doSearch() {
    var query = searchInput.value.trim().toLowerCase();
    suggestionsBox.classList.remove('open');

    if (!query) { showAllCards(); return; }

    filterBySearch(query);

    // If exact match found, fly to it
    var match = CENTERS.find(function(c) {
        return c.name.toLowerCase().includes(query) ||
               c.area.toLowerCase().includes(query);
    });
    if (match && map) {
        flyTo(match.lat, match.lng, match.distId);
    }
}


/* ════════════════════════════════════
   filterBySearch
════════════════════════════════════ */
function filterBySearch(query) {
    var cards   = document.querySelectorAll('.center-card-wrap');
    var noRes   = document.getElementById('noResults');
    var visible = 0;

    cards.forEach(function(card) {
        var name = card.getAttribute('data-name') || '';
        if (name.includes(query.toLowerCase())) {
            card.style.display = '';
            visible++;
        } else {
            card.style.display = 'none';
        }
    });

    noRes.classList.toggle('d-none', visible > 0);
}


/* ════════════════════════════════════
   clearSearch
════════════════════════════════════ */
function clearSearch() {
    if (searchInput) searchInput.value = '';
    suggestionsBox.classList.remove('open');
    showAllCards();
}

function showAllCards() {
    document.querySelectorAll('.center-card-wrap').forEach(function(c) {
        c.style.display = '';
    });
    document.getElementById('noResults').classList.add('d-none');
}


/* ════════════════════════════════════
   filterCenters — pill buttons
════════════════════════════════════ */
function filterCenters(type, btn) {
    // Update active pill
    document.querySelectorAll('.filter-pill').forEach(function(p) {
        p.classList.remove('active');
    });
    btn.classList.add('active');

    // Clear search box
    if (searchInput) searchInput.value = '';

    // Filter cards
    var cards  = document.querySelectorAll('.center-card-wrap');
    var noRes  = document.getElementById('noResults');
    var visible = 0;

    cards.forEach(function(card) {
        var cardType = card.getAttribute('data-type') || '';
        if (type === 'all' || cardType === type) {
            card.style.display = '';
            visible++;
        } else {
            card.style.display = 'none';
        }
    });

    noRes.classList.toggle('d-none', visible > 0);
}
