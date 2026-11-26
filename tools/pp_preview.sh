#!/bin/zsh
# PowerPoint 预览：导出 PDF -> 逐页 PNG + 总览图；加 --video 再导出带动画的 MP4 并抽帧
# 注意：需要在 Claude Code 沙箱外运行（PowerPoint 需要访问该文件夹）
set -e
here=${0:A:h}; f=${1:A}; d="${f:r}_pp"
rm -rf "$d"; mkdir -p "$d"
X="$here/../out/_pp"; mkdir -p "$X"; rm -f "$X/${f:t:r}.pdf"
osascript -e "tell application \"Microsoft PowerPoint\" to close (presentation \"${f:t}\") saving no" >/dev/null 2>&1 || true
open -a "Microsoft PowerPoint" "$f"
osascript "$here/pp_export.applescript" "${f:t}" "$X/${f:t:r}.pdf" pdf
mv "$X/${f:t:r}.pdf" "$d/deck.pdf"
"${PY:-$( [ -x $here/../.venv/bin/python ] && echo $here/../.venv/bin/python || echo python3)}" - "$d" <<'PY'
import sys, pypdfium2 as pdfium
from PIL import Image
d = sys.argv[1]; pdf = pdfium.PdfDocument(d + '/deck.pdf'); ims = []
for i, page in enumerate(pdf):
    im = page.render(scale=1.5).to_pil().convert('RGB'); im.save(f'{d}/slide{i+1:02d}.png'); ims.append(im)
w = 800; h = int(ims[0].height * w / ims[0].width); rows = (len(ims) + 1) // 2
sheet = Image.new('RGB', (w * 2 + 30, (h + 20) * rows + 10), '#777')
for i, im in enumerate(ims): sheet.paste(im.resize((w, h)), (10 + (i % 2) * (w + 10), 10 + (i // 2) * (h + 20)))
sheet.save(d + '/sheet.png'); print(d + '/sheet.png', len(ims), 'pages')
PY
if [ "$2" = "--video" ]; then
  open -a "Microsoft PowerPoint" "$f"
  osascript "$here/pp_export.applescript" "${f:t}" "$X/${f:t:r}.mp4" mp4
  prev=-1; until s=$(stat -f %z "$X/${f:t:r}.mp4" 2>/dev/null) && [ "$s" -gt 0 ] && [ "$s" = "$prev" ]; do prev=$s; sleep 10; done
  mv "$X/${f:t:r}.mp4" "$d/deck.mp4"
  osascript -e "tell application \"Microsoft PowerPoint\" to close (presentation \"${f:t}\") saving no" || true
  echo "$d/deck.mp4"
fi
