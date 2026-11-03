import os, re, json, hashlib, urllib.parse
from html.parser import HTMLParser
ROOT = r"C:\Users\XkXia\Desktop\radiation"
SKIP_TOP = {"_build"}

def all_html():
    for dp, dns, fns in os.walk(ROOT):
        rel = os.path.relpath(dp, ROOT)
        if rel.split(os.sep)[0] in SKIP_TOP:
            dns[:] = []; continue
        for f in fns:
            if f.lower().endswith((".html",".htm")):
                yield os.path.join(dp,f)

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.imgs=[]; self.ids=set(); self.anchors=set(); self.text=[]; self.skip=0; self.title=""; self.intitle=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="script" or tag=="style": self.skip+=1
        if tag=="title": self.intitle=True
        if "id" in a and a["id"]: self.ids.add(a["id"])
        if tag=="a":
            if a.get("name"): self.anchors.add(a["name"])
            if a.get("href") is not None: self.links.append(a["href"])
        if tag=="img" and a.get("src") is not None: self.imgs.append(a["src"])
    def handle_endtag(self,tag):
        if tag in ("script","style"): self.skip=max(0,self.skip-1)
        if tag=="title": self.intitle=False
    def handle_data(self,d):
        if self.intitle: self.title += d
        if not self.skip:
            t=" ".join(d.split())
            if t: self.text.append(t)

pages={}
for path in all_html():
    rel=os.path.relpath(path,ROOT).replace("\\","/")
    s=open(path,"rb").read().decode("utf-8","replace")
    p=P(); p.feed(s)
    pages[rel]=dict(sha=hashlib.sha256(s.encode()).hexdigest(), size=len(s),
                    links=p.links, imgs=p.imgs, ids=sorted(p.ids), anchors=sorted(p.anchors),
                    textlen=sum(len(x) for x in p.text), title=" ".join(p.title.split()))

def resolve(src, target):
    t=target.strip()
    if not t: return None
    low=t.lower()
    if low.startswith(("http:","https:","mailto:","javascript:","data:","tel:","ftp:")): return ("external",t)
    if t.startswith("#"): return ("anchor",src,t[1:])
    t=urllib.parse.unquote(t)
    path,_,frag = t.partition("#")
    path=path.split("?")[0]
    if not path: return ("anchor",src,frag)
    # absolute from site root if starts with /
    base = ROOT if path.startswith("/") else os.path.dirname(os.path.join(ROOT,src))
    dest=os.path.normpath(os.path.join(base, path.lstrip("/")))
    return ("local",dest,frag)

broken=[]; externals={}; anchors_bad=[]; img_missing=[]
for rel,p in pages.items():
    for href in p["links"]:
        r=resolve(rel,href)
        if r is None: continue
        if r[0]=="external": externals.setdefault(r[1],[]).append(rel)
        elif r[0]=="local":
            dest, frag=r[1],r[2]
            if not os.path.exists(dest):
                broken.append((rel,href,os.path.relpath(dest,ROOT).replace("\\","/")))
            elif frag:
                trel=os.path.relpath(dest,ROOT).replace("\\","/")
                if trel in pages:
                    if frag not in pages[trel]["ids"] and frag not in pages[trel]["anchors"]:
                        anchors_bad.append((rel,href,trel,frag))
                elif not dest.lower().endswith((".html",".htm")):
                    pass
        else:
            src,frag=r[1],r[2]
            if not frag or frag not in pages[src]["ids"] and frag not in pages[src]["anchors"]:
                if frag: anchors_bad.append((rel,href,src,frag))
    for im in p["imgs"]:
        r=resolve(rel,im)
        if r and r[0]=="local" and not os.path.exists(r[1]):
            img_missing.append((rel,im,os.path.relpath(r[1],ROOT).replace("\\","/")))

linked=set()
for rel,p in pages.items():
    for href in p["links"]:
        r=resolve(rel,href)
        if r and r[0]=="local" and r[1].lower().endswith((".html",".htm")):
            linked.add(os.path.relpath(r[1],ROOT).replace("\\","/"))
orphans=sorted(set(pages)-linked-{"index.html"})
# images on disk not referenced
used_imgs=set()
for rel,p in pages.items():
    for im in p["imgs"]:
        r=resolve(rel,im)
        if r and r[0]=="local": used_imgs.add(os.path.relpath(r[1],ROOT).replace("\\","/"))
disk_imgs=set()
for dp,dns,fns in os.walk(ROOT):
    if os.path.relpath(dp,ROOT).split(os.sep)[0] in SKIP_TOP: continue
    for f in fns:
        if f.lower().endswith((".png",".jpg",".jpeg",".gif",".svg",".webp",".mp4")):
            disk_imgs.add(os.path.relpath(os.path.join(dp,f),ROOT).replace("\\","/"))
unused=sorted(disk_imgs-used_imgs)
out=dict(pages=pages, broken=broken, anchors_bad=anchors_bad, img_missing=img_missing,
         externals=externals, orphans=orphans, unused_assets=unused)
json.dump(out, open(os.path.join(ROOT,"_build","baseline.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("PAGES",len(pages))
print("BROKEN LINKS",len(broken)); [print("  ",x) for x in broken]
print("BAD ANCHORS",len(anchors_bad)); [print("  ",x) for x in anchors_bad]
print("MISSING IMGS",len(img_missing)); [print("  ",x) for x in img_missing]
print("ORPHANS",len(orphans)); [print("  ",x) for x in orphans]
print("EXTERNAL URLS",len(externals))
print("UNUSED ASSETS",len(unused)); [print("  ",x) for x in unused[:80]]
