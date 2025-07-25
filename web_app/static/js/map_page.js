let map;

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

    $(window).resize(resizeMap);
    updateLayerControl();

    $('#layer-control').on('mouseenter', function () {
        $('#layer-list').addClass('show');
    }).on('mouseleave', function () {
        $('#layer-list').removeClass('show');
    });

});

