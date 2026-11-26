"""设计系统 A「薄荷数据」：参考 Capitalo 金融报告（Dribbble · Panthera Designs）。

拆解（每条都要在页面上看得出来）：
1. 两种颜色撑全场：藏青 + 薄荷绿；浅色页用纸白 + 钢蓝做第三色。不用渐变、不用阴影、不用卡片描边。
2. 数字是主角：细体（Light）超大字号 120–260pt，单位做成右上角小字；标签缩成 11pt 注脚。
3. 图表用「方块」：华夫格 / 方块条代替柱状图和饼图，一格 = 一个单位，数据有颗粒感。
4. 深色页、浅色页、满版大字页交替；版式按页型各不相同，不共用「标题 + 卡片网格」骨架。
5. 页框极轻：左上小圆标 + 刊名，右上 [02] 页码，左下来源。
"""
import re
from core import W, H, MX, mix, rgb
from layouts import _roll, _ghost, GHOST

NAVY, NAVY2, MINT, STEEL, PAPER, INK, GREY, WHITE = '1D2744', '26325A', '74F0A4', '6F9CCB', 'F3F4F6', '18203A', '8B93A7', 'FFFFFF'
NUM = 'Space Grotesk Light|Noto Sans SC Light'
LIGHT = 'Noto Sans SC Light'
BODY = 'Space Grotesk|Noto Sans SC'


def _bg(c, col):
    f = c.s.background.fill; f.solid(); f.fore_color.rgb = rgb(col)


def _frame(c, deck, dark=True, source=None):
    fg = WHITE if dark else INK; sub = mix(WHITE, NAVY, .55) if dark else GREY
    c.oval(MX + .09, .42, .18, line=fg, lw=1.5)
    c.text(MX + .3, .3, 5, .26, deck.get('masthead', ''), 10.5, fg, font=BODY)
    c.text(W - MX - 1.2, .3, 1.2, .26, f'[{c.idx:02d}]', 10.5, sub, align='r', font=BODY)
    if source: c.text(MX, H - .5, 8, .26, '来源：' + source, 10, sub, font=BODY)


def _w(s, size):
    """估算细体文字宽度（英寸）"""
    wd = {'1': .42, '.': .24, ',': .24, ':': .26, '%': .82, ' ': .26}
    return sum(1.0 if ord(ch) > 0x2E80 else wd.get(ch, .6) for ch in s) * size / 72


def _split(v):
    m = re.match(r'^([^\d]*)([\d.,]+)(.*)$', str(v))
    return (m.group(1), m.group(2), m.group(3)) if m else ('', str(v), '')


def bignum(c, x, y, value, size, color, unit_color=None, gap=0, dur=1100, anim=True):
    """超大细体数字 + 右上角小单位（64%、11.5小时、4倍）"""
    pre, num, unit = _split(value)
    nw = _w(pre + num, size) + .06
    hh = size / 72 * 1.05
    if anim: c.counter(x, y, nw + .3, hh, pre + num, size, color, gap=gap, dur=dur, bold=False)
    else: c.text(x, y, nw + .3, hh, pre + num, size, color, font=NUM, spacing=1)
    if unit:
        us = max(14, size * .2)
        c.a(c.text(x + nw - size / 72 * .04, y + size / 72 * .14, _w(unit, us) + .2, us / 72 * 1.4, unit, us, unit_color or color, font=LIGHT), 'fade', gap=0, hold=True)
    return nw


def waffle(c, x, y, n, cols, cell, gap, colors, at=0, step_ms=18, radius=.035):
    """方块格：colors 为每格颜色列表（长度 n），逐格弹出"""
    shapes = []
    for i in range(n):
        cx = x + (i % cols) * (cell + gap); cy = y + (i // cols) * (cell + gap)
        r = c.rect(cx, cy, cell, cell, fill=colors[i], radius=radius)
        c.a(r, 'zoom', at=at + i * step_ms, hold=True, dur=300); shapes.append(r)
    return shapes


def _eyebrow(c, x, y, text, color):
    c.a(c.text(x, y, 6, .3, text, 11, color, font=BODY, tracking=1), 'fade', at=0)


# ------------------------------------------------------------------ 页面
def cover(c, s, deck):
    _bg(c, NAVY); _frame(c, deck)
    ring = c.oval(W - 1.6, 3.3, 7.6, line=MINT, lw=1, line_alpha=.35)
    c.a(ring, 'zoom', at=0, dur=1200)
    c.a(c.oval(W - 1.6, 3.3, 5.2, line=WHITE, lw=.75, line_alpha=.12), 'zoom', at=150, dur=1200)
    _eyebrow(c, MX, 1.45, s.get('kicker', ''), MINT)
    lines = s['title'] if isinstance(s['title'], list) else [s['title']]
    c.a(c.text(MX, 1.95, 9.5, 2.6, lines, 60, MINT, font=NUM, spacing=1.02, para_gap=0), 'fade-up', at=200, dur=900)
    if s.get('subtitle'):
        c.a(c.text(MX, 4.25, 6.5, .5, s['subtitle'], 16, mix(WHITE, NAVY, .75), font=LIGHT), 'fade', gap=200)
    st = s.get('stats') or []
    for i, it in enumerate(st):
        x = MX + i * 2.9; y = H - 2.05
        c.a(c.rect(x, y, 2.5, .012, fill=mix(WHITE, NAVY, .3)), 'wipe-right', gap=80, dur=400)
        c.a(c.text(x, y + .15, 2.5, .3, it['label'], 11, mix(WHITE, NAVY, .55), font=BODY), 'fade', gap=0)
        c.clock -= 0
        bignum(c, x - .03, y + .45, it['value'], 44, WHITE if i else MINT, gap=0, dur=900)
    if s.get('meta'): c.text(W - MX - 4, H - .5, 4, .26, s['meta'], 10.5, mix(WHITE, NAVY, .55), align='r', font=BODY)


def kpi(c, s, deck):
    """深色：左侧标签列 + 右侧三个巨型数字 + 下方方块构成条（参考 64% / 36% 那页）"""
    _bg(c, NAVY); _frame(c, deck, source=s.get('source'))
    _eyebrow(c, MX, 1.2, s.get('kicker', ''), MINT)
    c.a(c.text(MX, 1.55, 3.0, 1.6, s['title'].replace('**', ''), 24, WHITE, font=LIGHT, spacing=1.3), 'fade-up', gap=60)
    items = s['items']; x0 = 4.35; colw = (W - MX - x0) / len(items)
    for i, it in enumerate(items):
        x = x0 + i * colw; hl = it.get('highlight')
        c.a(c.text(x, 1.2, colw - .2, .3, it['label'], 11, mix(WHITE, NAVY, .6), font=BODY), 'fade', gap=60)
        u = _split(it['value'])[2]
        sz = min(110, int((colw - .35 - _w(u, 20)) / _w(_split(it['value'])[1], 1) ))
        bignum(c, x - .05, 1.55, it['value'], sz, MINT if hl else WHITE, gap=0, dur=1000)
        if it.get('delta'):
            c.a(c.text(x, 3.35, colw - .2, .3, it['delta'], 11, MINT if hl else mix(WHITE, NAVY, .6), font=BODY), 'fade', gap=0)
    sp = s.get('split')
    if sp:
        parts = sp['parts']; tot = sum(p['value'] for p in parts)
        n = int(round(tot * 2)); cols = 23; cell = (W - MX - x0 - .1 * (cols - 1)) / cols * .9
        gapx = ((W - MX - x0) - cell * cols) / (cols - 1)
        cols_ = [MINT, WHITE, STEEL, mix(WHITE, NAVY, .35)]
        colors = []
        for k, p in enumerate(parts): colors += [cols_[k % 4]] * int(round(p['value'] * 2))
        colors = (colors + [cols_[-1]] * n)[:n]
        y = 4.75
        c.a(c.text(x0, y - .45, 6, .3, sp.get('title', ''), 11, mix(WHITE, NAVY, .6), font=BODY), 'fade', gap=100)
        waffle(c, x0, y, n, cols, cell, gapx, colors, at=c.clock + 100, step_ms=25)
        ly = y + cell + .35; lx = x0
        for k, p in enumerate(parts):
            c.a(c.rect(lx, ly + .06, .16, .16, fill=cols_[k % 4], radius=.03), 'fade', at=c.clock + 700, hold=True)
            t = f"{p['name']}  {p.get('label', p['value'])}"
            c.a(c.text(lx + .25, ly, 2.4, .3, t, 11, WHITE, font=BODY), 'fade', at=c.clock + 700, hold=True)
            lx += _w(t, 11) + .75
        c.text(MX, 4.7, 3.2, .9, '每格 = 0.5 小时', 11, mix(WHITE, NAVY, .55), font=BODY)


def section(c, s, deck):
    _bg(c, NAVY); _frame(c, deck)
    c.a(c.oval(W - .9, H / 2 + .4, 8.5, line=MINT, lw=1, line_alpha=.3), 'zoom', at=0, dur=1300)
    c.a(c.text(MX, 1.3, 3, .4, f"[{s.get('no', '')}]", 14, MINT, font=BODY), 'fade', at=100)
    c.a(c.text(MX - .05, 2.0, 11, 3.2, s['title'], 76, MINT, font=NUM, spacing=1.0), 'fade-up', at=250, dur=900)
    if s.get('subtitle'):
        c.a(c.text(MX, H - 1.4, 6, .4, s['subtitle'], 14, mix(WHITE, NAVY, .65), font=LIGHT), 'fade', gap=200)


def chart(c, s, deck):
    """左白栏（标题在上、解读在下）+ 右侧方块条形图（参考 How consumers prioritize… 那页）"""
    _bg(c, PAPER)
    c.rect(0, 0, 4.9, H, fill=WHITE)
    _frame(c, deck, dark=False, source=s.get('source'))
    _eyebrow(c, MX, 1.15, s.get('kicker', ''), STEEL)
    c.a(c.text(MX, 1.5, 3.7, 1.8, s['title'].replace('**', ''), 26, INK, font=LIGHT, spacing=1.25), 'fade-up', gap=60)
    ins = s.get('insights') or []
    if ins:
        c.a(c.text(MX, H - 2.6, 3.6, 1.9, [x.replace('**', '') for x in ins[:2]], 11.5, mix(INK, WHITE, .75), font=BODY, spacing=1.5, para_gap=.6), 'fade', gap=150)
    ch = s['chart']; cats = ch['categories']; vals = ch['series'][0]['values']; hl = ch.get('highlight', 0)
    unit = ch.get('unit', '')
    x0 = 5.55; cell = .2; gx = .07; per = 4   # 每格 = 1/per 单位
    rowh = (H - 2.2) / len(cats); y0 = 1.15
    c.a(c.text(x0, y0 - .45, 5, .3, f'每格 = {1/per:g} {unit.split("/")[0]}', 10.5, GREY, font=BODY), 'fade', gap=100)
    base = c.clock + 150
    for i, (cat, v) in enumerate(zip(cats, vals)):
        y = y0 + i * rowh; on = i == hl
        c.a(c.text(x0, y, 1.1, .7, f'{v:g}', 30, NAVY if not on else INK, font=NUM, anchor='m'), 'fade', at=base + i * 120, hold=True)
        c.a(c.text(x0 + 1.15, y, 1.4, .7, cat, 11.5, INK if on else GREY, font=BODY, anchor='m'), 'fade', at=base + i * 120, hold=True)
        n = int(round(v * per))
        cols = [MINT if on else (NAVY if i < 3 else STEEL)] * n
        waffle(c, x0 + 2.55, y + .25, n, 40, cell, gx, cols, at=base + i * 120, step_ms=14)


def donut_story(c, s, deck):
    """一周 40 小时 = 40 个方块。第二页：11 个方块从藏青翻成薄荷绿，数字同步滚动（代替饼图变化）"""
    _bg(c, NAVY); _frame(c, deck, source=s.get('source'))
    cont = s.get('continue'); prev = deck['slides'][c.idx - 2] if cont else None
    segs = s['segments']; tot = sum(g['value'] for g in segs)
    title = s['title'].replace('**', '')
    if prev:   # 标题：旧的淡出、新的淡入
        old = _ghost(c, c.text(MX, 1.15, 7, 1.2, prev['title'].replace('**', ''), 28, WHITE, font=LIGHT))
        c.a(old, 'out', at=0, hold=True, dur=300, grp=1)
        c.a(c.text(MX, 1.15, 7, 1.2, title, 28, WHITE, font=LIGHT), 'fade', at=250, hold=True, dur=400)
    else:
        c.a(c.text(MX, 1.15, 7, 1.2, title, 28, WHITE, font=LIGHT), 'fade-up', at=0)
    cols, cell, gp = 10, .46, .1; x0 = MX; y0 = 2.75
    old_mint = (prev['segments'][1]['value'] if prev else segs[1]['value'])
    new_mint = segs[1]['value']
    colors = [NAVY2] * (tot - old_mint) + [MINT] * old_mint
    cells = []
    for i in range(tot):
        cx = x0 + (i % cols) * (cell + gp); cy = y0 + (i // cols) * (cell + gp)
        cells.append((cx, cy))
        r = c.rect(cx, cy, cell, cell, fill=colors[i], radius=.05)
        if not prev: c.a(r, 'zoom', at=200 + i * 20, hold=True, dur=300)
    c.text(x0, y0 + 4 * (cell + gp) + .1, 6, .3, '每格 = 1 小时', 10.5, mix(WHITE, NAVY, .55), font=BODY)
    # 右侧两列数字
    rx = 7.4
    for k, g in enumerate(segs):
        x = rx + k * 2.85; col = MINT if k == 1 else WHITE
        c.text(x, 2.75, 2.6, .3, g['name'], 12, mix(WHITE, NAVY, .65), font=BODY)
        c.rect(x, 3.12, .3, .3, fill=MINT if k == 1 else NAVY2, radius=.04, line=None if k else mix(WHITE, NAVY, .4), lw=.75)
        if prev:
            pg = prev['segments'][k]
            _roll(c, x - .04, 3.5, 2.8, 1.4, _split(pg['label'])[1], _split(g['label'])[1], 88, col, 450, 1200, font=NUM, spacing=1)
        else:
            c.clock = 400
            bignum(c, x - .04, 3.5, _split(g['label'])[1], 88, col, gap=0, dur=1000)
        c.text(x + _w(_split(g['label'])[1], 88) + .05, 3.68, .8, .4, '小时', 14, col, font=LIGHT)
    if prev:   # 翻色：11 格逐个盖上薄荷绿
        flip = range(tot - new_mint, tot - old_mint)
        for j, i in enumerate(reversed(list(flip))):
            cx, cy = cells[i]
            c.a(c.rect(cx, cy, cell, cell, fill=MINT, radius=.05), 'zoom', at=450 + j * 100, hold=True, dur=350)
        c.clock = 450 + len(flip) * 100 + 300
        for k, an in enumerate(s.get('annotations', [])):
            x = rx + k * 2.85
            c.a(c.text(x, 5.05, 2.6, .35, an['title'], 13, MINT if an.get('trend') == 'up' else WHITE, font=BODY), 'fade-up', gap=120)
            c.a(c.text(x, 5.45, 2.6, .8, an['text'], 11, mix(WHITE, NAVY, .6), font=BODY, spacing=1.4), 'fade', gap=0)
    elif s.get('teaser'):
        c.a(c.text(rx, 5.2, 5.2, .5, s['teaser'] + '  →', 20, MINT, font=LIGHT), 'fade-left', gap=600)


def timeline(c, s, deck):
    """阶梯方块（参考 38 / 55 / 70 那页）：每年一块，越往右越高，块顶放巨型数字"""
    _bg(c, PAPER); _frame(c, deck, dark=False, source=s.get('source'))
    items = s['items']; ch = s.get('chart') or {}; vals = ch.get('line') or [0] * len(items)
    n = len(items); x0 = 3.9; bw = (W - x0) / n; bottom = H - .0
    fills = [WHITE, mix(STEEL, WHITE, .55), STEEL, MINT]
    inks = [INK, INK, WHITE, INK]
    base = 150
    for i, (it, v) in enumerate(zip(items, vals)):
        h = 2.75 + i * .85; x = x0 + i * bw; y = bottom - h
        blk = c.rect(x, y, bw, h, fill=fills[i % 4])
        c.a(blk, 'wipe-up', at=base + i * 180, hold=True, dur=700)
        c.clock = base + i * 180 + 350
        bignum(c, x + .25, y + .2, f'{v:g}%', 64, inks[i % 4], gap=0, dur=900)
        c.a(c.text(x + .28, y + 1.35, bw - .4, .3, it['time'], 11, inks[i % 4], font=BODY), 'fade', at=base + i * 180 + 500, hold=True)
        c.a(c.text(x + .28, y + 1.65, bw - .4, .9, [it['title'], it.get('text', '')], 11.5, inks[i % 4], font=BODY, spacing=1.35, para_gap=.2), 'fade', at=base + i * 180 + 500, hold=True)
    _eyebrow(c, MX, 1.15, s.get('kicker', ''), STEEL)
    c.a(c.text(MX, H - 2.7, 2.9, 1.6, s['title'].replace('**', ''), 24, INK, font=LIGHT, spacing=1.25), 'fade-up', at=200)
    c.a(c.text(MX, H - 1.05, 2.9, .5, ch.get('line_name', ''), 10.5, GREY, font=BODY), 'fade', at=400)


def table(c, s, deck):
    _bg(c, WHITE); _frame(c, deck, dark=False, source=s.get('source'))
    _eyebrow(c, MX, 1.15, s.get('kicker', ''), STEEL)
    c.a(c.text(MX, 1.5, 8, .7, s['title'].replace('**', ''), 28, INK, font=LIGHT), 'fade-up', gap=60)
    cols = s['columns']; rows = s['rows']; hl = s.get('highlight_row')
    ws = [2.3, 2.6, 2.3, 2.1, 2.43]; y = 2.75; rh = .95
    x = MX
    for j, col in enumerate(cols):
        c.a(c.text(x, y, ws[j], .3, col, 10.5, GREY, font=BODY), 'fade', gap=0 if j else 100); x += ws[j]
    c.a(c.rect(MX, y + .42, W - 2 * MX, .012, fill=INK), 'wipe-right', gap=0, dur=500)
    for i, r in enumerate(rows):
        yy = y + .55 + i * rh; on = i == hl
        if on: c.a(c.rect(MX - .15, yy, W - 2 * MX + .3, rh - .08, fill=MINT), 'wipe-right', gap=200, dur=500)
        x = MX
        for j, v in enumerate(r):
            big = j == 1
            c.a(c.text(x, yy, ws[j], rh - .08, str(v), 40 if big else 15, INK if (on or j == 0) else mix(INK, WHITE, .7),
                       font=NUM if big else BODY, anchor='m'), 'fade', gap=40)
            x += ws[j]
        c.rect(MX, yy + rh - .05, W - 2 * MX, .008, fill=mix(INK, WHITE, .2))
    if s.get('summary'):
        c.a(c.text(MX, H - 1.25, 9, .5, s['summary'].replace('**', ''), 16, INK, font=LIGHT), 'fade-up', gap=150)


def process(c, s, deck):
    """深色：四列，每列一个超大细体序号 + 细竖线，重点列整列薄荷绿"""
    _bg(c, NAVY); _frame(c, deck)
    _eyebrow(c, MX, 1.15, s.get('kicker', ''), MINT)
    c.a(c.text(MX, 1.5, 8, .7, s['title'].replace('**', ''), 28, WHITE, font=LIGHT), 'fade-up', gap=60)
    st = s['steps']; n = len(st); x0 = MX; w = (W - 2 * MX) / n; top = 2.75
    for i, it in enumerate(st):
        x = x0 + i * w; hl = it.get('highlight')
        if hl: c.a(c.rect(x, top, w, H - top - .7, fill=MINT), 'wipe-up', gap=150, dur=600)
        else: c.a(c.rect(x, top, .012, H - top - .7, fill=mix(WHITE, NAVY, .3)), 'wipe-down', gap=100, dur=400)
        ink = INK if hl else WHITE
        c.a(c.text(x + .3, top + .2, w - .4, 1.6, f'{i+1:02d}', 110, ink, font=NUM, spacing=1), 'fade-up', gap=60)
        c.a(c.text(x + .3, top + 2.3, w - .5, .5, it['title'], 22, ink, font=LIGHT), 'fade', gap=40)
        c.a(c.text(x + .3, top + 2.85, w - .6, 1, it.get('text', ''), 12, mix(ink, NAVY if not hl else MINT, .7), font=BODY, spacing=1.45), 'fade', gap=40)
    if s.get('summary'):
        c.a(c.text(W - MX - 6, 1.62, 6, .5, s['summary'], 13, mix(WHITE, NAVY, .65), font=BODY, align='r'), 'fade', gap=100)


def stat(c, s, deck):
    """满版巨型数字压底（参考 582.55 BIL 那页）"""
    _bg(c, NAVY); _frame(c, deck, source=None)
    _eyebrow(c, MX, 1.15, s.get('kicker', ''), MINT)
    c.a(c.text(MX, 1.5, 5.5, .9, s.get('label', ''), 26, WHITE, font=LIGHT), 'fade-up', gap=60)
    if s.get('text'):
        c.a(c.text(W - MX - 4.6, 1.5, 4.6, 1.2, s['text'], 13, mix(WHITE, NAVY, .65), font=BODY, spacing=1.5), 'fade', gap=100)
    if s.get('delta'):
        c.a(c.text(W - MX - 4.6, 2.75, 4.6, .4, '▲ ' + s['delta'], 13, MINT, font=BODY), 'fade', gap=60)
    c.clock += 100
    bignum(c, MX - .2, H - 4.45, s['value'], 300, MINT, gap=0, dur=1400)
    if s.get('source'): c.text(W - MX - 4.6, 3.25, 4.6, .26, '来源：' + s['source'], 10, mix(WHITE, NAVY, .55), font=BODY)


def compare(c, s, deck):
    """左右对半：左藏青（反例），右薄荷（正例），各自一列大字清单"""
    _bg(c, NAVY)
    c.a(c.rect(W / 2, 0, W / 2, H, fill=MINT), 'wipe-left', at=200, dur=700)
    _frame(c, deck)
    c.text(W - MX - 1.2, .3, 1.2, .26, f'[{c.idx:02d}]', 10.5, INK, align='r', font=BODY)
    for k, side in enumerate(('left', 'right')):
        d = s[side]; x = MX if k == 0 else W / 2 + .6; ink = WHITE if k == 0 else INK
        sub = mix(WHITE, NAVY, .55) if k == 0 else mix(INK, MINT, .6)
        c.a(c.text(x, 1.2, 5, .3, d.get('tag', ''), 11, MINT if k == 0 else NAVY, font=BODY), 'fade', at=300 + k * 400)
        c.a(c.text(x, 1.55, 5.4, .9, d['title'], 34, ink, font=LIGHT), 'fade-up', at=350 + k * 400)
        for j, it in enumerate(d['items']):
            y = 3.0 + j * .95
            c.a(c.rect(x, y, 5.3, .01, fill=sub), 'wipe-right', at=500 + k * 400 + j * 90, hold=True, dur=400)
            c.a(c.text(x, y + .18, .6, .5, f'{j+1:02d}', 13, sub, font=BODY), 'fade', at=550 + k * 400 + j * 90, hold=True)
            c.a(c.text(x + .65, y + .12, 4.7, .6, it, 20, ink, font=LIGHT), 'fade', at=550 + k * 400 + j * 90, hold=True)


def quote(c, s, deck):
    _bg(c, MINT); _frame(c, deck, dark=False)
    txt = s['text'] if isinstance(s['text'], list) else [s['text']]
    txt = [t.replace('**', '') for t in txt]
    c.a(c.text(MX - .1, .95, 2, 1.8, '“', 160, NAVY, font=NUM, spacing=.8), 'fade', at=0)
    c.a(c.text(MX, 2.55, W - 2 * MX, 3, txt, 46, INK, font=LIGHT, spacing=1.3, para_gap=.2), 'fade-up', at=100, dur=900)
    if s.get('by'):
        c.a(c.rect(MX, 5.6, .6, .015, fill=INK), 'wipe-right', gap=200, dur=400)
        c.a(c.text(MX + .8, 5.45, 6, .35, s['by'], 13, INK, font=BODY), 'fade', gap=0)


def end(c, s, deck):
    _bg(c, NAVY); _frame(c, deck)
    c.a(c.oval(W / 2, H / 2, 6.6, line=MINT, lw=1, line_alpha=.35), 'zoom', at=0, dur=1200)
    c.a(c.text(0, 2.75, W, 1.3, s.get('title', ''), 60, MINT, font=NUM, align='c'), 'fade-up', at=300, dur=900)
    if s.get('subtitle'):
        c.a(c.text(0, 4.1, W, .5, s['subtitle'], 15, mix(WHITE, NAVY, .7), font=LIGHT, align='c'), 'fade', gap=200)


LAYOUTS = {'cover': cover, 'kpi': kpi, 'section': section, 'chart': chart, 'donut_story': donut_story,
           'timeline': timeline, 'table': table, 'process': process, 'stat': stat, 'compare': compare,
           'quote': quote, 'end': end}
OWN_FRAME = True   # 页框由本设计系统自己画
