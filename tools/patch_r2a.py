import re
p = 'index.html'
s = open(p, encoding='utf-8').read()
def sub(old, new, count=1):
    global s
    assert old in s, 'miss: ' + old[:80]
    s = s.replace(old, new, count)

# ---------- head: PWA ----------
sub('<meta name="theme-color" content="#1c2d4f">', '<meta name="theme-color" content="#1c2d4f">\n    <link rel="manifest" href="manifest.webmanifest">\n    <link rel="apple-touch-icon" href="icons/apple-touch-icon.png">\n    <link rel="icon" type="image/png" href="icons/icon-192.png">')

# ---------- viewport engine: no more global scale(); real device classes ----------
sub(r'''            let shouldFit = (this.mode === 'fit') || (this.mode === 'auto' && vw < this.targetMinWidth);
            if (shouldFit && vw < this.targetMinWidth) {''', r'''            // Device class: phone gets the iOS-style shell; tablets/desktops get the desktop shell at 1:1 (never scaled).
            const coarse = window.matchMedia && matchMedia('(pointer: coarse)').matches;
            const phone = vw < 600 || (coarse && Math.min(vw, vh) < 500);
            const tablet = !phone && coarse;
            const wasPhone = document.body.classList.contains('device-phone');
            document.body.classList.toggle('device-phone', phone);
            document.body.classList.toggle('device-tablet', tablet);
            OS.device = { phone, tablet, desktop: !phone && !tablet };
            if (phone !== wasPhone && typeof onDeviceClassChange === 'function') onDeviceClassChange(phone);
            let shouldFit = false;
            if (shouldFit && vw < this.targetMinWidth) {''')
sub('''                root.style.width = '100vw';
                root.style.height = '100vh';
                root.style.transform = 'none';''', '''                root.style.width = '100vw';
                root.style.height = '100dvh';
                root.style.transform = 'none';''')

# ---------- Dock: phone shows 4 pins only ----------
sub('''    // 1. Pinned Apps
    pinnedDockApps.forEach(appId => {
        const el = createDockItem(appId);
        if (el) dock.appendChild(el);
    });
''', '''    // 1. Pinned Apps
    const isPhone = document.body.classList.contains('device-phone');
    (isPhone ? phoneDockApps : pinnedDockApps).forEach(appId => {
        const el = createDockItem(appId);
        if (el) dock.appendChild(el);
    });
    if (isPhone) { fitDockToViewport(); return; }
''')
sub("const pinnedDockApps = [", "const phoneDockApps = ['web-browser', 'ai-assistant', 'mail-client', 'notepad'];\nconst pinnedDockApps = [")

# ---------- phone: no dragging ----------
sub("        if (e.button !== 0 || e.target.closest('.traffic-lights')) return;", "        if (document.body.classList.contains('device-phone')) return;\n        if (e.button !== 0 || e.target.closest('.traffic-lights')) return;")

# ---------- iOS shell DOM ----------
sub('''    <!-- Main macOS Sequoia Desktop Canvas -->''', '''    <!-- iPhone shell (visible only in body.device-phone) -->
    <div id="ios-status" aria-hidden="true">
        <span id="ios-time">9:41</span>
        <span class="ios-right">
            <svg viewBox="0 0 20 14" width="19" height="13" fill="currentColor"><rect x="0" y="9" width="3.2" height="4.5" rx=".8"/><rect x="5.2" y="6.2" width="3.2" height="7.3" rx=".8"/><rect x="10.4" y="3.2" width="3.2" height="10.3" rx=".8"/><rect x="15.6" y="0" width="3.2" height="13.5" rx=".8"/></svg>
            <svg viewBox="0 0 20 14" width="18" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2 5a11 11 0 0 1 16 0"/><path d="M5 8.2a7 7 0 0 1 10 0"/><circle cx="10" cy="11.6" r="1.1" fill="currentColor" stroke="none"/></svg>
            <svg viewBox="0 0 28 14" width="27" height="13" fill="currentColor"><rect x=".5" y=".5" width="23" height="12" rx="3.4" fill="none" stroke="currentColor" opacity=".45"/><rect x="2" y="2" width="20" height="9" rx="2.2"/><path d="M25 4.6v4.8c1-.3 1.7-1.3 1.7-2.4S26 4.9 25 4.6z" opacity=".5"/></svg>
        </span>
    </div>
    <div id="ios-home" role="region" aria-label="Home Screen" hidden><div id="ios-grid"></div></div>
    <button id="ios-indicator" aria-label="Home" hidden></button>

    <!-- Main macOS Sequoia Desktop Canvas -->''')

# ---------- device-class handler + iOS home ----------
sub('''// Parabolic Magnifying macOS Sequoia Dock''', '''/* ============================================================================
 * iPhone shell: iOS home screen + full-screen apps. Same apps/state as the desktop, different chrome.
 * ============================================================================ */
const phoneHomeApps = ['calendar-app', 'image-viewer', 'mail-client', 'notepad', 'reminders', 'weather-app', 'music-player', 'web-browser', 'ai-assistant', 'file-explorer', 'terminal', 'calculator', 'clicker-game', 'settings', 'pdf-viewer'];
function renderIOSHome() {
    const grid = document.getElementById('ios-grid');
    if (!grid) return;
    const ids = phoneHomeApps.filter(id => appConfig[id]);
    Object.keys(appConfig).filter(id => id.startsWith('forged-') && !ids.includes(id)).forEach(id => ids.push(id));
    grid.innerHTML = ids.map(id => `<button class="ios-app" data-app="${id}" aria-label="${escapeHtml(appConfig[id].title)}"><span class="ios-app-icon">${getAppIconSVG(id)}</span><span class="ios-app-name">${escapeHtml(appConfig[id].title)}</span></button>`).join('');
    grid.querySelectorAll('.ios-app').forEach(b => b.addEventListener('click', () => launchOrFocusApp(b.dataset.app)));
}
function iosGoHome() {
    Object.values(openWindows).forEach(w => { if (!w.isMinimized) minimizeWindow(w.id); });
    syncPhoneShell();
}
function syncPhoneShell() {
    if (!document.body.classList.contains('device-phone')) return;
    const anyOpen = Object.values(openWindows).some(w => !w.isMinimized && w.virtualDesktop === currentVirtualDesktop);
    document.body.classList.toggle('app-open', anyOpen);
}
let phoneObserver = null;
function onDeviceClassChange(phone) {
    const home = document.getElementById('ios-home'), ind = document.getElementById('ios-indicator');
    if (home) home.hidden = !phone;
    if (ind) ind.hidden = !phone;
    if (phone) {
        renderIOSHome();
        const area = document.getElementById('desktop-area');
        if (area && !phoneObserver) { phoneObserver = new MutationObserver(syncPhoneShell); phoneObserver.observe(area, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'style'] }); }
        syncPhoneShell();
    } else {
        document.body.classList.remove('app-open');
        if (phoneObserver) { phoneObserver.disconnect(); phoneObserver = null; }
    }
    if (typeof renderDock === 'function' && document.getElementById('dock')) { try { renderDock(); } catch (_) {} }
}
(function initIOSIndicator() {
    document.addEventListener('DOMContentLoaded', () => {
        const ind = document.getElementById('ios-indicator'); if (!ind) return;
        let y0 = null;
        ind.addEventListener('pointerdown', e => { y0 = e.clientY; ind.setPointerCapture(e.pointerId); });
        ind.addEventListener('pointerup', e => { if (y0 !== null && (y0 - e.clientY > 30 || Math.abs(y0 - e.clientY) < 6)) iosGoHome(); y0 = null; });
    });
})();

// Parabolic Magnifying macOS Sequoia Dock''')
sub("    if (lsTime) lsTime.textContent", "    const iosT = document.getElementById('ios-time'); if (iosT) iosT.textContent = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: false });\n    if (lsTime) lsTime.textContent")

# ---------- focus hand-off, Cmd+H hide ----------
sub('''    if (activeWindowId === windowId) {
        activeWindowId = null;
        updateTopAppMenuBar(null);
    }
    renderDock();
}

function restoreWindow''', '''    if (activeWindowId === windowId) {
        activeWindowId = null;
        focusNextAfter(windowId, winData.appId);
    }
    renderDock();
}

// Key-window hand-off (macOS): same app's next window first, then the front-most window of the space.
function focusNextAfter(excludeId, appId) {
    const cand = Object.values(openWindows).filter(w => w.id !== excludeId && !w.isMinimized && !w.isHidden && w.virtualDesktop === currentVirtualDesktop && w.element);
    cand.sort((a, b) => (parseInt(b.element.style.zIndex) || 0) - (parseInt(a.element.style.zIndex) || 0));
    const next = cand.find(w => w.appId === appId) || cand[0];
    if (next) focusWindow(next.id); else updateTopAppMenuBar(appId && Object.values(openWindows).some(w => w.appId === appId && w.id !== excludeId) ? appId : null);
}

function restoreWindow''')
sub('''            if (remaining.length > 0) focusWindow(remaining[0]);
            else updateTopAppMenuBar(null);''', '''            if (remaining.length > 0) focusNextAfter(windowId, winData.appId);
            else updateTopAppMenuBar(null);''')
# shortcut bug: bail-out on altKey killed Ctrl+Alt on non-Apple
sub("        if (e.shiftKey || e.altKey) return;\n        if (key === 'w' && active)", "        if (e.shiftKey || (IS_APPLE && e.altKey)) return;\n        if (key === 'w' && active)")
sub("else if (key === 'h' && active) { e.preventDefault(); Object.values(openWindows).filter(w => w.appId === active.appId).forEach(w => minimizeWindow(w.id)); }",
    "else if (key === 'h' && active) { e.preventDefault(); const appId = active.appId; Object.values(openWindows).filter(w => w.appId === appId).forEach(w => { w.isHidden = true; if (w.element) w.element.style.display = 'none'; }); activeWindowId = null; focusNextAfter(null, null); }")
# un-hide on launch/focus
sub("            if (win.isMinimized) restoreWindow(existingId);\n            else focusWindow(existingId);", "            if (win.isHidden) { Object.values(openWindows).filter(w => w.appId === appId && w.isHidden).forEach(w => { w.isHidden = false; if (w.element && !w.isMinimized) w.element.style.display = 'flex'; }); }\n            if (win.isMinimized) restoreWindow(existingId);\n            else focusWindow(existingId);")

# ---------- SW registration ----------
sub("    initKeyboardShortcuts();\n});", "    initKeyboardShortcuts();\n    if ('serviceWorker' in navigator && /^https?:$/.test(location.protocol)) navigator.serviceWorker.register('sw.js').catch(() => {});\n});")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
