import re,json,sys
src=open(sys.argv[1],encoding='utf-8').read().replace('\r\n','\n')
T=json.load(open('tables.json'))
for n,t in T.items():
    pos=src.index(f"\nTABLE {n}: "); s=src.index('\nNOTES\n',pos)+7; e=src.index('\nCAUTIONS',s)
    txt=src[s:e]
    notes={}; cur=None
    for line in txt.split('\n'):
        m=re.match(r'^(\d+) (.*)',line)
        if m and (cur is None or int(m.group(1))==int(cur)+1): cur=m.group(1); notes[cur]=m.group(2).strip()
        elif cur and line.strip(): notes[cur]+=' '+line.strip()
    t['notes']=notes
    # caution page reference
    c=src[e:e+300]; mm=re.search(r'found on page (\d+)',c); t['caution_page']=mm.group(1) if mm else None
json.dump(T,open('tables.json','w'),ensure_ascii=False,indent=1)
for n in ['2','4','17','20','56' if '56' in T else '52']: print(n,T[n]['title'],len(T[n]['notes']),T[n]['caution_page']); 
print(json.dumps(T['17']['notes'],ensure_ascii=False,indent=0)[:1500])
