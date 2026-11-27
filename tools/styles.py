"""9 种版面风格预设（从用户挑的 14 个参考提炼，见 references/审美规范.md）。

风格 = 配色 + 字体 + 卡片画法 + 背景 + 页框 + 照片调色。和 36 套 html-ppt 配色是两层：
deck.json 里写 "style": "consulting"，也可以再写 "theme" 覆盖配色。
字体写法："西文字体|中文字体"，例如 "Space Grotesk|Noto Sans SC"。
"""

STYLES = {
    # S1 咨询报告：A01 / A07 / B01 —— 白底、单一强调色、发丝线、信息密度高
    'consulting': {
        'label': '咨询报告',
        'palette': {'bg': 'F6F7F5', 'surface': 'FFFFFF', 'surface_2': 'EEF1EC', 'border': 'DADFD8', 'border_strong': '1B1F1C',
                    'text_1': '15181A', 'text_2': '4B5257', 'text_3': '8A9196', 'accent': '2E9B57', 'accent_2': '9BD64B',
                    'accent_3': '1B1F1C', 'accent_ink': 'FFFFFF', 'good': '2E9B57', 'bad': 'D64541',
                    'grad': ['2E9B57', '9BD64B'], 'dark': False, 'radius_px': 10},
        'fonts': {'title': 'Inter|Noto Sans SC', 'body': 'Inter|Noto Sans SC', 'num': 'Space Grotesk|Noto Sans SC',
                  'quote': 'LXGW WenKai'},
        'card': 'soft', 'bg': 'flat', 'frame': 'rule', 'eyebrow': 'tag', 'photo': 'mute', 'cover': 'report',
    },
    # S2 经济学人：B09 / B02 / B03 —— 奶油纸色、衬线标题、刊头双线
    'economist': {
        'label': '经济学人',
        'palette': {'bg': 'F6EEE2', 'surface': 'FBF6EE', 'surface_2': 'EFE4D4', 'border': 'D9CBB5', 'border_strong': '2A2522',
                    'text_1': '1E1B18', 'text_2': '4D453D', 'text_3': '8C8172', 'accent': '1F4E8C', 'accent_2': 'A3743F',
                    'accent_3': 'B23A2E', 'accent_ink': 'FFFFFF', 'good': '2F7D4F', 'bad': 'B23A2E',
                    'grad': ['1F4E8C', 'A3743F'], 'dark': False, 'radius_px': 2},
        'fonts': {'title': 'Playfair Display|Noto Serif SC', 'body': 'Inter|Noto Sans SC', 'num': 'Noto Serif SC',
                  'quote': 'Playfair Display|Noto Serif SC'},
        'card': 'hairline', 'bg': 'paper', 'frame': 'masthead', 'eyebrow': 'caps', 'photo': 'sepia', 'cover': 'report',
    },
    # S3 暗夜数据：A02 / A11 / B08 / A03 —— 近黑底、暖色聚光、单一亮色、超大数字
    'nightdata': {
        'label': '暗夜数据',
        'palette': {'bg': '0D0D0F', 'surface': '17171B', 'surface_2': '202026', 'border': '2C2C33', 'border_strong': 'F2F0EB',
                    'text_1': 'F2F0EB', 'text_2': 'B5B1A8', 'text_3': '77736C', 'accent': 'FF7A2F', 'accent_2': 'FFB36B',
                    'accent_3': '8C5A3C', 'accent_ink': '111111', 'good': '7FD67A', 'bad': 'FF5A4E',
                    'grad': ['FF7A2F', 'FFB36B'], 'dark': True, 'radius_px': 8},
        'fonts': {'title': 'Space Grotesk|Noto Sans SC', 'body': 'Inter|Noto Sans SC', 'num': 'Space Grotesk|Noto Sans SC',
                  'display': 'Smiley Sans', 'quote': 'LXGW WenKai'},
        'card': 'dark', 'bg': 'spotlight', 'frame': 'minimal', 'eyebrow': 'caps', 'photo': 'warm', 'cover': 'dark',
    },
    # S4 深蓝发布会：A09 / A10 / B04 / B07 —— 深蓝渐变、玻璃卡片、满版照片
    'keynote': {
        'label': '深蓝发布会',
        'palette': {'bg': '0A1742', 'surface': '14245E', 'surface_2': '1C2F72', 'border': '3A4C8F', 'border_strong': 'FFFFFF',
                    'text_1': 'F4F7FF', 'text_2': 'B9C4E8', 'text_3': '7F8CBA', 'accent': '4FE3F0', 'accent_2': '7AA2FF',
                    'accent_3': 'C9A6FF', 'accent_ink': '06102E', 'good': '5BE3A0', 'bad': 'FF6B7A',
                    'grad': ['2F5BFF', '4FE3F0'], 'dark': True, 'radius_px': 16},
        'fonts': {'title': 'Inter|Noto Sans SC', 'body': 'Inter|Noto Sans SC', 'num': 'Inter|Noto Sans SC',
                  'quote': 'Inter|Noto Sans SC'},
        'card': 'glass', 'bg': 'gradient', 'frame': 'none', 'eyebrow': 'caps', 'photo': 'blue', 'cover': 'photo',
    },
    # A 薄荷数据（设计系统，版式自带：tools/design_mint.py）：参考 Capitalo 金融报告
    'mint': {
        'label': '薄荷数据',
        'palette': {'bg': '1D2744', 'surface': '26325A', 'surface_2': '2E3B66', 'border': '3A4775', 'border_strong': 'FFFFFF',
                    'text_1': 'FFFFFF', 'text_2': 'C3C9DA', 'text_3': '8B93A7', 'accent': '74F0A4', 'accent_2': '6F9CCB',
                    'accent_3': 'F3F4F6', 'accent_ink': '18203A', 'good': '74F0A4', 'bad': 'FF7A7A',
                    'grad': ['74F0A4', '6F9CCB'], 'dark': True, 'radius_px': 4},
        'fonts': {'title': 'Noto Sans SC Light', 'body': 'Space Grotesk|Noto Sans SC', 'num': 'Space Grotesk Light|Noto Sans SC Light',
                  'quote': 'Noto Sans SC Light'},
        'card': 'dark', 'bg': 'flat', 'frame': 'minimal', 'eyebrow': 'caps', 'photo': 'mute', 'cover': 'dark',
        'design': 'mint',
    },
    # B 黑白杂志（设计系统：tools/design_folio.py）：参考 Laurel
    'folio': {
        'label': '黑白杂志',
        'palette': {'bg': '0C0C0C', 'surface': '161616', 'surface_2': '1E1E1E', 'border': '3A3936', 'border_strong': 'F2F0EB',
                    'text_1': 'F2F0EB', 'text_2': 'A7A39B', 'text_3': '7A7771', 'accent': 'A9C7A1', 'accent_2': 'E9C46A',
                    'accent_3': '5E5B56', 'accent_ink': '0C0C0C', 'good': 'A9C7A1', 'bad': 'E07A5F',
                    'grad': ['A9C7A1', 'E9C46A'], 'dark': True, 'radius_px': 0},
        'fonts': {'title': 'Playfair Display|Noto Serif SC', 'body': 'Inter|Noto Sans SC', 'num': 'Playfair Display|Noto Serif SC',
                  'quote': 'Playfair Display|Noto Serif SC'},
        'card': 'hairline', 'bg': 'flat', 'frame': 'minimal', 'eyebrow': 'caps', 'photo': 'natural', 'cover': 'dark', 'design': 'folio',
    },
    # C 暗黑董事会（设计系统：tools/design_ember.py）：参考 Pitch · Board Deck
    'ember': {
        'label': '暗黑董事会',
        'palette': {'bg': '0B0B0C', 'surface': '141416', 'surface_2': '1C1C1F', 'border': '2A2A2E', 'border_strong': 'F4F4F2',
                    'text_1': 'F4F4F2', 'text_2': '9A9AA0', 'text_3': '6A6A70', 'accent': 'FF6A1A', 'accent_2': 'FF9A5A',
                    'accent_3': '55555B', 'accent_ink': '0B0B0C', 'good': 'FF6A1A', 'bad': 'FF4D4D',
                    'grad': ['FF6A1A', 'FF9A5A'], 'dark': True, 'radius_px': 0},
        'fonts': {'title': 'Space Grotesk|Noto Sans SC Black', 'body': 'Inter|Noto Sans SC', 'num': 'Space Grotesk|Noto Sans SC',
                  'quote': 'Space Grotesk|Noto Sans SC Black'},
        'card': 'dark', 'bg': 'flat', 'frame': 'minimal', 'eyebrow': 'caps', 'photo': 'natural', 'cover': 'dark', 'design': 'ember',
    },
    # D Y2K 糖果（设计系统：tools/design_candy.py）：参考 Pitch · Lucid
    'candy': {
        'label': 'Y2K 糖果',
        'palette': {'bg': 'F3D9F0', 'surface': 'FFFFFF', 'surface_2': 'F6F2FF', 'border': 'E4DAFF', 'border_strong': '231942',
                    'text_1': '231942', 'text_2': '4A4066', 'text_3': '7D7395', 'accent': '7B5CFF', 'accent_2': 'FF5FA8',
                    'accent_3': 'FFC23C', 'accent_ink': 'FFFFFF', 'good': '7B5CFF', 'bad': 'FF5FA8',
                    'grad': ['7B5CFF', 'FF5FA8'], 'dark': False, 'radius_px': 24},
        'fonts': {'title': 'Smiley Sans', 'body': 'Space Grotesk|Noto Sans SC', 'num': 'Smiley Sans', 'quote': 'Smiley Sans'},
        'card': 'soft', 'bg': 'flat', 'frame': 'minimal', 'eyebrow': 'caps', 'photo': 'natural', 'cover': 'dark', 'design': 'candy',
    },
    # E 深色荧光绿（设计系统：tools/design_volt.py）：参考 Grid-Scale Battery / B.Forge
    'volt': {
        'label': '深色荧光绿',
        'palette': {'bg': '101311', 'surface': '1B201C', 'surface_2': '242B25', 'border': '2F3830', 'border_strong': 'B8F36B',
                    'text_1': 'F1F5EE', 'text_2': 'A9B3A6', 'text_3': '6F7A6C', 'accent': 'B8F36B', 'accent_2': 'DDF7C8',
                    'accent_3': '3F5A3A', 'accent_ink': '101311', 'good': 'B8F36B', 'bad': 'FF7A5C',
                    'grad': ['B8F36B', 'DDF7C8'], 'dark': True, 'radius_px': 20},
        'fonts': {'title': 'Space Grotesk|Noto Sans SC', 'body': 'Space Grotesk|Noto Sans SC', 'num': 'Space Grotesk|Noto Sans SC',
                  'quote': 'Space Grotesk|Noto Sans SC'},
        'card': 'dark', 'bg': 'flat', 'frame': 'minimal', 'eyebrow': 'caps', 'photo': 'natural', 'cover': 'dark', 'design': 'volt',
    },
    # S5 瑞士网格：白底、大红色块、黑体超大字、粗黑线，网格感强
    'swiss': {
        'label': '瑞士网格',
        'palette': {'bg': 'FFFFFF', 'surface': 'F4F4F2', 'surface_2': 'EAEAE6', 'border': 'D6D6D2', 'border_strong': '111111',
                    'text_1': '111111', 'text_2': '3C3C3C', 'text_3': '8A8A8A', 'accent': 'E3261F', 'accent_2': '111111',
                    'accent_3': 'F2A900', 'accent_ink': 'FFFFFF', 'good': '111111', 'bad': 'E3261F',
                    'grad': ['E3261F', 'F2A900'], 'dark': False, 'radius_px': 0},
        'fonts': {'title': 'Inter|Noto Sans SC Black', 'body': 'Inter|Noto Sans SC', 'num': 'Inter|Noto Sans SC Black',
                  'quote': 'Inter|Noto Sans SC Black'},
        'card': 'swiss', 'bg': 'grid', 'frame': 'swiss', 'eyebrow': 'num', 'photo': 'mute', 'cover': 'swiss',
        'section': 'swiss', 'quote': 'swiss', 'title_size': 34,
    },
    # S6 便当格：浅灰底、大圆角白色格子，像产品发布页
    'bento': {
        'label': '便当格',
        'palette': {'bg': 'ECECF1', 'surface': 'FFFFFF', 'surface_2': 'F5F5F8', 'border': 'DCDCE4', 'border_strong': '1D1D1F',
                    'text_1': '1D1D1F', 'text_2': '4A4A55', 'text_3': '8E8E99', 'accent': '5B4CF5', 'accent_2': 'FF8A3D',
                    'accent_3': '1FC2A7', 'accent_ink': 'FFFFFF', 'good': '1FA37E', 'bad': 'F0453A',
                    'grad': ['5B4CF5', 'B26BFF'], 'dark': False, 'radius_px': 24},
        'fonts': {'title': 'Inter|Noto Sans SC', 'body': 'Inter|Noto Sans SC', 'num': 'Inter|Noto Sans SC',
                  'quote': 'Inter|Noto Sans SC'},
        'card': 'tile', 'bg': 'flat', 'frame': 'minimal', 'eyebrow': 'pill', 'photo': 'natural', 'cover': 'bento',
        'section': 'bento', 'quote': 'bento',
    },
    # S7 新粗野：米白点阵底、黑粗边框、硬阴影、贴纸和荧光笔
    'brutal': {
        'label': '新粗野',
        'palette': {'bg': 'F4EFE4', 'surface': 'FFFFFF', 'surface_2': 'FFE66B', 'border': '111111', 'border_strong': '111111',
                    'text_1': '111111', 'text_2': '2E2E2E', 'text_3': '6B665C', 'accent': 'FF5A36', 'accent_2': '3D5AFE',
                    'accent_3': 'FFD83D', 'accent_ink': 'FFFFFF', 'good': '0E9F6E', 'bad': 'FF3B30',
                    'grad': ['FF5A36', 'FFD83D'], 'dark': False, 'radius_px': 0},
        'fonts': {'title': 'Smiley Sans', 'body': 'Inter|Noto Sans SC', 'num': 'Space Grotesk|Smiley Sans',
                  'display': 'Smiley Sans', 'quote': 'Smiley Sans'},
        'card': 'brutal', 'bg': 'dots', 'frame': 'brutal', 'eyebrow': 'block', 'photo': 'natural', 'cover': 'brutal',
        'section': 'brutal', 'quote': 'brutal', 'title_size': 36,
    },
    # S8 国风水墨：宣纸底、宋体、朱红印章、竖排大标题
    'ink': {
        'label': '国风水墨',
        'palette': {'bg': 'F2ECDF', 'surface': 'F8F4EA', 'surface_2': 'E9E0CE', 'border': 'D3C7AF', 'border_strong': '2B2620',
                    'text_1': '1C1915', 'text_2': '4A433A', 'text_3': '8C806C', 'accent': 'B5302A', 'accent_2': '3C5A52',
                    'accent_3': 'A88A5A', 'accent_ink': 'FFFFFF', 'good': '3C5A52', 'bad': 'B5302A',
                    'grad': ['B5302A', 'A88A5A'], 'dark': False, 'radius_px': 0},
        'fonts': {'title': 'Noto Serif SC Black', 'body': 'Noto Serif SC', 'num': 'Playfair Display|Noto Serif SC',
                  'display': 'Noto Serif SC Black', 'quote': 'LXGW WenKai'},
        'card': 'ink', 'bg': 'washi', 'frame': 'ink', 'eyebrow': 'seal', 'photo': 'sepia', 'cover': 'ink',
        'section': 'ink', 'quote': 'ink',
    },
    # S9 极客终端：黑底荧光绿、等宽感字体、命令行提示符
    'terminal': {
        'label': '极客终端',
        'palette': {'bg': '0A0F0C', 'surface': '101813', 'surface_2': '16221A', 'border': '24382B', 'border_strong': '39FF88',
                    'text_1': 'DDF7E3', 'text_2': '93B89D', 'text_3': '5E7D66', 'accent': '39FF88', 'accent_2': '29D3FF',
                    'accent_3': 'FFB000', 'accent_ink': '04140A', 'good': '39FF88', 'bad': 'FF5F56',
                    'grad': ['39FF88', '29D3FF'], 'dark': True, 'radius_px': 6},
        'fonts': {'title': 'Space Grotesk|Noto Sans SC', 'body': 'Space Grotesk|Noto Sans SC', 'num': 'Space Grotesk|Noto Sans SC',
                  'quote': 'Space Grotesk|Noto Sans SC'},
        'card': 'term', 'bg': 'scan', 'frame': 'term', 'eyebrow': 'prompt', 'photo': 'mute', 'cover': 'term',
        'section': 'term', 'quote': 'term',
    },
}


def get(name):
    if name not in STYLES: raise SystemExit(f'没有这个风格：{name}。可选：{", ".join(STYLES)}')
    return STYLES[name]
