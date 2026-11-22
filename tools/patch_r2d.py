p = 'index.html'
s = open(p, encoding='utf-8').read()
def sub(old, new, count=1):
    global s
    assert old in s, 'miss: ' + old[:80]
    s = s.replace(old, new, count)

sub("function initKeyboardShortcuts() {", '''/* ============================================================================
 * StateStore + session restore. Everything that must follow the user between devices goes through
 * OS.store (namespaced per user, versioned, JSON). Today the adapter is localStorage; a remote
 * (cloud) adapter can replace get/set without touching any caller.
 * ============================================================================ */
OS.store = {
    ns() { return 'osweb:' + String(currentUsername || localStorage.getItem('osweb_username') || 'user').toLowerCase().replace(/\\s+/g, '-') + ':'; },
    get(key, fallback = null) { try { const v = localStorage.getItem(this.ns() + key); return v == null ? fallback : JSON.parse(v); } catch (_) { return fallback; } },
    set(key, value) { try { localStorage.setItem(this.ns() + key, JSON.stringify(value)); } catch (_) {} }
};
function serializeSession() {
    const wins = Object.values(openWindows).filter(w => w.element).map(w => {
        const el = w.element, pre = w.preTileRect;
        let opts = {}; try { opts = JSON.parse(JSON.stringify(w.options || {})); } catch (_) {}
        return { appId: w.appId, opts, space: w.virtualDesktop, min: !!w.isMinimized, max: !!(w.isMaximized || pre), z: parseInt(el.style.zIndex) || 0,
            rect: { left: pre ? pre.left : el.style.left, top: pre ? pre.top : el.style.top, width: pre ? pre.width : el.style.width, height: pre ? pre.height : el.style.height } };
    }).sort((a, b) => a.z - b.z);
    return { v: 1, space: currentVirtualDesktop, active: activeWindowId && openWindows[activeWindowId] ? openWindows[activeWindowId].appId : null, windows: wins };
}
let sessionSaveTimer = null;
function scheduleSessionSave() {
    if (document.getElementById('login-modal') && !document.getElementById('login-modal').classList.contains('hidden')) return;   // never overwrite while locked
    clearTimeout(sessionSaveTimer);
    sessionSaveTimer = setTimeout(() => OS.store.set('session', serializeSession()), 400);
}
function restoreSession() {
    const sess = OS.store.get('session');
    if (!sess || sess.v !== 1 || !Array.isArray(sess.windows) || !sess.windows.length) return false;
    let made = 0;
    sess.windows.forEach(sw => {
        if (!appConfig[sw.appId]) return;
        if (sw.space && virtualDesktops.includes(sw.space)) currentVirtualDesktop = sw.space; else currentVirtualDesktop = virtualDesktops[0];
        const id = createWindow(sw.appId, Object.assign({}, sw.opts || {}, { forceNew: true }));
        const w = id && openWindows[id]; if (!w) return;
        Object.assign(w.element.style, { left: sw.rect.left, top: sw.rect.top, width: sw.rect.width, height: sw.rect.height });
        if (sw.max) tileWindow(id, 'maximize');
        if (sw.min) minimizeWindow(id);
        made++;
    });
    if (sess.space && virtualDesktops.includes(sess.space)) switchVirtualDesktop(sess.space);
    const front = Object.values(openWindows).filter(w => !w.isMinimized && w.virtualDesktop === currentVirtualDesktop && (!sess.active || w.appId === sess.active));
    if (front.length) focusWindow(front[front.length - 1].id);
    return made > 0;
}
function initSessionPersistence() {
    const area = document.getElementById('desktop-area');
    if (area) new MutationObserver(scheduleSessionSave).observe(area, { childList: true, subtree: true, attributes: true, attributeFilter: ['style', 'class'] });
    window.addEventListener('pagehide', () => OS.store.set('session', serializeSession()));
    document.addEventListener('visibilitychange', () => { if (document.hidden) OS.store.set('session', serializeSession()); });
}

function initKeyboardShortcuts() {''')
sub("        if (!document.body.classList.contains('device-phone')) launchOrFocusApp('file-explorer');",
    "        if (!restoreSession() && !document.body.classList.contains('device-phone')) launchOrFocusApp('file-explorer');\n        scheduleSessionSave();")
sub("    initKeyboardShortcuts();\n    if ('serviceWorker'", "    initKeyboardShortcuts();\n    initSessionPersistence();\n    if ('serviceWorker'")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
