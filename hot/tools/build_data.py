import re,json,sys
src=open(sys.argv[1],encoding='utf-8').read().replace('\r\n','\n')
COLS=["FZFG","SN_FZFG","VLSN","LSN","MSN","FZDZ","LFZRA","MSN_RA","RCSW"]
OAT_RE=re.compile(r'(-?\d+(?:\.\d)? °C and above|below -?\d+(?:\.\d)? to -?\d+(?:\.\d)? °C|below -?\d+(?:\.\d)? °C)\s*\n?\s*\(([^)]*°F[^)]*)\)')
VAL_RE=re.compile(r'(\d+:\d{2}) - (\d+:\d{2})(\d*)|N/A')
def rng(lbl):
    m=re.match(r'(-?[\d.]+) °C and above',lbl)
    if m: return [float(m.group(1)),None]
    m=re.match(r'below (-?[\d.]+) to (-?[\d.]+) °C',lbl)
    if m: return [float(m.group(2)),float(m.group(1))]
    m=re.match(r'below (-?[\d.]+) °C',lbl); return [None,float(m.group(1))]
def parse(head):
    p=src.index(head); e=src.index('\nNOTES',p); b=src[p:e]
    b=b[b.index('Other')+5:]; b=re.sub(r'^\d+\n','\n',b,count=1)
    b=re.sub(r'CAUTION:\s*\nNo holdover time\s*\nguidelines exist',' ',b)
    b=re.sub(r'THIS TABLE IS FOR USE.*','',b)
    rows=[]; oats=list(OAT_RE.finditer(b))
    for j,m in enumerate(oats):
        seg=b[m.end(): oats[j+1].start() if j+1<len(oats) else len(b)]
        parts=re.split(r'\b(100/0|75/25|50/50)\b',seg); assert not parts[0].strip()
        for k in range(1,len(parts),2):
            vals=list(VAL_RE.finditer(parts[k+1])); assert not VAL_RE.sub('',parts[k+1]).strip()
            cells={}
            for c,v in zip(COLS,vals):
                cells[c]='N/A' if v.group(0)=='N/A' else [v.group(1),v.group(2)]+([v.group(3)] if v.group(3) else [])
            rows.append({"oat":m.group(1),"oatF":m.group(2).strip(),"range":rng(m.group(1)),"conc":parts[k],"cells":cells})
    return rows
def notes(head):
    p=src.index(head); s=src.index('\nNOTES\n',p)+7; e=src.index('\nCAUTIONS',s); n={}; cur=None
    for line in src[s:e].split('\n'):
        m=re.match(r'^(\d+) (.*)',line)
        if m and (cur is None or int(m.group(1))==int(cur)+1): cur=m.group(1); n[cur]=m.group(2).strip()
        elif cur and line.strip(): n[cur]+=' '+line.strip()
    return n
# frost Type IV (last value of each conc line) from Table 1 / Adj-1
def frost(head):
    p=src.index(head); e=src.index('\nNOTES',p); b=src[p:e]; out=[]
    lbls=list(OAT_RE.finditer(b))
    # labels appear twice per row (Type I column & Type II-IV column); take the 2nd of each pair
    pairs=lbls[1::2] if len(lbls)%2==0 else None
    assert pairs is not None
    for j,m in enumerate(pairs):
        seg=b[m.end(): lbls[2*j+2].start() if 2*j+2<len(lbls) else len(b)]
        for c,a,bb,d in re.findall(r'(100/0|75/25|50/50) (\d+:\d{2}) (\d+:\d{2}) (\d+:\d{2})',seg):
            out.append({"oat":m.group(1),"oatF":m.group(2).strip(),"range":rng(m.group(1)),"conc":c,"typeII":a,"typeIII":bb,"typeIV":d})
    return out
D={"std":parse('\nTABLE 43: '),"adj":parse('\nTABLE ADJ-43:'),
   "notes":notes('\nTABLE 43: '),
   "frost":frost('\nTABLE 1: ACTIVE'),"frostAdj":frost('\nTABLE ADJ-1:'),
   "frostNotes":notes('\nTABLE 1: ACTIVE')}
json.dump(D,open('abcs_data.json','w'),ensure_ascii=False,indent=1)
print(len(D['std']),len(D['adj']),len(D['frost']),len(D['frostAdj']))
for r in D['frost']: print(r['oat'],r['conc'],r['typeIV'])
for r in D['frostAdj']: print('adj',r['oat'],r['conc'],r['typeIV'])
