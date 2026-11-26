import re,json,sys
src=open(sys.argv[1],encoding='utf-8').read().replace('\r\n','\n')
def blk(h):
    p=src.index(h); e=src.index('\nNOTES',p); return src[p:e]
pat=r'(\d+:\d{2}) - (\d+:\d{2})'
std=re.findall(pat,blk('\nTABLE 43: ')); adj=re.findall(pat,blk('\nTABLE ADJ-43:'))
m=lambda s:int(s.split(':')[0])*60+int(s.split(':')[1])
print(len(std),len(adj))
import math
ok=bad=0
for (a,b),(c,d) in zip(std,adj):
    for s,x in ((a,c),(b,d)):
        exp=round(m(s)*0.76)
        if m(x)==exp: ok+=1
        else: bad+=1; print('diff std',s,'adj',x,'0.76x=',m(s)*0.76)
print('ok',ok,'diff',bad)
