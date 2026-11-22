import re
p = 'index.html'
s = open(p, encoding='utf-8').read()
def sub(old, new, count=1):
    global s
    assert old in s, 'miss: ' + old[:80]
    s = s.replace(old, new, count)
def rsub(pat, fn):
    global s
    s2, n = re.subn(pat, fn, s, count=1, flags=re.S)
    assert n == 1, 'rmiss: ' + pat[:60]
    s = s2

# ---- Wi-Fi: three arcs + dot ----
WIFI = ('<svg class="mb-glyph" viewBox="0 0 20 16" width="20" height="16" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" transform="translate(0 1)">'
        '<path d="M6.4 10.4a5 5 0 0 1 7.2 0"/><path d="M3.6 7.6a9 9 0 0 1 12.8 0"/><path d="M.9 4.9a12.8 12.8 0 0 1 18.2 0"/></g><circle cx="10" cy="13.4" r="1.5" fill="currentColor"/></svg>')
rsub(r'(<button id="wifi-menubar-button"[^>]*>\s*)<svg class="mb-glyph".*?</svg>', lambda m: m.group(1) + WIFI)

# ---- Spotlight: no ESC chip / dashboard placeholder / AI row ----
rsub(r'<div class="flex items-center px-4 py-3 border-b border-\[var\(--border-color\)\] gap-3">.*?</button>\s*</div>\s*<div id="spotlight-results"',
     lambda m: '''<div class="sl-field">
                <svg class="sl-mag" viewBox="0 0 20 20" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.6"/><path d="M13 13l4.6 4.6"/></svg>
                <input id="spotlight-input" type="text" placeholder="Spotlight Search" aria-label="Spotlight Search" autocomplete="off" spellcheck="false" />
            </div>
            <div id="spotlight-results"''')
sub('<div id="spotlight-results" class="max-h-80 overflow-y-auto p-2 space-y-1"></div>', '<div id="spotlight-results" role="listbox" aria-label="Results"></div>')
rsub(r"        // 4\. Apple Intelligence Syscall Option.*?\n        \}\n\n        results\.innerHTML", lambda m: '''        // 4. Web search (opens the in-OS browser)
        if (q.length > 1 && items.length < 3) {
            items.push({ title: `Search the Web for "${q}"`, sub: 'Safari', icon: getAppIconSVG('web-browser'),
                action: () => { toggleSpotlight(false); launchOrFocusApp('web-browser', { url: 'https://duckduckgo.com/?q=' + encodeURIComponent(q) }); } });
        }

        results.innerHTML''')
rsub(r"        results\.innerHTML = items\.slice\(0, 12\)\.map\(\(it, i\) => `.*?`\)\.join\(''\);", lambda m: '''        const shown = items.slice(0, 9);
        results.innerHTML = shown.length ? `<div class="sl-head">${q ? 'Top Hit' : 'Suggestions'}</div>` + shown.map((it, i) => `
            <div class="sl-row${i === 0 ? ' sel' : ''}" role="option" data-idx="${i}">
                <div class="sl-ico">${it.icon}</div>
                <div class="sl-txt"><div class="sl-title">${escapeHtml(it.title)}</div><div class="sl-sub">${escapeHtml(it.sub)}</div></div>
            </div>`).join('') : '';''')
sub("    input.onkeydown = (e) => {\n        if (e.key === 'Escape' || e.code === 'Escape') {\n            e.preventDefault();\n            e.stopPropagation();\n            OS.spotlight.close();\n            return;\n        }",
    "    input.onkeydown = (e) => {\n        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {\n            e.preventDefault();\n            const rows = [...results.querySelectorAll('.sl-row')]; if (!rows.length) return;\n            let i = rows.findIndex(r => r.classList.contains('sel')); rows[i]?.classList.remove('sel');\n            i = (i + (e.key === 'ArrowDown' ? 1 : -1) + rows.length) % rows.length; rows[i].classList.add('sel'); rows[i].scrollIntoView({ block: 'nearest' });\n            return;\n        }\n        if (e.key === 'Escape' || e.code === 'Escape') {\n            e.preventDefault();\n            e.stopPropagation();\n            OS.spotlight.close();\n            return;\n        }")
sub("            const first = results.querySelector('[data-idx=\"0\"]');\n            if (first) first.click();", "            const first = results.querySelector('.sl-row.sel') || results.querySelector('[data-idx=\"0\"]');\n            if (first) first.click();")
# hide third-party brand apps from system surfaces
sub("// Spotlight Search Overlay (Cmd+K / Cmd+Space)", "const HIDDEN_FROM_LAUNCHERS = new Set(['app-launcher', 'task-manager', 'chrome', 'slack', 'spotify', 'vscode', 'code-studio']);\n\n// Spotlight Search Overlay (Cmd+Space)")
sub("        Object.entries(appConfig).forEach(([id, cfg]) => {\n            if (!q || cfg.title", "        Object.entries(appConfig).forEach(([id, cfg]) => {\n            if (HIDDEN_FROM_LAUNCHERS.has(id)) return;\n            if (!q || cfg.title")
sub("sub: 'Application — /Applications',", "sub: 'Application',")

# ---- Launchpad ----
sub("const ids = Object.keys(appConfig).filter(id => id !== 'app-launcher' && id !== 'task-manager');", "const ids = Object.keys(appConfig).filter(id => !HIDDEN_FROM_LAUNCHERS.has(id));")
rsub(r'''\.map\(id => `\s*<div class="flex flex-col items-center gap-2 cursor-pointer group w-24 text-center".*?</div>\s*`\)\.join\(''\);''', lambda m: '''.map(id => `
                <button class="lp-app" onclick="toggleLaunchpad(false); launchOrFocusApp('${escapeHtml(id)}');" aria-label="${escapeHtml(appConfig[id].title)}">
                    <span class="lp-ico">${getAppIconSVG(id)}</span>
                    <span class="lp-name">${escapeHtml(appConfig[id].title)}</span>
                </button>
            `).join('');''')
rsub(r'<div class="w-72 mb-8">.*?</div>\s*</div>\s*<div id="launchpad-grid"[^>]*></div>', lambda m: '''<div class="lp-search">
            <svg viewBox="0 0 20 20" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.6"/><path d="M13 13l4.6 4.6"/></svg>
            <input id="launchpad-search" type="text" placeholder="Search" aria-label="Search applications" autocomplete="off" />
        </div>
        <div id="launchpad-grid"></div>''')

# ---- Mission Control: spaces strip + live scaled window thumbnails ----
rsub(r'<div id="mission-control-overlay">.*?</div>\s*</div>\s*(?=\n    <!-- Backward-compat)', lambda m: '''<div id="mission-control-overlay" role="dialog" aria-label="Mission Control">
        <div id="mc-spaces-bar"></div>
        <div id="mc-windows-grid"></div>
    </div>
''')
rsub(r"    spacesBar\.innerHTML = virtualDesktops\.map.*?    overlay\.classList\.add\('active'\);\n\}", lambda m: '''    spacesBar.innerHTML = virtualDesktops.map(d => `<button class="mc-space${d === currentVirtualDesktop ? ' cur' : ''}" onclick="switchVirtualDesktop(${d}); toggleMissionControl(true);" aria-label="Desktop ${d}"><span class="mc-space-thumb"></span><span>Desktop ${d}</span></button>`).join('')
        + `<button class="mc-add" onclick="addVirtualDesktop(); toggleMissionControl(true);" aria-label="Add Desktop">+</button>`;

    const spaceWins = Object.values(openWindows).filter(w => w.virtualDesktop === currentVirtualDesktop && w.element);
    winGrid.innerHTML = '';
    spaceWins.forEach(w => {
        const el = w.element, ww = el.offsetWidth || parseInt(el.style.width) || 600, wh = el.offsetHeight || parseInt(el.style.height) || 400;
        const k = Math.min(1, 300 / ww, 220 / wh);
        const card = document.createElement('button');
        card.className = 'mc-card'; card.setAttribute('aria-label', w.title);
        const thumb = document.createElement('div'); thumb.className = 'mc-thumb'; thumb.style.width = `${Math.round(ww * k)}px`; thumb.style.height = `${Math.round(wh * k)}px`;
        const clone = el.cloneNode(true);
        clone.removeAttribute('id'); clone.querySelectorAll('[id]').forEach(n => n.removeAttribute('id'));
        clone.style.cssText = `position:absolute;left:0;top:0;width:${ww}px;height:${wh}px;transform:scale(${k});transform-origin:0 0;display:flex;opacity:1;pointer-events:none;`;
        clone.classList.remove('minimizing', 'closing'); clone.querySelectorAll('iframe,canvas,video,audio').forEach(n => n.remove());
        thumb.appendChild(clone);
        const label = document.createElement('div'); label.className = 'mc-label'; label.textContent = w.title;
        card.append(thumb, label);
        card.addEventListener('click', () => { toggleMissionControl(false); if (w.isMinimized) restoreWindow(w.id); else focusWindow(w.id); });
        winGrid.appendChild(card);
    });
    overlay.classList.add('active');
}''')

# ---- Apple menu ----
rsub(r"function getAppleMenuItems\(\) \{.*?\n\}\n\nfunction getAppMenusFor", lambda m: '''function getAppleMenuItems() {
    const front = activeWindowId && openWindows[activeWindowId] ? appConfig[openWindows[activeWindowId].appId]?.title : null;
    return [
        { label: 'About This Mac', action: () => openAboutThisMacModal() },
        { separator: true },
        { label: 'System Settings…', action: () => launchOrFocusApp('settings') },
        { label: 'App Store…', action: () => launchOrFocusApp('clicker-game') },
        { separator: true },
        {
            label: 'Recent Items',
            submenu: () => ['file-explorer', 'web-browser', 'notepad', 'terminal', 'calendar-app'].filter(id => appConfig[id]).map(id => ({ label: appConfig[id].title, action: () => launchOrFocusApp(id) }))
        },
        { separator: true },
        { label: front ? `Force Quit ${front}` : 'Force Quit…', shortcut: '⌥⌘⎋', action: () => openForceQuitModal() },
        { separator: true },
        { label: 'Sleep', action: () => lockScreen() },
        { label: 'Restart…', action: () => location.reload() },
        { label: 'Shut Down…', action: () => lockScreen() },
        { separator: true },
        { label: 'Lock Screen', shortcut: '⌃⌘Q', action: () => lockScreen() },
        { label: `Log Out ${currentUsername || 'User'}…`, shortcut: '⇧⌘Q', action: () => lockScreen() }
    ];
}

function getAppMenusFor''')

# ---- Per-app menu bars (real macOS menu titles; unwired commands are shown disabled, as macOS does) ----
rsub(r"function getAppMenusFor\(appId\) \{.*?\n\}\n\nfunction updateTopAppMenuBar", lambda m: '''const APP_MENU_TITLES = {
    'file-explorer': ['File', 'Edit', 'View', 'Go', 'Window', 'Help'],
    'web-browser': ['File', 'Edit', 'View', 'History', 'Bookmarks', 'Window', 'Help'],
    'terminal': ['Shell', 'Edit', 'View', 'Window', 'Help'],
    'notepad': ['File', 'Edit', 'Format', 'View', 'Window', 'Help'],
    'calculator': ['File', 'Edit', 'View', 'Window', 'Help'],
    'system-monitor': ['File', 'Edit', 'View', 'Window', 'Help'],
    '*': ['File', 'Edit', 'View', 'Window', 'Help']
};
function getAppMenusFor(appId) {
    const cfg = appConfig[appId];
    const appTitle = cfg ? cfg.title : 'Finder';
    const targetAppId = cfg ? appId : 'file-explorer';
    const hasWin = !!activeWindowId;
    const run = (fn) => () => { if (activeWindowId) fn(activeWindowId); };
    const sameApp = () => Object.keys(openWindows).filter(id => openWindows[id].appId === targetAppId);
    const D = (label, shortcut) => ({ label, shortcut, disabled: true });
    const defs = {
        File: [
            { label: targetAppId === 'file-explorer' ? 'New Finder Window' : `New ${appTitle} Window`, shortcut: '⌘N', action: () => createWindow(targetAppId, { forceNew: true }) },
            { separator: true },
            ...(targetAppId === 'notepad' ? [{ label: 'New Note', shortcut: '⌘N', action: () => launchOrFocusApp('notepad') }, { separator: true }] : []),
            { label: 'Close Window', shortcut: '⌘W', disabled: !hasWin, action: run(closeWindow) },
            D('Print…', '⌘P')
        ],
        Shell: [{ label: 'New Window', shortcut: '⌘N', action: () => createWindow('terminal', { forceNew: true }) }, { separator: true }, { label: 'Close Window', shortcut: '⌘W', disabled: !hasWin, action: run(closeWindow) }],
        Edit: [D('Undo', '⌘Z'), D('Redo', '⇧⌘Z'), { separator: true },
            { label: 'Cut', shortcut: '⌘X', action: () => document.execCommand('cut') }, { label: 'Copy', shortcut: '⌘C', action: () => document.execCommand('copy') },
            { label: 'Paste', shortcut: '⌘V', disabled: true }, { label: 'Select All', shortcut: '⌘A', action: () => document.execCommand('selectAll') }],
        Format: [D('Font'), D('Text'), D('Table'), D('List')],
        View: [{ label: 'Enter Full Screen', shortcut: '⌃⌘F', disabled: !hasWin, action: run(toggleMaximizeWindow) }, { separator: true },
            { label: 'Change Wallpaper', action: () => changeWallpaperContext(true) }, { label: 'Switch Appearance', action: () => cycleTheme() }],
        Go: [{ label: 'Home', shortcut: '⇧⌘H', action: () => launchOrFocusApp('file-explorer', { initialPath: '/Users/eugene' }) },
            { label: 'Desktop', shortcut: '⇧⌘D', action: () => launchOrFocusApp('file-explorer', { initialPath: '/Users/eugene/Desktop' }) },
            { label: 'Documents', shortcut: '⇧⌘O', action: () => launchOrFocusApp('file-explorer', { initialPath: '/Users/eugene/Documents' }) },
            { label: 'Downloads', shortcut: '⌥⌘L', action: () => launchOrFocusApp('file-explorer', { initialPath: '/Users/eugene/Downloads' }) },
            { label: 'Applications', shortcut: '⇧⌘A', action: () => launchOrFocusApp('file-explorer', { initialPath: '/Applications' }) }],
        History: [D('Back', '⌘['), D('Forward', '⌘]'), { separator: true }, D('Show All History', '⌘Y')],
        Bookmarks: [D('Show Bookmarks', '⌥⌘B'), D('Add Bookmark…', '⌘D')],
        Window: [
            { label: 'Minimize', shortcut: '⌘M', disabled: !hasWin, action: run(minimizeWindow) },
            { label: 'Zoom', disabled: !hasWin, action: run(toggleMaximizeWindow) },
            { label: 'Move & Resize', disabled: !hasWin, submenu: () => [['Left', 'left'], ['Right', 'right'], ['Top', 'top'], ['Bottom', 'bottom']].map(([l, d]) => ({ label: l, action: run(id => tileWindow(id, d)) })) },
            { separator: true },
            { label: 'Move to Desktop', disabled: !hasWin, submenu: () => virtualDesktops.map(d => ({ label: `Desktop ${d}`, action: run(id => moveWindowToSpace(id, d)) })) },
            { separator: true },
            { label: 'Bring All to Front', action: () => showDesktop(false) }
        ],
        Help: [{ label: 'Search', action: () => toggleSpotlight(true) }, { separator: true }, { label: `${appTitle} Help`, disabled: true }]
    };
    const titles = APP_MENU_TITLES[targetAppId] || APP_MENU_TITLES['*'];
    return [
        { key: 'app', label: appTitle, bold: true, items: [
            { label: `About ${appTitle}`, disabled: true }, { separator: true },
            { label: 'Settings…', shortcut: '⌘,', action: () => launchOrFocusApp('settings') }, { separator: true },
            { label: `Hide ${appTitle}`, shortcut: '⌘H', action: () => sameApp().forEach(id => { openWindows[id].isHidden = true; openWindows[id].element.style.display = 'none'; }) },
            { label: 'Show All', action: () => Object.values(openWindows).forEach(w => { w.isHidden = false; if (!w.isMinimized && w.element) w.element.style.display = 'flex'; }) }, { separator: true },
            { label: `Quit ${appTitle}`, shortcut: '⌘Q', action: () => sameApp().forEach(id => closeWindow(id)) }
        ] },
        ...titles.map(t => ({ key: t.toLowerCase(), label: t, items: defs[t] || [] }))
    ];
}

function updateTopAppMenuBar''')

# ---- About This Mac: honest, real window, no fake hardware ----
rsub(r"function openAboutThisMacModal\(\) \{.*?\n\}\n\n// Force Quit", lambda m: '''function openAboutThisMacModal() {
    document.getElementById('about-mac-modal')?.remove();
    const cores = navigator.hardwareConcurrency ? `${navigator.hardwareConcurrency}-core` : 'Unavailable';
    const mem = navigator.deviceMemory ? `${navigator.deviceMemory}${navigator.deviceMemory >= 8 ? '+' : ''} GB` : 'Unavailable';
    const plat = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || 'Web';
    const modal = document.createElement('div');
    modal.id = 'about-mac-modal';
    modal.className = 'about-win';
    modal.setAttribute('role', 'dialog'); modal.setAttribute('aria-label', 'About This Mac');
    modal.innerHTML = `
        <div class="about-title"><button class="tl-btn tl-close" aria-label="Close" onclick="document.getElementById('about-mac-modal').remove()"><svg viewBox="0 0 8 8" aria-hidden="true"><path d="M1.6 1.6l4.8 4.8M6.4 1.6L1.6 6.4"/></svg></button></div>
        <svg class="about-hero" viewBox="0 0 120 84" aria-hidden="true"><defs><linearGradient id="abS" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3f77d6"/><stop offset="1" stop-color="#1b2a58"/></linearGradient></defs>
            <rect x="14" y="4" width="92" height="62" rx="6" fill="#2a2c33" stroke="#9aa0ab" stroke-width="1.5"/><rect x="19" y="9" width="82" height="52" rx="2.5" fill="url(#abS)"/>
            <path d="M4 70h112l-6 8a4 4 0 0 1-3 1.5H13a4 4 0 0 1-3-1.5z" fill="#c9cdd5"/></svg>
        <div class="about-name">OSWeb</div>
        <div class="about-sub">Sequoia-style desktop</div>
        <dl class="about-rows">
            <dt>Processor</dt><dd>${escapeHtml(cores)}</dd>
            <dt>Memory</dt><dd>${escapeHtml(mem)}</dd>
            <dt>Platform</dt><dd>${escapeHtml(plat)}</dd>
            <dt>Version</dt><dd>OSWeb 0.2</dd>
        </dl>
        <button class="mac-btn-secondary about-more" onclick="document.getElementById('about-mac-modal').remove(); launchOrFocusApp('settings');">More Info…</button>`;
    document.getElementById('macos-viewport-root').appendChild(modal);
}

// Force Quit''')

open(p, 'w', encoding='utf-8').write(s)
print('ok')
