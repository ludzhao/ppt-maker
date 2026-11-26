"""检查并安装依赖。用法：python tools/setup_env.py
缺什么装什么；pip 默认源失败时自动换清华镜像。"""
import importlib, subprocess, sys

NEED = {'pptx': 'python-pptx>=1.0', 'lxml': 'lxml', 'PIL': 'Pillow', 'fontTools': 'fonttools'}
MIRRORS = [None, 'https://pypi.tuna.tsinghua.edu.cn/simple', 'https://mirrors.aliyun.com/pypi/simple']


def missing():
    out = []
    for mod, pkg in NEED.items():
        try: importlib.import_module(mod)
        except ImportError: out.append(pkg)
    return out


def main():
    lack = missing()
    if not lack:
        print('依赖齐全，可以生成 PPT。'); return 0
    print('需要安装：', ' '.join(lack))
    for m in MIRRORS:
        cmd = [sys.executable, '-m', 'pip', 'install', '--quiet', *lack] + (['-i', m] if m else [])
        if subprocess.call(cmd) == 0 and not missing():
            print('安装完成。'); return 0
        cmd.insert(4, '--user')
        if subprocess.call(cmd) == 0 and not missing():
            print('安装完成（用户目录）。'); return 0
    print('安装失败，请把上面的报错发给用户。'); return 1


if __name__ == '__main__':
    sys.exit(main())
