"""版式库。每个版式 = 摆放 + 动画编排。动画原则（来自 html-ppt-skill authoring guide）：
- 标题 rise / type，正文 fade-up / stagger，数字 counter，图表逐根生长；
- 一页只用 1 个「主角动效」，其余保持克制；
- 页面之间用 morph（平滑）让背景光晕缓慢漂移。
"""
import pathlib, re
from core import W, H, MX, mix, rgb, pattern_png, vertical
from pptx.util import Inches
from charts import add_chart, pick_chart

GLOW_POS = [((W - 6.2, -3.2, 9), (-3.5, H - 4.2, 8)), ((W - 4.0, -2.4, 6.5), (-2.0, H - 3.0, 6)),
            ((W - 7.5, H - 4.5, 8), (-3.0, -3.0, 7)), ((W - 3.2, H - 3.4, 6), (W * .35, -3.6, 7))]

HERO_BG = '070B14'; HERO_TX = 'F3F5FA'; HERO_TX2 = 'C9CFDC'


def background(c, variant='content'):
    """按风格画背景：flat 纯色 / paper 纸纹 / spotlight 暖色聚光 / gradient 深蓝渐变 / glow 旧版光晕"""
    t = c.t; mode = c.style.get('bg', 'glow')
    fill = c.s.background.fill
    if mode == 'gradient':
        fill.gradient(); fill.gradient_angle = 120
        st = fill.gradient_stops
        st[0].color.rgb = rgb(mix(t.bg, '000000', .7)); st[0].position = 0
        st[1].color.rgb = rgb(mix(t.grad[0], t.bg, .45)); st[1].position = 1.0
        (x1, y1, d1), (x2, y2, d2) = GLOW_POS[c.idx % len(GLOW_POS)]
        c.glow(x1, y1, d1, t.accent, .16 if variant == 'content' else .28, name='!!glowA')
        return
    fill.solid(); fill.fore_color.rgb = rgb(t.bg)
    if mode == 'flat':
        return
    if mode in ('grid', 'dots', 'scan'):
        col = {'grid': t.text_1, 'dots': t.text_1, 'scan': t.accent}[mode]
        al = {'grid': .05, 'dots': .16, 'scan': .035}[mode]
        c.s.shapes.add_picture(str(pattern_png(mode, col, al)), 0, 0, Inches(W), Inches(H))
        if mode == 'scan': c.glow(W - 6, -3.5, 9, t.accent, .10 if variant == 'content' else .18, name='!!glowA')
        return
    if mode == 'washi':   # 宣纸颗粒 + 角落一团淡墨
        from core import grain_png
        c.s.shapes.add_picture(str(grain_png(t.text_1, .05)), 0, 0, Inches(W), Inches(H))
        c.glow(W - 5.5, H - 5, 8, t.text_1, .07 if variant == 'content' else .12, name='!!glowA')
        return
    if mode == 'paper':
        from core import grain_png
        c.s.shapes.add_picture(str(grain_png(t.text_1, .05)), 0, 0, Inches(W), Inches(H))
        return
    if mode == 'spotlight':   # 右上角暖色聚光 + 左下暗角（A10/A11/B08）
        (x1, y1, d1), _ = GLOW_POS[c.idx % len(GLOW_POS)]
        c.glow(W - 7.5, -5.0, 11, t.accent, .20 if variant == 'content' else .32, name='!!glowA')
        c.glow(-4, H - 3, 7, t.accent_3, .10, name='!!glowB')
        return
    (x1, y1, d1), (x2, y2, d2) = GLOW_POS[c.idx % len(GLOW_POS)]
    strong = variant in ('cover', 'section', 'end')
    a1 = (.38 if strong else .20) if t.dark else (.16 if strong else .08)
    a2 = (.30 if strong else .12) if t.dark else (.12 if strong else .05)
    c.glow(x1, y1, d1, t.grad[0], a1, name='!!glowA')
    c.glow(x2, y2, d2, t.grad[-1], a2, name='!!glowB')


def frame(c, deck, idx, total, light=False):
    """页框：rule 顶部细线（B01）/ masthead 报刊刊头双线（B09）/ minimal 只有页码 / none"""
    t = c.t; mode = c.style.get('frame', 'legacy')
    col = HERO_TX2 if light else t.text_3
    pg = f'{idx:02d} / {total:02d}'
    if mode == 'rule':
        c.rect(MX, .32, W - 2 * MX, .02, fill=t.border_strong)
        c.text(MX, .1, 6, .22, deck.get('masthead', deck.get('footer', '')), 10, col, tracking=1.5)
        c.text(W - MX - 3, .1, 3, .22, pg, 10, col, align='r', tracking=1.5, font=c.f_num)
        return .55
    if mode == 'masthead':
        c.text(MX, .12, W - 2 * MX, .42, deck.get('masthead', deck.get('title', '')), 17, t.text_1, bold=True, align='c', font=c.f_title)
        c.rect(MX, .58, W - 2 * MX, .02, fill=t.border_strong); c.rect(MX, .63, W - 2 * MX, .008, fill=t.border_strong)
        c.text(W - MX - 2, .66, 2, .22, pg, 10, col, align='r', font=c.f_num)
        c.text(MX, .66, 7, .22, deck.get('footer', ''), 10, col)
        return .95
    if mode == 'swiss':   # 左上红方块 + 粗黑刊头线 + 大页码
        c.rect(MX, .3, .22, .22, fill=t.accent)
        c.text(MX + .35, .27, 7, .3, deck.get('masthead', deck.get('footer', '')), 11, t.text_1, bold=True, tracking=1)
        c.text(W - MX - 2, .2, 2, .4, f'{idx:02d}', 20, t.text_1, bold=True, align='r', font=c.f_num)
        c.rect(MX, .66, W - 2 * MX, .035, fill=t.border_strong)
        return .8
    if mode == 'brutal':  # 顶部黑条 + 黄字 + 白底页码牌
        c.rect(0, 0, W, .42, fill=t.border_strong)
        c.text(MX, .08, 8, .28, deck.get('masthead', deck.get('footer', '')), 12, t.accent_3, bold=True, tracking=1)
        c.rect(W - MX - 1.0, .07, 1.0, .28, fill=t.accent_3)
        c.text(W - MX - 1.0, .07, 1.0, .28, f'{idx:02d}/{total:02d}', 11, t.text_1, bold=True, align='c', anchor='m', font=c.f_num)
        return .75
    if mode == 'ink':     # 右上朱红页码章 + 刊名
        c.rect(W - MX - .42, .22, .42, .42, fill=t.accent)
        c.text(W - MX - .42, .22, .42, .42, f'{idx:02d}', 13, t.accent_ink, bold=True, align='c', anchor='m', font=c.f_num)
        c.text(W - MX - 6.6, .3, 6, .3, deck.get('masthead', deck.get('footer', '')), 11, t.text_3, align='r', tracking=3)
        return .7
    if mode == 'term':    # 窗口三色点 + 路径提示符
        for k, col in enumerate(('FF5F56', 'FFBD2E', '27C93F')): c.oval(MX + .09 + k * .27, .32, .15, fill=col)
        c.text(MX + 1.0, .2, 8, .26, f"~/{deck.get('slug', 'ai-report')} $ open slide_{idx:02d}.pptx", 10.5, t.text_3, font=c.f_num)
        c.text(W - MX - 2, .2, 2, .26, f'[{idx:02d}/{total:02d}]', 10.5, t.accent, align='r', font=c.f_num)
        c.rect(MX, .52, W - 2 * MX, .012, fill=t.border)
        return .7
    if mode == 'minimal':
        c.text(W - MX - 3, .3, 3, .22, pg, 10, col, align='r', tracking=1.5, font=c.f_num)
        return .55
    return .55


def header(c, s, x=MX, w=None, color=None, title_size=None):
    """标题三层：眉标（#标签 或 英文大写）+ 结论式主标题 + 灰色副标题"""
    w = w or (W - 2 * MX)
    t = c.t; y = getattr(c, 'top', .55)
    mode = c.style.get('eyebrow', 'caps')
    if s.get('kicker'):
        if mode == 'num':     # 瑞士：红色粗体大写
            c.a(c.text(x, y, w, .3, s['kicker'].upper(), 11.5, t.accent, bold=True, tracking=3, name='!!kicker', font=c.f_num), 'fade', at=0)
            y += .42
        elif mode == 'pill':  # 便当格：浅色胶囊
            k = s['kicker']; tw = .13 * len(k) + .45
            c.a(c.rect(x, y, tw, .32, fill=t.accent, alpha=.12, radius=.16, name='!!kbar'), 'fade', at=0, dur=300)
            c.a(c.text(x, y, tw, .32, k, 11, t.accent, bold=True, align='c', anchor='m', name='!!kicker'), 'fade', gap=0)
            y += .5
        elif mode == 'block': # 新粗野：歪一点的黑底黄字标签
            k = s['kicker']; tw = .15 * len(k) + .5
            r_ = c.rect(x, y, tw, .36, fill=t.border_strong, name='!!kbar'); r_.rotation = -2
            tx = c.text(x, y, tw, .36, k, 13, t.accent_3, bold=True, align='c', anchor='m', name='!!kicker', font=c.f_num); tx.rotation = -2
            c.a(r_, 'pop', at=0, dur=350); c.a(tx, 'pop', gap=0, dur=350)
            y += .58
        elif mode == 'seal':  # 国风：朱红小印 + 宋体眉标
            k = s['kicker']
            c.a(c.rect(x, y, .3, .3, fill=t.accent, name='!!kbar'), 'pop', at=0, dur=350)
            c.a(c.text(x, y, .3, .3, k[0], 12, t.accent_ink, bold=True, align='c', anchor='m'), 'pop', gap=0, dur=350)
            c.a(c.text(x + .45, y, w - .5, .3, k, 12, t.accent, bold=True, tracking=4, name='!!kicker', anchor='m'), 'fade', gap=60)
            y += .5
        elif mode == 'prompt':  # 终端：提示符
            c.a(c.text(x, y, w, .3, '> ' + s['kicker'].lower() + ' _', 12, t.accent, name='!!kicker', font=c.f_num), 'type', at=0)
            y += .42
        elif mode == 'tag':
            k = s['kicker']; tw = .14 * len(k) + .3
            c.a(c.rect(x, y, tw, .3, fill=t.accent, radius=.06, name='!!kbar'), 'fade', at=0, dur=300)
            c.a(c.text(x, y, tw, .3, '# ' + k, 10.5, t.accent_ink, bold=True, align='c', anchor='m', name='!!kicker'), 'fade', gap=0)
            y += .45
        elif c.style.get('frame') == 'legacy':
            c.a(c.rect(x, y + .07, .28, .045, fill=t.accent, name='!!kbar'), 'wipe-right', at=0, dur=400)
            c.a(c.text(x + .4, y - .02, w - .4, .3, s['kicker'], 11, t.accent, bold=True, tracking=2, name='!!kicker'), 'fade', gap=60)
            y += .42
        else:
            c.a(c.text(x, y, w, .3, s['kicker'].upper(), 10.5, t.accent, bold=True, tracking=2.5, name='!!kicker', font=c.f_num), 'fade', at=0)
            y += .38
    title = s.get('title', '')
    base = c.style.get('title_size', 30)
    size = title_size or s.get('title_size') or (base if len(title) <= 24 else base - 4)
    lines = 1 if len(title) * size / 72 * 1.02 < w else 2
    c.a(c.text(x, y, w, .6 * lines + .3, title, size, color or t.text_1, bold=True, spacing=1.1, name='!!title', font=c.f_title),
        s.get('title_anim', 'rise'), gap=60, dur=700)
    y += (.72 if lines == 1 else 1.27) * size / 30
    if s.get('subtitle'):
        c.a(c.text(x, y - .05, w, .35, s['subtitle'], 13, t.text_3, name='!!sub'), 'fade', gap=60)
        y += .42
    return y + .1


def footer(c, idx, total, deck, light=False):
    """页脚只占一行：数据来源在左，页码 / 页名在右"""
    t = c.t; col = HERO_TX2 if light else t.text_3
    mode = c.style.get('frame', 'legacy')
    if c.source_text:
        c.text(MX, H - .5, W - 2 * MX - 3.2, .3, '来源：' + c.source_text, 10, col)
    if mode == 'legacy':
        if not c.source_text: c.text(MX, H - .5, 6, .3, deck.get('footer', deck.get('title', '')), 10, col, name='!!footer')
        c.text(W - MX - 2, H - .5, 2, .3, f'{idx:02d} / {total:02d}', 10, col, align='r', tracking=1)
    elif mode == 'none':
        c.text(W - MX - 3, H - .5, 3, .3, f'{idx:02d} / {total:02d}', 10, col, align='r', tracking=1, font=c.f_num)
    elif mode == 'minimal':
        c.text(W - MX - 3.1, H - .5, 3.1, .3, deck.get('footer', ''), 10, col, align='r')


def source(c, text, light=False):
    c.source_text = text or None


def credit(c, text, light=True, x=None, w=4.5, y=None):
    if text:
        c.text(x if x is not None else W - MX - w, y if y is not None else H - .8, w, .25, '图片：' + text, 9,
               HERO_TX2 if light else c.t.text_3, align='r')


def img_path(deck, p):
    q = pathlib.Path(p)
    if not q.is_absolute(): q = pathlib.Path(deck.get('_base', '.')) / q
    return q


# ================================================================== 开场
def _stat_strip(c, items, y, h=1.5, x0=MX, x1=None, light=False, size=34):
    """一排大数字：顶部细线 + 标签 + 数字（滚动）+ 涨跌；列之间留白，不套卡片（B01 / A11）"""
    t = c.t; x1 = x1 or (W - MX); n = len(items); gap = .35
    w = (x1 - x0 - gap * (n - 1)) / n
    tx1 = HERO_TX if light else t.text_1; tx3 = HERO_TX2 if light else t.text_3
    for i, it in enumerate(items):
        x = x0 + i * (w + gap); hl = it.get('highlight')
        c.a(c.rect(x, y, w, .03 if hl else .015, fill=t.accent if hl else (HERO_TX2 if light else t.border_strong)), 'wipe-right', gap=80 if i else 0, dur=450)
        c.a(c.text(x, y + .14, w, .3, it['label'], 11.5, tx3), 'fade', gap=30)
        c.counter(x - .02, y + .42, w, size / 60 + .2, it['value'], size, t.accent if hl else tx1, gap=30)
        if it.get('delta'):
            up = it.get('trend', 'up') == 'up'
            c.a(c.text(x, y + .5 + size / 60 + .1, w, .3, ('▲ ' if up else '▼ ') + it['delta'], 11.5, t.good if up else t.bad, bold=True), 'fade', gap=30)
        c.clock -= 700
    c.clock += 700


# ================================================================== 风格专属的封面 / 章节页（styles.py 里的 cover / section 字段）
def _lines(x): return x if isinstance(x, list) else [x]

def _cover_swiss(c, s, deck):
    t = c.t; background(c, 'cover'); bx = W * .6
    c.a(c.rect(bx, 0, W - bx, H, fill=t.accent), 'wipe-down', at=0, dur=700)
    c.a(c.text(bx + .25, H - 4.2, W - bx - .3, 3.9, s.get('badge', 'AI'), 250, 'FFFFFF', bold=True, spacing=.8, anchor='b', font=c.f_num), 'rise', at=450, dur=800)
    if s.get('meta'): c.a(c.text(bx + .4, .45, W - bx - .8, .3, s['meta'], 12, 'FFFFFF', bold=True, tracking=1), 'fade', at=500)
    c.a(c.text(MX, .9, bx - MX - .4, .3, (s.get('kicker') or '').upper(), 12, t.accent, bold=True, tracking=3, font=c.f_num), 'fade', at=100)
    lines = _lines(s['title']); size = s.get('title_size', 62)
    c.a(c.text(MX, 1.4, bx - MX - .3, 3, lines, size, t.text_1, bold=True, spacing=.98, font=c.f_title, para_gap=0), 'rise', gap=100, dur=800)
    y = 1.5 + len(lines) * size / 72 * 1.12
    c.a(c.rect(MX, y, 1.6, .09, fill=t.text_1), 'wipe-right', gap=100, dur=400)
    if s.get('subtitle'): c.a(c.text(MX, y + .3, bx - MX - .6, .9, s['subtitle'], 18, t.text_2, spacing=1.4), 'fade-up', gap=80)
    if s.get('stats'): _stat_strip(c, s['stats'], H - 2.0, x1=bx - .5, size=32)


def _cover_bento(c, s, deck):
    t = c.t; background(c, 'cover'); g = .22
    x2 = MX + 7.75; w2 = W - MX - x2; R = t.radius
    tiles = [(MX, .6, 7.75 - g, 4.3, t.surface), (x2, .6, w2, 2.04, t.accent), (x2, .6 + 2.04 + g, w2, 2.04, t.text_1)]
    for k, (x, y, w, h, f) in enumerate(tiles):
        c.a(c.rect(x, y, w, h, fill=f, radius=R), 'zoom', at=80 * k, hold=True, dur=550)
    c.clock = 300
    if s.get('kicker'):
        k = s['kicker']; tw = .12 * len(k) + .5
        c.a(c.rect(MX + .45, 1.0, tw, .34, fill=t.accent, alpha=.12, radius=.17), 'fade', gap=0)
        c.a(c.text(MX + .45, 1.0, tw, .34, k, 11, t.accent, bold=True, align='c', anchor='m'), 'fade', gap=0)
    lines = _lines(s['title'])
    c.a(c.text(MX + .45, 1.6, 6.8, 2.2, lines, s.get('title_size', 52), t.text_1, bold=True, spacing=1.02, font=c.f_title, para_gap=0), 'rise', gap=80, dur=700)
    if s.get('subtitle'): c.a(c.text(MX + .45, 3.75, 6.6, .9, s['subtitle'], 16, t.text_2, spacing=1.4), 'fade-up', gap=80)
    c.a(c.text(x2 + .35, .75, w2 - .7, 1.5, s.get('badge', 'AI'), 88, 'FFFFFF', bold=True, font=c.f_num), 'pop', at=500, hold=True)
    c.a(c.text(x2 + .35, 2.15, w2 - .7, .35, s.get('badge_note', ''), 12, 'FFFFFF'), 'fade', at=650, hold=True)
    if s.get('meta'): c.a(c.text(x2 + .35, 3.05, w2 - .7, 1.5, s['meta'], 15, 'FFFFFF', spacing=1.4, bold=True), 'fade', at=700, hold=True)
    st = s.get('stats') or []; n = max(len(st), 1); y = 4.9 + g; h = H - .5 - y; w = (W - 2 * MX - g * (n - 1)) / n
    for i, it in enumerate(st):
        x = MX + i * (w + g)
        c.a(c.rect(x, y, w, h, fill=t.surface, radius=R), 'zoom', at=800 + 90 * i, hold=True, dur=500)
        c.a(c.text(x + .35, y + .25, w - .7, .3, it['label'], 12, t.text_3), 'fade', at=900 + 90 * i, hold=True)
        c.clock = 900 + 90 * i
        c.counter(x + .33, y + .6, w - .6, .8, it['value'], 36, (t.accent, t.accent_2, t.accent_3)[i % 3], gap=0)


def _cover_brutal(c, s, deck):
    t = c.t; background(c, 'cover')
    k = s.get('kicker')
    if k:
        tw = .16 * len(k) + .6
        r_ = c.rect(MX, .7, tw, .42, fill=t.border_strong); r_.rotation = -3
        tx = c.text(MX, .7, tw, .42, k, 14, t.accent_3, bold=True, align='c', anchor='m', font=c.f_num); tx.rotation = -3
        c.a(r_, 'pop', at=0, dur=350); c.a(tx, 'pop', gap=0, dur=350)
    lines = _lines(s['title']); size = s.get('title_size', 78); lh = size / 72 * 1.08
    if len(lines) > 1:   # 第二行底下刷一道荧光笔
        hw = min(W - 2 * MX - 3, len(lines[1]) * size / 72 * 1.0 + .3)
        c.a(c.rect(MX - .1, 1.35 + lh + lh * .45, hw, lh * .45, fill=t.accent_3), 'wipe-right', at=900, hold=True, dur=500)
    c.a(c.text(MX, 1.35, W - 2 * MX - 2.6, lh * len(lines) + .3, lines, size, t.text_1, spacing=.98, font=c.f_title, para_gap=0), 'rise', gap=150, dur=700)
    cx, cy, d = W - MX - 1.15, 1.9, 2.2
    sh = c.oval(cx + .08, cy + .08, d, fill=t.border_strong); st_ = c.oval(cx, cy, d, fill=t.accent, line=t.border_strong, lw=2.5)
    bt = c.text(cx - d / 2, cy - d / 2, d, d, s.get('badge', 'AI'), 54, 'FFFFFF', align='c', anchor='m', font=c.f_title)
    grp = c.s.shapes.add_group_shape([sh, st_, bt]); grp.rotation = 12
    c.a(grp, 'pop', at=600, hold=True, dur=500)
    y = 1.35 + lh * len(lines) + .35
    if s.get('subtitle'):
        w = min(8.6, len(s['subtitle']) * .27 + .8)
        c.a(c.rect(MX + .08, y + .08, w, .7, fill=t.border_strong), 'fade-up', gap=100, dur=400)
        c.a(c.rect(MX, y, w, .7, fill=t.surface, line=t.border_strong, lw=2.25), 'fade-up', gap=0, dur=400)
        c.a(c.text(MX + .3, y, w - .5, .7, s['subtitle'], 18, t.text_1, bold=True, anchor='m'), 'fade', gap=0)
    st = s.get('stats') or []; n = len(st)
    if n:
        g = .4; yy = H - 1.75; w = (W - 2 * MX - g * (n - 1)) / n
        for i, it in enumerate(st):
            x = MX + i * (w + g)
            c.a(c.card(x, yy, w, 1.2, hl=(i == 0)), 'fade-up', gap=100, dur=450)
            c.a(c.text(x + .3, yy + .14, w - .5, .3, it['label'], 12, t.text_2, bold=True), 'fade', gap=0)
            c.counter(x + .28, yy + .42, w - .5, .7, it['value'], 30, t.text_1, gap=0)


def _cover_ink(c, s, deck):
    t = c.t; background(c, 'cover')
    lines = _lines(s['title']); vh = H - 1.2
    size = s.get('title_size', min(68, int(vh / (max(len(l.replace(' ', '')) for l in lines) * 1.08) * 72))); colw = size / 72 * 1.45
    ex, ey = W - MX - len(lines) * colw / 2 - 1.2, 3.75
    c.a(c.oval(ex, ey, 5.8, line=t.text_1, lw=16, line_alpha=.10), 'wheel', at=0, hold=True, dur=1400)
    x = W - MX - colw
    for i, ln in enumerate(lines):
        tx = vertical(c.text(x - i * (colw + .1), .6, colw, vh, ln.replace(' ', ''), size, t.text_1, font=c.f_title))
        c.a(tx, 'wipe-down', at=300 + 450 * i, hold=True, dur=900)
    sx = x - (len(lines) - 1) * (colw + .1) - 1.05
    seal = c.rect(sx, H - 2.3, .8, .8, fill=t.accent)
    c.a(seal, 'pop', at=300 + 450 * len(lines) + 300, hold=True, dur=400)
    c.a(c.text(sx, H - 2.3, .8, .8, s.get('badge', 'AI'), 22, t.accent_ink, bold=True, align='c', anchor='m', font=c.f_num), 'pop',
        at=300 + 450 * len(lines) + 300, hold=True, dur=400)
    c.clock = 200
    left_w = sx - MX - .6
    if s.get('kicker'):
        c.a(c.text(MX, 1.0, left_w, .35, s['kicker'], 13, t.accent, bold=True, tracking=6), 'fade', gap=0)
    if s.get('subtitle'):
        c.a(c.text(MX, 1.6, min(5.6, left_w), 2.2, s['subtitle'], 24, t.text_1, spacing=1.5, font=c.f_quote), 'fade-up', gap=200, dur=800)
    if s.get('meta'): c.a(c.text(MX, 4.0, left_w, .3, s['meta'], 12, t.text_3, tracking=2), 'fade', gap=100)
    if s.get('stats'): _stat_strip(c, s['stats'], H - 2.0, x1=sx - .5, size=30)


def _cover_term(c, s, deck):
    t = c.t; background(c, 'cover')
    wx, wy, ww, wh = MX - .2, .55, W - 2 * MX + .4, H - 1.1
    c.a(c.rect(wx, wy, ww, wh, fill=t.surface, line=t.border, radius=t.radius), 'fade', at=0, dur=400)
    c.rect(wx, wy, ww, .42, fill=t.surface_2, radius=t.radius)
    for k, col in enumerate(('FF5F56', 'FFBD2E', '27C93F')): c.oval(wx + .3 + k * .28, wy + .21, .15, fill=col)
    c.text(wx + 1.3, wy + .08, ww - 2.6, .28, 'ppt-maker — zsh — 120×36', 10.5, t.text_3, align='c', font=c.f_num)
    lines = _lines(s['title']); x = MX + .2
    cmd = f'$ ppt-maker --topic "{"".join(lines)}" --style terminal'
    c.a(c.text(x, 1.35, W - 2 * MX, .35, cmd, 14, t.text_2, font=c.f_num), 'type', at=300)
    c.clock += 20 * len(cmd)
    c.a(c.text(x, 1.8, W - 2 * MX, .35, s.get('kicker', ''), 13, t.accent, font=c.f_num), 'fade', gap=150)
    size = s.get('title_size', 64)
    c.a(c.text(x, 2.35, W - 2 * MX - .5, 2.4, lines, size, t.text_1, bold=True, spacing=1.0, font=c.f_title, para_gap=0), 'type', gap=150)
    c.clock += 30 * sum(len(l) for l in lines)
    ly = 2.35 + len(lines) * size / 72 * 1.2
    lastw = sum(1.0 if ord(ch) > 0x2E80 else .58 for ch in lines[-1]) * size / 72
    cur = c.rect(x + lastw + .12, ly - size / 72 * 1.05, .32, size / 72 * .95, fill=t.accent)
    c.a(cur, 'appear', gap=0, dur=1); c.a(cur, 'twinkle', gap=0, dur=1000, repeat='indefinite', grp=1, params={'low': 0})
    if s.get('subtitle'): c.a(c.text(x, ly + .25, W - 2 * MX - .5, .5, '# ' + s['subtitle'], 17, t.text_2, font=c.f_num), 'fade', gap=100)
    if s.get('stats'): _stat_strip(c, s['stats'], H - 2.15, x0=x, x1=W - MX - .2, size=32)


COVERS = {'swiss': _cover_swiss, 'bento': _cover_bento, 'brutal': _cover_brutal, 'ink': _cover_ink, 'term': _cover_term}

CN_NO = dict(zip('0123456789', '〇壹贰叁肆伍陆柒捌玖'))


def _section_skin(c, s, deck, mode):
    t = c.t; no = s.get('no', ''); title = s['title']
    if mode == 'swiss':
        c.s.background.fill.solid(); c.s.background.fill.fore_color.rgb = rgb(t.accent)
        c.a(c.text(MX - .1, .2, W, 3.6, no, 280, 'FFFFFF', bold=True, spacing=.8, font=c.f_num), 'rise', at=0, dur=700)
        c.a(c.rect(MX, 4.25, W - 2 * MX, .06, fill='FFFFFF'), 'wipe-right', gap=150, dur=500)
        c.a(c.text(MX, 4.5, W - 2 * MX, 1.1, title, 50, 'FFFFFF', bold=True, font=c.f_title), 'rise', gap=100)
        if s.get('subtitle'): c.a(c.text(MX, 5.6, 9, .8, s['subtitle'], 18, mix('FFFFFF', t.accent, .8)), 'fade-up', gap=100)
    elif mode == 'bento':
        background(c, 'section'); R = t.radius
        c.a(c.rect(MX, .6, 4.2, H - 1.2, fill=t.accent, radius=R), 'zoom', at=0, dur=550)
        c.a(c.rect(MX + 4.42, .6, W - 2 * MX - 4.42, H - 1.2, fill=t.surface, radius=R), 'zoom', at=100, dur=550)
        c.a(c.text(MX + .3, H - 3.6, 3.7, 3, no, 170, 'FFFFFF', bold=True, anchor='b', font=c.f_num), 'rise', at=400, dur=700)
        c.a(c.text(MX + 5.0, 2.6, W - 2 * MX - 5.5, 1.4, title, 46, t.text_1, bold=True, font=c.f_title), 'rise', at=500, dur=700)
        if s.get('subtitle'): c.a(c.text(MX + 5.0, 3.9, W - 2 * MX - 5.6, 1, s['subtitle'], 18, t.text_2, spacing=1.4), 'fade-up', gap=100)
    elif mode == 'brutal':
        c.s.background.fill.solid(); c.s.background.fill.fore_color.rgb = rgb(t.accent_3)
        c.s.shapes.add_picture(str(pattern_png('dots', t.text_1, .18)), 0, 0, Inches(W), Inches(H))
        sh = c.rect(MX + .12, 1.02, 4.2, 2.7, fill=t.border_strong); bx = c.rect(MX, .9, 4.2, 2.7, fill=t.accent, line=t.border_strong, lw=3)
        nt = c.text(MX, .9, 4.2, 2.7, no, 170, 'FFFFFF', align='c', anchor='m', font=c.f_num, bold=True)
        g = c.s.shapes.add_group_shape([sh, bx, nt]); g.rotation = -4
        c.a(g, 'pop', at=0, dur=500)
        c.a(c.text(MX, 4.25, W - 2 * MX, 1.3, title, 66, t.text_1, font=c.f_title), 'rise', gap=200, dur=650)
        if s.get('subtitle'): c.a(c.text(MX, 5.55, 10, .8, s['subtitle'], 20, t.text_1, bold=True), 'fade-up', gap=100)
    elif mode == 'ink':
        background(c, 'section')
        n_cn = ''.join(CN_NO.get(ch, ch) for ch in no.lstrip('0') or no)
        c.a(c.text(MX, .9, 4, 3.4, n_cn, 210, t.accent, font=c.f_title), 'fade', at=0, dur=900)
        tt = title.replace(' ', ''); sz = min(60, int((H - 1.2) / (len(tt) * 1.08) * 72))
        tx = vertical(c.text(W - MX - sz / 72 * 1.5, .6, sz / 72 * 1.5, H - 1.2, tt, sz, t.text_1, font=c.f_title))
        c.a(tx, 'wipe-down', at=400, dur=900)
        c.a(c.line(MX, 4.6, MX + 1.6, 4.6, t.text_1, 1.5), 'draw', gap=100, dur=400)
        if s.get('subtitle'): c.a(c.text(MX, 4.85, 7, 1.2, s['subtitle'], 20, t.text_2, spacing=1.5, font=c.f_quote), 'fade-up', gap=100)
    elif mode == 'term':
        background(c, 'section')
        c.a(c.text(MX, 1.3, 10, .4, f'$ cd ./chapter_{no}/ && cat README.md', 16, t.text_3, font=c.f_num), 'type', at=0)
        c.clock += 600
        c.a(c.text(MX, 2.0, 6, 2.2, no, 160, t.accent, bold=True, spacing=.9, font=c.f_num), 'pop', gap=100, dur=500)
        c.a(c.text(MX, 4.3, W - 2 * MX, 1.0, '# ' + title, 44, t.text_1, bold=True, font=c.f_title), 'type', gap=100)
        c.clock += 30 * len(title)
        if s.get('subtitle'): c.a(c.text(MX, 5.35, 10, .8, '// ' + s['subtitle'], 18, t.text_2, font=c.f_num), 'fade', gap=100)
    else:
        return False
    return True


def _quote_skin(c, s, mode):
    """返回 (正文色, 强调色, 引号色, 署名色, 字体)；同时画好背景"""
    t = c.t
    if mode == 'swiss':
        c.s.background.fill.solid(); c.s.background.fill.fore_color.rgb = rgb(t.accent)
        return 'FFFFFF', 'FFFFFF', '111111', 'FFFFFF', c.f_quote
    if mode == 'brutal':
        c.s.background.fill.solid(); c.s.background.fill.fore_color.rgb = rgb(t.accent_3)
        c.s.shapes.add_picture(str(pattern_png('dots', t.text_1, .18)), 0, 0, Inches(W), Inches(H))
        return t.text_1, t.accent, t.accent, t.text_1, c.f_quote
    if mode == 'ink':
        background(c, 'section')
        return t.text_1, t.accent, t.accent, t.text_2, c.f_quote
    if mode == 'bento':
        background(c, 'section')
        c.a(c.rect(MX - .2, .7, W - 2 * MX + .4, H - 1.4, fill=t.surface, radius=t.radius), 'zoom', at=0, dur=500)
        return t.text_1, t.accent, t.accent, t.text_3, c.f_quote
    if mode == 'term':
        background(c, 'section')
        return t.text_1, t.accent, t.accent, t.text_3, c.f_quote
    return None


def L_cover(c, s, deck):
    t = c.t; mode = s.get('cover', c.style.get('cover', 'dark'))
    if mode in COVERS: return COVERS[mode](c, s, deck)
    title = s['title']; lines = title if isinstance(title, list) else [title]
    if mode == 'photo' and s.get('image'):
        c.s.background.fill.solid(); c.s.background.fill.fore_color.rgb = rgb(HERO_BG)
        pic = c.picture(img_path(deck, s['image']), 0, 0, W, H)
        c.a(pic, 'fade', at=0, hold=True, dur=900)
        c.scrim(0, 0, W, H, mix(t.bg, '000000', .7), 'left', .95)
        y = 1.5
        if s.get('kicker'):
            c.a(c.text(MX, y, 8, .35, s['kicker'].upper(), 12, t.accent, bold=True, tracking=3, font=c.f_num), 'fade', at=100); y += .6
        c.a(c.text(MX, y, 8, 2.4, lines, s.get('title_size', 52), HERO_TX, bold=True, spacing=1.0, font=c.f_title, para_gap=0), 'rise', gap=100, dur=800)
        y += .35 + len(lines) * s.get('title_size', 52) / 72 * 1.22
        if s.get('subtitle'):
            c.a(c.text(MX, y, 7, .9, s['subtitle'], 18, HERO_TX2, spacing=1.4), 'fade-up', gap=120)
        if s.get('stats'): _stat_strip(c, s['stats'], H - 1.95, light=True, x1=W * .62, size=30)
        if s.get('meta'): c.a(c.text(W - MX - 5, H - .55, 5, .3, s['meta'], 10, HERO_TX2, align='r'), 'fade', gap=100)
        credit(c, s.get('credit'), light=True, y=H - .9)
        return
    background(c, 'cover')
    if mode == 'report':   # 白底 / 纸色报告封面（B01 / B09）
        if c.style.get('frame') == 'masthead':
            c.text(MX, .3, W - 2 * MX, .6, deck.get('masthead', ''), 30, t.text_1, bold=True, align='c', font=c.f_title)
            c.rect(MX, .98, W - 2 * MX, .025, fill=t.border_strong); c.rect(MX, 1.05, W - 2 * MX, .01, fill=t.border_strong)
            top = 1.2
        else:
            c.a(c.rect(0, 0, W, .07, fill=t.accent), 'wipe-right', at=0, dur=600)
            top = .45
        c.a(c.text(MX, top, 7, .3, (s.get('kicker') or '').upper(), 10.5, t.text_3, tracking=2.5, font=c.f_num), 'fade', at=0)
        if s.get('meta'): c.a(c.text(W - MX - 6, top, 6, .3, s['meta'], 10.5, t.text_3, align='r'), 'fade', at=0)
        y = top + .75
        size = s.get('title_size', 58)
        c.a(c.text(MX, y, W - 2 * MX, 2.6, lines, size, t.text_1, bold=True, spacing=1.0, font=c.f_title, para_gap=0), 'rise', gap=80, dur=800)
        y += .35 + len(lines) * size / 72 * 1.22
        if s.get('subtitle'):
            c.a(c.text(MX, y, 8.5, .9, s['subtitle'], 20, t.text_2, spacing=1.4), 'fade-up', gap=120)
        if s.get('stats'): _stat_strip(c, s['stats'], H - 2.1, size=36)
        return
    # dark：聚光 + 网络 + 信号波纹
    if s.get('visual', 'network') == 'network':
        c.network(6.9, .6, 6.0, 6.2, n=18, start=0, alpha=.28 if t.dark else .22)
        hx, hy = 10.0, 3.4
        c.rings(hx, hy, 5.0, t.accent, n=3, start=600)
        hub = c.oval(hx, hy, 1.25, fill=t.accent)
        c.a(hub, 'pop', at=500, hold=True, dur=700)
        c.a(c.text(hx - .62, hy - .3, 1.24, .6, s.get('badge', '5G'), 26, t.accent_ink, bold=True, align='c', anchor='m', font=c.f_num),
            'zoom', at=800, hold=True, dur=500)
    y = 1.4
    if s.get('kicker'):
        c.a(c.text(MX, y, 7, .35, s['kicker'].upper(), 12, t.accent, bold=True, tracking=3, font=c.f_num), 'fade', at=100); y += .55
    size = s.get('title_size', 58 if c.f_display != c.f_title else (46 if max(len(l) for l in lines) <= 9 else 40))
    c.a(c.text(MX, y, 6.8, 2.6, lines, size, t.text_1, bold=c.f_display == c.f_title, spacing=1.0, font=c.f_display, para_gap=0),
        s.get('title_anim', 'type'), gap=150)
    c.clock += 25 * sum(len(l) for l in lines) + 200
    y += .3 + len(lines) * size / 72 * 1.2
    c.a(c.gradbar(MX, y, 1.1, .06, t.grad), 'draw', gap=100, dur=500)
    if s.get('subtitle'):
        c.a(c.text(MX, y + .3, 6.4, .9, s['subtitle'], 18, t.text_2, spacing=1.35), 'fade-up', gap=150)
    if s.get('stats'): _stat_strip(c, s['stats'], H - 1.9, x1=W * .55, size=30)
    elif s.get('meta'):
        c.a(c.text(MX, H - 1.15, 7, .35, s['meta'], 12, t.text_3, tracking=1), 'fade', gap=200)


def L_agenda(c, s, deck):
    """目录：横排 N 列。每列 = 顶部细线 + 超大章节号 + 标题 + 说明 + 底部缩略图（可选）。整页排满"""
    t = c.t
    background(c)
    y0 = header(c, dict(s, kicker=s.get('kicker', 'CONTENTS')))
    items = s['items']; n = len(items); gap = .35
    w = (W - 2 * MX - gap * (n - 1)) / n; y = y0 + .25
    has_img = any(it.get('image') for it in items)
    c.clock += 100
    for i, it in enumerate(items):
        x = MX + i * (w + gap); hl = it.get('highlight')
        c.a(c.rect(x, y, w, .03 if i == 0 else .015, fill=t.accent if i == 0 else t.border_strong), 'wipe-right', gap=90 if i else 0, dur=450)
        if not has_img:   # 没图：大号章节号占上半，标题说明压在底部，整列撑满
            c.a(c.rect(x, y + .03, w, H - 1.0 - y - .03, fill=t.accent if i == 0 else t.text_3, alpha=.06 if i == 0 else .04), 'fade', gap=0, dur=500)
            c.a(c.text(x + .25, y + .3, w - .5, 1.8, f'{i+1:02d}', 96, t.accent if i == 0 else t.text_1, bold=True, spacing=1, font=c.f_num), 'rise', gap=40, dur=600)
            by = H - 1.0 - 1.75
            c.a(c.text(x + .25, by, w - .5, .8, it['title'], 20, t.text_1, bold=True, spacing=1.2), 'fade-up', gap=40)
            c.a(c.text(x + .25, by + .8, w - .5, .9, it.get('text', ''), 14, t.text_2, spacing=1.45), 'fade-up', gap=40)
            c.clock -= 260; continue
        c.a(c.text(x, y + .2, w, 1.1, f'{i+1:02d}', 60, t.accent if i == 0 else t.text_1, bold=True, spacing=1, font=c.f_num), 'rise', gap=40, dur=600)
        c.a(c.text(x, y + 1.35, w, .8, it['title'], 18, t.text_1, bold=True, spacing=1.2), 'fade-up', gap=40)
        c.a(c.text(x, y + 2.15, w, .9, it.get('text', ''), 13, t.text_2, spacing=1.45), 'fade-up', gap=40)
        if has_img and it.get('image'):
            ih = H - 1.0 - (y + 3.1)
            c.a(c.picture(img_path(deck, it['image']), x, y + 3.1, w, ih, radius=t.radius), 'fade-up', gap=60, dur=600)
        c.clock -= 260
    c.clock += 260

def L_section(c, s, deck):
    """章节页：有图 = 满版照片 + 左侧渐变遮罩（整套里的「变调」页）；无图 = 底色 + 网络装饰"""
    t = c.t
    if not s.get('image') and _section_skin(c, s, deck, c.style.get('section')): return
    if s.get('image'):
        c.s.background.fill.solid(); c.s.background.fill.fore_color.rgb = rgb(HERO_BG)
        pic = c.picture(img_path(deck, s['image']), 0, 0, W, H)
        c.a(pic, 'fade', at=0, hold=True, dur=600)
        c.scrim(0, 0, W, H, HERO_BG, 'left', .95)
        credit(c, s.get('credit'), light=True, y=H - .45)
        tx1, tx2 = HERO_TX, HERO_TX2
        ac = t.accent if t.dark else mix(t.accent, 'FFFFFF', .8)
    elif not t.dark:   # 浅色风格没图：深色底 + 强调色光晕，同样做「变调」页
        c.s.background.fill.solid(); c.s.background.fill.fore_color.rgb = rgb(HERO_BG)
        c.glow(W - 7, -4, 11, t.accent, .22)
        tx1, tx2, ac = HERO_TX, HERO_TX2, mix(t.accent, 'FFFFFF', .8)
    else:
        background(c, 'section')
        tx1, tx2, ac = t.text_1, t.text_2, t.accent
    tw = 7.0
    c.a(c.text(MX, 1.3, 5.5, 2.3, s.get('no', ''), 150, ac, bold=True, spacing=.9, name='!!secno', font=c.f_num), 'pop', at=0, dur=600)
    c.a(c.line(MX + .05, 3.85, MX + 1.4, 3.85, ac, 3), 'draw', gap=200, dur=450)
    size = 40 if len(s['title']) * 40 / 72 * 1.02 <= tw else 32
    nl = 1 if len(s['title']) * size / 72 * 1.02 <= tw else 2
    c.a(c.text(MX, 4.1, tw, 1.4, s['title'], size, tx1, bold=True, spacing=1.1, font=c.f_title), 'rise', gap=100, dur=650)
    if s.get('subtitle'):
        c.a(c.text(MX, 4.15 + nl * size / 72 * 1.3 + .15, tw, .9, s['subtitle'], 18, tx2, spacing=1.4), 'fade-up', gap=120)

# ================================================================== 数字
def _split_bar(c, sp, y, x0=MX, x1=None):
    """100% 构成条：一根横条按比例切段，重点段用强调色，标签在条上方、数值在条内"""
    t = c.t; x1 = x1 or (W - MX); parts = sp['parts']; tot = sum(p_['value'] for p_ in parts)
    c.a(c.text(x0, y, x1 - x0, .35, sp.get('title', ''), 14, t.text_1, bold=True), 'fade', gap=150)
    if sp.get('note'): c.a(c.text(x0, y, x1 - x0, .35, sp['note'], 11, t.text_3, align='r'), 'fade', gap=0)
    by = y + .85; bh = .62; x = x0; base = c.clock + 80
    shades = [t.accent, mix(t.text_3, t.bg, .45), mix(t.text_3, t.bg, .7), mix(t.text_3, t.bg, .85)]
    for i, p_ in enumerate(parts):
        w = (x1 - x0) * p_['value'] / tot; hl = p_.get('highlight', i == 0)
        col = t.accent if hl else shades[min(i, 3)]
        seg = c.rect(x + .02, by, w - .04, bh, fill=col)
        c.a(seg, 'wipe-right', at=base + i * 350, hold=True, dur=500)
        c.a(c.text(x, by - .38, w, .3, p_['name'], 12, t.accent if hl else t.text_2, bold=hl), 'fade', at=base + i * 350 + 200, hold=True)
        c.a(c.text(x + .15, by, w - .3, bh, p_.get('label', f"{p_['value'] / tot * 100:.0f}%"), 15,
                   t.accent_ink if hl else t.text_1, bold=True, anchor='m', font=c.f_num), 'fade', at=base + i * 350 + 300, hold=True)
        x += w
    c.clock = base + len(parts) * 350 + 400
    return by + bh


def L_kpi(c, s, deck):
    t = c.t
    background(c); y0 = header(c, s)
    items = s['items']; n = len(items)
    if c.style.get('card') in ('hairline', 'dark', 'swiss', 'ink'):   # 大数字条：细线分隔、不套卡片（A11 / B01 / B09）
        c.clock += 100
        _stat_strip(c, items, y0 + .45, size=s.get('value_size', 54 if n <= 3 else 44))
        yy = y0 + .45 + 54 / 60 + 1.25
        if s.get('split'):
            _split_bar(c, s['split'], yy + .4)
        elif s.get('summary'):
            c.a(c.rect(MX, yy + .25, W - 2 * MX, .012, fill=t.border), 'wipe-right', gap=150, dur=500)
            c.a(c.text(MX, yy + .5, W * .62, 1.2, s['summary'], 18, t.text_1, spacing=1.45, font=c.f_title), 'fade-up', gap=80)
        source(c, s.get('source'))
        return
    gap = .3; w = (W - 2 * MX - gap * (n - 1)) / n; h = 2.45 if s.get('split') else 2.7; y = y0 + .2
    c.clock += 200
    for i, it in enumerate(items):
        x = MX + i * (w + gap); hl = it.get('highlight')
        card = c.card(x, y, w, h, hl=hl)
        c.a(card, 'fade-up', gap=140, dur=550)
        c.a(c.text(x + .32, y + .28, w - .6, .35, it['label'], 13, t.text_2), 'fade', gap=60)
        em = sum(1.0 if ord(ch) > 0x2E80 else (.3 if ch in '.,' else .6) for ch in it['value'])
        size = min(48, int((w - .7) / em * 72 / 1.05))
        c.counter(x + .3, y + .68, w - .5, 1.0, it['value'], size, t.accent if hl else t.text_1, gap=40)
        if it.get('delta'):
            up = it.get('trend', 'up') == 'up'
            good = up if not it.get('lower_is_better') else not up
            c.a(c.text(x + .32, y + 1.72, w - .6, .35, ('▲ ' if up else '▼ ') + it['delta'], 13, t.good if good else t.bad, bold=True),
                'fade-up', gap=60)
        if it.get('note'):
            c.a(c.text(x + .32, y + h - .45, w - .6, .3, it['note'], 11, t.text_3), 'fade', gap=40)
        c.clock -= 900
    c.clock += 900
    yy = y + h + .35
    if s.get('split'):
        yy = _split_bar(c, s['split'], yy + .05) + .3
    if s.get('summary'):
        c.a(c.text(MX, yy, W - 2 * MX, .8, s['summary'], 16, t.text_2, spacing=1.45), 'fade-up', gap=150)
    source(c, s.get('source'))

def L_stat(c, s, deck):
    """一个巨型数字（stat-highlight）+ 右侧动态仪表盘：进度弧顺时针扫出、数字滚动、卫星绕轨道、外圈波纹"""
    import shapecharts as sc
    t = c.t
    background(c)
    g = s.get('gauge')
    hx, hy = 10.05, 3.75
    if g:
        frac = g['value'] / g.get('max', 100)
        c.rings(hx, hy, 5.9, t.accent, n=2, start=900, period=3600, width=1)
        track = sc.arc(c, hx, hy, 4.0, 0, 360, t.border, thickness=.09)
        c.a(track, 'fade', at=0, hold=True, dur=500)
        prog = sc.arc(c, hx, hy, 4.0, 0, 360 * frac, t.accent, thickness=.09)
        c.a(prog, 'wheel', at=150, hold=True, dur=1300)
        # 进度弧末端的发光点
        import math
        ang = math.radians(360 * frac - 90); r = 2.0 - .09
        tip = c.oval(hx + r * math.cos(ang), hy + r * math.sin(ang), .2, fill=t.accent)
        c.a(tip, 'pop', at=1350, hold=True, dur=400)
        c.a(c.glow(hx + r * math.cos(ang) - .45, hy + r * math.sin(ang) - .45, .9, t.accent, .7), 'fade', at=1350, hold=True, dur=500)
        # 轨道 + 卫星（orbit-ring）
        orbit = c.oval(hx, hy, 5.0, line=t.text_3, lw=.5, line_alpha=.5)
        c.a(orbit, 'fade', at=300, hold=True, dur=600)
        parts = [c.oval(hx, hy, 5.0)]
        for k, (deg, sz, col) in enumerate(((20, .16, t.accent), (150, .11, t.accent_2), (255, .13, t.accent_3))):
            a_ = math.radians(deg)
            parts.append(c.oval(hx + 2.5 * math.cos(a_), hy + 2.5 * math.sin(a_), sz, fill=col))
        sat = c.s.shapes.add_group_shape(parts)
        c.a(sat, 'fade', at=500, hold=True, dur=600)
        c.a(sat, 'spin', at=500, hold=True, dur=9000, repeat='indefinite', grp=1)
        c.clock = 150
        c.counter(hx - 1.6, hy - .6, 3.2, 1.0, g.get('text', f"{g['value']}%"), 50, t.text_1, gap=0, align='c', dur=1300)
        c.a(c.text(hx - 1.5, hy + .42, 3.0, .4, g.get('label', ''), 13, t.text_3, align='c', tracking=1), 'fade', at=600, hold=True)
    else:
        c.rings(hx, hy, 5.6, t.accent, n=4, start=300, period=3200)
        hub = c.oval(hx, hy, 1.6, fill=t.accent)
        c.a(hub, 'pop', at=200, hold=True, dur=700)
        c.a(c.text(hx - .8, hy - .4, 1.6, .8, s.get('badge', ''), 24, t.accent_ink, bold=True, align='c', anchor='m'), 'zoom', at=500, hold=True)
    c.clock = 0
    y = 1.2
    if s.get('kicker'):
        c.a(c.text(MX, y, 7, .35, s['kicker'], 12, t.accent, bold=True, tracking=3), 'fade', at=0); y += .5
    c.a(c.text(MX, y, 7, .5, s.get('label', ''), 20, t.text_2), 'rise', gap=60); y += .65
    c.counter(MX - .05, y, 7.5, 1.9, s['value'], s.get('value_size', 110), t.accent, gap=100, dur=1300)
    y += 2.05
    if s.get('delta'):
        c.a(c.text(MX, y, 7, .4, '▲ ' + s['delta'], 16, t.good, bold=True), 'fade-up', gap=100); y += .6
    if s.get('text'):
        c.a(c.text(MX, y, 6.4, 1.6, s['text'], 15, t.text_2, spacing=1.5), 'fade-up', gap=100)
    source(c, s.get('source'))


# ================================================================== 图表
def L_chart(c, s, deck):
    t = c.t
    background(c); y0 = header(c, s)
    ch = s['chart']
    side = s.get('insights') or s.get('stats')
    cw = (W - 2 * MX) * (.6 if side else 1)
    cy = y0 + .15
    if ch.get('unit') and pick_chart(ch) not in ('doughnut', 'pie'):
        c.a(c.text(MX, y0 - .1, 4, .3, '单位：' + ch['unit'], 10, t.text_3), 'fade', gap=100); cy += .2
    chh = H - cy - 1.05
    add_chart(c, ch, MX, cy, cw, chh)
    if s.get('stats'):   # 右侧小数字
        sx = MX + cw + .5; sw = W - MX - sx; n = len(s['stats']); rh = chh / n
        for i, st in enumerate(s['stats']):
            yy = cy + i * rh
            c.a(c.line(sx, yy + .05, sx, yy + rh - .25, t.accent if i == 0 else t.border, 2), 'wipe-down', gap=120, dur=400)
            c.a(c.text(sx + .3, yy, sw - .3, .35, st['label'], 12, t.text_3), 'fade', gap=40)
            c.counter(sx + .28, yy + .32, sw - .3, .8, st['value'], 34, t.accent if i == 0 else t.text_1, gap=40)
            if st.get('note'): c.a(c.text(sx + .3, yy + 1.08, sw - .3, .4, st['note'], 11, t.text_2), 'fade', gap=40)
    elif s.get('insights'):
        sx = MX + cw + .45; sw = W - MX - sx
        ins = s['insights']; ih = min(1.6, (chh - .2 * (len(ins) - 1)) / len(ins))
        c.clock += 200
        for i, txt in enumerate(ins):
            yy = cy + i * (ih + .2)
            c.a(c.rect(sx, yy, .05, ih, fill=t.accent if i == 0 else t.border), 'wipe-down', gap=150, dur=400)
            c.a(c.text(sx + .28, yy + .02, sw - .3, ih, txt, 14, t.text_2, spacing=1.45), 'fade-left', gap=60)
    source(c, s.get('source'))


def L_charts(c, s, deck):
    """两张图并排（如：流量 vs ARPU 的剪刀差）"""
    t = c.t
    background(c); y0 = header(c, s)
    gap = .5; pw = (W - 2 * MX - gap) / 2
    for k, p in enumerate(s['panels']):
        x = MX + k * (pw + gap); y = y0 + .15
        card = c.card(x, y, pw, H - y - 1.0)
        c.a(card, 'fade-up', gap=150 if k == 0 else 60, dur=550)
        c.a(c.text(x + .35, y + .25, pw - .7, .4, p['title'], 16, t.text_1, bold=True), 'fade', gap=60)
        if p.get('note'): c.a(c.text(x + .35, y + .65, pw - .7, .35, p['note'], 11, t.text_3), 'fade', gap=30)
        add_chart(c, p['chart'], x + .25, y + 1.05, pw - .5, H - y - 2.85, gap=100, legend_side=False)
        if p.get('takeaway'):
            c.a(c.text(x + .35, H - 1.55, pw - .7, .45, p['takeaway'], 13, t.text_2), 'fade-up', gap=120)
    source(c, s.get('source'))


def L_table(c, s, deck):
    """表格：表头粗线 + 行发丝线；数字列自动加「数据条」（单元格里的浅色横条，一眼比大小）；行高随行数放大排满"""
    import re
    t = c.t
    background(c); y0 = header(c, s)
    cols = s['columns']; rows = s['rows']
    vw = lambda z: sum(2 if ord(ch) > 0x2E80 else 1 for ch in str(z))
    lens = [max(vw(r[j]) for r in rows + [cols]) for j in range(len(cols))]
    tot = sum(max(l, 6) for l in lens); ws = [(W - 2 * MX) * max(l, 6) / tot for l in lens]
    room = H - y0 - 1.25 - (1.1 if s.get('summary') else 0)
    rh = min(.95, room / (len(rows) + .7)); hh = min(.6, rh * .7); y = y0 + .15
    hl = s.get('highlight_row')
    num = lambda v: float(re.sub(r'[^\d.]', '', str(v))) if re.search(r'\d', str(v)) else None
    num_col = [sum(num(r[j]) is not None for r in rows) >= max(1, len(rows) - 1) and j > 0 for j in range(len(cols))]
    bar_cols = s.get('bars', [j for j in range(len(cols)) if num_col[j]])
    x = MX; hdr = []
    for j, col in enumerate(cols):
        hdr.append(c.text(x + .15, y, ws[j] - .3, hh, col, 12, t.text_3, bold=True, anchor='b', align='r' if num_col[j] else 'l'))
        x += ws[j]
    cm = c.style.get('card')
    if cm in ('brutal', 'swiss'):   # 实心表头条
        bar = c.rect(MX, y - .08, W - 2 * MX, hh + .2, fill=t.border_strong if cm == 'brutal' else t.accent)
        hdr.insert(0, bar); c.s.shapes._spTree.remove(bar._element); c.s.shapes._spTree.insert(2, bar._element)
        for h_ in hdr[1:]:
            for r_ in h_.text_frame.paragraphs[0].runs: r_.font.color.rgb = rgb(t.accent_3 if cm == 'brutal' else 'FFFFFF')
    hdr.append(c.rect(MX, y + hh + .08, W - 2 * MX, .025, fill=t.border_strong))
    c.a(c.s.shapes.add_group_shape(hdr), 'fade', gap=150)
    y += hh + .1
    vmax = {j: max((num(r[j]) or 0) for r in rows) or 1 for j in bar_cols}
    for i, r in enumerate(rows):
        yy = y + rh * i; parts = []; bars = []
        if i == hl: parts.append(c.rect(MX, yy, W - 2 * MX, rh, fill=t.accent, alpha=.08))
        x = MX
        for j, v in enumerate(r):
            if j in bar_cols and num(v) is not None:
                bw = (ws[j] - .3) * num(v) / vmax[j]
                bars.append(c.rect(x + ws[j] - .15 - bw, yy + rh * .7, bw, .07, fill=t.accent if i == hl else mix(t.text_3, t.bg, .55)))
            parts.append(c.text(x + .15, yy, ws[j] - .3, rh * .85 if j in bar_cols else rh, str(v), 16 if j else 15,
                                t.accent if (i == hl and j) else (t.text_1 if j == 0 or j in bar_cols else t.text_2),
                                bold=(j == 0 or i == hl), anchor='m', align='r' if num_col[j] else 'l',
                                font=c.f_num if num_col[j] else None))
            x += ws[j]
        parts.append(c.rect(MX, yy + rh - .01, W - 2 * MX, .01, fill=t.border))
        c.a(c.s.shapes.add_group_shape(parts), 'fade-left', gap=110, dur=500)
        for b in bars: c.a(b, 'wipe-right', gap=0 if b is not bars[0] else 60, dur=600)
    if s.get('summary'):
        sy = y + rh * len(rows) + .35
        c.a(c.rect(MX, sy, .05, .75, fill=t.accent), 'wipe-down', gap=150, dur=400)
        c.a(c.text(MX + .25, sy, W - 2 * MX - .3, .8, s['summary'], 16, t.text_1, spacing=1.45, anchor='m'), 'fade-left', gap=60)
    source(c, s.get('source'))

# ================================================================== 文字结构
def L_points(c, s, deck):
    t = c.t
    background(c); y0 = header(c, s)
    items = s['items']; n = len(items)
    cols = n if n <= 4 else (3 if n in (5, 6) else 4); rows = (n + cols - 1) // cols
    gap = .3; w = (W - 2 * MX - gap * (cols - 1)) / cols
    h = min(3.4, (H - y0 - 1.15 - gap * (rows - 1)) / rows)
    c.clock += 200
    for i, it in enumerate(items):
        x = MX + (i % cols) * (w + gap); y = y0 + .15 + (i // cols) * (h + gap)
        step = (i + 1) if s.get('click') else 0
        if step: c.clock = 0
        card = c.card(x, y, w, h)
        c.a(card, 'fade-up', gap=120, dur=550, step=step)
        c.a(c.text(x + .32, y + .3, 1.5, .5, it.get('no', f'{i+1:02d}'), 22, t.accent, bold=True), 'pop', gap=60, step=step)
        c.a(c.text(x + .32, y + .95, w - .64, .9, it['title'], 18, t.text_1, bold=True, spacing=1.15), 'fade-up', gap=40, step=step)
        c.a(c.text(x + .32, y + 1.55, w - .64, h - 1.8, it.get('text', ''), 13, t.text_2, spacing=1.45), 'fade-up', gap=40, step=step)
    source(c, s.get('source'))


def L_compare(c, s, deck):
    t = c.t
    background(c); y0 = header(c, s)
    gap = .9; w = (W - 2 * MX - gap) / 2; h = H - y0 - 1.25; y = y0 + .2
    c.clock += 150
    for k, side in enumerate(('left', 'right')):
        d = s[side]; x = MX + k * (w + gap); win = (k == 1)
        card = c.card(x, y, w, h, hl=win)
        c.a(card, 'fade-right' if k else 'fade-left', gap=200 if k else 0, dur=650)
        c.a(c.text(x + .4, y + .35, w - .8, .35, d.get('tag', ''), 11, t.accent if win else t.text_3, bold=True, tracking=2), 'fade', gap=60)
        c.a(c.text(x + .4, y + .75, w - .8, .7, d['title'], 24, t.text_1 if win else t.text_2, bold=True), 'fade-up', gap=60)
        for j, it in enumerate(d['items']):
            c.a(c.text(x + .4, y + 1.6 + j * .55, w - .8, .5, '— ' + it, 15, t.text_1 if win else t.text_2), 'fade-up', gap=70)
        if k == 0:
            ax = MX + w + .15
            c.a(c.line(ax, y + h / 2, ax + gap - .3, y + h / 2, t.accent, 2.5, arrow=True), 'draw', gap=150, dur=500)
    source(c, s.get('source'))


def L_timeline(c, s, deck):
    """按 html-ppt timeline.html 还原：一条细横线，年份在线上方（小号、字距、灰），
    圆点压在线上（实心强调色 + 背景色描边 + 外圈强调色细环），标题和说明在下方居中；
    整列作为一个整体 rise 入场，每列错开 0.1 秒（anim-stagger-list）。
    有 chart 时，下方再画「柱 + 折线」组合图，和时间轴共用横坐标（每列正下方一根柱）"""
    import shapecharts as sc
    t = c.t
    background(c); y0 = header(c, s)
    items = s['items']; n = len(items)
    gapx = .15; colw = (W - 2 * MX - gapx * (n - 1)) / n
    top = y0 + (.35 if s.get('chart') else .55)
    line_y = top + .33
    c.a(c.rect(MX, line_y - .007, W - 2 * MX, .014, fill=t.border), 'fade', gap=80, dur=500)
    base = c.clock
    for i, it in enumerate(items):
        x = MX + i * (colw + gapx); cx = x + colw / 2; hl = it.get('highlight')
        parts = [c.text(x, top - .08, colw, .3, it['time'], 12, t.accent if hl else t.text_3, bold=True, align='c', tracking=1.5, font=c.f_num)]
        d = .24 if hl else .2
        parts.append(c.oval(cx, line_y, d + .1, line=t.accent, lw=1.25))
        parts.append(c.oval(cx, line_y, d, fill=t.accent, line=t.bg, lw=2.5))
        parts.append(c.text(x, top + .62, colw, .45, it['title'], 17 if hl else 16, t.accent if hl else t.text_1, bold=True, align='c', font=c.f_num))
        if it.get('text'):
            parts.append(c.text(x + .05, top + 1.08, colw - .1, .6, it['text'], 12, t.text_2, align='c', spacing=1.35))
        grp = c.s.shapes.add_group_shape(parts)
        c.a(grp, 'rise', at=base + 50 + 100 * i, hold=True, dur=650)
    c.clock = base + 50 + 100 * n + 650
    ch = s.get('chart')
    if ch:
        # 组合图：柱 = bars 系列（左轴），折线 = line 系列（右轴，0–100%）
        gy = top + 1.75; bottom = H - 1.05; ph = bottom - gy - .45
        c.a(c.text(MX, gy, 6, .3, ch.get('title', ''), 12, t.text_3), 'fade', gap=0)
        lg = ch.get('line_name')
        if lg:
            c.a(c.line(W - MX - 2.6, gy + .15, W - MX - 2.25, gy + .15, t.accent, 2.25), 'fade', gap=0)
            c.a(c.text(W - MX - 2.15, gy, 2.15, .3, lg, 12, t.text_3), 'fade', gap=0)
        ptop = gy + .45
        c.a(c.rect(MX, bottom, W - 2 * MX, .012, fill=t.border_strong), 'fade', gap=0)
        bv = ch['bars']; lv = ch.get('line'); bmax = max(bv) * 1.05
        t0 = c.clock
        bw = min(.9, colw * .42)
        for i, v in enumerate(bv):
            cx = MX + i * (colw + gapx) + colw / 2; hl = items[i].get('highlight')
            bh = ph * v / bmax * .78
            bar = c.rect(cx - bw / 2, bottom - bh, bw, bh, fill=t.accent if hl else mix(t.text_3, t.bg, .55))
            c.a(bar, 'grow-up', at=t0 + 60 * i, hold=True, dur=900)
        c.clock = t0 + 60 * n + 900
        if lv:
            lmax = ch.get('line_max', 100)
            pts = [(MX + i * (colw + gapx) + colw / 2, ptop + ph * (1 - v / lmax)) for i, v in enumerate(lv)]
            curve = sc._smooth(pts, .3)
            ln = sc.custom_shape(c, [('M', pts[0][0], bottom)] + curve, line=t.text_1, lw=2.25)
            c.a(ln, 'grow-up', at=t0 + 200, hold=True, dur=1100)
            for i, (px, py) in enumerate(pts):
                hl = items[i].get('highlight')
                dot = c.oval(px, py, .16 if hl else .12, fill=t.bg, line=t.text_1, lw=1.75)
                c.a(dot, 'rise-from', at=t0 + 200, hold=True, dur=1100, params={'dy': (bottom - py) / H})
                lab = c.text(px + .12, py - .36, 1.0, .28, f"{lv[i]:g}{ch.get('line_suffix', '%')}", 12, t.text_1, bold=True, font=c.f_num)
                c.a(lab, 'rise-from', at=t0 + 200, hold=True, dur=1100, params={'dy': (bottom - py) / H})
            c.clock = t0 + 1300
    elif s.get('summary'):
        c.a(c.text(MX, top + 2.6, W - 2 * MX, .8, s['summary'], 15, t.text_2, spacing=1.45), 'fade-up', gap=50)
    source(c, s.get('source'))

def L_process(c, s, deck):
    """阶梯式流程（逐级抬高）：每一步是一级台阶，越往右越高；重点步实心强调色；
    左上的三角空白放结论。台阶自下而上依次长出"""
    t = c.t
    background(c); y0 = header(c, s)
    steps = s['steps']; n = len(steps); gap = .12
    w = (W - 2 * MX - gap * (n - 1)) / n
    bottom = H - 1.0; rise = min(.75, (bottom - y0 - 2.9) / max(n - 1, 1)); h0 = 2.6
    shades = [mix(t.accent, t.bg, .1 + .07 * k) for k in range(n)]
    c.clock += 100; base = c.clock
    for i, st in enumerate(steps):
        x = MX + i * (w + gap); h = h0 + rise * i; y = bottom - h; hl = st.get('highlight')
        fill = t.accent if hl else (shades[i] if not t.dark else mix(t.accent, t.surface_2, .08 + .07 * i))
        ink1 = t.accent_ink if hl else t.text_1; ink2 = t.accent_ink if hl else t.text_2
        cm = c.style.get('card')
        if cm == 'brutal':     # 黑粗边彩色积木
            fill = [t.surface, t.accent_3, 'C9D3FF', t.accent][i % 4] if not hl else t.accent
            ink1 = t.text_1 if not hl else 'FFFFFF'; ink2 = t.text_2 if not hl else 'FFFFFF'
            blk = c.s.shapes.add_group_shape([c.rect(x + .09, y + .09, w, h, fill=t.border_strong),
                                              c.rect(x, y, w, h, fill=fill, line=t.border_strong, lw=2.25)])
        elif cm == 'swiss':    # 黑色实心块，重点红
            fill = t.accent if hl else (t.text_1 if i % 2 else '3A3A3A')
            ink1 = ink2 = 'FFFFFF'
            blk = c.rect(x, y, w, h, fill=fill)
        elif cm == 'term':     # 荧光描边的终端窗口
            fill = mix(t.accent, t.surface, .25) if hl else t.surface
            ink1 = t.text_1; ink2 = t.text_2
            blk = c.rect(x, y, w, h, fill=fill, line=t.accent, line_alpha=1 if hl else .4, lw=1.5, radius=t.radius)
        elif cm == 'ink':      # 宣纸上的墨框，重点朱红
            ink1 = t.text_1 if not hl else t.accent_ink; ink2 = t.text_2 if not hl else t.accent_ink
            blk = c.rect(x, y, w, h, fill=t.accent if hl else t.surface, line=t.border_strong, lw=1)
        else:
            blk = c.rect(x, y, w, h, fill=fill, radius=min(t.radius, .06))
        c.a(blk, 'grow-up', at=base + 160 * i, hold=True, dur=650)
        at = base + 160 * i + 350
        nc = t.accent_ink if hl else (t.accent if cm not in ('swiss',) else 'FFFFFF')
        if cm == 'brutal' and not hl: nc = t.text_1
        c.a(c.text(x + .3, y + .25, w - .6, .7, st.get('no', f'{i+1:02d}'), 34, nc, bold=True, font=c.f_num), 'fade-up', at=at, hold=True)
        if st.get('stage'): c.a(c.text(x + .3, y + .3, w - .6, .3, st['stage'].upper(), 10.5, ink2, align='r', tracking=1.5, font=c.f_num), 'fade', at=at, hold=True)
        c.a(c.text(x + .3, y + 1.0, w - .6, .5, st['title'], 19, ink1, bold=True), 'fade-up', at=at + 60, hold=True)
        c.a(c.text(x + .3, y + 1.5, w - .6, h - 1.6, st.get('text', ''), 13.5, ink2, spacing=1.45), 'fade-up', at=at + 120, hold=True)
    c.clock = base + 160 * n + 600
    if s.get('summary'):
        c.a(c.text(MX, y0 + .1, w * 2 - .2, bottom - h0 - y0 - .3, s['summary'], 18, t.text_1, bold=True, spacing=1.35, font=c.f_title), 'fade-up', gap=100)
    source(c, s.get('source'))

def L_arch(c, s, deck):
    """分层架构（端-管-云-用）：自下而上逐层擦出，重点层发光"""
    t = c.t
    background(c); y0 = header(c, s)
    layers = s['layers']; n = len(layers)
    gap = .16; bh = min(1.05, (H - y0 - 1.2 - gap * (n - 1)) / n); lw = 1.9
    c.clock += 150
    for k, i in enumerate(reversed(range(n))):
        L = layers[i]; y = y0 + .15 + i * (bh + gap); hl = L.get('highlight')
        band = c.rect(MX, y, W - 2 * MX, bh, fill=t.surface, line=t.accent if hl else t.border, radius=t.radius, lw=1.5 if hl else .75)
        c.a(band, 'wipe-right', gap=160 if k else 0, dur=500)
        tag = c.rect(MX + .2, y + .18, lw, bh - .36, fill=t.accent if hl else t.surface_2, radius=t.radius)
        c.a(tag, 'fade', gap=40)
        c.a(c.text(MX + .2, y + .18, lw, bh - .36, L['name'], 15, t.accent_ink if hl else t.text_1, bold=True, align='c', anchor='m'), 'fade', gap=10)
        items = L['items']; ix = MX + lw + .45; avail = W - MX - .2 - ix
        iw = min(2.6, (avail - .15 * (len(items) - 1)) / len(items))
        for j, it in enumerate(items):
            chip = c.rect(ix + j * (iw + .15), y + .22, iw, bh - .44, fill=t.accent if hl else t.bg, alpha=.16 if hl else None,
                          line=t.border, radius=t.radius)
            c.a(chip, 'pop', gap=45, dur=420)
            c.a(c.text(ix + j * (iw + .15), y + .22, iw, bh - .44, it, 13, t.text_1, align='c', anchor='m'), 'fade', gap=5)
        if hl:
            c.a(band, 'pulse', gap=300, dur=1600, grp=1, repeat=2, params={'by': 1.015})
    source(c, s.get('source'))


# ================================================================== 图片
def L_hero(c, s, deck):
    """全屏大图：可选 Ken Burns + 左侧渐变遮罩 + 大标题（可写成列表手动断行）+ 底部数字"""
    c.s.background.fill.solid(); c.s.background.fill.fore_color.rgb = rgb(HERO_BG)
    pic = c.picture(img_path(deck, s['image']), 0, 0, W, H)
    c.a(pic, 'fade', at=0, hold=True, dur=900)
    if s.get('kenburns'): c.a(pic, 'kenburns', at=0, hold=True, dur=s['kenburns'], params={'by': 1.05}, grp=1)
    c.scrim(0, 0, W, H, HERO_BG, s.get('scrim', 'left'), .95)
    t = c.t; y = 1.4; ac = t.accent if t.dark else mix(t.accent, 'FFFFFF', .8)
    if s.get('kicker'):
        c.a(c.text(MX, y, 7, .35, s['kicker'], 12, ac, bold=True, tracking=3, font=c.f_num), 'fade', at=300); y += .5
    title = s['title']; lines = title if isinstance(title, list) else [title]
    size = s.get('title_size', 42)
    c.a(c.text(MX, y, 7.6, 2.2, lines, size, HERO_TX, bold=True, spacing=1.1, para_gap=0, font=c.f_title), 'rise', gap=120, dur=800)
    nl = sum(max(1, int(len(l) * size / 72 * 1.02 / 7.6) + 1) for l in lines)
    y += .3 + nl * size / 72 * 1.25
    if s.get('subtitle'):
        c.a(c.text(MX, y, 6.6, 1.2, s['subtitle'], 17, HERO_TX2, spacing=1.45), 'fade-up', gap=150)
    if s.get('stats'):
        n = len(s['stats']); sw = min(2.8, (W - 2 * MX) / n)
        for i, st in enumerate(s['stats']):
            x = MX + i * sw
            c.a(c.line(x, H - 2.05, x, H - 1.05, ac, 2), 'wipe-up', gap=150, dur=400)
            c.counter(x + .2, H - 2.1, sw - .3, .7, st['value'], 30, HERO_TX, gap=40)
            c.a(c.text(x + .22, H - 1.4, sw - .3, .35, st['label'], 11, HERO_TX2), 'fade', gap=40)
    credit(c, s.get('credit'), light=True, y=H - .45)

def L_split(c, s, deck):
    """图文分栏：右半出血大图（聚光灯揭开）+ 左侧要点"""
    t = c.t
    background(c)
    ix = W * .5
    pic = c.picture(img_path(deck, s['image']), ix, 0, W - ix, H)
    c.a(pic, s.get('image_anim', 'circle'), at=0, hold=True, dur=900)
    credit(c, s.get('credit'), light=True, x=ix + .3, w=W - ix - .6, y=H - .45)
    y0 = header(c, s, w=ix - MX - .5)
    y = y0 + .1
    for i, b in enumerate(s.get('bullets', [])):
        c.a(c.oval(MX + .08, y + .17, .1, fill=t.accent), 'zoom', gap=150, dur=300)
        c.a(c.text(MX + .35, y, ix - MX - .9, .9, b, 15, t.text_2, spacing=1.45), 'fade-left', gap=30)
        y += .5 + .26 * (len(b) // 26)
    if s.get('stats'):
        sw = (ix - MX - .5) / len(s['stats']); yy = max(y + .2, H - 2.2)
        for i, st in enumerate(s['stats']):
            x = MX + i * sw
            c.counter(x, yy, sw - .2, .7, st['value'], 32, t.accent if i == 0 else t.text_1, gap=150)
            c.a(c.text(x, yy + .72, sw - .2, .35, st['label'], 11, t.text_3), 'fade', gap=40)
    source(c, s.get('source'))


def L_gallery(c, s, deck):
    """场景图库：统一调色的照片 + 每个场景一个关键数字 + 标题 + 说明"""
    t = c.t
    background(c); y0 = header(c, s)
    items = s['items']; n = len(items); gap = .3
    w = (W - 2 * MX - gap * (n - 1)) / n; y = y0 + .15
    has_stat = any(it.get('stat') for it in items)
    ih = min(w * .62, H - y - (3.0 if has_stat else 2.3))
    c.clock += 150
    for i, it in enumerate(items):
        x = MX + i * (w + gap)
        pic = c.picture(img_path(deck, it['image']), x, y, w, ih, radius=t.radius)
        c.a(pic, 'flip', gap=160 if i else 0, dur=650)
        if it.get('tag'):
            tw = .14 * len(it['tag']) + .35
            c.a(c.rect(x + .15, y + .15, tw, .32, fill=HERO_BG, alpha=.6, radius=.16), 'fade', gap=150)
            c.a(c.text(x + .15, y + .15, tw, .32, it['tag'], 10.5, HERO_TX, bold=True, align='c', anchor='m'), 'fade', gap=0)
        yy = y + ih + .2
        if it.get('stat'):
            c.counter(x, yy, w * .55, .7, it['stat'], 30, t.accent if i == 0 else t.text_1, gap=60)
            c.a(c.text(x, yy + .66, w, .3, it.get('stat_label', ''), 11, t.text_3), 'fade', gap=30)
            yy += 1.05
            c.a(c.rect(x, yy, w, .012, fill=t.border), 'wipe-right', gap=30, dur=400); yy += .12
        c.a(c.text(x, yy, w, .4, it['title'], 17, t.text_1, bold=True), 'fade-up', gap=60)
        c.a(c.text(x, yy + .42, w, 1.0, it.get('text', ''), 13, t.text_2, spacing=1.45), 'fade-up', gap=40)
        c.clock -= 600
    c.clock += 600
    if s.get('credit'):
        credit(c, s['credit'], light=False, x=MX, w=W - 2 * MX, y=H - .8)
    source(c, s.get('source'))

# ================================================================== 结尾



def L_quote(c, s, deck):
    """金句页：整套里的「变调」页。有图 = 满版暗调照片；无图 = 深色底。字号大、居中偏左"""
    t = c.t
    skin = None if s.get('image') else _quote_skin(c, s, c.style.get('quote'))
    if skin: return _quote_body(c, s, *skin)
    c.s.background.fill.solid(); c.s.background.fill.fore_color.rgb = rgb(HERO_BG if not t.dark else t.bg)
    if s.get('image'):
        c.a(c.picture(img_path(deck, s['image']), 0, 0, W, H), 'fade', at=0, hold=True, dur=700)
        c.scrim(0, 0, W, H, HERO_BG, 'left', .9)
    elif not t.dark:
        c.glow(W - 6, -3.5, 9, t.accent, .25)
    ac = t.accent if t.dark else t.accent_2
    txt = s['text']; L = sum(len(x) for x in txt) if isinstance(txt, list) else len(txt)
    c.a(c.text(MX, 1.0, 2, 1.6, '“', 150, ac, bold=True, spacing=.8, font=c.f_quote), 'drop', at=0, dur=600)
    size = s.get('size', 48 if L <= 30 else 40)
    c.a(c.text(MX + .1, 2.55, W - 2 * MX - .6, 2.9, txt, size, HERO_TX, bold=True, spacing=1.25, em_color=ac, font=c.f_quote, para_gap=0),
        'type', gap=200)
    c.clock += 25 * L
    if s.get('by'):
        c.a(c.line(MX + .1, 5.85, MX + .9, 5.85, ac, 2), 'draw', gap=200, dur=400)
        c.a(c.text(MX + 1.1, 5.68, 10, .4, s['by'], 16, HERO_TX2), 'fade', gap=50)

def _quote_body(c, s, tx, em, mark, by_col, font):
    txt = s['text']; L = sum(len(x) for x in txt) if isinstance(txt, list) else len(txt)
    c.a(c.text(MX, 1.0, 2, 1.6, '“', 150, mark, bold=True, spacing=.8, font=font), 'drop', at=0, dur=600)
    size = s.get('size', 48 if L <= 30 else 40)
    c.a(c.text(MX + .1, 2.55, W - 2 * MX - .6, 2.9, txt, size, tx, bold=True, spacing=1.25, em_color=em, font=font, para_gap=0), 'type', gap=200)
    c.clock += 25 * L
    if s.get('by'):
        c.a(c.line(MX + .1, 5.85, MX + .9, 5.85, mark, 2), 'draw', gap=200, dur=400)
        c.a(c.text(MX + 1.1, 5.68, 10, .4, s['by'], 16, by_col), 'fade', gap=50)


def _donut_arcs(c, segs_vals, cols, cx, cy, d, dy=0):
    """按 12 点方向起、顺时针画：最后一段（要讲「涨」的那段）放在最前面，变化时它顺时针变长"""
    import shapecharts as sc
    tot = sum(segs_vals) or 1; a0 = 0; out = []
    for i in reversed(range(len(segs_vals))):
        sw = 360 * segs_vals[i] / tot
        out.append(sc.arc(c, cx, cy + dy, d, a0 + .6, max(sw - 1.2, .1), cols[i], thickness=.3))
        a0 += sw
    return out


def _num(sv):
    m = re.search(r'[\d,]*\.?\d+', str(sv))
    return (float(m.group().replace(',', '')), m) if m else (None, None)


GHOST = H + 1.0   # 「旧画面」元素平时放在页面外，放映一开始瞬移到位：静态视图里不和新内容叠在一起


def _ghost(c, shp):
    shp.top = shp.top + Inches(GHOST)
    c.a(shp, 'appear', at=0, hold=True, dur=1, params={'dy': GHOST / H})
    return shp


def _roll(c, x, y, w, h, old, new, size, color, start, dur, frames=24, ease=None, swap=False, **kw):
    """数字从旧值滚到新值（同 counter：中间帧放在页面外，放映时瞬移到位）。旧值一开始就在，滚动开始时切掉"""
    ease = ease or (lambda k: 1 - (1 - k) ** 3)
    a, _ = _num(old); b, mb = _num(new)
    if swap: a = None   # 标签类文字（年份等）直接淡出淡入，不滚动
    if old == new:   # 没变：直接放一个静态的
        c.text(x, y, w, h, new, size, color, **kw); return
    first = _ghost(c, c.text(x, y, w, h, old, size, color, **kw))
    if a is None or b is None or old == new:
        if old != new:
            c.a(first, 'out', at=start, hold=True, dur=200, grp=1)
            c.a(c.text(x, y, w, h, new, size, color, **kw), 'fade', at=start + 200, hold=True, dur=300)
        return
    dec = len(mb.group().split('.')[1]) if '.' in mb.group() else 0
    pre, suf = new[:mb.start()], new[mb.end():]
    c.a(first, 'cut', at=start, hold=True, dur=1, grp=1)
    for i in range(frames):
        v = a + (b - a) * ease(i / frames); off = H + 1.0 + i * .02
        tb = c.text(x, y + off, w, h, f'{pre}{v:.{dec}f}{suf}', size, color, **kw)
        c.a(tb, 'appear', at=start + int(dur * i / frames), hold=True, dur=1, params={'dy': off / H})
        c.a(tb, 'cut', at=start + int(dur * (i + 1) / frames), hold=True, dur=1, grp=1)
    c.a(c.text(x, y, w, h, new, size, color, **kw), 'appear', at=start + dur, hold=True, dur=1)


def L_donut_story(c, s, deck):
    """环形图讲变化（两页连用）：第一页画出现状；第二页写 "continue": true，
    开场和上一页最后一帧完全一样，然后「算力」段顺时针变长、数字同步滚到新值，最后出原因标注。
    不用 PowerPoint 平滑切换：它不会按角度补间环形，只会把轮廓硬拧过去（中间会扭曲、文字重影）"""
    t = c.t
    background(c)
    cont = s.get('continue', s.get('morph_in'))
    prev = deck['slides'][c.idx - 2] if cont and c.idx >= 2 else None
    segs = s['segments']; tot = sum(g['value'] for g in segs)
    cols = [mix(t.text_3, t.bg, .75), t.accent, t.accent_2, t.accent_3]
    d = 4.5; rx = MX + d + .9; colw = (W - MX - rx - .3) / len(segs)
    geom = lambda y0: (MX + d / 2 + .1, y0 + .25 + d / 2)
    center = s['center'] if isinstance(s['center'], list) else str(s['center']).split('\n')

    def legend(g, i):
        x = rx + i * (colw + .3); yy = y0 + .35
        return (x, yy, [c.rect(x, yy + .12, .2, .2, fill=cols[i], radius=.1),
                        c.text(x + .35, yy, colw - .35, .4, g['name'], 16, t.text_1, bold=True)])

    if not prev:
        y0 = header(c, s); cx, cy = geom(y0)
        start = c.clock + 100
        for arc_ in _donut_arcs(c, [g['value'] for g in segs], cols, cx, cy, d):
            c.a(arc_, 'wheel', at=start, hold=True, dur=1000)
        c.a(c.text(cx - 1.4, cy - .55, 2.8, .4, center[0], 18, t.text_2, bold=True, align='c'), 'pop', at=start + 500, hold=True, dur=600)
        c.a(c.text(cx - 1.4, cy - .1, 2.8, .6, center[-1], 26, t.text_1, bold=True, align='c', font=c.f_num), 'pop', at=start + 500, dur=600)
        for i, g in enumerate(segs):
            x, yy, parts = legend(g, i)
            parts += [c.text(x, yy + .5, colw, .7, g['label'], 30, t.text_1 if i == 0 else cols[i], bold=True, font=c.f_num),
                      c.text(x, yy + 1.2, colw, .4, f"占 {g['value'] / tot * 100:.0f}%", 14, t.text_3)]
            for z in parts: c.a(z, 'fade-up', gap=50, dur=500)
        if s.get('note'):
            c.a(c.text(rx, y0 + 2.1, W - MX - rx, 1.2, s['note'], 15, t.text_2, spacing=1.5), 'fade-up', gap=120)
        if s.get('teaser'):
            ty = y0 + 3.6
            c.a(c.rect(rx, ty, W - MX - rx, .012, fill=t.border), 'wipe-right', gap=200, dur=400)
            c.a(c.text(rx, ty + .3, W - MX - rx, .7, s['teaser'] + '  →', 26, t.accent, bold=True, font=c.f_title), 'fade-left', gap=80)
        source(c, s.get('source'))
        return

    # ---------- 接上一页：开场画面 = 上一页最后一帧，再变成新数据
    psegs = prev['segments']; ptot = sum(g['value'] for g in psegs)
    pcenter = prev['center'] if isinstance(prev['center'], list) else str(prev['center']).split('\n')
    n0 = len(c.anims); k0 = len(c.s.shapes._spTree)
    y0 = header(c, prev); del c.anims[n0:]; cx, cy = geom(y0)
    old_hdr = list(c.s.shapes._spTree)[k0:]
    n0 = len(c.anims); k0 = len(c.s.shapes._spTree)
    header(c, s); del c.anims[n0:]
    new_hdr = list(c.s.shapes._spTree)[k0:]
    # 标题：旧的淡出、新的淡入（用 c.a 需要 shape 对象，直接按 id 找）
    shp_by_el = {sh._element: sh for sh in c.s.shapes}
    for el in old_hdr: c.a(_ghost(c, shp_by_el[el]), 'out', at=0, hold=True, dur=250, grp=1)
    for el in new_hdr: c.a(shp_by_el[el], 'fade', at=150, hold=True, dur=400)
    # 上一页右侧的说明和悬念句：直接淡出，给原因卡片腾位置
    if prev.get('note'):
        c.a(_ghost(c, c.text(rx, y0 + 2.1, W - MX - rx, 1.2, prev['note'], 15, t.text_2, spacing=1.5)), 'out', at=0, hold=True, dur=300, grp=1)
    if prev.get('teaser'):
        ty = y0 + 3.6
        c.a(_ghost(c, c.rect(rx, ty, W - MX - rx, .012, fill=t.border)), 'out', at=0, hold=True, dur=300, grp=1)
        c.a(_ghost(c, c.text(rx, ty + .3, W - MX - rx, .7, prev['teaser'] + '  →', 26, t.accent, bold=True, font=c.f_title)), 'out', at=0, hold=True, dur=300, grp=1)
    # 环形逐帧变化（easeInOutCubic，1.1 秒，30 帧）
    T0, DUR, FR = 350, 1100, 30
    ease = lambda k: 4 * k ** 3 if k < .5 else 1 - (-2 * k + 2) ** 3 / 2
    pv = [g['value'] / ptot for g in psegs]; nv = [g['value'] / tot for g in segs]
    first = c.s.shapes.add_group_shape(_donut_arcs(c, pv, cols, cx, cy, d, dy=GHOST))
    c.a(first, 'appear', at=0, hold=True, dur=1, params={'dy': GHOST / H})
    c.a(first, 'cut', at=T0, hold=True, dur=1, grp=1)
    for i in range(FR):
        k = ease(i / FR); vals = [a + (b - a) * k for a, b in zip(pv, nv)]
        off = H + 1.0 + i * .02
        grp = c.s.shapes.add_group_shape(_donut_arcs(c, vals, cols, cx, cy, d, dy=off))
        c.a(grp, 'appear', at=T0 + int(DUR * i / FR), hold=True, dur=1, params={'dy': off / H})
        c.a(grp, 'cut', at=T0 + int(DUR * (i + 1) / FR), hold=True, dur=1, grp=1)
    c.a(c.s.shapes.add_group_shape(_donut_arcs(c, nv, cols, cx, cy, d)), 'appear', at=T0 + DUR, hold=True, dur=1)
    # 中心文字：年份标签换掉，总数滚动
    _roll(c, cx - 1.4, cy - .55, 2.8, .4, pcenter[0], center[0], 18, t.text_2, T0, 300, swap=True, bold=True, align='c')
    _roll(c, cx - 1.4, cy - .1, 2.8, .6, pcenter[-1], center[-1], 26, t.text_1, T0, DUR, ease=ease, bold=True, align='c', font=c.f_num)
    # 图例：数值和占比跟着环一起滚
    for i, g in enumerate(segs):
        x, yy, _ = legend(g, i)
        pg = psegs[i]
        _roll(c, x, yy + .5, colw, .7, pg['label'], g['label'], 30, t.text_1 if i == 0 else cols[i], T0, DUR, ease=ease, bold=True, font=c.f_num)
        _roll(c, x, yy + 1.2, colw, .4, f"占 {pg['value'] / ptot * 100:.0f}%", f"占 {g['value'] / tot * 100:.0f}%", 14, t.text_3, T0, DUR, ease=ease)
    c.clock = T0 + DUR + 150
    for k, an in enumerate(s.get('annotations', [])):
        x = rx + k * (colw + .3); yy = y0 + 2.1
        up = an.get('trend') == 'up'
        card = c.card(x, yy, colw, 2.55, hl=up)
        c.a(card, 'rise', gap=100 if k else 0, dur=600)
        c.a(c.text(x + .25, yy + .2, colw - .5, .4, ('▲ ' if up else '▼ ') + an['title'], 16, t.good if up else t.bad, bold=True), 'fade', gap=50)
        c.a(c.text(x + .25, yy + .7, colw - .5, 1.8, an['text'], 13, t.text_2, spacing=1.5), 'fade-up', gap=50)
    source(c, s.get('source'))


def L_end(c, s, deck):
    t = c.t
    skin = _quote_skin(c, s, c.style.get('quote'))
    if skin:
        tx, em, mark, by_col, font = skin
        c.a(c.text(0, 2.35, W, 1.4, s.get('title', '谢谢'), 66, tx, bold=True, align='c', font=c.f_title), 'pop', at=150, dur=800)
        c.confetti(W / 2, 3.0, start=450)
        c.a(c.rect(W / 2 - .55, 3.95, 1.1, .07, fill=mark), 'wipe-right', at=900, dur=500)
        if s.get('subtitle'): c.a(c.text(0, 4.25, W, .6, s['subtitle'], 18, by_col, align='c'), 'fade-up', gap=150)
        return
    background(c, 'end')
    c.a(c.text(0, 2.35, W, 1.4, s.get('title', '谢谢'), 64, t.text_1, bold=True, align='c'), 'pop', at=150, dur=800)
    c.confetti(W / 2, 3.0, start=450)
    c.a(c.gradbar(W / 2 - .55, 3.95, 1.1, .06, t.grad), 'draw', at=900, dur=500)
    if s.get('subtitle'):
        c.a(c.text(0, 4.25, W, .6, s['subtitle'], 18, t.text_2, align='c'), 'fade-up', gap=150)
    if s.get('credits'):
        c.text(MX + 1, H - 1.05, W - 2 * MX - 2, .7, s['credits'], 10, t.text_3, align='c', spacing=1.35)


LAYOUTS = {'cover': L_cover, 'agenda': L_agenda, 'section': L_section, 'kpi': L_kpi, 'stat': L_stat,
           'chart': L_chart, 'charts': L_charts, 'table': L_table, 'points': L_points, 'compare': L_compare,
           'timeline': L_timeline, 'process': L_process, 'arch': L_arch, 'hero': L_hero, 'split': L_split,
           'gallery': L_gallery, 'quote': L_quote, 'donut_story': L_donut_story, 'end': L_end}
NO_FOOTER = {'cover', 'section', 'quote', 'end', 'hero'}
