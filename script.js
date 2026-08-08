let BACKEND_URL = '';
let currentState = {};

// ==================== Connection ====================
function connectBackend() {
    const url = document.getElementById('backendUrl').value.trim();
    if (!url) {
        alert('Masukkan URL backend (misal: https://abc123.ngrok.io)');
        return;
    }
    BACKEND_URL = url.replace(/\/+$/, '');
    document.getElementById('connectionStatus').textContent = 'Menghubungkan...';
    document.getElementById('connectBtn').textContent = '⏳';
    document.getElementById('connectBtn').disabled = true;

    fetch(`${BACKEND_URL}/api/state`)
        .then(r => {
            if (!r.ok) throw new Error('Backend tidak merespon');
            return r.json();
        })
        .then(state => {
            currentState = state;
            updateUI(state);
            document.getElementById('connectionStatus').textContent = '✅ Terhubung';
            document.getElementById('statusBadge').innerHTML = '<span class="dot online"></span> Online';
            document.getElementById('connectBtn').textContent = '✔️';
            document.getElementById('connectBtn').disabled = false;
            // Simpan ke localStorage
            localStorage.setItem('backendUrl', BACKEND_URL);
        })
        .catch(err => {
            document.getElementById('connectionStatus').textContent = '❌ Gagal: ' + err.message;
            document.getElementById('connectBtn').textContent = 'Connect';
            document.getElementById('connectBtn').disabled = false;
        });
}

// Auto-load dari localStorage
window.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('backendUrl');
    if (saved) {
        document.getElementById('backendUrl').value = saved;
        connectBackend();
    }
});

// ==================== API Calls ====================
function toggleFeature(feature) {
    if (!BACKEND_URL) return alert('Konek dulu ke backend!');
    fetch(`${BACKEND_URL}/api/toggle/${feature}`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'ok') {
                currentState[feature] = data[feature];
                updateUI(currentState);
            }
        })
        .catch(err => console.error('Toggle error:', err));
}

function setParam(key, value) {
    if (!BACKEND_URL) return;
    // Konversi tipe
    if (value === 'true') value = true;
    if (value === 'false') value = false;
    if (!isNaN(value) && value !== '') value = parseFloat(value);

    fetch(`${BACKEND_URL}/api/set`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key, value })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'ok') {
            currentState[key] = value;
            // Update display value
            const valEl = document.getElementById(key + 'Val');
            if (valEl) valEl.textContent = value;
        }
    })
    .catch(console.error);
}

function refreshState() {
    if (!BACKEND_URL) return;
    fetch(`${BACKEND_URL}/api/state`)
        .then(r => r.json())
        .then(state => {
            currentState = state;
            updateUI(state);
        })
        .catch(console.error);
}

function captureScreenshot() {
    if (!BACKEND_URL) return alert('Konek dulu!');
    const container = document.getElementById('screenshotContainer');
    const img = document.getElementById('screenshotImg');
    fetch(`${BACKEND_URL}/api/screenshot`)
        .then(r => r.json())
        .then(data => {
            if (data.image) {
                img.src = 'data:image/jpeg;base64,' + data.image;
                container.style.display = 'block';
            }
        })
        .catch(err => console.error('Screenshot error:', err));
}

// ==================== UI Update ====================
function updateUI(state) {
    // Toggle
    document.getElementById('aimbotToggle').checked = state.aimbot || false;
    document.getElementById('espToggle').checked = state.esp || false;
    document.getElementById('triggerbotToggle').checked = state.triggerbot || false;
    document.getElementById('noRecoilToggle').checked = state.no_recoil || false;
    document.getElementById('speedToggle').checked = state.speed_hack || false;

    // Slider
    document.getElementById('aimFov').value = state.aim_fov || 15;
    document.getElementById('aimFovVal').textContent = state.aim_fov || 15;
    document.getElementById('aimSmooth').value = state.aim_smooth || 5;
    document.getElementById('aimSmoothVal').textContent = state.aim_smooth || 5;
    document.getElementById('speedMultiplier').value = state.speed_multiplier || 1.5;
    document.getElementById('speedMultiplierVal').textContent = state.speed_multiplier || 1.5;

    // Select
    document.getElementById('aimTarget').value = state.aim_target || 'head';

    // Checkbox ESP
    document.getElementById('espBox').checked = state.esp_box || false;
    document.getElementById('espHealth').checked = state.esp_health || false;
    document.getElementById('espDistance').checked = state.esp_distance || false;
    document.getElementById('espSnaplines').checked = state.esp_snaplines || false;

    // Client info
    fetch(`${BACKEND_URL}/api/clients`)
        .then(r => r.json())
        .then(data => {
            document.getElementById('clientInfo').textContent = 'Client: ' + (data.count || 0);
        })
        .catch(() => {});
}

// Polling state tiap 3 detik
setInterval(() => {
    if (BACKEND_URL) refreshState();
}, 3000);