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

# ---- real system facts (nothing invented) ----
sub("OS.store = {", '''OS.sys = {
    cores() { return navigator.hardwareConcurrency || null; },
    memGB() { return navigator.deviceMemory || null; },
    platform() { return (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || 'Web'; },
    heap() { const m = performance && performance.memory; return m ? { used: m.usedJSHeapSize, total: m.totalJSHeapSize, limit: m.jsHeapSizeLimit } : null; },
    memLine() { const g = this.memGB(); return g ? `${g}${g >= 8 ? '+' : ''} GB (browser-reported)` : 'Not exposed by this browser'; },
    cpuLine() { const c = this.cores(); return c ? `${c} logical processors` : 'Not exposed by this browser'; }
};
OS.store = {''')

# terminal: free / neofetch / banner
sub("return `Apple M3 Max Unified Memory: 64.0 GB Total | 14.2 GB Wired/Active | 49.8 GB Available`;", "{ const h = OS.sys.heap(); return `Memory: ${OS.sys.memLine()}` + (h ? `\\nJS heap: ${(h.used / 1048576).toFixed(1)} MB used of ${(h.limit / 1048576).toFixed(0)} MB limit` : ''); }")
sub("'               OMMM0,            Host: MacBook Pro (16-inch, M3 Max)',", "'               OMMM0,            Host: Web browser on ' + OS.sys.platform(),")
sub("':MMMMMMMMMMMMMMMMMMMMMMMM:       CPU: Apple M3 Max (16-core @ 4.05GHz)',", "':MMMMMMMMMMMMMMMMMMMMMMMM:       CPU: ' + OS.sys.cpuLine(),")
sub("'.MMMMMMMMMMMMMMMMMMMMMMMMX.      GPU: Apple M3 Max (40-core Metal 3)',", "'.MMMMMMMMMMMMMMMMMMMMMMMMX.      GPU: Not exposed by this browser',")
sub("' kMMMMMMMMMMMMMMMMMMMMMMMMWd.    Memory: 14540MiB / 65536MiB LPDDR5X',", "' kMMMMMMMMMMMMMMMMMMMMMMMMWd.    Memory: ' + OS.sys.memLine(),")
sub("'neofetch' for Apple M3 Max specs,", "'neofetch' for system info,")
sub("<div><strong>Model:</strong> MacBook Pro (16-inch, Apple M3 Max)</div>", "<div><strong>Device:</strong> ${escapeHtml(OS.sys.platform())} (web browser)</div><div><strong>Processor:</strong> ${escapeHtml(OS.sys.cpuLine())}</div><div><strong>Memory:</strong> ${escapeHtml(OS.sys.memLine())}</div>")
sub("Prepared on macOS Sequoia 15.1 (Apple M3 Max).", "Prepared in OSWeb.")
s = s.replace("Apple Intelligence (M3 Max Local Neural Engine):", "Assistant (local rules):")

# ---- Activity Monitor: honest, macOS-styled ----
rsub(r"function renderActivityMonitorContent\(\) \{.*?\n\}\n\nfunction initActivityMonitor\(winEl, windowData\) \{.*?\n\}\n\n// --- 8\.15 Preview", lambda m: '''function renderActivityMonitorContent() {
    return `
        <div class="am-root">
            <div class="am-toolbar">
                <button data-role="quit-proc-btn" class="fx-tb" title="Quit the selected process" aria-label="Quit Process">${sf('trash')}</button>
                <span class="fx-spacer"></span>
                <div class="fx-seg" role="tablist" aria-label="Category">
                    <button class="fx-seg-btn on am-tab" data-tab="cpu" role="tab" aria-selected="true" style="width:auto;padding:0 12px">CPU</button>
                    <button class="fx-seg-btn am-tab" data-tab="memory" role="tab" aria-selected="false" style="width:auto;padding:0 12px">Memory</button>
                </div>
                <span class="fx-spacer"></span>
                <label class="fx-search">${sf('magnifyingglass', 12)}<input data-role="proc-filter" type="search" placeholder="Search" aria-label="Search processes"/></label>
            </div>
            <div class="am-table-wrap">
                <table class="am-table">
                    <thead><tr><th>Process Name</th><th class="num" data-col="a">% CPU</th><th class="num">Threads</th><th class="num">PID</th><th>User</th></tr></thead>
                    <tbody data-role="proc-tbody"></tbody>
                </table>
            </div>
            <div class="am-foot" data-role="am-foot"></div>
        </div>
    `;
}

function initActivityMonitor(winEl, windowData) {
    let selectedPid = null, tab = 'cpu';
    const tbody = winEl.querySelector('[data-role="proc-tbody"]');
    const filterInput = winEl.querySelector('[data-role="proc-filter"]');
    const quitBtn = winEl.querySelector('[data-role="quit-proc-btn"]');
    const foot = winEl.querySelector('[data-role="am-foot"]');
    const mb = n => (n / 1048576).toFixed(1) + ' MB';

    // Processes are the real things that exist: the OSWeb page itself plus one entry per open app window.
    const procs = () => {
        const list = [{ name: 'OSWeb (this tab)', pid: 1, appId: 'system-monitor', protectedProc: true }];
        Object.values(openWindows).forEach(w => list.push({ name: appConfig[w.appId]?.title || w.appId, pid: w.pid, appId: w.appId, winId: w.id }));
        return list;
    };
    const renderTable = () => {
        const q = (filterInput.value || '').toLowerCase().trim();
        const rows = procs().filter(p => !q || p.name.toLowerCase().includes(q) || String(p.pid).includes(q));
        const h = OS.sys.heap();
        winEl.querySelector('th[data-col]').textContent = tab === 'cpu' ? '% CPU' : 'Memory';
        tbody.innerHTML = rows.map((p, i) => `
            <tr data-pid="${p.pid}" class="${p.pid === selectedPid ? 'sel' : (i % 2 ? 'alt' : '')}">
                <td><span class="am-ico">${getAppIconSVG(p.appId)}</span>${escapeHtml(p.name)}</td>
                <td class="num">${tab === 'cpu' ? '—' : (p.pid === 1 && h ? mb(h.used) : '—')}</td>
                <td class="num">—</td><td class="num">${p.pid}</td><td>${escapeHtml(currentUsername || 'user')}</td>
            </tr>`).join('');
        tbody.querySelectorAll('[data-pid]').forEach(row => { row.onclick = () => { selectedPid = Number(row.dataset.pid); renderTable(); }; });
        foot.innerHTML = tab === 'cpu'
            ? `<div><b>Logical processors</b><span>${OS.sys.cores() ?? 'Not exposed'}</span></div><div><b>Per-process CPU</b><span>Not available to web pages</span></div><div><b>Processes</b><span>${rows.length}</span></div>`
            : `<div><b>JS heap used</b><span>${h ? mb(h.used) : 'Not exposed by this browser'}</span></div><div><b>JS heap limit</b><span>${h ? mb(h.limit) : '—'}</span></div><div><b>Device memory</b><span>${OS.sys.memLine()}</span></div>`;
    };
    winEl.querySelectorAll('.am-tab').forEach(b => b.onclick = () => { tab = b.dataset.tab; winEl.querySelectorAll('.am-tab').forEach(x => { x.classList.toggle('on', x === b); x.setAttribute('aria-selected', String(x === b)); }); renderTable(); });
    quitBtn.onclick = () => {
        const p = procs().find(x => x.pid === selectedPid);
        if (!p) { showTemporaryMessage('Select a process first.', 1600); return; }
        if (p.protectedProc) { showTemporaryMessage('OSWeb itself cannot be quit from here.', 1800); return; }
        closeWindow(p.winId); selectedPid = null; renderTable();
    };
    filterInput.oninput = renderTable;
    const timer = setInterval(() => { if (!document.hidden) renderTable(); }, 2000);
    windowData.abortController.signal.addEventListener('abort', () => clearInterval(timer));
    OS.bus.addEventListener('proc:change', renderTable, { signal: windowData.abortController.signal });
    renderTable();
}

// --- 8.15 Preview''')
open(p, 'w', encoding='utf-8').write(s)
print('ok')
