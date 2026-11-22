p = 'index.html'
s = open(p, encoding='utf-8').read()
def sub(old, new, count=1):
    global s
    assert old in s, 'miss: ' + old[:90]
    s = s.replace(old, new, count)

# URL escape hatch: ?ui=ios or ?ui=mac (persisted)
sub("    // 'mac' (default on every device) or 'ios'", "    // 'mac' (default on every device) or 'ios'")
sub("    uiMode() { try {", "    uiMode() { try {")
sub("<script>\n", "<script>\n(function () { try { const q = new URLSearchParams(location.search).get('ui'); if (q === 'ios' || q === 'mac') localStorage.setItem('osweb_ui_mode', q); } catch (_) {} })();\n", 1) if "<script>\n" in s else None

# narrower layout width on phones in Mac mode (bigger on-screen controls), orientation aware
sub("const content = (coarse && uiMode === 'mac' && shortSide < 700) ? 'width=1100, viewport-fit=cover' : 'width=device-width, initial-scale=1, viewport-fit=cover';",
    "const portrait = !window.matchMedia || matchMedia('(orientation: portrait)').matches;\n            const content = (coarse && uiMode === 'mac' && shortSide < 700) ? `width=${portrait ? 640 : 960}, viewport-fit=cover` : 'width=device-width, initial-scale=1, viewport-fit=cover';")
sub("            const phone = uiMode === 'ios' && (vw < 600 || (coarse && Math.min(vw, vh) < 500));",
    "            const phone = uiMode === 'ios' && (vw < 600 || (coarse && Math.min(vw, vh) < 500));\n            document.body.classList.toggle('touch-small', !!coarse && uiMode === 'mac' && Math.min(screen.width || 9999, screen.height || 9999) < 700);")

# windows fill the screen on small touch devices in Mac mode (dragging/resizing by finger is impractical)
sub("    const tall = areaH > areaW * 1.2;", "    const touchSmall = document.body.classList.contains('touch-small');\n    const tall = areaH > areaW * 1.2;")
sub("    const startX = Math.max(minLeft, Math.min(areaW - defaultW - 14, idealLeft));\n    const startY = Math.max(12, Math.min(areaH - defaultH - 12, Math.round((areaH - defaultH) / 2 - 26 + offset)));",
    "    let startX = Math.max(minLeft, Math.min(areaW - defaultW - 14, idealLeft));\n    let startY = Math.max(12, Math.min(areaH - defaultH - 12, Math.round((areaH - defaultH) / 2 - 26 + offset)));\n    if (touchSmall) { startX = 8; startY = 8; }")
sub("    const defaultW = Math.min(tall ? Math.round((config.width || 820) * 1.12) : (config.width || 820), areaW - 24);\n    const defaultH = Math.min(tall ? Math.round((config.height || 540) * 1.8) : (config.height || 540), areaH - 24);",
    "    const defaultW = touchSmall ? areaW - 16 : Math.min(tall ? Math.round((config.width || 820) * 1.12) : (config.width || 820), areaW - 24);\n    const defaultH = touchSmall ? Math.min(areaH - 16, Math.round(areaW * 1.45)) : Math.min(tall ? Math.round((config.height || 540) * 1.8) : (config.height || 540), areaH - 24);")

css = '''
        /* ===================================================================
         * Touch-first sizing for Mac mode on phones (body.touch-small): same Mac look, bigger hit areas
         * =================================================================== */
        body.touch-small .st-item, body.touch-small .fx-side-item, body.touch-small .nt-row, body.touch-small .wx-loc { min-height: 40px; }
        body.touch-small .st-row { min-height: 46px; } body.touch-small .st-switch { transform: scale(1.15); transform-origin: right center; }
        body.touch-small .os-menu-item { height: 34px; line-height: 34px; } body.touch-small .menubar-item { height: 24px; padding: 0 9px; }
        body.touch-small .fx-tb, body.touch-small .fx-seg-btn { min-width: 38px; min-height: 32px; }
        body.touch-small .mac-btn-secondary, body.touch-small .action-button { min-height: 32px; }
        body.touch-small .tl-btn::after { inset: -14px -8px; }
        body.touch-small .window-title-bar { min-height: 34px; }
        body.touch-small button, body.touch-small [role="button"], body.touch-small .st-item, body.touch-small .finder-item { touch-action: manipulation; cursor: pointer; }
'''
i = s.index('    </style>'); s = s[:i] + css + s[i:]
open(p, 'w', encoding='utf-8').write(s)
print('ok')
