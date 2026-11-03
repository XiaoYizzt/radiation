# PROGRESS — 辐射备忘录

> 最后更新：2026-11-03（Asia/Singapore）
> 项目根目录：`C:\Users\XkXia\Desktop\radiation`
> 当前状态：核心重构已完成，可部署；WESViewer 已新增 CSV/TXT 光谱支持并通过示例测试；无阻塞性开发任务。
> 本文件是交接记录；详细操作说明见 [README.md](README.md)。

---

## 0. 一句话状态

原有纯 HTML 辐射知识网站已完成整站前端重构：81 个 HTML 页面（75 个原有页面 + 6 个新增页面）和 1 个 PDF 已统一为现代静态知识门户，保留原 URL、文章正文、图片、链接、锚点、公式/表格与交互工具；自动完整性校验 13 项全部通过。WESViewer 已新增通用 CSV/TXT 光谱解析并通过两个示例、旧 XML 和计数-only 场景测试。下一步主要是人工验收、按需修复旧站遗留失效链接，以及真实设备测试。

---

## 1. 关键事实

| 项目 | 当前值 |
| --- | --- |
| 正式站点 | 项目根目录，入口 [index.html](index.html) |
| 旧站备份 | `_build/orig/`，仅用于重建与校验，**不要部署** |
| HTML 页面 | 81 个（原有 75 + 新增 6） |
| PDF | 1 个：[修正关于KB6011型辐射计能量响应的方案.pdf](修正关于KB6011型辐射计能量响应的方案.pdf) |
| 技术栈 | HTML + CSS + 原生 JavaScript |
| 运行时后端 | 无 |
| 运行时构建 | 无（根目录已是生成好的静态文件） |
| 前端框架 | 无（无 React/Vue/npm 依赖） |
| 字体/图标库 | 无外部字体、无图标库；使用系统字体 + 内联 SVG |
| 搜索 | 浏览器本地静态索引；按需加载 [js/search-index.js](js/search-index.js) |
| WESViewer 格式 | 原有 XML/SPE 等 + 新增 CSV / TXT 能谱（2026-11-03） |
| 图片引用 | 248 个原始图片引用 |
| 外部 URL | 48 个（改版前集合全部保留） |
| 更新日志 | 51 条（原首页 42 条 + 历史页 7 条 + 补充的背景色记录 2 条） |
| 版本控制 | 当前目录**不是** git 仓库（无 `.git`） |
| 自动校验结果 | 0 failures（[verify_out.txt](_build/verify_out.txt)） |

站点资源（不含 `_build/`）约 241 MB，主要来自原有图片和 3 个 MP4；未压缩或转码，以免改变原始资料。

---

## 2. 正式版本 vs. 开发备份

### 正式版本

`C:\Users\XkXia\Desktop\radiation` 根目录：

- [index.html](index.html) 是新版首页；
- `article/`、`info/`、`info2/`、`other/`、`tips/`、`tool/` 都是新版页面；
- `css/`、`js/`、`img/` 是正式运行资源；
- `README.md` 是部署与维护说明；
- `PROGRESS.md` 是本文件。

### 开发备份

`_build/orig/` 是重构前原始 HTML 的逐文件备份。例如：

- 旧版首页：[_build/orig/index.html](_build/orig/index.html)；
- 旧版评测、文章、工具页面也都在此目录。

**不要**用 `_build/orig` 覆盖根目录，也不要把 `_build/` 上传到静态托管空间。

### `_build/` 中的维护工具

| 文件 | 用途 |
| --- | --- |
| [build.py](_build/build.py) | 从 `_build/orig/` + `site_data.py` 重新生成整站 |
| [content.py](_build/content.py) | 原页正文抽取、清洗、标题/表格/锚点规范化 |
| [site_data.py](_build/site_data.py) | 页面标题、摘要、分类、标签、日期等元数据 |
| [render.py](_build/render.py) | 文章页、工具页、栏目页模板与文章列表 |
| [pages.py](_build/pages.py) | 首页、关于、搜索、站点地图、更新日志 |
| [viewers.py](_build/viewers.py) | WESViewer 工作区外壳 |
| [templates.py](_build/templates.py) | 全站头部、页脚、搜索对话框、脚本注入 |
| [verify.py](_build/verify.py) | 对基线做内容/链接/图片/锚点/结构校验 |
| [tests/test_parsers.js](_build/tests/test_parsers.js) | CSV/TXT 解析器离线回归测试（Node.js） |
| [baseline.json](_build/baseline.json) | 改版前的页面、链接、图片、锚点基线 |
| [changelog.json](_build/changelog.json) | 从旧首页解析出的 42 条更新日志 |
| [screenshots/](_build/screenshots/) | 最终视觉验收截图，含 WESViewer CSV/TXT/XML 实测截图 |
| `spviewer.js.before-csv-txt` | CSV/TXT 功能开发前的 `spviewer.js` 备份 |

重建命令（需要 Python 3 + lxml）：

```powershell
python _build/build.py
python _build/verify.py
```

WESViewer 解析器回归测试（仅开发用，需要 Node.js）：

```powershell
node _build/tests/test_parsers.js
```

重建会覆盖根目录页面；日常小改建议直接编辑根目录 HTML，不要改 `_build/orig/`。

---

## 3. 已完成任务

### 信息架构

- 重建为 8 个主要知识板块入口：基础知识、测量与仪器、仪器评测、文章与笔记、工具与数据、其他与专题、关于本站、站点地图。
- 新增统一面包屑；所有栏目页与文章页都有明确上级路径。
- 修正原站分类混乱：文章、评测、工具、医学辐射、存档页面分别归位。
- 首页从“文章链接目录”改为门户：主题卡片、阅读路径、精选评测、最近更新、工具入口、随机知识提示。
- 新增 [sitemap.html](sitemap.html)，全站 81 个 HTML + 1 个 PDF 均可从索引到达。
- 新增 [changelog.html](changelog.html)，合并旧首页更新日志与“先前的更新历史”。
- 保留旧首页、旧重复页面、缺失资源页面等为带说明的存档页。

### 设计系统与模板

- 全站统一 [css/site.css](css/site.css)：
  - 暖纸色背景、深墨正文、深青强调色；
  - 系统中文/英文字体栈，无外部字体依赖；
  - 统一字号、行高、间距、按钮、标签、卡片、表格、图注、引用和焦点样式；
  - 文章正文约 44rem，17px/1.95，避免行宽过长。
- 所有文章页统一结构：顶部导航、面包屑、标题区、元信息、标签、正文、上一篇/下一篇、返回分类、右侧粘性目录。
- 移动端隐藏右侧目录，改为文章头部的 `<details>` 内嵌目录。
- 手机导航使用原生 `<details>`，无 JS 也能展开。
- 阅读进度条、图片灯箱、宽表格横向滚动提示由 [js/site.js](js/site.js) 渐进增强。

### 页面迁移

- 75 个原有 HTML 页面全部重建；没有移动文件、没有改文件名。
- 6 个新增页面：[reviews.html](reviews.html)、[tools.html](tools.html)、[about.html](about.html)、[search.html](search.html)、[sitemap.html](sitemap.html)、[changelog.html](changelog.html)。
- 9 个 WESViewer 工作区页面保留原 `spviewer.js`、jQuery/Flot、元素 ID、XML 路径和光谱数据，只替换外层站点壳与样式。
- 旧版 `info/info010[X].html`、`Ju.html`、`Untitled-1.html`、重复的 `cs137.html` / `xray.html` / `other/info004.html`、过时的文章索引页均保留，并加存档提示。

### 搜索

- [search.html](search.html) + 顶部搜索对话框。
- 搜索索引为静态 [js/search-index.js](js/search-index.js)，共 66 条内容项，约 86 KB，首次打开搜索时按需加载。
- 支持标题、标签、摘要、正文匹配；支持分区筛选；结果高亮与摘要截取。
- 快捷键：`/`、`Ctrl/Cmd+K` 打开；方向键选择，Enter 打开。
- `file://` 下也可用（通过注入本地脚本加载索引，不依赖 fetch/CORS）。
- 搜索内容不经过任何服务器。

### 原有交互工具

- [tool/error simulation.html](tool/error%20simulation.html)：泊松误差模拟，自动出图。
- [tool/jitter simulation.html](tool/jitter%20simulation.html)：点击“开始模拟”后出图与误差表。
- [tool/beta ray range calculation.html](tool/beta%20ray%20range%20calculation.html)：β 射程计算表正常填充。
- [tool/info004.html](tool/info004.html)：灵敏度模拟 Canvas 正常。
- WESViewer 入口 [tool/WESViewer/index.html](tool/WESViewer/index.html) 与 9 个工作区。
- 旧首页随机 Tips 恢复；旧数据页时钟/IP 组件恢复（IP 查询仅在 HTTP 环境请求）。
- 原 51.LA 与 Google Analytics 代码保留；统计失败不影响页面。

### WESViewer CSV / TXT 支持（2026-11-03）

已为 WESViewer 新增 CSV 与 TXT 能谱解析，接入原有 `parse_file()` → `spectrum_data_ch` / `spectrum_data_ev` → Flot 绘图链路，不重写查看器。

**两个示例文件的实际结构**

- `tool/WESViewer/wesviewer/Ra-226.csv`
  - 65,151 字节；UTF-8 BOM；CRLF；2,501 行（1 行表头 + 2,500 个通道）。
  - 表头：`Channel,Energy,Counts (TotalTime=49662.2254374s)`。
  - 通道 0–2499；能量 -5.198966… 至 4358.694082… keV，逐通道给出。
  - 计数值总和 13,061,843；时间从表头 `TotalTime` 解析为 49,662.2254374 秒。
- `tool/WESViewer/wesviewer/Am241.txt`
  - 80,665 字节；UTF-8 无 BOM；CRLF；4,109 行，其中 4,096 行数据。
  - Theremino MCA 文本格式：虚线分隔、`Started at`、`Total time: 39573 sec.`、`Total pulses: 1506411`、`Sampling`、`Minimum energy`、`Bin multiplier` 等元数据。
  - 数据正则为 `Energy(KeV), Counts`，能量 0.00–181.29 keV；计数总和 1,506,411，与 `Total pulses` 一致。
  - 能量值是文件逐行给出的两位小数，不额外计算或改写；`Bin multiplier` 仅展示，不用于伪造刻度。

**原先为什么是 `Unknown format`**

`parse_file()` 只依次尝试 20 个原有解析器（XML、winTMCA、SPE、PRA 等）。没有 CSV/TXT 解析器处理完所有失败后返回 `false`，四个加载回调统一弹出 `Unknown format.`。两个文件本身是有效的数值表格，只是没有匹配的解析器。

**新增逻辑**

- 在 `spviewer.js` 的 `instruments` 数组末尾增加 `draw_graph_csv_spectrum`、`draw_graph_txt_spectrum`；原有解析器顺序不变，旧格式仍先匹配。
- CSV 不依赖扩展名：
  - 自动识别 `,` / `;` / Tab；
  - 支持 UTF-8 BOM、空行、`#` / `//` / `--` 注释；
  - 识别 `Channel`、`Energy`、`Counts` / `CPS` / `Rate` 表头，也支持无表头推断；
  - 支持 1 列计数、2 列 Energy/Counts 或 Channel/Counts、3 列 Channel/Energy/Counts；
  - 从 `TotalTime=`、`Total time:`、`Live time` 等表头/元数据读取测量时间；
  - 能量单位支持 eV / keV / MeV，内部统一转 keV。
- TXT 不依赖扩展名：
  - 识别 `Theremino_MCA` 与 `Energy(...) Counts` 表头；
  - 跳过虚线、空行和注释；
  - 解析 `能量, 计数` 行，读取元数据并保留在 `#sp_info`；
  - 支持 `Total time`；无时间时按 1 秒归一化并明确标注。
- 接入原有数据对象：
  - `spectrum_data_ch = [[channel, cps], ...]`
  - `spectrum_data_ev = [[energy_keV, cps], ...]`
  - `time`、`min_cps`、`sp_info`、`additional_sp_info_html` 与旧解析器一致；
  - 计数值只做 `/time` 的既有 cps 转换，不额外缩放或取整丢失。
- 无能量刻度的文件：
  - `has_energy = false`，`spectrum_data_ev = []`；
  - 单光谱模式只显示通道轴，隐藏能量轴、核素匹配和能量范围预设；
  - 光标能量显示 `—`；`sp_info` 明确显示“无（仅通道）”，并显示提示；
  - 不生成任何虚假能量刻度。
- 错误提示：
  - 新增 `parse_error_message`；加载回调改为 `alert(parse_error_message || "Unknown format.")`；
  - 缺计数列、行列数不足、非数字、能量/通道不递增、数据行不足等都有具体中文错误；
  - 无能量文件参与双/多光谱比较时提示改用单光谱模式。
- `save_tsv` 对无能量文件改为导出 `channel\tcps`；有能量文件仍导出 `energy\tcps`。

**测试**

- 离线解析回归（Node）：[_build/tests/test_parsers.js](_build/tests/test_parsers.js)
  - Ra-226.csv：2,500 通道、2,500 能量、总计数 13,061,843、时间 49,662.2254374 秒，全部一致。
  - Am241.txt：4,096 通道、4,096 能量、总计数 1,506,411、时间 39,573 秒，全部一致。
  - 无表头单列计数、带表头计数、无效 CSV 错误提示均通过。
- 浏览器实际加载（Chrome Headless + 本地 HTTP）：
  - `#__Ra-226.csv//0`：成功绘图，通道 2500，能量范围 -5.20–4358.69 keV，计测时间 13:47:42，Y 轴峰值约 3.5 cps。
  - `#__Am241.txt//0`：成功绘图，通道 4096，能量范围 0.00–181.29 keV，计测时间 10:59:33，Am-241 的 26/59.5 keV 峰可见。
  - `#__Am-241.xml//0`：原有 XML 格式仍正常绘图，双轴/能量轴未受影响。
  - 临时计数-only CSV：只显示通道轴，能量轴隐藏，提示“未提供时间，按 1 秒显示”，无脚本异常。
  - 截图：[wesviewer-csv.png](_build/screenshots/wesviewer-csv.png)、[wesviewer-txt.png](_build/screenshots/wesviewer-txt.png)、[wesviewer-xml.png](_build/screenshots/wesviewer-xml.png)、[wesviewer-counts-only.png](_build/screenshots/wesviewer-counts-only.png)。

**本次修改文件**

- [tool/WESViewer/wesviewer/spviewer.js](tool/WESViewer/wesviewer/spviewer.js)
- [css/viewer.css](css/viewer.css)（无能量提示样式）
- [PROGRESS.md](PROGRESS.md)、[README.md](README.md)
- 开发测试/截图：`_build/tests/`、`_build/screenshots/`、`_build/spviewer.js.before-csv-txt`（不参与部署）。

**新增格式尚未覆盖的情况**

- CSV 无表头、列角色无法可靠推断时，建议提供 `Channel/Energy/Counts` 表头。
- TXT 目前覆盖两列 `Energy, Counts` 的 Theremino/通用文本表；3 列以上 TXT 未定义语义，可能被当作 CSV 或明确报错。
- CSV/TXT 若没有时间，只按 1 秒显示并明确标注，不会伪造真实测量时间。
- CSV/TXT 若没有能量列，不支持双/多光谱比较（会提示）。
- 能量必须严格递增；重复/乱序会报错，避免绘图映射错误。

### 清理

- 清理了 `_build/` 中的临时 Chrome profile、调试截图、临时补丁与测试脚本。
- 保留可复现构建/校验所需的最小文件集。
- 没有删除任何原有站点页面、图片、PDF 或旧资源文件。

---

## 4. 重要技术决策与原因

1. **不使用全局左侧固定侧边栏**
   - 顶部主导航 + 面包屑 + 文章右侧目录，减少占用阅读宽度和点击层级。
   - 移动端用 `<details>` 抽屉，避免依赖 JS。

2. **保持纯静态、零运行时构建**
   - 直接上传根目录即可；不引入 npm、Node 服务端、PHP、Python 运行时或数据库。
   - 设计系统仅使用一个 CSS 文件，脚本全部为原生 JS。

3. **保留原 URL 与文件名**
   - 所有旧页面路径、含空格文件名、中文文件名、`[X]` 文件名、WESViewer 深层路径均不变。
   - 旧重复页面保留为存档，不做 301/跳转，避免旧链接失效。

4. **正文抽取而非人工改写**
   - `_build/content.py` 从 `_build/orig/` 抽取正文，做结构清理、标题层级归一、表格/图集转换、锚点保留。
   - 自动校验逐页比较正文文本；技术内容、单位、公式图片、表格数据未改写。
   - 标题重复项只做去重展示（页面 H1 + 原文标题去重）；原日期以 title-note 或 meta 日期显示。

5. **WESViewer 不重写业务代码**
   - 工作区保留 jQuery 1.5.2、Flot、`spviewer.js` 和全部元素 ID。
   - 只替换外层站点导航、字体/颜色和响应式宽度；避免破坏光谱加载与交互。
   - 在 `file://` 下浏览器会阻止读取 XML，页面提示需用 HTTP 静态托管。

6. **搜索索引按需加载**
   - 不把 86 KB 索引塞进每个页面；仅打开搜索/搜索页时加载。
   - 使用 `window.SITE_SEARCH` 静态数组，兼容 `file://`。

7. **宽表格采用横向滚动而不是压缩**
   - 技术表格列多、备注长；用 `.table-scroll` + 滚动提示保持可读性，移动端尤其必要。
   - 图片表格自动转换为图集；单图/双图有独立布局。

8. **旧站问题只记录、不擅自修改**
   - 已知失效链接、缺失图片、旧日期笔误全部保留。
   - 对 `info/info010[X].html` 的数据库失效入口增加了页面说明，但链接本身未改。
   - 旧站“针对 PC 端设计”的说明原文保留在关于页，并注明本次已响应式适配。

---

## 5. 新增/修改/删除文件

### 新增页面

[reviews.html](reviews.html)、[tools.html](tools.html)、[about.html](about.html)、[search.html](search.html)、[sitemap.html](sitemap.html)、[changelog.html](changelog.html)

### 新增样式

[css/site.css](css/site.css)、[css/viewer.css](css/viewer.css)

### 新增脚本

[js/site.js](js/site.js)、[js/search-index.js](js/search-index.js)、[js/analytics.js](js/analytics.js)

### 新增文档/记录

[README.md](README.md)、[PROGRESS.md](PROGRESS.md)

### 修改

- 全部 75 个原有 HTML 页面重写为统一模板。
- 9 个 WESViewer 工作区页面加入站点壳与 `viewer.css`，原有业务脚本保留。
- [tool/WESViewer/wesviewer/spviewer.js](tool/WESViewer/wesviewer/spviewer.js)：新增 CSV/TXT 解析、无能量刻度分支、错误提示和零索引映射修正。
- [css/viewer.css](css/viewer.css)：增加无能量刻度提示样式。
- [README.md](README.md)、[PROGRESS.md](PROGRESS.md) 文档更新。

### 删除

- 未删除任何原有站点文件。
- 仅删除了 `_build/` 中用于本次开发的临时 Chrome profile、调试截图、临时补丁/测试脚本；`_build/orig/`、构建脚本和校验基线保留。

### 未动

- 全部 `img/` 图片、MP4、PDF；
- 原有 `css/t1.css`、`css/TX.css`、`css/img.css`、`css/WESViewerIMG.css`、`tool/style.css`、`tool/WESViewer/.../spviewer.css` 等旧样式文件；
- 原有 jQuery/Flot、XML/TSV 数据文件、`nuclear_data.txt`、`range_preset.txt`、`spviewer_list.txt` 的内容与顺序（用户新增的两个 CSV/TXT 条目原样保留）。

---

## 6. 自动校验结果

命令：

```powershell
python _build/verify.py
```

最终输出（[verify_out.txt](_build/verify_out.txt)）：

| 检查项 | 结果 |
| --- | --- |
| 原有 75 个页面全部存在 | PASS |
| 文章正文逐页对比 | PASS |
| 原 H1/标题日期被页面标题表示 | PASS |
| WESViewer 工作区正文逐页对比 | PASS |
| 引用本地 CSS/JS/图片存在 | PASS |
| 无新增失效内部链接 | PASS |
| 无新增失效锚点 | PASS |
| 原有 ID/锚点保留 | PASS |
| 原有外部 URL 全站保留 | PASS（48 个） |
| 原有现存图片仍被引用 | PASS（248 个） |
| 无重复 ID | PASS |
| 每页有 H1 | PASS |
| 每页有 `<title>` | PASS |

**FAILURES: 0**

结构化检查另行确认：81 页均含统一 station header、footer、`main id="main"`、搜索 dialog、`site.css`、`site.js`。

构建可复现性：删除开发临时文件后重新运行 `python _build/build.py`，仍生成 81 页且校验通过。

WESViewer 解析器另有离线回归测试：`node _build/tests/test_parsers.js`，覆盖两个示例、计数-only、无表头单列和错误输入；结果见 [parser-test-output.txt](_build/tests/parser-test-output.txt)。

---

## 7. 已验证通过的功能

### 自动检查

- 原页面/文章正文、WESViewer 正文完整性。
- 内部链接目标、锚点、原始 ID 保留。
- 本地 CSS/JS/图片引用存在。
- 外部 URL 原集合保留。
- 重复 ID、H1、title。
- 构建与校验可重复运行。

### 浏览器渲染（Chrome Headless）

- 1440px：首页、基础知识、测量与仪器、评测、文章、工具、关于、更新日志、站点地图、文章页、评测页、WESViewer。
- 768px：文章页、宽表格、内嵌目录。
- 500px / 390px：首页、文章、评测、检测器表格、模拟工具、WESViewer、搜索对话框、搜索页、手机菜单。
- 320px：首页。
- 图片灯箱、目录滚动高亮、表格提示、手机菜单开关均实测。
- 关键页面未出现 JavaScript 异常；仅外部统计/外链请求可能失败。

### 搜索

- 顶部搜索框、搜索页实测。
- 示例查询“氡”返回 9 条，“PM1405”返回 3 条；“能量补偿”在搜索页返回多条并高亮。
- 分区筛选、无结果状态、`file://` 下索引加载均正常。

### 工具

- 误差模拟：自动绘制。 
- 抖动模拟：点击提交后生成 Canvas 与误差表。
- β 射程：结果表 19 行正常。
- 灵敏度模拟：Canvas 正常。
- WESViewer：原有 Am-241 XML 正常；Ra-226 CSV 与 Am241 TXT 正常绘图；计数-only CSV 的通道轴/无能量提示正常；500px 移动视口无横向溢出。

---

## 8. 尚未测试 / 存在限制

1. **全部 9 个 WESViewer 工作区未逐一实测**：已实测 `wesviewer/index.html` 中的 Am-241 XML、Ra-226 CSV、Am241 TXT 和计数-only CSV；`isotope/`、`rain/` 等页面共用同一 `spviewer.js`，但未逐个加载所有光谱。
2. **CSV/TXT 格式覆盖有边界**：CSV 支持 1–3 列常见布局并可从表头/数值推断；无表头且列角色不明确时建议补表头。TXT 当前覆盖两列 `Energy, Counts`（Theremino/通用文本表），3 列以上 TXT 未定义语义。无能量列的文件只支持单光谱通道显示，不能比较。
3. **外部 URL 未做实时可用性验证**：48 个外链、Bilibili/YouTube 嵌入、Wikimedia 图片、Google Analytics、51.LA 未逐一联网验证；只确认 URL 被保留。
4. **真实设备未测试**：使用 Chrome Headless 的 320/390/500/768/1440 视口，未在实体手机、Safari、Firefox 上人工验收。
5. **未做正式无障碍审计**：没有运行 Lighthouse/axe；已有 skip link、焦点样式、ARIA、语义标题、表格 region 等基础措施。
6. **WESViewer 在 `file://` 下无法加载本地 XML**：浏览器限制；页面已提示使用 HTTP 静态托管。部署到任意静态空间即可。
7. **`info/info010[X].html` 的访问 IP 组件**：通过 `ipify` 在 HTTP 下请求；未验证该外部 API 在当前网络可用。时钟组件已本地恢复。
8. **搜索不覆盖存档页和 WESViewer 工作区**：这是有意设计，避免旧重复页和工具控件干扰结果。
9. **未做性能预算/图片压缩**：站点约 241 MB，3 个 MP4 与大量原图未压缩，部署上传时间可能较长。

---

## 9. 已知 Bug / 待解决问题（保留自旧站）

这些是**改版前就存在**的问题。按“不擅自修改原内容”的要求保留，未改写链接或伪造资源：

### 失效链接

1. [history.html](history.html) → `geiger counter.html`
2. [changelog.html](changelog.html) → `geiger counter.html`（来自旧日志条目）
3. [Untitled-1.html](Untitled-1.html) → `geiger counter.html`
4. [info/info008.html](info/info008.html) → `../energy compensation.html`
5. [info/info010[X].html](info/info010[X].html) → `../database/NE/out/cgi-bin/fissionyield.html`
6. 同上 → `../database/PGAA/out/pgaa/egaf.html`
7. 同上 → `../database/N/NGATLAS2/index.html`

`info010` 页面已加“数据库链接可能 404”的说明；链接本身保持原样。

### 锚点

- `detector_list.html#1`：原站就没有对应锚点，保留原链接。
- `tool/info004.html` 的 21 个 `#0.1_...` 是 JS 模拟参数，不是静态锚点，运行时有效。
- WESViewer 的 `#__Lu-176.xml//0` 等是运行时哈希，不是静态锚点。

### 缺失/错误图片

- `img/ju.jfif` 在原站已缺失；[Ju.html](Ju.html) 中仍保留引用。
- [other/info004.html](other/info004.html) 使用 `img/fs1.png`、`img/zd.jpg`，在原站路径就是错误的；页面已有存档提示。

### 内容说明

- `about.html` 保留了旧站“针对 PC 端设计”的原文，并在下方注明本次已响应式适配。
- `info/info018.html` 的原始内容本身把权重因子表拆成了段落/图片；本次未重写技术内容。
- `cs137.html` / `xray.html` / `other/info004.html` 是旧重复页面，保留以兼容历史链接。
- `Untitled-1.html` 是旧首页存档；旧 `../../index.html` 返回链接已随旧导航移除。

---

## 10. 待办事项 / 下一步建议

核心开发已完成，以下按优先级排列：

1. **人工验收新 IA**：确认首页主题分类、评测分组、工具入口、关于页说明是否符合你的长期规划。
2. **真实设备测试**：至少一台 iPhone/Android + Safari/Firefox，重点看文章表格、搜索对话框和 WESViewer。
3. **决定是否修复旧失效链接**：如果修，建议保留原文并在旁边增加“新地址/镜像”说明；不要直接删除旧链接。
4. **决定是否把存档页/工作区纳入搜索**：当前为避免噪声未纳入；若需要，修改 `_build/build.py` 的 `build_search_index()` 后重建。
5. **可选：压缩图片/视频**：若部署空间或带宽有限，可生成 WebP/压缩 MP4；这会改变资源文件，需逐页确认图片引用。
6. **可选：无障碍审计**：用 Lighthouse/axe 检查对比度、表单标签、键盘顺序。
7. **后续新增文章**：复制同类文章页模板，更新正文、栏目索引和 `js/search-index.js`；或修改 `_build/site_data.py` 后运行 `build.py`。
8. **WESViewer 格式扩展（可选）**：如需支持更多仪器格式，优先在 `spviewer.js` 新增独立解析器并追加到 `instruments` 数组末尾；保持现有解析器顺序和 `spectrum_data_ch/ev` 结构。当前 CSV/TXT 边界见第 3.1 节。
9. **版本管理**：当前不是 git 仓库；如需要，建议在根目录初始化 git，并忽略 `_build/` 或至少不提交其中的临时产物。

---

## 11. 新对话接手步骤

1. 先读本文件，再读 [README.md](README.md)。
2. 检查实际文件：
   - [index.html](index.html) 是新版首页；
   - `_build/orig/index.html` 是旧版备份，不要用于部署；
   - [verify_out.txt](_build/verify_out.txt) 是最近一次校验输出。
3. 运行校验确认当前状态：

   ```powershell
   python _build/verify.py
   ```

   预期末尾为 `FAILURES: 0`。
4. 不要移动/改名现有 HTML、图片、PDF；旧 URL 兼容是硬性要求。
5. 不要直接改 `_build/orig/`；它只是基线备份。
6. 部署时上传根目录除 `_build/` 外的文件。
7. 如果需要重建：先备份根目录，再运行 `python _build/build.py`；重建会覆盖所有生成页面。
8. 如果只做局部文案/样式修改，直接编辑根目录 HTML/CSS 即可，不必重建。

---

## 12. 部署与运行

### 静态部署

上传根目录除 `_build/` 外的全部文件到任意静态托管空间。无 npm、无 Node 服务端、无 PHP/Python、无数据库、无账号系统。

### 本地预览

```powershell
cd C:\Users\XkXia\Desktop\radiation
python -m http.server 8000
# http://127.0.0.1:8000/
```

- 普通阅读和搜索：直接双击 [index.html](index.html) 也可用。
- WESViewer 的 XML 光谱：必须通过 HTTP（或部署到静态空间）才能被浏览器读取。

### 关键设计资源

- 设计系统：[css/site.css](css/site.css)
- WESViewer 工作区样式：[css/viewer.css](css/viewer.css)
- 站点交互：[js/site.js](js/site.js)
- 搜索索引：[js/search-index.js](js/search-index.js)
- 首页：[index.html](index.html)
- 全站索引：[sitemap.html](sitemap.html)

---

## 13. 当前结论

- 网站已经是可部署的正式版本，**不是** `_build/orig`。
- 内容完整性、链接目标、锚点、图片引用和页面结构自动校验均通过。
- WESViewer 已支持 CSV/TXT 并完成示例文件、旧 XML 和计数-only 场景的实际浏览器测试。
- 没有阻塞性 Bug。
- 需要你决策的是：旧站遗留失效链接是否修复、是否扩大搜索范围、是否压缩媒体资源、是否继续扩展其他仪器格式，以及真实设备验收。
