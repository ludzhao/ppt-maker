"""Chart.js 风格的「形状图表」：用 PowerPoint 形状画，动画和 html-ppt 的 chart-bar / chart-line / chart-pie 一致。
- 柱子：顶部圆角，底边固定从 0 长到满高（easeOutQuart，约 1 秒，同时生长）
- 折线：平滑曲线（tension .4）+ 半透明面积，整条线和面积从 X 轴一起「升」上来，数据点同步升起
- 环形：每段按顺时针依次扫出（Chart.js animateRotate）
代价：数据不能在 Excel 里改；每根柱子、每个点都是普通形状，可以直接拖改。需要可编辑数据时用 "native": true。
"""
import math
from pptx.util import Inches, Pt, Emu
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree
from core import rgb, mix, set_alpha, W, H

NS_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
EMU = 914400


def nice_max(v, ticks=5):
    if v <= 0: return 1, 1
    raw = v / ticks
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        step = m * mag
        if step >= raw: break
    top = math.ceil(v / step) * step
    if top == v: top += step * 0
    return top, step


def _fmt(v, dec):
    return f'{v:.{dec}f}'


def _dec(vals):
    return 0 if all(float(v).is_integer() for v in vals if v is not None) else 1


def custom_shape(c, pts_cmds, fill=None, fill_grad=None, line=None, lw=2.0, name=None):
    """pts_cmds: [('M',x,y), ('L',x,y), ('C',x1,y1,x2,y2,x,y), ('Z',)] 坐标单位为英寸（页面绝对坐标）"""
    xs = [v for cmd in pts_cmds for v in cmd[1::2]]
    ys = [v for cmd in pts_cmds for v in cmd[2::2]]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    w = max(x1 - x0, .01); h = max(y1 - y0, .01)
    shp = c.s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x0), Inches(y0), Inches(w), Inches(h))
    shp.shadow.inherit = False
    spPr = shp._element.spPr
    spPr.remove(spPr.find(qn('a:prstGeom')))
    pw, ph = int(w * EMU), int(h * EMU)
    def P(x, y): return f'<a:pt x="{int((x - x0) * EMU)}" y="{int((y - y0) * EMU)}"/>'
    body = []
    for cmd in pts_cmds:
        if cmd[0] == 'M': body.append(f'<a:moveTo>{P(cmd[1], cmd[2])}</a:moveTo>')
        elif cmd[0] == 'L': body.append(f'<a:lnTo>{P(cmd[1], cmd[2])}</a:lnTo>')
        elif cmd[0] == 'C': body.append(f'<a:cubicBezTo>{P(cmd[1], cmd[2])}{P(cmd[3], cmd[4])}{P(cmd[5], cmd[6])}</a:cubicBezTo>')
        elif cmd[0] == 'Z': body.append('<a:close/>')
    geom = etree.fromstring(
        f'<a:custGeom xmlns:a="{NS_A}"><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/>'
        f'<a:pathLst><a:path w="{pw}" h="{ph}">{"".join(body)}</a:path></a:pathLst></a:custGeom>')
    spPr.find(qn('a:xfrm')).addnext(geom)
    if fill_grad:   # [(颜色, 透明度0-1), (颜色, 透明度)] 从上到下
        for old in spPr.findall(qn('a:solidFill')) + spPr.findall(qn('a:noFill')): spPr.remove(old)
        (c1, a1), (c2, a2) = fill_grad
        g = etree.fromstring(
            f'<a:gradFill xmlns:a="{NS_A}" rotWithShape="1"><a:gsLst>'
            f'<a:gs pos="0"><a:srgbClr val="{c1}"><a:alpha val="{int(a1*100000)}"/></a:srgbClr></a:gs>'
            f'<a:gs pos="100000"><a:srgbClr val="{c2}"><a:alpha val="{int(a2*100000)}"/></a:srgbClr></a:gs>'
            f'</a:gsLst><a:lin ang="5400000" scaled="0"/></a:gradFill>')
        geom.addnext(g)
    elif fill:
        shp.fill.solid(); shp.fill.fore_color.rgb = rgb(fill)
    else:
        shp.fill.background()
    if line:
        shp.line.color.rgb = rgb(line); shp.line.width = Pt(lw)
        ln = shp.line._get_or_add_ln(); ln.set('cap', 'rnd')
        etree.SubElement(ln, qn('a:round'))
    else:
        shp.line.fill.background()
    if shp.has_text_frame: shp.text_frame.text = ''
    if name: shp.name = name
    return shp


def _smooth(points, tension=.4):
    """Catmull-Rom -> 三次贝塞尔（Chart.js tension .4）"""
    cmds = [('M',) + points[0]]
    k = tension / 2 * 1.0
    for i in range(len(points) - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1, p2 = points[i], points[i + 1]
        p3 = points[i + 2] if i + 2 < len(points) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 1.0 * .5, p1[1] + (p2[1] - p0[1]) * k * .5)
        c2 = (p2[0] - (p3[0] - p1[0]) * k * .5, p2[1] - (p3[1] - p1[1]) * k * .5)
        cmds.append(('C',) + c1 + c2 + p2)
    return cmds


def axes(c, x, y, w, h, cats, vmax, step, dec, horizontal=False, show_y=True, grid_v=True, base=0):
    """坐标网格：横线 + 刻度（Chart.js 默认样式），返回绘图区"""
    t = c.t
    left = x + (.6 if show_y and not horizontal else (1.4 if horizontal else .15))
    bottom = y + h - .38
    top = y + .35
    right = x + w - .1
    n = int(round(vmax / step))
    for i in range(n + 1):
        if horizontal:
            gx = left + (right - left) * i / n
            ln = c.line(gx, top, gx, bottom, t.border, .6)
            c.a(ln, 'fade', gap=0, hold=True, dur=400)
            lab = c.text(gx - .5, bottom + .08, 1, .25, _fmt(step * i, dec if step < 1 else 0), 10, t.text_3, align='c')
            c.a(lab, 'fade', gap=0, hold=True, dur=400)
        else:
            gy = bottom - (bottom - top) * i / n
            ln = c.line(left, gy, right, gy, t.border, .6 if i else 1.0)
            c.a(ln, 'fade', gap=0, hold=True, dur=400)
            if show_y:
                lab = c.text(x, gy - .12, left - x - .12, .25, _fmt(base + step * i, dec if step < 1 else 0), 10, t.text_3, align='r')
                c.a(lab, 'fade', gap=0, hold=True, dur=400)
    return left, top, right, bottom


def legend(c, x, y, w, series_names, colors):
    if len(series_names) < 2: return
    total = sum(.3 + .16 * len(nm) + .3 for nm in series_names)
    cx = x + (w - total) / 2
    for nm, col in zip(series_names, colors):
        b = c.rect(cx, y + .07, .22, .13, fill=col, radius=.03)
        tb = c.text(cx + .3, y, .16 * len(nm) + .2, .3, nm, 10, c.t.text_2)
        for s_ in (b, tb): c.a(s_, 'fade', gap=0, hold=True, dur=400)
        cx += .3 + .16 * len(nm) + .3


def bars(c, ch, x, y, w, h, gap=100):
    t = c.t
    cats = [str(v) for v in ch['categories']]; series = ch['series']; n = len(cats); m = len(series)
    horizontal = ch.get('type') == 'bar'
    vals = [v for s_ in series for v in s_['values']]
    dec = _dec(vals); vmax, step = nice_max(max(vals) * 1.08)
    hl = ch.get('highlight')
    if hl is None and m == 1 and ch.get('auto_highlight', True): hl = n - 1 if not horizontal else 0
    if isinstance(hl, int): hl %= n
    cols = [t.accent, t.accent_2, t.accent_3, t.text_3]
    legend(c, x, y, w, [s_['name'] for s_ in series], cols)
    c.clock += gap
    t0 = c.clock
    left, top, right, bottom = axes(c, x, y + (.25 if m > 1 else 0), w, h - (.25 if m > 1 else 0), cats, vmax, step, dec,
                                    horizontal=horizontal, show_y=ch.get('y_axis', True))
    r = .055 if c.t.radius_px >= 6 else 0.0
    if not horizontal:
        slot = (right - left) / n
        bw_total = min(slot * .62, .5 * m + .12 * (m - 1)) if m > 1 else min(slot * .58, .62)
        bw = (bw_total - .08 * (m - 1)) / m
        for i, cat in enumerate(cats):
            cx = left + slot * (i + .5)
            lab = c.text(cx - slot / 2, bottom + .08, slot, .28, cat, 11, t.text_1 if i == hl else t.text_2, align='c', bold=(i == hl))
            c.a(lab, 'fade', at=t0, hold=True, dur=400)
            for k, se in enumerate(series):
                v = se['values'][i]
                if v is None: continue
                bh = (bottom - top) * v / vmax
                bx = cx - bw_total / 2 + k * (bw + .08)
                col = cols[k] if m > 1 else (t.accent if (hl is None or i == hl) else t.muted)
                bar = c.rect(bx, bottom - bh, bw, max(bh, .01), fill=col, shape=MSO_SHAPE.ROUND_2_SAME_RECTANGLE)
                bar.adjustments[0] = min(.5, r / max(bw, .01)) if r else 0; bar.adjustments[1] = 0
                c.a(bar, 'grow-up', at=t0 + 60 + i * 45 + k * 20, hold=True, dur=1100)
                vl = c.text(bx - .3, bottom - bh - .3, bw + .6, .26, _fmt(v, dec) + ch.get('suffix', ''),
                            11 if m > 1 else 12, t.accent if (m == 1 and i == hl) else t.text_1, bold=True, align='c', font=c.f_num)
                c.a(vl, 'rise-from', at=t0 + 60 + i * 45 + k * 20, hold=True, dur=1100, params={'dy': bh / H})
    else:
        order = sorted(range(n), key=lambda i: -series[0]['values'][i]) if ch.get('sort', True) else list(range(n))
        slot = (bottom - top) / n
        bh = min(slot * .58, .42)
        for rank, i in enumerate(order):
            cy = top + slot * (rank + .5)
            lab = c.text(x, cy - .15, left - x - .15, .3, cats[i], 11, t.text_1 if i == hl else t.text_2, align='r', bold=(i == hl))
            c.a(lab, 'fade', at=t0, hold=True, dur=400)
            v = series[0]['values'][i]; bw = (right - left) * v / vmax
            col = t.accent if (hl is None or i == hl) else t.muted
            bar = c.rect(left, cy - bh / 2, max(bw, .01), bh, fill=col, shape=MSO_SHAPE.ROUND_2_SAME_RECTANGLE)
            bar.rotation = 0
            _round_right(bar, r / bh)
            c.a(bar, 'grow-right', at=t0 + 60 + rank * 45, hold=True, dur=1100)
            vl = c.text(left + bw + .08, cy - .14, 1.2, .28, _fmt(v, dec) + ch.get('suffix', ''), 11, t.text_1, bold=True, font=c.f_num)
            c.a(vl, 'rise-from', at=t0 + 60 + rank * 45, hold=True, dur=1100, params={'dx': -bw / W, 'dy': 0})
    c.clock = t0 + 60 + n * 45 + 1100


def _round_right(shape, frac):
    """横向条形只圆右侧两个角：用 round2Same 旋转 90°太麻烦，这里改成 roundRect 的小圆角"""
    geom = shape._element.spPr.find(qn('a:prstGeom'))
    geom.set('prst', 'roundRect')
    av = geom.find(qn('a:avLst'))
    for g in list(av): av.remove(g)
    gd = etree.SubElement(av, qn('a:gd')); gd.set('name', 'adj'); gd.set('fmla', f'val {int(min(.5, frac) * 100000)}')


def lines(c, ch, x, y, w, h, gap=100):
    t = c.t
    cats = [str(v) for v in ch['categories']]; series = ch['series']; n = len(cats); m = len(series)
    vals = [v for s_ in series for v in s_['values']]
    dec = _dec(vals)
    vmin = ch.get('y_min', 0)
    vmax, step = nice_max((max(vals) - vmin) * 1.12)
    vmax += vmin
    cols = [t.accent, t.accent_2, t.accent_3]
    legend(c, x, y, w, [s_['name'] for s_ in series], cols)
    c.clock += gap; t0 = c.clock
    left, top, right, bottom = axes(c, x, y + (.25 if m > 1 else 0), w, h - (.25 if m > 1 else 0), cats, vmax - vmin, step, dec,
                                    show_y=ch.get('y_axis', True), base=vmin)
    slot = (right - left) / max(n - 1, 1)
    pad = slot * .0
    xs = [left + .25 + (right - left - .5) * i / max(n - 1, 1) for i in range(n)]
    for i, cat in enumerate(cats):
        lab = c.text(xs[i] - .6, bottom + .08, 1.2, .28, cat, 11, t.text_2, align='c')
        c.a(lab, 'fade', at=t0, hold=True, dur=400)
    hl = ch.get('highlight', n - 1 if m == 1 else None)
    for k, se in enumerate(series):
        col = cols[k % len(cols)]
        pts = [(xs[i], bottom - (bottom - top) * (v - vmin) / (vmax - vmin)) for i, v in enumerate(se['values'])]
        curve = _smooth(pts, ch.get('tension', .4))
        # 面积：曲线 + 回到基线
        area_cmds = curve + [('L', pts[-1][0], bottom), ('L', pts[0][0], bottom), ('Z',)]
        area = custom_shape(c, area_cmds, fill_grad=[(col, .38 if m == 1 else .22), (col, .02)])
        c.a(area, 'grow-up', at=t0 + 80 + k * 60, hold=True, dur=1200)
        # 线：路径里加一个基线上的起点，让形状底边=基线，这样「长高」时整条线从 X 轴升起
        line_cmds = [('M', pts[0][0], bottom)] + curve
        ln = custom_shape(c, line_cmds, line=col, lw=ch.get('line_width', 2.75))
        c.a(ln, 'grow-up', at=t0 + 80 + k * 60, hold=True, dur=1200)
        for i, (px, py) in enumerate(pts):
            big = (m == 1 and i == hl)
            d = .17 if big else .11
            dot = c.oval(px, py, d, fill=col if big else t.bg, line=col, lw=1.75)
            c.a(dot, 'rise-from', at=t0 + 80 + k * 60, hold=True, dur=1200, params={'dy': (bottom - py) / H})
            if ch.get('labels', True) and (n <= 8 or i == n - 1) and (m == 1 or i == n - 1):
                vl = c.text(px - .6, py - .38, 1.2, .26, _fmt(se['values'][i], dec) + ch.get('suffix', ''), 11 if not big else 13,
                            t.accent if big else t.text_1, bold=True, align='c', font=c.f_num)
                c.a(vl, 'rise-from', at=t0 + 80 + k * 60, hold=True, dur=1200, params={'dy': (bottom - py) / H})
    c.clock = t0 + 80 + m * 60 + 1200


# ------------------------------------------------------------------ 环形（形状版，可做 morph 变形）
def arc(c, cx, cy, d, start_deg, sweep_deg, color, thickness=.24, name=None, alpha=None):
    """blockArc：从 start_deg（12 点方向为 0，顺时针）扫过 sweep_deg"""
    shp = c.s.shapes.add_shape(MSO_SHAPE.BLOCK_ARC, Inches(cx - d / 2), Inches(cy - d / 2), Inches(d), Inches(d))
    shp.shadow.inherit = False
    st = (start_deg - 90) % 360; en = (start_deg + sweep_deg - 90) % 360
    if sweep_deg >= 359.9: en = (st - .01) % 360
    geom = shp._element.spPr.find(qn('a:prstGeom'))
    av = geom.find(qn('a:avLst'))
    for g in list(av): av.remove(g)
    for nm, val in (('adj1', int(st * 60000)), ('adj2', int(en * 60000)), ('adj3', int(thickness * 50000))):
        gd = etree.SubElement(av, qn('a:gd')); gd.set('name', nm); gd.set('fmla', f'val {val}')
    shp.fill.solid(); shp.fill.fore_color.rgb = rgb(color)
    if alpha is not None: set_alpha(shp.fill._xPr.find(qn('a:solidFill'))[0], alpha)
    shp.line.fill.background()
    if shp.has_text_frame: shp.text_frame.text = ''
    if name: shp.name = name
    return shp


def donut(c, cx, cy, d, values, colors, names=None, thickness=.26, start=None, gap_deg=1.2, animate=True):
    """Chart.js doughnut：各段顺时针依次扫出"""
    tot = sum(values) or 1
    a0 = 0; shapes = []
    t0 = c.clock if start is None else start
    acc = 0
    for i, v in enumerate(values):
        sw = 360 * v / tot
        s_ = arc(c, cx, cy, d, a0 + gap_deg / 2, max(sw - gap_deg, .5), colors[i], thickness,
                 name=(names[i] if names else None))
        if animate:  # 所有段同时开始「轮子」扫出：扫到哪一段，哪一段就出现 = Chart.js 的顺时针生长
            c.a(s_, 'wheel', at=t0, hold=True, dur=1000)
        acc += v / tot
        a0 += sw; shapes.append(s_)
    c.clock = t0 + 1000
    return shapes
