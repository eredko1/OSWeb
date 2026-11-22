// Captures the standard "critic scenes". Usage: node tools/capture.js <outDir> [round]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const out = process.argv[2] || 'shots'; fs.mkdirSync(out, { recursive: true });
const url = 'file://' + path.resolve(__dirname, '..', 'index.html');
(async () => {
  const b = await chromium.launch(); const errs = [];
  async function page(vp, opts = {}) {
    const c = await b.newContext({ viewport: vp, deviceScaleFactor: opts.dsf || 1, hasTouch: !!opts.touch, isMobile: !!opts.mobile });
    const p = await c.newPage();
    p.on('pageerror', e => errs.push('pageerror: ' + e.message));
    await p.goto(url); await p.waitForTimeout(2500); return p;
  }
  const shot = async (p, n) => { await p.waitForTimeout(700); await p.screenshot({ path: path.join(out, n + '.png') }); };
  const unlock = async p => { await p.evaluate(() => unlockDesktop()); await p.waitForTimeout(1200); };
  const app = async (p, id, o = {}) => { await p.evaluate(([i, o]) => launchOrFocusApp(i, o), [id, o]); await p.waitForTimeout(900); };
  const closeAll = p => p.evaluate(() => { document.querySelectorAll('.window .window-close, .window [data-action=close]').forEach(b => b.click()); });

  let p = await page({ width: 1440, height: 900 });
  await shot(p, '01-lockscreen');
  await unlock(p); await shot(p, '02-desktop');
  for (const [id, n] of [['file-explorer','03-finder'],['web-browser','04-safari'],['notepad','05-notes'],['terminal','06-terminal'],['calendar-app','07-calendar'],['settings','08-settings'],['mail-client','09-mail'],['calculator','10-calculator'],['weather-app','11-weather'],['music-player','12-music'],['image-viewer','13-photos'],['vscode','14-vscode'],['reminders','15-reminders'],['system-monitor','16-activity-monitor']]) {
    await p.evaluate(() => Object.keys(openWindows).forEach(id => closeWindow(id, true)));
    await app(p, id); await shot(p, n);
  }
  await p.evaluate(() => Object.keys(openWindows).forEach(id => closeWindow(id, true)));
  await app(p, 'file-explorer'); await app(p, 'notepad'); await app(p, 'terminal'); await shot(p, '17-multiwindow');
  await p.evaluate(() => toggleLaunchpad(true)); await shot(p, '18-launchpad'); await p.evaluate(() => toggleLaunchpad(false));
  await p.evaluate(() => toggleMissionControl(true)); await shot(p, '19-mission-control'); await p.evaluate(() => toggleMissionControl(false));
  await p.evaluate(() => toggleSpotlight(true, 'safari')); await shot(p, '20-spotlight'); await p.evaluate(() => toggleSpotlight(false));
  await p.click('#apple-menu-button'); await shot(p, '21-apple-menu'); await p.keyboard.press('Escape'); await p.mouse.click(700, 500);
  await p.evaluate(() => openAboutThisMacModal()); await shot(p, '22-about'); await p.keyboard.press('Escape');
  await p.evaluate(() => { Object.keys(openWindows).forEach(id => closeWindow(id, true)); applyThemeByIndex(1); launchOrFocusApp('file-explorer'); launchOrFocusApp('notepad'); }); await p.waitForTimeout(800); await shot(p, '23-light-mode');
  p = await page({ width: 1180, height: 820, touch: true, mobile: true }); await unlock(p); await app(p, 'notepad'); await shot(p, '24-ipad');
  p = await page({ width: 390, height: 844, touch: true, mobile: true, dsf: 2 }); await shot(p, '25-iphone-lock'); await unlock(p); await shot(p, '26-iphone-home');
  await app(p, 'notepad'); await shot(p, '27-iphone-app');
  await p.evaluate(() => iosGoHome()); await app(p, 'file-explorer'); await shot(p, '28-iphone-finder');
  await p.evaluate(() => iosGoHome()); await app(p, 'settings'); await shot(p, '29-iphone-settings');
  p = await page({ width: 820, height: 1180, touch: true, mobile: true }); await unlock(p); await app(p, 'file-explorer'); await app(p, 'notepad'); await shot(p, '30-ipad-portrait');
  fs.writeFileSync(path.join(out, 'errors.txt'), [...new Set(errs)].join('\n'));
  console.log('errors:', [...new Set(errs)].slice(0, 8));
  await b.close();
})();
