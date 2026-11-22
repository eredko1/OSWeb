# OSWeb macOS-fidelity rubric

Goal: a blind side-by-side with a real Mac running macOS Sequoia (and the same pixels on iPad/iPhone Safari)
should be indistinguishable. Every metric is scored 1-10 per round.

Scoring rules (both critics):
- 10 = a Mac user cannot tell it apart from the real thing in that respect. Do NOT award 10 on effort,
  intent or "close enough". A single visible deviation caps the metric at 9; several caps it at 8, etc.
- Score only what you can evidence (screenshot file + scene, or file:line in /home/user/OSWeb/index.html, or a probe you ran).
- List concrete, actionable defects, most damaging first. Each: scene/file, what is wrong, what macOS actually does
  (give real values: px sizes, hex/rgba, font weights, radii, timings), and the fix.
- Be strict and consistent. Don't regress a score without evidence. Don't reward a fix you didn't verify.

## Chief Designer metrics (D)
D1 Typography        SF Pro stack, real sizes/weights/tracking (13px body, 13px semibold titles, 11px captions), no mono-font UI chrome, no ALL-CAPS "dashboard" labels
D2 Materials         vibrancy/blur/translucency, shadows (window, menu, dock), 0.5px borders & rim light, correct light AND dark mode
D3 Window chrome     traffic lights (12px, 8px gaps, glyphs on hover, inactive grey), title bar heights, toolbar layout, 10px window radius, active vs inactive window styling
D4 Menu bar & Dock   24px menu bar with REAL macOS items only (Apple, app name bold, File/Edit/View..., then status icons + clock), real dock proportions, running dots, magnification, separator/Trash
D5 Wallpaper & color Sequoia-style wallpaper (not black), accent color system, no neon/"dev dashboard" colors, desktop icon labels/selection
D6 Iconography       app icons = macOS squircle gradient icons (not FontAwesome glyphs on flat tiles); in-app icons SF-Symbols-like weight/size
D7 App fidelity      each app (Finder, Safari, Notes, Terminal, Calendar, Settings, Mail, Calculator, Weather, Music, Photos, Reminders, Activity Monitor, Preview, VS Code) matches its real macOS layout, controls and proportions
D8 System UI         lock/login screen, Spotlight, Launchpad, Mission Control, Apple menu, About This Mac, alerts/sheets/popovers, Control Center, notification-style widgets
D9 Device adaptation iPad (landscape/portrait) and iPhone look native to that device's Safari (safe areas, no tiny scaled desktop, tap targets 44pt)

## Chief Engineer metrics (E)
E1 Rendering robustness  no overflow/clipping/overlap, z-index and stacking correct, no layout jumps, correct at 1x/2x, resize-safe
E2 Window manager        drag, 8-way resize, min/max/close/zoom (green = fullscreen), snap, focus/stacking, per-window state, Cmd+W/Q/M/H/Tab/`
E3 Input & keyboard      real macOS shortcuts, text selection/caret, context menus (right-click) everywhere macOS has them, menu-bar menus per app, pointer/touch parity
E4 Performance           60fps drag/resize/magnify (use transform/opacity, no layout thrash), cheap timers (no 2s telemetry repaint of whole bar), boot < 1.5s, no memory leaks from windows
E5 Self-contained        zero CDN/network requirement to render, fonts/icons vendored, works offline, no console errors
E6 Truthful system data  no hardcoded fake telemetry presented as real (CPU/GPU/memory, weather, username "eugene"); real clock/battery/network/memory APIs or clearly absent
E7 Accessibility         keyboard nav, focus rings, ARIA roles/labels, prefers-reduced-motion/-contrast/-transparency, 4.5:1 contrast, VoiceOver-sane DOM
E8 State & structure     window/app/VFS state persisted (and restore on reload), no globals leaking between apps, code organized so a multi-user cloud-sync layer can be added later
E9 Cross-device input    iOS Safari quirks: 100dvh/safe-area insets, no rubber-band scroll of body, no double-tap zoom, 16px inputs (no focus zoom), Apple Pencil/touch drag, hover-less affordances

## Environment notes for critics
- Screenshots are rendered by headless Chromium on Linux, which has NO San Francisco font. `-apple-system` falls back to a generic sans.
  Judge the font *stack*, sizes, weights and tracking (on Apple devices the stack resolves to real SF), not glyph shapes.
- Screenshot scenes come from `node tools/capture.js <outDir>`. Scene numbers: 01 lock, 02 desktop, 03-16 apps
  (finder, safari, notes, terminal, calendar, settings, mail, calculator, weather, music, photos, vscode, reminders, activity monitor),
  17 multi-window, 18 launchpad, 19 mission control, 20 spotlight, 21 apple menu, 22 about, 23 light mode, 24 iPad, 25-27 iPhone.
- Read screenshots with the Read tool (they are PNG). Source is the single file /home/user/OSWeb/index.html (~8k lines).
- Do NOT edit any repo files. You may write probe scripts only inside your own scratchpad dir.
