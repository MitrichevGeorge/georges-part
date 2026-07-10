ymaps.ready(initPanorama);

let panorama;
let currentLocation = null;

function initPanorama() {
    // Create panorama player
    panorama = new ymaps.panorama.Player('panorama', {
        // Initial: first attraction
        coordinates: [ATTRACTIONS[0].lat, ATTRACTIONS[0].lng],
        direction: [0, 0],
        span: [60, 60]
    });

    // Show location name
    updateLocationName(ATTRACTIONS[0]);

    // Random button
    document.getElementById('sv-random').addEventListener('click', function() {
        const randomAttr = ATTRACTIONS[Math.floor(Math.random() * ATTRACTIONS.length)];
        panorama.moveTo([randomAttr.lat, randomAttr.lng], {
            direction: [0, 0],
            span: [60, 60],
            layer: 'yandex#panorama'
        }).then(function() {
            updateLocationName(randomAttr);
        }).catch(function(e) {
            // Fallback to first
            console.warn('Panorama not available, using fallback');
        });
    });

    // Exit button (go to map) - handled by link in HTML
}

function updateLocationName(attr) {
    document.getElementById('sv-location').textContent = '📍 ' + attr.name + ', ' + attr.address;
}