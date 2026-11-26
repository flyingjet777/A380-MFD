import re,json,sys
src=open(sys.argv[1],encoding='utf-8').read().replace('\r\n','\n')
COLS=["FZFG","SN_FZFG","VLSN","LSN","MSN","FZDZ","LFZRA","MSN_RA","RCSW"]
OAT_RE=re.compile(r'(-?\d+(?:\.\d)? °C and above|below -?\d+(?:\.\d)? to -?\d+(?:\.\d)? °C|below -?\d+(?:\.\d)? °C)\s*\n?\s*\(([^)]*°F[^)]*)\)')
VAL_RE=re.compile(r'(\d+:\d{2}) - (\d+:\d{2})(\d*)')
def rng(lbl):
    m=re.match(r'(-?[\d.]+) °C and above',lbl)
    if m: return [float(m.group(1)),None]
    m=re.match(r'below (-?[\d.]+) to (-?[\d.]+) °C',lbl)
    if m: return [float(m.group(2)),float(m.group(1))]
    m=re.match(r'below (-?[\d.]+) °C',lbl); return [None,float(m.group(1))]
def parse(head):
    p=src.index(head); e=src.index('\nNOTES',p); b=src[p:e]
    b=b[b.index('Other')+5:]; b=re.sub(r'^\d+\n','\n',b,count=1)
    b=re.sub(r'CAUTION:\s*\nNo holdover time\s*\nguidelines exist',' ',b); b=re.sub(r'THIS TABLE IS FOR USE.*','',b)
    rows=[]; oats=list(OAT_RE.finditer(b))
    for j,m in enumerate(oats):
        seg=b[m.end(): oats[j+1].start() if j+1<len(oats) else len(b)]
        vals=list(VAL_RE.finditer(seg)); assert not VAL_RE.sub('',seg).strip(), seg
        cells={c:[v.group(1),v.group(2)]+([v.group(3)] if v.group(3) else []) for c,v in zip(COLS,vals)}
        rows.append({"oat":m.group(1),"oatF":m.group(2).strip(),"range":rng(m.group(1)),"cells":cells})
    return rows
def notes(head):
    p=src.index(head); s=src.index('\nNOTES\n',p)+7; e=src.index('\nCAUTIONS',s); n={}; cur=None
    for line in src[s:e].split('\n'):
        m=re.match(r'^(\d+) (.*)',line)
        if m and (cur is None or int(m.group(1))==int(cur)+1): cur=m.group(1); n[cur]=m.group(2).strip()
        elif cur and line.strip(): n[cur]+=' '+line.strip()
    return n
T1={"al":parse('\nTABLE 2: '),"comp":parse('\nTABLE 3: '),"alAdj":parse('\nTABLE ADJ-2:'),"compAdj":parse('\nTABLE ADJ-3:'),"notes":notes('\nTABLE 2: ')}
json.dump(T1,open('typei_data.json','w'),ensure_ascii=False,indent=1)
m=lambda s:int(s.split(':')[0])*60+int(s.split(':')[1])
for a,b in (("al","alAdj"),("comp","compAdj")):
    ok=bad=0
    for ra,rb in zip(T1[a],T1[b]):
        assert ra['oat']==rb['oat'] and list(ra['cells'])==list(rb['cells'])
        for c in ra['cells']:
            for i in (0,1):
                s,x=m(ra['cells'][c][i]),m(rb['cells'][c][i])
                if x==round(s*0.76): ok+=1
                else: bad+=1; print(a,ra['oat'],c,ra['cells'][c][i],'adj',rb['cells'][c][i],s*0.76)
    print(a,'ok',ok,'diff',bad)
for k in ("al","comp"):
    for r in T1[k]: print(k,r['oat'],{c:'-'.join(v[:2]) for c,v in r['cells'].items()})
print(T1['notes'].keys())
