import re, json, sys
src = open(sys.argv[1], encoding='utf-8').read().replace('\r\n','\n')
# locate table bodies (uppercase headings)
heads = [(m.start(), int(m.group(1)), m.group(2)) for m in re.finditer(r'^TABLE (\d+): (.+)$', src, re.M)]
out = {}
COLS_SPLIT = ["FZFG","SN_FZFG","VLSN","LSN","MSN","FZDZ","LFZRA","MSN_RA","RCSW"]
COLS_SINGLE = ["FZFG","SN_FZFG","SN","FZDZ","LFZRA","MSN_RA","RCSW"]
OAT_RE = re.compile(r'(-?\d+(?:\.\d)? °C and above|below -?\d+(?:\.\d)? to -?\d+(?:\.\d)? °C|below -?\d+(?:\.\d)? °C)\s*\n?\s*\(([^)]*°F[^)]*)\)')
VAL_RE = re.compile(r'(\d+:\d{2}) - (\d+:\d{2})(\d*)|N/A')
CONC_RE = re.compile(r'\b(100/0|75/25|50/50)\b')
for i,(pos,num,title) in enumerate(heads):
    if not (2 <= num <= 52): continue
    end = src.index('\nNOTES', pos)
    block = src[pos:end]
    # full title may continue on next line
    lines = block.split('\n')
    full_title = title.strip()
    if not lines[1].startswith('Outside'): full_title += ' ' + lines[1].strip()
    hdr_end = block.index('Other')  # last header column
    header = block[:hdr_end]
    body = block[hdr_end+len('Other'):]
    body = re.sub(r'^\d+\n', '\n', body, count=1)  # footnote mark after "Other"
    split = 'Very Light' in header
    has_conc = 'Concentration' in header
    cols = COLS_SPLIT if split else COLS_SINGLE
    # remove the merged caution text
    body = re.sub(r'CAUTION:\s*\nNo holdover time\s*\nguidelines exist', ' ', body)
    rows = []
    oats = list(OAT_RE.finditer(body))
    for j,m in enumerate(oats):
        seg = body[m.end(): oats[j+1].start() if j+1 < len(oats) else len(body)]
        oat = m.group(1) + ' (' + m.group(2).strip() + ')'
        if has_conc:
            parts = CONC_RE.split(seg)
            leftover = parts[0].strip()
            if leftover: raise SystemExit(f'T{num} unexpected text before conc: {leftover!r}')
            for k in range(1, len(parts), 2):
                conc, txt = parts[k], parts[k+1]
                vals = [ (v.group(0) if v.group(0)=='N/A' else (v.group(1), v.group(2), v.group(3))) for v in VAL_RE.finditer(txt)]
                rest = VAL_RE.sub('', txt).strip()
                if rest: raise SystemExit(f'T{num} {oat} {conc} leftover {rest!r}')
                rows.append((oat, conc, vals))
        else:
            vals = [(v.group(1), v.group(2), v.group(3)) for v in VAL_RE.finditer(seg)]
            rest = VAL_RE.sub('', seg).strip()
            if rest: raise SystemExit(f'T{num} {oat} leftover {rest!r}')
            rows.append((oat, None, vals))
    tbl = {"num": num, "title": full_title, "cols": cols, "rows": []}
    for oat, conc, vals in rows:
        if len(vals) > len(cols): raise SystemExit(f'T{num} too many values {oat} {conc}')
        cells = {}
        for c, v in zip(cols, vals):
            if v == 'N/A': cells[c] = 'N/A'
            else: cells[c] = {"min": v[0], "max": v[1], **({"fn": v[2]} if v[2] else {})}
        tbl["rows"].append({"oat": oat, "conc": conc, "n": len(vals), "cells": cells})
    out[num] = tbl
json.dump(out, open(sys.argv[2],'w'), ensure_ascii=False, indent=1)
for n,t in out.items():
    print(n, len(t['cols']), [ (r['oat'].split(' (')[0], r['conc'], r['n']) for r in t['rows']])
