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

sub("    'square.and.pencil':", """    'square.and.arrow.up': 'M8 10V2M5 4.8L8 2l3 2.8M4.5 7H4a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V8a1 1 0 0 0-1-1h-.5',
    'plus': 'M8 3v10M3 8h10', 'lock': 'M4.5 7.5V5.5a3.5 3.5 0 0 1 7 0v2M3.5 7.5h9v6h-9z', 'rectangle.on.rectangle': 'M5.5 5.5h8v8h-8zM2.5 10.5v-8h8', 'arrow.clockwise': 'M13 8a5 5 0 1 1-1.6-3.7M13 2.5v3h-3',
    'square.and.pencil':""")

# ---- Safari: unified toolbar, centred address pill, tab bar only when needed ----
rsub(r"function renderBrowserContent\(isChrome = false\) \{.*?\n\}\n\nfunction initBrowser", lambda m: '''function renderBrowserContent(isChrome = false) {
    return `
        <div class="sf-root">
            <div class="sf-toolbar">
                <button class="fx-tb" data-role="nav-home" title="Start Page" aria-label="Show sidebar">${sf('sidebar.left')}</button>
                <button class="fx-tb" data-role="nav-back" title="Back" aria-label="Back">${sf('chevron.left')}</button>
                <button class="fx-tb" data-role="nav-fwd" title="Forward" aria-label="Forward">${sf('chevron.right')}</button>
                <span class="fx-spacer"></span>
                <label class="sf-pill">${sf('lock', 11)}<input data-role="url-input" type="text" placeholder="Search or enter website name" aria-label="Address and search" spellcheck="false" autocomplete="off"/><button class="sf-reload" data-role="nav-reload" title="Reload" aria-label="Reload">${sf('arrow.clockwise', 12)}</button></label>
                <span class="fx-spacer"></span>
                <button class="fx-tb sf-hide-phone" data-role="ext-btn" title="Share" aria-label="Share">${sf('square.and.arrow.up')}</button>
                <button class="fx-tb" data-role="new-tab-btn" title="New Tab" aria-label="New Tab">${sf('plus')}</button>
                <button hidden data-role="go-btn"></button><button hidden data-role="devtools-btn"></button>
            </div>
            <div class="sf-tabs" data-role="tabs-bar"><div data-role="tabs-list" class="sf-tabs-list"></div></div>
            <div class="sf-view">
                <div data-role="browser-viewport" class="sf-viewport"></div>
                <div data-role="devtools-drawer" class="hidden"><div data-role="devtools-log"></div></div>
            </div>
        </div>
    `;
}

function initBrowser''')
rsub(r"        tabsList\.innerHTML = tabs\.map\(t => `\s*<div class=\"flex items-center gap-2 px-3 py-1 rounded-t-lg.*?`\)\.join\(''\);", lambda m: '''        winEl.querySelector('[data-role="tabs-bar"]').style.display = tabs.length > 1 ? '' : 'none';
        tabsList.innerHTML = tabs.map(t => `
            <div class="sf-tab${t.id === activeTabId ? ' on' : ''}" data-tab="${t.id}" role="tab" aria-selected="${t.id === activeTabId}">
                ${tabs.length > 1 ? `<button data-close-tab="${t.id}" class="sf-tab-x" aria-label="Close Tab">${sf('plus', 9)}</button>` : ''}
                <span class="sf-tab-t">${escapeHtml(t.title)}</span>
            </div>
        `).join('');''')

# Start page: Favorites squircles + Privacy line (no emoji, no "100% Secure")
rsub(r"            viewport\.innerHTML = `\s*<div class=\"p-6 max-w-2xl mx-auto\">\s*<div class=\"text-center mb-6\">.*?\n            `;\n            viewport\.querySelectorAll\('\[data-quick\]'\)", lambda m: '''viewport.innerHTML = `
                <div class="sf-start">
                    <h2>Favorites</h2>
                    <div class="sf-favs">
                        ${[['vfs:///Users/eugene/Developer/synth_webapp.html', 'Synth', '#5e5ce6', 'M'], ['wiki://macOS_Sequoia', 'macOS', '#0a84ff', 'W'], ['vfs:///Users/eugene/Desktop/Project Roadmap.md', 'Roadmap', '#30d158', 'R'], ['https://duckduckgo.com', 'DuckDuckGo', '#ff9f0a', 'D']].map(([u, n, c, l]) => `
                            <button class="sf-fav" data-quick="${u}"><span style="background:${c}">${l}</span><em>${n}</em></button>`).join('')}
                    </div>
                    <h2>Privacy Report</h2>
                    <div class="sf-priv">${sf('lock', 18)}<div><b>Pages open in a private sandbox</b><small>Sites you visit here can't see the rest of your files.</small></div></div>
                </div>
            `;
            viewport.querySelectorAll('[data-quick]')''')
# back/forward history inside loadUrl
sub("        activeTab().url = u;\n        renderViewport();\n    };\n\n    windowData.loadUrl = loadUrl;", "        activeTab().url = u;\n        hist.length = hi + 1; hist.push(u); hi = hist.length - 1;\n        renderViewport();\n    };\n\n    windowData.loadUrl = loadUrl;")
sub("    const loadUrl = (raw) => {", "    const hist = []; let hi = -1;\n    const loadUrl = (raw) => {")
sub("    winEl.querySelector('[data-role=\"nav-home\"]').onclick = () => loadUrl('start://home');", "    winEl.querySelector('[data-role=\"nav-home\"]').onclick = () => loadUrl('start://home');\n    winEl.querySelector('[data-role=\"nav-back\"]').onclick = () => { if (hi > 0) { hi--; activeTab().url = hist[hi]; renderViewport(); } };\n    winEl.querySelector('[data-role=\"nav-fwd\"]').onclick = () => { if (hi < hist.length - 1) { hi++; activeTab().url = hist[hi]; renderViewport(); } };")
sub("    'web-browser': {\n", "    'web-browser': {\n        unified: true,\n")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
