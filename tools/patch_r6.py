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

# 44pt sizing only belongs to the iPhone shell; Mac mode keeps Mac metrics on touch devices
sub("@media (pointer: coarse) { .dock-icon, .menubar-item, .tl-btn::after { min-height: 44px; } .tl-btn { position: relative; } .tl-btn::after { content: ''; position: absolute; inset: -16px -6px; min-height: 0; } }",
    "body.device-phone .dock-icon, body.device-phone .menubar-item { min-height: 44px; }\n        @media (pointer: coarse) { .tl-btn { position: relative; } .tl-btn::after { content: ''; position: absolute; inset: -16px -6px; } }")
sub("@media (pointer: coarse) { .fx-tb, .fx-seg-btn { min-width: 44px; min-height: 44px; } .fx-side-item { min-height: 44px; } }",
    "body.device-phone .fx-tb, body.device-phone .fx-seg-btn { min-width: 44px; min-height: 44px; } body.device-phone .fx-side-item { min-height: 44px; }")
rsub(r"        @media \(pointer: coarse\) \{\n            button, \[role=\"button\"\], \.nt-row.*?\n        \}\n        @media \(forced-colors", lambda m: '''        body.device-phone button, body.device-phone [role="button"], body.device-phone .nt-row, body.device-phone .fx-side-item, body.device-phone .wx-loc, body.device-phone .wx-res { min-height: 44px; }
        body.device-phone .am-table td { height: 44px; } body.device-phone .mac-btn-secondary, body.device-phone .action-button { min-height: 44px; padding: 0 16px; }
        body.device-phone input[type="range"] { min-height: 44px; }
        @media (forced-colors''')

# ---- UI mode: Mac (default) or iPhone-style shell ----
sub("            const coarse = window.matchMedia && matchMedia('(pointer: coarse)').matches;\n            const phone = vw < 600 || (coarse && Math.min(vw, vh) < 500);",
    "            const coarse = window.matchMedia && matchMedia('(pointer: coarse)').matches;\n            const uiMode = OS.uiMode();\n            this.applyViewportMeta(coarse, uiMode);\n            const phone = uiMode === 'ios' && (vw < 600 || (coarse && Math.min(vw, vh) < 500));")
sub("        toDesktopCoords(clientX, clientY) {", '''        // Mac mode on phones: lay the page out at Mac width and let the browser scale it to the screen
        // (so media queries, hit-testing and pinch-zoom all behave like a desktop site). iOS mode uses the real device width.
        applyViewportMeta(coarse, uiMode) {
            const meta = document.querySelector('meta[name="viewport"]'); if (!meta) return;
            const shortSide = Math.min(screen.width || 9999, screen.height || 9999);
            const content = (coarse && uiMode === 'mac' && shortSide < 700) ? 'width=1100, viewport-fit=cover' : 'width=device-width, initial-scale=1, viewport-fit=cover';
            if (meta.getAttribute('content') !== content) meta.setAttribute('content', content);
        },

        toDesktopCoords(clientX, clientY) {''')
sub("    // --- 4.2 Zero-Dependency Web Audio API Sound & Synth Engine", '''    // 'mac' (default on every device) or 'ios' (iPhone-style home screen + full-screen apps; opt-in)
    uiMode() { try { return localStorage.getItem('osweb_ui_mode') === 'ios' ? 'ios' : 'mac'; } catch (_) { return 'mac'; } },
    setUiMode(m) {
        try { localStorage.setItem('osweb_ui_mode', m === 'ios' ? 'ios' : 'mac'); } catch (_) {}
        OS.viewport.apply();
        setTimeout(() => OS.viewport.apply(), 350);          // iOS Safari re-lays out after a viewport change
    },

    // --- 4.2 Zero-Dependency Web Audio API Sound & Synth Engine''')

# ---- Settings > General: Interface row (touch devices) ----
sub("                row('Version', 'OSWeb 0.2')) + group(", "                row('Version', 'OSWeb 0.2')) + (isTouchDevice() ? group(row('Interface', `<div class=\"fx-seg\" role=\"group\" aria-label=\"Interface\"><button class=\"fx-seg-btn${OS.uiMode() === 'mac' ? ' on' : ''}\" data-ui=\"mac\" style=\"width:auto;padding:0 14px\">Mac</button><button class=\"fx-seg-btn${OS.uiMode() === 'ios' ? ' on' : ''}\" data-ui=\"ios\" style=\"width:auto;padding:0 14px\">iPhone</button></div>`, 'Mac is the default on iPad and iPhone')) : '') + group(")
sub("            paneEl.querySelector('#factory-reset-btn').onclick = () => showCustomModal({", "            paneEl.querySelectorAll('[data-ui]').forEach(b => b.onclick = () => { OS.setUiMode(b.dataset.ui); setTimeout(renderPane, 400); });\n            paneEl.querySelector('#factory-reset-btn').onclick = () => showCustomModal({")
sub("function initSettings(winEl) {", "function isTouchDevice() { return !!(window.matchMedia && matchMedia('(pointer: coarse)').matches); }\nfunction initSettings(winEl) {")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
