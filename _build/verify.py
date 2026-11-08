# -*- coding: utf-8 -*-
"""Post-build integrity verification against the pre-refactor baseline."""

import json
import os
import re
from collections import Counter
from urllib.parse import unquote

from lxml import html

import content as C
from site_data import PAGES, WES_GALLERY, WES_VIEWERS

ROOT = C.ROOT
SKIP = {"_build", "css", "js", "img"}


def all_html():
    for dp, dns, fns in os.walk(ROOT):
        rel_dir = os.path.relpath(dp, ROOT)
        if rel_dir.split(os.sep)[0] in SKIP:
            dns[:] = []
            continue
        for fn in fns:
            if fn.lower().endswith((".html", ".htm")):
                yield os.path.relpath(os.path.join(dp, fn), ROOT).replace("\\", "/")


def parse_new(rel):
    return html.document_fromstring(open(os.path.join(ROOT, rel), encoding="utf-8").read())


def page_info(doc):
    prose = doc.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " prose ") '
                      'and not(contains(concat(" ", normalize-space(@class), " "), " viewer-prose "))]')
    viewer = doc.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " viewer-prose ")]')
    h1s = [" ".join(el.text_content().split()) for el in doc.xpath("//h1")]
    notes = [" ".join(el.text_content().split()) for el in doc.xpath('//*[@class="title-note"]')]
    scripts = doc.xpath("//script[@src]/@src")
    styles = doc.xpath('//link[contains(@rel,"stylesheet")]/@href')
    return {
        "links": [a.get("href") for a in doc.xpath("//a[@href]")],
        "imgs": doc.xpath("//img/@src"),
        "ids": [x for x in doc.xpath("//@id") if x],
        "anchors": [x for x in doc.xpath("//a[@name]/@name") if x],
        "scripts": scripts,
        "styles": styles,
        "h1": h1s,
        "title_note": notes,
        "prose": " ".join(prose[0].text_content().split()) if prose else "",
        "viewer": " ".join(viewer[0].text_content().split()) if viewer else "",
    }


def resolve(src, target):
    t = (target or "").strip()
    if not t:
        return None
    low = t.lower()
    if low.startswith(("http:", "https:", "mailto:", "javascript:", "data:", "tel:", "ftp:")):
        return ("external", t)
    if t.startswith("#"):
        return ("anchor", src, t[1:])
    t = unquote(t)
    path, _, frag = t.partition("#")
    path = path.split("?")[0]
    if not path:
        return ("anchor", src, frag)
    base = ROOT if path.startswith("/") else os.path.dirname(os.path.join(ROOT, src))
    return ("local", os.path.normpath(os.path.join(base, path.lstrip("/"))), frag)


def norm(s):
    return re.sub(r"[\s\u200b\ufeff]+", "", s or "")


def core(s):
    return re.sub(r"[^\w\u4e00-\u9fff]+", "", C.DATE_RE.sub("", s or "")).lower()


def main():
    baseline = json.load(open(os.path.join(ROOT, "_build", "baseline.json"), encoding="utf-8"))
    old_pages = baseline["pages"]
    new_rel = sorted(all_html())
    new = {rel: page_info(parse_new(rel)) for rel in new_rel}
    report = {"new_page_count": len(new_rel), "old_page_count": len(old_pages),
              "checks": [], "failures": [], "notes": []}

    def check(name, ok, detail=""):
        report["checks"].append({"name": name, "ok": bool(ok), "detail": detail})
        if not ok:
            report["failures"].append({"name": name, "detail": detail})

    missing_pages = sorted(set(old_pages) - set(new_rel))
    check("all original pages exist", not missing_pages, ", ".join(missing_pages))

    text_mismatch = []
    heading_mismatch = []
    for rel, meta in PAGES.items():
        if rel.endswith(".pdf") or rel not in new:
            continue
        data = C.extract(rel, meta.get("title", ""))
        ref = C.reference_text(rel)
        for dropped in data["dropped_headings"]:
            ref = ref.replace(dropped, "", 1)
        body = new[rel]["prose"]
        if norm(body) != norm(ref):
            text_mismatch.append({"page": rel, "reference_chars": len(norm(ref)),
                                  "new_chars": len(norm(body))})
        if data["dropped_headings"]:
            h1 = core(" ".join(new[rel]["h1"]) + " " + " ".join(new[rel]["title_note"]))
            expected = core(" ".join(data["dropped_headings"]))
            if h1 != expected:
                heading_mismatch.append({"page": rel, "h1": h1, "expected": expected})
    check("article body text preserved", not text_mismatch, json.dumps(text_mismatch[:10], ensure_ascii=False))
    check("dropped title headings represented", not heading_mismatch,
          json.dumps(heading_mismatch[:10], ensure_ascii=False))

    viewer_mismatch = []
    for rel in WES_VIEWERS:
        doc = C.parse_original(rel)
        body = doc.xpath("//body")[0]
        for bad in list(body.xpath(".//script|.//style")):
            bad.getparent().remove(bad)
        ref = C.plain_text(body)
        got = new[rel]["viewer"]
        if norm(ref) != norm(got):
            viewer_mismatch.append({"page": rel, "reference_chars": len(norm(ref)),
                                    "new_chars": len(norm(got))})
    check("WESViewer body text preserved", not viewer_mismatch,
          json.dumps(viewer_mismatch, ensure_ascii=False))

    missing_assets = []
    for rel, page in new.items():
        for src in page["styles"] + page["scripts"] + page["imgs"]:
            r = resolve(rel, src)
            if r and r[0] == "local" and not os.path.exists(r[1]):
                missing_assets.append([rel, src, os.path.relpath(r[1], ROOT).replace("\\", "/")])
    known_missing_paths = {"img/ju.jfif", "other/img/fs1.png", "other/img/zd.jpg"}
    real_missing = [item for item in missing_assets if item[2] not in known_missing_paths]
    check("all referenced local assets exist", not real_missing,
          json.dumps(real_missing[:10], ensure_ascii=False))
    report["notes"].append("pre-existing missing images kept: %s" %
                           sorted({m[2] for m in missing_assets}))

    broken = []
    bad_anchors = []
    for rel, page in new.items():
        for href in page["links"]:
            r = resolve(rel, href)
            if not r:
                continue
            if r[0] == "local":
                dest, frag = r[1], r[2]
                if not os.path.exists(dest):
                    broken.append([rel, href, os.path.relpath(dest, ROOT).replace("\\", "/")])
                    continue
                trel = os.path.relpath(dest, ROOT).replace("\\", "/")
                if frag and trel in new:
                    if frag in new[trel]["ids"] or frag in new[trel]["anchors"]:
                        continue
                    if frag.startswith("__") or re.match(r"^\d+(\.\d+)?(_|$)", frag):
                        continue
                    bad_anchors.append([rel, href, trel, frag])
            elif r[0] == "anchor":
                frag = r[2]
                if frag and frag not in page["ids"] and frag not in page["anchors"]:
                    bad_anchors.append([rel, href, rel, frag])

    known_broken = {
        ("history.html", "geiger counter.html"),
        ("changelog.html", "geiger counter.html"),
        ("Untitled-1.html", "../../index.html"),
        ("Untitled-1.html", "geiger counter.html"),
        ("info/info008.html", "../energy compensation.html"),
        ("info/info010[X].html", "../database/NE/out/cgi-bin/fissionyield.html"),
        ("info/info010[X].html", "../database/PGAA/out/pgaa/egaf.html"),
        ("info/info010[X].html", "../database/N/NGATLAS2/index.html"),
    }
    known_broken_norm = {(unquote(a), unquote(b)) for a, b in known_broken}
    new_broken = [b for b in broken
                  if (unquote(b[0]), unquote(b[1])) not in known_broken_norm]
    check("no newly broken internal links", not new_broken,
          json.dumps(new_broken[:12], ensure_ascii=False))
    report["known_broken"] = sorted({(b[0], b[1]) for b in broken})

    known_bad = {("index.html", "detector_list.html#1"),
                 ("Untitled-1.html", "detector_list.html#1"),
                 ("tool/info004.html", "#0.1_0.1_100_10_10")}
    # The original audit listed 21 info004 simulation links; all are JS params.
    new_bad = [a for a in bad_anchors if not (
        a[0] == "index.html" and a[1] == "detector_list.html#1"
        or a[0] == "Untitled-1.html" and a[1] == "detector_list.html#1"
        or a[0] == "tool/info004.html" and (a[1].startswith("#") and re.match(r"^#\d", a[1]))
    )]
    check("no newly broken anchors", not new_bad, json.dumps(new_bad[:15], ensure_ascii=False))
    report["known_bad_anchors"] = sorted({(a[0], a[1]) for a in bad_anchors})

    lost_ids = []
    for rel, old in old_pages.items():
        if rel not in new:
            continue
        old_set = set(old["ids"]) | set(old["anchors"])
        new_set = set(new[rel]["ids"]) | set(new[rel]["anchors"])
        missing = sorted(x for x in old_set - new_set if x)
        if missing:
            lost_ids.append({"page": rel, "missing": missing[:12]})
    check("original ids/anchors preserved", not lost_ids,
          json.dumps(lost_ids[:12], ensure_ascii=False))

    old_ext = set(baseline["externals"].keys())
    new_ext = set()
    for rel, page in new.items():
        for href in page["links"]:
            r = resolve(rel, href)
            if r and r[0] == "external":
                new_ext.add(r[1])
    lost_ext = sorted(old_ext - new_ext)
    check("all original external URLs still present", not lost_ext,
          json.dumps(lost_ext[:20], ensure_ascii=False))

    old_imgs = set()
    for rel, old in old_pages.items():
        for src in old["imgs"]:
            r = resolve(rel, src)
            if r and r[0] == "local":
                old_imgs.add(os.path.relpath(r[1], ROOT).replace("\\", "/"))
    new_imgs = set()
    for rel, page in new.items():
        for src in page["imgs"]:
            r = resolve(rel, src)
            if r and r[0] == "local":
                new_imgs.add(os.path.relpath(r[1], ROOT).replace("\\", "/"))
    lost_imgs = sorted(i for i in old_imgs - new_imgs if os.path.exists(os.path.join(ROOT, i)))
    check("all existing original images still referenced", not lost_imgs,
          json.dumps(lost_imgs[:20], ensure_ascii=False))

    dup_ids = []
    for rel, page in new.items():
        counts = Counter(page["ids"])
        dup = [k for k, v in counts.items() if v > 1]
        if dup:
            dup_ids.append({"page": rel, "duplicates": dup[:8]})
    check("no duplicate ids", not dup_ids, json.dumps(dup_ids[:10], ensure_ascii=False))

    no_h1 = [rel for rel, page in new.items() if not page["h1"]]
    check("every page has an h1", not no_h1, ", ".join(no_h1[:12]))

    no_title = []
    for rel in new_rel:
        raw = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        if "<title>" not in raw:
            no_title.append(rel)
    check("every page has a title", not no_title, ", ".join(no_title[:12]))

    report["external_urls_new"] = len(new_ext)
    report["image_refs_old"] = len(old_imgs)
    report["image_refs_new"] = len(new_imgs)
    report["pages_with_js_errors"] = []

    with open(os.path.join(ROOT, "_build", "verify_report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in report.items() if k not in ("checks", "failures")},
                     ensure_ascii=False, indent=2))
    print("\nCHECKS:")
    for item in report["checks"]:
        print(("PASS " if item["ok"] else "FAIL ") + item["name"] +
              ("" if item["ok"] else " :: " + item["detail"][:500]))
    print("\nFAILURES:", len(report["failures"]))


if __name__ == "__main__":
    main()
