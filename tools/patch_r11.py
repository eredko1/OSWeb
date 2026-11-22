import re
p = 'index.html'
s = open(p, encoding='utf-8').read()
def sub(old, new, count=1):
    global s
    assert old in s, 'miss: ' + old[:90]
    s = s.replace(old, new, count)

# ---- viewport: set it correctly BEFORE first layout, and replace the <meta> node on change (iOS ignores attribute edits) ----
sub('    <meta name="theme-color"', '''    <script>
    // Runs before first layout: pick the right viewport for this device/mode, so iOS never has to re-flow after load.
    (function () {
        try {
            var q = new URLSearchParams(location.search).get('ui'); if (q === 'ios' || q === 'mac') localStorage.setItem('osweb_ui_mode', q);
            var coarse = matchMedia('(pointer: coarse)').matches, ios = localStorage.getItem('osweb_ui_mode') === 'ios';
            var shortSide = Math.min(screen.width, screen.height);
            var portrait = matchMedia('(orientation: portrait)').matches;
            var c = (coarse && !ios && shortSide < 700) ? 'width=' + (portrait ? 640 : 960) + ', viewport-fit=cover' : 'width=device-width, initial-scale=1, viewport-fit=cover';
            var m = document.querySelector('meta[name="viewport"]'); if (m && m.getAttribute('content') !== c) m.setAttribute('content', c);
        } catch (e) {}
    })();
    </script>
    <meta name="theme-color"''')
sub("            if (meta.getAttribute('content') !== content) meta.setAttribute('content', content);",
    "            if (meta.getAttribute('content') !== content) {\n                // iOS Safari only honours a viewport change when the <meta> element itself is replaced\n                const fresh = document.createElement('meta'); fresh.name = 'viewport'; fresh.content = content;\n                meta.replaceWith(fresh);\n            }")
# switching UI mode = reload (session restores); no in-place re-layout
sub("        OS.viewport.apply();\n        setTimeout(() => OS.viewport.apply(), 350);          // iOS Safari re-lays out after a viewport change",
    "        setTimeout(() => location.reload(), 120);            // a clean reload applies the new viewport reliably; the session restores")

# ---- touch hygiene ----
sub("        body { -webkit-text-size-adjust: 100%; -webkit-tap-highlight-color: transparent; }",
    "        html { touch-action: manipulation; }       /* no double-tap-to-zoom delay; pinch still works */\n        body { -webkit-text-size-adjust: 100%; -webkit-tap-highlight-color: transparent; }")
css = '''
        /* iOS only fires click on elements it considers clickable: give every interactive element a pointer cursor */
        [role="button"], [role="option"], [role="menuitem"], [role="tab"], [role="switch"], .os-menu-item, .finder-item, .nt-row, .sl-row, .dock-icon, .desktop-icon, .lp-app, .mc-card, .st-item, .st-appr, .st-wall, .fx-side-item, .wx-loc, .wx-res, .sf-tab, .sf-fav, .am-table tbody tr, .ios-app, button { cursor: pointer; }
        .window-content { -webkit-touch-callout: none; }
        #touch-debug { position: fixed; left: 6px; right: 6px; bottom: 6px; z-index: 40000; background: rgba(0,0,0,0.82); color: #9f9; font: 11px/1.35 ui-monospace, Menlo, monospace; padding: 6px 8px; border-radius: 8px; max-height: 34vh; overflow: auto; white-space: pre-wrap; pointer-events: none; }
'''
i = s.index('    </style>'); s = s[:i] + css + s[i:]

# ---- focusWindow: a tap inside the already-front window must not restack / rebuild chrome ----
sub("    Object.values(openWindows).forEach(w => {\n        if (w.element) w.element.classList.remove('focused');\n    });\n    highestZIndex++;",
    "    if (activeWindowId === windowId && winData.element.classList.contains('focused') && parseInt(winData.element.style.zIndex) === highestZIndex) return;   // already front: do nothing (keeps taps clean on iOS)\n    Object.values(openWindows).forEach(w => {\n        if (w.element) w.element.classList.remove('focused');\n    });\n    highestZIndex++;")
sub("function updateTopAppMenuBar(appId) {\n    const container = document.getElementById('app-menu-bar-container');\n    if (!container) return;\n    container.innerHTML = '';",
    "function updateTopAppMenuBar(appId) {\n    const container = document.getElementById('app-menu-bar-container');\n    if (!container) return;\n    const key = `${appId || ''}|${!!activeWindowId}|${virtualDesktops.join(',')}`;\n    if (container.dataset.key === key && container.childElementCount) return;      // unchanged: don't rebuild the menu bar on every tap\n    container.dataset.key = key;\n    container.innerHTML = '';")

# ---- hover-driven handlers only for real mice ----
sub("                    row.addEventListener('pointerenter', () => {\n                        layer.querySelectorAll('.os-menu-item.submenu-open')", "                    row.addEventListener('pointerenter', (pe) => {\n                        if (pe.pointerType && pe.pointerType !== 'mouse') return;\n                        layer.querySelectorAll('.os-menu-item.submenu-open')")
sub("                    row.addEventListener('pointerenter', () => {\n                        layer.querySelectorAll('.os-menu-item.submenu-open').forEach(r => r.classList.remove('submenu-open'));\n                        this.closeFromDepth(depth + 1);", "                    row.addEventListener('pointerenter', (pe) => {\n                        if (pe.pointerType && pe.pointerType !== 'mouse') return;\n                        layer.querySelectorAll('.os-menu-item.submenu-open').forEach(r => r.classList.remove('submenu-open'));\n                        this.closeFromDepth(depth + 1);")
# submenu rows must open on tap
sub("                    arrow.innerHTML = '<i class=\"fas fa-chevron-right text-[10px]\"></i>';\n                    row.appendChild(arrow);\n", "                    arrow.innerHTML = '<i class=\"fas fa-chevron-right text-[10px]\"></i>';\n                    row.appendChild(arrow);\n                    row.addEventListener('click', (ce) => { ce.stopPropagation(); row.dispatchEvent(new PointerEvent('pointerenter', { pointerType: 'mouse' })); });\n")

# ---- ?debug=touch: see exactly what the phone delivers ----
sub("function initKeyboardShortcuts() {\n", '''function initTouchDebug() {
    if (new URLSearchParams(location.search).get('debug') !== 'touch') return;
    const box = document.createElement('div'); box.id = 'touch-debug'; document.body.appendChild(box);
    const lines = []; const log = (t) => { lines.push(t); if (lines.length > 14) lines.shift(); box.textContent = `viewport ${innerWidth}x${innerHeight} vv ${visualViewport ? visualViewport.width.toFixed(0) + 'x' + visualViewport.height.toFixed(0) + '@' + visualViewport.scale.toFixed(2) : '-'} mode=${OS.uiMode()} hover=${matchMedia('(hover: hover)').matches} coarse=${matchMedia('(pointer: coarse)').matches}\\n` + lines.join('\\n'); };
    const desc = (e) => { const t = e.target; return (t && t.tagName ? t.tagName.toLowerCase() : '?') + (t && t.id ? '#' + t.id : '') + (t && t.className && typeof t.className === 'string' ? '.' + t.className.split(' ')[0] : ''); };
    ['pointerdown', 'pointerup', 'click'].forEach(ev => document.addEventListener(ev, (e) => log(`${ev.padEnd(11)} ${e.pointerType || ''} ${desc(e)} @${Math.round(e.clientX)},${Math.round(e.clientY)}`), true));
    log('debug on: tap things; each line is an event the browser delivered');
}
function initKeyboardShortcuts() {
    initTouchDebug();
''')
open(p, 'w', encoding='utf-8').write(s)
print('ok')
