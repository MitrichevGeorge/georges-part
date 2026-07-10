ymaps.ready(initPanorama);

let panorama;

function initPanorama() {
    panorama = new ymaps.panorama.Player('panorama', {
        coordinates: [ATTRACTIONS[0].lat, ATTRACTIONS[0].lng],
        direction: [0, 0],
        span: [60, 60]
    });

    updateLocationName(ATTRACTIONS[0]);

    document.getElementById('sv-random').addEventListener('click', function() {
        const randomAttr = ATTRACTIONS[Math.floor(Math.random() * ATTRACTIONS.length)];
        panorama.moveTo([randomAttr.lat, randomAttr.lng], {
            direction: [0, 0],
            span: [60, 60],
            layer: 'yandex#panorama'
        }).then(function() {
            updateLocationName(randomAttr);
        }).catch(function(e) {
            console.warn('Panorama not available, using fallback');
        });
    });
}

function updateLocationName(attr) {
    document.getElementById('sv-location').textContent = '📍 ' + attr.name + ', ' + attr.address;
}