"""JSON 稿件 -> 原生可编辑 pptx（36 套主题、18 种版式、原生图表、原生动画、演讲备注）。

用法：python build_deck.py deck.json out.pptx [--theme tokyo-night] [--font "Microsoft YaHei"]
稿件格式见 ../SKILL.md，示例见 ../examples/。
"""
import json, sys, pathlib, argparse
from pptx import Presentation
from pptx.util import Inches
from pptx.oxml.ns import qn
from lxml import etree

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import anim
from core import Theme, Canvas, W, H
from layouts import LAYOUTS, NO_FOOTER, footer, frame
import styles, fonts as fontlib

DEFAULT_STYLE = 'consulting'   # 没写 style 也没写 theme 时用咨询报告风格


def _register_notes_master(prs):
    """python-pptx 有备注时不写 notesMasterIdLst：PowerPoint 能容忍，Keynote / WPS 会报「文件格式无效」"""
    from pptx.opc.constants import RELATIONSHIP_TYPE as RT
    pres = prs.part._element
    if pres.find(qn('p:notesMasterIdLst')) is not None: return
    rids = [r for r, rel in prs.part.rels.items() if rel.reltype == RT.NOTES_MASTER]
    if not rids: return
    lst = etree.Element(qn('p:notesMasterIdLst'))
    etree.SubElement(lst, qn('p:notesMasterId')).set(qn('r:id'), rids[0])
    pres.find(qn('p:sldMasterIdLst')).addnext(lst)


def _embed_source(out, deck):
    """把稿件 JSON 存进 pptx（ppt-maker/deck.json）：以后只有 pptx 也能取回稿件、改完重新生成"""
    import zipfile, shutil
    out = pathlib.Path(out)
    with zipfile.ZipFile(out) as z: files = {n: z.read(n) for n in z.namelist()}
    src = {k: v for k, v in deck.items() if not k.startswith('_')}
    files['ppt-maker/deck.json'] = json.dumps(src, ensure_ascii=False, indent=1).encode('utf-8')
    ct = files['[Content_Types].xml'].decode('utf-8')
    if 'Extension="json"' not in ct:
        ct = ct.replace('<Default ', '<Default Extension="json" ContentType="application/json"/><Default ', 1)
    files['[Content_Types].xml'] = ct.encode('utf-8')
    rels = files['_rels/.rels'].decode('utf-8')
    if 'ppt-maker/deck.json' not in rels:
        rels = rels.replace('</Relationships>', '<Relationship Id="rIdPptMaker" Type="https://ppt-maker/deck-source" Target="ppt-maker/deck.json"/></Relationships>')
    files['_rels/.rels'] = rels.encode('utf-8')
    tmp = out.with_suffix('.tmp.pptx')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', files.pop('[Content_Types].xml'))
        for n, b in files.items(): z.writestr(n, b)
    shutil.move(tmp, out)


def _write_script(out, deck):
    """演讲稿：每页的标题 + notes，存成 <文件名>_讲稿.md"""
    import re
    out = pathlib.Path(out); lines = [f"# {deck.get('title', out.stem)} · 演讲稿", '']
    for i, s in enumerate(deck['slides'], 1):
        t = s.get('title') or s.get('text') or s.get('layout')
        t = ''.join(t) if isinstance(t, list) else str(t)
        lines += [f'## 第 {i} 页 · {re.sub(r"[*]", "", t)}', '', s.get('notes', '（这一页没有写讲稿）'), '']
    f = out.with_name(out.stem + '_讲稿.md'); f.write_text('\n'.join(lines), encoding='utf-8')
    return f


def build(deck, out, theme_name=None, font=None, base=None, style_name=None, embed_fonts=True):
    themes = json.loads((HERE / 'themes.json').read_text(encoding='utf-8'))
    sn = style_name or deck.get('style') or (None if (theme_name or deck.get('theme')) else DEFAULT_STYLE)
    style = styles.get(sn) if sn else None
    tn = theme_name or deck.get('theme')
    if style and not theme_name:
        t = Theme(dict(style['palette'], name=sn, label=style['label']))
    else:
        tn = tn or 'corporate-clean'
        if tn not in themes: raise SystemExit(f'没有这个主题：{tn}。可选：{", ".join(themes)}')
        t = Theme(themes[tn])
    fnt = font or deck.get('font') or (None if style else 'Microsoft YaHei')
    deck = dict(deck); deck['_base'] = str(base or '.')
    if sn: deck['style'] = sn
    deck['_total'] = len(deck['slides'])
    prs = Presentation(); prs.slide_width = Inches(W); prs.slide_height = Inches(H)
    blank = prs.slide_layouts[6]
    total = len(deck['slides'])
    design = None
    if style and style.get('design'):   # 设计系统：版式自带（tools/design_<名字>.py），没覆盖的页型用通用版式
        import importlib
        design = importlib.import_module('design_' + style['design'])
    for i, s in enumerate(deck['slides'], 1):
        slide = prs.slides.add_slide(blank)
        c = Canvas(slide, t, fnt, style); c.idx = i
        c.top = {'rule': .62, 'masthead': 1.05, 'minimal': .6, 'swiss': .95, 'brutal': .8, 'ink': .75, 'term': .75}.get(c.style.get('frame'), .55)
        lay = s.get('layout', 'points')
        if lay not in LAYOUTS: raise SystemExit(f'第 {i} 页版式 {lay} 不存在，可选：{", ".join(LAYOUTS)}')
        own = design and lay in design.LAYOUTS
        (design.LAYOUTS[lay] if own else LAYOUTS[lay])(c, s, deck)
        if not own and lay not in NO_FOOTER:
            frame(c, deck, i, total)
            footer(c, i, total, deck)
        if s.get('notes'): slide.notes_slide.notes_text_frame.text = s['notes']
        if s.get('anim') == 'none' or deck.get('anim') == 'none': c.anims = []
        anim.attach(slide, c.anims, s.get('transition', deck.get('transition', 'fade')), s.get('transition_speed', 'fast'))
    _register_notes_master(prs)
    prs.save(out)
    if embed_fonts and style:
        fontlib.embed(out)   # 开源字体子集嵌入：对方电脑没装也能正常显示
    _embed_source(out, deck)
    _write_script(out, deck)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('deck'); ap.add_argument('out')
    ap.add_argument('--theme'); ap.add_argument('--font'); ap.add_argument('--style')
    ap.add_argument('--no-embed', action='store_true')
    a = ap.parse_args()
    p = pathlib.Path(a.deck)
    deck = json.loads(p.read_text(encoding='utf-8'))
    out = build(deck, a.out, a.theme, a.font, base=p.parent, style_name=a.style, embed_fonts=not a.no_embed)
    print('已生成', out, '和', pathlib.Path(out).with_name(pathlib.Path(out).stem + '_讲稿.md'))
    import check_deck
    iss = check_deck.check(out)
    if iss:
        print(f'自查发现 {len(iss)} 个问题（改稿件后重新生成）：')
        for pg, what, fix in iss: print(f'  第 {pg} 页 · {what} → {fix}')
    else:
        print('自查通过。')
