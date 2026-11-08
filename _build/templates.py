# -*- coding: utf-8 -*-
"""Shared HTML chrome for the rebuilt site."""

import html as htmllib

from site_data import FOOTER_GROUPS, NAV_ORDER, SECTIONS, SITE

ICON_PATHS = {
    "atom": '<circle cx="12" cy="12" r="1.9" fill="currentColor" stroke="none"/>'
            '<ellipse cx="12" cy="12" rx="9.4" ry="3.9"/>'
            '<ellipse cx="12" cy="12" rx="9.4" ry="3.9" transform="rotate(60 12 12)"/>'
            '<ellipse cx="12" cy="12" rx="9.4" ry="3.9" transform="rotate(120 12 12)"/>',
    "gauge": '<path d="M4 17a8 8 0 1 1 16 0"/><path d="M12 17l4.2-5.2"/>'
             '<circle cx="12" cy="17" r="1.2" fill="currentColor" stroke="none"/>'
             '<path d="M4 20h4M16 20h4"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11"/>'
            '<circle cx="4.5" cy="6" r="1" fill="currentColor" stroke="none"/>'
            '<circle cx="4.5" cy="12" r="1" fill="currentColor" stroke="none"/>'
            '<circle cx="4.5" cy="18" r="1" fill="currentColor" stroke="none"/>',
    "book": '<path d="M12 6.5C10.2 5.2 7.8 4.7 4.5 4.9v13.3c3.3-.2 5.7.3 7.5 1.6 1.8-1.3 4.2-1.8 7.5-1.6V4.9c-3.3-.2-5.7.3-7.5 1.6z"/>'
            '<path d="M12 6.5v13.3"/>',
    "tools": '<path d="M4 7h9M17 7h3M4 17h3M11 17h9"/>'
             '<circle cx="15" cy="7" r="2.2"/><circle cx="9" cy="17" r="2.2"/>',
    "info": '<circle cx="12" cy="12" r="8.5"/><path d="M12 11v5.3"/>'
            '<circle cx="12" cy="7.9" r="1" fill="currentColor" stroke="none"/>',
    "archive": '<path d="M4 8.5V19h16V8.5"/><path d="M3 5h18v3.5H3z"/><path d="M9.5 12h5"/>',
    "search": '<circle cx="10.8" cy="10.8" r="6.3"/><path d="M15.5 15.5L21 21"/>',
    "arrow": '<path d="M4 12h15M13 6l6 6-6 6"/>',
    "external": '<path d="M9 5h10v10"/><path d="M19 5L8 16"/><path d="M15 14v5H5V9h5"/>',
    "chevron": '<path d="M9 5l7 7-7 7"/>',
    "shield": '<path d="M12 3l7 3v6c0 4.2-2.8 7.4-7 9-4.2-1.6-7-4.8-7-9V6z"/>'
              '<path d="M9.5 12l1.8 1.8 3.4-3.6"/>',
    "spectrum": '<path d="M4 19V9M8 19V5M12 19V11M16 19V3M20 19v-7"/>',
    "medical": '<path d="M12 4v16M4 12h16"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6L6 18"/>',
    "pdf": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/>'
           '<path d="M9 13h6M9 17h4"/>',
    "download": '<path d="M12 4v10M8 10l4 4 4-4"/><path d="M5 19h14"/>',
}

SUBSECTION_ICONS = {
    "units": "gauge", "life": "atom", "shielding": "shield", "medical": "medical",
    "usage": "gauge", "dose": "spectrum", "instruments": "list",
    "gm": "gauge", "scint": "spectrum", "semi": "atom",
    "fieldnotes": "book", "nuclei": "atom", "research": "pdf", "site": "info",
    "spectrum": "spectrum", "simulation": "tools", "reference": "list",
    "legacy": "archive",
}


def esc(value):
    return htmllib.escape(str(value), quote=True)


def icon(name, cls="icon"):
    path = ICON_PATHS.get(name, ICON_PATHS["info"])
    return ('<svg class="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
            'aria-hidden="true">%s</svg>') % (cls, path)


def head(title, description, base, extra_head="", page_type="website", body_class=""):
    is_home = title == SITE["name"]
    doc_title = ("%s · 辐射、探测器与测量" % SITE["name"]) if is_home else ("%s · %s" % (title, SITE["name"]))
    return """<!DOCTYPE html>
<html lang="zh-CN" data-base="%(base)s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(doc_title)s</title>
<meta name="description" content="%(desc)s">
<meta name="theme-color" content="#f5f4ef">
<meta property="og:type" content="%(page_type)s">
<meta property="og:site_name" content="%(site)s">
<meta property="og:title" content="%(doc_title)s">
<meta property="og:description" content="%(desc)s">
<link rel="icon" href="%(base)simg/icon.png" sizes="512x512">
<link rel="stylesheet" href="%(base)scss/site.css">
<!-- Existing site analytics, kept from the original pages. -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-YGG4B16Z2G"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-YGG4B16Z2G');
</script>
%(extra_head)s
</head>
<body class="%(body_class)s">
<a class="skip-link" href="#main">跳到主要内容</a>
""" % {
        "base": base, "doc_title": esc(doc_title), "desc": esc(description),
        "site": esc(SITE["name_full"]), "page_type": page_type,
        "extra_head": extra_head,
        "body_class": body_class or ("is-home" if is_home else ""),
    }


def brand(base, compact=False):
    return """<a class="brand" href="%(base)sindex.html" aria-label="%(name)s 首页">
<span class="brand-mark" aria-hidden="true">%(icon)s</span>
<span class="brand-text"><strong>%(name)s</strong><span class="brand-sub">%(tagline)s</span></span>
</a>""" % {"base": base, "name": esc(SITE["name"]), "tagline": esc(SITE["tagline"]),
            "icon": icon("atom")}


def nav_link(base, sid, active):
    section = SECTIONS[sid]
    current = ' aria-current="page"' if sid == active else ""
    return '<a href="%s%s"%s>%s</a>' % (base, section["hub"], current, esc(section["nav"]))


def header(base, active="", home=False):
    home_current = ' aria-current="page"' if home else ""
    links = "".join(nav_link(base, sid, active) for sid in NAV_ORDER)
    mobile_links = "".join(nav_link(base, sid, active) for sid in NAV_ORDER)
    return """<header class="site-header" data-header>
<div class="shell header-inner">
%(brand)s
<nav class="primary-nav" aria-label="主导航">
<a href="%(base)sindex.html"%(home_current)s>首页</a>
%(links)s
</nav>
<div class="header-tools">
<a class="search-link" href="%(base)ssearch.html" data-search-open aria-label="搜索本站">
%(search_icon)s<span class="search-link-text">搜索</span><kbd class="key-hint">/</kbd>
</a>
<details class="nav-drawer" data-nav-drawer>
<summary class="nav-toggle" aria-label="打开菜单">%(menu_icon)s<span>菜单</span></summary>
<div class="nav-panel">
<nav aria-label="移动端导航">
<a href="%(base)sindex.html"%(home_current)s>首页</a>
%(mobile_links)s
</nav>
<a class="nav-panel-search" href="%(base)ssearch.html" data-search-open>%(search_icon)s 搜索文章与仪器</a>
<div class="nav-panel-meta">
<a href="%(base)ssitemap.html">全部页面</a>
<a href="%(base)sabout.html">关于本站</a>
</div>
</div>
</details>
</div>
</div>
</header>
""" % {
        "brand": brand(base), "base": base, "links": links, "mobile_links": mobile_links,
        "home_current": home_current, "search_icon": icon("search"),
        "menu_icon": icon("menu"),
    }


def breadcrumb(base, items):
    parts = []
    for index, (label, href) in enumerate(items):
        if index:
            parts.append('<span class="crumb-sep" aria-hidden="true">/</span>')
        if href:
            parts.append('<a href="%s%s">%s</a>' % (base, href, esc(label)))
        else:
            parts.append('<span aria-current="page">%s</span>' % esc(label))
    return '<nav class="breadcrumb" aria-label="面包屑">%s</nav>' % "".join(parts)


def tag_list(tags):
    return '<ul class="tag-list">%s</ul>' % "".join('<li>%s</li>' % esc(tag) for tag in tags)


def footer(base):
    groups = []
    for title, links in FOOTER_GROUPS:
        items = []
        for label, href in links:
            external = href.startswith(("http://", "https://"))
            attrs = ' class="external" target="_blank" rel="noopener noreferrer"' if external else ""
            url = href if external else base + href
            items.append('<li><a href="%s"%s>%s</a></li>' % (url, attrs, esc(label)))
        groups.append('<div class="footer-col"><h2>%s</h2><ul>%s</ul></div>' % (esc(title), "".join(items)))
    return """<footer class="site-footer">
<div class="shell">
<div class="footer-top">
<div class="footer-brand">
<a class="brand" href="%(base)sindex.html" aria-label="%(name)s 首页">
<span class="brand-mark" aria-hidden="true">%(icon)s</span>
<span class="brand-text"><strong>%(name)s</strong><span class="brand-sub">%(tagline)s</span></span>
</a>
<p>%(desc)s</p>
<p class="footer-note">静态站点 · 无账号 · 无后端依赖</p>
</div>
%(groups)s
</div>
<div class="footer-bottom">
<p>%(copyright)s<br><span class="muted">%(credit)s</span></p>
<p class="footer-meta">内容更新至 2024 年 6 月 · <a href="%(base)ssitemap.html">站点地图</a> · <a href="%(base)schangelog.html">更新日志</a></p>
</div>
</div>
</footer>
""" % {
        "base": base, "name": esc(SITE["name"]), "icon": icon("atom"),
        "tagline": esc(SITE["tagline"]), "desc": esc(SITE["description"]),
        "groups": "".join(groups), "copyright": esc(SITE["copyright"]),
        "credit": SITE["credit"],
    }


def search_dialog(base):
    return """<dialog class="search-dialog" data-search-dialog aria-labelledby="search-dialog-title">
<div class="search-dialog-inner">
<div class="search-dialog-head">
<p class="eyebrow">站点搜索</p>
<h2 id="search-dialog-title">查找文章、仪器与概念</h2>
<button class="icon-button" type="button" data-search-close aria-label="关闭搜索">%(close)s</button>
</div>
<form class="search-form" action="%(base)ssearch.html" method="get" role="search" data-search-form>
%(search_icon)s
<input type="search" name="q" id="site-search-input" placeholder="例如：能量补偿、氡、Cs-137、PM1405" autocomplete="off" data-search-input aria-label="搜索关键词">
<button type="submit" class="button button-solid">搜索</button>
</form>
<div class="search-filters" data-search-filters>
<button type="button" class="chip is-active" data-section="">全部</button>
<button type="button" class="chip" data-section="basics">基础知识</button>
<button type="button" class="chip" data-section="measurement">测量与仪器</button>
<button type="button" class="chip" data-section="reviews">仪器评测</button>
<button type="button" class="chip" data-section="articles">文章</button>
<button type="button" class="chip" data-section="tools">工具</button>
<button type="button" class="chip" data-section="about">关于</button>
</div>
<div class="search-results" data-search-results aria-live="polite"></div>
<p class="search-footnote">搜索在浏览器本地完成，不会上传查询内容。按 <kbd>Esc</kbd> 关闭，<kbd>↑</kbd> <kbd>↓</kbd> 选择，<kbd>Enter</kbd> 打开。</p>
</div>
</dialog>
<div class="lightbox" data-lightbox hidden>
<button type="button" class="lightbox-close" data-lightbox-close aria-label="关闭图片">%(close)s</button>
<figure><img alt="" data-lightbox-img><figcaption data-lightbox-caption></figcaption></figure>
</div>
""" % {"base": base, "search_icon": icon("search"), "close": icon("close")}


def scripts(base, extra=""):
    return """<script src="%(base)sjs/analytics.js" defer></script>
<script src="%(base)sjs/site.js" defer></script>
%(extra)s
</body>
</html>
""" % {"base": base, "extra": extra}


def page_shell(title, description, base, active, body, extra_head="", extra_scripts="", home=False, body_class=""):
    return "".join([
        head(title, description, base, extra_head, body_class=body_class),
        header(base, active, home),
        body,
        footer(base),
        search_dialog(base),
        scripts(base, extra_scripts),
    ])
