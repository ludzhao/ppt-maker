"""把 html-ppt-skill 的 36 套主题 CSS 变量转成 themes.json（PPT 配色用）。
来源：github.com/lewislulu/html-ppt-skill（MIT），见 NOTICE。
用法：python extract_themes.py <html-ppt-skill/assets/themes 目录> <输出 themes.json>
"""
import json, re, sys, pathlib

def hex6(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(c*2 for c in h)
    return h[:6].upper()

def blend(rgba, bg):
    m = re.match(r'rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)', rgba)
    if not m: return None
    r, g, b = (float(m.group(i)) for i in (1, 2, 3))
    a = float(m.group(4) or 1)
    br, bgc, bb = (int(bg[i:i+2], 16) for i in (0, 2, 4))
    return '%02X%02X%02X' % tuple(round(c*a + d*(1-a)) for c, d in ((r, br), (g, bgc), (b, bb)))

def color(v, bg):
    v = v.strip()
    if v.startswith('#'): return hex6(v)
    if v.startswith('rgb'): return blend(v, bg)
    return None

def parse(path):
    css = path.read_text(encoding='utf-8')
    root = re.search(r':root\s*\{(.*?)\}', css, re.S)
    if not root: return None
    vars_ = dict(re.findall(r'--([a-z0-9-]+)\s*:\s*([^;]+);', root.group(1)))
    bg = hex6(vars_['bg']) if vars_.get('bg', '').startswith('#') else 'FFFFFF'
    t = {'name': path.stem, 'label': (re.match(r'/\*\s*theme:\s*([^*]+)\*/', css) or [None, path.stem])[1].strip()}
    for k in ['bg', 'bg-soft', 'surface', 'surface-2', 'border', 'border-strong', 'text-1', 'text-2', 'text-3',
              'accent', 'accent-2', 'accent-3', 'accent-ink', 'good', 'warn', 'bad']:
        if k in vars_:
            c = color(vars_[k], bg)
            if c: t[k.replace('-', '_')] = c
    for k in ['grad', 'grad-soft']:
        if k in vars_:
            t[k.replace('-', '_')] = [hex6(h) for h in re.findall(r'#[0-9a-fA-F]{3,8}', vars_[k])]
    r = re.match(r'([\d.]+)px', vars_.get('radius', '8px'))
    t['radius_px'] = float(r.group(1)) if r else 8
    t['serif'] = 'serif' in vars_.get('font-display', vars_.get('font-sans', '')).lower().split(',')[0] or 'serif' in path.stem
    lum = lambda h: sum(int(h[i:i+2], 16)*w for i, w in ((0, .299), (2, .587), (4, .114)))
    t['dark'] = lum(bg) < 128
    return t

if __name__ == '__main__':
    src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    themes = {}
    for p in sorted(src.glob('*.css')):
        t = parse(p)
        if t: themes[t['name']] = t
    out.write_text(json.dumps(themes, ensure_ascii=False, indent=1), encoding='utf-8')
    print(len(themes), 'themes ->', out)
