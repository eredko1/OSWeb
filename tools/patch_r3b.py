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

# extra SF symbols
sub("    'app': 'M8 2L3 12.5M8 2l5 10.5M4.4 9.5h7.2M2.5 12.5h.01'\n};", """    'app': 'M8 2L3 12.5M8 2l5 10.5M4.4 9.5h7.2M2.5 12.5h.01',
    'square.and.pencil': 'M7 3H3.5A1.5 1.5 0 0 0 2 4.5v8A1.5 1.5 0 0 0 3.5 14h8a1.5 1.5 0 0 0 1.5-1.5V9M12.2 2.3a1.4 1.4 0 0 1 2 2L8 10.5 5.5 11l.5-2.5z',
    'trash': 'M2.5 4.5h11M6 4.5V3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v1.5M4 4.5l.6 8.3a1 1 0 0 0 1 .9h4.8a1 1 0 0 0 1-.9l.6-8.3M6.8 7v4M9.2 7v4',
    'sparkles': 'M7 2.5l1.2 3.3 3.3 1.2-3.3 1.2L7 11.5 5.8 8.2 2.5 7l3.3-1.2zM12.2 10l.6 1.5 1.5.6-1.5.6-.6 1.5-.6-1.5-1.5-.6 1.5-.6z',
    'textformat': 'M2 12.5L6 3l4 9.5M3.4 9.5h5.2M11 12.5l2-5 2 5',
    'checklist': 'M2.5 4l1.2 1.2L5.8 3M2.5 9l1.2 1.2L5.8 8M8 4.5h6M8 9.5h6M2.8 13.5h.01M8 14h6',
    'sidebar.left': 'M2.5 3h11v10h-11zM6.2 3v10'
};""")

# ---- Notes markup ----
rsub(r"function renderNotepadContent\(\) \{.*?\n\}\n\nfunction initNotepad", lambda m: '''function renderNotepadContent() {
    return `
        <div class="nt-root" data-view="list">
            <aside class="nt-list" aria-label="Notes">
                <div class="nt-list-head"><h2>Notes</h2><span class="nt-count" data-role="notes-count"></span></div>
                <label class="nt-search">${sf('magnifyingglass', 12)}<input data-role="note-search" type="search" placeholder="Search" aria-label="Search notes"/></label>
                <div data-role="notes-list" class="nt-rows" role="listbox" aria-label="Notes"></div>
            </aside>
            <section class="nt-editor">
                <div class="nt-toolbar">
                    <button class="fx-tb nt-back" data-role="nt-back" aria-label="Notes" title="Notes">${sf('chevron.left')}<span>Notes</span></button>
                    <span class="fx-spacer"></span>
                    <button data-role="new-note-btn" class="fx-tb" title="New Note" aria-label="New Note">${sf('square.and.pencil')}</button>
                    <button data-role="delete-note" class="fx-tb" title="Delete" aria-label="Delete Note">${sf('trash')}</button>
                    <button data-role="toggle-preview" class="fx-tb" title="Formatted View" aria-label="Formatted View">${sf('textformat')}</button>
                    <button data-role="writing-tools" class="fx-tb" title="Writing Tools" aria-label="Writing Tools" aria-haspopup="menu">${sf('sparkles')}</button>
                </div>
                <div class="nt-date" data-role="note-stats"></div>
                <textarea data-role="note-textarea" placeholder="" aria-label="Note" class="nt-text"></textarea>
                <div data-role="note-preview" class="nt-preview hidden"></div>
                <span data-role="note-path" hidden></span>
                <button hidden data-role="ai-summarize" id="summarize-note-btn"></button><button hidden data-role="ai-title" id="suggest-title-btn"></button><button hidden data-role="ai-bullets"></button>
            </section>
        </div>
    `;
}

function initNotepad''')

# ---- Notes behaviour tweaks ----
sub("""        statsEl.textContent = `${words} words • ${text.length} chars • Synced to VFS`;""", """        statsEl.textContent = new Date().toLocaleString('en-US', { dateStyle: 'long', timeStyle: 'short' }).replace(',', '') ;""")
rsub(r"        listEl\.innerHTML = notes\.map\(n => `\s*<div class=\"p-2 rounded-xl.*?`\)\.join\(''\);", lambda m: '''        const cnt = winEl.querySelector('[data-role="notes-count"]'); if (cnt) cnt.textContent = `${notes.length} note${notes.length === 1 ? '' : 's'}`;
        listEl.innerHTML = notes.map(n => `
            <div class="nt-row${n.path === activePath ? ' sel' : ''}" data-note-path="${escapeHtml(n.path)}" role="option" aria-selected="${n.path === activePath}" tabindex="0">
                <div class="nt-row-title">${escapeHtml(n.name.replace(/\\.(md|txt)$/i, ''))}</div>
                <div class="nt-row-sub"><span>${escapeHtml((n.content || '').replace(/^#+\\s*.*\\n?/, '').replace(/[#*`]/g, '').trim().slice(0, 44) || 'No additional text')}</span></div>
            </div>
        `).join('');''')
sub("""        listEl.querySelectorAll('[data-note-path]').forEach(el => {
            el.onclick = () => openNote(el.dataset.notePath);
        });""", """        listEl.querySelectorAll('[data-note-path]').forEach(el => {
            el.onclick = () => { openNote(el.dataset.notePath); if (document.body.classList.contains('device-phone')) rootEl.dataset.view = 'edit'; };
            el.onkeydown = (e) => { if (e.key === 'Enter') el.click(); };
        });""")
sub("    const pathEl = winEl.querySelector('[data-role=\"note-path\"]');\n    const statsEl", "    const rootEl = winEl.querySelector('.nt-root');\n    winEl.querySelector('[data-role=\"nt-back\"]').onclick = () => { rootEl.dataset.view = 'list'; };\n    winEl.querySelector('[data-role=\"writing-tools\"]').onclick = (e) => {\n        const r = e.currentTarget.getBoundingClientRect(); const c = OS.viewport.toDesktopCoords(r.right - 200, r.bottom + 4);\n        OS.menu.open([{ label: 'Summarize', action: () => summarizeBtn.click() }, { label: 'Suggest Title', action: () => titleBtn.click() }, { label: 'Key Points', action: () => bulletsBtn.click() }], c.x, c.y, 0);\n    };\n    const pathEl = winEl.querySelector('[data-role=\"note-path\"]');\n    const statsEl")
sub("summarizeBtn.textContent = '✨ Summarizing...';", "")
sub("summarizeBtn.textContent = '✨ Summarize';", "")
sub("titleBtn.textContent = '✨ Suggesting...';", "")
sub("titleBtn.textContent = '✨ Suggest Title';", "")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
