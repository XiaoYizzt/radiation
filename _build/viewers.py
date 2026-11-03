# -*- coding: utf-8 -*-
"""Wrap the WESViewer spectral workspaces in the new site shell without
touching their JavaScript or element IDs."""

import re

from lxml import etree, html

import content as C
import templates as T
from site_data import SITE, WES_GALLERY, WES_VIEWERS


def _strip_sizing(style):
    if not style:
        return style
    style = re.sub(r"(?:^|;)\s*(?:width|height)\s*:[^;]*", "", style)
    return style.strip(" ;")


def _local_scripts(rel):
    raw = C.read_original(rel)
    blocks = re.findall(r"<script\b([^>]*)>(.*?)</script\s*>", raw, re.S | re.I)
    output = []
    for attrs, body in blocks:
        src_match = re.search(r"src\s*=\s*[\"']([^\"']+)[\"']", attrs, re.I)
        if src_match:
            src = src_match.group(1)
            low = src.lower()
            if any(token in low for token in ("googletagmanager", "51.la", "socialbutton", "analytics")):
                continue
            output.append('<script src="%s"></script>' % T.esc(src))
            continue
        low = body.lower()
        if any(token in low for token in ("_gaq", "gtag(", "la_collect", "datalayer")):
            continue
        output.append("<script>%s</script>" % body)
    return "\n".join(output)


def render_viewer(rel):
    title, isotope, note = WES_VIEWERS[rel]
    base = "../" * rel.count("/")
    doc = C.parse_original(rel)
    body = doc.xpath("//body")[0]

    for bad in list(body.xpath(".//script|.//style|.//link|.//meta|.//title|.//noscript")):
        if bad.getparent() is not None:
            bad.getparent().remove(bad)
    for footer in list(body.xpath(".//*[contains(@class,'footer-inner')]")):
        if footer.getparent() is not None:
            footer.getparent().remove(footer)
    for el in body.iter():
        if not isinstance(el.tag, str):
            continue
        if el.get("style"):
            el.set("style", _strip_sizing(el.get("style")))
        for attr in ("bgcolor", "text", "link", "vlink", "alink", "background"):
            el.attrib.pop(attr, None)

    content = "".join(
        etree.tostring(child, encoding="unicode", method="html") for child in body
    )
    scripts = _local_scripts(rel)

    breadcrumb = T.breadcrumb(base, [
        ("首页", "index.html"),
        ("工具与数据", "tools.html"),
        ("WESViewer", "tool/WESViewer/index.html"),
        (title, None),
    ])
    extra_head = '<link rel="stylesheet" href="%scss/viewer.css">' % base

    page = """<main id="main" class="page page-viewer">
<div class="shell">
%(breadcrumb)s
<div class="viewer-bar">
<span class="viewer-label">WESViewer · 光谱查看</span>
<nav aria-label="WESViewer 导航">
<a href="%(base)stool/WESViewer/index.html">使用说明</a>
<a href="%(base)stool/WESViewer/index.html">全部光谱</a>
<a href="%(base)stool/WESViewer/rain/index.html">雨天样本</a>
</nav>
</div>
<div class="viewer-prose prose">
%(content)s
</div>
<p class="viewer-copyright">Retpaĝo © 2022-2023.XiaoYi No One Knows the Future. Icon of WESViewer All rights reserved.</p>
</div>
</main>""" % {"breadcrumb": breadcrumb, "base": base, "content": content}

    return "".join([
        T.head(title, "WESViewer 光谱查看页面：%s（%s）。" % (title, isotope),
               base, extra_head=extra_head, body_class="page-viewer"),
        T.header(base, "tools"),
        page,
        T.footer(base),
        T.search_dialog(base),
        T.scripts(base, scripts),
    ])


def build_viewers(write):
    for rel in WES_VIEWERS:
        write(rel, render_viewer(rel))
