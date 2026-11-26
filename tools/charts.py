"""原生可编辑图表：自动选型 + 审美样式 + 入场动画（柱子逐根长出、折线从左画到右、环形转圈）。"""
import re, copy
from pptx.util import Inches, Pt
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import (XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_MARK,
                            XL_MARKER_STYLE, XL_TICK_LABEL_POSITION)
from pptx.oxml.ns import qn
from lxml import etree
from core import rgb, mix

TIME_RE = re.compile(r'^(\d{2,4}\s*(年|Q[1-4]|H[12])?|Q[1-4]|[一二三四]季度|\d{1,2}月|\d{4}[-./]\d{1,2}|H[12]|\d{4}\s*[HQ][1-4])$', re.I)


def pick_chart(ch):
    """占比 -> 环形；时间序列 -> 柱/折线；排名或长标签 -> 横向条形；其他 -> 柱状"""
    if ch.get('type', 'auto') != 'auto': return ch['type']
    cats = [str(x) for x in ch['categories']]; ser = ch['series']; n = len(cats)
    vals = ser[0]['values']
    if len(ser) == 1 and (ch.get('share') or (n <= 6 and abs(sum(vals) - 100) < 1.5)):
        return 'doughnut'
    if all(TIME_RE.match(x.strip()) for x in cats):
        if len(ser) >= 2: return 'line' if n > 5 else 'column'
        return 'line' if n > 7 else 'column'
    if len(ser) == 1 and (n > 6 or max(len(x) for x in cats) > 5 or ch.get('ranking')):
        return 'bar'
    return 'column'


def _fmt(vals):
    return '0' if all(v is None or float(v).is_integer() for v in vals) else '0.0'


def _no_bg(chart):
    cs = chart._chartSpace
    sp = cs.find(qn('c:spPr'))
    if sp is None:
        sp = etree.Element(qn('c:spPr')); cs.find(qn('c:chart')).addnext(sp)
    for ch in list(sp): sp.remove(ch)
    etree.SubElement(sp, qn('a:noFill')); ln = etree.SubElement(sp, qn('a:ln')); etree.SubElement(ln, qn('a:noFill'))
    pa = cs.find(qn('c:chart')).find(qn('c:plotArea'))
    sp2 = pa.find(qn('c:spPr'))
    if sp2 is None: sp2 = etree.SubElement(pa, qn('c:spPr'))
    for ch in list(sp2): sp2.remove(ch)
    etree.SubElement(sp2, qn('a:noFill'))


def add_chart(c, ch, x, y, w, h, gap=150, legend_side=True):
    t = c.t
    kind = pick_chart(ch)
    if not ch.get('native'):   # 默认用 Chart.js 风格的形状图表（动画更接近 html-ppt）
        import shapecharts as sc
        if kind in ('column', 'bar'):
            return sc.bars(c, dict(ch, type=kind), x, y, w, h, gap=gap)
        if kind in ('line', 'area'):
            return sc.lines(c, ch, x, y, w, h, gap=gap)
        if kind in ('doughnut', 'pie'):
            return _shape_donut(c, ch, x, y, w, h, gap, legend_side)
    cats = [str(v) for v in ch['categories']]
    series = copy.deepcopy(ch['series'])
    hl = ch.get('highlight')
    if kind == 'bar' and ch.get('sort', True):
        order = sorted(range(len(cats)), key=lambda i: -series[0]['values'][i])
        cats = [cats[i] for i in order]
        for se in series: se['values'] = [se['values'][i] for i in order]
        if isinstance(hl, int): hl = order.index(hl % len(order))
    if isinstance(hl, str): hl = cats.index(hl) if hl in cats else None
    if hl is None and len(series) == 1 and ch.get('auto_highlight', True):
        hl = 0 if kind == 'bar' else (len(cats) - 1 if kind in ('column', 'line', 'area') else None)
    if isinstance(hl, int): hl %= len(cats)

    data = CategoryChartData(); data.categories = cats
    allv = [v for se in series for v in se['values']]
    fmt = ch.get('format', _fmt(allv))
    split_hl = kind in ('column', 'bar') and len(series) == 1 and hl is not None
    if split_hl:  # 高亮 = 两组系列重叠，兼容性最好
        v = series[0]['values']
        data.add_series(series[0]['name'], [None if i == hl else z for i, z in enumerate(v)], number_format=fmt)
        data.add_series(series[0]['name'] + '（重点）', [z if i == hl else None for i, z in enumerate(v)], number_format=fmt)
    else:
        for se in series: data.add_series(se['name'], se['values'], number_format=fmt)
    xl = {'column': XL_CHART_TYPE.COLUMN_CLUSTERED, 'bar': XL_CHART_TYPE.BAR_CLUSTERED, 'line': XL_CHART_TYPE.LINE_MARKERS,
          'doughnut': XL_CHART_TYPE.DOUGHNUT, 'pie': XL_CHART_TYPE.PIE, 'area': XL_CHART_TYPE.AREA,
          'stacked': XL_CHART_TYPE.COLUMN_STACKED, 'radar': XL_CHART_TYPE.RADAR_MARKERS}[kind]
    cw = h if kind in ('doughnut', 'pie') else w
    gf = c.s.shapes.add_chart(xl, Inches(x), Inches(y), Inches(cw), Inches(h), data)
    chart = gf.chart
    _no_bg(chart)
    chart.font.size = Pt(12); chart.font.color.rgb = rgb(t.text_2); chart.font.name = c.font
    multi = len(series) > 1
    chart.has_legend = multi and kind not in ('doughnut', 'pie')
    if chart.has_legend:
        chart.legend.position = XL_LEGEND_POSITION.TOP; chart.legend.include_in_layout = False
        chart.legend.font.size = Pt(11); chart.legend.font.color.rgb = rgb(t.text_2)
    plot = chart.plots[0]

    if kind in ('doughnut', 'pie'):
        def col_of(i): return t.palette[i % len(t.palette)] if hl is None else (t.accent if i == hl else mix(t.text_3, t.bg, .6 - .1 * (i % 4)))
        pts = plot.series[0].points
        for i in range(len(cats)):
            pts[i].format.fill.solid(); pts[i].format.fill.fore_color.rgb = rgb(col_of(i))
            pts[i].format.line.color.rgb = rgb(t.bg); pts[i].format.line.width = Pt(2)
        plot.has_data_labels = False
        if kind == 'doughnut':
            dn = chart._chartSpace.find('.//' + qn('c:doughnutChart'))
            hs = dn.find(qn('c:holeSize'))
            if hs is None: hs = etree.SubElement(dn, qn('c:holeSize'))
            hs.set('val', str(ch.get('hole', 68)))
        c.a(gf, 'wheel', gap=gap, dur=1100)
        if legend_side:
            vals = series[0]['values']; tot = sum(vals) or 1
            lx = x + h + .45; rowh = min(.62, h / max(len(cats), 1)); ly = y + max(0, (h - rowh * len(cats)) / 2)
            for i, cat in enumerate(cats):
                dot = c.rect(lx, ly + i*rowh + .12, .15, .15, fill=col_of(i), radius=.075)
                lab = c.text(lx + .3, ly + i*rowh, max(1.2, w - h - 2.4), .4, cat, 14, t.text_1 if i == hl else t.text_2, bold=(i == hl))
                pct = c.text(x + w - 1.3, ly + i*rowh, 1.3, .4,
                             f'{vals[i]/tot*100:.0f}%' if not ch.get('raw') else f'{vals[i]}{ch.get("unit", "")}',
                             14, t.accent if i == hl else t.text_1, bold=True, align='r')
                for p_ in (dot, lab, pct): c.a(p_, 'fade-left', gap=30, dur=450)
        if ch.get('center'):
            c.a(c.text(x, y + h/2 - .5, h, 1.0, ch['center'], ch.get('center_size', 22), t.text_1, bold=True, align='c', anchor='m', spacing=1.05),
                'pop', gap=120, dur=700)
        return gf

    if kind == 'radar':
        for si, se in enumerate(plot.series):
            col = t.palette[si % len(t.palette)]
            se.format.line.color.rgb = rgb(col); se.format.line.width = Pt(2.5)
            se.marker.style = XL_MARKER_STYLE.CIRCLE; se.marker.size = 6
            se.marker.format.fill.solid(); se.marker.format.fill.fore_color.rgb = rgb(col)
        c.a(gf, 'zoom', gap=gap, dur=900)
        return gf

    ca = chart.category_axis
    ca.major_tick_mark = XL_TICK_MARK.NONE; ca.format.line.color.rgb = rgb(t.border)
    ca.tick_labels.font.size = Pt(12); ca.tick_labels.font.color.rgb = rgb(t.text_2)
    ca.has_major_gridlines = False
    va = chart.value_axis
    va.major_tick_mark = XL_TICK_MARK.NONE; va.format.line.fill.background()
    va.tick_labels.font.size = Pt(10); va.tick_labels.font.color.rgb = rgb(t.text_3)
    va.has_major_gridlines = kind in ('line', 'area')
    if va.has_major_gridlines:
        va.major_gridlines.format.line.color.rgb = rgb(t.border); va.major_gridlines.format.line.width = Pt(.5)
        if ch.get('y_min') is not None: va.minimum_scale = ch['y_min']
    if kind in ('column', 'bar', 'stacked'):
        va.visible = False; va.tick_label_position = XL_TICK_LABEL_POSITION.NONE
        plot.gap_width = ch.get('gap_width', 55 if not multi else 80)
        if multi: plot.overlap = -10 if kind != 'stacked' else 100
        if split_hl: plot.overlap = 100
        va.minimum_scale = 0
    if kind == 'bar': ca.reverse_order = True

    plot.has_data_labels = True
    dl = plot.data_labels
    dl.font.size = Pt(11 if multi else 12); dl.font.color.rgb = rgb(t.text_1); dl.font.bold = True
    dl.number_format = ch.get('label_format', fmt); dl.number_format_is_linked = False
    if kind in ('column', 'bar'): dl.position = XL_LABEL_POSITION.OUTSIDE_END
    elif kind == 'line': dl.position = XL_LABEL_POSITION.ABOVE
    elif kind == 'stacked': dl.position = XL_LABEL_POSITION.CENTER

    for si, se in enumerate(plot.series):
        col = t.palette[si % len(t.palette)]
        if kind == 'line':
            se.smooth = bool(ch.get('smooth'))
            se.format.line.color.rgb = rgb(col); se.format.line.width = Pt(3 if si == 0 else 2.25)
            se.marker.style = XL_MARKER_STYLE.CIRCLE; se.marker.size = 7
            se.marker.format.fill.solid(); se.marker.format.fill.fore_color.rgb = rgb(t.bg)
            se.marker.format.line.color.rgb = rgb(col); se.marker.format.line.width = Pt(2)
            if hl is not None and not multi:
                p = se.points[hl]
                p.marker.size = 12; p.marker.format.fill.solid(); p.marker.format.fill.fore_color.rgb = rgb(t.accent)
        else:
            se.format.fill.solid()
            if split_hl: col = t.muted if si == 0 else t.accent
            elif not multi: col = t.accent
            se.format.fill.fore_color.rgb = rgb(col)
            se.format.line.fill.background()
    if kind in ('column', 'bar', 'stacked') and ch.get('grow', True):
        # 逐根生长：坐标轴先出，再一根一根擦出来
        c.a(gf, 'wipe-up' if kind != 'bar' else 'wipe-right', gap=gap, dur=650,
            chart_steps=len(cats), step_gap=ch.get('step_gap', 230))
        c.clock += 230 * len(cats)
    else:
        c.a(gf, 'wipe-right', gap=gap, dur=1600 if kind == 'line' else 1100)
    return gf


def _shape_donut(c, ch, x, y, w, h, gap, legend_side):
    import shapecharts as sc
    t = c.t
    cats = [str(v) for v in ch['categories']]; vals = ch['series'][0]['values']; hl = ch.get('highlight')
    def col_of(i): return t.palette[i % len(t.palette)] if hl is None else (t.accent if i == hl else mix(t.text_3, t.bg, .62 - .12 * (i % 4)))
    d = min(h, w * .5); cx = x + d / 2; cy = y + h / 2
    c.clock += gap
    sc.donut(c, cx, cy, d, vals, [col_of(i) for i in range(len(vals))], thickness=ch.get('thickness', .3))
    if ch.get('center'):
        c.a(c.text(cx - d / 2, cy - .5, d, 1.0, ch['center'], ch.get('center_size', 22), t.text_1, bold=True, align='c', anchor='m', spacing=1.05),
            'pop', at=c.clock - 600, hold=True, dur=700)
    if legend_side:
        tot = sum(vals) or 1
        lx = x + d + .5; rowh = min(.62, h / max(len(cats), 1)); ly = y + max(0, (h - rowh * len(cats)) / 2)
        c.clock -= 700
        for i, cat in enumerate(cats):
            dot = c.rect(lx, ly + i * rowh + .12, .15, .15, fill=col_of(i), radius=.075)
            lab = c.text(lx + .3, ly + i * rowh, max(1.2, w - d - 2.4), .4, cat, 14, t.text_1 if i == hl else t.text_2, bold=(i == hl))
            pct = c.text(x + w - 1.3, ly + i * rowh, 1.3, .4,
                         f'{vals[i]/tot*100:.0f}%' if not ch.get('raw') else f'{vals[i]}{ch.get("unit", "")}',
                         14, t.accent if i == hl else t.text_1, bold=True, align='r')
            for p_ in (dot, lab, pct): c.a(p_, 'fade-left', gap=30, dur=450)
