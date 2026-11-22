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

sub("    'square.and.pencil':", """    'gearshape': 'M8 10.2a2.2 2.2 0 1 0 0-4.4 2.2 2.2 0 0 0 0 4.4zM8 1.5l1 1.6 1.9-.4.5 1.9 1.8.8-.8 1.8 1.1 1.6-1.4 1.4.1 1.9-1.9.3-.9 1.7-1.7-.9-1.7.9-.9-1.7-1.9-.3.1-1.9L1.7 9.3l1.1-1.6-.8-1.8 1.8-.8.5-1.9 1.9.4z',
    'circle.lefthalf': 'M8 14.5a6.5 6.5 0 1 0 0-13 6.5 6.5 0 0 0 0 13zM8 1.5v13',
    'dock.rectangle': 'M2 3h12v9H2zM4.5 10h7',
    'accessibility': 'M8 4.5a1.2 1.2 0 1 0 0-2.4 1.2 1.2 0 0 0 0 2.4zM3 5.8l5 1 5-1M8 6.8v3M6 14l2-4 2 4',
    'square.and.pencil':""")

rsub(r"function renderSettingsContent\(\) \{.*?\n\}\n\nfunction initSettings", lambda m: '''const SETTINGS_PANES = [
    { id: 'general', label: 'General', color: '#8e8e93', icon: 'gearshape' },
    { id: 'appearance', label: 'Appearance', color: '#0a84ff', icon: 'circle.lefthalf' },
    { id: 'wallpaper', label: 'Wallpaper', color: '#5e5ce6', icon: 'photo' },
    { id: 'dock', label: 'Desktop & Dock', color: '#32ade6', icon: 'dock.rectangle' },
    { id: 'accessibility', label: 'Accessibility', color: '#0a84ff', icon: 'accessibility' },
    { id: 'intelligence', label: 'Intelligence', color: '#ff453a', icon: 'sparkles' }
];
function renderSettingsContent() {
    const name = currentUsername || 'User';
    return `
        <div class="st-root" data-view="list">
            <aside class="st-side" aria-label="Settings">
                <label class="fx-search st-search">${sf('magnifyingglass', 12)}<input data-role="st-search" type="search" placeholder="Search" aria-label="Search settings"/></label>
                <div class="st-profile"><span class="st-avatar">${escapeHtml(name.trim().charAt(0).toUpperCase() || 'U')}</span><span><b>${escapeHtml(name)}</b><small>This device</small></span></div>
                <div class="st-list" role="listbox" aria-label="Settings panes">
                    ${SETTINGS_PANES.map(pn => `<button class="st-item" data-set-pane="${pn.id}" role="option"><span class="st-ico" style="background:${pn.color}">${sf(pn.icon, 14)}</span>${pn.label}</button>`).join('')}
                </div>
            </aside>
            <section class="st-detail">
                <div class="st-top"><button class="fx-tb st-back" data-role="st-back" aria-label="Settings">${sf('chevron.left')}<span>Settings</span></button><h1 data-role="st-title">General</h1></div>
                <div data-role="settings-pane" class="st-pane"></div>
            </section>
        </div>
    `;
}

function initSettings''')

rsub(r"function initSettings\(winEl\) \{.*?\n\}\n\n/\* ====", lambda m: '''function initSettings(winEl) {
    let activePane = 'general';
    const root = winEl.querySelector('.st-root');
    const paneEl = winEl.querySelector('[data-role="settings-pane"]');
    const titleEl = winEl.querySelector('[data-role="st-title"]');
    const sw = (id, on) => `<button class="st-switch${on ? ' on' : ''}" role="switch" aria-checked="${on}" id="${id}"><i></i></button>`;
    const row = (label, ctrl, sub = '') => `<div class="st-row"><div class="st-lbl">${label}${sub ? `<small>${sub}</small>` : ''}</div><div class="st-ctl">${ctrl}</div></div>`;
    const group = (...rows) => `<div class="st-group">${rows.join('')}</div>`;
    const bindSwitch = (id, fn) => { const el = paneEl.querySelector('#' + id); if (el) el.onclick = () => { const on = !el.classList.contains('on'); el.classList.toggle('on', on); el.setAttribute('aria-checked', String(on)); fn(on); }; };
    const isAuto = () => { try { return localStorage.getItem('osweb_theme_auto') === '1'; } catch (_) { return false; } };

    const renderPane = () => {
        titleEl.textContent = SETTINGS_PANES.find(x => x.id === activePane).label;
        winEl.querySelectorAll('[data-set-pane]').forEach(b => { const on = b.dataset.setPane === activePane; b.classList.toggle('sel', on); b.setAttribute('aria-selected', String(on)); });
        if (activePane === 'general') {
            const h = OS.sys.heap();
            paneEl.innerHTML = group(
                row('Device', escapeHtml(OS.sys.platform()) + ' (web browser)'),
                row('Processor', escapeHtml(OS.sys.cpuLine())),
                row('Memory', escapeHtml(OS.sys.memLine())),
                row('Version', 'OSWeb 0.2')) + group(
                row('Files and folders', `${Object.keys(OS.vfs.tree).length} items`, 'Stored in this browser'),
                row('Erase All Content and Settings…', '<button class="mac-btn-secondary" id="factory-reset-btn">Erase…</button>'));
            paneEl.querySelector('#factory-reset-btn').onclick = () => showCustomModal({
                title: 'Erase All Content and Settings?', message: 'This removes every file, window layout and preference stored in this browser.', confirmText: 'Erase',
                onConfirm: () => { localStorage.clear(); indexedDB.deleteDatabase(OS.vfs.dbName); location.reload(); } });
        } else if (activePane === 'appearance') {
            const mode = isAuto() ? 'auto' : (document.body.classList.contains('light-mode') ? 'light' : 'dark');
            const tile = (id, label) => `<button class="st-appr${mode === id ? ' on' : ''}" data-mode="${id}" aria-pressed="${mode === id}"><span class="st-appr-t ${id}"></span><span>${label}</span></button>`;
            paneEl.innerHTML = `<div class="st-group st-apprs">${tile('light', 'Light')}${tile('dark', 'Dark')}${tile('auto', 'Auto')}</div>`;
            paneEl.querySelectorAll('[data-mode]').forEach(b => b.onclick = () => {
                const m = b.dataset.mode; try { localStorage.setItem('osweb_theme_auto', m === 'auto' ? '1' : '0'); } catch (_) {}
                applyThemeByIndex(m === 'light' ? 1 : (m === 'dark' ? 0 : (matchMedia('(prefers-color-scheme: dark)').matches ? 0 : 1))); renderPane();
            });
        } else if (activePane === 'wallpaper') {
            paneEl.innerHTML = `<div class="st-group st-walls">${wallpapers.map((w, i) => `<button class="st-wall${i === currentWallpaperIdx ? ' on' : ''}" data-wall-idx="${i}" aria-label="${escapeHtml(w.name)}"><span style="background-image:url('${w.url}')"></span><em>${escapeHtml(w.name)}</em></button>`).join('')}</div>` +
                group(row('Add Image…', '<button class="mac-btn-secondary" data-role="custom-wall-btn">Choose…</button>', 'Use an image address'));
            paneEl.querySelectorAll('[data-wall-idx]').forEach(el => el.onclick = () => { currentWallpaperIdx = Number(el.dataset.wallIdx); const w = wallpapers[currentWallpaperIdx]; applyWallpaper(w.auto && !document.body.classList.contains('light-mode') ? w.dark : w.url); renderPane(); });
            paneEl.querySelector('[data-role="custom-wall-btn"]').onclick = () => showCustomModal({ title: 'Add Image', message: 'Enter an image address (https or data URI):', showInput: true, inputPlaceholder: 'https://…', confirmText: 'Set Wallpaper', onConfirm: (url) => { if (url && url.trim()) applyWallpaper(url.trim()); } });
        } else if (activePane === 'dock') {
            const curSize = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--dock-base-size')) || 56;
            const widgetsOn = !document.getElementById('desktop-widgets-container')?.classList.contains('hidden');
            paneEl.innerHTML = group(row('Size', `<input id="set-dock-size" type="range" min="38" max="64" value="${curSize}" aria-label="Dock size"/>`)) + group(row('Show Widgets on Desktop', sw('sw-widgets', widgetsOn)));
            paneEl.querySelector('#set-dock-size').oninput = (e) => {
                const dock = document.getElementById('dock'); const n = (dock && dock.querySelectorAll('.dock-icon').length) || 16; const b = OS.viewport.getDesktopBounds();
                const maxFit = Math.max(34, Math.floor(((b.width || 1180) - 80 - (n - 1) * 4) / Math.max(1, n)));
                document.documentElement.style.setProperty('--dock-base-size', `${Math.min(Number(e.target.value) || 56, maxFit)}px`);
            };
            bindSwitch('sw-widgets', () => toggleDesktopWidgets());
        } else if (activePane === 'accessibility') {
            const rt = document.body.classList.contains('reduce-transparency');
            paneEl.innerHTML = group(row('Reduce transparency', sw('sw-rt', rt), 'Makes windows, the Dock and menus solid'));
            bindSwitch('sw-rt', (on) => { document.body.classList.toggle('reduce-transparency', on); try { localStorage.setItem('osweb_reduce_transparency', on ? '1' : '0'); } catch (_) {} });
        } else {
            paneEl.innerHTML = group(row('Assistant API key', '<input id="set-ai-key" type="password" placeholder="Optional" class="st-input" aria-label="Assistant API key"/>', 'Optional. Stored only in this browser.')) +
                group(row('', '<button class="action-button" id="save-ai-key">Save</button>'));
            paneEl.querySelector('#set-ai-key').value = OS.ai.getApiKey();
            paneEl.querySelector('#save-ai-key').onclick = () => { OS.ai.setApiKey(paneEl.querySelector('#set-ai-key').value); showTemporaryMessage('Saved.', 1500); };
        }
    };
    winEl.querySelectorAll('[data-set-pane]').forEach(btn => { btn.onclick = () => { activePane = btn.dataset.setPane; renderPane(); root.dataset.view = 'detail'; }; });
    winEl.querySelector('[data-role="st-back"]').onclick = () => { root.dataset.view = 'list'; };
    const search = winEl.querySelector('[data-role="st-search"]');
    search.oninput = () => { const q = search.value.trim().toLowerCase(); winEl.querySelectorAll('[data-set-pane]').forEach(b => { b.style.display = !q || b.textContent.toLowerCase().includes(q) ? '' : 'none'; }); };
    renderPane();
}

/* ====''')
sub("    'settings': {\n", "    'settings': {\n        unified: true,\n")
sub("    applyDefaultWallpaperForTheme();\n    setLockedState(true);\n", "    applyDefaultWallpaperForTheme();\n    setLockedState(true);\n    try { document.body.classList.toggle('reduce-transparency', localStorage.getItem('osweb_reduce_transparency') === '1'); if (localStorage.getItem('osweb_theme_auto') === '1') { const mq = matchMedia('(prefers-color-scheme: dark)'); applyThemeByIndex(mq.matches ? 0 : 1); mq.addEventListener('change', () => { if (localStorage.getItem('osweb_theme_auto') === '1') applyThemeByIndex(mq.matches ? 0 : 1); }); } } catch (_) {}\n")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
