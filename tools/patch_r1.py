import re, sys
p = 'index.html'
s = open(p, encoding='utf-8').read()
def sub(old, new, count=1, regex=False):
    global s
    if regex:
        s2, n = re.subn(old, new, s, count=count, flags=re.S)
        assert n >= 1, 'regex miss: ' + old[:60]
        s = s2
    else:
        assert old in s, 'miss: ' + old[:70]
        s = s.replace(old, new, count)

# ---------- head ----------
sub('<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">',
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">\n'
    '    <meta name="apple-mobile-web-app-capable" content="yes">\n    <meta name="mobile-web-app-capable" content="yes">\n'
    '    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n    <meta name="theme-color" content="#1c2d4f">')
sub('<title>macOS Sequoia 15.1 — OSWeb Desktop</title>', '<title>OSWeb</title>')

# ---------- menu bar ----------
GLYPH = lambda inner, vb='0 0 20 16': f'<svg class="mb-glyph" viewBox="{vb}" width="20" height="16" fill="currentColor" aria-hidden="true">{inner}</svg>'
menubar = '''<header id="top-panel" role="menubar" aria-label="Menu bar">
        <div class="menubar-left">
            <button id="apple-menu-button" class="menubar-item apple-logo" role="menuitem" aria-haspopup="menu" aria-label="Apple menu">
                <i class="fab fa-apple" aria-hidden="true"></i>
            </button>
            <div id="app-menu-bar-container" class="flex items-center h-full"></div>
        </div>

        <div class="menubar-right">
            <button id="battery-menubar-button" class="menubar-item" role="menuitem" aria-label="Battery" hidden>
                <span id="battery-pct" class="mb-pct"></span>
                ''' + GLYPH('<rect x="1.5" y="3.5" width="14.5" height="9" rx="2.6" fill="none" stroke="currentColor" stroke-width="1" opacity=".55"/><rect id="battery-fill" x="3" y="5" width="11.5" height="6" rx="1.4"/><path d="M17.3 6.3v3.4c.7-.2 1.2-.9 1.2-1.7s-.5-1.5-1.2-1.7z" opacity=".55"/>') + '''
            </button>
            <button id="wifi-menubar-button" class="menubar-item" role="menuitem" aria-label="Wi-Fi">
                ''' + GLYPH('<path d="M10 12.9a1.4 1.4 0 1 0 0 2.8 1.4 1.4 0 0 0 0-2.8z" transform="translate(0 -3.4)"/><path d="M6.6 9.3a4.9 4.9 0 0 1 6.8 0" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/><path d="M3.6 6.3a9.2 9.2 0 0 1 12.8 0" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/><path d="M.9 3.4a13 13 0 0 1 18.2 0" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" opacity=".0"/>') + '''
            </button>
            <button id="spotlight-menubar-button" class="menubar-item" role="menuitem" aria-label="Spotlight Search">
                ''' + GLYPH('<circle cx="8.6" cy="7.2" r="4.4" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M12 10.6l3.6 3.6" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>') + '''
            </button>
            <button id="sidebar-toggle" class="menubar-item" role="menuitem" aria-haspopup="true" aria-label="Control Center">
                ''' + GLYPH('<rect x="2.2" y="2.6" width="15.6" height="4.6" rx="2.3" fill="none" stroke="currentColor" stroke-width="1.3"/><circle cx="12.3" cy="4.9" r="1.7"/><rect x="2.2" y="8.8" width="15.6" height="4.6" rx="2.3" fill="none" stroke="currentColor" stroke-width="1.3"/><circle cx="7.7" cy="11.1" r="1.7"/>') + '''
            </button>
            <div id="clock" class="menubar-item" role="menuitem" title="Notification Center" aria-label="Date and time">Sun Nov 22  12:00 PM</div>
        </div>

        <!-- Legacy hooks kept for scripts; intentionally not part of the visible macOS menu bar -->
        <div hidden aria-hidden="true">
            <button id="app-launcher-button"></button>
            <button id="activities-button"></button>
            <div id="virtual-desktop-switcher"></div>
            <button id="add-desktop-button"></button>
            <button id="show-desktop-button"></button>
            <button id="viewport-scale-pill"><span id="viewport-scale-label">100%</span></button>
            <div id="cpu-meter"></div><div id="gpu-meter"></div>
            <input id="global-search-input" type="search" tabindex="-1">
            <button id="siri-menubar-button"></button>
            <button id="theme-toggle-button"><i></i></button>
            <button id="user-avatar-button"><img id="user-avatar-img" alt=""></button>
        </div>
    </header>'''
sub(r'<header id="top-panel">.*?</header>', lambda m: menubar, regex=True)

# ---------- widgets: macOS ships with none on the desktop; remove fake telemetry ----------
sub('<div id="desktop-widgets-container">', '<div id="desktop-widgets-container" class="hidden">')
sub(r'<!-- Widget 2: Apple Silicon M3 Max Live Telemetry -->.*?(?=<!-- Widget 3)', '', regex=True)

# ---------- lock screen ----------
lock = '''<div id="login-modal" class="lock-screen" role="dialog" aria-modal="true" aria-label="Lock screen">
        <div class="lock-top">
            <div id="lockscreen-date" class="lock-date">Sunday, November 22</div>
            <div id="lockscreen-time" class="lock-time">12:00</div>
        </div>
        <div class="lock-bottom">
            <div class="lock-avatar" aria-hidden="true"><span id="lockscreen-initial">U</span></div>
            <div id="lockscreen-username" class="lock-name">User</div>
            <form class="lock-field" onsubmit="event.preventDefault(); unlockDesktop();" autocomplete="off">
                <input type="password" id="username-input" placeholder="Enter Password" aria-label="Password" autocomplete="off">
                <button id="login-button" type="submit" aria-label="Log in">
                    <svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8h9M8.5 4l4 4-4 4"/></svg>
                </button>
            </form>
            <div class="lock-hint">Touch ID or Enter Password</div>
            <div class="lock-power">
                <button onclick="showTemporaryMessage('Sleep')" aria-label="Sleep"><span><i class="fas fa-moon"></i></span>Sleep</button>
                <button onclick="location.reload()" aria-label="Restart"><span><i class="fas fa-rotate-right"></i></span>Restart</button>
            </div>
        </div>
    </div>'''
sub(r'<div id="login-modal" class="fixed inset-0 z-\[20000\].*?\n    </div>\n</div>', lambda m: lock + '\n</div>', regex=True)

# ---------- wallpapers (local, offline) ----------
sub(r"const wallpapers = \[.*?\n\];", '''const wallpapers = [
    { name: 'Sequoia', url: 'vendor/wallpapers/sequoia.svg', dark: 'vendor/wallpapers/sequoia-dark.svg', auto: true },
    { name: 'Sonoma', url: 'vendor/wallpapers/sonoma.svg' },
    { name: 'Ventura', url: 'vendor/wallpapers/ventura.svg' },
    { name: 'Sequoia Dark', url: 'vendor/wallpapers/sequoia-dark.svg' }
];''', regex=True)
sub('''function applyWallpaper(url) {
    const el = document.getElementById('wallpaper-container');
    if (el) el.style.backgroundImage = `url('${url}')`;
    localStorage.setItem('osweb_wallpaper_url', url);
}''', '''function applyWallpaper(url, persist = true) {
    const el = document.getElementById('wallpaper-container');
    if (el) el.style.backgroundImage = `url('${url}')`;
    document.documentElement.style.setProperty('--wallpaper-url', `url('${url}')`);
    try { if (persist) localStorage.setItem('osweb_wallpaper_url', url); } catch (_) {}
}
// Default "Sequoia" wallpaper follows the appearance (dynamic light/dark), like macOS.
function applyDefaultWallpaperForTheme() {
    let saved = null;
    try { saved = localStorage.getItem('osweb_wallpaper_url'); } catch (_) {}
    if (saved && !/^https?:/.test(saved)) return applyWallpaper(saved, false);
    const light = document.body.classList.contains('light-mode');
    applyWallpaper(light ? wallpapers[0].url : wallpapers[0].dark, false);
}''')
sub('''    const savedWall = localStorage.getItem('osweb_wallpaper_url');
    applyWallpaper(savedWall || wallpapers[0].url);''', '    applyDefaultWallpaperForTheme();')
sub("    localStorage.setItem('osweb_theme_idx', String(currentThemeIndex));\n}",
    "    localStorage.setItem('osweb_theme_idx', String(currentThemeIndex));\n    if (typeof applyDefaultWallpaperForTheme === 'function' && document.getElementById('wallpaper-container')) applyDefaultWallpaperForTheme();\n}")

# ---------- dock ----------
sub(r"const pinnedDockApps = \[.*?\];", '''const pinnedDockApps = [
    'file-explorer',
    'app-launcher',
    'web-browser',
    'ai-assistant',
    'mail-client',
    'image-viewer',
    'calendar-app',
    'notepad',
    'reminders',
    'music-player',
    'clicker-game',
    'terminal',
    'settings'
];''', regex=True)
sub('''    const maxCap = iconCount > 16 ? 42 : 48;
    const baseSize = Math.max(32, Math.min(maxCap, computedSize));''', '''    const maxCap = 64;
    const baseSize = Math.max(34, Math.min(maxCap, computedSize));''')
sub("    const availableForIcons = stageW - 68 - (iconCount - 1) * gap;", "    const availableForIcons = stageW - 80 - (iconCount - 1) * gap;")
sub('''    const gap = iconCount > 18 ? 4 : 5;''', '''    const gap = 4;''')
# Trash after Downloads stack
sub('''    dock.appendChild(dlStack);

    fitDockToViewport();''', '''    dock.appendChild(dlStack);

    const trash = document.createElement('div');
    trash.className = 'dock-icon';
    trash.setAttribute('role', 'button');
    trash.setAttribute('aria-label', 'Trash');
    trash.innerHTML = `<div class="dock-tooltip">Trash</div>${getTrashSVG()}`;
    trash.addEventListener('click', () => launchOrFocusApp('file-explorer', { initialPath: '/Users/eugene/.Trash' }));
    dock.appendChild(trash);

    fitDockToViewport();''')
sub('''function getFileDocSVG(ext = 'md') {''', '''function getTrashSVG() {
    return `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <defs><linearGradient id="trBin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9EDF2" stop-opacity=".92"/><stop offset="1" stop-color="#B9C0CA" stop-opacity=".85"/></linearGradient></defs>
        <path d="M13 14 H51 L47 55 C46.8 57 45.2 58.5 43.2 58.5 H20.8 C18.8 58.5 17.2 57 17 55 Z" fill="url(#trBin)" stroke="rgba(255,255,255,.55)" stroke-width="1"/>
        <g stroke="rgba(120,128,140,.55)" stroke-width="1.6" stroke-linecap="round"><path d="M24 21 L25.5 52"/><path d="M32 21 V52"/><path d="M40 21 L38.5 52"/></g>
        <ellipse cx="32" cy="13.5" rx="19.5" ry="4.2" fill="#F4F6F9" stroke="rgba(255,255,255,.7)" stroke-width="1"/>
    </svg>`;
}

function getFileDocSVG(ext = 'md') {''')

# ---------- window chrome ----------
sub('''        <div class="window-title-text">
            <span class="w-4 h-4 inline-block">${getAppIconSVG(appId)}</span>
            <span class="window-title-label">''', '''        <div class="window-title-text">
            <span class="window-title-label">''')
sub('''            <button class="tl-btn tl-close" title="Close (⌘W)">×</button>
            <button class="tl-btn tl-min" title="Minimize (⌘M)">−</button>
            <button class="tl-btn tl-max" title="Full Screen / Hover for Sequoia Window Tiling">+</button>''',
'''            <button class="tl-btn tl-close" title="Close" aria-label="Close window"><svg viewBox="0 0 8 8" aria-hidden="true"><path d="M1.6 1.6l4.8 4.8M6.4 1.6L1.6 6.4"/></svg></button>
            <button class="tl-btn tl-min" title="Minimize" aria-label="Minimize window"><svg viewBox="0 0 8 8" aria-hidden="true"><path d="M1.2 4h5.6"/></svg></button>
            <button class="tl-btn tl-max" title="Zoom" aria-label="Zoom window"><svg viewBox="0 0 8 8" aria-hidden="true"><path d="M1.8 6.2V2.6a.4.4 0 0 1 .4-.4h3.6M6.2 1.8v3.6a.4.4 0 0 1-.4.4H2.2" fill="currentColor" stroke="none" opacity="0"/><path d="M2 2h3.2L2 5.2zM6 6H2.8L6 2.8z" fill="currentColor" stroke="none"/></svg></button>''')
sub("    winEl.className = 'window focused';", "    winEl.className = 'window focused';\n    winEl.dataset.app = appId;\n    winEl.setAttribute('role', 'group');\n    winEl.setAttribute('aria-label', config.title);")

# ---------- clock / telemetry ----------
sub("        clockEl.textContent = `${dStr}  ${tStr}`;", "        clockEl.textContent = `${dStr.replace(',', '')}  ${tStr}`;")
sub(r"    // CPU & GPU Telemetry\n    const winCount.*?\n}\n\nfunction lockScreen", "}\n\nfunction lockScreen", regex=True)
sub("setInterval(updateClockAndTelemetry, 2000);", '''(function tickClock() {
        updateClockAndTelemetry();
        setTimeout(tickClock, 60000 - (Date.now() % 60000) + 50);   // aligned to the minute, no 2s repaint
    })();
    document.addEventListener('visibilitychange', () => { if (!document.hidden) updateClockAndTelemetry(); });''')
sub("    updateClockAndTelemetry();\n    setInterval", "    setInterval") if "    updateClockAndTelemetry();\n    setInterval" in s else None

# ---------- menubar wiring ----------
sub("    document.getElementById('cpu-meter')?.addEventListener('click', () => launchOrFocusApp('system-monitor'));\n    document.getElementById('gpu-meter')?.addEventListener('click', () => launchOrFocusApp('system-monitor'));\n", "    document.getElementById('spotlight-menubar-button')?.addEventListener('click', () => toggleSpotlight());\n")
sub("showTemporaryMessage('Wi-Fi: Connected to Sequoia-5G (1200 Mbps)', 1800)", "showTemporaryMessage(navigator.onLine ? 'Wi-Fi: Connected' : 'Wi-Fi: Not Connected', 1600)")
sub("    document.getElementById('battery-menubar-button')?.addEventListener('click', () => showTemporaryMessage('Battery 100% — Power Source: MagSafe 3 (140W)', 1800));\n", '''    initRealStatusItems();
''')
s = s.replace("function lockScreen() {", '''// Real device status (no invented numbers): Battery API where supported, online state from the browser.
async function initRealStatusItems() {
    const wifi = document.getElementById('wifi-menubar-button');
    const syncNet = () => { if (wifi) wifi.style.opacity = navigator.onLine ? '1' : '.4'; };
    window.addEventListener('online', syncNet); window.addEventListener('offline', syncNet); syncNet();
    const btn = document.getElementById('battery-menubar-button');
    if (!btn || !navigator.getBattery) return;           // Safari/Firefox: no API -> show nothing rather than fake it
    try {
        const b = await navigator.getBattery();
        const paint = () => {
            btn.hidden = false;
            const pct = Math.round(b.level * 100);
            const pe = document.getElementById('battery-pct'); if (pe) pe.textContent = pct + '%';
            const fill = document.getElementById('battery-fill'); if (fill) fill.setAttribute('width', String(Math.max(1, 11.5 * b.level)));
            btn.title = `Battery ${pct}%` + (b.charging ? ' (charging)' : '');
        };
        b.addEventListener('levelchange', paint); b.addEventListener('chargingchange', paint); paint();
    } catch (_) {}
}

function lockScreen() {''', 1)

# unlock: no longer reads name from the field
sub("""    const name = (userInput && userInput.value.trim()) ? userInput.value.trim() : 'Eugene Redko';
    currentUsername = name;""", """    let name = 'Eugene Redko';
    try { name = localStorage.getItem('osweb_username') || name; } catch (_) {}
    currentUsername = name;
    if (userInput) userInput.value = '';""")

# ---------- keyboard ----------
sub(r"    window\.addEventListener\('keydown', \(e\) => \{\n        if \(e\.key === 'Escape' \|\| e\.code === 'Escape'\) \{\n            OS\.menu\.closeAll\(\);.*?\}, true\);\n\}\);", '''    initKeyboardShortcuts();
});

/* ============================================================================
 * Keyboard layer: macOS shortcuts. On Apple platforms the modifier is Cmd; elsewhere Ctrl+Alt,
 * so we never hijack browser-reserved bare Ctrl combos. (Safari itself reserves some Cmd keys
 * such as Cmd+W/Q/Tab/N — those work once the site is installed to the Dock / Home Screen.)
 * ============================================================================ */
const IS_APPLE = /Mac|iPhone|iPad|iPod/.test(navigator.platform || '') || /Mac OS X|iPhone|iPad/.test(navigator.userAgent || '');
const hasMod = (e) => IS_APPLE ? e.metaKey : (e.ctrlKey && e.altKey);

function runningAppsMRU() {
    const seen = []; 
    Object.values(openWindows).sort((a, b) => (parseInt(b.element?.style.zIndex) || 0) - (parseInt(a.element?.style.zIndex) || 0))
        .forEach(w => { if (!seen.includes(w.appId)) seen.push(w.appId); });
    return seen;
}
const appSwitcher = { el: null, list: [], idx: 0,
    open(dir) {
        this.list = runningAppsMRU(); if (this.list.length < 2) return;
        this.idx = dir < 0 ? this.list.length - 1 : 1;
        this.el = document.createElement('div'); this.el.id = 'app-switcher'; this.el.setAttribute('role', 'listbox'); this.el.setAttribute('aria-label', 'Application switcher');
        document.getElementById('macos-viewport-root').appendChild(this.el); this.render();
    },
    render() { this.el.innerHTML = this.list.map((id, i) => `<div class="as-item${i === this.idx ? ' sel' : ''}" role="option" aria-selected="${i === this.idx}"><div class="as-icon">${getAppIconSVG(id)}</div><div class="as-name">${escapeHtml(appConfig[id]?.title || id)}</div></div>`).join(''); },
    step(dir) { this.idx = (this.idx + dir + this.list.length) % this.list.length; this.render(); },
    commit() { if (!this.el) return; const id = this.list[this.idx]; this.el.remove(); this.el = null; if (id) launchOrFocusApp(id); }
};

function initKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
        const key = (e.key || '').toLowerCase();
        if (e.key === 'Escape') {
            if (appSwitcher.el) { appSwitcher.el.remove(); appSwitcher.el = null; }
            OS.menu.closeAll(); OS.spotlight.close(); toggleLaunchpad(false); toggleMissionControl(false);
        }
        const mod = hasMod(e);
        const active = activeWindowId && openWindows[activeWindowId];
        if ((mod && e.code === 'Space') || (e.altKey && !e.ctrlKey && !e.metaKey && e.code === 'Space')) { e.preventDefault(); toggleSpotlight(); return; }
        if (e.key === 'F3') { e.preventDefault(); toggleMissionControl(); return; }
        if (e.key === 'F4') { e.preventDefault(); toggleLaunchpad(); return; }
        if (e.ctrlKey && !e.metaKey && !e.altKey && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
            const ids = (typeof virtualDesktops !== 'undefined' ? virtualDesktops : []).map(d => d.id);
            const i = ids.indexOf(currentVirtualDesktop); if (ids.length > 1 && i >= 0) { e.preventDefault(); switchVirtualDesktop(ids[(i + (e.key === 'ArrowRight' ? 1 : -1) + ids.length) % ids.length]); }
            return;
        }
        if (e.key === 'Tab' && (mod || e.altKey)) {   // Cmd+Tab (or Option+Tab where the OS/browser owns Cmd+Tab)
            e.preventDefault();
            if (!appSwitcher.el) appSwitcher.open(e.shiftKey ? -1 : 1); else appSwitcher.step(e.shiftKey ? -1 : 1);
            return;
        }
        if (!mod) return;
        if (e.altKey && e.key === 'Escape') { e.preventDefault(); openForceQuitModal(); return; }
        if (e.ctrlKey && key === 'f' && active) { e.preventDefault(); toggleMaximizeWindow(activeWindowId); return; }
        if (e.shiftKey || e.altKey) return;
        if (key === 'w' && active) { e.preventDefault(); closeWindow(activeWindowId); }
        else if (key === 'm' && active) { e.preventDefault(); minimizeWindow(activeWindowId); }
        else if (key === 'q' && active) { e.preventDefault(); Object.values(openWindows).filter(w => w.appId === active.appId).forEach(w => closeWindow(w.id)); }
        else if (key === 'h' && active) { e.preventDefault(); Object.values(openWindows).filter(w => w.appId === active.appId).forEach(w => minimizeWindow(w.id)); }
        else if (key === 'n' && active) { e.preventDefault(); createWindow(active.appId, { forceNew: true }); }
        else if (key === ',') { e.preventDefault(); launchOrFocusApp('settings'); }
        else if (e.code === 'Backquote' && active) {
            e.preventDefault();
            const same = Object.values(openWindows).filter(w => w.appId === active.appId && !w.isMinimized);
            if (same.length > 1) { const i = same.findIndex(w => w.id === activeWindowId); focusWindow(same[(i + 1) % same.length].id); }
        }
    }, true);
    window.addEventListener('keyup', (e) => {
        if (appSwitcher.el && (e.key === 'Meta' || e.key === 'Alt' || e.key === 'Control')) appSwitcher.commit();
    }, true);
}''', regex=True)

open(p, 'w', encoding='utf-8').write(s)
print('patched OK')
