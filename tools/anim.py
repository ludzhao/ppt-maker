"""PowerPoint 原生动画（slide XML 的 <p:timing>）和页面切换（<p:transition>）。

动效命名对齐 html-ppt-skill（MIT）的 47 个动效，映射规则见 ../references/动效指南.md。
每个动画条目（item）：
  spid     目标形状 id
  effect   动效名（见 EFFECTS）
  delay    相对本组开始的毫秒数
  dur      时长（毫秒）
  step     0 = 进页自动播放；1、2… = 第几次点击
  kind     'sp' | 'graphic' | 'other'（决定 bldLst 写法）
  repeat   None | 'indefinite' | 次数（循环类动效）
  params   额外参数（如 burst 的 dx/dy/rot）
  chart_steps  图表逐类别生长时的类别数
"""
from lxml import etree

NS_P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
NS_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS_P14 = 'http://schemas.microsoft.com/office/powerpoint/2010/main'
NS_P15 = 'http://schemas.microsoft.com/office/powerpoint/2012/main'

# 网页动效名 -> 本文件实现的原生动效名（同义词 / 降级）
ALIAS = {
    'rise-in': 'rise', 'drop-in': 'drop', 'zoom-pop': 'pop', 'blur-in': 'blur', 'glitch-in': 'glitch',
    'typewriter': 'type', 'letter-explode': 'type', 'word-cascade': 'type', 'typewriter-multi': 'type',
    'stagger-list': 'fade-up', 'stagger': 'fade-up', 'counter-up': 'pop', 'counter': 'pop',
    'path-draw': 'draw', 'card-flip-3d': 'flip', 'perspective-zoom': 'zoom', 'spotlight': 'circle',
    'ripple-reveal': 'circle', 'neon-glow': 'twinkle', 'shimmer-sweep': 'fade', 'gradient-flow': 'fade',
    'kenburns': 'kenburns', 'shockwave': 'ring', 'cube-rotate-3d': 'zoom', 'page-turn-3d': 'flip',
    'morph-shape': 'fade', 'marquee-scroll': 'fade-left',
}

ENTR = {  # 名称: (presetID, subtype)
    'appear': (1, 0), 'fade': (10, 0), 'fade-up': (42, 0), 'rise': (42, 0), 'fade-down': (47, 0),
    'drop': (47, 0), 'fade-left': (10, 0), 'fade-right': (10, 0), 'zoom': (53, 16), 'pop': (53, 16),
    'blur': (10, 0), 'glitch': (10, 0), 'flip': (17, 10), 'circle': (6, 32),
    'wipe-up': (22, 4), 'wipe-down': (22, 1), 'wipe-right': (22, 8), 'wipe-left': (22, 2),
    'draw': (22, 8), 'wheel': (21, 1), 'type': (10, 0), 'burst': (10, 0), 'split': (16, 21),
    'grow-up': (17, 4), 'grow-right': (17, 8), 'rise-from': (2, 4),
}
EMPH = {'spin': (8, 0), 'kenburns': (6, 0), 'pulse': (26, 0), 'twinkle': (9, 0), 'ring': (6, 0), 'sweep': (6, 0)}
EXIT = {'out': (10, 0), 'cut': (1, 0), 'out-up': (42, 0)}

WIPE = {'wipe-up': 'wipe(up)', 'wipe-down': 'wipe(down)', 'wipe-right': 'wipe(right)',
        'wipe-left': 'wipe(left)', 'draw': 'wipe(right)', 'wheel': 'wheel(1)', 'circle': 'circle(out)',
        'split': 'barn(outVertical)'}


class _Ids:
    def __init__(self): self.n = 2
    def __call__(self):
        self.n += 1
        return self.n


def _tgt(spid, sub=''):
    return f'<p:tgtEl><p:spTgt spid="{spid}">{sub}</p:spTgt></p:tgtEl>'


def _set_vis(ids, tgt, val='visible', delay=0):
    return (f'<p:set><p:cBhvr><p:cTn id="{ids()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="{delay}"/></p:stCondLst></p:cTn>'
            f'{tgt}<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="{val}"/></p:to></p:set>')


def _filter(ids, tgt, flt, dur, direction='in', delay=0):
    st = f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst>' if delay else ''
    return (f'<p:animEffect transition="{direction}" filter="{flt}"><p:cBhvr><p:cTn id="{ids()}" dur="{dur}">{st}</p:cTn>'
            f'{tgt}</p:cBhvr></p:animEffect>')


EASE = {True: ' accel="30000" decel="70000"', 'std': ' accel="30000" decel="70000"', 'out': ' decel="100000"', None: '', False: ''}


def _kf(ids, tgt, attr, frames, dur, calc='lin', decel='std', delay=0, value_type='num'):
    """关键帧动画：frames = [(0~1 时间点, 值字符串), ...]；decel: 'std' 标准缓动 / 'out' 强缓出 / None 线性"""
    tav = ''.join(f'<p:tav tm="{int(t*100000)}"><p:val><p:strVal val="{v}"/></p:val></p:tav>' for t, v in frames)
    de = EASE[True if decel is True else decel] if decel is not True else EASE['std']
    st = f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst>' if delay else ''
    return (f'<p:anim calcmode="{calc}" valueType="{value_type}"><p:cBhvr additive="base">'
            f'<p:cTn id="{ids()}" dur="{dur}"{de} fill="hold">{st}</p:cTn>{tgt}'
            f'<p:attrNameLst><p:attrName>{attr}</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:tavLst>{tav}</p:tavLst></p:anim>')


def _opacity(ids, tgt, frames, dur, delay=0):
    return _kf(ids, tgt, 'style.opacity', frames, dur, decel=None, delay=delay)


def _scale(ids, tgt, frm, to, dur, delay=0):
    st = f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst>' if delay else ''
    return (f'<p:animScale><p:cBhvr><p:cTn id="{ids()}" dur="{dur}" decel="100000" fill="hold">{st}</p:cTn>{tgt}</p:cBhvr>'
            f'<p:from x="{int(frm*100000)}" y="{int(frm*100000)}"/><p:to x="{int(to*100000)}" y="{int(to*100000)}"/></p:animScale>')


def _by_scale(ids, tgt, by, dur, auto_rev=False):
    ar = ' autoRev="1"' if auto_rev else ''
    return (f'<p:animScale><p:cBhvr><p:cTn id="{ids()}" dur="{dur}" fill="hold"{ar}/>{tgt}</p:cBhvr>'
            f'<p:by x="{int(by*100000)}" y="{int(by*100000)}"/></p:animScale>')


def _rot(ids, tgt, deg, dur):
    return (f'<p:animRot by="{int(deg*60000)}"><p:cBhvr><p:cTn id="{ids()}" dur="{dur}" fill="hold"/>{tgt}'
            f'<p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst></p:cBhvr></p:animRot>')


def _entr(ids, tgt, eff, dur, p):
    b = [_set_vis(ids, tgt)]
    if eff in WIPE:
        b.append(_filter(ids, tgt, WIPE[eff], dur))
        return b
    if eff == 'appear':
        if p.get('dy'):  # 从页面外瞬移到目标位置（数字滚动的中间帧平时放在页面外，静态视图更干净）
            b.append(_kf(ids, tgt, 'ppt_y', [(0, f'#ppt_y-{p["dy"]:.4f}'), (1, f'#ppt_y-{p["dy"]:.4f}')], 1, calc='discrete', decel=None))
        return b
    if eff == 'glitch':  # 故障闪现：透明度跳变 + 左右抖动
        b.append(_opacity(ids, tgt, [(0, '0'), (.15, '1'), (.25, '0.1'), (.4, '1'), (.5, '0.3'), (.62, '1'), (1, '1')], dur))
        b.append(_kf(ids, tgt, 'ppt_x', [(0, '#ppt_x-0.012'), (.2, '#ppt_x+0.01'), (.4, '#ppt_x-0.006'),
                                         (.6, '#ppt_x+0.004'), (1, '#ppt_x')], dur, calc='discrete', decel=None))
        return b
    if eff == 'grow-up':   # Chart.js 柱子/面积：底边不动，从 0 长到满高（easeOutQuart）
        b.append(_kf(ids, tgt, 'ppt_h', [(0, '0'), (1, '#ppt_h')], dur, decel='out'))
        b.append(_kf(ids, tgt, 'ppt_y', [(0, '#ppt_y+#ppt_h/2'), (1, '#ppt_y')], dur, decel='out'))
        return b
    if eff == 'grow-right':  # 横向条形：左边不动，从 0 长到满宽
        b.append(_kf(ids, tgt, 'ppt_w', [(0, '0'), (1, '#ppt_w')], dur, decel='out'))
        b.append(_kf(ids, tgt, 'ppt_x', [(0, '#ppt_x-#ppt_w/2'), (1, '#ppt_x')], dur, decel='out'))
        return b
    if eff == 'rise-from':   # 数据点/标签：从基线升到自己的位置（和图形同步）
        b.append(_kf(ids, tgt, 'ppt_y', [(0, f'#ppt_y+{p.get("dy", 0):.4f}'), (1, '#ppt_y')], dur, decel='out'))
        if p.get('dx'):
            b.append(_kf(ids, tgt, 'ppt_x', [(0, f'#ppt_x+{p["dx"]:.4f}'), (1, '#ppt_x')], dur, decel='out'))
        return b
    if eff == 'burst':  # 彩纸/粒子：从中心飞出、旋转、淡出
        dx, dy, rot, off = p.get('dx', 0), p.get('dy', 0), p.get('rot', 360), p.get('off', 0)
        b.append(_kf(ids, tgt, 'ppt_x', [(0, f'#ppt_x-{dx:.4f}'), (1, '#ppt_x')], dur))
        b.append(_kf(ids, tgt, 'ppt_y', [(0, f'#ppt_y-{dy + off:.4f}'), (1, f'#ppt_y-{off:.4f}')], dur))
        b.append(_rot(ids, tgt, rot, dur))
        b.append(_opacity(ids, tgt, [(0, '1'), (.6, '1'), (1, '0')], dur))
        return b
    b.append(_filter(ids, tgt, 'fade', dur if eff != 'type' else dur))
    off = {'fade-up': ('ppt_y', '+0.03'), 'rise': ('ppt_y', '+0.056'), 'fade-down': ('ppt_y', '-0.05'),
           'drop': ('ppt_y', '-0.10'), 'fade-left': ('ppt_x', '-0.05'), 'fade-right': ('ppt_x', '+0.05')}.get(eff)
    if off:
        a, d = off
        b.append(_kf(ids, tgt, a, [(0, f'#{a}{d}'), (1, f'#{a}')], dur))
    if eff == 'zoom':
        for a in ('ppt_w', 'ppt_h'):
            b.append(_kf(ids, tgt, a, [(0, f'#{a}*0.5'), (1, f'#{a}')], dur))
    if eff == 'pop':  # 0.6 -> 1.06 -> 1 回弹
        for a in ('ppt_w', 'ppt_h'):
            b.append(_kf(ids, tgt, a, [(0, f'#{a}*0.6'), (.6, f'#{a}*1.04'), (1, f'#{a}')], dur, decel=None))
    if eff == 'drop':
        for a in ('ppt_w', 'ppt_h'):
            b.append(_kf(ids, tgt, a, [(0, f'#{a}*1.08'), (1, f'#{a}')], dur))
    if eff in ('blur', 'rise'):
        k = '1.08' if eff == 'blur' else '0.97'
        for a in ('ppt_w', 'ppt_h'):
            b.append(_kf(ids, tgt, a, [(0, f'#{a}*{k}'), (1, f'#{a}')], dur))
    if eff == 'flip':  # 卡片翻入：宽度从 0 展开
        b.append(_kf(ids, tgt, 'ppt_w', [(0, '0'), (1, '#ppt_w')], dur))
    return b


def _emph(ids, tgt, eff, dur, p):
    if eff == 'kenburns':  # 图片缓慢推近
        return [_by_scale(ids, tgt, p.get('by', 1.12), dur)]
    if eff == 'spin':
        return [_rot(ids, tgt, p.get('deg', 360), dur)]
    if eff == 'pulse':
        return [_by_scale(ids, tgt, p.get('by', 1.06), dur // 2, auto_rev=True)]
    if eff == 'twinkle':
        return [_opacity(ids, tgt, [(0, '1'), (.5, str(p.get('low', 0.35))), (1, '1')], dur)]
    if eff == 'ring':  # 信号波纹：放大并淡出
        return [_set_vis(ids, tgt), _scale(ids, tgt, p.get('from', .3), p.get('to', 1.0), dur),
                _opacity(ids, tgt, [(0, '0'), (.12, str(p.get('peak', .9))), (1, '0')], dur)]
    if eff == 'sweep':  # 光带扫过
        return [_set_vis(ids, tgt), _kf(ids, tgt, 'ppt_x', [(0, f'#ppt_x-{p.get("dist", .3)}'), (1, f'#ppt_x+{p.get("dist", .3)}')], dur, decel=None),
                _opacity(ids, tgt, [(0, '0'), (.3, '0.8'), (.7, '0.8'), (1, '0')], dur)]
    raise ValueError(eff)


def _exit(ids, tgt, eff, dur, p):
    if eff == 'cut':
        return [_set_vis(ids, tgt, 'hidden')]
    b = [_filter(ids, tgt, 'fade', dur, direction='out')]
    if eff == 'out-up':
        b.append(_kf(ids, tgt, 'ppt_y', [(0, '#ppt_y'), (1, '#ppt_y-0.05')], dur))
    b.append(_set_vis(ids, tgt, 'hidden', delay=dur - 1))
    return b


def _chart_targets(item):
    """图表逐类别生长：先出坐标轴，再一根一根出来"""
    n = item['chart_steps']
    yield '<p:graphicEl><a:chart seriesIdx="-3" categoryIdx="-3" bldStep="gridLegend"/></p:graphicEl>', 0
    for i in range(n):
        yield f'<p:graphicEl><a:chart seriesIdx="-4" categoryIdx="{i}" bldStep="category"/></p:graphicEl>', i + 1


def _effect_pars(ids, item, first_node):
    eff = ALIAS.get(item['effect'], item['effect'])
    dur = item.get('dur', 600); p = item.get('params', {})
    rep = item.get('repeat')
    rep_attr = f' repeatCount="{"indefinite" if rep == "indefinite" else int(rep*1000)}"' if rep else ''
    if eff in EMPH: cls, (pid, sub) = 'emph', EMPH[eff]
    elif eff in EXIT: cls, (pid, sub) = 'exit', EXIT[eff]
    else:
        if eff not in ENTR: eff = 'fade-up'
        cls, (pid, sub) = 'entr', ENTR[eff]
    out = []
    targets = [('', 0)]
    if item.get('chart_steps'):
        targets = list(_chart_targets(item))
    for k, (sub_t, idx) in enumerate(targets):
        tgt = f'<p:tgtEl><p:spTgt spid="{item["spid"]}">{sub_t}</p:spTgt></p:tgtEl>'
        node = first_node if k == 0 and first_node else 'withEffect'
        delay = int(item.get('delay', 0)) + idx * item.get('step_gap', 220)
        iterate = ''
        d = dur
        if eff == 'type':
            d = 250
            iterate = '<p:iterate type="lt"><p:tmPct val="22000"/></p:iterate>'
        if cls == 'entr': beh = _entr(ids, tgt, eff, d, p)
        elif cls == 'emph': beh = _emph(ids, tgt, eff, d, p)
        else: beh = _exit(ids, tgt, eff, d, p)
        cid = ids()
        out.append(f'<p:par><p:cTn id="{cid}" presetID="{pid}" presetClass="{cls}" presetSubtype="{sub}" fill="hold"'
                   f' grpId="{item.get("grp", 0)}" nodeType="{node}"{rep_attr}><p:stCondLst><p:cond delay="{delay}"/></p:stCondLst>'
                   f'{iterate}<p:childTnLst>{"".join(beh)}</p:childTnLst></p:cTn></p:par>')
    return out


SPEED = 1.3   # 全局倍速（用户要求整体快 1.3 倍）


def _speed(items):
    out = []
    first = min((i.get('delay', 0) for i in items if i.get('step', 0) == 0), default=0)
    for i in items:
        j = dict(i)
        d = j.get('delay', 0) - (first if j.get('step', 0) == 0 else 0)
        j['delay'] = int(d / SPEED)
        if j.get('dur', 0) > 1 and j.get('repeat') is None: j['dur'] = max(1, int(j['dur'] / SPEED))
        if j.get('step_gap'): j['step_gap'] = int(j['step_gap'] / SPEED)
        out.append(j)
    return out


def build_timing(items):
    if not items: return None
    items = _speed(items)
    ids = _Ids()
    steps = sorted({i.get('step', 0) for i in items})
    groups = []
    for s in steps:
        its = sorted([i for i in items if i.get('step', 0) == s], key=lambda i: i.get('delay', 0))
        outer = ids(); inner = ids()
        cond = ('<p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond>'
                if s == 0 else '<p:cond delay="indefinite"/>')
        effs = []
        for k, it in enumerate(its):
            effs += _effect_pars(ids, it, ('afterEffect' if s == 0 else 'clickEffect') if k == 0 else None)
        groups.append(f'<p:par><p:cTn id="{outer}" fill="hold"><p:stCondLst>{cond}</p:stCondLst><p:childTnLst>'
                      f'<p:par><p:cTn id="{inner}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                      f'<p:childTnLst>{"".join(effs)}</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')
    bld = []
    seen = set()
    for it in items:
        key = (it['spid'], it.get('grp', 0))
        if key in seen: continue
        seen.add(key)
        if it.get('kind') == 'sp':
            bld.append(f'<p:bldP spid="{it["spid"]}" grpId="{it.get("grp", 0)}" animBg="1"/>')
        elif it.get('kind') == 'graphic':
            if it.get('chart_steps'):
                bld.append(f'<p:bldGraphic spid="{it["spid"]}" grpId="{it.get("grp", 0)}"><p:bldSub>'
                           f'<a:bldChart xmlns:a="{NS_A}" bld="category"/></p:bldSub></p:bldGraphic>')
            else:
                bld.append(f'<p:bldGraphic spid="{it["spid"]}" grpId="{it.get("grp", 0)}"><p:bldAsOne/></p:bldGraphic>')
    xml = (f'<p:timing xmlns:p="{NS_P}" xmlns:a="{NS_A}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
           f'<p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq">'
           f'<p:childTnLst>{"".join(groups)}</p:childTnLst></p:cTn>'
           f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
           f'</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>'
           f'{"<p:bldLst>" + "".join(bld) + "</p:bldLst>" if bld else ""}</p:timing>')
    return etree.fromstring(xml)


# ------------------------------------------------------------------ 页面切换
# html-ppt 的 3D / 揭幕类效果在 PowerPoint 里用切换实现
TRANSITIONS = {
    'fade': ('p', '<p:fade/>'),
    'push': ('p', '<p:push dir="u"/>'),
    'wipe': ('p', '<p:wipe dir="r"/>'),
    'cover': ('p', '<p:cover dir="l"/>'),
    'circle': ('p', '<p:circle/>'),            # spotlight
    'zoom': ('p', '<p:zoom/>'),
    'morph': ('p159', '<p159:morph option="byObject"/>'),   # 平滑（同名形状自动补间）
    'cube': ('p14', '<p14:prism/>'),            # cube-rotate-3d
    'rotate': ('p14', '<p14:prism isContent="1"/>'),
    'gallery': ('p14', '<p14:gallery dir="l"/>'),
    'flip': ('p14', '<p14:flip dir="r"/>'),     # card-flip-3d
    'ripple': ('p14', '<p14:ripple/>'),         # ripple-reveal
    'vortex': ('p14', '<p14:vortex dir="r"/>'),
    'honeycomb': ('p14', '<p14:honeycomb/>'),
    'glitter': ('p14', '<p14:glitter pattern="hexagon"/>'),
    'flythrough': ('p14', '<p14:flythrough/>'),  # perspective-zoom
    'conveyor': ('p14', '<p14:conveyor dir="l"/>'),
    'reveal': ('p14', '<p14:reveal thruBlk="1"/>'),
    'pagecurl': ('p15', '<p15:prstTrans prst="pageCurlDouble"/>'),  # page-turn-3d
    'curtains': ('p15', '<p15:prstTrans prst="curtains"/>'),
    'fracture': ('p15', '<p15:prstTrans prst="fracture"/>'),
    'origami': ('p15', '<p15:prstTrans prst="origami"/>'),
}
_NS_FOR = {'p14': NS_P14, 'p15': NS_P15, 'p159': 'http://schemas.microsoft.com/office/powerpoint/2015/09/main'}


def transition_xml(kind, speed='fast'):
    if not kind or kind == 'none': return None
    ns, inner = TRANSITIONS.get(kind, TRANSITIONS['fade'])
    if ns == 'p':
        return etree.fromstring(f'<p:transition xmlns:p="{NS_P}" spd="{speed}">{inner}</p:transition>')
    xml = (f'<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:p="{NS_P}">'
           f'<mc:Choice xmlns:{ns}="{_NS_FOR[ns]}" Requires="{ns}">'
           f'<p:transition spd="{speed}">{inner}</p:transition></mc:Choice>'
           f'<mc:Fallback><p:transition spd="{speed}"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')
    return etree.fromstring(xml)


def attach(slide, items, transition=None, speed='fast'):
    sld = slide._element
    for tag in ('transition', 'timing'):
        for old in sld.findall(f'{{{NS_P}}}{tag}'): sld.remove(old)
    for old in sld.findall('{http://schemas.openxmlformats.org/markup-compatibility/2006}AlternateContent'):
        sld.remove(old)
    ext = sld.find(f'{{{NS_P}}}extLst')
    for el in (transition_xml(transition, speed), build_timing(items)):
        if el is None: continue
        if ext is not None: ext.addprevious(el)
        else: sld.append(el)
