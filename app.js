let map;
let serviceLayers = {};
let markers = [];

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 20.5937, lng: 78.9629 }, // India center
    zoom: 5,
    styles: [ /* dark theme styles */ ]
  });

  // Load store data
  fetch("stores.json")
    .then((response) => {
      if (!response.ok) {
        throw new Error("stores.json not found");
      }
      return response.json();
    })
    .then((data) => {
      if (!data.length) {
        document.getElementById("errorPanel").innerText = "⚠️ No store data available.";
        document.getElementById("errorPanel").classList.remove("hidden");
        return;
      }
      renderStores(data);
    })
    .catch((err) => {
      document.getElementById("errorPanel").innerText = "⚠️ Failed to load store data.";
      document.getElementById("errorPanel").classList.remove("hidden");
      console.error(err);
    });

  // Add search box
  const input = document.getElementById("searchBox");
  const searchBox = new google.maps.places.SearchBox(input);

  map.controls[google.maps.ControlPosition.TOP_RIGHT].push(input);

  searchBox.addListener("places_changed", () => {
    const places = searchBox.getPlaces();
    if (places.length == 0) return;

    const bounds = new google.maps.LatLngBounds();
    places.forEach((place) => {
      if (!place.geometry) return;
      if (place.geometry.viewport) bounds.union(place.geometry.viewport);
      else bounds.extend(place.geometry.location);
    });
    map.fitBounds(bounds);
  });
}

function renderStores(data) {
  const storeCounts = {};
  markers = [];

  data.forEach((store) => {
    const marker = new google.maps.Marker({
      position: { lat: store.lat, lng: store.lon },
      map,
      title: `${store.source_name}: ${store.store_id}`,
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        scale: 6,
        fillColor: store.color,
        fillOpacity: 1,
        strokeWeight: 1,
        strokeColor: "#000"
      }
    });

    const infowindow = new google.maps.InfoWindow({
      content: `
        <b>${store.source_name}</b><br>
        Store ID: ${store.store_id}<br>
        Lat: ${store.lat}, Lon: ${store.lon}
      `
    });

    marker.addListener("click", () => {
      infowindow.open(map, marker);
    });

    markers.push(marker);

    // Count stores per source
    storeCounts[store.source_name] = (storeCounts[store.source_name] || 0) + 1;
  });

  // Update counts panel
  let countsHtml = "<h4>Store Counts</h4>";
  for (let [source, count] of Object.entries(storeCounts)) {
    const color = data.find((s) => s.source_name === source).color;
    countsHtml += `<p><span style="color:${color}">●</span> ${source}: ${count}</p>`;
  }
  document.getElementById("storeCounts").innerHTML = countsHtml;
}
