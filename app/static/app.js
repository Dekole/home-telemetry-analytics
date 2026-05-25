let activeFilter = 'all';
let allEvents = [];

function fmtLocal(isoString) {
  const d = new Date(isoString);
  const pad = n => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

function renderEvents() {
  const filtered = activeFilter === 'all' ? allEvents : allEvents.filter(e => e.event_type === activeFilter);
  const list = document.getElementById('event-list');
  document.getElementById('event-count').textContent = filtered.length + ' event' + (filtered.length !== 1 ? 's' : '') + ' total';
  list.innerHTML = filtered.map(e => `
    <div class="event-row">
      <span class="event-dot dot-${e.event_type}"></span>
      <span class="event-dt">${fmtLocal(e.timestamp)}</span>
      <span class="event-badge badge-${e.event_type}">${e.event_type === 'person' ? 'Person detected' : 'Motion detected'}</span>
    </div>
  `).join('');
}

async function fetchEvents() {
  const res = await fetch('/events?limit=200');
  if (!res.ok) return;
  const data = await res.json();
  allEvents = data.events;
  renderEvents();
}

async function fetchHealth() {
  try {
    const res = await fetch('/health');
    if (!res.ok) throw new Error();
    const data = await res.json();
    const badge = document.getElementById('status-badge');
    const label = document.getElementById('status-label');
    if (data.camera_connected) {
      badge.classList.remove('offline');
      label.textContent = 'Live';
    } else {
      badge.classList.add('offline');
      label.textContent = 'Offline';
    }
    const demoBadge = document.getElementById('demo-badge');
    demoBadge.style.display = data.demo_mode ? 'inline-flex' : 'none';
  } catch {
    document.getElementById('status-badge').classList.add('offline');
    document.getElementById('status-label').textContent = 'Offline';
  }
}

document.querySelectorAll('.chip').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.chip').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.dataset.filter;
    renderEvents();
  });
});

document.getElementById('csv-btn').addEventListener('click', () => {
  const filtered = activeFilter === 'all' ? allEvents : allEvents.filter(e => e.event_type === activeFilter);
  const rows = [['event_id', 'timestamp', 'device_id', 'event_type']];
  filtered.forEach(e => rows.push([e.event_id, fmtLocal(e.timestamp), e.device_id, e.event_type]));
  const csv = rows.map(r => r.join(',')).join('\n');
  const a = document.createElement('a');
  a.href = 'data:text/csv,' + encodeURIComponent(csv);
  a.download = 'events.csv';
  a.click();
});

setInterval(() => {
  const d = new Date();
  const pad = n => String(n).padStart(2, '0');
  document.getElementById('clock').textContent = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}, 1000);

// Video player
const HLS_URL = `http://${window.location.hostname}:8888/cam/index.m3u8`;

function initPlayer() {
  const video = document.getElementById('video');
  const placeholder = document.getElementById('video-placeholder');

  video.addEventListener('playing', () => {
    video.style.display = 'block';
    placeholder.style.display = 'none';
  });

  if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = HLS_URL;
    video.play().catch(() => {});
  } else if (window.Hls && Hls.isSupported()) {
    const hls = new Hls();
    hls.loadSource(HLS_URL);
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED, () => {
      video.play().catch(() => {});
    });
  }
}

document.getElementById('mute-btn').addEventListener('click', () => {
  const video = document.getElementById('video');
  video.muted = !video.muted;
  const muted = video.muted;
  document.getElementById('mute-icon').className = muted ? 'ti ti-volume-3' : 'ti ti-volume';
  document.getElementById('mute-label').textContent = muted ? 'Muted' : 'Audio on';
  document.getElementById('mute-btn').setAttribute('aria-label', muted ? 'Unmute audio' : 'Mute audio');
});

initPlayer();
fetchHealth();
fetchEvents();
setInterval(fetchEvents, 5000);
setInterval(fetchHealth, 10000);
