"""设计系统共用的小工具：背景、满版照片、数字拆分与宽度估算、大数字、方块格。"""
import re, pathlib
from core import W, H, MX, mix, rgb

ASSETS = pathlib.Path(__file__).resolve().parent.parent.parent / 'assets' / 'designs'


def bg(c, col):
    f = c.s.background.fill; f.solid(); f.fore_color.rgb = rgb(col)


def asset(design, name, s=None, deck=None):
    """页面图片：稿件里写了 image 就用稿件的，否则用设计系统自带的配图"""
    if s and s.get('image'):
        p = pathlib.Path(s['image'])
        return p if p.is_absolute() else pathlib.Path(deck.get('_base', '.')) / p
    return ASSETS / design / f'{name}.jpg'


def photo(c, path, x=0, y=0, w=W, h=H, at=0, dur=900, anim='fade'):
    p = c.picture(path, x, y, w, h, tone='natural')
    c.a(p, anim, at=at, hold=True, dur=dur)
    return p


def split(v):
    m = re.match(r'^([^\d]*)([\d.,]+)(.*)$', str(v))
    return (m.group(1), m.group(2), m.group(3)) if m else ('', str(v), '')


WD = {'1': .42, '.': .24, ',': .24, ':': .26, '%': .82, ' ': .26}

def tw(s, size, k=1.0):
    """估算文字宽度（英寸）；k 为西文字体宽度系数（窄体 < 1）"""
    return sum(1.0 if ord(ch) > 0x2E80 else WD.get(ch, .6) * k for ch in str(s)) * size / 72


def bignum(c, x, y, value, size, color, font, unit_font=None, unit_color=None, unit_scale=.2, gap=0, dur=1100, anim=True, bold=False, k=1.0, unit_pos='sup', align='l', w=None):
    """大数字 + 小单位（右上角上标，或 unit_pos='base' 跟在基线）"""
    pre, num, unit = split(value)
    nw = tw(pre + num, size, k) + .06
    hh = size / 72 * 1.08
    x0 = x if align == 'l' else x + (w - nw - tw(unit, size * unit_scale)) / 2
    if anim: c.counter(x0, y, nw + .4, hh, pre + num, size, color, gap=gap, dur=dur, bold=bold)
    else: c.text(x0, y, nw + .4, hh, pre + num, size, color, font=font, spacing=1, bold=bold)
    if unit:
        us = max(13, size * unit_scale)
        uy = y + size / 72 * .14 if unit_pos == 'sup' else y + hh - us / 72 * 1.55
        c.a(c.text(x0 + nw - size / 72 * .03, uy, tw(unit, us) + .3, us / 72 * 1.4, unit, us, unit_color or color, font=unit_font or font), 'fade', gap=0, hold=True)
    return nw


def plain(t):
    if isinstance(t, list): return [plain(x) for x in t]
    return str(t).replace('**', '')


def accent_tail(lines, n=2):
    """杂志式强调：没写 ** 时，把最后一行的最后 n 个字标成强调"""
    lines = lines if isinstance(lines, list) else [lines]
    if any('**' in l for l in lines): return lines
    last = lines[-1]
    return lines[:-1] + [last[:-n] + '**' + last[-n:] + '**']
