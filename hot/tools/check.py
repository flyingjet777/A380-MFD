import json,re,sys
T=json.load(open('tables.json'))
src=open(sys.argv[1],encoding='utf-8').read().replace('\r\n','\n')
def m(s): h,mm=s.split(':'); return int(h)*60+int(mm)
bad=0; fns={}
for n,t in T.items():
    seq=[]
    for r in t['rows']:
        for c in t['cols']:
            v=r['cells'].get(c)
            if v is None: continue
            if v=='N/A': seq.append('N/A'); continue
            if m(v['min'])>m(v['max']): print('min>max',n,r['oat'],r['conc'],c,v); bad+=1
            if 'fn' in v: fns.setdefault(n,set()).add((r['oat'],r['conc'],c,v['fn']))
            seq.append(f"{v['min']} - {v['max']}")
    # independent: raw regex over table text between heading and NOTES
    pos=src.index(f"\nTABLE {n}: "); end=src.index('\nNOTES',pos)
    raw=re.findall(r'\d+:\d{2} - \d+:\d{2}|N/A', src[pos:end])
    if raw!=seq: print('SEQ MISMATCH',n,len(raw),len(seq)); bad+=1
print('problems',bad)
for n,s in fns.items(): print(n,sorted(s))
