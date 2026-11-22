#!/usr/bin/env python3
"""Wraps every top-level `:hover` rule in index.html's inline CSS in `@media (hover: hover)`.
iOS Safari treats the first tap on an element whose :hover changes the page as a hover and swallows the click;
hover styles must therefore only exist on devices that really hover. Idempotent."""
import re, sys
p = 'index.html'
s = open(p, encoding='utf-8').read()
m = re.search(r'(<style>)(.*?)(</style>)', s, flags=re.S)
css = m.group(2)

def split_top(text, sep=','):
    parts, depth, cur = [], 0, ''
    for ch in text:
        if ch in '([': depth += 1
        if ch in ')]': depth -= 1
        if ch == sep and depth == 0: parts.append(cur); cur = ''
        else: cur += ch
    parts.append(cur); return parts

out, i, n, changed = [], 0, len(css), 0
while i < n:
    # find next top-level block: prelude { body }
    j = css.find('{', i)
    if j < 0: out.append(css[i:]); break
    prelude = css[i:j]
    depth, k = 1, j + 1
    while k < n and depth:
        if css[k] == '{': depth += 1
        elif css[k] == '}': depth -= 1
        k += 1
    body = css[j + 1:k - 1]
    # keep comments/whitespace that precede the selector untouched
    lead_m = re.match(r'(\s*(?:/\*.*?\*/\s*)*)(.*)$', prelude, flags=re.S)
    lead, sel = lead_m.group(1), lead_m.group(2)
    if sel.strip().startswith('@') or ':hover' not in sel:
        out.append(css[i:k])
    else:
        sels = [x.strip() for x in split_top(sel)]
        hov = [x for x in sels if ':hover' in x]; rest = [x for x in sels if ':hover' not in x]
        txt = lead
        if rest: txt += ', '.join(rest) + ' {' + body + '}\n        '
        txt += '@media (hover: hover) { ' + ', '.join(hov) + ' {' + body + '} }'
        out.append(txt); changed += 1
    i = k
new_css = ''.join(out)
if new_css != css:
    s = s[:m.start(2)] + new_css + s[m.end(2):]
    open(p, 'w', encoding='utf-8').write(s)
print(f'hover rules wrapped: {changed}')
