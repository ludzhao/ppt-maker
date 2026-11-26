"""基础：主题、画布（形状/文字/图片）、动效组件（数字滚动、信号波纹、网络连线、彩纸、光晕）。"""
import re, math, random, pathlib, tempfile
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn
from lxml import etree

W, H = 13.333, 7.5
MX = 0.8
CACHE = pathlib.Path(tempfile.gettempdir()) / 'ppt_skill_cache'


def rgb(h): return RGBColor.from_string(h)

def mix(a, b, t):
    pa = [int(a[i:i+2], 16) for i in (0, 2, 4)]; pb = [int(b[i:i+2], 16) for i in (0, 2, 4)]
    return '%02X%02X%02X' % tuple(round(x*t + y*(1-t)) for x, y in zip(pa, pb))

def dist(a, b):
    return sum(abs(int(a[i:i+2], 16) - int(b[i:i+2], 16)) for i in (0, 2, 4))


class Theme:
    def __init__(self, d):
        self.__dict__.update(d)
        self.text_1 = d.get('text_1', '111111'); self.text_2 = d.get('text_2', '444444'); self.text_3 = d.get('text_3', '888888')
        self.surface = d.get('surface', self.bg); self.surface_2 = d.get('surface_2', self.surface)
        self.border = d.get('border', mix(self.text_1, self.bg, .12))
        self.accent_2 = d.get('accent_2', self.accent); self.accent_3 = d.get('accent_3', self.accent_2)
        self.good = d.get('good', '16A34A'); self.bad = d.get('bad', 'DC2626')
        g = d.get('grad') or [self.accent, self.accent_2]
        self.grad = g if len(g) > 1 else g + [self.accent_2]
        if self.surface == self.bg:
            self.surface = mix(self.text_1, self.bg, .04 if not self.dark else .06)
        self.muted = mix(self.text_3, self.bg, .38 if self.dark else .45)   # 非重点数据：中性灰
        self.radius = min(self.radius_px, 24) / 144
        self.em = self.accent_2 if dist(self.accent, self.text_1) < 60 else self.accent
        self.palette = [self.accent, self.accent_2, self.accent_3, self.text_3, mix(self.accent, self.bg, .5), self.good]
        self.accent_ink = d.get('accent_ink', 'FFFFFF' if not self.dark else '0B1024')
        self.border_strong = d.get('border_strong', self.text_1)


# ------------------------------------------------------------------ 文字工具
def segments(s):
    parts = re.split(r'(\*\*[^*]+\*\*)', s)
    return [(p[2:-2], True) if p.startswith('**') else (p, False) for p in parts if p]

def set_font(run, name):
    """name 可以是 "西文字体|中文字体"：数字和英文用前者，中文用后者"""
    latin, ea = (name.split('|') + [None])[:2] if '|' in name else (name, name)
    ea = ea or latin
    run.font.name = latin
    rPr = run._r.get_or_add_rPr()
    for tag, face in (('a:ea', ea), ('a:cs', ea)):
        el = rPr.find(qn(tag))
        if el is None: el = etree.SubElement(rPr, qn(tag))
        el.set('typeface', face)

def set_alpha(clr_el, a):
    for old in clr_el.findall(qn('a:alpha')): clr_el.remove(old)
    etree.SubElement(clr_el, qn('a:alpha')).set('val', str(int(a * 100000)))


# ------------------------------------------------------------------ 生成的 PNG 素材（光晕、遮罩）
def glow_png(color, alpha):
    from PIL import Image
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f'glow_{color}_{int(alpha*100)}.png'
    if f.exists(): return f
    n = 256; r, g, b = (int(color[i:i+2], 16) for i in (0, 2, 4))
    im = Image.new('RGBA', (n, n)); px = im.load()
    for yy in range(n):
        for xx in range(n):
            d = (((xx - n/2 + .5)**2 + (yy - n/2 + .5)**2) ** .5) / (n/2)
            px[xx, yy] = (r, g, b, int(max(0.0, 1 - d) ** 1.8 * alpha * 255))
    im.save(f); return f

def toned(path, tone):
    """照片统一调色：natural 不处理；mute 降饱和；warm 暗调暖色；blue 蓝色双色调；sepia 纸色复古"""
    if not tone or tone == 'natural': return path
    from PIL import Image, ImageEnhance, ImageOps
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f'tone_{tone}_{pathlib.Path(path).stem}.jpg'
    if f.exists(): return f
    im = Image.open(path).convert('RGB')
    g = ImageOps.grayscale(im)
    if tone == 'blue':
        out = ImageOps.colorize(g, black='#050B26', mid='#2A4FB8', white='#D8F6FF')
        out = Image.blend(out, im, .18)
    elif tone == 'warm':
        out = ImageOps.colorize(g, black='#0A0706', mid='#7A3E1C', white='#FFE2C2')
        out = Image.blend(out, im, .25); out = ImageEnhance.Brightness(out).enhance(.85)
    elif tone == 'sepia':
        out = ImageOps.colorize(g, black='#2A2119', mid='#8C7458', white='#F6EEE2')
        out = Image.blend(out, im, .3)
    elif tone == 'mute':   # 咨询报告：降饱和、压高光，所有照片看起来像同一组
        out = ImageEnhance.Color(im).enhance(.35)
        out = ImageEnhance.Contrast(out).enhance(1.08); out = ImageEnhance.Brightness(out).enhance(.9)
    else:
        out = im
    out.save(f, quality=90); return f


def grain_png(color, alpha=.06):
    """纸张颗粒（经济学人风格背景）"""
    from PIL import Image
    import random as _r
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f'grain_{color}_{int(alpha*100)}.png'
    if f.exists(): return f
    r_, g_, b_ = (int(color[i:i+2], 16) for i in (0, 2, 4))
    w, h = 800, 450; im = Image.new('RGBA', (w, h)); px = im.load(); rnd = _r.Random(5)
    for y in range(h):
        for x in range(w):
            px[x, y] = (r_, g_, b_, int(rnd.random() * alpha * 255))
    im.save(f); return f


def pattern_png(kind, color, alpha):
    """背景纹理：dots 点阵（新粗野）/ scan 扫描线（终端）/ grid 网格（瑞士）"""
    from PIL import Image, ImageDraw
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f'pat_{kind}_{color}_{int(alpha*100)}.png'
    if f.exists(): return f
    w, h = 1333, 750; r, g, b = (int(color[i:i+2], 16) for i in (0, 2, 4)); a = int(alpha * 255)
    im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im)
    if kind == 'dots':
        for y in range(12, h, 25):
            for x in range(12, w, 25): d.ellipse((x - 1.6, y - 1.6, x + 1.6, y + 1.6), fill=(r, g, b, a))
    elif kind == 'scan':
        for y in range(0, h, 4): d.line((0, y, w, y), fill=(r, g, b, a))
    elif kind == 'grid':
        for x in range(0, w, 111): d.line((x, 0, x, h), fill=(r, g, b, a))
        for y in range(0, h, 125): d.line((0, y, w, y), fill=(r, g, b, a))
    im.save(f); return f


def vertical(shape):
    """文字竖排（中文从上到下、从右到左）"""
    shape.text_frame._txBody.find(qn('a:bodyPr')).set('vert', 'eaVert')
    return shape


def scrim_png(color, mode='left', strength=.92):
    """照片上的渐变遮罩：left = 左深右透；bottom = 下深上透"""
    from PIL import Image
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f'scrim2_{color}_{mode}_{int(strength*100)}.png'
    if f.exists(): return f
    w, h = 640, 360; r, g, b = (int(color[i:i+2], 16) for i in (0, 2, 4))
    im = Image.new('RGBA', (w, h)); px = im.load()
    for y in range(h):
        for x in range(w):
            if mode == 'left': k = min(1.0, max(0.0, 1.15 - x / (w * .85)))
            else: k = max(0.0, (y / h - .25) / .75)
            k2 = max(0.0, (y / h - .55) / .45) * .6   # 底部再压一点，方便放页脚
            px[x, y] = (r, g, b, int(min(1, k ** 1.25 + k2) * strength * 255))
    im.save(f); return f


# ------------------------------------------------------------------ 画布
class Canvas:
    def __init__(self, slide, theme, font, style=None):
        self.s, self.t = slide, theme
        self.style = style or {'card': 'dark', 'bg': 'glow', 'frame': 'legacy', 'eyebrow': 'caps', 'photo': 'natural', 'cover': 'dark', 'fonts': {}}
        fs = self.style.get('fonts', {})
        self.font = font or fs.get('body', 'Microsoft YaHei')
        self.f_title = fs.get('title', self.font)
        self.f_num = fs.get('num', self.f_title)
        self.f_display = fs.get('display', self.f_title)
        self.f_quote = fs.get('quote', self.f_title)
        self.anims = []
        self.clock = 0
        self.rand = random.Random(7)
        self.source_text = None

    def card(self, x, y, w, h, hl=False):
        """按风格画「一组内容的底板」：soft 浅底无边 / hairline 顶部细线 / dark 暗卡描边 / glass 玻璃"""
        t = self.t; mode = self.style.get('card', 'dark')
        if mode == 'hairline':
            r = self.rect(x, y, w, .02 if not hl else .04, fill=t.accent if hl else t.border_strong)
            return r
        if mode == 'soft':
            r = self.rect(x, y, w, h, fill=t.surface, radius=t.radius, line=t.accent if hl else None, lw=1.5)
            return r
        if mode == 'swiss':   # 粗黑顶线，重点项用红
            return self.rect(x, y, w, .06 if hl else .045, fill=t.accent if hl else t.border_strong)
        if mode == 'tile':    # 大圆角白格子
            return self.rect(x, y, w, h, fill=t.surface, radius=t.radius, line=t.accent if hl else None, lw=2)
        if mode == 'brutal':  # 黑粗边 + 右下硬阴影
            sh = self.rect(x + .09, y + .09, w, h, fill=t.border_strong)
            box = self.rect(x, y, w, h, fill=t.surface_2 if hl else t.surface, line=t.border_strong, lw=2.25)
            return self.s.shapes.add_group_shape([sh, box])
        if mode == 'ink':     # 宣纸上一条墨线 + 朱红小方块
            parts = [self.rect(x, y, w, .015, fill=t.border_strong)]
            parts.append(self.rect(x, y - .05, .12, .12, fill=t.accent if hl else t.border_strong))
            return self.s.shapes.add_group_shape(parts)
        if mode == 'term':    # 终端窗口：暗底 + 荧光描边
            return self.rect(x, y, w, h, fill=t.surface, line=t.accent, line_alpha=.9 if hl else .35, lw=1.5 if hl else 1, radius=t.radius)
        if mode == 'glass':
            r = self.rect(x, y, w, h, fill=t.accent if hl else 'FFFFFF', alpha=.14 if hl else .06, radius=t.radius,
                          line=t.accent if hl else 'FFFFFF', line_alpha=.9 if hl else .16, lw=1)
            return r
        return self.rect(x, y, w, h, fill=t.surface, line=t.accent if hl else t.border, radius=t.radius, lw=1.5 if hl else .75)

    # ---- 动画登记
    def a(self, shape, effect='fade-up', gap=120, dur=600, step=0, at=None, hold=False, **kw):
        """gap: 距上一个动画的间隔；at: 绝对时间；hold=True 不推进时钟（并行动画）"""
        if effect in (None, 'none') or shape is None: return shape
        start = at if at is not None else self.clock + gap
        if not hold: self.clock = start
        el = shape._element
        kind = 'graphic' if el.tag == qn('p:graphicFrame') else ('sp' if el.tag == qn('p:sp') else 'other')
        item = {'spid': shape.shape_id, 'effect': effect, 'delay': start, 'dur': dur, 'step': step, 'kind': kind}
        item.update(kw)
        self.anims.append(item)
        return shape

    # ---- 形状
    def rect(self, x, y, w, h, fill=None, line=None, radius=None, alpha=None, lw=0.75, shape=None, line_alpha=None, name=None):
        shp = MSO_SHAPE.ROUNDED_RECTANGLE if radius else (shape or MSO_SHAPE.RECTANGLE)
        r = self.s.shapes.add_shape(shp, Inches(x), Inches(y), Inches(w), Inches(h))
        if radius and shp == MSO_SHAPE.ROUNDED_RECTANGLE: r.adjustments[0] = min(.5, radius / max(min(w, h), .01))
        r.shadow.inherit = False
        if fill:
            r.fill.solid(); r.fill.fore_color.rgb = rgb(fill)
            if alpha is not None: set_alpha(r.fill._xPr.find(qn('a:solidFill'))[0], alpha)
        else: r.fill.background()
        if line:
            r.line.color.rgb = rgb(line); r.line.width = Pt(lw)
            if line_alpha is not None:
                set_alpha(r.line._get_or_add_ln().find(qn('a:solidFill'))[0], line_alpha)
        else: r.line.fill.background()
        if r.has_text_frame: r.text_frame.text = ''
        if name: r.name = name
        return r

    def oval(self, cx, cy, d, **kw):
        return self.rect(cx - d/2, cy - d/2, d, d, shape=MSO_SHAPE.OVAL, **kw)

    def line(self, x1, y1, x2, y2, color, width=1.25, alpha=None, arrow=False, dash=None):
        ln = self.s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
        ln.line.color.rgb = rgb(color); ln.line.width = Pt(width)
        lnx = ln.line._get_or_add_ln()
        if alpha is not None: set_alpha(lnx.find(qn('a:solidFill'))[0], alpha)
        if dash: etree.SubElement(lnx, qn('a:prstDash')).set('val', dash)
        if arrow:
            tail = etree.SubElement(lnx, qn('a:tailEnd')); tail.set('type', 'triangle'); tail.set('w', 'med'); tail.set('len', 'med')
        return ln

    def glow(self, x, y, d, color, alpha=.35, name=None):
        p = self.s.shapes.add_picture(str(glow_png(color, alpha)), Inches(x), Inches(y), Inches(d), Inches(d))
        if name: p.name = name
        return p

    def gradbar(self, x, y, w, h, colors, angle=0, radius=None):
        r = self.rect(x, y, w, h, fill=colors[0], radius=radius)
        r.fill.gradient(); r.fill.gradient_angle = angle
        st = r.fill.gradient_stops
        st[0].color.rgb = rgb(colors[0]); st[0].position = 0
        st[1].color.rgb = rgb(colors[-1]); st[1].position = 1.0
        return r

    def text(self, x, y, w, h, content, size=16, color=None, bold=False, align='l', anchor='t',
             spacing=1.25, tracking=None, em_color=None, font=None, name=None, para_gap=.45, em_style='bold'):
        tb = self.s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame; tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[anchor]
        paras = content if isinstance(content, list) else [content]
        for i, ptxt in enumerate(paras):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[align]
            p.line_spacing = spacing
            if i: p.space_before = Pt(size * para_gap)
            for seg, em in segments(str(ptxt)):
                r = p.add_run(); r.text = seg
                f = r.font; f.size = Pt(size); f.bold = bold or (em and em_style == 'bold')
                if em and em_style == 'italic': f.italic = True
                f.color.rgb = rgb((em_color or self.t.em) if em else (color or self.t.text_1))
                set_font(r, font or self.font)
                if tracking: r._r.get_or_add_rPr().set('spc', str(int(tracking * 100)))
        if name: tb.name = name
        return tb

    def picture(self, path, x, y, w, h, radius=None, tone=None):
        """按框裁切填满（object-fit: cover）；tone 默认跟风格走"""
        path = toned(path, tone if tone is not None else self.style.get('photo'))
        pic = self.s.shapes.add_picture(str(path), Inches(x), Inches(y))
        ratio = pic.height / pic.width; want = h / w
        if ratio > want:
            cut = (1 - want / ratio) / 2; pic.crop_top = cut; pic.crop_bottom = cut
        else:
            cut = (1 - ratio / want) / 2; pic.crop_left = cut; pic.crop_right = cut
        pic.left, pic.top, pic.width, pic.height = Inches(x), Inches(y), Inches(w), Inches(h)
        if radius:
            geom = pic._element.spPr.find(qn('a:prstGeom')); geom.set('prst', 'roundRect')
            av = geom.find(qn('a:avLst'))
            if av is None: av = etree.SubElement(geom, qn('a:avLst'))
            gd = etree.SubElement(av, qn('a:gd')); gd.set('name', 'adj'); gd.set('fmla', f'val {int(min(50000, radius / min(w, h) * 100000))}')
        return pic

    def scrim(self, x, y, w, h, color, mode='left', strength=.92):
        return self.s.shapes.add_picture(str(scrim_png(color, mode, strength)), Inches(x), Inches(y), Inches(w), Inches(h))

    # ------------------------------------------------------------ 动效组件
    def counter(self, x, y, w, h, value, size, color, gap=150, dur=1000, frames=30, align='l', bold=True, step=0):
        """原生「数字滚动」：叠放若干帧数字，按时间依次闪现，最后停在真实数值（真实数值那一帧可编辑）"""
        m = re.match(r'^(\D*?)([\d,]*\.?\d+)(.*)$', str(value))
        if not m:
            tb = self.text(x, y, w, h, value, size, color, bold=bold, align=align, spacing=1, font=self.f_num)
            return self.a(tb, 'pop', gap=gap, step=step)
        pre, num, suf = m.groups()
        dec = len(num.split('.')[1]) if '.' in num else 0
        target = float(num.replace(',', ''))
        comma = ',' in num
        start = self.clock + gap
        times = [int(dur * (i / frames)) for i in range(frames + 1)]
        for i in range(frames):
            k = i / frames
            v = target * (1 - (1 - k) ** 4)   # easeOutQuart，和 html-ppt counter 一样先快后慢
            s = f'{v:,.{dec}f}' if comma else f'{v:.{dec}f}'
            off = H + 1.0 + i * 0.02   # 中间帧放在页面下方的灰色区域，放映时才瞬移到位
            tb = self.text(x, y + off, w, h, pre + s + suf, size, color, bold=bold, align=align, spacing=1, name=f'counter-frame-{i}', font=self.f_num)
            self.a(tb, 'appear', at=start + times[i], hold=True, dur=1, step=step, params={'dy': off / H})
            self.a(tb, 'cut', at=start + times[i + 1], hold=True, dur=1, grp=1, step=step)
        final = self.text(x, y, w, h, value, size, color, bold=bold, align=align, spacing=1, name='counter-value', font=self.f_num)
        self.a(final, 'appear', at=start + dur, dur=1, step=step)
        self.clock = start + dur
        return final

    def rings(self, cx, cy, d, color, n=3, period=2700, width=1.5, start=0):
        """信号波纹（shockwave）：同心圆循环放大淡出"""
        out = []
        for i in range(n):
            r = self.oval(cx, cy, d, line=color, lw=width)
            self.a(r, 'ring', at=start + i * period // n, hold=True, dur=period, repeat='indefinite',
                   params={'from': .18, 'to': 1.0, 'peak': .85})
            out.append(r)
        return out

    def network(self, x, y, w, h, n=16, color=None, start=0, link=2, alpha=.35, node=.07, seed=3):
        """网络连线背景（constellation / knowledge-graph 的原生版）：线条依次画出，节点闪烁"""
        color = color or self.t.accent
        rnd = random.Random(seed)
        pts = []
        for _ in range(3000):
            if len(pts) >= n: break
            p = (x + rnd.random() * w, y + rnd.random() * h)
            if all((p[0]-q[0])**2 + (p[1]-q[1])**2 > (min(w, h) / 5) ** 2 for q in pts): pts.append(p)
        edges = set()
        for i, p in enumerate(pts):
            near = sorted(range(len(pts)), key=lambda j: (p[0]-pts[j][0])**2 + (p[1]-pts[j][1])**2)[1:link+1]
            for j in near: edges.add(tuple(sorted((i, j))))
        t0 = start
        for k, (i, j) in enumerate(sorted(edges)):
            (x1, y1), (x2, y2) = pts[i], pts[j]
            ln = self.line(x1, y1, x2, y2, color, width=.75, alpha=alpha)
            self.a(ln, 'fade', at=t0 + k * 45, hold=True, dur=700)
        for i, (px_, py_) in enumerate(pts):
            big = rnd.random() < .25
            d = node * (1.8 if big else 1)
            o = self.oval(px_, py_, d, fill=color, alpha=.9 if big else .6)
            self.a(o, 'pop', at=t0 + 150 + i * 50, hold=True, dur=500)
            if big:
                self.a(o, 'twinkle', at=t0 + 1500 + rnd.randint(0, 1500), hold=True, dur=1800, repeat='indefinite',
                       params={'low': .25}, grp=1)
        return pts

    def confetti(self, cx, cy, n=42, spread_x=5.5, spread_y=2.6, start=0, colors=None):
        """彩纸爆发：小色块从中心飞出、旋转、落定后淡出"""
        colors = colors or [self.t.accent, self.t.accent_2, self.t.accent_3] + self.t.grad
        rnd = random.Random(11)
        for i in range(n):
            ang = rnd.random() * math.tau
            r = rnd.random() ** .6
            fx = cx + math.cos(ang) * spread_x * r; fy = cy + math.sin(ang) * spread_y * r - .4
            sz = .07 + rnd.random() * .09
            shp = MSO_SHAPE.OVAL if i % 3 == 0 else MSO_SHAPE.RECTANGLE
            o = self.rect(fx - sz/2, fy - sz/2 + H + 1.0, sz * (1 if shp == MSO_SHAPE.OVAL else 1.7), sz, fill=rnd.choice(colors), shape=shp)
            o.rotation = rnd.randint(0, 180)
            self.a(o, 'burst', at=start + rnd.randint(0, 220), hold=True, dur=1500 + rnd.randint(0, 700),
                   params={'dx': (fx - cx) / W, 'dy': (fy - cy) / H, 'off': (H + 1.0) / H, 'rot': rnd.choice([-1, 1]) * rnd.randint(180, 540)})
