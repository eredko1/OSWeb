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

# desktop: no preset folders; user's Desktop files laid out from the top-right with middle-ellipsis labels
rsub(r"    // Always include Macintosh HD \+ Developer folder.*?    const dynamicIcons = desktopEntries\.map\(\(node, idx\) => \{.*?\n    \}\);", lambda m: '''    const fixedIcons = [];
    const aw = (document.getElementById('desktop-area') || {}).clientWidth || 1200, ah = (document.getElementById('desktop-area') || {}).clientHeight || 700;
    const perCol = Math.max(1, Math.floor((ah - 24) / 94));
    const mid = (n, max = 14) => n.length <= max ? n : n.slice(0, Math.ceil((max - 1) * 0.6)) + '…' + n.slice(-Math.floor((max - 1) * 0.4));
    const dynamicIcons = desktopEntries.map((node, idx) => {
        const col = Math.floor(idx / perCol), row = idx % perCol;
        const ext = (node.name.split('.').pop() || '').toLowerCase();
        return {
            name: mid(node.name),
            full: node.name,
            path: node.path,
            isDir: node.type === 'dir',
            top: 14 + row * 94,
            left: aw - 94 - col * 98,
            art: node.type === 'dir' ? getMacFolderSVG() : getFileDocSVG(ext)
        };
    });''')
sub('''            <span>${escapeHtml(ic.name)}</span>
        </div>
    `).join('');''', '''            <span title="${escapeHtml(ic.full || ic.name)}">${escapeHtml(ic.name)}</span>
        </div>
    `).join('');''')
sub('<div id="my-files-folder" class="desktop-icon"', '<div id="my-files-folder" hidden class="desktop-icon"')

# lock screen / status bar: 12h clock without AM/PM (like macOS and iOS)
sub("if (lsTime) lsTime.textContent = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: false });", "if (lsTime) lsTime.textContent = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }).replace(/\\s?[AP]M/i, '');")
sub("const iosT = document.getElementById('ios-time'); if (iosT) iosT.textContent = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: false });", "const iosT = document.getElementById('ios-time'); if (iosT) iosT.textContent = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }).replace(/\\s?[AP]M/i, '');")

# Dock: no invented "Messages & AI" app; honest naming for the assistant
sub("    'web-browser',\n    'ai-assistant',\n    'mail-client',\n    'image-viewer',", "    'web-browser',\n    'mail-client',\n    'image-viewer',")
sub("const phoneDockApps = ['web-browser', 'ai-assistant', 'mail-client', 'notepad'];", "const phoneDockApps = ['web-browser', 'mail-client', 'notepad', 'settings'];")
sub("        title: 'Messages & AI',", "        title: 'Assistant',")
rsub(r"        'ai-assistant': `<svg viewBox=\"0 0 64 64\".*?</svg>`,", lambda m: '''        'ai-assistant': `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="aiBg2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5b5f6b"/><stop offset="1" stop-color="#2a2d36"/></linearGradient></defs>
            <rect x="4" y="4" width="56" height="56" rx="13" fill="url(#aiBg2)"/><path d="M32 14l4.2 11.8L48 30l-11.8 4.2L32 46l-4.2-11.8L16 30l11.8-4.2z" fill="#fff"/><path d="M47 40l1.6 4.4L53 46l-4.4 1.6L47 52l-1.6-4.4L41 46l4.4-1.6z" fill="#fff" opacity=".85"/></svg>`,''')
# proper Settings gear
rsub(r"        'settings': `<svg viewBox=\"0 0 64 64\".*?</svg>`,", lambda m: '''        'settings': `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="setBg2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b9bcc4"/><stop offset="1" stop-color="#6e717a"/></linearGradient><linearGradient id="gearG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f5f7"/><stop offset="1" stop-color="#9a9da6"/></linearGradient></defs>
            <rect x="4" y="4" width="56" height="56" rx="13" fill="url(#setBg2)"/>
            <g transform="translate(32 32)" fill="url(#gearG)"><circle r="14.5"/>${[0,45,90,135].map(a => `<rect x="-4.2" y="-21" width="8.4" height="42" rx="2.4" transform="rotate(${a})"/>`).join('')}</g>
            <circle cx="32" cy="32" r="6.5" fill="#5d6068"/><circle cx="32" cy="32" r="3.6" fill="#8b8e96"/></svg>`,''')

# Mail: honest sample labelling
sub("iCloud Mail • Connected", "Sample mailbox")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
