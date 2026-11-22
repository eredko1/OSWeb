#!/usr/bin/env python3
"""Generates the vendored, offline Sequoia-style wallpapers (layered misty ridgelines)."""
import math, random
W, H = 1920, 1200

def ridge(seed, base, amp, rough, n=96):
    r = random.Random(seed)
    ph = [r.uniform(0, 6.28) for _ in range(5)]
    pts = []
    for i in range(n + 1):
        x = -40 + i / n * (W + 80)
        t = i / n
        y = base
        for k in range(5):
            f = (k + 1) * rough
            y += math.sin(t * f * 6.28 + ph[k]) * amp / (k + 1) ** 1.25
        pts.append((x, y))
    d = f"M-40 {H} L{pts[0][0]:.1f} {pts[0][1]:.1f} "
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d += f"Q{x0:.1f} {y0:.1f} {(x0+x1)/2:.1f} {(y0+y1)/2:.1f} "
    return d + f"L{W+40} {H} Z"

def make(name, sky, sun, layers, sun_xy=(1180, 560), sun_r=520, haze="#ffffff", haze_op=0.0):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">', '<defs>']
    out.append('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">' + ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in sky) + '</linearGradient>')
    out.append(f'<radialGradient id="sun" cx="{sun_xy[0]}" cy="{sun_xy[1]}" r="{sun_r}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{sun[0]}" stop-opacity="{sun[1]}"/><stop offset="1" stop-color="{sun[0]}" stop-opacity="0"/></radialGradient>')
    for i, (c1, c2, _, _, _, _) in enumerate(layers):
        out.append(f'<linearGradient id="l{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>')
    out.append('<filter id="soft"><feGaussianBlur stdDeviation="1.2"/></filter></defs>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/><rect width="{W}" height="{H}" fill="url(#sun)"/>')
    for i, (c1, c2, base, amp, rough, seed) in enumerate(layers):
        out.append(f'<path d="{ridge(seed, base, amp, rough)}" fill="url(#l{i})"/>')
        if haze_op:
            out.append(f'<rect y="{base-amp*1.4:.0f}" width="{W}" height="{amp*3:.0f}" fill="{haze}" opacity="{haze_op}" />' if False else '')
    out.append('</svg>')
    open(f'vendor/wallpapers/{name}.svg', 'w').write('\n'.join(out))

# Sequoia (light / dawn): pale teal sky, glowing sun, blue-green layered forested ridges
make('sequoia', [(0, '#7fb4c8'), (.45, '#bcd9d9'), (.7, '#f1e3c9')], ('#fff4d6', .95), [
    ('#9fc3bf', '#b6d2c6', 640, 60, 1.3, 1), ('#7fb0aa', '#9dc2b3', 720, 70, 1.6, 2),
    ('#5e9a98', '#7db0a2', 810, 80, 1.9, 3), ('#3f7f86', '#5b9a95', 900, 85, 2.2, 4),
    ('#2a6270', '#3d7c82', 990, 80, 2.6, 5), ('#17414f', '#245b66', 1080, 70, 3.0, 6)], sun_xy=(1250, 560))
# Sequoia Dark: deep blue dusk
make('sequoia-dark', [(0, '#0b1230'), (.5, '#1d3560'), (.8, '#47628a')], ('#9fb6e6', .55), [
    ('#33507a', '#3f5f8c', 650, 60, 1.3, 11), ('#2a4570', '#355580', 730, 70, 1.6, 12),
    ('#213a63', '#2b4a72', 820, 80, 1.9, 13), ('#192f53', '#223d62', 910, 85, 2.2, 14),
    ('#11233f', '#192e4d', 1000, 80, 2.6, 15), ('#0a1830', '#102039', 1090, 70, 3.0, 16)], sun_xy=(1250, 640), sun_r=620)
# Sonoma-style warm hills
make('sonoma', [(0, '#e8c9a4'), (.5, '#f4d9b0'), (.8, '#f8e8c8')], ('#fff2c4', .9), [
    ('#d9b98a', '#c8a475', 700, 50, 1.2, 21), ('#c29a62', '#b08752', 790, 60, 1.5, 22),
    ('#a77f46', '#946f3e', 880, 70, 1.8, 23), ('#6f8a4a', '#5b743d', 960, 70, 2.1, 24),
    ('#476b3a', '#385a31', 1050, 60, 2.5, 25)], sun_xy=(700, 520))
# Ventura-style violet waves
make('ventura', [(0, '#1b1034'), (.5, '#4a2a7a'), (.85, '#e0668a')], ('#ff9a8b', .7), [
    ('#7b3d8f', '#8e4a99', 700, 70, 1.1, 31), ('#5e2f86', '#6c3a92', 790, 80, 1.4, 32),
    ('#43246f', '#512d7b', 880, 90, 1.7, 33), ('#2d1a58', '#392163', 980, 90, 2.0, 34),
    ('#1c1040', '#251650', 1080, 70, 2.4, 35)], sun_xy=(960, 640), sun_r=700)
