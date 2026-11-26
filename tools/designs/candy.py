"""设计系统 D「Y2K 糖果」：参考 Pitch · Lucid。

拆解：
1. 紫-粉-黄柔和渐变做底；3D 糖果 / 镀铬物件做主角（封面、章节、配图栏）。
2. 内容放在大圆角白色面板上，和渐变底形成「窗口」感。
3. 标题竖排贴在右边缘（旋转 90°），字体是有个性的得意黑。
4. 色彩跳跃但只用三色：紫、粉、黄，深紫做文字。
5. 形状全是胶囊和大圆角，没有直角。
"""
from core import W, H, MX, mix, rgb
from layouts import _roll, _ghost, _donut_arcs, GHOST
from designs.kit import bg, asset, photo, split, tw, bignum, plain

INK, PURPLE, PINK, YELLOW, LILAC, WHITE, GREY = '231942', '7B5CFF', 'FF5FA8', 'FFC23C', 'E4DAFF', 'FFFFFF', '7D7395'
FUN = 'Smiley Sans'
BODY = 'Space Grotesk|Noto Sans SC'
D = 'candy'
R = .3


def _grad(c):
    bg(c, 'F3D9F0'); photo(c, asset(D, 'grad'), dur=1, anim='appear')


def _frame(c, deck, source=None, dark=False):
    col = INK if not dark else WHITE
    c.text(MX, .32, 6, .26, deck.get('masthead', ''), 10.5, col, font=BODY)
    c.text(W - MX - 2, .32, 2, .26, f'{c.idx:02d}', 10.5, col, align='r', font=BODY)
    if source: c.text(MX, H - .45, 8, .26, '来源：' + source, 10, GREY, font=BODY)


def _vtitle(c, text, x=None, size=34, color=INK, at=0):
    """竖排标题：文字框转 90°，贴在右边缘"""
    L = H - 1.4; hh = size / 72 * 2.6; cx = (x if x is not None else W - .75); cy = H / 2
    t = c.text(cx - L / 2, cy - hh / 2, L, hh, plain(text), size, color, font=FUN, align='l', anchor='m', spacing=1.0)
    t.rotation = 90
    return c.a(t, 'fade', at=at, dur=600)


def _panel(c, x, y, w, h, fill=WHITE, at=None, gap=0, line=None):
    return c.a(c.rect(x, y, w, h, fill=fill, radius=R, line=line, lw=2.5), 'zoom', at=at, gap=gap, dur=500)


# ------------------------------------------------------------------ 页面
def cover(c, s, deck):
    bg(c, 'F3D9F0'); photo(c, asset(D, 'robot', s, deck), dur=1000)
    _frame(c, deck)
    lines = s['title'] if isinstance(s['title'], list) else [s['title']]
    c.a(c.rect(MX, 1.3, tw(s.get('kicker', ''), 11) + .6, .4, fill=WHITE, radius=.2), 'zoom', at=100)
    c.a(c.text(MX, 1.3, tw(s.get('kicker', ''), 11) + .6, .4, s.get('kicker', ''), 11, PURPLE, align='c', anchor='m', font=BODY), 'fade', at=150)
    c.a(c.text(MX, 2.0, 6.6, 3, lines, 62, INK, font=FUN, spacing=1.0, para_gap=0), 'rise', at=250, dur=800)
    if s.get('subtitle'): c.a(c.text(MX, 4.6, 6, .5, s['subtitle'], 15, INK, font=BODY), 'fade', gap=200)
    for i, it in enumerate(s.get('stats') or []):
        x = MX + i * 2.05
        _panel(c, x, H - 1.75, 1.85, 1.05, gap=80)
        c.a(c.text(x + .2, H - 1.65, 1.6, .3, it['label'], 10.5, GREY, font=BODY), 'fade', gap=0)
        c.counter(x + .2, H - 1.35, 1.6, .6, it['value'], 28, [PURPLE, PINK, INK][i % 3], gap=0, bold=False)


def kpi(c, s, deck):
    """左：3D 配图栏；右：白面板里三个大数字竖着排；最右竖排标题"""
    _grad(c)
    photo(c, asset(D, 'cursor', s, deck), 0, 0, 4.6, H, dur=900)
    _panel(c, 4.9, .7, W - 4.9 - 1.6, H - 1.4, at=100)
    _frame(c, deck, s.get('source'))
    _vtitle(c, s['title'], size=30, at=200)
    items = s['items']; x = 5.4; y0 = 1.1; rh = (H - 2.3) / len(items)
    cols = [PURPLE, PINK, INK]
    for i, it in enumerate(items):
        y = y0 + i * rh
        c.a(c.text(x, y + .15, 2.4, .3, it['label'], 12, GREY, font=BODY), 'fade', gap=100)
        c.a(c.text(x, y + .5, 2.6, .6, it.get('delta', ''), 11, INK, font=BODY), 'fade', gap=0)
        bignum(c, x + 2.7, y - .05, it['value'], 64, cols[i % 3], FUN, unit_font=FUN, unit_scale=.35, gap=0, dur=900, unit_pos='base', k=.78)
        if i < len(items) - 1: c.rect(x, y + rh - .1, W - x - 2.1, .012, fill=LILAC)


def section(c, s, deck):
    bg(c, 'F3D9F0'); photo(c, asset(D, 'bubble', s, deck), dur=1000)
    _frame(c, deck)
    c.a(c.text(MX, 2.0, 3, 1.2, s.get('no', ''), 80, WHITE, font=FUN), 'pop', at=100)
    c.a(c.text(MX, 3.3, 7, 1.4, s['title'], 56, INK, font=FUN), 'rise', at=300, dur=800)
    if s.get('subtitle'): c.a(c.text(MX, 4.5, 6, .5, s['subtitle'], 15, INK, font=BODY), 'fade', gap=200)


def chart(c, s, deck):
    """白面板 + 胶囊横条（重点条紫色，其余淡紫），竖排标题"""
    _grad(c); _panel(c, .6, .7, W - 2.3, H - 1.4, at=0)
    _frame(c, deck, s.get('source')); _vtitle(c, s['title'], size=30, at=100)
    ch = s['chart']; cats = ch['categories']; vals = ch['series'][0]['values']; hl = ch.get('highlight', 0)
    x0 = 1.2; x1 = W - 2.6; rh = (H - 2.6) / len(cats); vmax = max(vals)
    ins = s.get('insights') or []
    if ins: c.a(c.text(x0, 1.05, 8, .4, plain(ins[0]), 13, INK, font=BODY), 'fade', at=200)
    base = 350
    for i, (cat, v) in enumerate(zip(cats, vals)):
        y = 1.7 + i * rh; on = i == hl
        c.a(c.text(x0, y, 1.6, rh * .8, cat, 14, INK, font=BODY, anchor='m'), 'fade', at=base + i * 90, hold=True)
        bw = (x1 - x0 - 2.8) * v / vmax
        c.a(c.rect(x0 + 1.7, y + rh * .12, bw, rh * .56, fill=PURPLE if on else LILAC, radius=rh * .28), 'wipe-right', at=base + i * 90, hold=True, dur=800)
        c.a(c.text(x0 + 1.85 + bw, y, 1, rh * .8, f'{v:g}', 26, PURPLE if on else INK, font=FUN, anchor='m'), 'fade', at=base + i * 90 + 500, hold=True)


def donut_story(c, s, deck):
    _grad(c); _panel(c, .6, .7, W - 2.3, H - 1.4, at=None if s.get('continue') else 0)
    _frame(c, deck, s.get('source'))
    cont = s.get('continue'); prev = deck['slides'][c.idx - 2] if cont else None
    segs = s['segments']; tot = sum(g['value'] for g in segs)
    cols = [LILAC, PINK]; cx, cy, d = 3.6, 4.0, 4.4
    if prev:
        t_old = _ghost(c, c.text(W - .75 - (H - 1.4) / 2, H / 2 - 1.1 / 2, H - 1.4, 1.1, plain(prev['title']), 30, INK, font=FUN, anchor='m'))
        t_old.rotation = 90; c.a(t_old, 'out', at=0, hold=True, dur=250, grp=1)
        _vtitle(c, s['title'], size=30, at=250)
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
        _vtitle(c, s['title'], size=30, at=100)
        for a in _donut_arcs(c, [g['value'] / tot for g in segs], cols, cx, cy, d):
            c.a(a, 'wheel', at=300, hold=True, dur=1000)
    c.text(cx - 1.2, cy - .45, 2.4, .9, '40 小时', 30, INK, align='c', anchor='m', font=FUN)
    for k, g in enumerate(segs):
        x = 6.6 + k * 2.4; col = PINK if k else PURPLE
        c.rect(x, 2.0, .3, .3, fill=cols[k], radius=.15)
        c.text(x + .45, 1.95, 2, .4, g['name'], 14, INK, font=BODY)
        if prev: _roll(c, x, 2.45, 2.3, 1.1, prev['segments'][k]['label'], g['label'], 50, col, 400, 1100, font=FUN)
        else: c.a(c.text(x, 2.45, 2.3, 1.1, g['label'], 50, col, font=FUN), 'fade-up', at=800, hold=True)
    if prev:
        for k, an in enumerate(s.get('annotations', [])):
            c.a(c.text(6.6 + k * 2.4, 3.8, 2.2, 1.2, an['text'], 12, INK, font=BODY, spacing=1.4), 'fade', at=1600, hold=True)
    elif s.get('teaser'):
        c.a(c.rect(6.6, 4.3, 4.2, .7, fill=YELLOW, radius=.35), 'zoom', at=1300)
        c.a(c.text(6.6, 4.3, 4.2, .7, s['teaser'] + ' →', 18, INK, align='c', anchor='m', font=FUN), 'fade', at=1400)


def timeline(c, s, deck):
    """胶囊阶梯：每年一颗胶囊，越来越高越来越亮"""
    _grad(c); _frame(c, deck, s.get('source')); _vtitle(c, s['title'], size=30, at=0)
    items = s['items']; n = len(items); x0 = MX; x1 = W - 2.0; cw = (x1 - x0) / n
    ch = s.get('chart') or {}; vals = ch.get('line') or [0] * n
    fills = [WHITE, LILAC, PINK, PURPLE]; inks = [INK, INK, WHITE, WHITE]
    bottom = H - 1.0
    for i, it in enumerate(items):
        h = 2.6 + i * .8; x = x0 + i * cw + .1; w = cw - .25
        c.a(c.rect(x, bottom - h, w, h, fill=fills[i % 4], radius=w / 2 * .98), 'wipe-up', at=150 + i * 160, hold=True, dur=700)
        c.a(c.text(x, bottom - h + .3, w, .9, f'{vals[i]:g}%', 40, inks[i % 4], align='c', font=FUN), 'pop', at=600 + i * 160, hold=True)
        c.a(c.text(x, bottom - h + 1.15, w, .35, it['time'], 12, inks[i % 4], align='c', font=BODY), 'fade', at=600 + i * 160, hold=True)
        c.a(c.text(x + .1, bottom - .9, w - .2, .6, it['title'], 18, inks[i % 4], align='c', font=FUN), 'fade', at=600 + i * 160, hold=True)
    if ch.get('line_name'): c.text(MX, .85, 6, .3, '百分比 = ' + ch['line_name'], 11, INK, font=BODY)


def table(c, s, deck):
    _grad(c); _panel(c, .6, .7, W - 2.3, H - 1.4, at=0)
    _frame(c, deck, s.get('source')); _vtitle(c, s['title'], size=30, at=100)
    cols = s['columns']; rows = s['rows']; hl = s.get('highlight_row')
    ws = [2.2, 2.2, 2.0, 1.9, 1.8]; x0 = 1.1; y = 1.3; rh = 1.0; x = x0
    for j, col in enumerate(cols):
        c.text(x, y, ws[j], .3, col, 11, GREY, font=BODY); x += ws[j]
    for i, r in enumerate(rows):
        yy = y + .5 + i * (rh + .15); on = i == hl
        c.a(c.rect(x0 - .2, yy, sum(ws) + .3, rh, fill=PINK if on else 'F6F2FF', radius=rh / 2), 'zoom', gap=150, dur=450)
        x = x0
        for j, v in enumerate(r):
            c.a(c.text(x, yy, ws[j], rh, str(v), 34 if j == 1 else 14, WHITE if on else INK, anchor='m', font=FUN if j < 2 else BODY), 'fade', gap=30)
            x += ws[j]
    if s.get('summary'): c.a(c.text(x0, H - 1.6, 9, .5, plain(s['summary']), 15, INK, font=BODY), 'fade', gap=150)


def process(c, s, deck):
    _grad(c); _frame(c, deck); _vtitle(c, s['title'], size=30, at=0)
    st = s['steps']; n = len(st); x0 = MX; cw = (W - 2.0 - x0) / n
    fills = [WHITE, YELLOW, PINK, PURPLE]; inks = [INK, INK, WHITE, WHITE]
    for i, it in enumerate(st):
        x = x0 + i * cw; h = 2.8 + i * .7; y = H - .9 - h; hl = it.get('highlight')
        c.a(c.rect(x, y, cw - .2, h, fill=fills[i % 4], radius=R), 'rise', at=150 + i * 150, hold=True, dur=600)
        c.a(c.text(x + .3, y + .25, cw - .6, 1, f'{i+1:02d}', 54, inks[i % 4], font=FUN), 'pop', at=400 + i * 150, hold=True)
        c.a(c.text(x + .3, y + 1.3, cw - .6, .6, it['title'], 24, inks[i % 4], font=FUN), 'fade', at=450 + i * 150, hold=True)
        c.a(c.text(x + .3, y + 1.95, cw - .6, 1, it.get('text', ''), 12, inks[i % 4], font=BODY, spacing=1.4), 'fade', at=500 + i * 150, hold=True)
    if s.get('summary'): c.a(c.text(MX, 1.0, 7, .5, s['summary'], 15, INK, font=BODY), 'fade', at=900)


def stat(c, s, deck):
    bg(c, 'F3D9F0'); photo(c, asset(D, 'robot', s, deck), dur=900)
    _frame(c, deck, s.get('source'))
    c.a(c.text(MX, 1.2, 6, .5, s.get('label', ''), 20, INK, font=FUN), 'fade', at=0)
    c.clock = 200
    bignum(c, MX - .1, 1.8, s['value'], 220, PURPLE, FUN, unit_font=FUN, unit_scale=.35, gap=0, dur=1300, k=.78)
    if s.get('delta'):
        c.a(c.rect(MX, 5.35, 3.6, .55, fill=WHITE, radius=.27), 'zoom', gap=100)
        c.a(c.text(MX, 5.35, 3.6, .55, '▲ ' + s['delta'], 13, PINK, align='c', anchor='m', font=BODY), 'fade', gap=0)
    if s.get('text'): c.a(c.text(MX, 6.1, 6, .5, s['text'], 12, INK, font=BODY), 'fade', gap=0)


def compare(c, s, deck):
    _grad(c); _frame(c, deck); _vtitle(c, s['title'], size=30, at=0)
    gw = (W - 2.0 - MX - .3) / 2
    for k, side in enumerate(('left', 'right')):
        d = s[side]; x = MX + k * (gw + .3); hl = k == 1
        _panel(c, x, .9, gw, H - 1.7, fill=WHITE if hl else 'EDE6F7', line=PURPLE if hl else None, gap=150)
        c.a(c.rect(x + .4, 1.3, tw(d.get('tag', ''), 12) + .5, .4, fill=PURPLE if hl else GREY, radius=.2), 'zoom', gap=60)
        c.a(c.text(x + .4, 1.3, tw(d.get('tag', ''), 12) + .5, .4, d.get('tag', ''), 12, WHITE, align='c', anchor='m', font=BODY), 'fade', gap=0)
        c.a(c.text(x + .4, 1.95, gw - .8, .8, d['title'], 32, INK if hl else GREY, font=FUN), 'fade', gap=0)
        for j, it in enumerate(d['items']):
            c.a(c.text(x + .4, 3.1 + j * .6, gw - .8, .5, ('✓  ' if hl else '✗  ') + it, 15, INK if hl else GREY, font=BODY), 'fade', gap=50)


def quote(c, s, deck):
    _grad(c); _frame(c, deck)
    _panel(c, 1.2, 1.3, W - 2.4, H - 2.6, at=0)
    txt = s['text'] if isinstance(s['text'], list) else [s['text']]
    c.a(c.text(1.8, 2.3, W - 3.6, 2.4, txt, 40, INK, align='c', font=FUN, spacing=1.25, em_color=PURPLE, para_gap=.1), 'rise', at=300, dur=800)
    if s.get('by'): c.a(c.text(0, 4.9, W, .4, s['by'], 13, GREY, align='c', font=BODY), 'fade', gap=300)


def end(c, s, deck):
    bg(c, 'F3D9F0'); photo(c, asset(D, 'bubble', s, deck), dur=900)
    _frame(c, deck)
    c.a(c.text(MX, 2.6, 7.5, 1.5, s.get('title', ''), 60, INK, font=FUN), 'rise', at=300, dur=800)
    if s.get('subtitle'): c.a(c.text(MX, 3.9, 7, .5, s['subtitle'], 15, INK, font=BODY), 'fade', gap=200)
    c.confetti(W / 2, 3.0, start=600, colors=[PURPLE, PINK, YELLOW, WHITE])


LAYOUTS = {'cover': cover, 'kpi': kpi, 'section': section, 'chart': chart, 'donut_story': donut_story,
           'timeline': timeline, 'table': table, 'process': process, 'stat': stat, 'compare': compare,
           'quote': quote, 'end': end}
