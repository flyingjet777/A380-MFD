import re,json,sys
src=open(sys.argv[1],encoding='utf-8').read().replace('\r\n','\n')
# page N text = from "Page N of 91" header to next header
pages={}
hs=list(re.finditer(r'Original Issue Page (\d+) of 91',src))
for i,h in enumerate(hs):
    pages[h.group(1)]=src[h.end(): hs[i+1].start() if i+1<len(hs) else len(src)]
T=json.load(open('tables.json'))
C={}
for p in sorted({t['caution_page'] for t in T.values()}|{'9'},key=int):
    txt=pages[p]; s=txt.index('CAUTIONS')
    body=txt[s+8:]; body=body[:body.index('FAA Holdover')] if 'FAA Holdover' in body else body
    items=[re.sub(r'\s+',' ',b).strip() for b in body.split('•') if b.strip()]
    C[p]=items
    print(p, items)
json.dump(C,open('cautions.json','w'),ensure_ascii=False,indent=1)
