# -*- coding: utf-8 -*-
"""Assemble the new static site."""

import json
import os
import re

import content as C
import pages as P
import render as R
import viewers as V
import templates as T
from site_data import (GENERATED_HUBS, PAGES, SECTIONS, SITE, SUBSECTIONS,
                       WES_GALLERY, WES_VIEWERS)

ROOT = C.ROOT
BUILT = {}


def write(rel, text):
    path = os.path.join(ROOT, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    BUILT[rel] = text


def estimate_minutes():
    for rel, meta in PAGES.items():
        if rel.endswith(".pdf"):
            meta["minutes"] = 8
            continue
        if rel in WES_VIEWERS:
            continue
        try:
            data = C.extract(rel, meta.get("title", ""))
            meta["minutes"] = R.read_time(data["text"])
        except Exception:
            meta["minutes"] = 1


def build_articles():
    estimate_minutes()
    order = {sid: R.section_pages(sid) for sid in SECTIONS}
    for rel, meta in PAGES.items():
        if rel.endswith(".pdf") or rel in WES_GALLERY or rel in WES_VIEWERS or rel in GENERATED_HUBS:
            continue
        seq = order.get(meta.get("section"), [])
        idx = seq.index(rel) if rel in seq else -1
        prev_link = (seq[idx - 1], PAGES[seq[idx - 1]]) if idx > 0 else None
        next_link = (seq[idx + 1], PAGES[seq[idx + 1]]) if 0 <= idx < len(seq) - 1 else None
        html = R.render_article(rel, meta, prev_link, next_link)
        write(rel, html)


def build_hubs():
    for rel, sid in [
        ("base.html", "basics"),
        ("info/index.html", "measurement"),
        ("reviews.html", "reviews"),
        ("article.html", "articles"),
        ("other/index.html", "articles"),
        ("tools.html", "tools"),
    ]:
        write(rel, R.render_hub(rel, sid))


def build_galleries():
    for rel in WES_GALLERY:
        meta = R.find_meta(rel)
        meta["kind"] = "gallery"
        write(rel, R.render_article(rel, meta))


def build_specials():
    write("index.html", P.render_home())
    write("about.html", P.render_about())
    write("search.html", P.render_search_page())
    write("sitemap.html", P.render_sitemap())
    write("changelog.html", P.render_changelog())


def hub_search_text(sid):
    bits = [SECTIONS[sid]["blurb"]]
    for rel in R.section_pages(sid):
        meta = PAGES[rel]
        bits.append(meta["title"] + " " + meta.get("summary", ""))
    return " ".join(bits)


def build_search_index():
    items = []
    section_names = {sid: SECTIONS[sid]["label"] for sid in SECTIONS}
    section_names["home"] = "首页"
    section_names["search"] = "搜索"

    def add(u, t, s, d, k="", l="", b=""):
        items.append({"u": u, "t": t, "s": s, "sn": section_names.get(s, s),
                      "d": d, "k": k, "l": l, "b": b})

    add("index.html", "首页：辐射、探测器与测量", "home",
        "辐射备忘录首页。基础知识、测量与仪器、仪器评测、文章与工具的总入口。",
        "辐射 探测器 测量 首页", "", "辐射知识 从测量开始 站点索引")
    for sid in ["basics", "measurement", "reviews", "articles", "tools"]:
        add(SECTIONS[sid]["hub"], SECTIONS[sid]["label"], sid,
            SECTIONS[sid]["blurb"], " ".join(SECTIONS[sid]["label"] for _ in [0]),
            "", hub_search_text(sid))
    add("about.html", "关于本站", "about", "站点说明、联系方式、静态技术实现、版权与更新记录。",
        "关于 联系 版权 技术 静态", "", "关于本站 我不是专家 可能会有错误 联系方式 XkXiaoYi475@outlook.com")
    add("sitemap.html", "站点地图：全部页面", "about", "站内全部 HTML 页面与 PDF 的索引。",
        "站点地图 全部页面 索引", "", "站点地图 全部页面")
    add("changelog.html", "更新日志", "about", "2022–2024 年的完整更新记录。",
        "更新日志 历史", "", "更新日志 更新历史 2022 2023 2024")
    add("search.html", "搜索", "search", "搜索文章、仪器与概念。", "搜索 查找", "", "搜索")

    for rel, meta in PAGES.items():
        if meta.get("section") == "archive":
            continue
        if meta.get("kind") == "pdf":
            add(rel, meta["title"], "articles", meta["summary"], " ".join(meta.get("tags", [])),
                meta.get("level", ""), meta["summary"] + " PDF 研究 文档 KB6011")
            continue
        data = BUILT.get(rel)
        body = ""
        if data:
            match = re.search(r'<div class="prose"[^>]*>(.*)</div>\s*<footer', data, re.S)
            if match:
                body = re.sub(r"<[^>]+>", " ", match.group(1))
                body = " ".join(body.split())
        add(rel, meta["title"], meta.get("section", "articles"), meta.get("summary", ""),
            " ".join(meta.get("tags", [])), meta.get("level", ""), body)
    for rel, meta in [(r, R.find_meta(r)) for r in WES_GALLERY]:
        add(rel, meta["title"], "tools", meta["summary"], " ".join(meta.get("tags", [])), meta.get("level", ""), meta["summary"])

    payload = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    write("js/search-index.js", "window.SITE_SEARCH=%s;\n" % payload)
    print("search index items:", len(items), "bytes:", len(payload))


def main():
    build_articles()
    build_hubs()
    build_galleries()
    V.build_viewers(write)
    build_specials()
    build_search_index()
    print("built pages:", len([r for r in BUILT if r.endswith(".html")]))


if __name__ == "__main__":
    main()
