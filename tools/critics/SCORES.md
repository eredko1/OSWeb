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
