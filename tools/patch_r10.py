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

# ---------- lock screen markup ----------
rsub(r'        <div class="lock-bottom">.*?\n        </div>\n    </div>\n</div>', lambda m: '''        <div class="lock-bottom">
            <div class="lock-avatar" aria-hidden="true"><span id="lockscreen-initial">U</span></div>
            <div id="lockscreen-username" class="lock-name">User</div>

            <div id="lock-open" class="lock-open">
                <button id="lock-continue" class="lock-big" type="button">Unlock</button>
                <div class="lock-hint">No passcode is set. Add one in Settings &gt; Lock Screen.</div>
            </div>

            <div id="lock-pin" class="lock-pin" hidden>
                <div id="lock-dots" class="lock-dots" role="img" aria-label="Passcode entry"></div>
                <div id="lock-msg" class="lock-msg" role="status" aria-live="polite">Enter Passcode</div>
                <div class="lock-keys" role="group" aria-label="Passcode keypad">
                    <button type="button" class="lk" data-k="1">1</button><button type="button" class="lk" data-k="2">2</button><button type="button" class="lk" data-k="3">3</button>
                    <button type="button" class="lk" data-k="4">4</button><button type="button" class="lk" data-k="5">5</button><button type="button" class="lk" data-k="6">6</button>
                    <button type="button" class="lk" data-k="7">7</button><button type="button" class="lk" data-k="8">8</button><button type="button" class="lk" data-k="9">9</button>
                    <button type="button" class="lk lk-ghost" id="lock-faceid" aria-label="Unlock with Face ID or Touch ID" hidden><svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M4 8V6a2 2 0 0 1 2-2h2M16 4h2a2 2 0 0 1 2 2v2M20 16v2a2 2 0 0 1-2 2h-2M8 20H6a2 2 0 0 1-2-2v-2M9 10v1.5M15 10v1.5M12 10v3.5h-1M9 16c1.7 1.4 4.3 1.4 6 0"/></svg></button><span class="lk-gap" id="lock-gap"></span>
                    <button type="button" class="lk" data-k="0">0</button>
                    <button type="button" class="lk lk-ghost" id="lock-del" aria-label="Delete"><svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M21 5H9l-6 7 6 7h12a1 1 0 0 0 1-1V6a1 1 0 0 0-1-1zM15 9.5l5 5M20 9.5l-5 5"/></svg></button>
                </div>
            </div>

            <div class="lock-power">
                <button onclick="showTemporaryMessage('Sleep')" aria-label="Sleep"><span><i class="fas fa-moon"></i></span>Sleep</button>
                <button onclick="location.reload()" aria-label="Restart"><span><i class="fas fa-rotate-right"></i></span>Restart</button>
            </div>
        </div>
    </div>
</div>''')

# ---------- auth core: salted PBKDF2 passcode, lockout, optional platform passkey (Face ID / Touch ID) ----------
sub("OS.proxy = {", '''OS.auth = {
    ITER: 150000,
    get() { try { const v = JSON.parse(localStorage.getItem('osweb_auth') || 'null'); return v && v.hash && v.salt ? v : null; } catch (_) { return null; } },
    secure() { return !!(window.crypto && crypto.subtle); },
    async derive(pin, saltHex, iter) {
        const salt = Uint8Array.from(saltHex.match(/../g).map(h => parseInt(h, 16)));
        const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(pin), 'PBKDF2', false, ['deriveBits']);
        return Array.from(new Uint8Array(await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt, iterations: iter }, key, 256))).map(b => b.toString(16).padStart(2, '0')).join('');
    },
    async set(pin) {
        if (!this.secure()) throw new Error('A secure (https) page is required to store a passcode.');
        const salt = Array.from(crypto.getRandomValues(new Uint8Array(16))).map(b => b.toString(16).padStart(2, '0')).join('');
        const hash = await this.derive(pin, salt, this.ITER);
        localStorage.setItem('osweb_auth', JSON.stringify({ v: 1, salt, hash, len: pin.length, iter: this.ITER }));
        localStorage.removeItem('osweb_auth_fail');
    },
    async check(pin) { const a = this.get(); if (!a) return true; return (await this.derive(pin, a.salt, a.iter || this.ITER)) === a.hash; },
    clear() { localStorage.removeItem('osweb_auth'); localStorage.removeItem('osweb_auth_fail'); },
    // Brute-force slowdown: 5 wrong tries -> 30s, then doubling (stored so a reload doesn't reset it)
    lockout() { try { const f = JSON.parse(localStorage.getItem('osweb_auth_fail') || '{"n":0,"until":0}'); return { n: f.n || 0, until: f.until || 0 }; } catch (_) { return { n: 0, until: 0 }; } },
    fail() { const f = this.lockout(); f.n++; if (f.n >= 5) f.until = Date.now() + 30000 * Math.pow(2, Math.floor((f.n - 5) / 5)); localStorage.setItem('osweb_auth_fail', JSON.stringify(f)); return f; },
    ok() { localStorage.removeItem('osweb_auth_fail'); },
    autolockMin() { const v = localStorage.getItem('osweb_autolock'); return v == null ? 5 : Number(v); }
};
// Face ID / Touch ID through WebAuthn (platform authenticator). This is a convenience gate stored on this device
// (there is no server to verify against), so it is as strong as the device biometrics, not a substitute for account security.
OS.passkey = {
    id() { try { return localStorage.getItem('osweb_passkey') || ''; } catch (_) { return ''; } },
    supported() { return !!(window.PublicKeyCredential && navigator.credentials && (location.protocol === 'https:' || location.hostname === 'localhost')); },
    async available() { try { return this.supported() && await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable(); } catch (_) { return false; } },
    b64(buf) { return btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=+$/, ''); },
    unb64(s) { s = s.replace(/-/g, '+').replace(/_/g, '/'); const b = atob(s + '==='.slice((s.length + 3) % 4)); return Uint8Array.from(b, c => c.charCodeAt(0)); },
    async register(name) {
        const cred = await navigator.credentials.create({ publicKey: { challenge: crypto.getRandomValues(new Uint8Array(32)), rp: { name: 'OSWeb', id: location.hostname },
            user: { id: crypto.getRandomValues(new Uint8Array(16)), name: 'osweb-device', displayName: name || 'OSWeb' }, pubKeyCredParams: [{ type: 'public-key', alg: -7 }, { type: 'public-key', alg: -257 }],
            authenticatorSelection: { authenticatorAttachment: 'platform', userVerification: 'required', residentKey: 'preferred' }, timeout: 60000 } });
        localStorage.setItem('osweb_passkey', this.b64(cred.rawId));
    },
    async verify() {
        const id = this.id(); if (!id) return false;
        const a = await navigator.credentials.get({ publicKey: { challenge: crypto.getRandomValues(new Uint8Array(32)), rpId: location.hostname, userVerification: 'required', timeout: 60000,
            allowCredentials: [{ type: 'public-key', id: this.unb64(id), transports: ['internal'] }] } });
        return !!a;
    },
    clear() { localStorage.removeItem('osweb_passkey'); }
};
OS.proxy = {''')

# ---------- lock UI controller ----------
sub("function isLocked() {", '''/* ---- Lock screen controller ---- */
const lock = { buf: '', busy: false, tick: 0 };
function lockRender() {
    const a = OS.auth.get();
    document.getElementById('lock-open').hidden = !!a;
    document.getElementById('lock-pin').hidden = !a;
    const dots = document.getElementById('lock-dots');
    if (a) { dots.innerHTML = Array.from({ length: a.len }, (_, i) => `<i class="${i < lock.buf.length ? 'on' : ''}"></i>`).join(''); }
    const fid = document.getElementById('lock-faceid'), gap = document.getElementById('lock-gap');
    const hasKey = !!(a && OS.passkey.id() && OS.passkey.supported());
    fid.hidden = !hasKey; gap.hidden = hasKey;
    const lo = OS.auth.lockout(), msg = document.getElementById('lock-msg');
    const left = Math.ceil((lo.until - Date.now()) / 1000);
    document.querySelectorAll('.lk').forEach(k => { k.disabled = left > 0 && !k.classList.contains('lk-ghost'); });
    if (left > 0) { msg.textContent = `Try again in ${left}s`; clearTimeout(lock.tick); lock.tick = setTimeout(lockRender, 1000); }
    else if (a && msg.dataset.err !== '1') msg.textContent = 'Enter Passcode';
}
function lockShowError(text) {
    const pin = document.getElementById('lock-pin'), msg = document.getElementById('lock-msg');
    msg.textContent = text; msg.dataset.err = '1'; pin.classList.remove('shake'); void pin.offsetWidth; pin.classList.add('shake');
    try { navigator.vibrate && navigator.vibrate(120); } catch (_) {}
    setTimeout(() => { msg.dataset.err = ''; lockRender(); }, 1400);
}
async function lockPress(d) {
    const a = OS.auth.get(); if (!a || lock.busy) return;
    const lo = OS.auth.lockout(); if (lo.until > Date.now()) return;
    if (lock.buf.length >= a.len) return;
    lock.buf += d; lockRender();
    if (lock.buf.length === a.len) {
        lock.busy = true; const pin = lock.buf; let good = false;
        try { good = await OS.auth.check(pin); } catch (_) {}
        lock.busy = false; lock.buf = '';
        if (good) { OS.auth.ok(); unlockDesktop(); lockRender(); }
        else { const f = OS.auth.fail(); lockRender(); lockShowError(f.until > Date.now() ? 'Too many attempts' : 'Incorrect passcode'); }
    }
}
async function lockFaceId() {
    try { if (await OS.passkey.verify()) { lock.buf = ''; OS.auth.ok(); unlockDesktop(); } } catch (_) { lockShowError('Face ID was cancelled'); }
}
function initLockScreen() {
    document.getElementById('lock-continue').addEventListener('click', () => { if (!OS.auth.get()) unlockDesktop(); });
    document.querySelectorAll('.lk[data-k]').forEach(b => b.addEventListener('click', () => lockPress(b.dataset.k)));
    document.getElementById('lock-del').addEventListener('click', () => { lock.buf = lock.buf.slice(0, -1); lockRender(); });
    document.getElementById('lock-faceid').addEventListener('click', lockFaceId);
    window.addEventListener('keydown', (e) => {
        if (!isLocked()) return;
        if (!OS.auth.get()) { if (e.key === 'Enter') { e.preventDefault(); unlockDesktop(); } return; }
        if (/^[0-9]$/.test(e.key) && !e.metaKey && !e.ctrlKey) { e.preventDefault(); lockPress(e.key); }
        else if (e.key === 'Backspace') { e.preventDefault(); lock.buf = lock.buf.slice(0, -1); lockRender(); }
        else if (e.key === 'Escape') { lock.buf = ''; lockRender(); }
    });
    // Re-lock after the app has been in the background (only when a passcode is set)
    let hiddenAt = 0;
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) { hiddenAt = Date.now(); return; }
        const mins = OS.auth.autolockMin();
        if (hiddenAt && OS.auth.get() && !isLocked() && mins >= 0 && Date.now() - hiddenAt >= mins * 60000) lockScreen();
        hiddenAt = 0;
    });
    lockRender();
}
function isLocked() {''')
sub("    initKeyboardShortcuts();\n    initSessionPersistence();", "    initKeyboardShortcuts();\n    initLockScreen();\n    initSessionPersistence();")
# opening the lock screen resets the entry state; never auto-focus a text field (no keyboard pop-up on touch)
sub("    if (locked) { lockPrevFocus = document.activeElement && document.activeElement !== document.body ? document.activeElement : lockPrevFocus; setTimeout(() => document.getElementById('username-input')?.focus(), 60); }",
    "    if (locked) { lockPrevFocus = document.activeElement && document.activeElement !== document.body ? document.activeElement : lockPrevFocus; lock.buf = ''; try { lockRender(); } catch (_) {} if (!window.matchMedia('(pointer: coarse)').matches) setTimeout(() => { const t = OS.auth.get() ? document.querySelector('.lk[data-k=\"5\"]') : document.getElementById('lock-continue'); t && t.focus({ preventScroll: true }); }, 60); }")
sub("    const userInput = document.getElementById('username-input');", "    const userInput = null;")
# the lock-screen name follows the stored display name
sub("window.addEventListener('keydown', (e) => { if (isLocked()) return; if (OS.menu.layers.length) menuKeyNav(e); }, true);", "window.addEventListener('keydown', (e) => { if (isLocked()) return; if (OS.menu.layers.length) menuKeyNav(e); }, true);")

# ---------- Settings: Lock Screen pane ----------
sub("    { id: 'web', label: 'Websites', color: '#30d158', icon: 'globe' },", "    { id: 'lock', label: 'Lock Screen', color: '#ff9f0a', icon: 'lock' },\n    { id: 'web', label: 'Websites', color: '#30d158', icon: 'globe' },")
sub("        } else if (activePane === 'web') {", '''        } else if (activePane === 'lock') {
            const a = OS.auth.get(), key = OS.passkey.id();
            const nm = currentUsername || 'User';
            paneEl.innerHTML = group(row('Name', `<input id="lk-name" class="st-input" value="${escapeHtml(nm)}" aria-label="Name" maxlength="40"/>`, 'Shown on the lock screen')) +
                group(
                    row('Passcode', a ? '<button class="mac-btn-secondary" id="lk-change">Change…</button> <button class="mac-btn-secondary" id="lk-off">Turn Off…</button>' : '<button class="action-button" id="lk-on">Turn On…</button>', a ? `${a.len}-digit passcode` : 'Required to unlock this desktop'),
                    ...(a ? [row('Require passcode', `<select id="lk-auto" class="st-input" aria-label="Require passcode"><option value="0">Immediately</option><option value="1">After 1 minute</option><option value="5">After 5 minutes</option><option value="15">After 15 minutes</option><option value="-1">Never</option></select>`, 'After the app has been in the background')] : [])) +
                `<div id="lk-faceid-group"></div><div id="lk-form"></div><p class="st-help" id="lk-msg">The passcode and Face ID / Touch ID unlock this desktop on this device. They are stored in this browser, so they keep people out of your session but are not a replacement for an account login.</p>`;
            const msg = t => { paneEl.querySelector('#lk-msg').textContent = t; };
            const nameEl = paneEl.querySelector('#lk-name');
            nameEl.onchange = () => { const v = nameEl.value.trim() || 'User'; currentUsername = v; try { localStorage.setItem('osweb_username', v); } catch (_) {} document.getElementById('lockscreen-username').textContent = v; document.getElementById('lockscreen-initial').textContent = v.charAt(0).toUpperCase(); msg('Saved.'); };
            const autoSel = paneEl.querySelector('#lk-auto'); if (autoSel) { autoSel.value = String(OS.auth.autolockMin()); autoSel.onchange = () => localStorage.setItem('osweb_autolock', autoSel.value); }
            const form = paneEl.querySelector('#lk-form');
            const pinForm = (title, needCurrent, done) => {
                form.innerHTML = group(
                    ...(needCurrent ? [row('Current passcode', '<input id="pf-cur" class="st-input" type="password" inputmode="numeric" pattern="[0-9]*" autocomplete="off" maxlength="6" aria-label="Current passcode"/>')] : []),
                    ...(done.set ? [row('New passcode', '<input id="pf-new" class="st-input" type="password" inputmode="numeric" pattern="[0-9]*" autocomplete="new-password" maxlength="6" aria-label="New passcode"/>', '4 to 6 digits'), row('Verify', '<input id="pf-ver" class="st-input" type="password" inputmode="numeric" pattern="[0-9]*" autocomplete="new-password" maxlength="6" aria-label="Verify passcode"/>')] : []),
                    row('', `<button class="mac-btn-secondary" id="pf-cancel">Cancel</button> <button class="action-button" id="pf-ok">${title}</button>`));
                form.querySelector('#pf-cancel').onclick = () => { form.innerHTML = ''; };
                form.querySelector('#pf-ok').onclick = async () => {
                    try {
                        if (needCurrent && !(await OS.auth.check(form.querySelector('#pf-cur').value))) { msg('That passcode is incorrect.'); return; }
                        if (done.set) { const n = form.querySelector('#pf-new').value, v = form.querySelector('#pf-ver').value; if (!/^\\d{4,6}$/.test(n)) { msg('Use 4 to 6 digits.'); return; } if (n !== v) { msg('The passcodes do not match.'); return; } await OS.auth.set(n); msg('Passcode saved.'); }
                        else { OS.auth.clear(); OS.passkey.clear(); msg('Passcode turned off.'); }
                        renderPane();
                    } catch (e) { msg(e.message || 'Could not save.'); }
                };
                form.querySelector('input')?.focus();
            };
            paneEl.querySelector('#lk-on')?.addEventListener('click', () => pinForm('Turn On', false, { set: true }));
            paneEl.querySelector('#lk-change')?.addEventListener('click', () => pinForm('Change', true, { set: true }));
            paneEl.querySelector('#lk-off')?.addEventListener('click', () => pinForm('Turn Off', true, { set: false }));
            // Face ID / Touch ID row (only when a passcode exists, as the fallback, and the device supports it)
            OS.passkey.available().then(av => {
                const g = paneEl.querySelector('#lk-faceid-group'); if (!g) return;
                if (!av) { g.innerHTML = group(row('Face ID / Touch ID', '<span>Not available</span>', OS.passkey.supported() ? 'This device has no Face ID or Touch ID set up' : 'Needs an https page')); return; }
                g.innerHTML = group(row('Face ID / Touch ID', key ? '<button class="mac-btn-secondary" id="lk-fid-off">Remove</button>' : `<button class="mac-btn-secondary" id="lk-fid-on" ${a ? '' : 'disabled'}>Set Up…</button>`, a ? 'Unlock with your face or fingerprint' : 'Turn on a passcode first'));
                g.querySelector('#lk-fid-on')?.addEventListener('click', async () => { try { await OS.passkey.register(currentUsername); msg('Face ID / Touch ID is set up.'); renderPane(); } catch (e) { msg('Set up was cancelled or is not supported here.'); } });
                g.querySelector('#lk-fid-off')?.addEventListener('click', () => { OS.passkey.clear(); renderPane(); });
            });
        } else if (activePane === 'web') {''')
open(p, 'w', encoding='utf-8').write(s)
print('ok')
