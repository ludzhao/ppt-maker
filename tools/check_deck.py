"""生成后自查（不需要 PowerPoint）：python tools/check_deck.py out.pptx
逐页检查：
  1. 排满：内容页的内容底边要到页面高度 78% 以下，否则「下半页空」
  2. 溢出：文字估算行数超过文本框高度
  3. 出界：形状超出页面（数字滚动、彩纸等动画帧故意放在页面下方，自动忽略）
  4. 字太小：正文 < 10pt（图片署名除外）
有问题时返回码 1，并逐条打印「第几页 · 问题 · 建议」。
"""
import json, math, re, sys, zipfile
from pptx import Presentation
from pptx.util import Emu

EMU = 914400
FULL = {'cover', 'section', 'quote', 'end', 'hero', 'stat', 'split'}   # 这些版式本来就留白或满版图，不查排满
FRAME_TOP, FRAME_BOTTOM = .55, .6                                         # 页眉、页脚区


def load_deck(path):
    with zipfile.ZipFile(path) as z:
        n = [x for x in z.namelist() if x.endswith('ppt-maker/deck.json')]
        return json.loads(z.read(n[0])) if n else None


def text_width(s, size):
    return sum(1.0 if ord(ch) > 0x2E80 else (.3 if ch in ' .,:;|' else .56) for ch in s) * size / 72


def check(path):
    prs = Presentation(path); W = prs.slide_width / EMU; H = prs.slide_height / EMU
    deck = load_deck(path); issues = []
    import styles
    airy = bool(deck and styles.STYLES.get(deck.get('style'), {}).get('design'))   # 设计系统讲究留白，不查「排满」
    for i, slide in enumerate(prs.slides, 1):
        lay = deck['slides'][i - 1].get('layout') if deck else None
        bottom = 0
        for sh in slide.shapes:
            x, y = (sh.left or 0) / EMU, (sh.top or 0) / EMU
            w, h = (sh.width or 0) / EMU, (sh.height or 0) / EMU
            if y > H + .5: continue                                      # 动画帧（故意放在页面外）
            if w >= W - .01 and h >= H - .01: continue                   # 满版背景图 / 遮罩
            if getattr(sh, 'rotation', 0) and abs(sh.rotation) > 45: continue   # 竖排旋转的标题：按旋转前的框算会误报
            if x < -.05 or y < -.05 or x + w > W + .05 or y + h > H + .05:
                if not (sh.shape_type == 13 or 'glow' in sh.name.lower() or w > W * .6 or (w > 2 and h > 2)):
                    issues.append((i, f'「{sh.name}」超出页面', '缩小或挪进页面'))
            inside = y > FRAME_TOP and y + h < H - FRAME_BOTTOM + .05
            txt = sh.text_frame.text.strip() if sh.has_text_frame else ''
            if inside and not txt: bottom = max(bottom, y + h)
            if not txt: continue
            tf = sh.text_frame
            if tf._txBody.find('{http://schemas.openxmlformats.org/drawingml/2006/main}bodyPr').get('vert'): continue   # 竖排文字
            need = 0
            for p in tf.paragraphs:
                runs = [r for r in p.runs if r.text]
                if not runs: continue
                size = max((r.font.size.pt if r.font.size else 18) for r in runs)
                if size < 10 and not txt.startswith(('图片：', '图片来源')) and y < H:
                    issues.append((i, f'字号 {size:g}pt 太小：「{txt[:16]}」', '正文 ≥ 14pt，注释 ≥ 11pt，来源 ≥ 10pt'))
                lines = max(1, math.ceil(text_width(p.text, size) / max(w, .1) - .02))
                need += lines * size * (p.line_spacing if isinstance(p.line_spacing, float) else 1.2) * 1.2 / 72
            if inside:   # 文字框按实际文字高度算（框本身常常比字高）
                anchor = str(tf.vertical_anchor or '')
                bottom = max(bottom, y + h if ('MIDDLE' in anchor or 'BOTTOM' in anchor) else y + min(h, need))
            if need > h + .2 and y < H and len(txt) > 4:
                issues.append((i, f'文字可能溢出：「{txt[:18]}」需要约 {need:.1f} 英寸高，框只有 {h:.1f}', '删字、拆成两页或换宽一点的版式'))
        if lay and not airy and lay not in FULL and bottom and bottom < H * .78:
            issues.append((i, f'下半页空：内容只排到 {bottom / H * 100:.0f}% 高度（{lay}）',
                           '加一张图表/构成条/结论句，或换信息量更大的版式（见 SKILL.md「排不满时」）'))
    return issues


if __name__ == '__main__':
    iss = check(sys.argv[1])
    if not iss:
        print('自查通过：没有排不满、溢出、出界、字太小的问题。'); sys.exit(0)
    print(f'自查发现 {len(iss)} 个问题：')
    for pg, what, fix in iss: print(f'  第 {pg} 页 · {what} → {fix}')
    sys.exit(1)
