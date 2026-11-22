p = 'index.html'
s = open(p, encoding='utf-8').read()
def sub(old, new, count=1):
    global s
    assert old in s, 'miss: ' + old[:90]
    s = s.replace(old, new, count)

# unique SVG ids per instance (gradients defined in a hidden/earlier node must never starve later icons)
sub("function getFileDocSVG(ext = 'md') {", '''let svgUid = 0;
function uniqSvg(svg) {
    const k = (++svgUid).toString(36);
    return String(svg).replace(/\\bid="([^"]+)"/g, (m, i) => `id="${i}-${k}"`).replace(/url\\(#([^)]+)\\)/g, (m, i) => `url(#${i}-${k})`);
}
function getFileDocSVG(ext = 'md') {''')
sub("// --- 4. OS Kernel", "// --- 4. OS Kernel") if False else None
# apply wrapper right before the kernel section starts
marker = "/* ============================================================================\n * 4. OS Kernel"
assert marker in s
s = s.replace(marker, '''(function wrapIconFactories() {
    const a = getMacFolderSVG, b = getAppIconSVG, c = getFileDocSVG, d = getTrashSVG;
    getMacFolderSVG = (...x) => uniqSvg(a(...x)); getAppIconSVG = (...x) => uniqSvg(b(...x)); getFileDocSVG = (...x) => uniqSvg(c(...x)); getTrashSVG = (...x) => uniqSvg(d(...x));
})();

''' + marker, 1)

# new windows: use the space on tall (portrait) canvases
sub("    const defaultW = Math.min(config.width || 820, areaW - 24);\n    const defaultH = Math.min(config.height || 540, areaH - 24);",
    "    const tall = areaH > areaW * 1.2;                      // portrait canvas (iPhone/iPad in Mac mode)\n    const defaultW = Math.min(tall ? Math.round((config.width || 820) * 1.12) : (config.width || 820), areaW - 24);\n    const defaultH = Math.min(tall ? Math.round((config.height || 540) * 1.8) : (config.height || 540), areaH - 24);")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
