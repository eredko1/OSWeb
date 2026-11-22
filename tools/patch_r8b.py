import re
p = 'index.html'
s = open(p, encoding='utf-8').read()
def sub(old, new, count=1):
    global s
    assert old in s, 'miss: ' + old[:90]
    s = s.replace(old, new, count)
def rsub(pat, fn):
    global s
    s2, n = re.subn(pat, fn, s, count=1, flags=re.S)
    assert n == 1, 'rmiss: ' + pat[:60]
    s = s2

# ---- OS.perf: real, browser-measurable metrics ----
sub("OS.sys = {", '''OS.perf = {
    hist: { load: [], fps: [], heap: [] }, users: 0, raf: 0, timer: 0, last: 0, frames: 0, acc: 0, base: Infinity, longMs: 0, lt: null, listeners: new Set(),
    start() {
        if (this.users++ > 0) return;
        this.last = performance.now();
        const loop = (t) => { const d = t - this.last; this.last = t; if (d > 4 && d < 1000) { this.frames++; this.acc += d; if (d < this.base) this.base = d; } this.raf = requestAnimationFrame(loop); };
        this.raf = requestAnimationFrame(loop);
        try { if (window.PerformanceObserver && PerformanceObserver.supportedEntryTypes?.includes('longtask')) { this.lt = new PerformanceObserver(l => l.getEntries().forEach(e => { this.longMs += e.duration; })); this.lt.observe({ type: 'longtask', buffered: false }); } } catch (_) {}
        this.timer = setInterval(() => this.sample(), 1000);
    },
    stop() { if (--this.users > 0) return; this.users = 0; cancelAnimationFrame(this.raf); clearInterval(this.timer); try { this.lt && this.lt.disconnect(); } catch (_) {} this.lt = null; this.frames = 0; this.acc = 0; },
    sample() {
        if (document.hidden) { this.frames = 0; this.acc = 0; this.longMs = 0; return; }
        const n = this.frames, avg = n ? this.acc / n : 0, base = isFinite(this.base) ? this.base : 16.7;
        let load = avg ? Math.round((1 - base / avg) * 100) : 0;
        load = Math.max(load, Math.min(100, Math.round(this.longMs / 10)));   // long tasks (>50ms) count too
        load = Math.max(0, Math.min(100, load)); this.frames = 0; this.acc = 0; this.longMs = 0;
        const h = OS.sys.heap();
        const push = (a, v) => { a.push(v); if (a.length > 60) a.shift(); };
        push(this.hist.load, load); push(this.hist.fps, n); push(this.hist.heap, h ? h.used / 1048576 : 0);
        this.latest = { load, fps: n, heapMB: h ? h.used / 1048576 : null };
        this.listeners.forEach(fn => { try { fn(this.latest); } catch (_) {} });
    },
    gpu() {
        if (this._gpu !== undefined) return this._gpu;
        try { const c = document.createElement('canvas'); const gl = c.getContext('webgl') || c.getContext('experimental-webgl'); const ext = gl && gl.getExtension('WEBGL_debug_renderer_info'); this._gpu = gl ? String(ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER)) : null; } catch (_) { this._gpu = null; }
        return this._gpu;
    },
    net() { const c = navigator.connection; return c ? { type: c.effectiveType, down: c.downlink, rtt: c.rtt } : null; }
};
function drawSeries(canvas, arr, max, color) {
    const dpr = window.devicePixelRatio || 1, w = canvas.clientWidth || 200, h = canvas.clientHeight || 40;
    if (canvas.width !== w * dpr) { canvas.width = w * dpr; canvas.height = h * dpr; }
    const ctx = canvas.getContext('2d'); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, w, h);
    ctx.strokeStyle = 'rgba(128,128,128,0.25)'; ctx.lineWidth = 0.5; for (let i = 1; i < 4; i++) { ctx.beginPath(); ctx.moveTo(0, h * i / 4); ctx.lineTo(w, h * i / 4); ctx.stroke(); }
    if (!arr.length) return;
    const m = max || Math.max(1, ...arr), step = w / 59; ctx.beginPath();
    arr.forEach((v, i) => { const x = w - (arr.length - 1 - i) * step, y = h - Math.min(1, v / m) * (h - 3) - 1.5; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); });
    ctx.strokeStyle = color; ctx.lineWidth = 1.6; ctx.lineJoin = 'round'; ctx.stroke();
    ctx.lineTo(w, h); ctx.lineTo(w - (arr.length - 1) * step, h); ctx.closePath(); ctx.fillStyle = color + '33'; ctx.fill();
}
OS.sys = {''')

# ---- menu bar item + popover ----
sub('            <button id="spotlight-menubar-button"', '            <button id="sysmon-menubar-button" class="menubar-item" role="menuitem" aria-haspopup="true" aria-label="System monitor" hidden><span id="sysmon-text">CPU —</span></button>\n            <button id="spotlight-menubar-button"')
sub("function initKeyboardShortcuts() {\n", '''// ---- Optional system monitor in the menu bar (honest, browser-measurable metrics) ----
function sysmonEnabled() { try { return localStorage.getItem('osweb_sysmon') !== '0'; } catch (_) { return true; } }
function applySysmonSetting() {
    const btn = document.getElementById('sysmon-menubar-button'); if (!btn) return;
    const on = sysmonEnabled();
    btn.hidden = !on;
    if (on && !btn._on) {
        btn._on = true; OS.perf.start();
        OS.perf.listeners.add((l) => { const t = document.getElementById('sysmon-text'); if (t) t.textContent = `CPU ${l.load}%` + (l.heapMB != null ? ` · ${Math.round(l.heapMB)} MB` : ` · ${l.fps} fps`); updateSysmonPopover(); });
        btn.addEventListener('click', (e) => { e.stopPropagation(); toggleSysmonPopover(btn); });
    } else if (!on && btn._on) { btn._on = false; OS.perf.stop(); OS.perf.listeners.clear(); document.getElementById('sysmon-pop')?.remove(); }
}
function toggleSysmonPopover(btn) {
    const ex = document.getElementById('sysmon-pop'); if (ex) { ex.remove(); return; }
    const pop = document.createElement('div'); pop.id = 'sysmon-pop'; pop.setAttribute('role', 'dialog'); pop.setAttribute('aria-label', 'System monitor');
    const r = btn.getBoundingClientRect(); pop.style.top = (r.bottom + 6) + 'px'; pop.style.right = Math.max(8, innerWidth - r.right - 40) + 'px';
    const g = OS.perf.gpu(), n = OS.perf.net();
    pop.innerHTML = `<div class="sm-sec"><div class="sm-h"><b>Tab load</b><span data-sm="load">—</span></div><canvas data-sm-c="load"></canvas><small>Estimated from how busy this page's main thread is. Browsers can't read system-wide CPU.</small></div>
        <div class="sm-sec"><div class="sm-h"><b>Memory</b><span data-sm="heap">—</span></div><canvas data-sm-c="heap"></canvas><small>${OS.sys.heap() ? 'JavaScript heap for this tab.' : 'Heap size is not exposed by this browser.'} Device memory: ${escapeHtml(OS.sys.memLine())}.</small></div>
        <div class="sm-sec"><div class="sm-h"><b>GPU</b><span data-sm="fps">—</span></div><canvas data-sm-c="fps"></canvas><small>${g ? escapeHtml(g) + '. ' : ''}Frame rate shown; GPU utilization isn't available to web pages.</small></div>
        ${n ? `<div class="sm-net">Network: ${escapeHtml(String(n.type))}, ${n.down} Mbps, ${n.rtt} ms RTT</div>` : ''}
        <button class="mac-btn-secondary sm-open">Open Activity Monitor</button>`;
    document.getElementById('macos-viewport-root').appendChild(pop);
    pop.querySelector('.sm-open').onclick = () => { pop.remove(); launchOrFocusApp('system-monitor'); };
    setTimeout(() => document.addEventListener('pointerdown', function off(e) { if (!pop.contains(e.target) && !btn.contains(e.target)) { pop.remove(); document.removeEventListener('pointerdown', off); } }), 0);
    updateSysmonPopover();
}
function updateSysmonPopover() {
    const pop = document.getElementById('sysmon-pop'); if (!pop || !OS.perf.latest) return; const l = OS.perf.latest, H = OS.perf.hist;
    const set = (k, v) => { const e = pop.querySelector(`[data-sm="${k}"]`); if (e) e.textContent = v; };
    set('load', `${l.load}%`); set('heap', l.heapMB != null ? `${l.heapMB.toFixed(1)} MB` : 'n/a'); set('fps', `${l.fps} fps`);
    drawSeries(pop.querySelector('[data-sm-c="load"]'), H.load, 100, '#30D158'); drawSeries(pop.querySelector('[data-sm-c="heap"]'), H.heap, 0, '#0A84FF'); drawSeries(pop.querySelector('[data-sm-c="fps"]'), H.fps, Math.max(60, ...H.fps), '#FF9F0A');
}

function initKeyboardShortcuts() {
    applySysmonSetting();
''')

# ---- Activity Monitor: CPU / Memory / GPU tabs with real graphs ----
sub('''<button class="fx-seg-btn am-tab" data-tab="memory" role="tab" aria-selected="false" style="width:auto;padding:0 12px">Memory</button>''', '''<button class="fx-seg-btn am-tab" data-tab="memory" role="tab" aria-selected="false" style="width:auto;padding:0 12px">Memory</button>
                    <button class="fx-seg-btn am-tab" data-tab="gpu" role="tab" aria-selected="false" style="width:auto;padding:0 12px">GPU</button>''')
sub('''            <div class="am-foot" data-role="am-foot"></div>''', '''            <div class="am-graph"><canvas data-role="am-canvas"></canvas><div class="am-foot" data-role="am-foot"></div></div>''')
sub("    const mb = n => (n / 1048576).toFixed(1) + ' MB';", "    const mb = n => (n / 1048576).toFixed(1) + ' MB';\n    const canvas = winEl.querySelector('[data-role=\"am-canvas\"]');\n    OS.perf.start();")
rsub(r"        foot\.innerHTML = tab === 'cpu'.*?;\n    \};", lambda m: '''        const L = OS.perf.latest || { load: 0, fps: 0, heapMB: null }, g = OS.perf.gpu(), net = OS.perf.net();
        foot.innerHTML = tab === 'cpu'
            ? `<div><b>Tab load (estimated)</b><span>${L.load}%</span></div><div><b>Logical processors</b><span>${OS.sys.cores() ?? 'Not exposed'}</span></div><div><b>Processes</b><span>${rows.length}</span></div><div class="am-note">System-wide and per-process CPU aren't available to web pages.</div>`
            : tab === 'memory'
            ? `<div><b>JS heap used</b><span>${h ? mb(h.used) : 'Not exposed'}</span></div><div><b>JS heap limit</b><span>${h ? mb(h.limit) : '—'}</span></div><div><b>Device memory</b><span>${OS.sys.memLine()}</span></div>`
            : `<div><b>Frame rate</b><span>${L.fps} fps</span></div><div><b>GPU</b><span>${g ? escapeHtml(g) : 'Not exposed'}</span></div>${net ? `<div><b>Network</b><span>${escapeHtml(String(net.type))} · ${net.down} Mbps</span></div>` : ''}<div class="am-note">GPU utilization isn't available to web pages.</div>`;
        const H = OS.perf.hist;
        if (tab === 'cpu') drawSeries(canvas, H.load, 100, '#30D158'); else if (tab === 'memory') drawSeries(canvas, H.heap, 0, '#0A84FF'); else drawSeries(canvas, H.fps, Math.max(60, ...H.fps), '#FF9F0A');
    };''')
sub("    windowData.abortController.signal.addEventListener('abort', () => clearInterval(timer));\n    OS.bus.addEventListener('proc:change', renderTable", "    windowData.abortController.signal.addEventListener('abort', () => { clearInterval(timer); OS.perf.stop(); });\n    OS.bus.addEventListener('proc:change', renderTable")
sub("    const timer = setInterval(() => { if (!document.hidden) renderTable(); }, 2000);", "    const timer = setInterval(() => { if (!document.hidden) renderTable(); }, 1000);")

# ---- Settings: switch for the menu-bar monitor ----
sub("group(row('Show Widgets on Desktop', sw('sw-widgets', widgetsOn)));", "group(row('Show Widgets on Desktop', sw('sw-widgets', widgetsOn)), row('System monitor in menu bar', sw('sw-sysmon', sysmonEnabled()), 'CPU load, memory and frame rate for this tab'));")
sub("            bindSwitch('sw-widgets', () => toggleDesktopWidgets());", "            bindSwitch('sw-widgets', () => toggleDesktopWidgets());\n            bindSwitch('sw-sysmon', (on) => { try { localStorage.setItem('osweb_sysmon', on ? '1' : '0'); } catch (_) {} applySysmonSetting(); });")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
