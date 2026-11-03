# -*- coding: utf-8 -*-
"""Home page, about, search, sitemap and changelog."""

import html as htmllib
import json
import os
import re

import content as C
import templates as T
from render import (base_for, entry_card, find_meta, level_badge, pdf_card,
                    read_time, review_card, section_pages, tool_card)
from site_data import (FEATURED_REVIEWS, GENERATED_HUBS, PAGES, PATHS,
                       SECTIONS, SITE, SUBSECTIONS, WES_GALLERY, WES_VIEWERS)

ROOT = C.ROOT


def esc(value):
    return htmllib.escape(str(value), quote=True)


def count_section(sid):
    return len(section_pages(sid)) + (1 if sid == "articles" else 0)


def topic_card(sid, base):
    section = SECTIONS[sid]
    pages = section_pages(sid)
    samples = pages[:3]
    if sid == "reviews":
        samples = FEATURED_REVIEWS[:3]
    links = "".join('<li><a href="%s%s">%s</a></li>' % (
        base, esc(rel), esc(PAGES[rel]["card"])) for rel in samples if rel in PAGES)
    return """<article class="topic-card topic-%(sid)s">
<a class="topic-head" href="%(base)s%(hub)s">
<span class="topic-num">%(number)s</span>
<span class="topic-icon">%(icon)s</span>
<h2>%(label)s</h2>
<span class="topic-count">%(count)d 篇</span>
</a>
<p class="topic-blurb">%(blurb)s</p>
<ul class="topic-links">%(links)s</ul>
<a class="topic-more" href="%(base)s%(hub)s">进入板块 %(arrow)s</a>
</article>""" % {
        "sid": esc(sid), "base": base, "hub": esc(section["hub"]),
        "number": section["number"], "icon": T.icon(section["icon"]),
        "label": esc(section["label"]),
        "count": len(pages) + (1 if sid == "articles" else 0),
        "blurb": esc(section["blurb"]), "links": links, "arrow": T.icon("arrow"),
    }


def index_card(base):
    return """<article class="topic-card topic-index">
<a class="topic-head" href="%(base)ssitemap.html">
<span class="topic-num">00</span>
<span class="topic-icon">%(icon)s</span>
<h2>站点索引</h2>
<span class="topic-count">全部页面</span>
</a>
<p class="topic-blurb">按主题、目录与存档浏览站内全部页面，也包含为兼容旧链接保留的历史页面。</p>
<ul class="topic-links">
<li><a href="%(base)ssitemap.html">全部页面清单</a></li>
<li><a href="%(base)schangelog.html">完整更新日志</a></li>
<li><a href="%(base)sabout.html">关于本站</a></li>
</ul>
<a class="topic-more" href="%(base)ssitemap.html">打开索引 %(arrow)s</a>
</article>""" % {"base": base, "icon": T.icon("list"), "arrow": T.icon("arrow")}


# ---------------------------------------------------------------------------
# Change log parsing
# ---------------------------------------------------------------------------

def _split_date(text):
    text = " ".join(text.split())
    match = re.search(r"[（(]?\s*(\d{2,4}\s*[/.\-]\s*\d{1,2}\s*[/.\-]\s*\d{1,2})\s*[)）]?\s*$", text)
    if not match:
        return text, ""
    date = re.sub(r"\s+", "", match.group(1))
    body = text[:match.start()].rstrip(" 　")
    return body, date


def load_changelog():
    entries = []
    entries.append({"text": "将背景更改为淡黄色", "href": "", "date": "2024/3/15",
                    "icon": "img/exclamation.gif"})
    entries.append({"text": "Change the background to light yellow", "href": "", "date": "2024/3/15"})
    with open(os.path.join(ROOT, "_build", "changelog.json"), encoding="utf-8") as fh:
        for item in json.load(fh):
            body, date = _split_date(item["text"])
            entries.append({"text": body, "href": (item.get("href") or "").strip(),
                            "date": item.get("date") or date})
    # Older history page entries
    doc = C.parse_original("history.html")
    heading = None
    for h in doc.xpath("//h1|//h2|//h3|//h4"):
        if "更新日志历史" in C.plain_text(h):
            heading = h
            break
    if heading is not None:
        nxt = heading.getnext()
        while nxt is not None and nxt.tag not in ("ul", "ol"):
            nxt = nxt.getnext()
        if nxt is not None:
            for li in nxt.xpath("./li"):
                text = " ".join(li.itertext())
                text = " ".join(text.split())
                links = li.xpath(".//a")
                href = links[0].get("href").strip() if links else ""
                body, date = _split_date(text)
                entries.append({"text": body, "href": href, "date": date})
    def sort_key(entry):
        parts = re.split(r"[/.\-]", entry.get("date") or "")
        try:
            numbers = [int(part) for part in parts if part.strip().isdigit()]
        except ValueError:
            numbers = []
        if len(numbers) >= 3:
            return (numbers[0], numbers[1], numbers[2], 1)
        return (0, 0, 0, 0)
    entries.sort(key=sort_key, reverse=True)
    return entries


def log_item(entry, base, show_link=True):
    body = entry["text"]
    date = entry["date"]
    href = entry["href"]
    content = esc(body)
    if show_link and href and href != "#":
        content = '<a href="%s%s">%s</a>' % (base, esc(href), content)
    elif show_link and href == "#":
        content = '<a href="#main">%s</a>' % content
    icon = ""
    if entry.get("icon"):
        icon = '<img class="log-icon" src="%s%s" width="14" height="14" alt="" loading="lazy">' % (base, esc(entry["icon"]))
    return """<li class="log-item">
<div class="log-date">%s</div>
<div class="log-body"><p>%s %s</p></div>
</li>""" % (esc(date) if date else '<span class="muted">—</span>', icon, content)


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

def render_home():
    base = ""
    entries = load_changelog()
    latest = [item for item in entries if item.get("date")][:7]
    latest_html = "".join(log_item(item, base, show_link=True) for item in latest)

    path_cards = []
    for path in PATHS:
        steps = []
        for index, rel in enumerate(path["steps"], 1):
            meta = find_meta(rel) or PAGES.get(rel)
            if not meta:
                continue
            steps.append('<li><span class="step-num">%02d</span><a href="%s%s">%s</a></li>' % (
                index, base, esc(rel), esc(meta.get("card") or meta["title"])))
        path_cards.append("""<article class="path-card">
<p class="path-level">%(level)s</p>
<h3>%(title)s</h3>
<p>%(desc)s</p>
<ol class="path-steps">%(steps)s</ol>
</article>""" % {"level": esc(path["level"]), "title": esc(path["title"]),
                 "desc": esc(path["desc"]), "steps": "".join(steps)})

    review_cards = "".join(review_card(rel, PAGES[rel], base) for rel in FEATURED_REVIEWS)
    tool_rels = ["tool/WESViewer/index.html", "tool/error simulation.html",
                 "tool/jitter simulation.html", "tool/beta ray range calculation.html"]
    tool_cards = "".join(tool_card(rel, PAGES[rel], base) for rel in tool_rels)

    sections = []
    for sid in ["basics", "measurement", "reviews", "articles", "tools"]:
        sections.append(topic_card(sid, base))
    sections.append(index_card(base))

    index_rows = []
    for sid in ["basics", "measurement", "reviews", "articles", "tools"]:
        section = SECTIONS[sid]
        index_rows.append("""<a class="index-row" href="%(base)s%(hub)s">
<span class="index-num">%(number)s</span>
<span class="index-label">%(label)s</span>
<span class="index-count">%(count)d</span>
%(arrow)s
</a>""" % {"base": base, "hub": esc(section["hub"]), "number": section["number"],
           "label": esc(section["label"]), "count": count_section(sid), "arrow": T.icon("arrow")})

    body = """<main id="main" class="page page-home">
<section class="hero">
<div class="shell hero-grid">
<div class="hero-main">
<p class="eyebrow">Radiation · Detectors · Measurement</p>
<h1>辐射知识，<br>从测量开始。</h1>
<p class="hero-lede">一个关于电离辐射、辐射探测与测量仪器的中文知识库。从单位与屏蔽，到能谱与仪器评测；既写给刚入门的读者，也留给需要查资料的专业人士。</p>
<form class="hero-search" action="search.html" method="get" role="search">
<label class="sr-only" for="hero-search-input">搜索站内内容</label>
%(search_icon)s
<input id="hero-search-input" type="search" name="q" placeholder="搜索文章、核素、仪器或工具…" autocomplete="off">
<button type="submit" class="button button-solid">搜索</button>
</form>
<div class="quick-links">
<span>常被查阅</span>
<a href="Sv.html">希沃特</a>
<a href="info/info001.html">能量补偿</a>
<a href="info/info022.html">β 射线测量</a>
<a href="rn.html">氡</a>
<a href="tips/cs137.html">Cs-137</a>
<a href="tool/WESViewer/index.html">WESViewer</a>
</div>
</div>
<aside class="hero-index" aria-label="站点索引">
<div class="hero-index-head"><span>站点索引</span><span>Index</span></div>
%(index_rows)s
<p class="hero-index-foot">自 2022 年持续更新 · 最近更新 2024/6/28</p>
</aside>
</div>
</section>

<section class="tip-band">
<div class="shell tip-inner" data-tip>
<p class="eyebrow">Tips · 知识提示</p>
<div class="tip-items">
<p class="tip-item">铯 137 已被用于确定葡萄酒的年代和检测假冒产品，并作为一种相对定年材料用于评估 1945 年后发生的沉积年龄。 <a href="tips/cs137.html">了解更多</a></p>
<p class="tip-item" hidden>环境中的大多数钚以微小颗粒的形式存在，是核武器试验和核反应堆事故的残余物。大气层核试验产生的微小颗粒广泛散布在环境中。因此，几乎每个人都会接触到极少量的钚。</p>
<p class="tip-item" hidden>X 射线和伽马射线具有相同的基本特性，但来自原子的不同部分。X 射线从原子核外的过程中发出，但伽马射线起源于原子核内。 <a href="tips/xray.html">了解更多</a></p>
</div>
</div>
</section>

<section class="section">
<div class="shell">
<div class="section-head">
<p class="eyebrow">Browse by topic</p>
<h2>按主题进入</h2>
<p class="section-desc">五个知识板块，加上一个完整的站点索引。每个入口都直接指向内容，而不是层层目录。</p>
</div>
<div class="topic-grid">%(topics)s</div>
</div>
</section>

<section class="section section-alt">
<div class="shell">
<div class="section-head">
<p class="eyebrow">Reading paths</p>
<h2>不知道从哪里开始？</h2>
<p class="section-desc">按照你的目的选择一条路径。每一步都可以单独阅读，也可以顺序读完。</p>
</div>
<div class="path-grid">%(paths)s</div>
</div>
</section>

<section class="section">
<div class="shell">
<div class="section-head section-head-row">
<div><p class="eyebrow">Instrument reviews</p><h2>仪器评测</h2></div>
<a class="text-link" href="reviews.html">全部评测 %(arrow)s</a>
</div>
<p class="section-desc">实际购买、借用或长期使用的记录。参数之外，也记录读数表现、方向特性与使用限制。</p>
<div class="review-grid review-grid-home">%(reviews)s</div>
</div>
</section>

<section class="section section-alt">
<div class="shell home-columns">
<div class="home-col">
<div class="section-head">
<p class="eyebrow">Changelog</p>
<h2>最近更新</h2>
</div>
<ol class="timeline timeline-compact">%(latest)s</ol>
<a class="text-link" href="changelog.html">完整更新日志 %(arrow)s</a>
</div>
<div class="home-col">
<div class="section-head">
<p class="eyebrow">Interactive tools</p>
<h2>工具</h2>
</div>
<div class="tool-list">%(tools)s</div>
<a class="text-link" href="tools.html">全部工具与数据 %(arrow)s</a>
</div>
</div>
</section>

<section class="section">
<div class="shell">
<div class="about-band">
<div class="about-band-main">
<p class="eyebrow">About this site</p>
<h2>一个个人维护的知识库</h2>
<p>我不是专家，所以可能会有错误。我搜集来自互联网的资料和参考其他网站的资料；技术内容尽量保留原始出处与测量条件，便于核对。</p>
<p>欢迎分享、链接到此页面（无需联系我）。如果发现错误或有希望补充的内容，请通过邮件联系。</p>
<div class="about-band-links">
<a class="button button-outline" href="about.html">关于本站</a>
<a class="text-link" href="mailto:XkXiaoYi475@outlook.com">XkXiaoYi475@outlook.com</a>
</div>
</div>
<div class="about-band-side">
<div class="stat"><span class="stat-value">%(c_basic)d</span><span class="stat-label">基础与生活</span></div>
<div class="stat"><span class="stat-value">%(c_measure)d</span><span class="stat-label">测量与仪器</span></div>
<div class="stat"><span class="stat-value">%(c_reviews)d</span><span class="stat-label">仪器评测</span></div>
<div class="stat"><span class="stat-value">%(c_tools)d</span><span class="stat-label">交互工具</span></div>
</div>
</div>
</div>
</section>
</main>""" % {
        "search_icon": T.icon("search"), "index_rows": "".join(index_rows),
        "topics": "".join(sections), "paths": "".join(path_cards),
        "reviews": review_cards, "latest": latest_html, "tools": tool_cards,
        "arrow": T.icon("arrow"),
        "c_basic": count_section("basics"), "c_measure": count_section("measurement"),
        "c_reviews": count_section("reviews"), "c_tools": count_section("tools"),
    }
    return T.page_shell(SITE["name"], SITE["description"], base, "", body, home=True)


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------

def render_about():
    base = ""
    body = """<main id="main" class="page page-about">
<div class="shell">
%(breadcrumb)s
<header class="hub-head about-head">
<p class="kicker">About / 关于本站</p>
<h1>关于本站</h1>
<p class="hub-lede">辐射备忘录（原「辐射及辐射测量仪器备忘录」）是一个个人维护的辐射科学知识站点，收录基础概念、测量方法、仪器资料与评测，以及若干可以在浏览器中运行的小工具。</p>
</header>

<div class="about-grid">
<div class="about-main prose">
<h2 id="purpose">这个站点是什么</h2>
<p>网站主要提供有关辐射、辐射探测器、辐射测量仪器、核物理和相关工程技术的知识、文章、资料及参考信息。内容面向物理、核工程、核技术、辐射防护等专业的学生，从事辐射探测与核电子学工作的技术人员，也面向对核科学与辐射探测器感兴趣的技术爱好者，以及没有专业背景但希望了解辐射知识的普通读者。</p>
<p>原始内容来自 2022–2024 年间的个人笔记、公开资料与仪器使用记录。本次改版只重新组织导航与版式，保留全部原文、图片、链接与数据；没有为了视觉效果删减或改写技术内容。</p>

<h2 id="disclaimer">建站时的说明（原文）</h2>
<blockquote class="quote-block">
<p>有关此页及子页的内容<br>
我不是专家，所以可能会有错误<br>
我搜集来自互联网的资料和参考其他网站的资料<br>
本站为针对PC端设计的，所以移动设备可能会有兼容性问题<br>
如果您有任何疑问，请通过XkXiaoYi475@outlook.com与我联系。<br>
欢迎分享、链接到此页面（无需联系我）</p>
</blockquote>
<p class="note-inline">注：原文中“针对 PC 端设计”是建站时的情况。本次改版已重新实现响应式布局，手机、平板与桌面均可用；这些原文保留在此以便对照。</p>

<h2 id="contact">联系与分享</h2>
<p>邮箱：<a href="mailto:XkXiaoYi475@outlook.com">XkXiaoYi475@outlook.com</a>。也欢迎访问外部博客与数据库：<a href="http://blog.xkxiaoyi.ink/" class="external" target="_blank" rel="noopener noreferrer">blog.xkxiaoyi.ink</a>、<a href="http://database.xkxiaoyi.ink/" class="external" target="_blank" rel="noopener noreferrer">database.xkxiaoyi.ink</a>。</p>
<p>欢迎分享、链接到本站页面（无需联系）。</p>

<h2 id="static">技术说明</h2>
<p>本站是纯静态站点，只使用 HTML、CSS 与原生 JavaScript。没有后端服务、数据库、账号系统或构建步骤；可以直接放在任意静态文件托管空间中。站内搜索在浏览器本地完成，搜索索引是一个静态 JavaScript 文件，不会把查询内容发送到服务器。</p>
<ul>
<li>字体：使用操作系统自带的中英文字体，不依赖外部字体服务。</li>
<li>图标：站内 SVG 图标，无图标库依赖。</li>
<li>分析：保留原有的 Google Analytics（gtag.js）与 51.LA 统计代码；它们不影响页面内容，即使加载失败也不影响阅读。</li>
<li>嵌入内容：部分文章的 Bilibili / YouTube 视频来自外部服务，需要网络连接；无法加载时不影响正文。</li>
<li>交互工具：误差模拟、抖动模拟、射程计算与 WESViewer 全部在浏览器本地计算，不上传数据。</li>
</ul>

<h2 id="credits">版权与致谢</h2>
<p>%(copyright)s<br>%(credit)s</p>
<p>站内引用的外部资料、图片与商标归各自权利人所有。原始文章的措辞、实验数据与结论保持原样；如发现事实错误、过时信息或失效链接，请在邮件中指出，我会在核对后处理。</p>

<h2 id="history">版本与记录</h2>
<p>最近一次内容更新为 2024 年 6 月 28 日。完整的历史改动见 <a href="changelog.html">更新日志</a>，全部页面见 <a href="sitemap.html">站点地图</a>。</p>
</div>

<aside class="about-side">
<nav class="toc" aria-label="本页目录">
<p class="side-title">本页目录</p>
<ol class="toc-list">
<li class="toc-item"><a href="#purpose">这个站点是什么</a></li>
<li class="toc-item"><a href="#disclaimer">建站时的说明</a></li>
<li class="toc-item"><a href="#contact">联系与分享</a></li>
<li class="toc-item"><a href="#static">技术说明</a></li>
<li class="toc-item"><a href="#credits">版权与致谢</a></li>
<li class="toc-item"><a href="#history">版本与记录</a></li>
</ol>
</nav>
<div class="side-block">
<p class="side-title">站点信息</p>
<dl class="facts-list">
<dt>起始</dt><dd>2022 年</dd>
<dt>内容更新</dt><dd>2024/6/28</dd>
<dt>架构</dt><dd>纯静态 HTML</dd>
<dt>搜索</dt><dd>浏览器本地索引</dd>
</dl>
</div>
</aside>
</div>
</div>
</main>""" % {
        "breadcrumb": T.breadcrumb(base, [("首页", "index.html"), ("关于本站", None)]),
        "copyright": esc(SITE["copyright"]), "credit": SITE["credit"],
    }
    return T.page_shell("关于本站", "辐射备忘录的站点说明、联系方式、技术实现、版权与更新记录。", base, "about", body)


# ---------------------------------------------------------------------------
# Search page
# ---------------------------------------------------------------------------

def render_search_page():
    base = ""
    body = """<main id="main" class="page page-search">
<div class="shell">
%(breadcrumb)s
<header class="hub-head search-head">
<p class="kicker">Search / 站内搜索</p>
<h1>搜索</h1>
<p class="hub-lede">输入文章标题、仪器型号、核素名称或技术关键词。搜索在浏览器本地完成，不会上传查询内容。</p>
<form class="search-form search-form-large" action="search.html" method="get" role="search" data-search-page-form>
%(icon)s
<label class="sr-only" for="search-page-input">搜索关键词</label>
<input id="search-page-input" type="search" name="q" placeholder="例如：能量补偿、氡、Cs-137、PM1405" autocomplete="off" data-search-page-input>
<button type="submit" class="button button-solid">搜索</button>
</form>
<div class="quick-links">
<span>试试</span>
<a href="search.html?q=希沃特">希沃特</a>
<a href="search.html?q=能量补偿">能量补偿</a>
<a href="search.html?q=氡">氡</a>
<a href="search.html?q=Cs-137">Cs-137</a>
<a href="search.html?q=PM1405">PM1405</a>
<a href="search.html?q=能谱">能谱</a>
</div>
</header>
<div class="search-page-body" data-search-page-results>
<noscript><p>搜索需要 JavaScript。你也可以直接从 <a href="sitemap.html">站点地图</a> 浏览全部页面。</p></noscript>
<p class="muted">正在准备搜索索引…</p>
</div>
</div>
</main>""" % {
        "breadcrumb": T.breadcrumb(base, [("首页", "index.html"), ("搜索", None)]),
        "icon": T.icon("search"),
    }
    return T.page_shell("搜索", "搜索辐射备忘录的文章、仪器评测、核素资料与工具。", base, "", body)


# ---------------------------------------------------------------------------
# Sitemap
# ---------------------------------------------------------------------------

def render_sitemap():
    base = ""
    groups = [
        ("门户与索引", [
            ("index.html", "首页"),
            ("base.html", "基础知识"),
            ("info/index.html", "测量与仪器"),
            ("reviews.html", "仪器评测"),
            ("article.html", "文章与笔记"),
            ("other/index.html", "其他与专题"),
            ("tools.html", "工具与数据"),
            ("about.html", "关于本站"),
            ("search.html", "搜索"),
            ("changelog.html", "更新日志"),
            ("sitemap.html", "站点地图"),
        ]),
        ("基础知识", [(r, PAGES[r]["title"]) for r in section_pages("basics")]),
        ("测量与仪器", [(r, PAGES[r]["title"]) for r in section_pages("measurement")]),
        ("仪器评测", [(r, PAGES[r]["title"]) for r in section_pages("reviews")]),
        ("文章与笔记", [(r, PAGES[r]["title"]) for r in section_pages("articles")] +
         [("修正关于KB6011型辐射计能量响应的方案.pdf", "修正关于 KB6011 型辐射计能量响应的方案（PDF）")]),
        ("工具与数据", [(r, PAGES[r]["title"]) for r in section_pages("tools")] +
         [(r, (find_meta(r) or {}).get("title", r)) for r in WES_GALLERY] +
         [(r, "WESViewer · " + (find_meta(r) or {}).get("title", r)) for r in WES_VIEWERS]),
        ("关于与存档", [(r, PAGES[r]["title"]) for r in section_pages("about")] +
         [(r, PAGES[r]["title"]) for r in section_pages("archive")]),
    ]
    total = sum(len(items) for _, items in groups)
    blocks = []
    for title, items in groups:
        links = "".join('<li><a href="%s%s">%s</a></li>' % (base, esc(rel), esc(label)) for rel, label in items)
        blocks.append("""<section class="sitemap-group">
<div class="group-head"><h2>%s</h2><span class="group-count">%d 个页面</span></div>
<ul class="sitemap-list">%s</ul>
</section>""" % (esc(title), len(items), links))
    body = """<main id="main" class="page page-sitemap">
<div class="shell">
%(breadcrumb)s
<header class="hub-head">
<p class="kicker">Index / 站点地图</p>
<h1>全部页面</h1>
<p class="hub-lede">这里列出站内全部 HTML 页面与 PDF 文档，包括为兼容旧链接而保留的存档页面。共 %(total)d 项。</p>
<div class="hub-meta"><span>%(pages)d 个 HTML 页面</span><span>1 个 PDF</span><span>无孤立页面</span></div>
</header>
%(blocks)s
</div>
</main>""" % {
        "breadcrumb": T.breadcrumb(base, [("首页", "index.html"), ("站点地图", None)]),
        "total": total, "pages": total - 1, "blocks": "".join(blocks),
    }
    return T.page_shell("站点地图", "辐射备忘录全部页面、文章、工具与存档页面的索引。", base, "", body)


# ---------------------------------------------------------------------------
# Changelog
# ---------------------------------------------------------------------------

def render_changelog():
    base = ""
    entries = load_changelog()
    blocks = []
    current_year = None
    current = []
    for entry in entries:
        year = entry["date"].split("/")[0] if entry["date"] else "更早"
        if year != current_year:
            if current:
                blocks.append((current_year, current))
            current_year = year
            current = []
        current.append(entry)
    if current:
        blocks.append((current_year, current))
    groups = []
    for year, items in blocks:
        lis = []
        for item in items:
            lis.append(log_item(item, base, show_link=True))
        groups.append("""<section class="log-year">
<h2>%s</h2>
<ol class="timeline">%s</ol>
</section>""" % (esc(year if year != "更早" else "更早／未注明日期"), "".join(lis)))
    body = """<main id="main" class="page page-changelog">
<div class="shell">
%(breadcrumb)s
<header class="hub-head">
<p class="kicker">Changelog / 更新日志</p>
<h1>更新日志</h1>
<p class="hub-lede">这份日志合并了旧版首页的更新记录与“先前的更新历史”页面。原始措辞、日期与其中的笔误均按原样保留。</p>
<div class="hub-meta"><span>%(count)d 条记录</span><span>2022–2024</span><a class="text-link" href="history.html">2022–2023 单独页面 %(arrow)s</a></div>
</header>
<div class="log-wrap">%(groups)s</div>
</div>
</main>""" % {
        "breadcrumb": T.breadcrumb(base, [("首页", "index.html"), ("更新日志", None)]),
        "count": len(entries), "groups": "".join(groups), "arrow": T.icon("arrow"),
    }
    return T.page_shell("更新日志", "辐射备忘录 2022–2024 年的全部更新记录。", base, "about", body)
