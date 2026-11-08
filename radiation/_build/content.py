# -*- coding: utf-8 -*-
"""Extraction and normalisation of the legacy article bodies.

The source pages are hand written HTML from 2022-2024 and several of them are
structurally broken (content outside <body>, nested <p>/<ul>, styles in the
middle of the document).  lxml recovers a usable tree; this module then

* drops site chrome (old "back" links, footers, scripts, inline styles),
* normalises headings and anchors,
* turns image-only tables into figure grids,
* wraps wide data tables in a keyboard-focusable scroller,

while keeping every piece of text and every src/href intact.
"""

import copy
import os
import re
from urllib.parse import urlsplit

from lxml import etree, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(ROOT, "_build", "orig")

BAD_TAGS = {"script", "style", "link", "meta", "title", "base", "noscript"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
SKIP_ATTRS = ("bgcolor", "text", "link", "vlink", "alink", "background",
              "border", "cellpadding", "cellspacing", "valign", "align")
DATE_RE = re.compile(r"[（(]\s*\d{1,4}\s*[/.\-年]\s*\d{1,2}\s*[/.\-月]\s*\d{1,4}\s*[)）]")
WS_RE = re.compile(r"\s+")


def read_original(rel):
    with open(os.path.join(ORIG, rel), "rb") as fh:
        return fh.read().decode("utf-8", "replace")


def parse_original(rel):
    return html.document_fromstring(read_original(rel))


def norm_text(value):
    return WS_RE.sub("", (value or "").replace("\u200b", "").replace("\ufeff", ""))


def plain_text(el):
    return " ".join(("".join(el.itertext())).split())


def _content_nodes(root):
    nodes = []
    for el in root:
        if not isinstance(el.tag, str):
            continue
        if el.tag == "head":
            continue
        if el.tag == "body":
            for child in el:
                if isinstance(child.tag, str) and child.tag not in BAD_TAGS:
                    nodes.append(child)
        elif el.tag in BAD_TAGS:
            continue
        else:
            nodes.append(el)
    return nodes


def reference_text(rel):
    """Text of the original document minus chrome, for verification."""
    doc = parse_original(rel)
    for el in list(doc.iter()):
        if not isinstance(el.tag, str):
            continue
        if el.tag in BAD_TAGS:
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)
    for node in list(doc.xpath("//*[contains(@class,'footer-inner')]")):
        node.getparent().remove(node)
    for anchor in list(doc.xpath("//a")):
        text = plain_text(anchor)
        if text.startswith("返回") or text.startswith("回到主页"):
            anchor.getparent().remove(anchor)
    for head in doc.xpath("//head"):
        head.getparent().remove(head)
    return plain_text(doc)


def _drop(el):
    """Remove an element but keep its tail text in the document."""
    if el is None or el.getparent() is None:
        return
    try:
        el.drop_tree()
    except AttributeError:
        parent = el.getparent()
        prev = el.getprevious()
        tail = el.tail
        if tail:
            if prev is not None:
                prev.tail = (prev.tail or "") + tail
            else:
                parent.text = (parent.text or "") + tail
        parent.remove(el)


def _replace_keep_tail(old, new):
    tail = old.tail
    old.tail = None
    old.getparent().replace(old, new)
    if tail:
        new.tail = tail



BLOCK_IN_HEADING = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "table",
                    "ul", "ol", "dl", "figure", "form", "section", "blockquote",
                    "img", "iframe", "video", "pre", "hr"}



def _unwrap_orphan_list_items(container):
    for li in list(container.xpath(".//li")):
        parent = li.getparent()
        if parent is not None and parent.tag in ("ul", "ol"):
            continue
        if li.text and li.text.strip():
            span = etree.Element("span")
            span.text = li.text
            li.addprevious(span)
        for child in list(li):
            li.remove(child)
            li.addprevious(child)
        _drop(li)


def _unwrap_lists_with_headings(container):
    """Legacy pages such as the data index use <ul> as a generic container and
    put headings inside it.  Unwrap those lists, keeping the nested normal
    lists and all links/text in document order."""
    for lst in list(container.xpath(".//ul|.//ol")):
        if lst.getparent() is None:
            continue
        if not lst.xpath("./h1|./h2|./h3|./h4|./h5|./h6|./li/h1|./li/h2|./li/h3|./li/h4"):
            continue
        for child in list(lst):
            lst.remove(child)
            lst.addprevious(child)
        _drop(lst)


def _split_heading_blocks(container):
    """The legacy pages often leave a heading unclosed, so lxml nests the rest
    of the section inside it.  Move block children (and everything after them)
    out of the heading, keeping document order."""
    for heading in list(container.iter()):
        if not isinstance(heading.tag, str) or heading.tag not in HEADING_TAGS:
            continue
        children = list(heading)
        start = None
        for index, child in enumerate(children):
            if isinstance(child.tag, str) and child.tag in BLOCK_IN_HEADING:
                start = index
                break
        if start is None:
            continue
        anchor = heading
        for child in children[start:]:
            heading.remove(child)
            anchor.addnext(child)
            anchor = child


def _remove_spacer_breaks(container):
    for br in list(container.xpath(".//br")):
        prev = br.getprevious()
        nxt = br.getnext()
        near_block = False
        if prev is not None and isinstance(prev.tag, str) and (prev.tag in HEADING_TAGS or prev.tag in ("img", "table", "div", "figure", "iframe", "video")):
            near_block = True
        if nxt is not None and isinstance(nxt.tag, str) and (nxt.tag in HEADING_TAGS or nxt.tag in ("img", "table", "div", "figure", "iframe", "video")):
            near_block = True
        if near_block:
            _drop(br)


def _strip_styles(container):
    for el in container.iter():
        if not isinstance(el.tag, str):
            continue
        style = el.get("style") or ""
        if el.tag in ("td", "th") and "text-align" in style and "right" in style:
            classes = (el.get("class") or "").split()
            if "num" not in classes:
                classes.append("num")
                el.set("class", " ".join(classes).strip())
        el.attrib.pop("style", None)
        for attr in SKIP_ATTRS:
            el.attrib.pop(attr, None)


def _clean_links(container):
    for anchor in container.xpath(".//a"):
        href = anchor.get("href")
        name = anchor.get("name")
        if name and not href:
            # In-page legacy anchor.  If it sits inside a heading it is moved
            # to the heading itself later; otherwise turn it into a span.
            if anchor.getparent() is not None and anchor.getparent().tag in HEADING_TAGS:
                anchor.getparent().set("data-legacy-anchor", name)
                anchor.drop_tag()
            else:
                span = etree.Element("span")
                span.set("id", name)
                span.set("class", "legacy-anchor")
                span.text = anchor.text
                for child in anchor:
                    span.append(child)
                span.tail = anchor.tail
                anchor.getparent().replace(anchor, span)
            continue
        if href is None:
            continue
        value = href.strip()
        anchor.set("href", value)
        low = value.lower()
        if low.startswith(("http://", "https://")):
            classes = (anchor.get("class") or "").split()
            if "external" not in classes:
                classes.append("external")
            anchor.set("class", " ".join(classes).strip())
            anchor.set("rel", "noopener noreferrer")
            anchor.set("target", "_blank")
        elif not low or low.startswith("#"):
            continue


def _unwrap_decorations(container):
    for node in list(container.xpath(".//font")):
        node.drop_tag()
    for node in list(container.xpath(".//center")):
        node.tag = "div"
        node.set("class", ((node.get("class") or "") + " center").strip())
    for node in list(container.xpath(".//hr")):
        _drop(node)
    for node in list(container.xpath(".//*[contains(@class,'divider')]")):
        if not plain_text(node) and not node.xpath(".//img"):
            _drop(node)
    for comment in list(container.xpath(".//comment()")):
        comment.getparent().remove(comment)
    for node in list(container.xpath(".//*[contains(@class,'footer-inner')]")):
        _drop(node)


def _cell_is_only_images(cell):
    if plain_text(cell):
        return False
    imgs = cell.xpath(".//img")
    if not imgs:
        return False
    for el in cell.iter():
        if el is cell:
            continue
        if el.tag in ("img", "a", "br", "p", "div", "span"):
            continue
        return False
    return True


def _table_is_image_only(table):
    if table.xpath(".//table"):
        return False
    rows = table.xpath("./tr|./thead/tr|./tbody/tr")
    if not rows:
        return False
    cells = []
    for row in rows:
        cells.extend(row.xpath("./td|./th"))
    if not cells:
        return False
    return all(_cell_is_only_images(cell) for cell in cells)


def _figure_from_cell(cell):
    figures = []
    for img in cell.xpath(".//img"):
        wrapper = img.getparent()
        link = None
        while wrapper is not None and wrapper is not cell and wrapper.tag == "a":
            link = wrapper
            break
        fig = etree.Element("figure")
        fig.set("class", "gallery-item")
        if link is not None:
            new_link = copy.deepcopy(link)
            for extra in new_link.xpath(".//img[position()>1]"):
                extra.getparent().remove(extra)
            fig.append(new_link)
            alt = link.xpath(".//img/@alt")
        else:
            fig.append(copy.deepcopy(img))
            alt = img.get("alt")
        alt = alt[0] if alt else ""
        if alt and alt not in ("Big Boat",) and not alt.startswith("丢失或加载失败"):
            cap = etree.SubElement(fig, "figcaption")
            cap.text = alt
        figures.append(fig)
    return figures


def _convert_image_table(table):
    grid = etree.Element("div")
    grid.set("class", "figure-grid")
    count = 0
    for row in table.xpath("./tr|./thead/tr|./tbody/tr"):
        for cell in row.xpath("./td|./th"):
            for fig in _figure_from_cell(cell):
                grid.append(fig)
                count += 1
    grid.set("data-count", "many" if count >= 4 else str(count))
    _replace_keep_tail(table, grid)


def _count_columns(table):
    best = 0
    for row in table.xpath("./tr|./thead/tr|./tbody/tr")[:4]:
        total = 0
        for cell in row.xpath("./td|./th"):
            try:
                total += int(cell.get("colspan") or 1)
            except ValueError:
                total += 1
        best = max(best, total)
    return best


def _wrap_table(table):
    classes = (table.get("class") or "").split()
    is_form = bool(table.xpath(".//input|.//select|.//textarea|.//button"))
    is_layout = bool(table.xpath(".//table")) or "noborder" in classes
    if not is_layout and not is_form and "csv" not in classes:
        classes.append("data-table")
        table.set("class", " ".join(classes))
    if is_layout:
        classes.append("layout-table")
        table.set("class", " ".join(dict.fromkeys(classes)))
        return

    wrapper = etree.Element("div")
    wrapper.set("class", "table-scroll")
    wrapper.set("role", "region")
    wrapper.set("tabindex", "0")
    wrapper.set("aria-label", "数据表格，可横向滚动")
    columns = _count_columns(table)
    wrapper.set("data-cols", str(columns))
    if columns >= 6 or is_form:
        wrapper.set("data-wide", "true")
    tail = table.tail
    table.tail = None
    table.addprevious(wrapper)
    wrapper.append(table)
    if tail:
        wrapper.tail = tail


def _normalise_media(container):
    for iframe in container.xpath(".//iframe"):
        src = (iframe.get("src") or "").strip()
        if src.startswith("//"):
            src = "https:" + src
        iframe.set("src", src)
        iframe.set("loading", "lazy")
        if not iframe.get("title"):
            iframe.set("title", "嵌入的视频")
        for attr in ("width", "height", "border", "frameborder", "framespacing",
                     "scrolling"):
            iframe.attrib.pop(attr, None)
        if iframe.getparent() is not None and iframe.getparent().tag != "div":
            parent = iframe.getparent()
            if parent.tag in ("p", "div", "body") or parent.tag in HEADING_TAGS:
                wrapper = etree.Element("div")
                wrapper.set("class", "embed")
                iframe.addprevious(wrapper)
                wrapper.append(iframe)
    for video in container.xpath(".//video"):
        for attr in ("width", "height"):
            video.attrib.pop(attr, None)
        classes = (video.get("class") or "").split()
        if "content-video" not in classes:
            classes.append("content-video")
        video.set("class", " ".join(classes).strip())
    imgs = container.xpath(".//img")
    for index, img in enumerate(imgs):
        classes = (img.get("class") or "").split()
        if "content-img" not in classes:
            classes.append("content-img")
        img.set("class", " ".join(classes).strip())
        if index >= 3:
            img.set("loading", "lazy")
        img.set("decoding", "async")
    for dl in container.xpath(".//dl"):
        classes = (dl.get("class") or "").split()
        if "spec-list" not in classes:
            classes.append("spec-list")
        dl.set("class", " ".join(classes).strip())
        for br in dl.xpath("./br"):
            br.getparent().remove(br)


def _tidy_blocks(container):
    # Empty paragraphs are only used as spacers in the source.
    for p in list(container.xpath(".//p")):
        if not plain_text(p) and not p.xpath(".//img|.//iframe|.//video|.//input|.//table"):
            _drop(p)
    # Remove leading/trailing <br> children of the article container.
    def is_br(node):
        return isinstance(node.tag, str) and node.tag == "br"

    def empty_block(node):
        if not isinstance(node.tag, str) or node.tag != "p":
            return False
        return (not plain_text(node) and
                not node.xpath(".//img|.//iframe|.//video|.//input|.//table|.//svg"))

    while len(container) and (is_br(container[0]) or empty_block(container[0])):
        _drop(container[0])
    while len(container) and (is_br(container[-1]) or empty_block(container[-1])):
        _drop(container[-1])
    # A bare link left at the top level (legacy data index) becomes a paragraph.
    for anchor in list(container):
        if isinstance(anchor.tag, str) and anchor.tag == "a" and anchor.get("href"):
            para = etree.Element("p")
            anchor.addprevious(para)
            para.append(anchor)

    # Collapse runs of more than two <br> elements.
    for parent in container.iter():
        if not isinstance(parent.tag, str):
            continue
        run = 0
        for child in list(parent):
            if is_br(child):
                run += 1
                if run > 2:
                    _drop(child)
            else:
                run = 0


def _prepare_headings(container, title):
    title_core = re.sub(r"[^\w\u4e00-\u9fff]+", "", DATE_RE.sub("", title or "")).lower()
    dropped = []
    kept = []
    # A very long H1 at the very start is a legacy headline/lead, not a
    # section heading.  Keep its text but present it as a standfirst.
    first_meaningful = None
    for child in container:
        if isinstance(child.tag, str) and child.tag not in ("br",):
            first_meaningful = child
            break
    if (first_meaningful is not None and first_meaningful.tag == "h1"
            and len(plain_text(first_meaningful)) > 40):
        first_meaningful.tag = "p"
        first_meaningful.set("class", "standfirst")

    # Long sentence-like "headings" are body paragraphs in the source, not
    # section headings.  Keep the text, but stop styling it as a headline.
    for heading in list(container.iter()):
        if not isinstance(heading.tag, str) or heading.tag not in HEADING_TAGS:
            continue
        if len(plain_text(heading)) <= 60:
            continue
        legacy = heading.get("data-legacy-anchor")
        heading.tag = "p"
        heading.set("class", "long-quote")
        if legacy:
            heading.set("id", legacy)
            heading.attrib.pop("data-legacy-anchor", None)

    # Some legacy pages repeat the page title as the first paragraph.
    first = None
    for child in container:
        if isinstance(child.tag, str) and child.tag not in ("br",):
            first = child
            break
    if first is not None and first.tag == "p":
        first_text = plain_text(first)
        first_core = re.sub(r"[^\w\u4e00-\u9fff]+", "", DATE_RE.sub("", first_text)).lower()
        if first_core and first_core == title_core:
            date_match = DATE_RE.search(first_text)
            dropped.append({"heading": first, "text": first_text,
                            "note": date_match.group(0) if date_match else ""})
            _drop(first)

    headings = [h for h in container.iter() if isinstance(h.tag, str) and h.tag in HEADING_TAGS]
    for heading in headings:
        text = plain_text(heading)
        if not text:
            kept.append(heading)
            continue
        core = re.sub(r"[^\w\u4e00-\u9fff]+", "", DATE_RE.sub("", text)).lower()
        if core and core == title_core:
            date_match = DATE_RE.search(text)
            dropped.append({"heading": heading, "text": text,
                            "note": date_match.group(0) if date_match else ""})
        else:
            kept.append(heading)

    notes = []
    for item in dropped:
        heading = item["heading"]
        if item["note"]:
            notes.append(item["note"])
        # If the heading also carries an anchor, keep the anchor as a span.
        anchor = heading.get("data-legacy-anchor")
        if anchor:
            span = etree.Element("span")
            span.set("id", anchor)
            span.set("class", "legacy-anchor")
            heading.addprevious(span)
        _drop(heading)

    used_ids = set(container.xpath(".//@id"))
    toc = []
    sections = 0
    for heading in kept:
        text = plain_text(heading)
        legacy = heading.get("data-legacy-anchor")
        heading.attrib.pop("data-legacy-anchor", None)
        if legacy and legacy not in used_ids:
            heading.set("id", legacy)
            used_ids.add(legacy)
        elif not heading.get("id"):
            sections += 1
            new_id = "sec-%d" % sections
            while new_id in used_ids:
                sections += 1
                new_id = "sec-%d" % sections
            heading.set("id", new_id)
            used_ids.add(new_id)
        # Remove empty anchor tags still inside the heading.
        for anchor in heading.xpath(".//a[@name]"):
            anchor.drop_tag()
        if text:
            toc.append({"level": 0, "id": heading.get("id"), "text": text,
                        "rank": int(heading.tag[1])})

    # Map the levels that actually occur onto h2/h3/h4.
    levels = sorted({item["rank"] for item in toc})
    mapping = {level: min(4, 2 + index) for index, level in enumerate(levels)}
    for item in toc:
        item["level"] = mapping[item["rank"]] - 2
        item.pop("rank", None)
    for heading in kept:
        rank = int(heading.tag[1])
        heading.tag = "h%d" % mapping.get(rank, 3)
    return toc, notes, [item["text"] for item in dropped]


def _mark_legacy_toc(container):
    """Detect an in-body "目录" list and style it as a compact index."""
    found = None
    for heading in container.xpath(".//h1|.//h2|.//h3|.//h4"):
        if norm_text(plain_text(heading)) != "目录":
            continue
        nxt = heading.getnext()
        while nxt is not None and isinstance(nxt.tag, str) and not plain_text(nxt) \
                and nxt.tag not in ("ul", "ol", "p"):
            nxt = nxt.getnext()
        target = nxt
        if target is not None and target.tag == "p":
            lists = target.xpath("./ul|./ol")
            target = lists[0] if lists else None
        if target is not None and target.tag in ("ul", "ol"):
            found = (heading, target)
            break
    if not found:
        return False
    heading, listing = found
    heading.set("class", ((heading.get("class") or "") + " toc-heading").strip())
    listing.set("class", ((listing.get("class") or "") + " legacy-toc").strip())
    return True


def extract(rel, title=""):
    doc = parse_original(rel)
    container = html.Element("div")
    for node in _content_nodes(doc):
        if not isinstance(node.tag, str) or node.tag in BAD_TAGS:
            continue
        container.append(copy.deepcopy(node))

    for bad in list(container.xpath(".//script|.//style|.//title|.//meta|.//link|.//noscript")):
        _drop(bad)
    for anchor in list(container.xpath(".//a")):
        text = plain_text(anchor)
        if text.startswith("返回") or text.startswith("回到主页"):
            _drop(anchor)
    for footer in list(container.xpath(".//*[contains(@class,'footer-inner')]")):
        _drop(footer)

    _strip_styles(container)
    _unwrap_lists_with_headings(container)
    _unwrap_orphan_list_items(container)
    _split_heading_blocks(container)
    _unwrap_decorations(container)
    _clean_links(container)
    _remove_spacer_breaks(container)
    _normalise_media(container)
    has_legacy_toc = _mark_legacy_toc(container)

    # tables (image tables become galleries, the rest get scrollers)
    for table in list(container.xpath(".//table")):
        if table.getparent() is None:
            continue
        if _table_is_image_only(table):
            _convert_image_table(table)
        else:
            _wrap_table(table)

    toc, title_notes, dropped_headings = _prepare_headings(container, title)
    _tidy_blocks(container)
    return {
        "fragment": container,
        "html": "".join(
            etree.tostring(child, encoding="unicode", method="html") for child in container
        ),
        "text": plain_text(container),
        "toc": toc,
        "title_notes": title_notes,
        "dropped_headings": dropped_headings,
        "has_legacy_toc": has_legacy_toc,
    }
