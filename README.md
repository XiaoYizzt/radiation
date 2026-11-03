# 辐射备忘录 · 辐射及辐射测量仪器备忘录

一个纯静态的辐射科学知识门户。内容涵盖辐射基础概念、剂量与单位、探测器与测量仪器、仪器评测、实验笔记、核数据入口和可交互工具。

- 首页：`index.html`
- 技术栈：HTML + CSS + 原生 JavaScript
- 后端：无
- 构建步骤：无（已生成静态文件）
- 搜索：浏览器本地静态索引
- 部署：任意静态文件托管空间

## 直接预览

直接双击 `index.html` 即可阅读绝大部分页面。搜索、目录、模拟工具也能在 `file://` 下运行。

WESViewer 光谱查看器通过浏览器读取本地 XML 光谱数据。浏览器会阻止 `file://` 页面读取本地文件，因此光谱图需要在 HTTP 环境下加载：

```powershell
# 在站点根目录运行，然后访问 http://127.0.0.1:8000/
python -m http.server 8000
```

## 部署

把站点根目录下的文件上传到静态托管空间即可，不需要 Node、PHP、Python、数据库或任何服务端程序。

**不要上传 `_build/` 目录。** 它包含改版前的原始页面备份、迁移/校验脚本和开发截图，只用于维护与复核；它不是网站的一部分，也不应被公开访问。

推荐上传：

```
index.html  about.html  search.html  sitemap.html  changelog.html
base.html   reviews.html  article.html  tools.html
article/  info/  info2/  other/  tips/  tool/
css/  js/  img/  *.pdf
```

## 目录说明

| 路径 | 内容 |
| --- | --- |
| `index.html` | 首页：主题入口、阅读路径、评测与工具、更新记录摘要 |
| `base.html` | 基础知识板块索引 |
| `info/index.html` | 测量与仪器板块索引 |
| `reviews.html` | 仪器评测索引（含外部评测链接） |
| `article.html` | 文章与笔记索引 |
| `other/index.html` | 其他与专题索引 |
| `tools.html` | 工具与数据索引 |
| `about.html` | 关于本站、联系方式、技术说明、原文说明 |
| `search.html` | 搜索页（读取 `js/search-index.js`） |
| `sitemap.html` | 全部页面索引 |
| `changelog.html` | 合并后的 2022–2024 更新日志 |
| `css/site.css` | 全站设计系统 |
| `css/viewer.css` | WESViewer 工作区样式 |
| `js/site.js` | 导航、搜索、目录、表格提示、图片灯箱等 |
| `js/search-index.js` | 静态搜索索引（按需加载） |
| `js/analytics.js` | 原有的 51.LA 统计加载器 |
| `article/` `info/` `info2/` `other/` `tips/` | 原有文章页面（保留原路径与文件名） |
| `tool/` | 原有模拟工具与 WESViewer（保留原路径；WESViewer 支持 XML、CSV、TXT 光谱） |

## 维护内容

- 每个内容是独立的静态 HTML 文件。公共头部、面包屑、侧栏目录和页脚由构建脚本生成；若要手工新增文章，可以复制同类文章页，替换 `<main>` 内容、标题、面包屑、前后篇链接，并同步更新栏目索引。
- 搜索索引是 `js/search-index.js` 中的 `window.SITE_SEARCH` 数组。新增页面后需要追加 `{u,t,s,sn,d,k,l,b}` 条目，或运行下面的生成脚本重新生成。
- `_build/` 中的迁移脚本可以从 `_build/orig/` 的原始 HTML 重建整站（需要 Python 3 与 lxml）：

```powershell
python _build/build.py
python _build/verify.py
```

重建会覆盖现有页面；日常小改动建议直接编辑生成后的 HTML。

WESViewer 的 CSV/TXT 解析器位于 `tool/WESViewer/wesviewer/spviewer.js`。离线回归测试（需要 Node.js，仅开发用）可以运行：

```powershell
node _build/tests/test_parsers.js
```

注意：`css/viewer.css` 中移动端的 `[style*="float"]:not(.tickLabel)` 选择器用于避开 Flot 的刻度测量元素；不要去掉 `:not(.tickLabel)`，否则手机会因轴标签换行导致图表绘图区高度变成负数。

## 第三方资源

- Google Analytics（gtag.js）与 51.LA：沿用原站的访问统计。加载失败不影响阅读。
- Bilibili / YouTube 嵌入式视频：文章中的原有视频，需联网。
- Wikimedia Commons：Fusor 条目的一张外链图片。
- WESViewer 使用仓库内的 jQuery 1.5.2 与 Flot，不依赖 CDN；原有 XML 格式和新增 CSV/TXT 格式共用同一套光谱数据结构和绘图逻辑。

站内字体使用操作系统中文字体，不加载外部字体或图标库。

## 已知问题（保留原样，未擅自修改）

- 旧站遗留的失效链接：`history.html` / 更新日志中的 `geiger counter.html`、`info/info008.html` 中的 `../energy compensation.html`、`info/info010[X].html` 中三条 `../database/...` 入口、`Untitled-1.html` 中的 `geiger counter.html`。旧 `Untitled-1.html` 的 `../../index.html` 返回链接已随旧站点导航一起移除，首页本身正常存在。
- `detector_list.html#1` 在原站就没有对应锚点。
- `img/ju.jfif` 在原站已缺失；`other/info004.html` 的 `img/fs1.png`、`img/zd.jpg` 在原站使用了错误相对路径。
- `about.html` 的“建站时的说明”保留了原文中“针对 PC 端设计”的说法，并在下方注明本次改版已完成响应式适配。
- `_build/` 不参与部署。
