/* 
   TIG — Patient Dashboard JavaScript
   FIXED: Distance calculation + Line drawing to hospital
   No API key needed  uses OpenStreetMap (free)
   */

// ── Vaccination Centers (coordinates) ──
const CENTERS = [
  { name: "DHQ Teaching Hospital",       lat: 32.1617, lng: 74.1883, hours: "8am–4pm", distId: "dist1" },
  { name: "Civil Hospital Vaccination",  lat: 32.1877, lng: 74.1945, hours: "9am–3pm", distId: "dist2" },
  { name: "MCH Center Gujranwala",       lat: 32.1712, lng: 74.2021, hours: "8am–2pm", distId: "dist3" }
];

// ── Global variables ──
let map        = null;   // Leaflet map instance
let userLat    = null;   // User's latitude
let userLng    = null;   // User's longitude
let routeLine  = null;   // The drawn line on map
let activeCard = null;   // Currently highlighted center card

// ── Icons ──
const centerIcon = L.divIcon({
  className: '',
  html: `<div style="background:#6884d3;color:white;width:36px;height:36px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);display:flex;align-items:center;justify-content:center;box-shadow:0 3px 10px rgba(104,132,211,.55);border:3px solid white;">
           <span style="transform:rotate(45deg);font-size:16px;">🏥</span>
         </div>`,
  iconSize: [36,36], iconAnchor: [18,36], popupAnchor: [0,-40]
});

const userIcon = L.divIcon({
  className: '',
  html: `<div style="background:#f06272;color:white;width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 3px 12px rgba(240,98,114,.55);border:3px solid white;font-size:18px;">📍</div>`,
  iconSize: [38,38], iconAnchor: [19,19]
});


/* ════════════════════════════════════════
   buildMap(lat, lng, isUser)
   Builds the Leaflet map
════════════════════════════════════════ */
function buildMap(lat, lng, isUser) {
  document.getElementById('locPrompt').style.display  = 'none';
  document.getElementById('mapOverlay').style.display = 'flex';

  if (map) { map.remove(); map = null; }

  map = L.map('tig-map', { zoomControl: true, scrollWheelZoom: false })
          .setView([lat, lng], 13);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 18
  }).addTo(map);

  // Add hospital markers — clicking them draws a line
  CENTERS.forEach(function(c) {
    var marker = L.marker([c.lat, c.lng], { icon: centerIcon }).addTo(map);

    marker.bindPopup(
      `<div style="font-family:'Poppins',sans-serif;min-width:160px;padding:4px 0">
        <strong style="color:#526fc0;font-size:13px;">${c.name}</strong><br>
        <span style="font-size:11px;color:#6b7db3;">🕐 ${c.hours}<br>📍 Gujranwala</span>
        ${isUser ? `<br><span style="font-size:12px;font-weight:600;color:#526fc0;margin-top:4px;display:block;">
          📏 Distance: ${getDistance(lat, lng, c.lat, c.lng)} km</span>` : ''}
      </div>`
    );

    // When hospital marker clicked → draw line from user
    marker.on('click', function() {
      if (isUser) {
        drawLineTo(lat, lng, c.lat, c.lng, c.name);
        highlightCard(c.distId);
      }
    });
  });

  // User location
  if (isUser) {
    userLat = lat;
    userLng = lng;

    L.marker([lat, lng], { icon: userIcon })
      .addTo(map)
      .bindPopup('<div style="font-family:Poppins,sans-serif"><strong style="color:#f06272">📍 You are here</strong></div>')
      .openPopup();

    L.circle([lat, lng], {
      color: '#6884d3', fillColor: '#F3F0FF', fillOpacity: 0.25, radius: 700
    }).addTo(map);

    document.getElementById('locStatusText').textContent = '✓ Live location active';

    // ✅ Calculate and show distances immediately
    showAllDistances(lat, lng);

  } else {
    document.getElementById('locStatusText').textContent = 'Showing Gujranwala';
    CENTERS.forEach(function(c) {
      var el = document.getElementById(c.distId);
      if (el) el.innerHTML = '<span style="color:#f06272">enable location</span>';
    });
  }
}


/* ════════════════════════════════════════
   showAllDistances(uLat, uLng)
   Shows distance for ALL 3 centers in list
════════════════════════════════════════ */
function showAllDistances(uLat, uLng) {
  CENTERS.forEach(function(c) {
    var dist = getDistance(uLat, uLng, c.lat, c.lng);
    var el   = document.getElementById(c.distId);
    if (el) {
      el.innerHTML = '<span style="color:#526fc0;font-weight:700;">' + dist + ' km away</span>';
    }
  });
}


/* ════════════════════════════════════════
   getDistance(lat1, lng1, lat2, lng2)
   Returns distance in km (Haversine formula)
════════════════════════════════════════ */
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


/* ════════════════════════════════════════
   drawLineTo(uLat, uLng, cLat, cLng, name)
   Draws a dashed line from user → hospital
   Called when user clicks center in list OR map pin
════════════════════════════════════════ */
function drawLineTo(uLat, uLng, cLat, cLng, centerName) {
  if (!map) return;

  // Remove any previously drawn line
  if (routeLine) {
    map.removeLayer(routeLine);
    routeLine = null;
  }

  // Draw dashed line from user location to center
  routeLine = L.polyline(
    [[uLat, uLng], [cLat, cLng]],
    {
      color:     '#6884d3',
      weight:    3,
      opacity:   0.85,
      dashArray: '8, 6'       // dashed style like Google Maps
    }
  ).addTo(map);

  // Fit map view to show both user and hospital
  var bounds = L.latLngBounds(
    [uLat, uLng],
    [cLat, cLng]
  );
  map.fitBounds(bounds, { padding: [50, 50] });

  // Show distance popup on the line midpoint
  var midLat = (uLat + cLat) / 2;
  var midLng = (uLng + cLng) / 2;
  var dist   = getDistance(uLat, uLng, cLat, cLng);

  L.popup({ closeButton: true, className: 'dist-popup' })
    .setLatLng([midLat, midLng])
    .setContent(
      `<div style="font-family:'Poppins',sans-serif;text-align:center;padding:4px 6px;">
        <strong style="color:#526fc0;font-size:13px;">📏 ${dist} km</strong><br>
        <span style="font-size:11px;color:#6b7db3;">to ${centerName}</span>
      </div>`
    )
    .openOn(map);
}


/* ════════════════════════════════════════
   flyTo(lat, lng, distId)
   Called when clicking center item in the list below map
════════════════════════════════════════ */
function flyTo(lat, lng, distId) {
  if (!map) return;

  // Find matching center
  var center = CENTERS.find(function(c) { return c.distId === distId; });
  if (!center) return;

  // If user location is known → draw line
  if (userLat !== null && userLng !== null) {
    drawLineTo(userLat, userLng, lat, lng, center.name);
    highlightCard(distId);
  } else {
    // Just fly to hospital if no user location
    map.flyTo([lat, lng], 15, { animate: true, duration: 1.0 });
  }
}


/* ════════════════════════════════════════
   highlightCard(distId)
   Highlights the selected center card in list
════════════════════════════════════════ */
function highlightCard(distId) {
  // Remove highlight from previous
  if (activeCard) {
    activeCard.style.background  = '';
    activeCard.style.borderColor = '';
    activeCard.style.transform   = '';
  }

  // Highlight new selected card
  var card = document.getElementById('card-' + distId);
  if (card) {
    card.style.background   = '#e8ecff';
    card.style.borderColor  = '#6884d3';
    card.style.transform    = 'translateX(5px)';
    activeCard = card;
  }
}


/* ════════════════════════════════════════
   requestLocation()
   Called when "Allow My Location" is clicked
════════════════════════════════════════ */
function requestLocation() {
  document.getElementById('locPrompt').style.display  = 'none';
  document.getElementById('mapOverlay').style.display = 'flex';
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
      loadDefaultMap();
    },
    { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
  );
}


/* ════════════════════════════════════════
   loadDefaultMap()
   Fallback — centers on Gujranwala
════════════════════════════════════════ */
function loadDefaultMap() {
  buildMap(32.1617, 74.1883, false);
}