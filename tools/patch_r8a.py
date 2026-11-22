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

# --- switch: honour Cmd+H hidden windows, slide transition ---
rsub(r"function switchVirtualDesktop\(spaceId\) \{.*?\n\}\n", lambda m: '''function switchVirtualDesktop(spaceId, animate = true) {
    if (!virtualDesktops.includes(spaceId)) return;
    const changed = spaceId !== currentVirtualDesktop;
    const dir = virtualDesktops.indexOf(spaceId) > virtualDesktops.indexOf(currentVirtualDesktop) ? 1 : -1;
    currentVirtualDesktop = spaceId;
    Object.values(openWindows).forEach(w => {
        if (!w.element) return;
        if (w.virtualDesktop === spaceId && !w.isMinimized && !w.isHidden) {
            w.element.style.display = 'flex';
            if (animate && changed) { w.element.classList.remove('space-in-l', 'space-in-r'); void w.element.offsetWidth; w.element.classList.add(dir > 0 ? 'space-in-r' : 'space-in-l'); setTimeout(() => w.element && w.element.classList.remove('space-in-l', 'space-in-r'), 320); }
        } else {
            w.element.style.display = 'none';
        }
    });
    const front = Object.values(openWindows).filter(w => w.virtualDesktop === spaceId && !w.isMinimized && !w.isHidden && w.element).sort((a, b) => (parseInt(b.element.style.zIndex) || 0) - (parseInt(a.element.style.zIndex) || 0))[0];
    if (changed) { if (front) focusWindow(front.id); else { activeWindowId = null; updateTopAppMenuBar(null); } }
    renderVirtualDesktopButtons();
    if (typeof scheduleSessionSave === 'function') scheduleSessionSave();
}

// Remove a desktop: its windows move to the neighbouring desktop (like macOS).
function removeVirtualDesktop(id) {
    if (virtualDesktops.length <= 1) { showTemporaryMessage('You need at least one desktop.', 1600); return; }
    const idx = virtualDesktops.indexOf(id); if (idx < 0) return;
    const target = virtualDesktops[idx === 0 ? 1 : idx - 1];
    Object.values(openWindows).forEach(w => { if (w.virtualDesktop === id) w.virtualDesktop = target; });
    virtualDesktops.splice(idx, 1);
    if (currentVirtualDesktop === id) switchVirtualDesktop(target, false); else switchVirtualDesktop(currentVirtualDesktop, false);
    showTemporaryMessage(`Removed Desktop ${id}`, 1400);
}
function desktopLabel(id) { return `Desktop ${virtualDesktops.indexOf(id) + 1}`; }
''')
sub("    showTemporaryMessage(`Moved ${winData.title} to Space ${targetSpaceId}`, 1600);", "    showTemporaryMessage(`Moved ${winData.title} to ${desktopLabel(targetSpaceId)}`, 1600);")
sub("showTemporaryMessage(`Created & switched to Space ${newId}`, 1500);", "showTemporaryMessage(`Created ${desktopLabel(newId)}`, 1400);")

# --- Mission Control strip: labels by position, remove button, drop target for window cards ---
rsub(r"    spacesBar\.innerHTML = virtualDesktops\.map\(d => `<button class=\"mc-space.*?\+ `<button class=\"mc-add\"[^\n]*\n", lambda m: '''    spacesBar.innerHTML = virtualDesktops.map(d => `<div class="mc-space-wrap"><button class="mc-space${d === currentVirtualDesktop ? ' cur' : ''}" data-space="${d}" onclick="switchVirtualDesktop(${d}); toggleMissionControl(true);" aria-label="${desktopLabel(d)}"><span class="mc-space-thumb"></span><span>${desktopLabel(d)}</span></button>${virtualDesktops.length > 1 ? `<button class="mc-space-x" aria-label="Remove ${desktopLabel(d)}" onclick="removeVirtualDesktop(${d}); toggleMissionControl(true);">&times;</button>` : ''}</div>`).join('')
        + `<button class="mc-add" onclick="addVirtualDesktop(); toggleMissionControl(true);" aria-label="Add Desktop">+</button>`;
''')
sub("        card.addEventListener('click', () => { toggleMissionControl(false); if (w.isMinimized) restoreWindow(w.id); else focusWindow(w.id); });",
    '''        // click = open window; press-and-drag onto a desktop in the strip = move it there (works with touch)
        let drag = null;
        card.addEventListener('pointerdown', (e) => { drag = { x: e.clientX, y: e.clientY, moved: false, ghost: null }; card.setPointerCapture(e.pointerId); });
        card.addEventListener('pointermove', (e) => {
            if (!drag) return;
            if (!drag.moved && Math.hypot(e.clientX - drag.x, e.clientY - drag.y) > 8) { drag.moved = true; drag.ghost = thumb.cloneNode(true); drag.ghost.className = 'mc-ghost'; document.body.appendChild(drag.ghost); }
            if (drag.moved) { drag.ghost.style.left = e.clientX + 'px'; drag.ghost.style.top = e.clientY + 'px'; document.querySelectorAll('.mc-space').forEach(sp => { const r = sp.getBoundingClientRect(); sp.classList.toggle('drop', e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom); }); }
        });
        card.addEventListener('pointerup', (e) => {
            if (!drag) return; const d = drag; drag = null; d.ghost && d.ghost.remove();
            if (d.moved) { const tgt = document.elementFromPoint(e.clientX, e.clientY)?.closest?.('.mc-space'); document.querySelectorAll('.mc-space.drop').forEach(x => x.classList.remove('drop')); if (tgt) { moveWindowToSpace(w.id, Number(tgt.dataset.space)); toggleMissionControl(true); } return; }
            toggleMissionControl(false); if (w.isMinimized) restoreWindow(w.id); else focusWindow(w.id);
        });
        card.addEventListener('pointercancel', () => { if (drag && drag.ghost) drag.ghost.remove(); drag = null; });''')

# --- Mission Control as a launchable app (Launchpad / touch) + Control Center button ---
sub("    if (appId === 'app-launcher') {\n        toggleLaunchpad();\n        return null;\n    }", "    if (appId === 'app-launcher') {\n        toggleLaunchpad();\n        return null;\n    }\n    if (appId === 'mission-control') {\n        toggleMissionControl(true);\n        return null;\n    }")
sub("    'app-launcher': {", "    'mission-control': { title: 'Mission Control', width: 10, height: 10, content: () => '' },\n    'app-launcher': {")
sub("        'file-explorer': `<svg viewBox=\"0 0 64 64\"", "        'mission-control': `<svg viewBox=\"0 0 64 64\" xmlns=\"http://www.w3.org/2000/svg\"><defs><linearGradient id=\"mcBg\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#3a4252\"/><stop offset=\"1\" stop-color=\"#1c2029\"/></linearGradient></defs><rect x=\"4\" y=\"4\" width=\"56\" height=\"56\" rx=\"13\" fill=\"url(#mcBg)\"/><rect x=\"11\" y=\"14\" width=\"42\" height=\"9\" rx=\"2.5\" fill=\"#9fb4d6\" opacity=\".9\"/><rect x=\"11\" y=\"27\" width=\"19\" height=\"22\" rx=\"3\" fill=\"#e8eef8\"/><rect x=\"34\" y=\"27\" width=\"19\" height=\"22\" rx=\"3\" fill=\"#e8eef8\"/></svg>`,\n\n        'file-explorer': `<svg viewBox=\"0 0 64 64\"")
sub("            <button id=\"cc-toggle-widgets-btn\"", "            <button id=\"cc-mission-btn\" class=\"mac-btn-secondary !py-1 !px-2 !text-[11px]\">Mission Control</button>\n            <button id=\"cc-toggle-widgets-btn\"")
sub("    document.getElementById('cc-toggle-widgets-btn')?.addEventListener('click', () => toggleDesktopWidgets());", "    document.getElementById('cc-toggle-widgets-btn')?.addEventListener('click', () => toggleDesktopWidgets());\n    document.getElementById('cc-mission-btn')?.addEventListener('click', () => { document.getElementById('right-sidebar')?.classList.add('hidden'); toggleMissionControl(true); });")
sub("const HIDDEN_FROM_LAUNCHERS = new Set(['app-launcher', 'task-manager',", "const HIDDEN_FROM_LAUNCHERS = new Set(['app-launcher', 'task-manager',")  # mission-control stays visible in Launchpad

# --- persist the list of desktops with the session ---
sub("    return { v: 1, space: currentVirtualDesktop,", "    return { v: 1, spaces: virtualDesktops.slice(), nextSpace: nextDesktopId, space: currentVirtualDesktop,")
sub("    const b = OS.viewport.getDesktopBounds();\n    const num = (v, d)", "    if (Array.isArray(sess.spaces) && sess.spaces.length && sess.spaces.length <= 8 && sess.spaces.every(n => Number.isInteger(n) && n > 0)) { virtualDesktops.length = 0; sess.spaces.forEach(n => virtualDesktops.push(n)); nextDesktopId = Math.max(Number(sess.nextSpace) || 0, ...sess.spaces) + 1; renderVirtualDesktopButtons(); }\n    const b = OS.viewport.getDesktopBounds();\n    const num = (v, d)")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
