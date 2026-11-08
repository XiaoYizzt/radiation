# -*- coding: utf-8 -*-
"""Build the static site from the legacy pages plus the new editorial layer."""

import html as htmllib
import json
import os
import re
from collections import OrderedDict

from lxml import html

import content as C
import templates as T
from site_data import (FEATURED_REVIEWS, PAGES, PATHS, SECTIONS, SITE,
                       SUBSECTIONS, WES_GALLERY, WES_VIEWERS, GENERATED_HUBS)

ROOT = C.ROOT
DATE_TAIL = re.compile(r"[（(]?\s*(\d{2,4}\s*[/.\-]\s*\d{1,2}\s*[/.\-]\s*\d{1,2})\s*[)）]?\s*$")


def esc(value):
    return htmllib.escape(str(value), quote=True)


def base_for(rel):
    return "../" * rel.count("/")


def rel_href(base, path):
    return base + path


def read_time(text):
    cjk = len(re.findall(r"[\u3400-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z0-9]+", text))
    minutes = max(1, round(cjk / 380 + latin / 180))
    return minutes


def tool_scripts(rel):
    """Re-attach the original local scripts of an interactive tool page.

    Analytics and social-button loaders are dropped (the new shell includes
    the site analytics); jQuery/Flot and the inline calculator code are kept
    exactly as published so the tools continue to work.
    """
    raw = C.read_original(rel)
    blocks = re.findall(r"<script\b([^>]*)>(.*?)</script\s*>", raw, re.S | re.I)
    output = []
    for attrs, body in blocks:
        src_match = re.search(r"src\s*=\s*[\"']([^\"']+)[\"']", attrs, re.I)
        if src_match:
            src = src_match.group(1)
            low = src.lower()
            if any(token in low for token in ("googletagmanager", "51.la", "socialbutton",
                                               "analytics", "excanvas")):
                continue
            output.append('<script src="%s"></script>' % esc(src))
            continue
        low = body.lower()
        if any(token in low for token in ("_gaq", "gtag(", "la_collect", "datalayer")):
            continue
        output.append("<script>%s</script>" % body)
    return "\n".join(output)


def section_pages(sid):
    return [rel for rel, meta in PAGES.items()
            if meta.get("section") == sid and meta.get("kind") != "pdf"]


def find_meta(rel):
    if rel in PAGES:
        return PAGES[rel]
    if rel in WES_GALLERY:
        title, item, note = WES_GALLERY[rel]
        return dict(title=title, card=title, section="tools", sub="spectrum",
                    level="进阶", tags=["WESViewer", title], summary=note or item,
                    tool=True)
    if rel in WES_VIEWERS:
        title, isotope, note = WES_VIEWERS[rel]
        return dict(title=title, card=title, section="tools", sub="spectrum",
                    level="进阶", tags=["WESViewer", isotope], summary="WESViewer 光谱查看页面：%s。" % isotope,
                    tool=True)
    return None


def card_image(meta, base):
    image = meta.get("image")
    if not image:
        return ""
    if image.startswith(("http://", "https://")):
        src = image
    else:
        src = base + image
    return '<img src="%s" alt="" loading="lazy" decoding="async">' % esc(src)


def level_badge(level):
    if not level:
        return ""
    return '<span class="badge badge-%s">%s</span>' % (
        {"入门": "intro", "进阶": "mid", "专业": "pro"}.get(level, "mid"), esc(level))


def entry_card(rel, meta, base, show_image=False):
    href = base + rel
    date = ('<span class="meta-dot">·</span><time>%s</time>' % esc(meta["date"])) if meta.get("date") else ""
    image = card_image(meta, base) if show_image and meta.get("image") else ""
    thumb = ('<a class="entry-thumb" href="%s" tabindex="-1" aria-hidden="true">%s</a>' % (href, image)) if image else ""
    return """<article class="entry-card%(has_thumb)s">
%(thumb)s
<div class="entry-body">
<p class="entry-kicker">%(sub)s %(level)s</p>
<h3><a href="%(href)s">%(title)s</a></h3>
<p>%(summary)s</p>
<div class="entry-meta"><span class="read-time">阅读约 %(minutes)d 分钟</span>%(date)s</div>
</div>
</article>""" % {
        "has_thumb": " has-thumb" if thumb else "",
        "thumb": thumb,
        "sub": esc(SUBSECTIONS.get(meta.get("sub"), "")),
        "level": level_badge(meta.get("level")),
        "href": esc(href),
        "title": esc(meta["title"]),
        "summary": esc(meta["summary"]),
        "minutes": meta.get("minutes") or read_time(meta["summary"]),
        "date": date,
    }


def review_card(rel, meta, base):
    href = base + rel
    specs = "".join("<li>%s</li>" % esc(spec) for spec in meta.get("specs", []))
    return """<article class="review-card">
<a class="review-thumb" href="%(href)s" tabindex="-1" aria-hidden="true">%(image)s</a>
<div class="review-body">
<p class="entry-kicker">%(sub)s%(date)s</p>
<h3><a href="%(href)s">%(title)s</a></h3>
<p>%(summary)s</p>
<ul class="spec-list-inline">%(specs)s</ul>
</div>
</article>""" % {
        "href": esc(href), "image": card_image(meta, base),
        "sub": esc(SUBSECTIONS.get(meta.get("sub"), "仪器评测")),
        "date": ('<span class="meta-dot">·</span><time>%s</time>' % esc(meta["date"])) if meta.get("date") else "",
        "title": esc(meta["title"]), "summary": esc(meta["summary"]),
        "specs": specs,
    }


def tool_card(rel, meta, base):
    href = base + rel
    return """<article class="tool-card">
<div class="tool-icon">%(icon)s</div>
<div class="tool-body">
<p class="entry-kicker">%(sub)s</p>
<h3><a href="%(href)s">%(title)s</a></h3>
<p>%(summary)s</p>
<span class="tool-open">打开工具 %(arrow)s</span>
</div>
</article>""" % {
        "icon": T.icon(T.SUBSECTION_ICONS.get(meta.get("sub"), "tools")),
        "sub": esc(SUBSECTIONS.get(meta.get("sub"), "工具")),
        "href": esc(href), "title": esc(meta["title"]), "summary": esc(meta["summary"]),
        "arrow": T.icon("arrow"),
    }


def pdf_card(meta, base):
    href = base + "修正关于KB6011型辐射计能量响应的方案.pdf"
    return """<article class="entry-card has-thumb">
<a class="entry-thumb pdf-thumb" href="%(href)s" tabindex="-1" aria-hidden="true">%(icon)s</a>
<div class="entry-body">
<p class="entry-kicker">研究文档 · PDF <img class="legacy-icon" src="%(base)simg/pdf.png" width="14" height="14" alt="" loading="lazy"></p>
<h3><a href="%(href)s">%(title)s</a></h3>
<p>%(summary)s</p>
<div class="entry-meta"><span>1.0 MB</span><span class="meta-dot">·</span><span>2024/6/28</span></div>
</div>
</article>""" % {"href": esc(href), "base": base, "icon": T.icon("pdf", "icon icon-lg"),
                  "title": esc(meta["title"]), "summary": esc(meta["summary"])}


def article_card(rel, meta, base, thumb=False):
    if meta.get("section") == "reviews":
        return review_card(rel, meta, base)
    if meta.get("tool"):
        return tool_card(rel, meta, base)
    if meta.get("kind") == "pdf":
        return pdf_card(meta, base)
    return entry_card(rel, meta, base, show_image=thumb)


# ---------------------------------------------------------------------------
# Article / tool page
# ---------------------------------------------------------------------------

def toc_html(toc, base=""):
    items = []
    for item in toc:
        cls = "toc-item toc-l%d" % (item["level"] + 2)
        items.append('<li class="%s"><a href="#%s">%s</a></li>' % (
            cls, esc(item["id"]), esc(item["text"])))
    return '<ol class="toc-list">%s</ol>' % "".join(items)


def render_article(rel, meta, prev_link=None, next_link=None):
    base = base_for(rel)
    data = C.extract(rel, meta["title"])
    toc = data["toc"]
    section = SECTIONS.get(meta.get("section"), SECTIONS["articles"])
    hub = section["hub"]
    read = read_time(re.sub(r"<[^>]+>", "", data["text"]))
    note = "".join(data["title_notes"])
    date_line = ""
    if meta.get("date"):
        date_line = '<span class="meta-item"><time datetime="%s">更新于 %s</time></span>' % (
            esc(meta["date"].replace("/", "-")), esc(meta["date"]))
    title_note = ('<p class="title-note">%s</p>' % esc(note)) if note else ""

    notice = ""
    if meta.get("canonical"):
        canonical = meta["canonical"]
        canonical_meta = PAGES.get(canonical, {})
        notice = """<aside class="notice notice-archive">
<strong>这是为兼容旧链接保留的存档页面。</strong>
<p>内容与 <a href="%(base)s%(canonical)s">%(ctitle)s</a> 相同；推荐阅读该页面以获得最新的版式与目录。</p>
</aside>""" % {"base": base, "canonical": esc(canonical),
               "ctitle": esc(canonical_meta.get("title", canonical))}
    elif meta.get("section") == "archive":
        notice = """<aside class="notice notice-archive">
<strong>存档页面</strong>
<p>本页保留自旧版站点，仅用于兼容历史链接与记录。它不属于主要的阅读路径，部分外部资源可能已经失效。</p>
</aside>"""

    related = [r for r in section_pages(meta.get("section"))
               if r != rel and PAGES[r].get("sub") == meta.get("sub")][:4]
    related_html = "".join('<li><a href="%s%s"><span>%s</span>%s</a></li>' % (
        base, esc(r), esc(PAGES[r]["title"]), T.icon("arrow")) for r in related[:3])

    aside = ""
    if len(toc) >= 2 or related:
        toc_block = ""
        if len(toc) >= 2:
            toc_block = """<nav class="toc" aria-label="本页目录" data-toc>
<p class="side-title">本页目录</p>
%(toc)s
</nav>""" % {"toc": toc_html(toc)}
        related_block = ""
        if related:
            related_block = """<div class="side-block">
<p class="side-title">同主题阅读</p>
<ul class="side-links">%(items)s</ul>
</div>""" % {"items": related_html}
        aside = """<aside class="article-side">
%(toc)s
%(related)s
%(back)s
</aside>""" % {"toc": toc_block, "related": related_block,
               "back": ('<a class="side-back" href="%s%s">← 返回%s</a>' % (base, esc(hub), esc(section["label"])))
                       if toc_block else ""}

    inline_toc = ""
    if len(toc) >= 2:
        inline_toc = """<details class="toc-inline">
<summary>本页目录 <span>%(count)d 节</span></summary>
%(toc)s
</details>""" % {"count": len(toc), "toc": toc_html(toc)}

    pager = ""
    if prev_link or next_link:
        prev_html = ""
        next_html = ""
        if prev_link:
            pr, pm = prev_link
            prev_html = """<a class="pager-link pager-prev" href="%(base)s%(rel)s">
<span>上一篇</span><strong>%(title)s</strong>
</a>""" % {"base": base, "rel": esc(pr), "title": esc(pm["title"])}
        if next_link:
            nr, nm = next_link
            next_html = """<a class="pager-link pager-next" href="%(base)s%(rel)s">
<span>下一篇</span><strong>%(title)s</strong>
</a>""" % {"base": base, "rel": esc(nr), "title": esc(nm["title"])}
        pager = '<nav class="pager" aria-label="上下篇">%s%s</nav>' % (prev_html, next_html)

    body = """<main id="main" class="page page-article%(tool)s">
<div class="shell">
%(breadcrumb)s
<div class="article-grid%(wide)s">
<article class="article">
<header class="article-head">
<p class="kicker"><a href="%(base)s%(hub)s">%(section)s</a><span class="kicker-sep">/</span><span>%(sub)s</span></p>
<h1>%(title)s</h1>
%(title_note)s
<div class="article-meta">
<span class="meta-item">%(clock)s %(reading_label)s</span>
%(date)s
%(level)s
</div>
%(tags)s
</header>
%(toc_inline)s
%(tool_cta)s
%(notice)s
<div class="prose" data-prose>
%(content)s
</div>
<footer class="article-foot">
%(pager)s
<div class="article-back">
<a href="%(base)s%(hub)s">← 返回%(section)s</a>
<a href="#main">回到顶部 ↑</a>
</div>
</footer>
</article>
%(aside)s
</div>
</div>
</main>""" % {
        "tool": " page-tool" if meta.get("tool") else "",
        "breadcrumb": T.breadcrumb(base, [("首页", "index.html"), (section["label"], hub), (meta["title"], None)]),
        "wide": " article-grid--wide" if meta.get("wide") or not aside else "",
        "base": base, "hub": esc(hub), "section": esc(section["label"]),
        "sub": esc(SUBSECTIONS.get(meta.get("sub"), "")),
        "title": esc(meta["title"]), "title_note": title_note,
        "clock": T.icon("clock"),
        "minutes": read,
        "reading_label": "光谱案例" if meta.get("kind") == "gallery" else ("阅读约 %d 分钟" % read),
        "date": date_line,
        "level": "" if meta.get("kind") == "gallery" else level_badge(meta.get("level")),
        "tags": T.tag_list(meta.get("tags", [])),
        "toc_inline": inline_toc, "notice": notice, "content": data["html"],
        "tool_cta": ('<div class="tool-cta"><a class="button button-solid" href="wesviewer/index.html">打开光谱查看器</a><span>读取本地 XML 光谱数据，或浏览已有案例。</span></div>')
                    if rel == "tool/WESViewer/index.html" else "",
        "pager": pager, "aside": aside,
    }
    description = meta.get("summary") or SITE["description"]
    extra = tool_scripts(rel) if meta.get("tool") and rel != "tool/WESViewer/index.html" else ""
    return T.page_shell(meta["title"], description, base, meta.get("section"), body,
                        body_class="page-tool" if meta.get("tool") else "",
                        extra_scripts=extra)


# ---------------------------------------------------------------------------
# Section hubs
# ---------------------------------------------------------------------------

HUB_INTROS = {
    "basics": ("基础知识。在开始研究辐射及仪器等之前，推荐来看看。", "我会一条条增加页面。"),
    "measurement": ("关于辐射和辐射测量仪器的说明。", "我会根据我研究过的资料描述我可能会犯错误或有疑问的事情。我搜集来自互联网的资料和参考其他网站的资料，我会一条条增加页面。"),
    "articles": ("关于辐射和辐射探测器的文章。我会在这里写一些与辐射和辐射测量仪器有关的事。", "实验记录、采购笔记、核素故事与站点回顾。"),
    "reviews": ("这里收录的是实际购买、借用或长期使用的仪器记录，而不是参数表的复述。", "每篇评测尽量说明测试条件与局限；不同批次的设备可能存在差异。"),
    "tools": ("这些工具全部在浏览器中运行，不需要安装软件，也不上传数据。", "能谱查看器读取本地 XML 文件；模拟工具使用 JavaScript 在本地计算。"),
    "archive": ("这些页面为兼容旧链接而保留，不属于主要阅读路径。", "部分页面存在重复内容或已经失效的外部资源，原样保留以便核对。"),
}

HUB_SUBS = {
    "basics": ["units", "life", "shielding", "medical"],
    "measurement": ["usage", "dose", "instruments"],
    "reviews": ["gm", "scint", "semi"],
    "articles": ["fieldnotes", "nuclei", "research", "site"],
    "tools": ["spectrum", "simulation", "reference"],
    "archive": ["legacy"],
}


def render_hub(rel, sid):
    base = base_for(rel)
    section = SECTIONS[sid]
    pages = [r for r in section_pages(sid)]
    if rel == "other/index.html":
        pages = [r for r in pages if r.startswith(("other/", "tips/", "net.html")) or r in ("net.html",)]
    page_title = "其他与专题" if rel == "other/index.html" else section["label"]
    intro = HUB_INTROS.get(sid, ("", ""))
    if rel == "other/index.html":
        intro = ("其他知识，可以看，不看也没有影响。", "当然我推荐看一下我的博客。")
    subs = [s for s in HUB_SUBS.get(sid, []) if any(PAGES[r].get("sub") == s for r in pages)]
    groups = []
    quick = []
    for sub in subs:
        items = [r for r in pages if PAGES[r].get("sub") == sub]
        if not items:
            continue
        quick.append('<a class="chip" href="#%s">%s <span>%d</span></a>' % (
            esc(sub), esc(SUBSECTIONS.get(sub, sub)), len(items)))
        cards = []
        for r in items:
            meta = PAGES[r]
            if sid == "reviews":
                cards.append(review_card(r, meta, base))
            elif sid == "tools":
                cards.append(tool_card(r, meta, base))
            elif meta.get("kind") == "pdf":
                cards.append(pdf_card(meta, base))
            else:
                cards.append(entry_card(r, meta, base))
        grid_class = "card-grid"
        if sid == "reviews":
            grid_class += " review-grid"
        elif sid == "tools":
            grid_class += " tool-grid"
        groups.append("""<section class="listing-group" id="%(sub)s">
<div class="group-head">
<h2>%(title)s</h2>
<span class="group-count">%(count)d 篇</span>
</div>
<div class="%(grid)s">%(cards)s</div>
</section>""" % {
            "sub": esc(sub), "title": esc(SUBSECTIONS.get(sub, sub)),
            "count": len(items), "grid": grid_class, "cards": "".join(cards),
        })

    total = len(pages) + (1 if sid == "articles" else 0)
    # The PDF is part of the article section but is not an HTML page.
    if sid == "articles" and rel != "other/index.html":
        groups.append("""<section class="listing-group" id="research">
<div class="group-head"><h2><img class="legacy-icon" src="%(base)simg/book.png" width="18" height="18" alt="" loading="lazy"> 研究文档</h2><span class="group-count">1 篇</span></div>
<div class="card-grid">%(cards)s</div>
</section>""" % {"base": base, "cards": pdf_card(PAGES["修正关于KB6011型辐射计能量响应的方案.pdf"], base)})
        total = len(pages) + 1

    if rel == "other/index.html":
        total = len(pages)

    if sid == "articles" and rel == "other/index.html":
        groups.append("""<section class="listing-group" id="external">
<div class="group-head"><h2>外部链接</h2><span class="group-count">2 个链接</span></div>
<div class="card-grid">
<article class="entry-card"><p class="entry-kicker">外部博客</p><h3><a href="http://blog.xkxiaoyi.ink/" class="external" target="_blank" rel="noopener noreferrer">放射性博客（辐射来源、小实验、老机型评测）</a></h3><p>原「Other」页推荐的外部博客。</p></article>
<article class="entry-card"><p class="entry-kicker">外部数据库</p><h3><a href="http://database.xkxiaoyi.ink/" class="external" target="_blank" rel="noopener noreferrer">数据库（镜像）</a></h3><p>核数据与辐射资料的镜像入口。</p></article>
</div>
</section>""")

    if sid == "reviews" and rel == "reviews.html":
        groups.append("""<section class="listing-group" id="external">
<div class="group-head"><h2>外部评测</h2><span class="group-count">1 个链接</span></div>
<div class="card-grid">
<article class="entry-card">
<p class="entry-kicker">外部博客</p>
<h3><a href="https://blog.xkxiaoyi.ink/content/blog7.html" class="external" target="_blank" rel="noopener noreferrer">FJJ03 型个人剂量仪（链接至博客）</a></h3>
<p>站外的一篇仪器评测，按原站点目录保留链接。</p>
</article>
</div>
</section>""")

    if sid == "measurement" and rel == "info/index.html":
        groups.append("""<section class="listing-group" id="related-basics">
<div class="group-head"><h2>相关基础阅读</h2><span class="group-count">1 篇</span></div>
<div class="card-grid"><article class="entry-card">
<p class="entry-kicker">基础知识 · 屏蔽与衰减</p>
<h3><a href="%(base)sPB_gamma.html">辐射衰减（γ射线）</a></h3>
<p>点源、线源与平面源的距离衰减规律，以及屏蔽中「数量减少而非能量减少」的含义。</p>
<p><a class="text-link" href="%(base)sPB_gamma.html">阅读 %(arrow)s</a></p>
</article></div>
</section>""" % {"base": base, "arrow": T.icon("arrow")})
        tool_rels = ["tool/error simulation.html", "tool/jitter simulation.html",
                     "tool/beta ray range calculation.html", "tool/info004.html"]
        tools_html = "".join(tool_card(r, PAGES[r], base) for r in tool_rels)
        groups.append("""<section class="listing-group" id="related-tools">
<div class="group-head"><h2>测量与计算工具</h2><span class="group-count">4 个工具</span></div>
<div class="tool-grid">%s</div>
</section>""" % tools_html)

    subcount = len(subs)
    if sid == "articles" and rel != "other/index.html":
        subcount += 1
    if sid == "articles" and rel == "other/index.html":
        subcount += 1
    if sid == "measurement" and rel == "info/index.html":
        subcount += 2
    if sid == "reviews" and rel == "reviews.html":
        subcount += 1

    chip_bar = ""
    if quick:
        chip_bar = '<nav class="chip-bar" aria-label="本页分组">%s</nav>' % "".join(quick)

    hub_actions = ""
    if sid == "articles":
        if rel == "other/index.html":
            hub_actions = '<a class="text-link" href="%sarticle.html">全部文章 %s</a>' % (base, T.icon("arrow"))
        else:
            hub_actions = '<a class="text-link" href="%sother/index.html">其他与专题 %s</a>' % (base, T.icon("arrow"))
    elif sid == "measurement":
        hub_actions = '<a class="text-link" href="%sdetector.html">仪器类型 %s</a>' % (base, T.icon("arrow"))

    body = """<main id="main" class="page page-hub">
<div class="shell">
%(breadcrumb)s
<header class="hub-head">
<p class="kicker">%(number)s / 知识板块</p>
<h1>%(title)s</h1>
<p class="hub-lede">%(blurb)s</p>
<div class="hub-intro"><p>%(intro1)s</p><p class="muted">%(intro2)s</p></div>
<div class="hub-meta"><span>%(total)d 篇内容</span><span>%(subcount)d 个分组</span>%(actions)s</div>
%(chips)s
</header>
%(groups)s
<div class="hub-foot">
<a class="text-link" href="%(base)ssitemap.html">查看全部页面 %(arrow)s</a>
</div>
</div>
</main>""" % {
        "breadcrumb": (T.breadcrumb(base, [("首页", "index.html"), (section["label"], "article.html"), (page_title, None)])
                       if rel == "other/index.html"
                       else T.breadcrumb(base, [("首页", "index.html"), (section["label"], None)])),
        "number": section["number"], "title": esc(page_title),
        "blurb": esc(section["blurb"]),
        "intro1": esc(intro[0]), "intro2": esc(intro[1]),
        "total": total, "subcount": subcount, "actions": hub_actions,
        "chips": chip_bar, "groups": "".join(groups), "base": base,
        "arrow": T.icon("arrow"),
    }
    return T.page_shell(page_title, section["blurb"], base, sid, body)
