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

# ---- window manager: defer un-maximize until real movement; snap restores the pre-drag frame ----
rsub(r"        // If window was maximized, un-maximize proportionally under cursor, back to its previous size\n.*?        const startLeft = winEl\.offsetLeft;\n        const startTop = winEl\.offsetTop;\n", lambda m: '''        let startPt = OS.viewport.toDesktopCoords(e.clientX, e.clientY);
        let startLeft = winEl.offsetLeft, startTop = winEl.offsetTop;
        let armed = !(winData && winData.isMaximized);        // a plain click on a maximized title bar must not un-maximize it
        const unmaxUnderCursor = (pt) => {
            const areaW = area.clientWidth;
            const pre = winData.preTileRect;
            const restoreW = Math.min(pre ? parseFloat(pre.width) || 820 : 820, areaW - 40);
            winEl.style.width = `${restoreW}px`;
            winEl.style.height = `${Math.min(pre ? parseFloat(pre.height) || 540 : 540, area.clientHeight - 40)}px`;
            winData.preTileRect = null; winData.isMaximized = false;
            winEl.style.left = `${Math.max(10, pt.x - restoreW / 2)}px`; winEl.style.top = '10px';
            startLeft = winEl.offsetLeft; startTop = winEl.offsetTop; startPt = pt; nextL = startLeft; nextT = startTop;
            armed = true;
        };
''')
sub("        let nextL = startLeft, nextT = startTop, rafId = 0;\n        const paint", "        let rafId = 0;\n        const paint")
sub("        const onMove = (ev) => {\n            const pt = OS.viewport.toDesktopCoords(ev.clientX, ev.clientY);\n            const dx = pt.x - startPt.x;",
    "        const onMove = (ev) => {\n            const pt = OS.viewport.toDesktopCoords(ev.clientX, ev.clientY);\n            if (!armed) { if (Math.hypot(pt.x - startPt.x, pt.y - startPt.y) < 4) return; unmaxUnderCursor(pt); }\n            const dx = pt.x - startPt.x;")
sub("document.body.classList.add('wm-dragging');\n        try { titleBar.setPointerCapture(e.pointerId); } catch (_) {}\n        let rafId", "document.body.classList.add('wm-dragging');\n        try { titleBar.setPointerCapture(e.pointerId); } catch (_) {}\n        let nextL = startLeft, nextT = startTop;\n        let rafId")
sub("            winEl.style.left = `${nextL}px`; winEl.style.top = `${nextT}px`;\n            void winEl.offsetWidth;", "            if (pendingSnap) { winEl.style.left = `${startLeft}px`; winEl.style.top = `${startTop}px`; }   // snap records the frame from before the drag\n            else { winEl.style.left = `${nextL}px`; winEl.style.top = `${nextT}px`; }\n            void winEl.offsetWidth;")

# ---- close/relaunch race ----
sub("function closeWindow(windowId, skipAnim = false) {\n    const winData = openWindows[windowId];\n    if (!winData) return;\n", "function closeWindow(windowId, skipAnim = false) {\n    const winData = openWindows[windowId];\n    if (!winData) return;\n    winData.isClosing = true;\n")
sub("const existingId = Object.keys(openWindows).find(id => openWindows[id].appId === appId);", "const existingId = Object.keys(openWindows).find(id => openWindows[id].appId === appId && !openWindows[id].isClosing);")
sub("const cand = Object.values(openWindows).filter(w => w.id !== excludeId && !w.isMinimized", "const cand = Object.values(openWindows).filter(w => w.id !== excludeId && !w.isClosing && !w.isMinimized")

# ---- ARIA menus + keyboard navigation ----
sub("            layer.dataset.depth = String(depth);\n", "            layer.dataset.depth = String(depth);\n            layer.setAttribute('role', 'menu');\n")
sub("                    sep.className = 'os-menu-sep';\n", "                    sep.className = 'os-menu-sep'; sep.setAttribute('role', 'separator');\n")
sub("                row.className = 'os-menu-item' + (item.disabled ? ' disabled' : '');\n", "                row.className = 'os-menu-item' + (item.disabled ? ' disabled' : '');\n                row.setAttribute('role', 'menuitem'); if (item.disabled) row.setAttribute('aria-disabled', 'true'); if (item.submenu) row.setAttribute('aria-haspopup', 'menu');\n")
sub("function initKeyboardShortcuts() {", '''// Keyboard model for open menus (menu bar, Apple menu, context menus): arrows, Home/End, Enter, Esc, type-ahead.
function menuKeyNav(e) {
    const layers = OS.menu.layers; if (!layers.length) return false;
    const layer = layers[layers.length - 1];
    const rows = [...layer.querySelectorAll('.os-menu-item:not(.disabled)')];
    let i = rows.findIndex(r => r.classList.contains('kb'));
    const mark = (n) => { rows.forEach(r => r.classList.remove('kb')); if (rows[n]) { rows[n].classList.add('kb'); rows[n].scrollIntoView({ block: 'nearest' }); } };
    const top = [...document.querySelectorAll('#app-menu-bar-container .menubar-item, #apple-menu-button')];
    const topIdx = top.findIndex(b => b.classList.contains('active'));
    switch (e.key) {
        case 'ArrowDown': mark(i < 0 ? 0 : (i + 1) % rows.length); break;
        case 'ArrowUp': mark(i < 0 ? rows.length - 1 : (i - 1 + rows.length) % rows.length); break;
        case 'Home': mark(0); break; case 'End': mark(rows.length - 1); break;
        case 'ArrowRight': if (i >= 0 && rows[i].getAttribute('aria-haspopup')) { rows[i].dispatchEvent(new PointerEvent('pointerenter')); const sub = OS.menu.layers[OS.menu.layers.length - 1]; sub?.querySelector('.os-menu-item:not(.disabled)')?.classList.add('kb'); }
            else if (topIdx >= 0 && layers.length === 1) top[(topIdx + 1) % top.length].click(); break;
        case 'ArrowLeft': if (layers.length > 1) OS.menu.closeFromDepth(layers.length - 1); else if (topIdx >= 0) top[(topIdx - 1 + top.length) % top.length].click(); break;
        case 'Enter': case ' ': if (i >= 0) rows[i].click(); break;
        case 'Escape': if (layers.length > 1) OS.menu.closeFromDepth(layers.length - 1); else OS.menu.closeAll(); break;
        default:
            if (e.key.length === 1 && !e.metaKey && !e.ctrlKey) { const k = e.key.toLowerCase(); const n = rows.findIndex((r, j) => j > i && r.textContent.trim().toLowerCase().startsWith(k)); const m = n >= 0 ? n : rows.findIndex(r => r.textContent.trim().toLowerCase().startsWith(k)); if (m >= 0) mark(m); else return false; }
            else return false;
    }
    e.preventDefault(); e.stopPropagation(); return true;
}

// Focus management for modal surfaces: trap Tab, restore focus on close.
function trapFocus(container, { restore = document.activeElement } = {}) {
    const sel = 'button:not([disabled]), [href], input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])';
    const onKey = (e) => { if (e.key !== 'Tab') return; const f = [...container.querySelectorAll(sel)].filter(x => x.offsetParent !== null); if (!f.length) return; const first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); } else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); } };
    container.addEventListener('keydown', onKey);
    (container.querySelector(sel) || container).focus?.();
    return () => { container.removeEventListener('keydown', onKey); try { restore && restore.focus && restore.focus(); } catch (_) {} };
}

// While locked, everything behind the lock screen is inert (no Tab/AT/pointer access).
function setLockedState(locked) {
    ['top-panel', 'desktop-area', 'dock-wrapper', 'ios-status', 'ios-home', 'ios-indicator', 'right-sidebar'].forEach(id => { const el = document.getElementById(id); if (el) { if (locked) el.setAttribute('inert', ''); else el.removeAttribute('inert'); } });
    if (locked) setTimeout(() => document.getElementById('username-input')?.focus(), 60);
}

// Context menus inside app content (text: Cut/Copy/Paste/Select All; elsewhere: Copy/Select All).
function initContentContextMenu() {
    document.addEventListener('contextmenu', (e) => {
        if (e.defaultPrevented) return;
        const t = e.target; if (!t.closest || !t.closest('.window-content')) return;
        e.preventDefault();
        const editable = t.closest('input:not([type=checkbox]):not([type=range]), textarea, [contenteditable="true"]');
        const sel = String(window.getSelection ? window.getSelection() : '');
        const hasSel = !!sel || (editable && editable.selectionStart !== editable.selectionEnd);
        const items = editable ? [
            { label: 'Cut', shortcut: '⌘X', disabled: !hasSel, action: () => { editable.focus(); document.execCommand('cut'); } },
            { label: 'Copy', shortcut: '⌘C', disabled: !hasSel, action: () => { editable.focus(); document.execCommand('copy'); } },
            { label: 'Paste', shortcut: '⌘V', action: async () => { editable.focus(); try { const tx = await navigator.clipboard.readText(); document.execCommand('insertText', false, tx); } catch (_) { showTemporaryMessage('Use ⌘V to paste (clipboard permission needed).', 2000); } } },
            { separator: true },
            { label: 'Select All', shortcut: '⌘A', action: () => { editable.focus(); document.execCommand('selectAll'); } }
        ] : [
            { label: 'Copy', shortcut: '⌘C', disabled: !hasSel, action: () => document.execCommand('copy') },
            { label: 'Select All', shortcut: '⌘A', action: () => document.execCommand('selectAll') }
        ];
        const c = OS.viewport.toDesktopCoords(e.clientX, e.clientY);
        OS.menu.open(items, c.x, c.y, 0);
    });
}

function initKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => { if (OS.menu.layers.length) menuKeyNav(e); }, true);
    initContentContextMenu();''')
sub("function lockScreen() {\n    const loginModal = document.getElementById('login-modal');\n    if (loginModal) loginModal.classList.remove('hidden');", "function lockScreen() {\n    const loginModal = document.getElementById('login-modal');\n    if (loginModal) loginModal.classList.remove('hidden');\n    setLockedState(true);")
sub("    if (loginModal) loginModal.classList.add('hidden');\n    OS.audio.playChime();", "    if (loginModal) loginModal.classList.add('hidden');\n    setLockedState(false);\n    OS.audio.playChime();")
sub("    applyDefaultWallpaperForTheme();\n", "    applyDefaultWallpaperForTheme();\n    setLockedState(true);\n")
# About + custom modal: focus trap
sub("    document.getElementById('macos-viewport-root').appendChild(modal);\n}\n\n// Force Quit", "    document.getElementById('macos-viewport-root').appendChild(modal);\n    const release = trapFocus(modal); new MutationObserver((_, o) => { if (!modal.isConnected) { release(); o.disconnect(); } }).observe(document.getElementById('macos-viewport-root'), { childList: true });\n    modal.addEventListener('keydown', (e) => { if (e.key === 'Escape') modal.remove(); });\n}\n\n// Force Quit")
# name every control
sub("function labelButtons(root = document) {", '''function labelFields(root = document) {
    root.querySelectorAll('input:not([aria-label]):not([type=hidden]), textarea:not([aria-label]), select:not([aria-label])').forEach(f => {
        const n = f.getAttribute('placeholder') || f.getAttribute('title') || (f.dataset && f.dataset.role) || f.type || 'field';
        f.setAttribute('aria-label', String(n).replace(/[-_]/g, ' '));
    });
}
function labelButtons(root = document) {
    labelFields(root);''')
# demo content: no invented hardware
for a, b in [('Apple M3 Max', 'Apple silicon'), ('M3 Max', 'Apple silicon'), ('ARM64_T6031', 'ARM64'), ('C02ZTC5TC7M3', 'Unavailable')]:
    s = s.replace(a, b)
s = s.replace('64 GB Unified LPDDR5X', 'Unified memory').replace('64.0 GB', 'unified memory')
open(p, 'w', encoding='utf-8').write(s)
print('ok')
