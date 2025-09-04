let map;
let layers = {};
let markers = {};
let storeCounts = {};

function initMap() {
  // Dark theme styles
  const darkStyle = [
    { elementType: "geometry", stylers: [{ color: "#212121" }] },
    { elementType: "labels.icon", stylers: [{ visibility: "off" }] },
    { elementType: "labels.text.fill", stylers: [{ color: "#757575" }] },
    { elementType: "labels.text.stroke", stylers: [{ color: "#212121" }] },
    {
      featureType: "administrative",
      elementType: "geometry",
      stylers: [{ color: "#757575" }],
    },
    {
      featureType: "poi",
      elementType: "geometry",
      stylers: [{ color: "#181818" }],
    },
    {
      featureType: "road",
      elementType: "geometry.fill",
      stylers: [{ color: "#2c2c2c" }],
    },
    {
      featureType: "road",
      elementType: "geometry.stroke",
      stylers: [{ color: "#1c1c1c" }],
    },
    {
      featureType: "water",
      elementType: "geometry",
      stylers: [{ color: "#000000" }],
    },
  ];

  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 20.5937, lng: 78.9629 }, // India
    zoom: 5,
    styles: darkStyle,
  });

  // SearchBox
  const input = document.getElementById("searchBox");
  const searchBox = new google.maps.places.SearchBox(input);
  map.controls[google.maps.ControlPosition.TOP_CENTER].push(input);

  map.addListener("bounds_changed", () => {
    searchBox.setBounds(map.getBounds());
  });

  searchBox.addListener("places_changed", () => {
    const places = searchBox.getPlaces();
    if (places.length === 0) return;

    const bounds = new google.maps.LatLngBounds();
    places.forEach((place) => {
      if (!place.geometry) return;
      if (place.geometry.viewport) bounds.union(place.geometry.viewport);
      else bounds.extend(place.geometry.location);
    });
    map.fitBounds(bounds);
  });

  // Load store data
  fetch("stores.json")
    .then((res) => res.json())
    .then((data) => {
      renderStores(data);
      renderControls();
    })
    .catch((err) => console.error("Error loading stores.json", err));
}

function renderStores(data) {
  data.forEach((store) => {
    const { lat, lon, source_name, color } = store;

    if (!layers[source_name]) {
      layers[source_name] = new google.maps.MVCArray();
      markers[source_name] = [];
      storeCounts[source_name] = 0;
    }

    const marker = new google.maps.Marker({
      position: { lat, lng: lon },
      map: map,
      title: source_name,
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        scale: 6,
        fillColor: color,
        fillOpacity: 1,
        strokeWeight: 0.5,
        strokeColor: "#fff",
      },
    });

    markers[source_name].push(marker);
    layers[source_name].push(marker);
    storeCounts[source_name]++;
  });

  updateStoreCounts();
}

function updateStoreCounts() {
  const panel = document.getElementById("storeCounts");
  panel.innerHTML = "<b>Store Counts</b><br>";
  for (const source in storeCounts) {
    panel.innerHTML += `${source}: ${storeCounts[source]}<br>`;
  }
}

function renderControls() {
  const controls = document.getElementById("layerControls");
  controls.innerHTML = "<b>Toggle Sources</b><br>";

  for (const source in layers) {
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = `chk-${source}`;
    checkbox.checked = true;

    checkbox.addEventListener("change", (e) => {
      toggleLayer(source, e.target.checked);
    });

    const label = document.createElement("label");
    label.htmlFor = `chk-${source}`;
    label.innerText = source;

    controls.appendChild(checkbox);
    controls.appendChild(label);
    controls.appendChild(document.createElement("br"));
  }
}

function toggleLayer(source, visible) {
  markers[source].forEach((marker) => {
    marker.setMap(visible ? map : null);
  });
}
