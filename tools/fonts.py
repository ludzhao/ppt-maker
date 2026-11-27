"""开源字体：读取离线包、实例化字重、按用到的字子集化、嵌入 pptx（对方电脑没装字体也能正常显示）。

所有字体均为 SIL Open Font License 1.1，允许嵌入文档和随软件分发（授权原文见 licenses/）。
嵌入格式：PowerPoint 的 ppt/fonts/*.fntdata = Embedded OpenType（未压缩、未加密）。
"""
import io, re, struct, zipfile, pathlib, shutil
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset as ftsubset

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / 'fonts' / 'cache'
PACK = ROOT / 'fonts' / 'pack'   # 随 skill 分发的离线包：中文字体是 GB2312 全部 6763 字 + 常用符号的静态子集
# 本模块不联网：字体只从 fonts/pack（离线包，由 setup_env.py 校验后放好）和 fonts/cache（可选，用户自备的完整字体）读取。

# PPT 里用的字体名 -> {样式: (源文件, 可变轴设置 或 None)}
FAMILIES = {
    'Noto Sans SC':        {'regular': ('NotoSansSC[wght].ttf', {'wght': 400}), 'bold': ('NotoSansSC[wght].ttf', {'wght': 700})},
    'Noto Sans SC Black':  {'regular': ('NotoSansSC[wght].ttf', {'wght': 900}), 'bold': ('NotoSansSC[wght].ttf', {'wght': 900})},
    'Noto Serif SC':       {'regular': ('NotoSerifSC[wght].ttf', {'wght': 400}), 'bold': ('NotoSerifSC[wght].ttf', {'wght': 700})},
    'Noto Serif SC Black': {'regular': ('NotoSerifSC[wght].ttf', {'wght': 900}), 'bold': ('NotoSerifSC[wght].ttf', {'wght': 900})},
    'Smiley Sans':         {'regular': ('smiley/SmileySans-Oblique.ttf', None), 'bold': ('smiley/SmileySans-Oblique.ttf', None)},
    'LXGW WenKai':         {'regular': ('LXGWWenKai-Regular.ttf', None), 'bold': ('LXGWWenKai-Medium.ttf', None)},
    'Inter':               {'regular': ('Inter[opsz,wght].ttf', {'wght': 400, 'opsz': 14}), 'bold': ('Inter[opsz,wght].ttf', {'wght': 700, 'opsz': 32})},
    'Space Grotesk Light': {'regular': ('SpaceGrotesk[wght].ttf', {'wght': 300}), 'bold': ('SpaceGrotesk[wght].ttf', {'wght': 500})},
    'Noto Sans SC Light':  {'regular': ('NotoSansSC[wght].ttf', {'wght': 300}), 'bold': ('NotoSansSC[wght].ttf', {'wght': 500})},
    'Space Grotesk':       {'regular': ('SpaceGrotesk[wght].ttf', {'wght': 400}), 'bold': ('SpaceGrotesk[wght].ttf', {'wght': 700})},
    'Playfair Display':    {'regular': ('PlayfairDisplay[wght].ttf', {'wght': 400}), 'bold': ('PlayfairDisplay[wght].ttf', {'wght': 700})},
}


def _open(family, style, text):
    """找字体文件：完整字体（fonts/cache，可选）> 离线包。离线包缺的生僻字由对方电脑的系统字体显示。"""
    src, axes = FAMILIES[family][style]
    if (CACHE / src).exists(): return TTFont(CACHE / src), axes
    if (PACK / src).exists(): return TTFont(PACK / src), axes          # 西文字体：整个可变字体都在包里
    pk = PACK / f"{family.replace(' ', '')}-{style}.ttf"
    if not pk.exists() and style == 'bold': pk = PACK / f"{family.replace(' ', '')}-regular.ttf"
    if not pk.exists():
        raise FileNotFoundError(f'缺少字体文件 {pk.name}，请先运行 python3 tools/setup_env.py 补齐素材')
    f = TTFont(pk); cmap = f.getBestCmap()
    missing = {ch for ch in text if ch.strip() and ord(ch) not in cmap}
    if missing:
        print(f'提示：{family} 离线包缺 {len(missing)} 个生僻字（如 {"".join(sorted(missing)[:8])}），这些字由对方电脑的系统字体显示')
    return f, None

def _rename(font, family, style):
    name = font['name']
    full = family if style == 'Regular' else f'{family} {style}'
    ps = re.sub(r'[^A-Za-z0-9-]', '', family.replace(' ', '')) + '-' + style
    for rec in list(name.names):
        if rec.nameID in (16, 17, 21, 22, 25): name.removeNames(nameID=rec.nameID)
    for nid, val in ((1, family), (2, style), (4, full), (6, ps)):
        name.setName(val, nid, 3, 1, 0x409); name.setName(val, nid, 1, 0, 0)
    font['OS/2'].usWeightClass = 700 if style == 'Bold' else 400
    font['OS/2'].fsSelection = (font['OS/2'].fsSelection & ~0b1100001) | (0b100000 if style == 'Bold' else 0b1000000)
    font['head'].macStyle = 1 if style == 'Bold' else 0


def build_subset(family, style, text):
    """返回子集化后的 TTF 字节（只含 text 里出现的字 + 基本拉丁）"""
    font, axes = _open(family, style, text)
    if axes is not None and 'fvar' in font:
        axes = {k: v for k, v in axes.items() if k in [a.axisTag for a in font['fvar'].axes]}
        font = instancer.instantiateVariableFont(font, axes, updateFontNames=False)
    opts = ftsubset.Options()
    opts.layout_features = ['kern', 'liga', 'locl', 'vert', 'palt']
    opts.name_IDs = ['*']; opts.name_languages = ['*']; opts.notdef_outline = True
    opts.hinting = False; opts.drop_tables += ['DSIG', 'STAT', 'MVAR', 'HVAR']
    sub = ftsubset.Subsetter(opts)
    chars = set(text) | set(' 0123456789.,%+-–—:;!?()（）、，。：；！？“”‘’《》·/*×÷=<>' +
                            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
    sub.populate(unicodes=[ord(ch) for ch in chars])
    sub.subset(font)
    _rename(font, family, 'Bold' if style == 'bold' else 'Regular')
    if 'OS/2' in font: font['OS/2'].fsType = 0   # OFL：可安装嵌入
    buf = io.BytesIO(); font.save(buf)
    return buf.getvalue(), font


def to_eot(ttf_bytes, font):
    """Embedded OpenType 0x00020001，未压缩"""
    os2 = font['OS/2']; nm = font['name']
    def s(nid):
        v = nm.getDebugName(nid) or ''
        return v.encode('utf-16-le')
    fam, sty, ver, full = s(1), s(2), s(5), s(4)
    panose = os2.panose
    pan = bytes([panose.bFamilyType, panose.bSerifStyle, panose.bWeight, panose.bProportion, panose.bContrast,
                 panose.bStrokeVariation, panose.bArmStyle, panose.bLetterForm, panose.bMidline, panose.bXHeight])
    italic = 1 if (os2.fsSelection & 1) else 0
    body = struct.pack('<I', 0x00020001) + struct.pack('<I', 0) + pan + struct.pack('<BBIHH', 1, italic, os2.usWeightClass, 0, 0x504C)
    body += struct.pack('<IIII', os2.ulUnicodeRange1, os2.ulUnicodeRange2, os2.ulUnicodeRange3, os2.ulUnicodeRange4)
    body += struct.pack('<II', getattr(os2, 'ulCodePageRange1', 1), getattr(os2, 'ulCodePageRange2', 0))
    body += struct.pack('<I', font['head'].checkSumAdjustment) + b'\0' * 16
    for i, st in enumerate((fam, sty, ver, full)):
        body += struct.pack('<H', 0) + struct.pack('<H', len(st)) + st
    body += struct.pack('<H', 0) + struct.pack('<H', 0)            # Padding5 + RootStringSize=0
    header_len = 8 + len(body)
    return struct.pack('<II', header_len + len(ttf_bytes), len(ttf_bytes)) + body + ttf_bytes


# ------------------------------------------------------------------ 扫描 pptx 用到的字 + 嵌入
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'

def collect_usage(z):
    """{(字体名, 'regular'|'bold'): 字符集合}"""
    from lxml import etree
    usage = {}
    for n in z.namelist():
        if not re.match(r'ppt/slides/slide\d+\.xml$', n): continue
        root = etree.fromstring(z.read(n))
        for r in root.iter(f'{A}r'):
            rpr = r.find(f'{A}rPr'); t = r.find(f'{A}t')
            if rpr is None or t is None or not t.text: continue
            faces = {el.get('typeface') for el in (rpr.find(f'{A}latin'), rpr.find(f'{A}ea')) if el is not None}
            bold = 'bold' if rpr.get('b') == '1' else 'regular'
            for f in faces:
                if f in FAMILIES: usage.setdefault((f, bold), set()).update(t.text)
    return usage


def embed(pptx_path):
    """把 pptx 用到的开源字体子集嵌进去（原地改写）。返回嵌入清单"""
    p = pathlib.Path(pptx_path)
    with zipfile.ZipFile(p) as z:
        files = {n: z.read(n) for n in z.namelist()}
    with zipfile.ZipFile(p) as z:
        usage = collect_usage(z)
    if not usage: return []
    from lxml import etree
    pres = etree.fromstring(files['ppt/presentation.xml'])
    rels = etree.fromstring(files['ppt/_rels/presentation.xml.rels'])
    ct = etree.fromstring(files['[Content_Types].xml'])
    NSP = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    NSR = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    NSREL = 'http://schemas.openxmlformats.org/package/2006/relationships'
    NSCT = 'http://schemas.openxmlformats.org/package/2006/content-types'
    if not any(d.get('Extension') == 'fntdata' for d in ct.findall(f'{{{NSCT}}}Default')):
        d = etree.SubElement(ct, f'{{{NSCT}}}Default'); d.set('Extension', 'fntdata'); d.set('ContentType', 'application/x-fontdata')
        ct.insert(0, d)
    old = pres.find(f'{{{NSP}}}embeddedFontLst')
    if old is not None: pres.remove(old)
    lst = etree.Element(f'{{{NSP}}}embeddedFontLst')
    used_ids = {r.get('Id') for r in rels}
    k = 0; report = []
    for fam in sorted({f for f, _ in usage}):
        ef = etree.SubElement(lst, f'{{{NSP}}}embeddedFont')
        fe = etree.SubElement(ef, f'{{{NSP}}}font'); fe.set('typeface', fam); fe.set('charset', '-122' if 'SC' in fam or fam in ('Smiley Sans', 'LXGW WenKai') else '0')
        for style in ('regular', 'bold'):
            if (fam, style) not in usage: continue
            ttf, font = build_subset(fam, style, ''.join(usage[(fam, style)]))
            eot = to_eot(ttf, font)
            k += 1
            part = f'fonts/font{k}.fntdata'
            files['ppt/' + part] = eot
            rid = f'rIdFont{k}'
            while rid in used_ids: rid += 'x'
            used_ids.add(rid)
            r = etree.SubElement(rels, f'{{{NSREL}}}Relationship'); r.set('Id', rid)
            r.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/font'); r.set('Target', part)
            el = etree.SubElement(ef, f'{{{NSP}}}{style}'); el.set(f'{{{NSR}}}id', rid)
            report.append((fam, style, len(usage[(fam, style)]), len(eot)))
    notes = pres.find(f'{{{NSP}}}notesSz')
    notes.addnext(lst)
    pres.set('embedTrueTypeFonts', '1'); pres.set('saveSubsetFonts', '1')
    files['ppt/presentation.xml'] = etree.tostring(pres, xml_declaration=True, encoding='UTF-8', standalone=True)
    files['ppt/_rels/presentation.xml.rels'] = etree.tostring(rels, xml_declaration=True, encoding='UTF-8', standalone=True)
    files['[Content_Types].xml'] = etree.tostring(ct, xml_declaration=True, encoding='UTF-8', standalone=True)
    tmp = p.with_suffix('.tmp.pptx')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', files.pop('[Content_Types].xml'))
        for n, b in files.items(): z.writestr(n, b)
    shutil.move(tmp, p)
    return report


if __name__ == '__main__':
    import sys
    for row in embed(sys.argv[1]): print(*row)
