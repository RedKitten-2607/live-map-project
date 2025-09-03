let map;

async function initMap() {
  // Map init
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 20.5937, lng: 78.9629 }, // India center
    zoom: 5,
    styles: [
      { elementType: "geometry", stylers: [{ color: "#212121" }] },
      { elementType: "labels.icon", stylers: [{ visibility: "off" }] },
      { elementType: "labels.text.fill", stylers: [{ color: "#757575" }] },
      { elementType: "labels.text.stroke", stylers: [{ color: "#212121" }] },
      {
        featureType: "administrative",
        elementType: "geometry",
        stylers: [{ color: "#757575" }]
      },
      {
        featureType: "poi",
        elementType: "geometry",
        stylers: [{ color: "#181818" }]
      },
      {
        featureType: "road",
        elementType: "geometry.fill",
        stylers: [{ color: "#2c2c2c" }]
      },
      {
        featureType: "water",
        elementType: "geometry",
        stylers: [{ color: "#000000" }]
      }
    ]
  });

  // Load store data
  const response = await fetch("stores.json");
  const stores = await response.json();

  // Create markers
  const markers = stores.map(store => {
    const marker = new google.maps.Marker({
      position: { lat: store.lat, lng: store.lon },
      title: `${store.source_name}: ${store.store_id}`,
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        scale: 6,
        fillColor: store.color,
        fillOpacity: 0.9,
        strokeWeight: 0
      }
    });

    const info = new google.maps.InfoWindow({
      content: `
        <div style="font-size:14px; color:#333;">
          <b>${store.source_name}</b><br>
          Store ID: ${store.store_id}<br>
          Lat: ${store.lat.toFixed(4)}, Lon: ${store.lon.toFixed(4)}
        </div>
      `
    });

    marker.addListener("click", () => {
      info.open(map, marker);
    });

    return marker;
  });

  // Cluster markers
  new markerClusterer.MarkerClusterer({ map, markers });

  // Update store counts panel
  const counts = {};
  stores.forEach(s => {
    counts[s.source_name] = (counts[s.source_name] || 0) + 1;
  });
  document.getElementById("storeCounts").innerHTML = Object.entries(counts)
    .map(([name, count]) => `<div><b>${name}</b>: ${count}</div>`)
    .join("");

  // Search box
  const input = document.getElementById("searchBox");
  const searchBox = new google.maps.places.SearchBox(input);

  map.controls[google.maps.ControlPosition.TOP_RIGHT].push(input);

  searchBox.addListener("places_changed", () => {
    const places = searchBox.getPlaces();
    if (!places || places.length === 0) return;

    const bounds = new google.maps.LatLngBounds();
    places.forEach(place => {
      if (!place.geometry) return;
      if (place.geometry.viewport) bounds.union(place.geometry.viewport);
      else bounds.extend(place.geometry.location);
    });
    map.fitBounds(bounds);
  });
}
