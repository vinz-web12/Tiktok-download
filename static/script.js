const map = L.map('map').setView([-6.2088, 106.8456], 13);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '© OpenStreetMap, CartoDB'
}).addTo(map);

let marker = L.marker([-6.2088, 106.8456]).addTo(map);
marker.bindPopup('📍 Lokasi');

const input = document.getElementById('numberInput');
const trackBtn = document.getElementById('trackBtn');
const resetBtn = document.getElementById('resetBtn');
const nameDisplay = document.getElementById('nameDisplay');
const deviceDisplay = document.getElementById('deviceDisplay');
const locationDisplay = document.getElementById('locationDisplay');
const lastSeenDisplay = document.getElementById('lastSeenDisplay');
const statusBadge = document.getElementById('statusBadge');
const sourceDisplay = document.getElementById('sourceDisplay');
const profilePhoto = document.getElementById('profilePhoto');

function updateUI(data) {
    if (data.error) { alert(data.error); return; }
    nameDisplay.textContent = data.name;
    deviceDisplay.textContent = data.device;
    locationDisplay.textContent = data.location;
    lastSeenDisplay.textContent = data.last_seen;
    sourceDisplay.textContent = data.source === 'osint' ? 'OSINT' : 'Dummy';
    statusBadge.textContent = data.status === 'online' ? '● Online' : '● Offline';
    statusBadge.className = data.status === 'online' ? 'status-badge online' : 'status-badge';
    if (data.photo) profilePhoto.src = data.photo;
    const latlng = [data.lat, data.lng];
    map.setView(latlng, 14);
    marker.setLatLng(latlng);
    marker.bindPopup(`📍 ${data.name} · ${data.location}`);
    marker.openPopup();
}

async function trackNumber(number) {
    try {
        const res = await fetch('/api/track', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ number })
        });
        const data = await res.json();
        updateUI(data);
    } catch (e) {
        alert('Server error.');
    }
}

trackBtn.addEventListener('click', () => {
    const raw = input.value.trim();
    if (!raw) return alert('Masukkan nomor!');
    trackNumber(raw);
});

resetBtn.addEventListener('click', () => {
    input.value = '+6281234567890';
    trackNumber('+6281234567890');
});

input.addEventListener('keydown', e => {
    if (e.key === 'Enter') trackBtn.click();
});

trackNumber('+6281234567890');async function trackNumber(number) {
    try {
        const res = await fetch('/api/track', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ number })
        });
        const data = await res.json();
        updateUI(data);
    } catch (e) {
        alert('Server error.');
    }
}

trackBtn.addEventListener('click', () => {
    const raw = input.value.trim();
    if (!raw) return alert('Masukkan nomor!');
    trackNumber(raw);
});

resetBtn.addEventListener('click', () => {
    input.value = '+6281234567890';
    trackNumber('+6281234567890');
});

input.addEventListener('keydown', e => {
    if (e.key === 'Enter') trackBtn.click();
});

trackNumber('+6281234567890');
