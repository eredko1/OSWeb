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

# ---- Safari: address parser (URL vs search), scheme allow-list, per-tab history, same-origin isolation ----
sub('''    const hist = [tabs[0].url]; let hi = 0;
    const loadUrl = (raw) => {
        let u = String(raw || '').trim();
        if (!u) return;
        if (u.startsWith('/')) u = 'vfs://' + u;
        activeTab().url = u;
        hist.length = hi + 1; hist.push(u); hi = hist.length - 1;
        renderViewport();
    };''', '''    // Address bar: URL or search. Only http(s)/vfs/wiki/start schemes are loadable; everything else is a search.
    const resolveAddress = (raw) => {
        const u = String(raw || '').trim(); if (!u) return '';
        if (u.startsWith('/')) return 'vfs://' + u;
        const m = u.match(/^([a-z][a-z0-9+.-]*):/i);
        if (m) {
            const sch = m[1].toLowerCase();
            if (['http', 'https', 'vfs', 'wiki', 'start'].includes(sch)) return u;
            if (!/\\s/.test(u) && /^[\\w.-]+:\\d+(\\/|$)/.test(u)) return 'https://' + u;       // host:port
            return 'https://duckduckgo.com/?q=' + encodeURIComponent(u);                  // javascript:, data:, etc. are never navigated
        }
        if (/\\s/.test(u) || (!/\\./.test(u) && !/^localhost(:|\\/|$)/i.test(u))) return 'https://duckduckgo.com/?q=' + encodeURIComponent(u);
        return 'https://' + u;
    };
    const loadUrl = (raw) => {
        const u = resolveAddress(raw); if (!u) return;
        const t = activeTab(); const h = t.hist || (t.hist = [t.url]); if (t.hi == null) t.hi = h.length - 1;
        t.url = u; h.length = t.hi + 1; h.push(u); t.hi = h.length - 1;
        renderViewport();
    };''')
sub('''    winEl.querySelector('[data-role="nav-back"]').onclick = () => { if (hi > 0) { hi--; activeTab().url = hist[hi]; renderViewport(); } };
    winEl.querySelector('[data-role="nav-fwd"]').onclick = () => { if (hi < hist.length - 1) { hi++; activeTab().url = hist[hi]; renderViewport(); } };''', '''    const step = (d) => { const t = activeTab(); const h = t.hist || (t.hist = [t.url]); if (t.hi == null) t.hi = h.length - 1; const n = t.hi + d; if (n >= 0 && n < h.length) { t.hi = n; t.url = h[n]; renderViewport(); } };
    winEl.querySelector('[data-role="nav-back"]').onclick = () => step(-1);
    winEl.querySelector('[data-role="nav-fwd"]').onclick = () => step(1);''')
sub('''<iframe src="${escapeHtml(safeUrl)}" class="flex-1 w-full border-0" sandbox="allow-scripts allow-same-origin allow-forms"></iframe>''',
    '''<iframe src="${escapeHtml(safeUrl)}" class="flex-1 w-full border-0" sandbox="allow-scripts ${(() => { try { const o = new URL(safeUrl, location.href).origin; return (o === location.origin || o === 'null') ? '' : 'allow-same-origin'; } catch (_) { return ''; } })()} allow-forms"></iframe>''')

# ---- no invented real-person sender/quote ----
s = s.replace('Craig Federighi <craig@apple.com>', 'OSWeb Team <hello@osweb.invalid>').replace('Craig Federighi', 'OSWeb Team').replace('craig@apple.com', 'hello@osweb.invalid')

# ---- lock barrier ----
sub("function setLockedState(locked) {", "function isLocked() { const lm = document.getElementById('login-modal'); return !!lm && !lm.classList.contains('hidden'); }\nfunction setLockedState(locked) {")
sub("['top-panel', 'desktop-area', 'dock-wrapper', 'ios-status', 'ios-home', 'ios-indicator', 'right-sidebar']", "['top-panel', 'desktop-area', 'dock-wrapper', 'ios-status', 'ios-home', 'ios-indicator', 'right-sidebar', 'spotlight-overlay', 'launchpad-overlay', 'mission-control-overlay', 'force-quit-modal', 'custom-modal', 'about-mac-modal', 'app-switcher', 'os-menu-root', 'temp-message-container']")
sub("    if (locked) setTimeout(() => document.getElementById('username-input')?.focus(), 60);", "    if (locked) { lockPrevFocus = document.activeElement && document.activeElement !== document.body ? document.activeElement : lockPrevFocus; setTimeout(() => document.getElementById('username-input')?.focus(), 60); }\n    else if (lockPrevFocus && lockPrevFocus.isConnected) { try { lockPrevFocus.focus(); } catch (_) {} }")
sub("function isLocked() {", "let lockPrevFocus = null;\nfunction isLocked() {")
sub("    if (loginModal) loginModal.classList.remove('hidden');\n    setLockedState(true);", "    try { OS.menu.closeAll(); toggleSpotlight(false); toggleLaunchpad(false); toggleMissionControl(false); ['force-quit-modal', 'about-mac-modal', 'app-switcher'].forEach(id => document.getElementById(id)?.remove()); document.getElementById('custom-modal')?.classList.add('hidden'); } catch (_) {}\n    if (loginModal) loginModal.classList.remove('hidden');\n    setLockedState(true);")
sub("    window.addEventListener('keydown', (e) => { if (OS.menu.layers.length) menuKeyNav(e); }, true);", "    window.addEventListener('keydown', (e) => { if (isLocked()) return; if (OS.menu.layers.length) menuKeyNav(e); }, true);")
sub("    window.addEventListener('keydown', (e) => {\n        const key = (e.key || '').toLowerCase();", "    window.addEventListener('keydown', (e) => {\n        if (isLocked()) return;          // the lock screen swallows every shortcut\n        const key = (e.key || '').toLowerCase();")

# ---- modals: dialog semantics, focus trap, Esc, restore ----
sub("    modal.classList.remove('hidden');\n\n    const close = () => {\n        modal.classList.add('hidden');", "    modal.classList.remove('hidden');\n    modal.setAttribute('role', 'dialog'); modal.setAttribute('aria-modal', 'true'); modal.setAttribute('aria-label', title);\n    const release = trapFocus(modal);\n    const onEsc = (e) => { if (e.key === 'Escape') { e.stopPropagation(); cancelBtn.click(); } };\n    modal.addEventListener('keydown', onEsc);\n\n    const close = () => {\n        release(); modal.removeEventListener('keydown', onEsc);\n        modal.classList.add('hidden');")
sub("    modal.querySelector('#fq-confirm-btn').onclick = () => {", "    if (!modal.isConnected) document.body.appendChild(modal);\n    modal.setAttribute('role', 'dialog'); modal.setAttribute('aria-modal', 'true'); modal.setAttribute('aria-label', 'Force Quit Applications');\n    modal.querySelector('.tl-close')?.setAttribute('aria-label', 'Close');\n    const relFQ = trapFocus(modal);\n    modal.addEventListener('keydown', (e) => { if (e.key === 'Escape') { modal.remove(); relFQ(); } });\n    modal.querySelector('#fq-confirm-btn').onclick = () => {")
sub("<span class=\"text-[10px] font-mono opacity-60\">PID ${w.pid}</span>", "")

# ---- new window takes key focus ----
sub("    activeWindowId = windowId;\n    updateTopAppMenuBar(winData.appId);\n}", "    activeWindowId = windowId;\n    updateTopAppMenuBar(winData.appId);\n    if (!winData.element.contains(document.activeElement)) { winData.element.tabIndex = -1; try { winData.element.focus({ preventScroll: true }); } catch (_) {} }\n}")

# ---- menus restore focus to the control that had it ----
sub("        closeAll() {\n            this.layers.forEach(el => el.remove());", "        closeAll() {\n            const had = this.layers.length > 0;\n            this.layers.forEach(el => el.remove());")
sub("            const legacyCtx = document.getElementById('context-menu');\n            if (legacyCtx) legacyCtx.classList.add('hidden');\n        },", "            const legacyCtx = document.getElementById('context-menu');\n            if (legacyCtx) legacyCtx.classList.add('hidden');\n            if (had && OS._lastContentFocus && OS._lastContentFocus.isConnected) { try { OS._lastContentFocus.focus({ preventScroll: true }); } catch (_) {} }\n        },")
sub("function initKeyboardShortcuts() {\n", "function initKeyboardShortcuts() {\n    document.addEventListener('focusin', (e) => { if (e.target.closest && e.target.closest('.window-content')) OS._lastContentFocus = e.target; });\n")

# ---- Auto appearance follows the OS live ----
sub("function setLockedState(locked) {", '''function initAutoTheme() {
    const mq = matchMedia('(prefers-color-scheme: dark)');
    const auto = () => { try { return localStorage.getItem('osweb_theme_auto') === '1'; } catch (_) { return false; } };
    if (!initAutoTheme._on) { initAutoTheme._on = true; mq.addEventListener('change', () => { if (auto()) applyThemeByIndex(mq.matches ? 0 : 1); }); }
    if (auto()) applyThemeByIndex(mq.matches ? 0 : 1);
}
function setLockedState(locked) {''')
rsub(r"if \(localStorage\.getItem\('osweb_theme_auto'\) === '1'\) \{ const mq = matchMedia.*?\} \} catch \(_\) \{\}", lambda m: "initAutoTheme(); } catch (_) {}")
sub("applyThemeByIndex(m === 'light' ? 1 : (m === 'dark' ? 0 : (matchMedia('(prefers-color-scheme: dark)').matches ? 0 : 1))); renderPane();", "applyThemeByIndex(m === 'light' ? 1 : (m === 'dark' ? 0 : (matchMedia('(prefers-color-scheme: dark)').matches ? 0 : 1))); initAutoTheme(); renderPane();")

# ---- dragging a tiled window restores its pre-tile size ----
sub("let armed = !(winData && winData.isMaximized);", "let armed = !(winData && (winData.isMaximized || winData.preTileRect));")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
