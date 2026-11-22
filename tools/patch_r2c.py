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

# --- SF-Symbols-style icon helper (stroke glyphs on a 16px grid) ---
sub("function getTrashSVG() {", '''const SF_PATHS = {
    'chevron.left': 'M10 3L5 8l5 5', 'chevron.right': 'M6 3l5 5-5 5', 'arrow.up': 'M8 13V3M4 7l4-4 4 4',
    'square.grid.2x2': 'M2.5 2.5h4.5v4.5H2.5zM9 2.5h4.5v4.5H9zM2.5 9H7v4.5H2.5zM9 9h4.5v4.5H9z', 'list.bullet': 'M5.5 4h8M5.5 8h8M5.5 12h8M2.5 4h.01M2.5 8h.01M2.5 12h.01',
    'eye': 'M1.5 8S4 3.5 8 3.5 14.5 8 14.5 8 12 12.5 8 12.5 1.5 8 1.5 8zM8 10a2 2 0 1 0 0-4 2 2 0 0 0 0 4z',
    'folder.badge.plus': 'M2 4.5A1.5 1.5 0 0 1 3.5 3h2.6l1.4 1.5h5A1.5 1.5 0 0 1 14 6v5.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 11.5zM8 7.2v3.6M6.2 9h3.6',
    'doc.badge.plus': 'M4 2h5l3.5 3.5V13a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1zM8 7.5v4M6 9.5h4',
    'magnifyingglass': 'M7 11.5a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9zM10.3 10.3L14 14', 'house': 'M2 8l6-5.5L14 8M3.5 7v6h3.2V9.5h2.6V13h3.2V7',
    'desktopcomputer': 'M2 3h12v8H2zM6 14h4M8 11v3', 'doc': 'M4 2h5l3.5 3.5V13a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1zM9 2v3.5h3.5',
    'chevron.left.forwardslash.chevron.right': 'M5 4L1.5 8 5 12M11 4l3.5 4L11 12M9.2 3l-2.4 10', 'photo': 'M2.5 3h11v10h-11zM2.5 11l3.5-3.5 3 3 2-2 2.5 2.5M10.5 6.2h.01',
    'music.note': 'M6 12V3.5l7-1.5V10.5M6 12a1.8 1.8 0 1 1-3.6 0A1.8 1.8 0 0 1 6 12zM13 10.5a1.8 1.8 0 1 1-3.6 0 1.8 1.8 0 0 1 3.6 0z',
    'arrow.down.circle': 'M8 14.5a6.5 6.5 0 1 0 0-13 6.5 6.5 0 0 0 0 13zM8 4.5v6M5.5 8.2L8 10.7l2.5-2.5', 'internaldrive': 'M2 9.5l1.7-5.2A1 1 0 0 1 4.6 3.5h6.8a1 1 0 0 1 .9.8L14 9.5v2.2a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1zM2 9.5h12M11.5 11.2h.01',
    'app': 'M8 2L3 12.5M8 2l5 10.5M4.4 9.5h7.2M2.5 12.5h.01'
};
function sf(name, size = 16, cls = '') {
    return `<svg class="sf ${cls}" viewBox="0 0 16 16" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${SF_PATHS[name] || ''}"/></svg>`;
}

function getTrashSVG() {''')

# --- Finder markup: sidebar full height + unified toolbar ---
side = lambda nav, icon, label: f'<button data-nav="{nav}" class="fx-side-item">${{sf(\'{icon}\')}}<span>{label}</span></button>'
rsub(r"function renderFinderContent\(\) \{.*?\n\}\n\nfunction initFinder", lambda m: '''function renderFinderContent() {
    return `
        <div class="fx-root">
            <aside class="fx-sidebar" aria-label="Sidebar">
                <div class="fx-side-head">Favorites</div>
                ''' + side('/Users/eugene', 'house', 'Home') + side('/Users/eugene/Desktop', 'desktopcomputer', 'Desktop') + side('/Users/eugene/Documents', 'doc', 'Documents')
                + side('/Users/eugene/Developer', 'chevron.left.forwardslash.chevron.right', 'Developer') + side('/Users/eugene/Pictures', 'photo', 'Pictures') + side('/Users/eugene/Music', 'music.note', 'Music')
                + side('/Users/eugene/Downloads', 'arrow.down.circle', 'Downloads') + '''
                <div class="fx-side-head">Locations</div>
                ''' + side('/', 'internaldrive', 'Macintosh HD') + side('/Applications', 'app', 'Applications') + '''
            </aside>
            <section class="fx-main">
                <div class="fx-toolbar">
                    <button data-role="back-btn" class="fx-tb" title="Back" aria-label="Back">${sf('chevron.left')}</button>
                    <button data-role="up-btn" class="fx-tb" title="Enclosing Folder" aria-label="Enclosing Folder">${sf('arrow.up')}</button>
                    <span data-role="current-folder-name" class="fx-title">eugene</span>
                    <span class="fx-spacer"></span>
                    <div class="fx-seg" role="group" aria-label="View">
                        <button data-role="view-grid" class="fx-seg-btn on" title="as Icons" aria-label="as Icons">${sf('square.grid.2x2')}</button>
                        <button data-role="view-list" class="fx-seg-btn" title="as List" aria-label="as List">${sf('list.bullet')}</button>
                    </div>
                    <button data-role="quicklook-btn" class="fx-tb" title="Quick Look" aria-label="Quick Look">${sf('eye')}</button>
                    <button data-role="new-folder-btn" class="fx-tb" title="New Folder" aria-label="New Folder">${sf('folder.badge.plus')}</button>
                    <button data-role="new-file-btn" class="fx-tb" title="New File" aria-label="New File">${sf('doc.badge.plus')}</button>
                    <label class="fx-search">${sf('magnifyingglass', 12)}<input data-role="search-input" type="search" placeholder="Search" aria-label="Search" /></label>
                </div>
                <div class="fx-body">
                    <div data-role="items-container" class="fx-items"></div>
                    <div data-role="quicklook-pane" class="fx-ql hidden flex-col"></div>
                </div>
                <div class="fx-path">
                    <div data-role="path-breadcrumbs" class="fx-crumbs"></div>
                    <div data-role="status-count" class="fx-status"></div>
                </div>
            </section>
        </div>
    `;
}

function initFinder''')
sub("gridBtn.className = 'px-2.5 py-1 bg-sky-500 text-white';\n        listBtn.className = 'px-2.5 py-1 bg-[var(--surface-overlay-bg)]';", "gridBtn.className = 'fx-seg-btn on';\n        listBtn.className = 'fx-seg-btn';")
sub("listBtn.className = 'px-2.5 py-1 bg-sky-500 text-white';\n        gridBtn.className = 'px-2.5 py-1 bg-[var(--surface-overlay-bg)]';", "listBtn.className = 'fx-seg-btn on';\n        gridBtn.className = 'fx-seg-btn';")
sub("btn.classList.toggle('bg-sky-500/25', btn.dataset.nav === state.cwd);\n            btn.classList.toggle('font-semibold', btn.dataset.nav === state.cwd);", "btn.classList.toggle('sel', btn.dataset.nav === state.cwd);")

# --- unified windows ---
sub("    winEl.dataset.app = appId;", "    winEl.dataset.app = appId;\n    if (config.unified) winEl.classList.add('unified');")
sub("    'file-explorer': {\n        title: 'Finder',", "    'file-explorer': {\n        unified: true,\n        title: 'Finder',")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
