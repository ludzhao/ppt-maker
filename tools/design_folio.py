"""设计系统 B「黑白杂志」：参考 Laurel（Dribbble · Sanmi Ibitoye）。

拆解：
1. 黑底 + 黑白纪实摄影，大面积暗部；文字压在照片暗处。
2. 标题用大号衬线字（宋体 / Playfair），一句话里只有一个词换颜色（鼠尾草绿）并变斜体。
3. 数据卡是「白底黑字」的巨型衬线数字，像杂志插页，压在暗调背景上。
4. 列表式目录：当前项金色高亮，其余变暗。
5. 页框只有顶部居中的刊名和右上角的小页码；没有色块、没有圆角、没有图标。
"""
from core import W, H, MX, mix, rgb
from layouts import _roll, _ghost
from design_kit import bg, asset, photo, split, tw, bignum, plain, accent_tail

BLACK, INK2, WHITE, GREY, DIM, SAGE, GOLD, PAPER = '0C0C0C', '161616', 'F2F0EB', 'A7A39B', '5E5B56', 'A9C7A1', 'E9C46A', 'F4F2EE'
SERIF = 'Playfair Display|Noto Serif SC'
SANS = 'Inter|Noto Sans SC'
D = 'folio'


def _frame(c, deck, source=None, light=False):
    col = GREY if not light else '6B6862'
    c.text(0, .3, W, .3, deck.get('masthead', ''), 11, WHITE if not light else BLACK, align='c', font=SERIF)
    c.text(W - MX - 1, .32, 1, .26, f'{c.idx:02d}', 10.5, col, align='r', font=SANS)
    if source: c.text(MX, H - .48, 8, .26, '来源：' + source, 10, col, font=SANS)


def _title(c, x, y, w, text, size, color=WHITE, at=None, gap=60, anim='fade-up'):
    t = c.text(x, y, w, 2.6, text, size, color, font=SERIF, spacing=1.05, em_color=SAGE, em_style='italic', para_gap=0)
    return c.a(t, anim, at=at, gap=gap, dur=900)


def _kicker(c, x, y, text, color=GREY):
    c.a(c.text(x, y, 6, .3, text, 11, color, font=SANS, tracking=2), 'fade', at=0)


# ------------------------------------------------------------------ 页面
def cover(c, s, deck):
    bg(c, BLACK)
    photo(c, asset(D, 'meeting', s, deck), dur=1400)
    c.scrim(0, 0, W, H, BLACK, 'bottom', .9)
    c.a(c.rect(0, 0, W, H, fill=BLACK, alpha=.35), 'fade', at=0, dur=1)
    _frame(c, deck)
    lines = accent_tail(s['title'] if isinstance(s['title'], list) else [s['title']])
    c.a(c.text(0, 2.35, W, 2.8, lines, 64, WHITE, align='c', font=SERIF, spacing=1.05, em_color=SAGE, em_style='italic', para_gap=0), 'fade-up', at=400, dur=1200)
    if s.get('subtitle'): c.a(c.text(0, 4.85, W, .4, s['subtitle'], 15, GREY, align='c', font=SANS), 'fade', gap=300)
    if s.get('meta'): c.text(0, H - .65, W, .3, s['meta'], 10.5, GREY, align='c', font=SANS, tracking=2)


def kpi(c, s, deck):
    """暗调照片铺左侧，右侧三张白卡：巨型衬线数字"""
    bg(c, BLACK)
    photo(c, asset(D, 'hands', s, deck), 0, 0, 5.2, H, dur=900)
    c.scrim(0, 0, 5.2, H, BLACK, 'bottom', .85)
    _frame(c, deck, s.get('source'))
    _kicker(c, MX, 1.2, s.get('kicker', ''))
    _title(c, MX, 1.6, 4.0, s['title'], 30)
    items = s['items']; n = len(items); x0 = 5.75; gp = .25; cw = (W - MX - x0 - gp * (n - 1)) / n; y = 2.2; ch = 3.7
    for i, it in enumerate(items):
        x = x0 + i * (cw + gp)
        c.a(c.rect(x, y, cw, ch, fill=PAPER), 'fade-up', gap=150, dur=600)
        c.clock -= 300
        pre, num, unit = split(it['value'])
        size = min(74, int((cw - .5) / max(tw(num, 1), 1e-3) * .95))
        bignum(c, x + .25, y + .25, it['value'], size, BLACK, SERIF, unit_font=SANS, unit_scale=.22, gap=150, dur=1000)
        c.a(c.rect(x + .28, y + 2.2, cw - .56, .01, fill='BDB9B0'), 'wipe-right', gap=0, dur=400)
        c.a(c.text(x + .28, y + 2.35, cw - .5, .35, it['label'], 13, BLACK, font=SERIF), 'fade', gap=0)
        c.a(c.text(x + .28, y + 2.75, cw - .5, .8, it.get('delta', ''), 11, '6B6862', font=SANS, spacing=1.4), 'fade', gap=0)
    sm = s.get('summary') or (s.get('split') or {}).get('title')
    if sm: c.a(c.text(x0, y + ch + .3, W - MX - x0, .5, plain(sm), 12, GREY, font=SANS), 'fade', gap=200)


def section(c, s, deck):
    bg(c, BLACK)
    photo(c, asset(D, 'window', s, deck), 0, 0, W * .48, H, dur=1000)
    _frame(c, deck)
    x = W * .48 + .8
    c.a(c.text(x, 1.6, 4, .4, f"Chapter {s.get('no', '')}", 14, SAGE, font=SERIF, em_style='italic'), 'fade', at=200)
    _title(c, x, 2.3, W - x - MX, s['title'], 40, at=400)
    if s.get('subtitle'): c.a(c.text(x, 4.3, W - x - MX, .8, s['subtitle'], 15, GREY, font=SANS), 'fade', gap=200)


def chart(c, s, deck):
    """编辑部图表：细横条，只有第一名用鼠尾草绿；数值用衬线大字"""
    bg(c, BLACK); _frame(c, deck, s.get('source'))
    _kicker(c, MX, 1.2, s.get('kicker', ''))
    _title(c, MX, 1.6, 4.4, s['title'], 30)
    ins = s.get('insights') or []
    for i, t in enumerate(ins[:3]):
        y = 4.0 + i * .85
        c.a(c.text(MX, y, .5, .4, f'{i+1}', 18, SAGE, font=SERIF, em_style='italic'), 'fade', gap=120)
        c.a(c.text(MX + .45, y + .04, 3.9, .8, plain(t), 11.5, GREY, font=SANS, spacing=1.45), 'fade', gap=0)
    ch = s['chart']; cats = ch['categories']; vals = ch['series'][0]['values']; hl = ch.get('highlight', 0)
    x0 = 6.0; x1 = W - MX; rh = (H - 2.3) / len(cats); vmax = max(vals)
    base = c.clock + 100
    for i, (cat, v) in enumerate(zip(cats, vals)):
        y = 1.35 + i * rh; on = i == hl; col = SAGE if on else WHITE
        c.a(c.text(x0, y, 2, .4, cat, 13, col if on else GREY, font=SANS), 'fade', at=base + i * 110, hold=True)
        c.a(c.text(x1 - 1.6, y - .2, 1.6, .7, f'{v:g}', 34 if on else 26, col, align='r', font=SERIF), 'fade', at=base + i * 110, hold=True)
        bw = (x1 - x0 - 1.8) * v / vmax
        c.rect(x0, y + .5, x1 - x0, .01, fill='2A2A2A')
        c.a(c.rect(x0, y + .46, bw, .09 if on else .05, fill=col), 'wipe-right', at=base + i * 110, hold=True, dur=900)


def donut_story(c, s, deck):
    """100% 细长条：一周 40 小时切两段；第二页绿色段向左长出去，数字滚动"""
    bg(c, BLACK); _frame(c, deck, s.get('source'))
    cont = s.get('continue'); prev = deck['slides'][c.idx - 2] if cont else None
    segs = s['segments']; tot = sum(g['value'] for g in segs)
    if prev:
        c.a(_ghost(c, c.text(MX, 1.2, 9, 1.2, accent_tail(prev['title'] if isinstance(prev['title'], list) else [plain(prev['title'])]), 40, WHITE, font=SERIF, em_color=SAGE, em_style='italic')), 'out', at=0, hold=True, dur=300, grp=1)
        c.a(c.text(MX, 1.2, 9, 1.2, s['title'], 40, WHITE, font=SERIF, em_color=SAGE, em_style='italic'), 'fade', at=300, hold=True, dur=500)
    else:
        _title(c, MX, 1.2, 9, accent_tail([plain(s['title'])]), 40, at=0)
    bx, by, bw, bh = MX, 3.6, W - 2 * MX, .22
    old = prev['segments'] if prev else segs
    w0 = bw * old[0]['value'] / tot
    c.a(c.rect(bx, by, bw, bh, fill='3A3936'), 'wipe-right', at=200 if not prev else 0, hold=True, dur=800 if not prev else 1)
    c.a(c.rect(bx + w0, by, bw - w0, bh, fill=SAGE), 'wipe-left', at=600 if not prev else 0, hold=True, dur=800 if not prev else 1)
    if prev:
        w1 = bw * segs[0]['value'] / tot
        c.a(c.rect(bx + w1, by, w0 - w1, bh, fill=SAGE), 'wipe-left', at=500, hold=True, dur=1100)
    for k, g in enumerate(segs):
        x = bx if k == 0 else bx + bw - 4.5; al = 'l' if k == 0 else 'r'; col = WHITE if k == 0 else SAGE
        c.text(x, by + .5, 4.5, .35, g['name'], 13, GREY, font=SANS, align=al)
        new = split(g['label'])[1]
        if prev: _roll(c, x, by + .85, 4.5, 1.5, split(old[k]['label'])[1] + ' 小时', new + ' 小时', 72, col, 500, 1100, font=SERIF, align=al)
        else: c.a(c.text(x, by + .85, 4.5, 1.5, new + ' 小时', 72, col, font=SERIF, align=al), 'fade-up', at=900, hold=True)
    if prev:
        for k, an in enumerate(s.get('annotations', [])):
            x = bx if k == 0 else bx + bw - 4.5; al = 'l' if k == 0 else 'r'
            c.a(c.text(x, by + 2.3, 4.5, .8, an['text'], 12, GREY, font=SANS, align=al), 'fade', at=1700 + k * 150, hold=True)
    elif s.get('teaser'):
        c.a(c.text(0, H - 1.3, W, .5, s['teaser'], 20, SAGE, font=SERIF, align='c', em_style='italic'), 'fade', at=1500)


def timeline(c, s, deck):
    """杂志目录式：左侧小幅照片，右侧大号衬线年份列表，当前项金色，其余变暗"""
    bg(c, BLACK)
    photo(c, asset(D, 'crowd', s, deck), MX, 1.6, 3.6, 4.6, dur=900)
    _frame(c, deck, s.get('source'))
    c.a(c.text(MX, 1.0, 6, .4, plain(s['title']), 16, WHITE, font=SERIF), 'fade', at=0)
    items = s['items']; x = 5.4; y0 = 1.45; rh = (H - 2.4) / len(items)
    for i, it in enumerate(items):
        y = y0 + i * rh; hl = it.get('highlight'); col = GOLD if hl else ('4A4843' if i < len(items) - 1 else WHITE)
        col = GOLD if hl else '55524C'
        c.a(c.text(x + .65, y, 6.2, rh, f"{it['time']}  {it['title']}", 40, col, font=SERIF, anchor='t'), 'fade-up', at=150 + i * 150, hold=True)
        if hl and it.get('text'):
            c.a(c.text(x + .68, y + .78, 6, .4, it['text'], 12, GREY, font=SANS), 'fade', at=150 + i * 150 + 300, hold=True)


def table(c, s, deck):
    bg(c, BLACK); _frame(c, deck, s.get('source'))
    _kicker(c, MX, 1.2, s.get('kicker', ''))
    _title(c, MX, 1.55, 10, s['title'], 32)
    cols = s['columns']; rows = s['rows']; hl = s.get('highlight_row')
    ws = [2.5, 2.4, 2.4, 2.2, 2.23]; y = 3.0; rh = .9
    x = MX
    for j, col in enumerate(cols):
        c.text(x, y, ws[j], .3, col, 10.5, GREY, font=SANS); x += ws[j]
    c.rect(MX, y + .42, W - 2 * MX, .01, fill=WHITE)
    for i, r in enumerate(rows):
        yy = y + .5 + i * rh; on = i == hl; x = MX
        for j, v in enumerate(r):
            col = (SAGE if on else WHITE) if j in (0, 1) else (WHITE if on else GREY)
            c.a(c.text(x, yy, ws[j], rh - .05, str(v), 34 if j == 1 else (17 if j == 0 else 13), col, font=SERIF if j < 2 else SANS, anchor='m',
                       em_style='italic'), 'fade', gap=50)
            x += ws[j]
        c.rect(MX, yy + rh - .02, W - 2 * MX, .006, fill='3A3936')
    if s.get('summary'): c.a(c.text(MX, H - 1.2, 10, .5, s['summary'], 18, WHITE, font=SERIF, em_color=SAGE, em_style='italic'), 'fade-up', gap=200)


def process(c, s, deck):
    """大号衬线步骤列表（参考 ROI Sprint 那页）：重点步金色，其余逐级变暗；右侧照片"""
    bg(c, BLACK)
    photo(c, asset(D, 'night', s, deck), W * .58, 0, W * .42, H, dur=900)
    c.scrim(W * .58, 0, W * .42, H, BLACK, 'left', .9)
    _frame(c, deck)
    c.a(c.text(MX, 1.0, 6, .4, plain(s['title']), 16, WHITE, font=SERIF), 'fade', at=0)
    st = s['steps']; y0 = 1.9; rh = .95
    for i, it in enumerate(st):
        hl = it.get('highlight'); col = GOLD if hl else ['F2F0EB', 'B9B6AF', '85827C', '5E5B56'][min(i, 3)]
        y = y0 + i * rh
        c.a(c.text(MX, y + .2, .6, .4, f'0{i+1}', 11, GREY, font=SANS), 'fade', at=200 + i * 140, hold=True)
        c.a(c.text(MX + .7, y, 6.5, .8, it['title'], 42, col, font=SERIF), 'fade-up', at=200 + i * 140, hold=True)
        c.a(c.text(MX + 3.1, y + .25, 3.8, .5, it.get('text', ''), 11.5, GREY, font=SANS), 'fade', at=400 + i * 140, hold=True)
    if s.get('summary'): c.a(c.text(MX + .7, H - 1.3, 6.5, .5, s['summary'], 13, SAGE, font=SERIF, em_style='italic'), 'fade', at=1200)


def stat(c, s, deck):
    bg(c, BLACK)
    photo(c, asset(D, 'night', s, deck), dur=1200)
    c.scrim(0, 0, W, H, BLACK, 'left', .85)
    _frame(c, deck, s.get('source'))
    _kicker(c, MX, 1.2, s.get('kicker', ''))
    c.a(c.text(MX, 1.6, 6, .6, s.get('label', ''), 22, WHITE, font=SERIF), 'fade-up', gap=60)
    c.clock = 300
    bignum(c, MX - .1, 2.3, s['value'], 230, WHITE, SERIF, unit_font=SERIF, unit_scale=.3, gap=0, dur=1400)
    if s.get('delta'): c.a(c.text(MX, 5.6, 6, .4, s['delta'], 14, SAGE, font=SERIF, em_style='italic'), 'fade', gap=100)
    if s.get('text'): c.a(c.text(MX, 6.05, 6, .5, s['text'], 12, GREY, font=SANS), 'fade', gap=0)


def compare(c, s, deck):
    bg(c, BLACK); _frame(c, deck)
    _kicker(c, MX, 1.2, s.get('kicker', ''))
    _title(c, MX, 1.55, 11, accent_tail([plain(s['title'])], 3), 34)
    c.a(c.rect(W / 2, 3.0, .01, H - 3.8, fill='3A3936'), 'wipe-down', gap=100, dur=600)
    for k, side in enumerate(('left', 'right')):
        d = s[side]; x = MX if k == 0 else W / 2 + .5; col = WHITE if k else '7A7771'
        c.a(c.text(x, 3.0, 5, .3, d.get('tag', ''), 11, SAGE if k else GREY, font=SANS, tracking=2), 'fade', gap=100)
        c.a(c.text(x, 3.35, 5.5, .6, d['title'], 26, col, font=SERIF), 'fade-up', gap=0)
        for j, it in enumerate(d['items']):
            c.a(c.text(x, 4.25 + j * .55, 5.5, .45, it, 15, col, font=SERIF), 'fade', gap=60)


def quote(c, s, deck):
    bg(c, BLACK)
    photo(c, asset(D, 'crowd', s, deck), dur=1200)
    c.a(c.rect(0, 0, W, H, fill=BLACK, alpha=.55), 'fade', at=0, dur=1)
    _frame(c, deck)
    txt = s['text'] if isinstance(s['text'], list) else [s['text']]
    c.a(c.text(0, 2.3, W, 2.6, txt, 44, WHITE, align='c', font=SERIF, spacing=1.25, em_color=SAGE, em_style='italic', para_gap=.1), 'fade-up', at=300, dur=1200)
    if s.get('by'): c.a(c.text(0, 5.2, W, .4, '— ' + s['by'], 13, GREY, align='c', font=SANS), 'fade', gap=300)


def end(c, s, deck):
    bg(c, BLACK)
    photo(c, asset(D, 'window', s, deck), dur=1200)
    c.a(c.rect(0, 0, W, H, fill=BLACK, alpha=.6), 'fade', at=0, dur=1)
    _frame(c, deck)
    c.a(c.text(MX, 2.6, W, 1.4, accent_tail([s.get('title', '')], 2), 60, WHITE, font=SERIF, em_color=SAGE, em_style='italic'), 'fade-up', at=300, dur=1000)
    if s.get('subtitle'): c.a(c.text(MX, 3.9, 9, .5, s['subtitle'], 14, GREY, font=SANS), 'fade', gap=200)
    c.a(c.text(W - MX - 5, H - 2.75, 5, 1.8, '2026', 110, '3A3936', align='r', font=SERIF), 'fade', gap=300)


LAYOUTS = {'cover': cover, 'kpi': kpi, 'section': section, 'chart': chart, 'donut_story': donut_story,
           'timeline': timeline, 'table': table, 'process': process, 'stat': stat, 'compare': compare,
           'quote': quote, 'end': end}
