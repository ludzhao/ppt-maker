"""风格菜单：给用户看每种风格长什么样，再让用户按编号选。

用法：python3 SKILL_DIR/tools/style_menu.py          打印编号清单 + 菜单图路径，并在浏览器打开网页版菜单
      python3 SKILL_DIR/tools/style_menu.py --build  （维护者用）重新生成 examples/风格菜单.png / .html
"""
import sys, pathlib, webbrowser

ROOT = pathlib.Path(__file__).resolve().parent.parent
EX = ROOT / 'examples'

MENU = [  # 编号, style, 中文名, 一句话特点, 适合
    (1, 'folio', '黑白杂志', '黑白纪实摄影 + 衬线大标题，一个词变斜体绿色', '年终汇报、品牌故事、想显得有格调'),
    (2, 'ember', '暗黑董事会', '黑底 + 橙色 3D 球体，粗黑大标题', '融资路演、科技发布、董事会汇报'),
    (3, 'candy', 'Y2K 糖果', '粉紫渐变 + 3D 糖果物件，竖排标题', '年轻受众、活动策划、课程分享'),
    (4, 'volt', '深色荧光绿', '圆角深色面板 + 荧光绿，阶梯流程、仪表盘', '数据复盘、产品/运营周报、技术分享'),
    (5, 'consulting', '咨询报告', '白底单色强调，发丝线，信息密度高', '正式工作汇报（默认）'),
    (6, 'economist', '经济学人', '米色纸张 + 衬线标题', '研究报告、行业分析'),
    (7, 'nightdata', '暗夜数据', '近黑底 + 橙色超大数字', '数据驱动的分享'),
    (8, 'keynote', '深蓝发布会', '深蓝渐变 + 玻璃卡片', '发布会、对外宣讲'),
    (9, 'swiss', '瑞士网格', '白底大红色块 + 黑体大字', '设计感强的汇报'),
    (10, 'bento', '便当格', '浅灰底 + 大圆角白格子', '产品介绍'),
    (11, 'brutal', '新粗野', '米白点阵 + 黑粗边硬阴影', '创意提案、年轻品牌'),
    (12, 'ink', '国风水墨', '宣纸 + 竖排宋体 + 朱红印章', '文化、传统行业'),
    (13, 'terminal', '极客终端', '黑底荧光绿命令行', '技术分享、开发者'),
]
PAGES = [1, 2, 4, 9]   # 封面 / 数字页 / 图表页 / 流程页（缩略图在 examples/menu/<style>_<页>.jpg）


def build():
    from PIL import Image, ImageDraw, ImageFont
    fb = ImageFont.truetype(str(ROOT / 'fonts/pack/NotoSansSC-bold.ttf'), 40)
    fm = ImageFont.truetype(str(ROOT / 'fonts/pack/NotoSansSC-bold.ttf'), 26)
    fr = ImageFont.truetype(str(ROOT / 'fonts/pack/NotoSansSC-regular.ttf'), 22)
    fnum = ImageFont.truetype(str(ROOT / 'fonts/pack/NotoSansSCBlack-regular.ttf'), 64)
    Wd = 1900; tw, th = 400, 225; lw = 440
    rows_a = MENU[:4]; rows_b = MENU[4:]
    Hh = 130 + len(rows_a) * (th + 40) + 110 + ((len(rows_b) + 2) // 3) * 420 + 40
    im = Image.new('RGB', (Wd, Hh), '#F4F3EF'); d = ImageDraw.Draw(im)
    d.text((40, 36), '选一个风格，回复编号即可（内容不变，随时可以换）', fill='#16181D', font=fb)
    y = 130
    d.text((40, y - 6), '推荐 · 设计系统（每种页型都有独立构图）', fill='#2E9E4F', font=fm); y += 46
    for n, st, zh, desc, fit in rows_a:
        d.rounded_rectangle((30, y - 10, Wd - 30, y + th + 20), 18, fill='white')
        d.text((60, y + 10), str(n), fill='#16181D', font=fnum)
        d.text((150, y + 18), zh, fill='#16181D', font=fb)
        d.text((150, y + 74), st, fill='#8A8F98', font=fr)
        import textwrap
        txt = '\n'.join(textwrap.wrap(desc, 17) + textwrap.wrap('适合：' + fit, 17))
        d.multiline_text((60, y + 105), txt, fill='#4B5257', font=fr, spacing=6)
        for k, p in enumerate(PAGES[:3]):
            t = Image.open(EX / 'menu' / f'{st}_{p:02d}.jpg').resize((tw, th))
            im.paste(t, (lw + 40 + k * (tw + 20), y + 5))
        y += th + 40
    y += 20
    d.text((40, y), '经典换色风格（版式共用一套骨架，适合保守场合）', fill='#8A8F98', font=fm); y += 50
    cw = (Wd - 80) // 3; RH = int((cw - 30) * 9 / 16) + 70
    for i, (n, st, zh, desc, fit) in enumerate(rows_b):
        x = 40 + (i % 3) * cw; yy = y + (i // 3) * RH
        t = Image.open(EX / 'menu' / f'{st}_01.jpg').resize((cw - 30, int((cw - 30) * 9 / 16)))
        im.paste(t, (x, yy))
        d.text((x, yy + t.height + 10), f'{n}  {zh}', fill='#16181D', font=fm)
        d.text((x + 175, yy + t.height + 14), desc, fill='#8A8F98', font=fr)
    im = im.crop((0, 0, Wd, y + ((len(rows_b) + 2) // 3) * RH + 10))
    im.save(EX / '风格菜单.png', optimize=True)

    cards = []
    for n, st, zh, desc, fit in MENU:
        imgs = ''.join(f'<img src="menu/{st}_{p:02d}.jpg" onclick="z(this)">' for p in PAGES)
        tag = '推荐' if n <= 4 else '经典'
        cards.append(f'<section class="{"rec" if n <= 4 else ""}"><h2><b>{n}</b>{zh}<small>{st} · {tag}</small></h2>'
                     f'<p>{desc}<br><span>适合：{fit}</span></p><div class="g">{imgs}</div></section>')
    html = f'''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PPT 风格菜单</title><style>
body{{margin:0;background:#F4F3EF;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;color:#16181D}}
header{{padding:28px 32px 8px}} h1{{margin:0;font-size:26px}} header p{{color:#6B6F76;margin:6px 0 0}}
main{{padding:16px 32px 40px;display:grid;gap:18px}}
section{{background:#fff;border-radius:16px;padding:18px 22px}} section.rec{{outline:3px solid #2E9E4F}}
h2{{margin:0;font-size:22px;display:flex;align-items:baseline;gap:12px}} h2 b{{font-size:30px}} h2 small{{color:#8A8F98;font-size:14px;font-weight:400}}
p{{margin:6px 0 12px;color:#4B5257}} p span{{color:#8A8F98}}
.g{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}} .g img{{width:100%;border-radius:8px;cursor:zoom-in;box-shadow:0 4px 12px rgba(0,0,0,.08)}}
#z{{position:fixed;inset:0;background:rgba(0,0,0,.85);display:none;align-items:center;justify-content:center}} #z img{{max-width:92vw;max-height:92vh}}
@media(max-width:700px){{.g{{grid-template-columns:repeat(2,1fr)}}}}
</style><header><h1>选一个风格，回复编号即可</h1><p>同一份内容在 13 种风格下的样子。绿框是推荐的 4 套设计系统；点图片可放大。</p></header>
<main>{"".join(cards)}</main><div id="z" onclick="this.style.display='none'"><img></div>
<script>function z(i){{const b=document.getElementById('z');b.querySelector('img').src=i.src;b.style.display='flex'}}</script></html>'''
    (EX / '风格菜单.html').write_text(html, encoding='utf-8')
    print('已生成', EX / '风格菜单.png', EX / '风格菜单.html')


def show():
    print('风格菜单（回复编号即可）：')
    for n, st, zh, desc, fit in MENU:
        print(f'  {n:>2}. {zh}（{st}）{"【推荐】" if n <= 4 else ""}：{desc}；适合 {fit}')
    print('\n菜单图：', EX / '风格菜单.png')
    html = EX / '风格菜单.html'
    print('网页版（可放大看）：', html)
    try: webbrowser.open(html.as_uri())
    except Exception: pass


if __name__ == '__main__':
    build() if '--build' in sys.argv else show()
