"""设计系统 E「深色荧光绿」：参考 Grid-Scale Battery（Rostu Design）+ B.Forge（Gaurav Chauhan）。

拆解：
1. 近黑外框里套一块大圆角深色面板，像设备屏幕；荧光绿只给最重要的东西。
2. 眉标是绿色胶囊；卡片是大圆角，浅薄荷色或从绿色渐隐到底色。
3. 流程做成「阶梯胶囊」：绿色胶囊标签逐级抬高，下面挂浅色说明卡。
4. 数据图：渐隐柱、分段半圆仪表盘、比例条，图形本身就是装饰。
5. 字体统一 Space Grotesk / 思源黑体，标题不加粗、偏大。
"""
import math
from core import W, H, MX, mix, rgb
from layouts import _roll, _ghost, _donut_arcs, GHOST
from designs.kit import bg, split, tw, bignum, plain

OUT, PANEL, LINE, WHITE, GREY, LIME, MINT, MOSS = '0A0C0A', '171B18', '2B332C', 'F1F5EE', '98A396', 'B8F36B', 'E2F8D2', '3C4F38'
F = 'Space Grotesk|Noto Sans SC'
RAD = .28


def _shell(c, deck, source=None):
    bg(c, OUT)
    c.rect(.22, .22, W - .44, H - .44, fill=PANEL, radius=RAD, line=LINE, lw=.75)
    c.text(W - MX - 2, .45, 2, .26, f'{c.idx:02d}', 10.5, GREY, align='r', font=F)
    c.text(MX, H - .62, 7, .26, ('来源：' + source) if source else deck.get('masthead', ''), 10, GREY, font=F)
    c.text(W - MX - .3, H - .7, .3, .3, '⚡', 13, LIME, font=F)


def _pill(c, x, y, text, fill=LIME, ink=OUT, size=11, at=None, gap=0):
    w = tw(text, size) + .45
    c.a(c.rect(x, y, w, .36, fill=fill, radius=.18), 'zoom', at=at, gap=gap, dur=350)
    c.a(c.text(x, y, w, .36, text, size, ink, align='c', anchor='m', font=F), 'fade', gap=0)
    return w


def _head(c, s, y=.75, w=None, size=30):
    if s.get('kicker'): _pill(c, MX, y, s['kicker'].title(), at=0)
    c.a(c.text(MX, y + .5, w or W - 2 * MX, 1.2, plain(s['title']), size, WHITE, font=F, spacing=1.1), 'fade-up', gap=60)


def _fade_rect(c, x, y, w, h, top=LIME, k=.55, radius=RAD):
    return c.gradbar(x, y, w, h, [mix(top, PANEL, k), PANEL], angle=90, radius=radius)


def gauge(c, cx, cy, r, frac, n=26, at=0, lit=LIME, dim=None, bw=.13, bh=.5, colors=None):
    """分段半圆仪表盘：n 根小胶囊沿半圆排开，frac 比例点亮"""
    dim = dim or mix(LIME, PANEL, .18)
    for k in range(n):
        a = math.pi - math.pi * k / (n - 1)
        px, py = cx + r * math.cos(a), cy - r * math.sin(a)
        on = k < round(frac * n)
        b = c.rect(px - bw / 2, py - bh / 2, bw, bh, fill=(colors[k] if colors else (lit if on else dim)), radius=bw / 2)
        b.rotation = 90 - math.degrees(a)
        c.a(b, 'zoom', at=at + k * 30, hold=True, dur=250)


# ------------------------------------------------------------------ 页面
def cover(c, s, deck):
    _shell(c, deck)
    _pill(c, MX, 1.0, s.get('kicker', ''), at=0)
    lines = s['title'] if isinstance(s['title'], list) else [s['title']]
    c.a(c.text(MX, 1.6, 6.8, 2.6, lines, 52, WHITE, font=F, spacing=1.05, para_gap=0), 'fade-up', at=150, dur=800)
    if s.get('subtitle'): c.a(c.text(MX, 3.7, 6, .5, s['subtitle'], 14, GREY, font=F), 'fade', gap=200)
    st = s.get('stats') or []
    tiles = [(7.9, .75, 4.6, 2.7, LIME, OUT), (7.9, 3.65, 2.2, 3.05, MINT, OUT), (10.3, 3.65, 2.2, 3.05, '222823', WHITE)]
    for i, (x, y, w, h, fill, ink) in enumerate(tiles):
        c.a(c.rect(x, y, w, h, fill=fill, radius=RAD, line=None if i < 2 else LINE), 'zoom', at=300 + i * 120, hold=True, dur=500)
        if i < len(st):
            c.a(c.text(x + .3, y + .3, w - .6, .3, st[i]['label'], 11, ink, font=F), 'fade', at=600 + i * 120, hold=True)
            c.clock = 650 + i * 120
            c.counter(x + .28, y + h - (1.5 if i == 0 else 1.1), w - .5, 1.2, st[i]['value'], 64 if i == 0 else 34, ink, gap=0, bold=False)
    if s.get('meta'): c.text(MX, H - 1.2, 6, .3, s['meta'], 11, GREY, font=F)


def kpi(c, s, deck):
    """三张渐隐卡：①分段圆环 = 省下的 11.5 小时（每段 0.5 小时，按去向上色）②两根柱对比 ③倍数柱"""
    _shell(c, deck, s.get('source')); _head(c, s)
    items = s['items']; x0 = MX; g = .3; cw = (W - 2 * MX - 2 * g) / 3; y = 2.35; ch = H - y - .95
    for i, it in enumerate(items[:3]):
        x = x0 + i * (cw + g)
        c.a(_fade_rect(c, x, y, cw, ch, k=.45 if i == 0 else .25), 'fade-up', at=200 + i * 150, hold=True, dur=600)
        c.a(c.text(x + .3, y + .3, cw - .6, .3, it['label'], 12, WHITE, font=F), 'fade', at=300 + i * 150, hold=True)
    # 卡 1：分段半圆，按 split 的去向点亮
    it = items[0]; x = x0
    sp = s.get('split'); n = 23
    cols = None
    if sp:   # 每段 0.5 小时，按去向上色：第一类亮绿，其余渐暗
        shades = [LIME, mix(LIME, PANEL, .6), mix(LIME, PANEL, .38), mix(LIME, PANEL, .22)]
        cols = []
        for k, p in enumerate(sp['parts']): cols += [shades[min(k, 3)]] * int(round(p['value'] * 2))
        n = len(cols)
    gauge(c, x + cw / 2, y + 2.75, 1.3, 1.0, n=n, at=500, colors=cols, bw=.11, bh=.42)
    c.clock = 700
    bignum(c, x + .3, y + 2.0, it['value'], 40, WHITE, F, unit_scale=.3, gap=0, dur=900, align='c', w=cw - .6)
    c.a(c.text(x + .3, y + ch - .75, cw - .6, .5, it.get('delta', ''), 11, LIME, font=F, align='c'), 'fade', at=1400, hold=True)
    # 卡 2：原来 vs 现在
    it = items[1]; x = x0 + cw + g
    c.clock = 800
    bignum(c, x + .3, y + .75, it['value'], 54, WHITE, F, unit_scale=.3, gap=0, dur=900)
    bars = [(it.get('delta', '原来'), 1.0, '3A463A'), ('现在', 40 / 360, LIME)]
    for k, (lab, v, col) in enumerate(bars):
        bx = x + .45 + k * 1.3; bh = 1.7 * v + .1
        c.a(c.rect(bx, y + ch - .6 - bh, .9, bh, fill=col, radius=.12), 'wipe-up', at=1000 + k * 200, hold=True, dur=700)
        c.a(c.text(bx - .2, y + ch - .5, 1.3, .3, lab, 10.5, GREY, align='c', font=F), 'fade', at=1000, hold=True)
    # 卡 3：倍数
    it = items[2]; x = x0 + 2 * (cw + g)
    c.clock = 900
    bignum(c, x + .3, y + .75, it['value'], 54, LIME, F, unit_scale=.3, gap=0, dur=900)
    for k in range(4):
        bx = x + .45 + k * .7; bh = .55 * (k + 1)
        c.a(c.rect(bx, y + ch - .6 - bh, .45, bh, fill=LIME if k == 3 else mix(LIME, PANEL, .35), radius=.1), 'wipe-up', at=1100 + k * 120, hold=True, dur=600)
    c.a(c.text(x + .3, y + ch - .5, cw - .6, .3, it.get('delta', ''), 10.5, GREY, font=F), 'fade', at=1100, hold=True)


def section(c, s, deck):
    _shell(c, deck)
    c.a(c.rect(MX - .2, 1.3, W - 2 * MX + .4, H - 2.6, fill=LIME, radius=RAD), 'zoom', at=0, dur=600)
    c.a(c.text(MX + .3, 1.75, 3, .4, s.get('no', ''), 16, OUT, font=F), 'fade', at=300)
    c.a(c.text(MX + .3, 2.6, W - 2 * MX - .6, 1.6, s['title'], 60, OUT, font=F), 'fade-up', at=400, dur=800)
    if s.get('subtitle'): c.a(c.text(MX + .3, 4.25, 8, .5, s['subtitle'], 16, MOSS, font=F), 'fade', gap=200)


def chart(c, s, deck):
    """渐隐竖柱：重点柱实心荧光绿，其余从绿色渐隐到面板色"""
    _shell(c, deck, s.get('source')); _head(c, s, w=5.2, size=28)
    ins = s.get('insights') or []
    for i, t in enumerate(ins[:2]):
        c.a(c.rect(MX, 3.0 + i * 1.2, .05, .9, fill=LIME if i == 0 else LINE), 'wipe-down', gap=120, dur=300)
        c.a(c.text(MX + .25, 3.0 + i * 1.2, 4.6, 1, plain(t), 12, GREY, font=F, spacing=1.45), 'fade', gap=0)
    ch = s['chart']; cats = ch['categories']; vals = ch['series'][0]['values']; hl = ch.get('highlight', 0)
    x0 = 6.3; x1 = W - MX; bottom = H - 1.25; ph = 4.6; n = len(cats); cw = (x1 - x0) / n; bw = cw * .62; vmax = max(vals)
    for i, (cat, v) in enumerate(zip(cats, vals)):
        h = ph * v / vmax; x = x0 + i * cw + (cw - bw) / 2; on = i == hl
        bar = c.rect(x, bottom - h, bw, h, fill=LIME, radius=.12) if on else c.gradbar(x, bottom - h, bw, h, [mix(LIME, PANEL, .5), PANEL], angle=90, radius=.12)
        c.a(bar, 'wipe-up', at=300 + i * 90, hold=True, dur=800)
        c.a(c.text(x - .3, bottom - h + .15, bw + .6, .4, f'{v:g}', 15, OUT if on else WHITE, align='c', font=F), 'fade', at=800 + i * 90, hold=True)
        c.a(c.text(x - .4, bottom + .1, bw + .8, .3, cat, 10.5, WHITE if on else GREY, align='c', font=F), 'fade', at=300 + i * 90, hold=True)
    c.rect(x0, bottom, x1 - x0, .01, fill=LINE)


def donut_story(c, s, deck):
    _shell(c, deck, s.get('source'))
    cont = s.get('continue'); prev = deck['slides'][c.idx - 2] if cont else None
    segs = s['segments']; tot = sum(g['value'] for g in segs)
    cols = [MOSS, LIME]; cx, cy, d = 3.5, 4.3, 4.0
    if prev:
        c.a(_ghost(c, c.text(MX, 1.25, 10, 1, plain(prev['title']), 30, WHITE, font=F)), 'out', at=0, hold=True, dur=250, grp=1)
        c.a(c.text(MX, 1.25, 10, 1, plain(s['title']), 30, WHITE, font=F), 'fade', at=200, hold=True, dur=400)
        _pill(c, MX, .75, (s.get('kicker') or '').title(), at=0)
        pv = [g['value'] / tot for g in prev['segments']]; nv = [g['value'] / tot for g in segs]
        first = c.s.shapes.add_group_shape(_donut_arcs(c, pv, cols, cx, cy, d, dy=GHOST))
        c.a(first, 'appear', at=0, hold=True, dur=1, params={'dy': GHOST / H}); c.a(first, 'cut', at=400, hold=True, dur=1, grp=1)
        ease = lambda k: 4 * k ** 3 if k < .5 else 1 - (-2 * k + 2) ** 3 / 2
        for i in range(24):
            k = ease(i / 24); vals = [a + (b - a) * k for a, b in zip(pv, nv)]; off = H + 1 + i * .02
            g = c.s.shapes.add_group_shape(_donut_arcs(c, vals, cols, cx, cy, d, dy=off))
            c.a(g, 'appear', at=400 + 45 * i, hold=True, dur=1, params={'dy': off / H}); c.a(g, 'cut', at=400 + 45 * (i + 1), hold=True, dur=1, grp=1)
        c.a(c.s.shapes.add_group_shape(_donut_arcs(c, nv, cols, cx, cy, d)), 'appear', at=400 + 45 * 24, hold=True, dur=1)
    else:
        _head(c, s)
        for a in _donut_arcs(c, [g['value'] / tot for g in segs], cols, cx, cy, d):
            c.a(a, 'wheel', at=300, hold=True, dur=1000)
    for k, g in enumerate(segs):
        x = 6.6 + k * 3.0; hl = k == 1
        c.rect(x, 2.6, 2.75, 2.2, fill=LIME if hl else '222823', radius=RAD)
        c.text(x + .3, 2.85, 2.2, .3, g['name'], 12, OUT if hl else GREY, font=F)
        if prev: _roll(c, x + .3, 3.3, 2.4, 1.1, prev['segments'][k]['label'], g['label'], 44, OUT if hl else WHITE, 400, 1100, font=F)
        else: c.a(c.text(x + .3, 3.3, 2.4, 1.1, g['label'], 44, OUT if hl else WHITE, font=F), 'fade-up', at=800, hold=True)
    if prev:
        for k, an in enumerate(s.get('annotations', [])):
            c.a(c.text(6.6 + k * 3.0, 5.0, 2.7, 1, an['text'], 11.5, GREY, font=F, spacing=1.4), 'fade', at=1600, hold=True)
    elif s.get('teaser'):
        c.a(c.text(6.6, 5.1, 5.6, .5, s['teaser'] + ' →', 18, LIME, font=F), 'fade', at=1400)


def timeline(c, s, deck):
    """四张迷你卡：年份胶囊 + 大百分比 + 渐隐柱（高度 = 使用比例）"""
    _shell(c, deck, s.get('source')); _head(c, s)
    items = s['items']; n = len(items); g = .25; cw = (W - 2 * MX - g * (n - 1)) / n; y = 2.4; ch = H - y - 1.0
    vals = (s.get('chart') or {}).get('line') or [0] * n
    for i, it in enumerate(items):
        x = MX + i * (cw + g); hl = it.get('highlight')
        c.a(c.rect(x, y, cw, ch, fill=LIME if hl else '1F2520', radius=RAD), 'fade-up', at=200 + i * 130, hold=True, dur=500)
        ink = OUT if hl else WHITE
        c.a(c.text(x + .3, y + .3, 1.2, .3, it['time'], 12, ink if hl else LIME, font=F), 'fade', at=300 + i * 130, hold=True)
        c.a(c.text(x + .3, y + .65, cw - .5, .9, f'{vals[i]:g}%', 44, ink, font=F), 'fade', at=300 + i * 130, hold=True)
        c.a(c.text(x + .3, y + 1.55, cw - .5, .7, [it['title'], it.get('text', '')], 12, ink if hl else GREY, font=F, spacing=1.35, para_gap=.15), 'fade', at=300 + i * 130, hold=True)
        bh = (ch - 2.6) * vals[i] / 100 + .1
        bar = c.rect(x + .3, y + ch - .3 - bh, cw - .6, bh, fill=OUT, alpha=.18, radius=.12) if hl else c.gradbar(x + .3, y + ch - .3 - bh, cw - .6, bh, [mix(LIME, PANEL, .45), '1F2520'], angle=90, radius=.12)
        c.a(bar, 'wipe-up', at=500 + i * 130, hold=True, dur=700)


def table(c, s, deck):
    _shell(c, deck, s.get('source')); _head(c, s)
    cols = s['columns']; rows = s['rows']; hl = s.get('highlight_row')
    ws = [2.5, 2.4, 2.4, 2.2, 2.23]; y = 2.45; rh = .9; x = MX
    for j, col in enumerate(cols):
        c.text(x + .25, y, ws[j], .3, col, 10.5, GREY, font=F); x += ws[j]
    for i, r in enumerate(rows):
        yy = y + .42 + i * (rh + .12); on = i == hl
        c.a(c.rect(MX, yy, W - 2 * MX, rh, fill=LIME if on else '1F2520', radius=rh / 2), 'zoom', gap=130, dur=450)
        x = MX
        for j, v in enumerate(r):
            c.a(c.text(x + .3, yy, ws[j] - .2, rh, str(v), 30 if j == 1 else 13, OUT if on else (WHITE if j < 2 else GREY), anchor='m', font=F), 'fade', gap=30)
            x += ws[j]
    if s.get('summary'): c.a(c.text(MX, H - 1.35, 10, .5, plain(s['summary']), 15, WHITE, font=F), 'fade', gap=150)


def process(c, s, deck):
    """阶梯胶囊：绿色胶囊逐级抬高、粗绿线连成台阶，下面挂浅色说明卡（参考 Charge → Hold → Dispatch → Stack）"""
    _shell(c, deck); _head(c, s)
    st = s['steps']; n = len(st); g = .2; cw = (W - 2 * MX - g * (n - 1)) / n
    top0 = 4.05; step = .62; ph = .62
    for i, it in enumerate(st):
        x = MX + i * (cw + g); py = top0 - i * step
        if i:   # 台阶连线：上一颗胶囊右端 → 横 → 竖 → 这颗胶囊左端
            pe = MX + (i - 1) * (cw + g) + cw * .78; my = py + step + ph / 2; mx = x - .12
            c.a(c.line(pe, my, mx, my, LIME, 5), 'draw', at=250 + i * 180, hold=True, dur=200)
            c.a(c.line(mx, my, mx, py + ph / 2, LIME, 5), 'wipe-up', at=400 + i * 180, hold=True, dur=200)
            c.a(c.line(mx, py + ph / 2, x, py + ph / 2, LIME, 5), 'draw', at=500 + i * 180, hold=True, dur=100)
        pill = c.rect(x, py, cw * .78, ph, fill=LIME, radius=ph / 2)
        c.a(pill, 'wipe-right', at=320 + i * 180, hold=True, dur=400)
        c.a(c.text(x + .3, py, cw * .78 - .4, ph, it['title'], 22, OUT, anchor='m', font=F), 'fade', at=500 + i * 180, hold=True)
        cy = py + ph + .2
        c.a(c.rect(x, cy, cw - .05, H - .95 - cy, fill=MINT, radius=RAD), 'fade-up', at=550 + i * 180, hold=True, dur=500)
        c.a(c.text(x + .3, cy + .3, cw - .6, .4, f'{i+1:02d}', 13, MOSS, font=F), 'fade', at=650 + i * 180, hold=True)
        c.a(c.text(x + .3, cy + .7, cw - .6, 1.2, it.get('text', ''), 13, OUT, font=F, spacing=1.45), 'fade', at=650 + i * 180, hold=True)
    if s.get('summary'): c.a(c.text(W - MX - 5.5, .95, 5.5, .4, s['summary'], 12, GREY, font=F, align='r'), 'fade', at=900)


def stat(c, s, deck):
    _shell(c, deck, s.get('source'))
    _pill(c, MX, .9, (s.get('kicker') or '').title(), at=0)
    c.a(c.text(MX, 1.45, 6, .5, s.get('label', ''), 22, WHITE, font=F), 'fade', gap=60)
    c.clock = 300
    bignum(c, MX - .1, 2.1, s['value'], 190, LIME, F, unit_scale=.3, gap=0, dur=1300)
    if s.get('delta'): _pill(c, MX, 5.0, '▲ ' + s['delta'], fill=MINT, gap=100)
    if s.get('text'): c.a(c.text(MX, 5.55, 6, .5, s['text'], 12, GREY, font=F), 'fade', gap=0)
    g = s.get('gauge') or {}
    frac = g.get('value', 0) / g.get('max', 100) if g else .6
    gauge(c, 9.9, 5.1, 2.4, frac, n=30, at=400, bw=.17, bh=.75)
    c.a(c.text(8.4, 4.35, 3, .7, g.get('text', ''), 40, WHITE, align='c', font=F), 'fade', at=1300)
    c.a(c.text(8.4, 5.0, 3, .3, g.get('label', ''), 11, GREY, align='c', font=F), 'fade', at=1300)


def compare(c, s, deck):
    _shell(c, deck); _head(c, s)
    gw = (W - 2 * MX - .3) / 2
    for k, side in enumerate(('left', 'right')):
        d = s[side]; x = MX + k * (gw + .3); hl = k == 1; ink = OUT if hl else WHITE
        c.a(c.rect(x, 2.4, gw, H - 3.35, fill=LIME if hl else '1F2520', radius=RAD), 'fade-up', gap=150, dur=500)
        _pill(c, x + .35, 2.75, d.get('tag', ''), fill=OUT if hl else MOSS, ink=LIME if hl else WHITE, gap=60)
        c.a(c.text(x + .35, 3.3, gw - .7, .7, d['title'], 26, ink, font=F), 'fade', gap=0)
        for j, it in enumerate(d['items']):
            c.a(c.text(x + .35, 4.2 + j * .48, gw - .7, .4, ('●  ' if hl else '○  ') + it, 14, ink if hl else GREY, font=F), 'fade', gap=50)


def quote(c, s, deck):
    bg(c, OUT)
    c.a(c.rect(.22, .22, W - .44, H - .44, fill=LIME, radius=RAD), 'zoom', at=0, dur=600)
    txt = s['text'] if isinstance(s['text'], list) else [s['text']]
    c.a(c.text(MX + .3, 2.3, W - 2 * MX - .6, 2.6, plain(txt), 44, OUT, font=F, spacing=1.25, para_gap=.1), 'fade-up', at=300, dur=800)
    if s.get('by'): c.a(c.text(MX + .3, 4.9, 6, .4, '⚡ ' + s['by'], 13, MOSS, font=F), 'fade', gap=300)


def end(c, s, deck):
    _shell(c, deck)
    c.a(c.text(0, 2.0, W, 1.0, '⚡', 54, LIME, align='c', font=F), 'pop', at=100)
    c.a(c.text(0, 3.0, W, 1.2, s.get('title', ''), 56, WHITE, align='c', font=F), 'fade-up', at=300, dur=800)
    if s.get('subtitle'):
        w = tw(s['subtitle'], 13) + .6
        _pill(c, (W - w) / 2, 4.3, s['subtitle'], size=13, gap=200)


LAYOUTS = {'cover': cover, 'kpi': kpi, 'section': section, 'chart': chart, 'donut_story': donut_story,
           'timeline': timeline, 'table': table, 'process': process, 'stat': stat, 'compare': compare,
           'quote': quote, 'end': end}
