"""检查运行环境，并补齐素材。用法：python3 tools/setup_env.py

做两件事，都不会修改系统：
1. 检查 Python 依赖是否齐全。缺了只打印安装命令，由用户或助手确认后自行运行，本脚本不会自动安装任何东西。
2. 补齐素材（字体、设计系统配图、风格菜单图）。技能商店的安装包有 3MB 上限，这些文件放在本项目的公开 GitHub 仓库
   （github.com/ludzhao/ppt-maker）里。脚本只从该仓库下载下面清单里列出的文件，
   只写入本技能自己的文件夹；每个文件下载后都要核对字节数和 SHA256，对不上就丢弃，所以拿到的一定是清单里这份内容。
   下载地址只有两类：jsDelivr 官方 CDN（转发同一个 GitHub 仓库，国内访问更稳）和 GitHub 官方 raw 地址。
   从 GitHub 克隆的完整版已经带有这些文件，会直接跳过下载。
"""
import hashlib, importlib, pathlib, sys, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
NEED = {'pptx': 'python-pptx>=1.0', 'lxml': 'lxml', 'PIL': 'Pillow', 'fontTools': 'fonttools'}

REPO = 'ludzhao/ppt-maker'
COMMIT = 'main'   # 内容由下面清单里的 SHA256 锁定，仓库更新了也只接受清单里这一份
SOURCES = [
    f'https://cdn.jsdelivr.net/gh/{REPO}@{COMMIT}/',
    f'https://fastly.jsdelivr.net/gh/{REPO}@{COMMIT}/',
    f'https://gcore.jsdelivr.net/gh/{REPO}@{COMMIT}/',
    f'https://raw.githubusercontent.com/{REPO}/{COMMIT}/',
]

# 素材清单：相对路径 -> (字节数, SHA256)
ASSETS = {
    'assets/designs/candy/bubble.jpg': (82723, '2058b853be4b8586bf1e194d7ebe13691e502d684c7160ddad4279c0fd1e778d'),
    'assets/designs/candy/cursor.jpg': (109615, '520b06484d5c511b6e097aa858dd08f95a7b36ebe4c6d750525383f0616235b6'),
    'assets/designs/candy/grad.jpg': (38952, '68205a44b81cc5635a9c43ac035c39b9af3742d55c22a678d3d8c861d5d85d54'),
    'assets/designs/candy/robot.jpg': (103342, '0bfe5223068bb02a38f6448f88761626c45923dcb78bfbebb4fb74e70558bbaa'),
    'assets/designs/ember/cluster.jpg': (62852, '7dbcfb872b10d7bc07394b749803e8df56873f9bfac97095b9f336170c44fecb'),
    'assets/designs/ember/hero.jpg': (83659, '7031a1bef1480e9ce6579ecbcb784cd8b5692003402a02895936ea25dbfdc02e'),
    'assets/designs/ember/ring.jpg': (72093, '0566e48ef8bfed946369a6fb4c265e88c6c0f40ce58bbea16e4c2ee15c49374a'),
    'assets/designs/folio/crowd.jpg': (246175, '43be6b7c359ed8b78d215dcdbeb8c8985b091d9bea8c6be387bbc435d1700039'),
    'assets/designs/folio/hands.jpg': (113839, 'fbee9346a956b4a1d9eb3c2ab61bbdc33bd0fbc2c4b30c166093c06721db671c'),
    'assets/designs/folio/meeting.jpg': (146844, 'a726351791c5026c027f928cfbc18288317186f7ca92855d8f3f304aff89ed86'),
    'assets/designs/folio/night.jpg': (106526, 'a4909732e3add8e742377478e412cb47c4b16f6c21269eee8cc18c98f404c9fd'),
    'assets/designs/folio/window.jpg': (120085, '7cbe58066868b792c27d1147e1c8bf437fd87843df1c654afdb9442a2f14d36c'),
    'examples/menu/bento_01.jpg': (22088, 'd98548e9f3b3544174b1a8a5f4c0b28701925201cf857fe8bbb860a5d39fa0ec'),
    'examples/menu/bento_02.jpg': (23704, 'c020bfd8ef3e7b01d8a40e81e3b538b3e6a525eafcd07d7e7369d494efcb18e0'),
    'examples/menu/bento_04.jpg': (17516, '7934a3895d42755992dc8adc07b7c297eac579a8e4b587ed2edf486d7b39d77c'),
    'examples/menu/bento_09.jpg': (19062, '6211488238037c4ee1ac49cb5cab53854ca1bb7661ece536af70729b1d1dd961'),
    'examples/menu/brutal_01.jpg': (41432, 'ee08096e18e3e124152586260e1bcd4ab223cf1ecac20412d3ec292a1e6d926a'),
    'examples/menu/brutal_02.jpg': (37545, '275b4bef73b731dd35ccb54a11b3437744b34a398b968e363f29aa5ce611f7c5'),
    'examples/menu/brutal_04.jpg': (34907, '30f94f76b9e8aae0556aa78c4a571a8771686b59312953ed94e1524fff954abc'),
    'examples/menu/brutal_09.jpg': (33761, 'b1e0c4a26dd18bf0c4bca86ce8694b7e3376a27ce601ad46fecef70c31f28559'),
    'examples/menu/candy_01.jpg': (33434, 'ed407a7180bcd8a2e79d87386f6402ed843f24afb0639924b43290954c84b4a9'),
    'examples/menu/candy_02.jpg': (21174, '51402fbbd73314afe29e71f2b0c57548025ffb3b79673db608c2565a86814802'),
    'examples/menu/candy_04.jpg': (19589, '05802610b830009fdc9bc7c2cdc04d533e070e7e4e490417a462ab8505a11631'),
    'examples/menu/candy_09.jpg': (20704, '196ac36a8f1f79c66183c5fbaa65c1187f819015fa8e5cdd21d193a82d268bfe'),
    'examples/menu/consulting_01.jpg': (19794, '3932222d6ced3938e2463f1651f2fe9646191f91dc6e80c20ecb2878eaf7c342'),
    'examples/menu/consulting_02.jpg': (28043, '541fdc6d1b568afcfdd9249e1eda3862cadd66f40ef61b5ab7aea02846280775'),
    'examples/menu/consulting_04.jpg': (20845, 'a54489a5b58e39939ca8e560c5556ea65344ae0164d495e0626c3d6ccd9be5d7'),
    'examples/menu/consulting_09.jpg': (21214, '41e644b5a9f7bc58319eef14f1ba97b1a9462645da9ec109d47be6f2565b2900'),
    'examples/menu/economist_01.jpg': (30500, '0d887a2b9037c5dc9831dc7cdd17d65ccee4c6ec8cadc630deae2c31d6a7705d'),
    'examples/menu/economist_02.jpg': (31371, '0de5996da6d91692a5ded5adc33b7c34ef5b21dcfbb9a2993b3b8b36a37f312c'),
    'examples/menu/economist_04.jpg': (27610, 'f1d245e423e6cd87b441161914728d5924f408fa3004e52663503ab50fd86884'),
    'examples/menu/economist_09.jpg': (25973, 'c78ed2b8c62a913b553cd83238fc93a115da2f162be69bbb165bdbe480b9e3f3'),
    'examples/menu/ember_01.jpg': (29318, '8d84440fe3f6564bf9f31a34e354b42f336875c10efd45ed5a94c2aad398ed0a'),
    'examples/menu/ember_02.jpg': (19052, '921ca4590775ce578506a2f6c50c2a4c55be7aa2de003cde5f750becaba530d8'),
    'examples/menu/ember_04.jpg': (14653, '581b024904cace31c20490bf0d802ad1c82d258b4d5e5f390667faee8df05555'),
    'examples/menu/ember_09.jpg': (18104, '704f509191368d2344ea5c4bf0b81e314da0af648f921643356c63b7dc86c626'),
    'examples/menu/folio_01.jpg': (22076, '3d3c7ef6badef00f60d57bad28678001d3ad42e0d4d188c92e3d50100b302fe8'),
    'examples/menu/folio_02.jpg': (20345, 'e385cc775981be820bbcb249f8eb21f09c604a3a8529665cbeba6a01155364f4'),
    'examples/menu/folio_04.jpg': (18113, 'aab1d756308e8aca217409c994800ece598ffa112c4c1a6f9ed945c45207854d'),
    'examples/menu/folio_09.jpg': (14098, '717b755e97b0e1ccd19251cb45af200924fba4ae24209d4c39464f79399c3466'),
    'examples/menu/ink_01.jpg': (27815, '26c331ec1da6f8400a0395605cbd610913dae5638b6e34192ac9291dc23633f6'),
    'examples/menu/ink_02.jpg': (28959, '32e2e7d7bc8638cb017809d2e878ebfe3989d6d9aa4af75f3d1321c9e377152f'),
    'examples/menu/ink_04.jpg': (25819, '4e4adb3d2260e5adad59aeaf85768de50befd029af4ec3bd6576992f5b07de33'),
    'examples/menu/ink_09.jpg': (26536, '136eb49a61298932df0e6802490663fd729e452de4a64cf3eabbd0859fd3d33e'),
    'examples/menu/keynote_01.jpg': (24852, '2b29e14a56d99d6eb4bea80d19142d603abddfc4c69abd1f91df6d84f487a0f6'),
    'examples/menu/keynote_02.jpg': (25198, '59342e376bcf108210c5bc31d5c6b97efb31333c6d9362302e0a213e0f256a0c'),
    'examples/menu/keynote_04.jpg': (19807, '8c233d7b8668a0622992de8acebd853463e4a39d502af970ff7e57d7851f8c32'),
    'examples/menu/keynote_09.jpg': (20413, '6130f0f988cc01af89f58d00cbc3dde6e5149008a7ec7f935681f89ad1591ca1'),
    'examples/menu/nightdata_01.jpg': (24404, '8ec10f89a85d3724f414c50874eba40406eb113f9f5d3a91e22e963f9246c4d6'),
    'examples/menu/nightdata_02.jpg': (23055, '1fc9e5e77444101ffa7d6d687d84969f0318b194ee231c071ea90339c802012c'),
    'examples/menu/nightdata_04.jpg': (18795, '542257dbd14db8c798cef2cef598e3811cb906fad29b0501b8e4b292363b9742'),
    'examples/menu/nightdata_09.jpg': (20090, '3aeba0aa00760c7fac0bca6afba7669c08d6621ce0f474722d1662e9592473d9'),
    'examples/menu/swiss_01.jpg': (25007, '0cf134759bd1f2bf917be15e55eda6ddd7db7d159962af195d76e7228365c45b'),
    'examples/menu/swiss_02.jpg': (28653, 'cc802dc74e128e944e40fde278acec8b00910c7a22ba0dfd535a4926a905fb0b'),
    'examples/menu/swiss_04.jpg': (24648, '7a28eed429a1a77bd29eeee15bbd6d319dacbeaf6a3f186b82bae04f84117f97'),
    'examples/menu/swiss_09.jpg': (26652, '66c03bc3b8fab911919a4190c90d17e377c29cc705b795080e78ebf76c7aacdf'),
    'examples/menu/terminal_01.jpg': (23807, '009d945fdfb9703060f5678ae396f5700a0de553a5479d740a86aaf48bd6cbf3'),
    'examples/menu/terminal_02.jpg': (27888, '88aa9447a72fe9ceff3e3cf27b4a7198f149b70d50b4a93ef2d2483b8c0b240f'),
    'examples/menu/terminal_04.jpg': (20067, '46a70a421f935c57b12507bfdd17b3ed30339e4220503430c1af398015409ed0'),
    'examples/menu/terminal_09.jpg': (22950, 'f645a3468bc3920522114801672241ffcc8008fc0cd0014508465fa41ed7fecb'),
    'examples/menu/volt_01.jpg': (22390, '245eecb8141208e55a012d5a4689dcc243e1bd5bc05e07b30aa4550805c3f6b3'),
    'examples/menu/volt_02.jpg': (21835, 'eee2d647889d5a17b17ee4ab784610592c54b5041f98216d835aa80e83bdc603'),
    'examples/menu/volt_04.jpg': (18371, 'b571df3eb4a27a748b8245419824d3b538f5f1aab07ad43060adcf78b42736b9'),
    'examples/menu/volt_09.jpg': (25384, 'a263bf5634e19ebe714214a415af6fa0ae88ddb41a1b7920e5b0f408417ea3d3'),
    'examples/设计系统总览.jpg': (429557, '6317f1f8d620ef3e85273ea3861e9eb7b12836a44aa8f108e1a5ee358632c148'),
    'examples/风格总览.png': (1126040, '34ed1b1e7e31073e1945a637f053f059c1aeae82e080ba5a36061750b10bf81e'),
    'examples/风格菜单.png': (1746694, 'd758dd96e2a8d853e0db50a7d63a1f4b9ec639300888135a1cf367675144c598'),
    'fonts/pack/Inter[opsz,wght].ttf': (876576, '29160a80ff49ddcab2c97711247e08b1fab27a484a329ce8b813d820dc559031'),
    'fonts/pack/LXGWWenKai-bold.ttf': (3492360, '3e9e75aaf990d67797e241d1bfefc03ebc49c8fec3939617737c707b04731b31'),
    'fonts/pack/LXGWWenKai-regular.ttf': (3488248, 'bdbc04b6bffc80e5114fc05817d85760ace8e243f877ddea679fc5d0988179d7'),
    'fonts/pack/NotoSansSC-bold.ttf': (2295640, '2254508136438fbeabeb921afb9cba2477ffc2ac94b21f7e6aa76c0150ac4c80'),
    'fonts/pack/NotoSansSC-regular.ttf': (2296380, 'f71e9dd8584870528d6d7e5c49f6cb257de74200ec96a53def77ee45292497c5'),
    'fonts/pack/NotoSansSCBlack-regular.ttf': (2293900, 'a8357e21649618712b5957da5863a6d336446d3bf5e186f13f398dd047a8d091'),
    'fonts/pack/NotoSansSCLight-bold.ttf': (2432412, '41324b073dd8580a2704eee58101ec66d385fe8b5681f1e38fcf9d5fa1b4b800'),
    'fonts/pack/NotoSansSCLight-regular.ttf': (2434672, '9a0b3525420140b35b5741adbb39b3bf257d9d98abbb3bf2146cf666cfb6a779'),
    'fonts/pack/NotoSerifSC-bold.ttf': (3181564, '6f7f13bcde6aea75392ee03fc98a9662266eb9845042ca0c03ded5e9935f3bb9'),
    'fonts/pack/NotoSerifSC-regular.ttf': (3181748, 'a7d9ccb08495e04f6030b990acd5e71b86948d9d3b2b8bd9a8034598fdfa18d2'),
    'fonts/pack/NotoSerifSCBlack-regular.ttf': (3377672, '7f5290b22b7bec6ef00998e4aa825ad90e6c69f67b6648bea78537d34410b14b'),
    'fonts/pack/PlayfairDisplay[wght].ttf': (300724, 'c40f2293766a503bc70cce9e512ef844a4ccb7cbcde792fe2ea31d191917d8d6'),
    'fonts/pack/SmileySans-regular.ttf': (1946760, '411070db6a5b70c5ccef894f8aca4a2fcda46f82fa25fdc194a111c10ac96e67'),
    'fonts/pack/SpaceGrotesk[wght].ttf': (136676, 'acad6de1fc93436f5c0f1f4137751ef04f1aea3063e7036535970ffcfbd79f72'),
}


def _ok(path, size, digest):
    return path.exists() and path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest


def _download(rel, size, digest):
    for base in SOURCES:
        try:
            req = urllib.request.Request(base + urllib.parse.quote(rel), headers={'User-Agent': 'ppt-maker-setup'})
            data = urllib.request.urlopen(req, timeout=60).read(size + 1)
        except Exception:
            continue
        if len(data) == size and hashlib.sha256(data).hexdigest() == digest:
            dst = ROOT / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
            return True
    return False


def ensure_assets():
    todo = [(r, n, h) for r, (n, h) in ASSETS.items() if not _ok(ROOT / r, n, h)]
    if not todo:
        return True
    print(f'正在补齐素材：{len(todo)} 个文件，约 {sum(n for _, n, _ in todo) / 1048576:.0f}MB（来源：GitHub 仓库 {REPO}，逐个校验 SHA256）……')
    failed = []
    for i, (r, n, h) in enumerate(todo, 1):
        if not _download(r, n, h):
            failed.append(r)
        if i % 10 == 0 or i == len(todo):
            print(f'  {i}/{len(todo)}')
    if failed:
        print(f'有 {len(failed)} 个素材没有下载成功（如 {failed[0]}），多半是网络波动，稍后再运行一次本命令即可。')
        return False
    print('素材已就绪。')
    return True


def missing():
    out = []
    for mod, pkg in NEED.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            out.append(pkg)
    return out


def main():
    assets_ok = ensure_assets()
    lack = missing()
    if lack:
        print('缺少 Python 依赖：', ' '.join(lack))
        print('请运行下面的命令安装（国内用清华源；不在国内可去掉 -i 及后面的地址）：')
        print(f'  {sys.executable} -m pip install {" ".join(repr(p) if ">" in p else p for p in lack)} -i https://pypi.tuna.tsinghua.edu.cn/simple')
        return 1
    if not assets_ok:
        return 1
    print('依赖齐全，可以生成 PPT。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
