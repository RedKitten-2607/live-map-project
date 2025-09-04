let map;
let serviceLayers = {}; // Stores markers grouped by platform

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 20.5937, lng: 78.9629 }, // India center
    zoom: 5,
    mapTypeId: "roadmap",
    styles: [ // dark theme
      { elementType: "geometry", stylers: [{ color: "#212121" }] },
      { elementType: "labels.icon", stylers: [{ visibility: "off" }] },
      { elementType: "labels.text.fill", stylers: [{ color: "#757575" }] },
      { elementType: "labels.text.stroke", stylers: [{ color: "#212121" }] },
      { featureType: "administrative", elementType: "geometry", stylers: [{ color: "#757575" }] },
      { featureType: "poi", elementType: "geometry", stylers: [{ color: "#181818" }] },
      { featureType: "road", elementType: "geometry", stylers: [{ color: "#383838" }] },
      { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#212121" }] },
      { featureType: "water", elementType: "geometry", stylers: [{ color: "#000000" }] },
      { featureType: "water", elementType: "labels.text.fill", stylers: [{ color: "#3d3d3d" }] }
    ]
  });

  // Load stores.json
  fetch("stores.json")
    .then((res) => res.json())
    .then((data) => {
      console.log("Loaded stores:", data.length);
      addMarkersByPlatform(data);
      buildLegendAndControls(data);
    })
    .catch((err) => console.error("Error loading stores.json:", err));

  // Add search box
  const input = document.getElementById("searchBox");
  const searchBox = new google.maps.places.SearchBox(input);

  map.controls[google.maps.ControlPosition.TOP_RIGHT].push(input);

  searchBox.addListener("places_changed", () => {
    const places = searchBox.getPlaces();
    if (places.length === 0) return;
    const bounds = new google.maps.LatLngBounds();
    places.forEach((place) => {
      if (!place.geometry) return;
      if (place.geometry.viewport) {
        bounds.union(place.geometry.viewport);
      } else {
        bounds.extend(place.geometry.location);
      }
    });
    map.fitBounds(bounds);
  });
}

// Group markers by service and add to map
function addMarkersByPlatform(data) {
  const infoWindow = new google.maps.InfoWindow();

  data.forEach((store) => {
    const marker = new google.maps.Marker({
      position: { lat: store.lat, lng: store.lon },
      map: map,
      title: `${store.source_name}: ${store.store_id}`,
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: store.color,
        fillOpacity: 0.9,
        strokeWeight: 1,
        strokeColor: "#000000",
        scale: 6,
      },
    });

    marker.addListener("click", () => {
      infoWindow.setContent(`
        <div style="font-size:14px;line-height:1.4;">
          <b>${store.source_name}</b><br>
          Store ID: ${store.store_id}<br>
          Lat: ${store.lat.toFixed(4)}, Lon: ${store.lon.toFixed(4)}
        </div>
      `);
      infoWindow.open(map, marker);
    });

    if (!serviceLayers[store.source_name]) {
      serviceLayers[store.source_name] = [];
    }
    serviceLayers[store.source_name].push(marker);
  });
}

// Build legend with counts + checkboxes
function buildLegendAndControls(data) {
  const legend = document.createElement("div");
  legend.classList.add("info-panel");

  const counts = {};
  data.forEach((s) => {
    counts[s.source_name] = (counts[s.source_name] || 0) + 1;
  });

  legend.innerHTML = "<h4>Store Counts</h4>";

  Object.keys(counts).forEach((service) => {
    const color = serviceLayers[service][0].icon.fillColor;
    const checkboxId = `chk-${service}`;

    const container = document.createElement("div");
    container.innerHTML = `
      <input type="checkbox" id="${checkboxId}" checked>
      <label for="${checkboxId}">
        <span style="color:${color};font-size:16px;">●</span> ${service}: ${counts[service]}
      </label>
    `;
    legend.appendChild(container);

    // Attach toggle logic directly
    container.querySelector("input").addEventListener("change", (e) => {
      serviceLayers[service].forEach((marker) => {
        marker.setMap(e.target.checked ? map : null);
      });
    });
  });

  map.controls[google.maps.ControlPosition.LEFT_TOP].push(legend);
}
