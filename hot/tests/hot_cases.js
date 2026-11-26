const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport:{width:390,height:844}});
  const errs=[]; p.on('pageerror', e=>errs.push(e.message));
  await p.goto('file://'+require('path').resolve(__dirname,'..','index.html'));
  const cases = [
    ['IV','100/0',-5,'SN',1600,false,'AUTO',false,'1:50-3:00'],
    ['IV','100/0',-5,'SN',1600,true,'AUTO',false,'1:05-1:50'],
    ['IV','100/0',-5,'SN',500,false,'AUTO',false,'NONE'],
    ['IV','75/25',2,'FZFG',null,false,'AUTO',false,'1:25-2:40'],
    ['IV','100/0',-12,'FZDZ',null,false,'AUTO',false,'NONE'],
    ['IV','100/0',-9,'LFZRA',null,false,'AUTO',false,'0:20-0:30'],
    ['IV','50/50',-4,'FZFG',null,false,'AUTO',false,'NONE'],
    ['IV','100/0',-27,'SN',null,false,'L',false,'0:02-0:07'],
    ['IV','100/0',-3,'FROST',null,false,'AUTO',false,'12:00'],
    ['IV','100/0',-3,'FZFG',null,false,'AUTO',true,'1:39-3:02'],
    ['IV','100/0',3,'SNRA',1600,false,'AUTO',false,'1:05-2:00'],
    ['IV','100/0',-29,'FZFG',null,false,'AUTO',false,'NONE'],
    // Type I
    ['IAL',null,-2,'FZFG',null,false,'AUTO',false,'0:11-0:17'],
    ['IAL',null,-7,'SN',1600,false,'AUTO',false,'0:06-0:11'],   // day -7 1600 Light → LSN row -6..-10
    ['ICOMP',null,-12,'SN',null,false,'M',false,'0:02-0:04'],
    ['IAL',null,-12,'LFZRA',null,false,'AUTO',false,'NONE'],
    ['IAL',null,2,'RCSW',null,false,'AUTO',false,'0:02-0:05'],
    ['IAL',null,-1,'RCSW',null,false,'AUTO',false,'NONE'],
    ['ICOMP',null,-4,'FZDZ',null,false,'AUTO',true,'0:04-0:07'],   // adj of 0:05-0:09 → 3.8→4, 6.84→7
    ['IAL',null,-5,'OTHER',null,false,'AUTO',false,'NONE'],
    ['IAL',null,-5,'FROST',null,false,'AUTO',false,'0:45'],
    ['ICOMP',null,-30,'FROST',null,false,'AUTO',true,'0:27'],
    ['IV','100/0',-3,'PL0',null,false,'AUTO',false,'AT50'],
    ['IV','100/0',0,'PL2',null,false,'AUTO',false,'AT25'],
    ['IV','100/0',1,'PL2',null,false,'AUTO',false,'NONE'],
    ['IV','100/0',-12,'PL1',null,false,'AUTO',false,'AT15'],
    ['IV','100/0',-18,'PL1',null,false,'AUTO',false,'NONE'],
    ['IV','100/0',-20,'PL0',null,false,'AUTO',true,'AT15'],
    ['IV','100/0',-23,'PL0',null,false,'AUTO',false,'NONE'],
    ['IV','75/25',-3,'PL0',null,false,'AUTO',false,'NONE'],
    ['IAL',null,-3,'PL0',null,false,'AUTO',false,'NONE'],
    ['IV','100/0',-7,'PL10',null,false,'AUTO',false,'AT7'],
    ['IV','100/0',5,'PL12',null,false,'AUTO',true,'AT8'],
  ];
  let fail=0;
  for (const [fl,conc,oat,wx,vis,night,im,adj,exp] of cases) {
    const got = await p.evaluate(a => { const h=window.__hot; const w=a[3].startsWith('PL')?'PL':a[3]; Object.assign(h.S,{pl:w==='PL'?+a[3].slice(2):0,fluid:a[0],conc:a[1]||'100/0',oat:a[2],wx:w,vis:a[4],night:a[5],intMode:a[6],adj:a[7]}); h.render(); const R=h.compute(); return R.at ? 'AT'+R.at : R.hot ? (R.hot[1]?R.hot[0]+'-'+R.hot[1]:R.hot[0]) : 'NONE'; }, [fl,conc,oat,wx,vis,night,im,adj]);
    if (got!==exp) fail++;
    console.log(got===exp?'OK ':'BAD', fl,conc,oat,wx,vis,night,im,adj,'=>',got);
  }
  await p.evaluate(()=>{const S=window.__hot.S; Object.assign(S,{fluid:'IAL',oat:-7,wx:'SN',vis:1600,night:false,intMode:'AUTO',adj:false,page:'MAIN'}); window.__hot.render();});
  await p.screenshot({path:'shot3.png'});
  await p.evaluate(()=>{const S=window.__hot.S; Object.assign(S,{fluid:'IV',conc:'100/0',oat:-3,wx:'WX',page:'MAIN',start:600}); });
  await p.evaluate(()=>{window.__hot.S.wx='SN'; window.__hot.render();});
  await p.click('[data-fn="WX"]'); await p.screenshot({path:'shot_wx2.png'}); await p.click('#lsk-R5'); await p.screenshot({path:'shot_pl.png'}); await p.screenshot({path:'shot_pl.png'});
  await p.click('#lsk-R6'); await p.click('#lsk-L1'); await p.screenshot({path:'shot_pl_main.png'});
  // L1 cycle test
  const seq=[]; for (let i=0;i<5;i++){ await p.click('#lsk-L1'); seq.push(await p.evaluate(()=>window.__hot.S.fluid+' '+window.__hot.S.conc)); }
  console.log('L1 cycle', seq.join(' | '));
  console.log('fail',fail,'errors',errs); await b.close();
})();
