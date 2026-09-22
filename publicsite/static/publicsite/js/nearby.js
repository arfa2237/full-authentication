/* ═══════════════════════════════════════════
   nearby.js — Ayesha Dispensary Location Page
   Free map (Leaflet) + free road routing (OSRM
   via Leaflet Routing Machine). No API key needed.
═══════════════════════════════════════════ */

// Ayesha Dispensary — Main Road, Peoples Colony, Gujranwala (verified real location)
var ayeshaLat = 32.1381538;
var ayeshaLng = 74.2081076;

var map = null;
var ayeshaMarker = null;
var userMarker = null;
var userCircle = null;
var userLocation = null;
var routingControl = null;

function initMap() {
    if (map) return;

    var mapEl = document.getElementById('tig-map');
    if (!mapEl) {
        console.error('nearby.js: #tig-map element not found on this page.');
        return;
    }

    // FIX: maxZoom raised to 20. maxNativeZoom on each tile layer tells
    // Leaflet the highest zoom level actual tile images exist for; if the
    // user zooms past that, Leaflet automatically upscales the last real
    // tile (slightly blurry) instead of showing nothing. That combination
    // is what stops the map from ever going blank/grey no matter how far
    // someone zooms in.
    map = L.map('tig-map', {
        maxZoom: 19,
        minZoom: 3
    }).setView([ayeshaLat, ayeshaLng], 15);

    // Original map exactly as it was at the start — standard OpenStreetMap
    // OpenStreetMap standard tiles — no CARTO API key required
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
    // Required by OSM tile usage policy
    crossOrigin: true
    }).addTo(map);

    ayeshaMarker = L.marker([ayeshaLat, ayeshaLng], {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(map);
    ayeshaMarker.bindPopup('<b>Ayesha Dispensary</b><br>Peoples Colony, Gujranwala<br>Free EPI Vaccines');

    // FIX: invalidateSize() on every zoom/move end too — not just once on
    // load. Leaflet caches the container's pixel size internally; if that
    // cached size is even slightly wrong (common when the map sits inside
    // a flex/grid layout, or the page is still doing layout/animations
    // when the map first initializes), tiles beyond the "known" area will
    // not render as you zoom or pan, leaving blank grey patches.
    map.on('zoomend moveend', function () {
        map.invalidateSize();
    });

    // Re-check size whenever the window is resized (orientation change,
    // devtools opening, sidebar collapsing, etc.)
    window.addEventListener('resize', function () {
        if (map) map.invalidateSize();
    });

    // Fix leaflet rendering issue when map container was hidden/resized on load
    setTimeout(function () { if (map) map.invalidateSize(); }, 300);
    // A second, later check catches slow web-font/layout shifts that can
    // still throw off the container size after the first check.
    setTimeout(function () { if (map) map.invalidateSize(); }, 1000);
}

/* Skip location — just show the dispensary on the map */
function loadDefaultMap() {
    var overlay = document.getElementById('locPrompt');
    if (overlay) overlay.style.display = 'none';

    if (!map) initMap();
    map.setView([ayeshaLat, ayeshaLng], 15);

    var statusEl = document.getElementById('locStatusText');
    if (statusEl) statusEl.textContent = 'Showing Ayesha Dispensary';

    var distEl = document.getElementById('distAyesha');
    if (distEl) {
        distEl.innerHTML = '<i class="fas fa-route me-1"></i>Ayesha Dispensary, Gujranwala';
        distEl.classList.remove('has-distance');
    }

    var panel = document.getElementById('routePanel');
    if (panel) panel.classList.remove('active');
}

/* Ask for the user's location, then draw the route + distance to the dispensary */
function requestLocation() {
    var overlay = document.getElementById('locPrompt');
    if (overlay) overlay.style.display = 'none';

    var statusEl = document.getElementById('locStatusText');

    if (!navigator.geolocation) {
        if (statusEl) statusEl.textContent = 'Location not supported on this device';
        return;
    }

    if (statusEl) statusEl.textContent = 'Detecting location…';

    navigator.geolocation.getCurrentPosition(
        function (position) {
            userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            if (statusEl) statusEl.textContent = 'Location found — calculating route...';
            showRoute();
        },
        function (error) {
            if (statusEl) statusEl.textContent = 'Location unavailable — showing Ayesha Dispensary';
            console.warn('Geolocation error:', error.message);
            loadDefaultMap();
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
}

function showRoute() {
    if (!userLocation) return;
    if (!map) initMap();

    // Remove old route/markers
    if (routingControl) {
        map.removeControl(routingControl);
        routingControl = null;
    }
    if (userMarker) map.removeLayer(userMarker);
    if (userCircle) map.removeLayer(userCircle);

    // User marker
    userMarker = L.marker([userLocation.lat, userLocation.lng], {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(map);
    userMarker.bindPopup('Your Location');

    userCircle = L.circle([userLocation.lat, userLocation.lng], {
        radius: 100,
        color: '#4a66b0',
        fillColor: '#8fa4e0',
        fillOpacity: 0.2
    }).addTo(map);

    // Calculate road route using Leaflet Routing Machine (free OSRM)
    routingControl = L.Routing.control({
        waypoints: [
            L.latLng(userLocation.lat, userLocation.lng),
            L.latLng(ayeshaLat, ayeshaLng)
        ],
        routeWhileDragging: false,
        show: false,
        addWaypoints: false,
        draggableWaypoints: false,
        fitSelectedRoutes: true,
        showAlternatives: false,
        createMarker: function () { return null; }
    }).addTo(map);

    routingControl.on('routesfound', function (e) {
        var route = e.routes[0];
        var summary = route.summary;
        var totalDistance = summary.totalDistance; // meters
        var totalTime = summary.totalTime; // seconds

        var distanceKm = (totalDistance / 1000).toFixed(1);
        var distanceM  = totalDistance.toFixed(0);
        var distDisplay = totalDistance > 1000 ? distanceKm + ' km' : distanceM + ' m';

        var distanceEl = document.getElementById('routeDistance');
        var timeEl = document.getElementById('routeTime');
        var stepsCountEl = document.getElementById('routeStepsCount');
        if (distanceEl) distanceEl.textContent = distDisplay;
        if (timeEl) timeEl.textContent = formatTime(totalTime);
        if (stepsCountEl) stepsCountEl.textContent = route.instructions.length;

        var stepsHtml = '';
        route.instructions.forEach(function (instruction, index) {
            var stepDist = instruction.distance > 1000 ?
                (instruction.distance / 1000).toFixed(1) + ' km' :
                instruction.distance.toFixed(0) + ' m';
            stepsHtml += '' +
                '<li class="route-step">' +
                    '<div class="route-step-icon">' + (index + 1) + '</div>' +
                    '<div class="route-step-text">' + instruction.text + '</div>' +
                    '<div class="route-step-distance">' + stepDist + '</div>' +
                '</li>';
        });
        var stepsListEl = document.getElementById('routeSteps');
        if (stepsListEl) stepsListEl.innerHTML = stepsHtml;

        var panel = document.getElementById('routePanel');
        if (panel) panel.classList.add('active');

        var distEl = document.getElementById('distAyesha');
        if (distEl) {
            distEl.innerHTML = '<i class="fas fa-route me-1"></i>' + distDisplay + ' from your location';
            distEl.classList.add('has-distance');
        }

        var statusEl = document.getElementById('locStatusText');
        if (statusEl) statusEl.textContent = 'Route found — ' + distDisplay;

        // FIX: fitSelectedRoutes already re-fits the view/zoom for the
        // route bounds, which can leave Leaflet's cached container size
        // stale for a moment — re-check right after.
        setTimeout(function () { if (map) map.invalidateSize(); }, 200);
    });

    // Fallback to straight-line distance if routing fails/times out
    setTimeout(function () {
        var panel = document.getElementById('routePanel');
        if (panel && !panel.classList.contains('active')) {
            var distance = calculateDistance(userLocation.lat, userLocation.lng, ayeshaLat, ayeshaLng);
            var distText = distance < 1 ?
                Math.round(distance * 1000) + ' m' :
                distance.toFixed(1) + ' km';

            var distEl = document.getElementById('distAyesha');
            if (distEl) {
                distEl.innerHTML = '<i class="fas fa-route me-1"></i>' + distText + ' (straight line) from your location';
                distEl.classList.add('has-distance');
            }

            var statusEl = document.getElementById('locStatusText');
            if (statusEl) statusEl.textContent = 'Location found — ' + distText;
        }
    }, 4000);
}

function formatTime(seconds) {
    if (seconds < 60) return Math.round(seconds) + ' sec';
    var mins = Math.floor(seconds / 60);
    var hrs = Math.floor(mins / 60);
    if (hrs > 0) return hrs + ' hr ' + (mins % 60) + ' min';
    return mins + ' min';
}

function flyToAyesha() {
    if (!map) initMap();
    if (map) {
        map.flyTo([ayeshaLat, ayeshaLng], 16);
        if (ayeshaMarker) ayeshaMarker.openPopup();
    }
}

/* Haversine distance (fallback if OSRM route fails) */
function calculateDistance(lat1, lon1, lat2, lon2) {
    var R = 6371;
    var dLat = (lat2 - lat1) * Math.PI / 180;
    var dLon = (lon2 - lon1) * Math.PI / 180;
    var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

function scrollToMap() {
    var mapSection = document.querySelector('.map-section');
    if (mapSection) mapSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* ── DEFENSIVE FIX ──────────────────────────────────────────────
   Explicitly attach every function used by inline onclick="..."
   handlers to the global window object. This guarantees they are
   always callable from HTML onclick attributes no matter how this
   script gets loaded/bundled/minified in the future — eliminates
   the "X is not defined" class of errors permanently.
   ──────────────────────────────────────────────────────────────── */
window.initMap = initMap;
window.loadDefaultMap = loadDefaultMap;
window.requestLocation = requestLocation;
window.flyToAyesha = flyToAyesha;
window.scrollToMap = scrollToMap;

document.addEventListener('DOMContentLoaded', function () {
    initMap();
});