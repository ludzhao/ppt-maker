---
name: ppt-maker
description: 做 PPT / 幻灯片 / 汇报 / 述职 / 课件 / 路演 / 行业分析报告时使用。先采访用户、给出大纲建议，确认后生成原生可编辑的 PowerPoint（.pptx，带动画、自动图表、嵌入字体）和逐页演讲稿。用户要改已经生成的 PPT（改数字、改文字、加页）时也用。
display_name: 高级感 PPT 一键生成
display_name_en: PPT Maker
description_zh: 先采访再出大纲，一键生成原生可编辑的 PowerPoint：13 种风格可看图选择，图表数据自带动效，嵌入字体，附逐页讲稿。
description_en: Interviews you, drafts an outline, then builds a native editable PowerPoint with 13 visual styles, animated data charts, embedded fonts and speaker notes.
examples_zh:
  - "帮我做一份 10 分钟的年终述职 PPT，数据我贴给你"
  - "做一个 AI 行业分析报告的 PPT，要深色高级风"
  - "把这份 PPT 换成黑白杂志风格，第 5 页的数字改一下"
examples_en:
  - "Make a 10-minute year-end review deck from the numbers I paste"
  - "Build a dark, premium-looking AI industry report deck"
  - "Switch this deck to the black-and-white magazine style and fix the numbers on slide 5"
version: 1.0.0
author: ludzhao
---

# PPT 生成

本 skill 所在文件夹记作 `SKILL_DIR`（这个 SKILL.md 所在的文件夹）。所有命令都用 `python3`；Windows 用 `python`。

## 第 0 步：检查环境（每个新对话第一次用时做一次）
```
python3 SKILL_DIR/tools/setup_env.py
```
第一次运行会自动下载字体和配图（约 28MB，走国内镜像，通常 1 分钟内）。看到「依赖齐全」或「安装完成」再往下走。失败就把报错原文告诉用户，不要自己改代码。

## 第 1 步：采访（一次问完，等用户回答）
用一条消息问下面这些，用户没说的不要自己编：
1. 讲给谁听？在什么场合？讲多久？
2. 最想让听众记住的**一句话结论**是什么？
3. 手上有哪些材料和数据？（可以直接贴表格、数字、文档）哪些需要你帮忙上网查？
4. 有没有必须出现的内容、图片、公司名称/汇报人？
5. 风格偏好：**不要只报风格名字，必须让用户看到样子**。问这一题之前先运行 `python3 SKILL_DIR/tools/style_menu.py`（会打印 1–13 号清单，并在浏览器打开网页版菜单），然后在消息里贴出菜单图 `![风格菜单](SKILL_DIR/examples/风格菜单.png)`（把 SKILL_DIR 换成实际路径；界面显示不了图片时，告诉用户网页版已在浏览器打开、或把图片路径发给他）。让用户回复编号。没有偏好就推荐 1–4 号设计系统里最贴合场合的一个，并说明理由。

## 第 2 步：给建议（等用户确认后再生成）
用一张表给出大纲：页码 | 版式 | 结论式标题 | 这页放什么数据/图。规则：
- **页数**：约 1 分钟 1 页；10 分钟 ≈ 10–14 页。
- **结构**：封面 → 目录 → 每章（章节页 + 2–4 页内容）→ 结论金句 → 结尾。
- **标题写结论**，不写「XX 情况」「XX 分析」。✗「用户规模情况」✓「5G 用户五年从 2 成涨到 7 成」。
- **每页只讲一件事**；有数字的页优先用图表（chart / charts / kpi / timeline）。
- **节奏**：每 4–6 页安排一页「变调」（section 满版照片、stat 巨型数字、quote 金句）。
- 同时说明：哪些数据还缺、打算去哪里查。

## 第 3 步：查数据（需要时）
- 每个数字都要有来源（机构 + 时间），写进该页的 `source`。
- 查不到或拿不准的写「待核实」，**绝不编造数字**；计算出来的数字在 source 里注明「为计算值」。
- 把用到的数字和来源链接整理成一个 `数据来源.md` 放在输出文件夹，交付时一起给用户。

## 第 4 步：写稿件 JSON
1. 在用户的工作文件夹新建 `deck.json`。先打开 `SKILL_DIR/examples/模板_通用.json` 照着改，字段说明见 `SKILL_DIR/references/稿件格式.md`。
2. 每页必须写 `notes`（演讲稿，口语，60–150 字），这就是交付给用户的「讲稿」。
3. 字数上限：要点正文 ≤ 40 字，insights 每条 ≤ 45 字，表格 ≤ 6 行 6 列，标题 ≤ 24 字。
4. 用户给的图片放在 deck.json 旁边，用相对路径；没有图片就**不要用** hero / split / gallery 版式，section 不写 image。

## 第 5 步：生成并自查
```
python3 SKILL_DIR/tools/build_deck.py deck.json 输出名.pptx
```
命令会同时生成 `输出名_讲稿.md`，并自动自查。如果打印「自查发现 N 个问题」：
- 按每条后面的建议改 deck.json，再运行一次，直到「自查通过」。最多改 3 轮，还有问题就如实告诉用户是哪几页。
- 「下半页空」怎么补，见 `references/稿件格式.md` 最后一节。

## 第 6 步：交付
告诉用户：pptx 和讲稿的文件路径、一共几页、用了哪种风格、哪些数字是「待核实」。提醒：
- 用 **PowerPoint** 打开效果最好（动画、字体都正常）；WPS 能打开，个别动画会简化；Keynote 字体会被替换。
- 想换风格：说一声就能用同一份稿件重新生成。

## 修改已经生成的 PPT
- **改 deck.json 再重新生成**，不要直接改 pptx：图表是画出来的，直接改数字柱子不会变。
- 改了数字，同一页的标题、解读、notes 里引用的旧数字要一起改，source 也要跟着改。
- 重新生成会覆盖用户在 PowerPoint 里手动做的修改，先问一句。
- 只有 pptx、找不到 deck.json 时：`python3 SKILL_DIR/tools/extract_deck.py 文件.pptx deck.json` 取回稿件。

## 换风格 / 换字体
- 用户想换风格时，同样先运行 `python3 SKILL_DIR/tools/style_menu.py` 并贴出菜单图，让用户按编号选。
- deck.json 里 `"style"`：folio / ember / candy / volt（设计系统），或 consulting（默认）/ economist / nightdata / keynote / swiss / bento / brutal / ink / terminal。
- **推荐先用 4 套「设计系统」**：folio（黑白杂志，带黑白摄影）/ ember（暗黑董事会，带 3D 橙球）/ candy（Y2K 糖果，带 3D 物件）/ volt（深色荧光绿）。它们每种页型都有自己的构图，不共用骨架，配图已随 skill 附带；稿件里写 `image` 可以换成用户自己的图。
- 其余 9 种是早期的「换色风格」，版式共用一套骨架，适合要求保守的场合。
- 9 种风格的封面、章节页、金句页、结尾页版式各不相同，内容一个字不用改。完整示例：`SKILL_DIR/examples/ai_demo.json`（13 页，覆盖全部常用版式）。
- 字体是开源字体，已随 skill 打包，生成时自动把用到的字嵌进 pptx，对方电脑没装也能正常显示。

## 不要做的事
- 不要修改 SKILL_DIR 里的代码；版式不满足需求时换版式或拆页。
- 不要在一页里堆超过 3 块内容；不要整页都是文字。
- 不要用 `**` 标出一页里超过 1 处重点。

## 可选：在 Mac + PowerPoint 上导出预览图和动画视频
```
zsh SKILL_DIR/tools/pp_preview.sh 输出名.pptx [--video]
```
第一次运行 PowerPoint 会请求文件夹权限，需要用户本人点允许。
