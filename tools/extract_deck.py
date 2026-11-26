"""从本 skill 生成的 pptx 里取回稿件 JSON：python tools/extract_deck.py in.pptx deck.json"""
import sys, zipfile
with zipfile.ZipFile(sys.argv[1]) as z:
    n = [x for x in z.namelist() if x.endswith('ppt-maker/deck.json')]
    if not n: sys.exit('这个 pptx 里没有稿件（不是本 skill 生成的，或在别的软件里另存过）。请按页面内容重建稿件。')
    open(sys.argv[2], 'wb').write(z.read(n[0]))
print('已取回稿件：', sys.argv[2], '（图片路径是相对原稿件文件夹的，换了文件夹要检查图片还在不在）')
