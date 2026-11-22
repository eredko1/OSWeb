import re
p = 'index.html'
s = open(p, encoding='utf-8').read()
def rsub(pat, fn):
    global s
    s2, n = re.subn(pat, fn, s, count=1, flags=re.S)
    assert n == 1, 'rmiss: ' + pat[:60]
    s = s2

new_weather = r'''/* ---- Weather: live data from Open-Meteo (no key). Location is only requested when the user asks. ---- */
const WX_CODES = { 0: ['Clear', 'sun'], 1: ['Mostly Clear', 'sun'], 2: ['Partly Cloudy', 'partly'], 3: ['Cloudy', 'cloud'], 45: ['Fog', 'fog'], 48: ['Fog', 'fog'], 51: ['Drizzle', 'rain'], 53: ['Drizzle', 'rain'], 55: ['Drizzle', 'rain'],
    61: ['Rain', 'rain'], 63: ['Rain', 'rain'], 65: ['Heavy Rain', 'rain'], 71: ['Snow', 'snow'], 73: ['Snow', 'snow'], 75: ['Heavy Snow', 'snow'], 80: ['Showers', 'rain'], 81: ['Showers', 'rain'], 82: ['Heavy Showers', 'rain'], 95: ['Thunderstorm', 'bolt'], 96: ['Thunderstorm', 'bolt'], 99: ['Thunderstorm', 'bolt'] };
function wxIcon(kind, size = 28) {
    const sun = '<circle cx="16" cy="16" r="6" fill="#FFD60A"/><g stroke="#FFD60A" stroke-width="2" stroke-linecap="round"><path d="M16 4v3M16 25v3M4 16h3M25 16h3M7.5 7.5l2 2M22.5 22.5l2 2M24.5 7.5l-2 2M9.5 22.5l-2 2"/></g>';
    const cloud = '<path d="M10 24h13a5 5 0 0 0 .6-9.96A7.5 7.5 0 0 0 9.2 12.6 5.7 5.7 0 0 0 10 24z" fill="#F2F4F8"/>';
    const g = { sun, partly: '<g transform="translate(-3 -4) scale(.8)">' + sun + '</g><g transform="translate(2 1)">' + cloud + '</g>', cloud,
        fog: cloud + '<path d="M7 27h18M10 30h12" stroke="#cfd6e2" stroke-width="2" stroke-linecap="round"/>',
        rain: cloud + '<path d="M11 26l-1.5 4M16 26l-1.5 4M21 26l-1.5 4" stroke="#5AC8FA" stroke-width="2" stroke-linecap="round"/>',
        snow: cloud + '<g fill="#fff"><circle cx="11" cy="28" r="1.5"/><circle cx="16" cy="29" r="1.5"/><circle cx="21" cy="28" r="1.5"/></g>',
        bolt: cloud + '<path d="M17 24l-4 6h3l-1 4 5-7h-3z" fill="#FFD60A"/>' };
    return `<svg viewBox="0 0 32 34" width="${size}" height="${size}" aria-hidden="true">${g[kind] || g.cloud}</svg>`;
}
const wxUnitF = () => /^en-(US|LR)|^my/.test(navigator.language || '');
const wxState = { locs: [], active: 0, loaded: false };
function wxLoad() { if (wxState.loaded) return; wxState.loaded = true; const v = OS.store.get('weather'); if (v && Array.isArray(v.locs)) { wxState.locs = v.locs; wxState.active = Math.min(v.active || 0, Math.max(0, v.locs.length - 1)); } }
function wxSave() { OS.store.set('weather', { locs: wxState.locs, active: wxState.active }); }
async function wxFetch(loc) {
    const u = wxUnitF() ? '&temperature_unit=fahrenheit&wind_speed_unit=mph' : '';
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${loc.lat}&longitude=${loc.lon}&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,is_day&hourly=temperature_2m,weather_code,is_day&daily=weather_code,temperature_2m_max,temperature_2m_min&forecast_days=7&timezone=auto${u}`;
    const r = await fetch(url); if (!r.ok) throw new Error('weather ' + r.status);
    loc.data = await r.json(); loc.fetchedAt = Date.now(); wxSave(); return loc;
}
async function wxGeocode(q) {
    const r = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(q)}&count=5&language=en`); if (!r.ok) throw new Error('geocode');
    return ((await r.json()).results || []).map(x => ({ name: [x.name, x.admin1].filter(Boolean).join(', '), lat: x.latitude, lon: x.longitude }));
}

function renderWeatherContent() {
    return `
        <div class="wx-root" data-view="main">
            <aside class="wx-side" aria-label="Locations">
                <div class="wx-search">${sf('magnifyingglass', 12)}<input data-role="wx-search" type="search" placeholder="Search for a city" aria-label="Search for a city"/></div>
                <div data-role="wx-results" class="wx-results"></div>
                <div data-role="weather-cities" class="wx-locs"></div>
                <button data-role="wx-locate" class="mac-btn-secondary wx-locate">Use My Location</button>
            </aside>
            <section data-role="weather-main" class="wx-main"></section>
        </div>`;
}

function initWeatherApp(winEl, windowData) {
    wxLoad();
    const citiesEl = winEl.querySelector('[data-role="weather-cities"]');
    const mainEl = winEl.querySelector('[data-role="weather-main"]');
    const resEl = winEl.querySelector('[data-role="wx-results"]');
    const searchEl = winEl.querySelector('[data-role="wx-search"]');
    const deg = v => `${Math.round(v)}°`;

    const render = () => {
        citiesEl.innerHTML = wxState.locs.map((l, i) => {
            const c = l.data && l.data.current; const code = c ? (WX_CODES[c.weather_code] || ['', 'cloud']) : null;
            return `<button data-i="${i}" class="wx-loc${i === wxState.active ? ' sel' : ''}"><span><b>${escapeHtml(l.name)}</b><small>${code ? code[0] : 'No data'}</small></span><span class="wx-loc-t">${c ? deg(c.temperature_2m) : '—'}</span></button>`;
        }).join('');
        citiesEl.querySelectorAll('[data-i]').forEach(b => b.onclick = () => { wxState.active = Number(b.dataset.i); wxSave(); render(); updateSidebarWeather(); winEl.querySelector('.wx-root').dataset.view = 'main'; });
        const l = wxState.locs[wxState.active];
        if (!l) { mainEl.className = 'wx-main wx-empty'; mainEl.innerHTML = `<div class="wx-empty-box"><div class="wx-empty-t">Weather</div><p>Search for a city, or allow location access to see the forecast where you are.</p></div>`; return; }
        const d = l.data;
        if (!d) { mainEl.className = 'wx-main wx-empty'; mainEl.innerHTML = `<div class="wx-empty-box"><div class="wx-empty-t">${escapeHtml(l.name)}</div><p>${navigator.onLine ? 'Loading forecast…' : 'Weather needs an internet connection.'}</p></div>`; return; }
        const c = d.current, info = WX_CODES[c.weather_code] || ['—', 'cloud'], night = !c.is_day;
        mainEl.className = 'wx-main ' + (night ? 'night' : (info[1] === 'rain' || info[1] === 'bolt' ? 'rainy' : (info[1] === 'cloud' || info[1] === 'fog' ? 'cloudy' : 'clear')));
        const now = new Date(c.time); const hrs = []; for (let i = 0; i < d.hourly.time.length && hrs.length < 24; i++) { if (new Date(d.hourly.time[i]) >= new Date(now.getTime() - 3600e3)) hrs.push(i); }
        const lo = Math.min(...d.daily.temperature_2m_min), hi = Math.max(...d.daily.temperature_2m_max);
        mainEl.innerHTML = `
            <div class="wx-hero"><div class="wx-city">${escapeHtml(l.name)}</div><div class="wx-temp">${deg(c.temperature_2m)}</div><div class="wx-cond">${info[0]}</div><div class="wx-hl">H:${deg(d.daily.temperature_2m_max[0])}  L:${deg(d.daily.temperature_2m_min[0])}</div></div>
            <div class="wx-card"><div class="wx-card-h">Hourly Forecast</div><div class="wx-hours">${hrs.map((i, k) => `<div class="wx-hour"><span>${k === 0 ? 'Now' : new Date(d.hourly.time[i]).toLocaleTimeString('en-US', { hour: 'numeric' })}</span>${wxIcon((WX_CODES[d.hourly.weather_code[i]] || [0, 'cloud'])[1], 26)}<b>${deg(d.hourly.temperature_2m[i])}</b></div>`).join('')}</div></div>
            <div class="wx-card"><div class="wx-card-h">7-Day Forecast</div>${d.daily.time.map((t, i) => { const a = d.daily.temperature_2m_min[i], b = d.daily.temperature_2m_max[i]; return `<div class="wx-day"><span class="wx-dn">${i === 0 ? 'Today' : new Date(t + 'T12:00').toLocaleDateString('en-US', { weekday: 'short' })}</span>${wxIcon((WX_CODES[d.daily.weather_code[i]] || [0, 'cloud'])[1], 24)}<span class="wx-lo">${deg(a)}</span><span class="wx-bar"><i style="left:${((a - lo) / (hi - lo || 1)) * 100}%;width:${Math.max(6, ((b - a) / (hi - lo || 1)) * 100)}%"></i></span><span class="wx-hi">${deg(b)}</span></div>`; }).join('')}</div>
            <div class="wx-tiles"><div class="wx-card"><div class="wx-card-h">Feels Like</div><div class="wx-big">${deg(c.apparent_temperature)}</div></div><div class="wx-card"><div class="wx-card-h">Humidity</div><div class="wx-big">${Math.round(c.relative_humidity_2m)}%</div></div><div class="wx-card"><div class="wx-card-h">Wind</div><div class="wx-big">${Math.round(c.wind_speed_10m)} <small>${wxUnitF() ? 'mph' : 'km/h'}</small></div></div></div>
            <div class="wx-attr">Weather data by Open-Meteo.com · updated ${new Date(l.fetchedAt).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}</div>`;
    };
    const addLocation = async (loc) => {
        const existing = wxState.locs.findIndex(x => Math.abs(x.lat - loc.lat) < 0.01 && Math.abs(x.lon - loc.lon) < 0.01);
        if (existing >= 0) wxState.active = existing; else { wxState.locs.push(loc); wxState.active = wxState.locs.length - 1; }
        wxSave(); render();
        try { await wxFetch(wxState.locs[wxState.active]); } catch (_) { showTemporaryMessage('Could not load weather. Check your connection.', 2200); }
        render(); updateSidebarWeather();
    };
    let t = null;
    searchEl.oninput = () => {
        clearTimeout(t); const q = searchEl.value.trim(); if (q.length < 2) { resEl.innerHTML = ''; return; }
        t = setTimeout(async () => { try { const r = await wxGeocode(q); resEl.innerHTML = r.map((x, i) => `<button data-r="${i}" class="wx-res">${escapeHtml(x.name)}</button>`).join('') || '<div class="wx-none">No results</div>'; resEl.querySelectorAll('[data-r]').forEach(b => b.onclick = () => { addLocation(r[Number(b.dataset.r)]); resEl.innerHTML = ''; searchEl.value = ''; }); } catch (_) { resEl.innerHTML = '<div class="wx-none">Search needs a connection</div>'; } }, 300);
    };
    winEl.querySelector('[data-role="wx-locate"]').onclick = () => {
        if (!navigator.geolocation) { showTemporaryMessage('Location is not available in this browser.', 2000); return; }
        navigator.geolocation.getCurrentPosition(pos => addLocation({ name: 'My Location', lat: +pos.coords.latitude.toFixed(3), lon: +pos.coords.longitude.toFixed(3) }), () => showTemporaryMessage('Location permission was not granted.', 2200), { timeout: 10000, maximumAge: 600000 });
    };
    render();
    const stale = wxState.locs[wxState.active];
    if (stale && navigator.onLine && (!stale.fetchedAt || Date.now() - stale.fetchedAt > 600000)) wxFetch(stale).then(() => { render(); updateSidebarWeather(); }).catch(() => {});
}

function updateSidebarWeather() {
    wxLoad();
    const l = wxState.locs[wxState.active], c = l && l.data && l.data.current;
    const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
    set('sidebar-weather-city', l ? l.name : 'Weather');
    set('sidebar-weather-temp', c ? `${Math.round(c.temperature_2m)}°${wxUnitF() ? 'F' : 'C'}` : '—');
    set('sidebar-weather-condition', c ? (WX_CODES[c.weather_code] || ['—'])[0] : 'Open Weather to add a location');
    set('widget-weather-city', l ? l.name : 'Weather'); set('widget-weather-temp', c ? `${Math.round(c.temperature_2m)}°` : '—'); set('widget-weather-cond', c ? (WX_CODES[c.weather_code] || ['—'])[0] : '');
    set('widget-weather-range', l && l.data ? `H:${Math.round(l.data.daily.temperature_2m_max[0])}°  L:${Math.round(l.data.daily.temperature_2m_min[0])}°` : '');
}

// --- 8.14 Activity Monitor'''
rsub(r"function renderWeatherContent\(\) \{.*?\n// --- 8\.14 Activity Monitor", lambda m: new_weather)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
