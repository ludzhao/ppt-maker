"""设计系统 C「暗黑董事会」：参考 Pitch · Board Deck。

拆解：
1. 近黑底 + 唯一的橙色；3D 橙色球体 / 黑色金属环做章节页和封面的视觉主角。
2. 标题是又粗又紧的大字（思源黑体 Black），英文全大写；左上对齐，正文很小。
3. 左边缘一根橙色竖条做「书脊」；右上角橙色方块小徽标。
4. 数据图极简：深灰柱 + 最后一根橙色，细基线，没有网格和边框。
5. 内容页大量留白，数字用无衬线粗体。
"""
from core import W, H, MX, mix, rgb
from layouts import _roll, _ghost, _donut_arcs
from designs.kit import bg, asset, photo, split, tw, bignum, plain

BLACK, PANEL, LINE, WHITE, GREY, DIM, ORANGE = '0B0B0C', '141416', '2A2A2E', 'F4F4F2', '9A9AA0', '55555B', 'FF6A1A'
HEAD = 'Space Grotesk|Noto Sans SC Black'
NUM = 'Space Grotesk|Noto Sans SC'
SANS = 'Inter|Noto Sans SC'
D = 'ember'


def _frame(c, deck, source=None, spine=True):
    if spine: c.rect(0, 0, .09, H, fill=ORANGE)
    c.text(W - MX - 2, .32, 2, .26, f'{c.idx:02d} / {deck.get("_total", 13):02d}', 10, GREY, align='r', font=SANS)
    c.text(MX, H - .48, 6, .26, ('来源：' + source) if source else deck.get('masthead', ''), 10, DIM, font=SANS)


def _badge(c, glyph='✦'):
    c.a(c.rect(W - MX - .55, .85, .55, .55, fill=ORANGE), 'pop', at=0, dur=400)
    c.a(c.text(W - MX - .55, .85, .55, .55, glyph, 18, BLACK, align='c', anchor='m', font=SANS), 'pop', at=0, dur=400)


def _head(c, text, y=.8, size=40, w=None, at=0):
    t = c.text(MX, y, w or W - 2 * MX - 1, 1.4, plain(text), size, WHITE, bold=True, font=HEAD, spacing=1.0)
    return c.a(t, 'rise', at=at, dur=700)


# ------------------------------------------------------------------ 页面
def cover(c, s, deck):
    bg(c, BLACK)
    photo(c, asset(D, 'hero', s, deck), 3.2, 0, W - 3.2, H, dur=1400)
    c.scrim(3.2, 0, 4, H, BLACK, 'left', 1.0)
    _frame(c, deck)
    lines = s['title'] if isinstance(s['title'], list) else [s['title']]
    c.a(c.text(MX, 1.0, 7, .3, s.get('kicker', '').upper(), 11, ORANGE, bold=True, font=SANS, tracking=2), 'fade', at=100)
    c.a(c.text(MX, 1.55, 7.5, 3.2, lines, 66, WHITE, bold=True, font=HEAD, spacing=.98, para_gap=0), 'rise', at=200, dur=900)
    if s.get('subtitle'): c.a(c.text(MX, 4.15, 5.5, .8, s['subtitle'], 14, GREY, font=SANS, spacing=1.4), 'fade', gap=200)
    for i, it in enumerate(s.get('stats') or []):
        x = MX + i * 2.0
        c.a(c.text(x, H - 1.85, 1.9, .3, it['label'], 10.5, GREY, font=SANS), 'fade', gap=60)
        c.counter(x, H - 1.55, 1.9, .7, it['value'], 30, ORANGE if i == 0 else WHITE, gap=0, bold=True)


def kpi(c, s, deck):
    bg(c, BLACK); _frame(c, deck, s.get('source')); _badge(c, '✦')
    _head(c, s['title'], size=36)
    items = s['items']; n = len(items); cw = (W - 2 * MX) / n; y = 2.6
    for i, it in enumerate(items):
        x = MX + i * cw; hl = it.get('highlight')
        c.a(c.text(x, y, cw - .3, .3, it['label'].upper(), 11, ORANGE if hl else GREY, bold=True, font=SANS, tracking=1), 'fade', gap=100)
        pre, num, unit = split(it['value'])
        bignum(c, x - .03, y + .4, it['value'], 76, WHITE, NUM, unit_font=HEAD, unit_scale=.24, bold=True, gap=0, dur=1000)
        c.a(c.text(x, y + 1.75, cw - .4, .6, it.get('delta', ''), 12, GREY, font=SANS), 'fade', gap=0)
    sp = s.get('split')
    if sp:
        parts = sp['parts']; tot = sum(p['value'] for p in parts); x = MX; y2 = 5.45; bw = W - 2 * MX
        c.a(c.text(MX, y2 - .45, 8, .3, sp.get('title', ''), 11, GREY, font=SANS), 'fade', gap=100)
        base = c.clock
        for k, p in enumerate(parts):
            w = bw * p['value'] / tot
            col = ORANGE if k == 0 else ['3A3A40', '2C2C31', '222226'][min(k - 1, 2)]
            c.a(c.rect(x, y2, w - .04, .42, fill=col), 'wipe-right', at=base + k * 200, hold=True, dur=500)
            c.a(c.text(x + .12, y2 + .52, w, .3, f"{p['name']} {p.get('label', '')}", 11, WHITE if k == 0 else GREY, font=SANS), 'fade', at=base + k * 200 + 200, hold=True)
            x += w


def section(c, s, deck):
    bg(c, BLACK)
    photo(c, asset(D, 'ring', s, deck), dur=1300)
    c.scrim(0, 0, W, H, BLACK, 'left', .9)
    _frame(c, deck)
    c.a(c.text(MX, 2.1, 3, .4, s.get('no', ''), 16, ORANGE, bold=True, font=SANS), 'fade', at=200)
    c.a(c.text(MX, 2.55, 10.5, 2.4, s['title'], 62, WHITE, bold=True, font=HEAD, spacing=1.0), 'rise', at=300, dur=900)
    if s.get('subtitle'): c.a(c.text(MX, 4.75, 6, .5, s['subtitle'], 14, GREY, font=SANS), 'fade', gap=200)


def chart(c, s, deck):
    """竖柱：深灰柱 + 重点橙柱，数字在柱顶，左侧标题和一句话"""
    bg(c, BLACK); _frame(c, deck, s.get('source')); _badge(c, '↗')
    _head(c, s['title'], size=28, w=4.8)
    ins = s.get('insights') or []
    if ins: c.a(c.text(MX, 2.6, 4.2, 1.6, plain(ins[0]), 13, GREY, font=SANS, spacing=1.5), 'fade', gap=150)
    ch = s['chart']; cats = ch['categories']; vals = ch['series'][0]['values']; hl = ch.get('highlight', 0)
    x0 = 6.0; x1 = W - MX; bottom = H - 1.3; ph = 4.2; n = len(cats); cw = (x1 - x0) / n; bw = cw * .42; vmax = max(vals)
    c.rect(x0, bottom, x1 - x0, .012, fill=LINE)
    base = c.clock + 100
    for i, (cat, v) in enumerate(zip(cats, vals)):
        h = ph * v / vmax; x = x0 + i * cw + (cw - bw) / 2; on = i == hl
        c.a(c.rect(x, bottom - h, bw, h, fill=ORANGE if on else '2E2E33'), 'wipe-up', at=base + i * 90, hold=True, dur=800)
        c.a(c.text(x - .3, bottom - h - .45, bw + .6, .35, f'{v:g}', 15 if on else 12, ORANGE if on else WHITE, bold=True, align='c', font=NUM), 'fade', at=base + i * 90 + 500, hold=True)
        c.a(c.text(x - .4, bottom + .12, bw + .8, .3, cat, 10.5, WHITE if on else GREY, align='c', font=SANS), 'fade', at=base + i * 90, hold=True)


def donut_story(c, s, deck):
    """橙色环形图（借用通用环形动画），黑底、粗标题"""
    bg(c, BLACK); _frame(c, deck, s.get('source'))
    cont = s.get('continue'); prev = deck['slides'][c.idx - 2] if cont else None
    segs = s['segments']; tot = sum(g['value'] for g in segs)
    cols = ['2E2E33', ORANGE]; cx, cy, d = 3.6, 4.2, 4.4
    if prev:
        c.a(_ghost(c, c.text(MX, .8, 10, 1.2, plain(prev['title']), 36, WHITE, bold=True, font=HEAD)), 'out', at=0, hold=True, dur=250, grp=1)
        c.a(c.text(MX, .8, 10, 1.2, plain(s['title']), 36, WHITE, bold=True, font=HEAD), 'fade', at=200, hold=True, dur=400)
        pv = [g['value'] / tot for g in prev['segments']]; nv = [g['value'] / tot for g in segs]
        from layouts import GHOST
        first = c.s.shapes.add_group_shape(_donut_arcs(c, pv, cols, cx, cy, d, dy=GHOST))
        c.a(first, 'appear', at=0, hold=True, dur=1, params={'dy': GHOST / H}); c.a(first, 'cut', at=400, hold=True, dur=1, grp=1)
        ease = lambda k: 4 * k ** 3 if k < .5 else 1 - (-2 * k + 2) ** 3 / 2
        for i in range(24):
            k = ease(i / 24); vals = [a + (b - a) * k for a, b in zip(pv, nv)]; off = H + 1 + i * .02
            g = c.s.shapes.add_group_shape(_donut_arcs(c, vals, cols, cx, cy, d, dy=off))
            c.a(g, 'appear', at=400 + 45 * i, hold=True, dur=1, params={'dy': off / H}); c.a(g, 'cut', at=400 + 45 * (i + 1), hold=True, dur=1, grp=1)
        c.a(c.s.shapes.add_group_shape(_donut_arcs(c, nv, cols, cx, cy, d)), 'appear', at=400 + 45 * 24, hold=True, dur=1)
    else:
        _head(c, s['title'], size=36)
        for a in _donut_arcs(c, [g['value'] / tot for g in segs], cols, cx, cy, d):
            c.a(a, 'wheel', at=300, hold=True, dur=1000)
    for k, g in enumerate(segs):
        x = 7.2 + k * 2.9; col = ORANGE if k else WHITE
        c.text(x, 2.8, 2.7, .3, g['name'].upper(), 11, ORANGE if k else GREY, bold=True, font=SANS)
        if prev: _roll(c, x, 3.15, 2.8, 1.2, prev['segments'][k]['label'], g['label'], 46, col, 400, 1100, bold=True, font=NUM)
        else: c.a(c.text(x, 3.15, 2.8, 1.2, g['label'], 46, col, bold=True, font=NUM), 'fade-up', at=800, hold=True)
    if prev:
        for k, an in enumerate(s.get('annotations', [])):
            c.a(c.text(7.2 + k * 2.9, 4.6, 2.6, 1, an['text'], 12, GREY, font=SANS, spacing=1.4), 'fade', at=1600, hold=True)
    elif s.get('teaser'):
        c.a(c.text(7.2, 4.8, 5.5, .5, s['teaser'].upper() + ' →', 18, ORANGE, bold=True, font=HEAD), 'fade', at=1400)


def timeline(c, s, deck):
    """路线图（参考 Product Roadmap）：横向时间刻度 + 一条条橙色进度条，越往后越长"""
    bg(c, BLACK); _frame(c, deck, s.get('source')); _badge(c, '→')
    _head(c, s['title'], size=32)
    items = s['items']; n = len(items); x0 = 3.2; x1 = W - MX; cw = (x1 - x0) / n
    ch = s.get('chart') or {}; vals = ch.get('line') or [0] * n
    for i, it in enumerate(items):
        x = x0 + i * cw
        c.a(c.text(x, 2.2, cw, .3, it['time'], 12, ORANGE if it.get('highlight') else GREY, bold=True, font=NUM), 'fade', gap=60)
        c.rect(x, 2.6, .01, H - 3.6, fill=LINE)
    for i, it in enumerate(items):
        y = 3.0 + i * .95; hl = it.get('highlight')
        c.a(c.text(MX, y, 2.3, .5, it['title'], 17, WHITE if hl else GREY, bold=True, font=HEAD), 'fade', gap=80)
        c.a(c.text(MX, y + .4, 2.3, .4, it.get('text', ''), 10.5, DIM, font=SANS), 'fade', gap=0)
        w = cw * (n - i) - .2
        c.a(c.rect(x0 + i * cw, y + .12, w, .36, fill=ORANGE if hl else '2E2E33'), 'wipe-right', gap=0, dur=700)
        c.a(c.text(x0 + i * cw + .15, y + .12, 2, .36, f'{vals[i]:g}%', 12, BLACK if hl else WHITE, bold=True, anchor='m', font=NUM), 'fade', gap=300)
    if ch.get('line_name'): c.text(x0, H - .95, 6, .3, '百分比 = ' + ch['line_name'], 10.5, DIM, font=SANS)


def table(c, s, deck):
    bg(c, BLACK); _frame(c, deck, s.get('source')); _badge(c, '≡')
    _head(c, s['title'], size=32)
    cols = s['columns']; rows = s['rows']; hl = s.get('highlight_row')
    ws = [2.6, 2.4, 2.4, 2.2, 2.13]; y = 2.3; rh = .95; x = MX
    for j, col in enumerate(cols):
        c.text(x, y, ws[j], .3, col.upper(), 10.5, GREY, bold=True, font=SANS); x += ws[j]
    for i, r in enumerate(rows):
        yy = y + .45 + i * (rh + .1); on = i == hl
        c.a(c.rect(MX, yy, W - 2 * MX, rh, fill=ORANGE if on else PANEL), 'wipe-right', gap=120, dur=500)
        x = MX
        for j, v in enumerate(r):
            c.a(c.text(x + .2, yy, ws[j] - .2, rh, str(v), 34 if j == 1 else 14, BLACK if on else (WHITE if j < 2 else GREY), bold=j < 2, anchor='m',
                       font=NUM if j == 1 else (HEAD if j == 0 else SANS)), 'fade', gap=30)
            x += ws[j]
    if s.get('summary'): c.a(c.text(MX, H - 1.2, 10, .5, plain(s['summary']), 15, WHITE, font=SANS), 'fade', gap=150)


def process(c, s, deck):
    bg(c, BLACK); _frame(c, deck); _badge(c, '→')
    _head(c, s['title'], size=36)
    st = s['steps']; n = len(st); cw = (W - 2 * MX) / n
    for i, it in enumerate(st):
        x = MX + i * cw; hl = it.get('highlight')
        c.a(c.rect(x, 2.5, cw - .3, .05, fill=ORANGE if hl else '3A3A40'), 'wipe-right', gap=120, dur=400)
        c.a(c.text(x, 2.75, cw - .3, 1.2, f'{i+1:02d}', 64, ORANGE if hl else WHITE, bold=True, font=NUM), 'fade-up', gap=0)
        c.a(c.text(x, 3.95, cw - .3, .5, it['title'], 20, WHITE, bold=True, font=HEAD), 'fade', gap=0)
        c.a(c.text(x, 4.5, cw - .5, 1, it.get('text', ''), 12, GREY, font=SANS, spacing=1.45), 'fade', gap=0)


def stat(c, s, deck):
    bg(c, BLACK)
    photo(c, asset(D, 'cluster', s, deck), 4.5, 0, W - 4.5, H, dur=1200)
    c.scrim(4.5, 0, 4, H, BLACK, 'left', 1.0)
    _frame(c, deck, s.get('source'))
    c.a(c.text(MX, 1.0, 6, .3, s.get('kicker', '').upper(), 11, ORANGE, bold=True, font=SANS, tracking=2), 'fade', at=0)
    c.a(c.text(MX, 1.4, 6, .6, s.get('label', ''), 24, WHITE, bold=True, font=HEAD), 'rise', at=100)
    c.clock = 300
    bignum(c, MX - .1, 2.2, s['value'], 200, ORANGE, NUM, unit_font=NUM, unit_scale=.3, bold=True, gap=0, dur=1300)
    if s.get('delta'): c.a(c.text(MX, 5.2, 6, .4, '▲ ' + s['delta'], 14, WHITE, bold=True, font=SANS), 'fade', gap=100)
    if s.get('text'): c.a(c.text(MX, 5.65, 5.5, .6, s['text'], 12, GREY, font=SANS, spacing=1.4), 'fade', gap=0)


def compare(c, s, deck):
    bg(c, BLACK); _frame(c, deck); _badge(c, '×')
    _head(c, s['title'], size=34)
    gw = (W - 2 * MX - .3) / 2
    for k, side in enumerate(('left', 'right')):
        d = s[side]; x = MX + k * (gw + .3); hl = k == 1
        c.a(c.rect(x, 2.3, gw, H - 3.2, fill=PANEL), 'fade-up', gap=150, dur=500)
        if hl: c.a(c.rect(x, 2.3, gw, .07, fill=ORANGE), 'wipe-right', gap=0, dur=500)
        c.a(c.text(x + .4, 2.65, gw - .8, .3, d.get('tag', '').upper(), 11, ORANGE if hl else GREY, bold=True, font=SANS), 'fade', gap=60)
        c.a(c.text(x + .4, 3.0, gw - .8, .7, d['title'], 26, WHITE if hl else GREY, bold=True, font=HEAD), 'fade', gap=0)
        for j, it in enumerate(d['items']):
            c.a(c.text(x + .4, 4.0 + j * .5, gw - .8, .4, ('→  ' if hl else '·  ') + it, 14, WHITE if hl else GREY, font=SANS), 'fade', gap=50)


def quote(c, s, deck):
    bg(c, BLACK)
    photo(c, asset(D, 'ring', s, deck), dur=1200)
    c.a(c.rect(0, 0, W, H, fill=BLACK, alpha=.5), 'fade', at=0, dur=1)
    _frame(c, deck)
    txt = s['text'] if isinstance(s['text'], list) else [s['text']]
    c.a(c.text(MX, 2.4, W - 2 * MX, 2.6, txt, 44, WHITE, bold=True, font=HEAD, spacing=1.2, em_color=ORANGE, para_gap=.1), 'rise', at=300, dur=900)
    if s.get('by'): c.a(c.text(MX, 4.9, 6, .4, s['by'].upper(), 12, ORANGE, bold=True, font=SANS, tracking=1), 'fade', gap=300)


def end(c, s, deck):
    bg(c, BLACK)
    photo(c, asset(D, 'hero', s, deck), dur=1200)
    c.scrim(0, 0, W, H, BLACK, 'left', .95)
    _frame(c, deck)
    c.a(c.text(MX, 2.6, 8, 1.4, s.get('title', ''), 64, WHITE, bold=True, font=HEAD), 'rise', at=300, dur=900)
    if s.get('subtitle'): c.a(c.text(MX, 3.85, 7, .5, s['subtitle'], 14, ORANGE, bold=True, font=SANS), 'fade', gap=200)


LAYOUTS = {'cover': cover, 'kpi': kpi, 'section': section, 'chart': chart, 'donut_story': donut_story,
           'timeline': timeline, 'table': table, 'process': process, 'stat': stat, 'compare': compare,
           'quote': quote, 'end': end}
