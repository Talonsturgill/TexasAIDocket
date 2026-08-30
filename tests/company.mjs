// company: the registry read down its columns, driven in a real browser.
//
// THE FIRST CHECK RUNS WITH JAVASCRIPT OFF, same rule as the dossiers and the calendar. These
// pages are lists and counts. Nothing on them should need a script and nothing does.
//
// The counts asserted here are COMPUTED from the ledgers by the test itself rather than typed,
// because a hardcoded 59 would be wrong the day the Comptroller publishes its next list, and a
// test that goes red on correct data is a test somebody deletes.
//
//     SITE=docs node tests/company.mjs

import { chromium } from "playwright";
import fs from "node:fs"; import path from "node:path"; import http from "node:http";
const P="/opt/pw-browsers/chromium"; const L=fs.existsSync(P)?{executablePath:P}:{};
const SITE=path.resolve(process.env.SITE||"docs"); let fails=0;
const REG=JSON.parse(fs.readFileSync("ledger/gridwatch/datacenters.json","utf8")).facilities;
const GRP=JSON.parse(fs.readFileSync("config/entity_groups.json","utf8")).groups;
const norm=s=>String(s).toLowerCase().replace(/[.,'"]/g," ").replace(/\s+/g," ")
  .replace(/\b(llc|l\s?l\s?c|inc|incorporated|ltd|limited|lp|l\s?p|corporation|corp|company|co|holdings|us|usa)\b/g," ")
  .replace(/\s+/g," ").trim();
const reach=new Map(), spell=new Map();
for(const f of REG) for(const r of ["owners","occupants","operators"]) for(const raw of (f[r]||[])){
  const k=norm(raw); if(!k) continue;
  if(!reach.has(k)) reach.set(k,new Set()); reach.get(k).add(f.name);
  if(!spell.has(k)) spell.set(k,new Set()); spell.get(k).add(String(raw).trim());
}
const MULTI=[...reach.values()].filter(v=>v.size>=2).length;
const SPLIT=[...spell.values()].filter(v=>v.size>1).length;
const PAGES=MULTI+GRP.length;
const ok=(n,c,x="")=>{console.log(`  ${c?"ok  ":"FAIL"}  ${n}${c?"":"  "+x}`); if(!c)fails++;};
const T={".css":"text/css",".png":"image/png",".webp":"image/webp",".svg":"image/svg+xml",".woff2":"font/woff2",".json":"application/json",".xml":"application/xml"};
const srv=http.createServer((rq,rs)=>{let f=path.join(SITE,decodeURIComponent(rq.url.split("?")[0]));
  if(!f.startsWith(SITE)){rs.writeHead(403).end();return;}
  try{if(fs.statSync(f).isDirectory())f=path.join(f,"index.html");fs.statSync(f);}catch{rs.writeHead(404).end("no");return;}
  rs.writeHead(200,{"content-type":T[path.extname(f)]||"text/html"});fs.createReadStream(f).pipe(rs);});
await new Promise(r=>srv.listen(0,"127.0.0.1",r));
const O=`http://127.0.0.1:${srv.address().port}`;
const b=await chromium.launch(L);
{
  const ctx=await b.newContext({javaScriptEnabled:false}); const p=await ctx.newPage();
  const r=await p.goto(`${O}/company/`,{waitUntil:"domcontentloaded"});
  ok("the company hub serves with script off", r.status()===200, String(r.status()));
  const n=await p.$$eval(".clist li a",a=>a.length);
  ok("it lists every company with a page", n===PAGES, `${n} of ${PAGES}`);
  const s=await p.$$eval(".csplit li",e=>e.length);
  ok("it names the companies split by punctuation", s===SPLIT, `${s} of ${SPLIT}`);
  await ctx.close();
}
{
  const p=await b.newPage({viewport:{width:1280,height:900}});
  const r=await p.goto(`${O}/company/oracle-america-cloud-services-llc/`,{waitUntil:"domcontentloaded"});
  ok("the Oracle page serves", r.status()===200);
  const d=await p.evaluate(()=>({
    h1:(document.querySelector("h1")||{}).textContent,
    reach:(document.querySelector(".cstat:first-child strong")||{}).textContent,
    stats:document.querySelectorAll(".cstat").length,
    facs:document.querySelectorAll(".cfac").length,
    linked:document.querySelectorAll(".cfac a").length,
    vars:document.querySelectorAll(".cvars li").length,
    relations:document.querySelectorAll(".crelation").length,
    relationCopy:(document.querySelector(".crelations")||{}).textContent}));
  ok("it names Oracle", (d.h1||"").includes("Oracle"), d.h1);
  const ORACLE=reach.get(norm("Oracle America Cloud Services, LLC")).size;
  ok("it reports the computed facility count", (d.reach||"").includes(String(ORACLE)), d.reach);
  ok("it lists all of them", d.facs===ORACLE, `${d.facs} of ${ORACLE}`);
  ok("it separates reach from the three filed roles", d.stats===4, String(d.stats));
  ok("it shows both spellings the state used", d.vars===2, String(d.vars));
  ok("dossiered facilities link through", d.linked>=1, String(d.linked));
  ok("it explains graph lines with exact shared-row cards",
    d.relations>0 && (d.relationCopy||"").includes("It is a registry relationship"),
    `${d.relations} relationship cards`);
  await p.close();
}
{
  const p=await b.newPage({viewport:{width:390,height:780},isMobile:true});
  await p.goto(`${O}/company/riot-platforms/`,{waitUntil:"domcontentloaded"});
  const m=await p.evaluate(()=>({over:document.documentElement.scrollWidth-document.documentElement.clientWidth,
    note:!!document.querySelector(".csum"), members:document.querySelectorAll(".cvars li").length}));
  ok("a group page states its reason", m.note);
  ok("...and lists its member entities", m.members>=10, String(m.members));
  ok("no sideways scroll on a phone", m.over<=0, String(m.over));
  await p.close();
}
await b.close(); srv.close();
console.log(fails?`\ncompany: ${fails} FAILED`:"\ncompany: all passed");
process.exit(fails?1:0);
