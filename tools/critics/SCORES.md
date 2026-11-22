# Critic score history (strict 1-10; 10 = indistinguishable from real macOS in that respect)

Chief Designer (D) and Chief Engineer (E) are independent reviewers working from `tools/critics/RUBRIC.md`
and screenshots from `node tools/capture.js <dir>`. Scores are their judgement, not pixel measurements.

| Round | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | avg | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 | avg |
|------:|---:|---:|---:|---:|---:|---:|---:|---:|---:|----:|---:|---:|---:|---:|---:|---:|---:|---:|---:|----:|
| 0 (baseline) | 4 | 4 | 5 | 3 | 1 | 3 | 3 | 4 | 2 | 3.2 | 4 | 4 | 3 | 4 | 3 | 2 | 2 | 3 | 3 | 3.1 |
| 1 | 5 | 5 | 6 | 6 | 6 | 3 | 3 | 4 | 2 | 4.4 | 5 | 4 | 3 | 6 | 8 | 3 | 4 | 2 | 4 | 4.3 |
| 2 | 5 | 6 | 6 | 7 | 6 | 3 | 3 | 6 | 4 | 5.1 | 5 | 6 | 4 | 6 | 9 | 3 | 4 | 6 | 6 | 5.4 |
| 3 | 6 | 6 | 7 | 7 | 6 | 5 | 4 | 6 | 4 | 5.7 | 6 | 6 | 4 | 7 | 9 | 5 | 5 | 7 | 6 | 6.1 |
| 4 | 6 | 6 | 7 | 7 | 6 | 5 | 5 | 6 | 5 | 5.9 | 6 | 7 | 5 | 7 | 9 | 5 | 6 | 6 | 6 | 6.3 |

Round 5 (in progress): lock-screen input barrier, modal focus traps, Safari URL/search + sandbox hardening,
live Auto appearance, tiled drag-out restore. Not yet re-scored.

## Open work, highest leverage first
1. Rebuild Calendar, Mail, Music, Photos, Reminders, Terminal, VS Code interiors on the unified shell (+ phone drill-down).
2. iPad shell (status bar, icon grid, floating Dock, full-screen apps) instead of the Mac shell on touch tablets.
3. Real macOS folder/document icons (Finder, desktop, iPhone Finder); redraw Preview/Photos/Terminal icon art.
4. Identity: replace hardcoded `Eugene Redko` and `/Users/eugene` (~85 places) with a per-user OS.user + VFS root.
5. Route all persisted state through an async OS.store adapter (27 raw localStorage uses remain) for cloud sync.
6. Window manager: true full-screen Space, transform/rAF resize. Finder keyboard model (arrows/Enter/Space).
7. Service-worker update prompt + fetch timeout; split the 8.6k-line inline script into ES modules.

## Round 6 (user request): Mac mode is the default on iPad and iPhone
- `OS.uiMode()` = 'mac' (default everywhere) or 'ios' (opt-in iPhone-style shell). Stored in `osweb_ui_mode`; switch in Settings > General > Interface (touch devices only).
- iPhone in Mac mode: viewport meta becomes `width=1100`, so the browser scales the Mac desktop to the screen (pinch-zoom works, media queries see a desktop width).
- 44pt sizing and phone chrome apply only to the iPhone shell. New windows are taller on portrait canvases.
- Fixed: shared SVG gradient ids starved later icons when an earlier copy sat in a hidden element (empty outline folders in Finder/Dock); every generated icon now gets unique ids.

## Round 7 (user report): touch on iPhone could not change/select Settings
- Cause (most likely): Mac mode on a phone laid the page out at 1100px, so controls were ~10pt on screen. Now portrait lays out at 640px (landscape 960), rows are 40-46px, windows open full-screen (`body.touch-small`).
- Escape hatch that does not need Settings: open the site with `?ui=ios` (iPhone-style shell) or `?ui=mac`; the choice is remembered.
- Verified with Chromium touch emulation only; real iOS Safari still needs a device check.

## Round 8-9 (user request): Spaces, monitor, proxy
- Virtual desktops: add/remove, Ctrl+arrows, drag windows between desktops in Mission Control (touch-capable), Mission Control launcher in Launchpad + Control Center, desktops persisted with the session.
- System monitor: menu-bar item + popover and Activity Monitor graphs. Honest metrics only: tab load (timer-lateness heartbeat), JS heap (Chromium), GPU name via WebGL + frame rate, network info. System-wide CPU/GPU utilisation is not exposed to web pages. Toggle: Settings > Desktop & Dock.
- Web proxy: `proxy/` (Vercel function or `node proxy/server.js`), HMAC-signed 5-minute URLs, SSRF block, no cookies, 10MB/15s limits. Client: Settings > Websites, Safari routes external sites through it. Tested against a local upstream that forbids framing. NOT deployed anywhere.

## Round 10 (user request): better login on iPhone
- Before: password field 122x17pt / arrow 13pt in Mac mode, keyboard auto-popped, any text unlocked.
- Now: big Unlock button (no passcode) or iOS-style passcode keypad with dots (64-68pt keys), shake + haptic on error, 5-try lockout (30s, doubling), no on-screen keyboard, physical digits work on desktop.
- Passcode: salted PBKDF2-SHA256 (150k), 4-6 digits, set/change/turn off in Settings > Lock Screen, re-lock after background (default 5 min).
- Face ID / Touch ID via WebAuthn platform authenticator (needs https; tested with a virtual authenticator, not on real hardware). Local convenience gate only: there is no server, so it is not account security.
- Display name is editable (Settings > Lock Screen).
