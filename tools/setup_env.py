"""检查并安装依赖。用法：python tools/setup_env.py
缺什么装什么；pip 默认源失败时自动换清华镜像。"""
import importlib, subprocess, sys

NEED = {'pptx': 'python-pptx>=1.0', 'lxml': 'lxml', 'PIL': 'Pillow', 'fontTools': 'fonttools'}
PIP_MIRRORS = ['https://pypi.tuna.tsinghua.edu.cn/simple', 'https://mirrors.aliyun.com/pypi/simple', None]   # 国内源优先

# 大文件（字体、设计系统配图、风格菜单图）不放进技能商店的安装包，第一次运行时从 GitHub 仓库补齐。
# 从 GitHub 克隆的完整版已经有这些文件，会直接跳过。
# 镜像按国内可用性排列；运行时先测速，再按快慢顺序逐个尝试，下载后按文件大小校验（防止代理返回错误页）。
_RAW = 'https://raw.githubusercontent.com/ludzhao/ppt-maker/main/'
MIRRORS = [
    'https://testingcf.jsdelivr.net/gh/ludzhao/ppt-maker@main/',
    'https://gcore.jsdelivr.net/gh/ludzhao/ppt-maker@main/',
    'https://fastly.jsdelivr.net/gh/ludzhao/ppt-maker@main/',
    'https://cdn.jsdelivr.net/gh/ludzhao/ppt-maker@main/',
    'https://gh-proxy.com/' + _RAW,
    'https://ghfast.top/' + _RAW,
    'https://ghproxy.net/' + _RAW,
    _RAW,
]
# 路径: 字节数
REMOTE_FILES = {
    'assets/designs/candy/bubble.jpg': 82723,
    'assets/designs/candy/cursor.jpg': 109615,
    'assets/designs/candy/grad.jpg': 38952,
    'assets/designs/candy/robot.jpg': 103342,
    'assets/designs/ember/cluster.jpg': 62852,
    'assets/designs/ember/hero.jpg': 83659,
    'assets/designs/ember/ring.jpg': 72093,
    'assets/designs/folio/crowd.jpg': 246175,
    'assets/designs/folio/hands.jpg': 113839,
    'assets/designs/folio/meeting.jpg': 146844,
    'assets/designs/folio/night.jpg': 106526,
    'assets/designs/folio/window.jpg': 120085,
    'examples/menu/bento_01.jpg': 22088,
    'examples/menu/bento_02.jpg': 23704,
    'examples/menu/bento_04.jpg': 17516,
    'examples/menu/bento_09.jpg': 19062,
    'examples/menu/brutal_01.jpg': 41432,
    'examples/menu/brutal_02.jpg': 37545,
    'examples/menu/brutal_04.jpg': 34907,
    'examples/menu/brutal_09.jpg': 33761,
    'examples/menu/candy_01.jpg': 33434,
    'examples/menu/candy_02.jpg': 21174,
    'examples/menu/candy_04.jpg': 19589,
    'examples/menu/candy_09.jpg': 20704,
    'examples/menu/consulting_01.jpg': 19794,
    'examples/menu/consulting_02.jpg': 28043,
    'examples/menu/consulting_04.jpg': 20845,
    'examples/menu/consulting_09.jpg': 21214,
    'examples/menu/economist_01.jpg': 30500,
    'examples/menu/economist_02.jpg': 31371,
    'examples/menu/economist_04.jpg': 27610,
    'examples/menu/economist_09.jpg': 25973,
    'examples/menu/ember_01.jpg': 29318,
    'examples/menu/ember_02.jpg': 19052,
    'examples/menu/ember_04.jpg': 14653,
    'examples/menu/ember_09.jpg': 18104,
    'examples/menu/folio_01.jpg': 22076,
    'examples/menu/folio_02.jpg': 20345,
    'examples/menu/folio_04.jpg': 18113,
    'examples/menu/folio_09.jpg': 14098,
    'examples/menu/ink_01.jpg': 27815,
    'examples/menu/ink_02.jpg': 28959,
    'examples/menu/ink_04.jpg': 25819,
    'examples/menu/ink_09.jpg': 26536,
    'examples/menu/keynote_01.jpg': 24852,
    'examples/menu/keynote_02.jpg': 25198,
    'examples/menu/keynote_04.jpg': 19807,
    'examples/menu/keynote_09.jpg': 20413,
    'examples/menu/nightdata_01.jpg': 24404,
    'examples/menu/nightdata_02.jpg': 23055,
    'examples/menu/nightdata_04.jpg': 18795,
    'examples/menu/nightdata_09.jpg': 20090,
    'examples/menu/swiss_01.jpg': 25007,
    'examples/menu/swiss_02.jpg': 28653,
    'examples/menu/swiss_04.jpg': 24648,
    'examples/menu/swiss_09.jpg': 26652,
    'examples/menu/terminal_01.jpg': 23807,
    'examples/menu/terminal_02.jpg': 27888,
    'examples/menu/terminal_04.jpg': 20067,
    'examples/menu/terminal_09.jpg': 22950,
    'examples/menu/volt_01.jpg': 22390,
    'examples/menu/volt_02.jpg': 21835,
    'examples/menu/volt_04.jpg': 18371,
    'examples/menu/volt_09.jpg': 25384,
    'examples/设计系统总览.jpg': 429557,
    'examples/风格总览.png': 1126040,
    'examples/风格菜单.png': 1746694,
    'fonts/pack/Inter[opsz,wght].ttf': 876576,
    'fonts/pack/LXGWWenKai-bold.ttf': 3492360,
    'fonts/pack/LXGWWenKai-regular.ttf': 3488248,
    'fonts/pack/NotoSansSC-bold.ttf': 2295640,
    'fonts/pack/NotoSansSC-regular.ttf': 2296380,
    'fonts/pack/NotoSansSCBlack-regular.ttf': 2293900,
    'fonts/pack/NotoSerifSC-bold.ttf': 3181564,
    'fonts/pack/NotoSerifSC-regular.ttf': 3181748,
    'fonts/pack/PlayfairDisplay[wght].ttf': 300724,
    'fonts/pack/SmileySans-regular.ttf': 1946760,
    'fonts/pack/SpaceGrotesk[wght].ttf': 136676,
}


def _get(url, timeout):
    import urllib.request
    req = urllib.request.Request(url, headers={'User-Agent': 'ppt-maker/1.0'})
    return urllib.request.urlopen(req, timeout=timeout).read()


def _rank_mirrors():
    """用最小的一个文件给每个镜像测速，能用的按快慢排序。"""
    import time, urllib.parse
    from concurrent.futures import ThreadPoolExecutor
    probe = min(REMOTE_FILES, key=REMOTE_FILES.get)
    def t(m):
        t0 = time.time()
        try:
            return time.time() - t0 if len(_get(m + urllib.parse.quote(probe), 8)) == REMOTE_FILES[probe] else None
        except Exception:
            return None
    with ThreadPoolExecutor(len(MIRRORS)) as ex: res = list(ex.map(t, MIRRORS))
    ok = sorted((r, m) for r, m in zip(res, MIRRORS) if r is not None)
    return [m for _, m in ok] or MIRRORS


def ensure_assets():
    import pathlib, urllib.parse
    from concurrent.futures import ThreadPoolExecutor
    root = pathlib.Path(__file__).resolve().parent.parent
    todo = [f for f, n in REMOTE_FILES.items() if not ((root / f).exists() and (root / f).stat().st_size == n)]
    if not todo: return True
    mb = sum(REMOTE_FILES[f] for f in todo) / 1048576
    print(f'首次使用，正在下载字体和配图（{len(todo)} 个文件，约 {mb:.0f}MB，一般 1 分钟内完成）……')
    mirrors = _rank_mirrors()
    def one(f):
        dst = root / f; dst.parent.mkdir(parents=True, exist_ok=True)
        for m in mirrors:
            try:
                data = _get(m + urllib.parse.quote(f), 60)
                if len(data) != REMOTE_FILES[f]: continue
                tmp = dst.with_name(dst.name + '.part'); tmp.write_bytes(data); tmp.replace(dst)
                return None
            except Exception:
                continue
        return f
    with ThreadPoolExecutor(6) as ex: failed = [f for f in ex.map(one, todo) if f]
    if failed:
        print(f'有 {len(failed)} 个素材没下载成功（如 {failed[0]}），多半是网络波动，可以再运行一次本命令。'
              '不影响生成：缺字体时由系统字体代替；缺配图时，folio / ember / candy 风格请换成别的风格。')
        return False
    print('素材已就绪。')
    return True


def missing():
    out = []
    for mod, pkg in NEED.items():
        try: importlib.import_module(mod)
        except ImportError: out.append(pkg)
    return out


def main():
    ensure_assets()
    lack = missing()
    if not lack:
        print('依赖齐全，可以生成 PPT。'); return 0
    print('需要安装：', ' '.join(lack))
    for m in PIP_MIRRORS:
        cmd = [sys.executable, '-m', 'pip', 'install', '--quiet', *lack] + (['-i', m] if m else [])
        if subprocess.call(cmd) == 0 and not missing():
            print('安装完成。'); return 0
        cmd.insert(4, '--user')
        if subprocess.call(cmd) == 0 and not missing():
            print('安装完成（用户目录）。'); return 0
    print('安装失败，请把上面的报错发给用户。'); return 1


if __name__ == '__main__':
    sys.exit(main())
