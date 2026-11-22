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

# ---- proxy config + signing (HMAC-SHA256 via WebCrypto; secret never leaves the browser, signatures expire in 5 min) ----
sub("OS.perf = {", '''OS.proxy = {
    get() { try { return { url: localStorage.getItem('osweb_proxy_url') || '', secret: localStorage.getItem('osweb_proxy_secret') || '', on: localStorage.getItem('osweb_proxy_on') !== '0' }; } catch (_) { return { url: '', secret: '', on: false }; } },
    set(url, secret, on) { try { localStorage.setItem('osweb_proxy_url', (url || '').trim()); localStorage.setItem('osweb_proxy_secret', secret || ''); localStorage.setItem('osweb_proxy_on', on ? '1' : '0'); } catch (_) {} },
    configured() { const c = this.get(); return !!(c.url && c.secret && c.on); },
    async signedUrl(target) {
        const c = this.get(); const exp = Date.now() + 5 * 60 * 1000;
        const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(c.secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
        const sig = Array.from(new Uint8Array(await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(`${target}|${exp}`)))).map(b => b.toString(16).padStart(2, '0')).join('');
        const base = c.url.replace(/\\/+$/, '');
        return `${base}${base.includes('?') ? '&' : '?'}url=${encodeURIComponent(target)}&exp=${exp}&sig=${sig}`;
    }
};
OS.perf = {''')

# ---- Safari: route external sites through the proxy when configured ----
REPL_SAFARI = '''            const safeUrl = tab.url.startsWith('http') ? tab.url : `https://${tab.url}`;
            tab.title = safeUrl.replace(/^https?:\\/\\//, '').split('/')[0];
            const viaProxy = OS.proxy.configured() && /^https?:/i.test(safeUrl);
            const sandbox = (() => { try { const o = new URL(safeUrl, location.href).origin; return (o === location.origin || o === 'null') ? '' : 'allow-same-origin'; } catch (_) { return ''; } })();
            viewport.innerHTML = `
                <div class="flex flex-col h-full">
                    <div class="sf-banner">
                        <span>${viaProxy ? 'Loaded through your web proxy.' : 'Many sites refuse to be shown inside another page.'}${viaProxy ? '' : ' <a href="#" data-role="sf-setup">Set up a web proxy</a> to open them here.'}</span>
                        <a href="${escapeHtml(safeUrl)}" target="_blank" rel="noopener noreferrer">Open in new tab ↗</a>
                    </div>
                    <iframe data-role="sf-frame" class="flex-1 w-full border-0" referrerpolicy="no-referrer" sandbox="allow-scripts ${viaProxy ? '' : sandbox} allow-forms" ${viaProxy ? '' : `src="${escapeHtml(safeUrl)}"`}></iframe>
                </div>
            `;
            viewport.querySelector('[data-role="sf-setup"]')?.addEventListener('click', (e) => { e.preventDefault(); launchOrFocusApp('settings', { pane: 'web' }); });
            if (viaProxy) {
                const frame = viewport.querySelector('[data-role="sf-frame"]'); const want = tab.url;
                OS.proxy.signedUrl(safeUrl).then(u => { if (activeTab().url === want && frame.isConnected) frame.src = u; }).catch(() => { viewport.querySelector('.sf-banner span').textContent = 'Could not sign the proxy request (needs a secure page).'; });
            }
        }
'''
_i = s.index("            const safeUrl = tab.url.startsWith('http')")
_j = s.index("`;\n        }", _i) + len("`;\n        }")
s = s[:_i] + REPL_SAFARI.rstrip('\n') + s[_j:]
# links inside proxied pages navigate the tab (postMessage from the injected script), accepted only from this window's frame
sub("    windowData.loadUrl = loadUrl;", '''    windowData.loadUrl = loadUrl;
    window.addEventListener('message', (e) => {
        const f = viewport.querySelector('[data-role="sf-frame"]');
        if (!f || e.source !== f.contentWindow || !e.data || e.data.type !== 'osweb-nav') return;
        const u = String(e.data.url || ''); if (/^https?:\\/\\//i.test(u)) loadUrl(u);
    }, { signal: windowData?.abortController?.signal });''')

# ---- Settings: Websites pane ----
sub("    'globe':", "    'globe':") if "'globe':" in s else None
sub("    'square.and.pencil':", "    'globe': 'M8 14.5a6.5 6.5 0 1 0 0-13 6.5 6.5 0 0 0 0 13zM1.5 8h13M8 1.5c2 2 2.8 4 2.8 6.5S10 12.5 8 14.5M8 1.5C6 3.5 5.2 5.5 5.2 8S6 12.5 8 14.5',\n    'square.and.pencil':")
sub("    { id: 'accessibility', label: 'Accessibility', color: '#0a84ff', icon: 'accessibility' },", "    { id: 'accessibility', label: 'Accessibility', color: '#0a84ff', icon: 'accessibility' },\n    { id: 'web', label: 'Websites', color: '#30d158', icon: 'globe' },")
sub("        } else if (activePane === 'accessibility') {", '''        } else if (activePane === 'web') {
            const c = OS.proxy.get();
            paneEl.innerHTML = group(
                row('Use web proxy', sw('sw-proxy', c.on), 'Show sites that block embedding'),
                row('Proxy address', '<input id="px-url" class="st-input" style="width:240px" placeholder="https://your-proxy.vercel.app/api/p" aria-label="Proxy address"/>'),
                row('Secret', '<input id="px-secret" type="password" class="st-input" placeholder="Same as PROXY_SECRET" aria-label="Proxy secret"/>', 'Stored in this browser. Requests are signed, the secret is never sent.')) +
                group(row('', '<button class="mac-btn-secondary" id="px-test">Test</button> <button class="action-button" id="px-save">Save</button>')) +
                `<p class="st-help" id="px-msg">The proxy is a small server you run (see <code>proxy/README.md</code> in the repository). Without one, Safari can only show sites that allow embedding.</p>`;
            paneEl.querySelector('#px-url').value = c.url; paneEl.querySelector('#px-secret').value = c.secret;
            const msg = (t) => { paneEl.querySelector('#px-msg').textContent = t; };
            bindSwitch('sw-proxy', (on) => OS.proxy.set(paneEl.querySelector('#px-url').value, paneEl.querySelector('#px-secret').value, on));
            paneEl.querySelector('#px-save').onclick = () => { OS.proxy.set(paneEl.querySelector('#px-url').value, paneEl.querySelector('#px-secret').value, paneEl.querySelector('#sw-proxy').classList.contains('on')); msg('Saved.'); };
            paneEl.querySelector('#px-test').onclick = async () => {
                const url = paneEl.querySelector('#px-url').value.trim(); msg('Testing…');
                try { const r = await fetch(url + (url.includes('?') ? '&' : '?') + 'health=1'); const j = await r.json(); msg(j.ok ? (j.signed ? 'Proxy reachable and configured.' : 'Reachable, but PROXY_SECRET is not set on the server.') : 'Unexpected response.'); } catch (_) { msg('Could not reach the proxy (check the address, and that it allows this page).'); }
            };
        } else if (activePane === 'accessibility') {''')
sub("function initSettings(winEl) {\n    let activePane = 'general';", "function initSettings(winEl, windowData, opts) {\n    let activePane = (opts && SETTINGS_PANES.some(x => x.id === opts.pane)) ? opts.pane : 'general';")
sub("init: (winEl, winData, opts) => initSettings(winEl)", "init: (winEl, winData, opts) => initSettings(winEl, winData, opts)") if "init: (winEl, winData, opts) => initSettings(winEl)" in s else None
open(p, 'w', encoding='utf-8').write(s)
print('ok')
