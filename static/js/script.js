// Yandex Maps initialization
ymaps.ready(init);

let map, tooltip, detailPanel, currentAttractionId;

function init() {
    // Create map
    map = new ymaps.Map('map', {
        center: [55.7570, 48.7420],
        zoom: 14,
        controls: ['zoomControl', 'fullscreenControl']
    });

    // Add placemarks
    ATTRACTIONS.forEach(attraction => {
        const placemark = new ymaps.Placemark(
            [attraction.lat, attraction.lng],
            { balloonContent: '' },
            { preset: 'islands#redIcon' }
        );
        placemark.properties.set('attractionId', attraction.id);
        map.geoObjects.add(placemark);

        // Hover events
        placemark.events.add('mouseenter', function(e) {
            const id = e.get('target').properties.get('attractionId');
            showTooltip(id);
        });
        placemark.events.add('mouseleave', function() {
            hideTooltip();
        });

        // Click event – show detail panel
        placemark.events.add('click', function(e) {
            const id = e.get('target').properties.get('attractionId');
            showDetailPanel(id);
        });
    });

    // Tooltip element
    tooltip = document.getElementById('hover-tooltip');
    detailPanel = document.getElementById('detail-panel');

    // Close panel button
    document.getElementById('panel-close').addEventListener('click', closeDetailPanel);

    // Review form submit
    const form = document.getElementById('review-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const attractionId = document.getElementById('review-attraction-id').value;
            const rating = document.getElementById('review-rating').value;
            const text = document.getElementById('review-text').value;
            if (!attractionId || !rating) return;
            fetch('/api/reviews', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ attraction_id: parseInt(attractionId), rating: parseInt(rating), text: text })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('review-text').value = '';
                    document.getElementById('review-rating').value = '';
                    refreshReviews(parseInt(attractionId));
                }
            });
        });
    }
}

// ---------- Tooltip ----------
function showTooltip(id) {
    const attr = ATTRACTIONS.find(a => a.id === id);
    if (!attr) return;
    document.getElementById('tooltip-img').src = STATIC_URL + 'images/' + attr.image;
    document.getElementById('tooltip-name').textContent = attr.name;
    document.getElementById('tooltip-desc').textContent = attr.desc;
    document.getElementById('tooltip-addr').textContent = attr.address;
    tooltip.style.display = 'flex';
    // Position near cursor: we use fixed bottom-left, but we could update position
    // For simplicity we keep it at bottom-left
}

function hideTooltip() {
    tooltip.style.display = 'none';
}

// ---------- Detail Panel ----------
function showDetailPanel(id) {
    const attr = ATTRACTIONS.find(a => a.id === id);
    if (!attr) return;
    currentAttractionId = id;
    document.getElementById('panel-img').src = STATIC_URL + 'images/' + attr.image;
    document.getElementById('panel-name').textContent = attr.name;
    document.getElementById('panel-desc').textContent = attr.desc;
    document.getElementById('panel-addr').textContent = attr.address;
    document.getElementById('review-attraction-id').value = id;
    detailPanel.style.display = 'block';
    refreshReviews(id);
}

function closeDetailPanel() {
    detailPanel.style.display = 'none';
}

function refreshReviews(attractionId) {
    fetch('/api/reviews/' + attractionId)
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById('reviews-list');
            list.innerHTML = '';
            if (data.reviews.length === 0) {
                list.innerHTML = '<p class="no-reviews">No reviews yet. Be the first!</p>';
            } else {
                data.reviews.forEach(r => {
                    const div = document.createElement('div');
                    div.className = 'review-item';
                    div.innerHTML = `
                        <div class="review-user">${r.username} <span class="review-rating">${'⭐'.repeat(r.rating)}</span>
                        <span class="review-date">${new Date(r.created_at).toLocaleDateString()}</span></div>
                        <div class="review-text">${r.text || ''}</div>
                    `;
                    list.appendChild(div);
                });
            }
            document.getElementById('panel-rating').textContent = data.average.toFixed(1);
            document.getElementById('panel-review-count').textContent = data.count;
        });
}