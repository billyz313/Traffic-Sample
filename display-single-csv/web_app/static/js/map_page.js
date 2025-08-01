let map;
let trafficLayer; // Layer to hold traffic segments

let currentLayer = 'dark'; // Default layer
const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});
const satelliteLayer = L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
    maxZoom: 20, subdomains: ['mt0', 'mt1', 'mt2', 'mt3'], attribution: 'Google Satellite'
});
const terrainLayer = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    attribution: 'OpenTopoMap'
});
const darkmap = L.tileLayer(' https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '<a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
});
const graymap = L.esri.tiledMapLayer({
    maxZoom: 19,
    url: 'https://services.arcgisonline.com/arcgis/rest/services/Canvas/World_Light_Gray_Base/MapServer',
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
});

const layers = {
    'osm': {
        layer: osmLayer, name: 'OpenStreetMap', icon: osm_icon
    }, 'dark': {
        layer: darkmap, name: 'Dark Map', icon: dark_icon
    }, 'satellite': {
        layer: satelliteLayer, name: 'Satellite', icon: sat_icon
    }, 'terrain': {
        layer: terrainLayer, name: 'Terrain', icon: terrain_icon
    }, 'gray': {
        layer: graymap, name: 'Gray', icon: gray_icon
    }
};

// Function to get color based on speed
function getSpeedColor(speed) {
    if (speed === null || parseInt(speed) === -1) return '#808080'; // Gray for no data
    if (parseInt(speed) >= 35) return '#00ff00'; // Green for fast
    if (parseInt(speed) >= 25) return '#ffff00'; // Yellow for moderate
    if (parseInt(speed) >= 15) return '#ff8800'; // Orange for slow
    return '#ff0000'; // Red for very slow
}

// Function to get line width based on speed
function getLineWidth(speed) {
    if (speed === null || speed === -1) return 2;
    if (speed >= 35) return 3;
    if (speed >= 25) return 4;
    if (speed >= 15) return 5;
    return 6;
}
let hold_data;
// Function to load traffic segments
function loadTrafficSegments() {
    fetch('/api/traffic-segments/')
        .then(response => response.json())
        .then(data => {
            // Remove existing traffic layer if it exists
            if (trafficLayer) {
                map.removeLayer(trafficLayer);
            }
            hold_data = data;
            // Create new traffic layer
            trafficLayer = L.geoJSON(data, {
                style: function(feature) {
                    const speed = feature.properties._current_speed;
                    return {
                        color: getSpeedColor(speed),
                        weight: getLineWidth(speed),
                        opacity: 0.8,
                        lineCap: 'round',
                        lineJoin: 'round'
                    };
                },
                onEachFeature: function(feature, layer) {
                    const props = feature.properties;
                    const speed = props._current_speed;
                    const speedText = speed !== null ? `${speed} mph` : 'No data';

                    const popupContent = `
                        <div style="font-size: 12px;">
                            <strong>${props.street} ${props.direction}</strong><br>
                            From: ${props.from_street}<br>
                            To: ${props.to_street}<br>
                            Current Speed: <strong>${speedText}</strong><br>
                            Length: ${props.length} miles<br>
                            Last Updated: ${props._last_updated}
                        </div>
                    `;

                    layer.bindPopup(popupContent);

                    // Add hover effects
                    layer.on('mouseover', function(e) {
                        this.setStyle({
                            weight: this.options.weight + 2,
                            opacity: 1
                        });
                    });

                    layer.on('mouseout', function(e) {
                        this.setStyle({
                            weight: this.options.weight - 2,
                            opacity: 0.8
                        });
                    });
                }
            });

            // Add traffic layer to map
            trafficLayer.addTo(map);

            // Fit map to show Chicago area (optional)
            if (data.features.length > 0) {
                map.fitBounds(trafficLayer.getBounds());
            }
        })
        .catch(error => {
            console.error('Error loading traffic segments:', error);
        });
}

// Function to create legend
function createLegend() {
    const legend = L.control({position: 'bottomright'});

    legend.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'info legend');
        div.style.backgroundColor = 'white';
        div.style.padding = '10px';
        div.style.borderRadius = '5px';
        div.style.boxShadow = '0 0 15px rgba(0,0,0,0.2)';

        div.innerHTML = `
            <h4>Traffic Speed</h4>
            <div><span style="color: #00ff00; font-weight: bold;">■</span> 35+ mph</div>
            <div><span style="color: #ffff00; font-weight: bold;">■</span> 25-34 mph</div>
            <div><span style="color: #ff8800; font-weight: bold;">■</span> 15-24 mph</div>
            <div><span style="color: #ff0000; font-weight: bold;">■</span> < 15 mph</div>
            <div><span style="color: #808080; font-weight: bold;">■</span> No data</div>
        `;

        return div;
    };

    legend.addTo(map);
}

function updateLayerControl() {
    $('#layer-control-icon').attr('src', layers[currentLayer].icon);
    let layerList = $('#layer-list');
    layerList.empty();
    for (let key in layers) {
        let item = $('<div class="layer-item">')
            .data('layer-key', key)
            .click(function () {
                map.removeLayer(layers[currentLayer].layer);

                map.addLayer(layers[$(this).data('layer-key')].layer);
                currentLayer = $(this).data('layer-key');
                updateLayerControl();
                layerList.removeClass('show'); // Hide list after
            });

        let altText = layers[key].name || '';
        let img = $('<img src="" alt="">').attr('src', layers[key].icon).attr('alt', altText).attr('title', altText);
        item.append(img);
        layerList.append(item);
    }
}

function resizeMap() {
    $("#map").height('calc(100vh - ' + $(".navbar").outerHeight() + "px" + ')');
    map.invalidateSize();
}

function initializeMap() {
    map = L.map('map', {
        layers: [darkmap], maxBounds: [[-90, -180], // Southwest corner (global)
            [90, 180]   // Northeast corner (global)
        ]
    }).setView([40.67252546509121, -96.99518493301309], 4);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });
}

$(document).ready(function () {
    initializeMap();
    resizeMap();

    loadTrafficSegments();

    // Create legend
    createLegend();

    // Auto-refresh traffic data every 5 minutes
    setInterval(loadTrafficSegments, 5 * 60 * 1000);


    $(window).resize(resizeMap);
    updateLayerControl();

    $('#layer-control').on('mouseenter', function () {
        $('#layer-list').addClass('show');
    }).on('mouseleave', function () {
        $('#layer-list').removeClass('show');
    });

});

