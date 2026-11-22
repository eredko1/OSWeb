import re
p = 'index.html'
s = open(p, encoding='utf-8').read()
def sub(old, new, count=1):
    global s
    assert old in s, 'miss: ' + old[:80]
    s = s.replace(old, new, count)

# --- viewport: allow pinch zoom (a11y); 16px inputs already prevent focus-zoom ---
sub('viewport-fit=cover, user-scalable=no">', 'viewport-fit=cover">')

# --- Alt+Space is a NBSP on macOS, not Spotlight ---
sub("if ((mod && e.code === 'Space') || (e.altKey && !e.ctrlKey && !e.metaKey && e.code === 'Space')) {", "if (mod && e.code === 'Space') {")

# --- drag: pointer capture + rAF + transform; restore previous size ---
sub('''        // If window was maximized, un-maximize proportionally under cursor
        if (winData && winData.isMaximized) {
            const areaW = area.clientWidth;
            const restoreW = Math.min(820, areaW - 40);
            winEl.style.width = `${restoreW}px`;
            winEl.style.height = `${Math.min(540, area.clientHeight - 40)}px`;''', '''        // If window was maximized, un-maximize proportionally under cursor, back to its previous size
        if (winData && winData.isMaximized) {
            const areaW = area.clientWidth;
            const pre = winData.preTileRect;
            const restoreW = Math.min(pre ? parseFloat(pre.width) || 820 : 820, areaW - 40);
            winEl.style.width = `${restoreW}px`;
            winEl.style.height = `${Math.min(pre ? parseFloat(pre.height) || 540 : 540, area.clientHeight - 40)}px`;
            winData.preTileRect = null;''')
sub('''        const startLeft = winEl.offsetLeft;
        const startTop = winEl.offsetTop;
        document.body.classList.add('wm-dragging');

        const onMove = (ev) => {''', '''        const startLeft = winEl.offsetLeft;
        const startTop = winEl.offsetTop;
        document.body.classList.add('wm-dragging');
        try { titleBar.setPointerCapture(e.pointerId); } catch (_) {}
        let nextL = startLeft, nextT = startTop, rafId = 0;
        const paint = () => { rafId = 0; winEl.style.transform = `translate3d(${nextL - startLeft}px, ${nextT - startTop}px, 0)`; };

        const onMove = (ev) => {''')
sub('''            winEl.style.left = `${Math.round(newLeft)}px`;
            winEl.style.top = `${Math.round(newTop)}px`;

            // Detect Edge Snap Zones
            const relX = pt.x;
            const relY = pt.y - 28; // below 28px top menu bar''', '''            nextL = Math.round(newLeft); nextT = Math.round(newTop);
            if (!rafId) rafId = requestAnimationFrame(paint);

            // Detect Edge Snap Zones
            const relX = pt.x;
            const relY = pt.y - 24; // below the 24px menu bar''')
sub('''        const onUp = () => {
            document.body.classList.remove('wm-dragging');
            window.removeEventListener('pointermove', onMove);
            window.removeEventListener('pointerup', onUp);
            window.removeEventListener('pointercancel', onUp);
            if (snapPreview) snapPreview.style.display = 'none';''', '''        let ended = false;
        const onUp = () => {
            if (ended) return; ended = true;
            if (rafId) cancelAnimationFrame(rafId);
            winEl.style.transform = '';
            winEl.style.left = `${nextL}px`; winEl.style.top = `${nextT}px`;
            document.body.classList.remove('wm-dragging');
            window.removeEventListener('pointermove', onMove);
            window.removeEventListener('pointerup', onUp);
            window.removeEventListener('pointercancel', onUp);
            titleBar.removeEventListener('lostpointercapture', onUp);
            if (snapPreview) snapPreview.style.display = 'none';''')
sub('''        window.addEventListener('pointermove', onMove);
        window.addEventListener('pointerup', onUp);
        window.addEventListener('pointercancel', onUp);
    });''', '''        window.addEventListener('pointermove', onMove);
        window.addEventListener('pointerup', onUp);
        window.addEventListener('pointercancel', onUp);
        titleBar.addEventListener('lostpointercapture', onUp);
    });''')
sub("function scheduleSessionSave() {\n", "function scheduleSessionSave() {\n    if (document.body.classList.contains('wm-dragging')) return;\n")

# --- hardened, clamped session restore ---
i = s.index('function restoreSession() {'); j = s.index('function initSessionPersistence()')
s = s[:i] + '''function restoreSession() {
    let sess = null;
    try { sess = OS.store.get('session'); } catch (_) {}
    if (!sess || sess.v !== 1 || !Array.isArray(sess.windows) || !sess.windows.length) return false;
    const b = OS.viewport.getDesktopBounds();
    const num = (v, d) => { const n = parseFloat(v); return Number.isFinite(n) ? n : d; };
    let made = 0;
    sess.windows.slice(0, 40).forEach(sw => {
        try {
            if (!sw || !appConfig[sw.appId]) return;
            currentVirtualDesktop = (sw.space && virtualDesktops.includes(sw.space)) ? sw.space : virtualDesktops[0];
            const id = createWindow(sw.appId, Object.assign({}, (sw.opts && typeof sw.opts === 'object') ? sw.opts : {}, { forceNew: true }));
            const w = id && openWindows[id]; if (!w) return;
            const r = sw.rect || {};
            const width = Math.max(300, Math.min(num(r.width, 820), b.width - 16));
            const height = Math.max(200, Math.min(num(r.height, 540), b.height - 40));
            const left = Math.max(0, Math.min(num(r.left, 80), b.width - Math.min(width, 140)));
            const top = Math.max(0, Math.min(num(r.top, 40), b.height - 60));
            Object.assign(w.element.style, { left: left + 'px', top: top + 'px', width: width + 'px', height: height + 'px' });
            if (sw.max) tileWindow(id, 'maximize');
            if (sw.min) minimizeWindow(id);
            made++;
        } catch (err) { console.warn('restore skipped a window', err); }
    });
    try {
        if (sess.space && virtualDesktops.includes(sess.space)) switchVirtualDesktop(sess.space);
        const front = Object.values(openWindows).filter(w => !w.isMinimized && w.virtualDesktop === currentVirtualDesktop && (!sess.active || w.appId === sess.active));
        if (front.length) focusWindow(front[front.length - 1].id);
    } catch (_) {}
    return made > 0;
}
''' + s[j:]
sub("    const sess = OS.store.get('session');\n", "") if "    const sess = OS.store.get('session');\n" in s else None

# --- Dock accessibility: toolbar of labelled buttons with roving focus ---
sub("function fitDockToViewport() {", '''function decorateDock(dock) {
    dock.setAttribute('role', 'toolbar'); dock.setAttribute('aria-label', 'Dock');
    dock.querySelectorAll('.dock-icon').forEach((ic, i) => {
        ic.setAttribute('role', 'button'); ic.tabIndex = i === 0 ? 0 : -1;
        const name = ic.querySelector('.dock-tooltip')?.textContent || ic.getAttribute('aria-label') || 'Dock item';
        ic.setAttribute('aria-label', ic.querySelector('.dock-running-dot') ? `${name}, running` : name);
    });
    if (!dock._kb) {
        dock._kb = true;
        dock.addEventListener('keydown', (e) => {
            const items = [...dock.querySelectorAll('.dock-icon')]; const i = items.indexOf(document.activeElement); if (i < 0) return;
            if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); const n = items[(i + (e.key === 'ArrowRight' ? 1 : -1) + items.length) % items.length]; items.forEach(x => x.tabIndex = -1); n.tabIndex = 0; n.focus(); }
            else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); document.activeElement.click(); }
        });
    }
}

function fitDockToViewport() {''')
sub("    if (isPhone) { fitDockToViewport(); return; }", "    if (isPhone) { decorateDock(dock); fitDockToViewport(); return; }")
sub("    dock.appendChild(trash);\n\n    fitDockToViewport();", "    dock.appendChild(trash);\n\n    decorateDock(dock);\n    fitDockToViewport();")

# --- a11y: live region, combobox, unnamed buttons ---
sub('<div id="temp-message-container" class="temp-message"></div>', '<div id="temp-message-container" class="temp-message" role="status" aria-live="polite"></div>')
sub('<input id="spotlight-input" type="text" placeholder="Spotlight Search" aria-label="Spotlight Search"', '<input id="spotlight-input" type="text" role="combobox" aria-expanded="true" aria-controls="spotlight-results" aria-autocomplete="list" placeholder="Spotlight Search" aria-label="Spotlight Search"')
sub("function initKeyboardShortcuts() {", '''// Give every icon-only control an accessible name (title / data-role fallback).
function labelButtons(root = document) {
    root.querySelectorAll('button:not([aria-label]), [role="button"]:not([aria-label])').forEach(b => {
        if ((b.textContent || '').trim()) return;
        const n = b.getAttribute('title') || (b.dataset && (b.dataset.role || b.dataset.tile)) || '';
        if (n) b.setAttribute('aria-label', n.replace(/[-_]/g, ' '));
    });
}
function initKeyboardShortcuts() {''')
sub("    initSessionPersistence();\n", "    initSessionPersistence();\n    labelButtons();\n    new MutationObserver(m => { if (m.some(r => r.addedNodes.length)) labelButtons(); }).observe(document.getElementById('macos-viewport-root'), { childList: true, subtree: true });\n")

# --- text selection in content views ---
sub("        /* ---- Accessibility ---- */", '''        /* Content is selectable/copyable like on a real Mac; only chrome stays unselectable */
        .window-content, .window-content *:not(button):not(.finder-item):not(.fx-side-item):not(.ios-app) { -webkit-user-select: text; user-select: text; }
        body.wm-dragging .window { transition: none !important; will-change: transform; }

        /* ---- Accessibility ---- */''')
open(p, 'w', encoding='utf-8').write(s)

# --- service worker: network-first navigations, stale-while-revalidate assets ---
open('sw.js', 'w').write('''// OSWeb service worker. Navigations: network-first (fresh code when online), cache fallback offline.
// Assets: stale-while-revalidate. Bump VERSION to drop old caches.
const VERSION = 'osweb-v3';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'vendor/tailwind.css', 'vendor/fa/css/all.min.css',
  'vendor/fa/webfonts/fa-solid-900.woff2', 'vendor/fa/webfonts/fa-regular-400.woff2', 'vendor/fa/webfonts/fa-brands-400.woff2',
  'vendor/wallpapers/sequoia.svg', 'vendor/wallpapers/sequoia-dark.svg', 'vendor/wallpapers/sonoma.svg', 'vendor/wallpapers/ventura.svg',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  const put = res => { if (res && res.ok) { const copy = res.clone(); caches.open(VERSION).then(c => c.put(req, copy)); } return res; };
  if (req.mode === 'navigate') { e.respondWith(fetch(req).then(put).catch(() => caches.match('index.html'))); return; }
  e.respondWith(caches.match(req).then(hit => { const net = fetch(req).then(put).catch(() => hit); return hit || net; }));
});
''')
print('ok')
