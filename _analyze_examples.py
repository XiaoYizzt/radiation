import os, re, io
root=r"C:\Users\XkXia\Desktop\radiation\tool\WESViewer\wesviewer"
for fn in ["Ra-226.csv","Am241.txt"]:
    p=os.path.join(root,fn); raw=open(p,"rb").read()
    print("="*70); print(fn, "bytes",len(raw), "BOM", raw[:3]==b'\xef\xbb\xbf', "CRLF", b'\r\n' in raw, "LF", raw.count(b'\n'))
    text=raw.decode("utf-8-sig")
    lines=text.replace("\r\n","\n").replace("\r","\n").split("\n")
    if lines and lines[-1]=="": lines.pop()
    print("lines",len(lines))
    print("first 20 raw lines:")
    for i,l in enumerate(lines[:20]): print(f"{i:4d}: {l!r}")
    print("last 8:")
    for i,l in enumerate(lines[-8:],len(lines)-8): print(f"{i:4d}: {l!r}")
    print("empty lines",sum(1 for l in lines if not l.strip()))
    print("comment-ish",sum(1 for l in lines if l.strip().startswith(("#",";","//","---"))))
    if fn.endswith(".csv"):
        rows=[]
        for i,l in enumerate(lines[1:],2):
            if not l.strip(): continue
            parts=next(__import__('csv').reader([l]))
            if len(parts)<3: print("short row",i,parts); continue
            try: rows.append((int(float(parts[0])),float(parts[1]),float(parts[2])))
            except Exception as e: print("bad row",i,parts,e)
        print("data rows",len(rows), "ch min/max",rows[0][0],rows[-1][0])
        print("energy min/max/step",rows[0][1],rows[-1][1],(rows[-1][1]-rows[0][1])/(len(rows)-1))
        print("counts sum",sum(r[2] for r in rows), "min/max",min(r[2] for r in rows),max(r[2] for r in rows), "noninteger",sum(1 for r in rows if r[2]!=int(r[2])))
        print("channel step unique",sorted(set(rows[i+1][0]-rows[i][0] for i in range(len(rows)-1)))[:10])
        print("energy diff min/max",min(rows[i+1][1]-rows[i][1] for i in range(len(rows)-1)),max(rows[i+1][1]-rows[i][1] for i in range(len(rows)-1)))
    else:
        data=[]; meta=[]; header_idx=None
        for i,l in enumerate(lines):
            s=l.strip()
            if not s: continue
            if s.startswith("---"): continue
            m=re.match(r"^\s*([\d.]+)\s*,\s*([\d.]+)\s*$", l)
            if m:
                data.append((float(m.group(1)), float(m.group(2))))
            else:
                meta.append((i,l))
                if "Energy" in l and "Counts" in l: header_idx=i
        print("data rows",len(data),"header idx",header_idx,"meta lines",len(meta))
        print("energy min/max/step",data[0][0],data[-1][0],(data[-1][0]-data[0][0])/(len(data)-1))
        print("counts sum",sum(d[1] for d in data),"min/max",min(d[1] for d in data),max(d[1] for d in data),"noninteger",sum(1 for d in data if d[1]!=int(d[1])))
        print("energy diff unique sample",sorted(set(round(data[i+1][0]-data[i][0],6) for i in range(len(data)-1)))[:10])
        print("meta:")
        for i,l in meta: print(f"  {i:4d}: {l!r}")
