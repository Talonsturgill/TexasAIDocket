import json
T="https://assets-ir.tesla.com/tesla-contents/IR/TSLA-Q3-2026-Update.pdf"; N="https://static.nhtsa.gov/odi/inv/2026/INOA-AQ26002-17078.pdf"
LOC=" Quote matched against the showrunner's fetch_doc extraction at out/2026-10-24/tmp/src/; a WebFetch re-fetch on October 24th returned the PDF as undecoded binary."
R=[
("c1",0,"Tesla scheduled the live webcast of its third quarter 2026 financial results call for October 21st, 2026.","live webcast of its third quarter 2026 financial results conference call beginning at 4:30 p.m. CT on October 21, 2026","high","Page 32. The PDF prints no publication date of its own."),
("c2",0,"Tesla's installed annual manufacturing capacity table lists Model Y in Texas at more than 375,000 units, status Production.","Texas Model Y >375,000 Production","high","Page 6. The row carries the Texas label itself. Installed capacity, not output."),
("c3",0,"The same table lists Cybertruck at more than 125,000 units of installed annual capacity, status Production, in the rows under the Texas region label.","Cybertruck >125,000 Production","medium","Page 6. Texas by table layout, directly below the Texas Model Y row and above Nevada."),
("c4",0,"The table lists Cybercab at more than 125,000 units of installed annual capacity, status Production, in the rows under the Texas region label.","Cybercab >125,000 Production","medium","Page 6. Texas by table layout. Installed capacity. No count of Cybercabs built or deployed (c34)."),
("c5",0,"The table lists Megapack in Texas at 50 GWh of installed annual capacity, status Production.","Texas Megapack 50 GWh Production","high","Page 6. The page 3 highlights call the same 50 GWh planned capacity."),
("c6",0,"The table lists Optimus in Texas with the status Construction and gives no capacity figure.","Texas Optimus - Construction","high","Page 6, Robotics. The capacity cell is a hyphen."),
("c7",0,"The table lists Optimus in California with the status Early Ramp.","California Optimus - Early Ramp","high","Page 6, Robotics."),
("c8",0,"A footnote to Tesla's capacity tables says installed capacity is not the current production rate.","Installed capacity ≠ current production rate","high","Pages 6 and 7 footnotes. The not-equal sign is the extractor's rendering, kept as found."),
("c9",0,"The footnote says production rates depend on several factors, including equipment uptime.","Production rates depend on a variety of factors, including equipment uptime,","high","Page 6 footnote."),
("c10",0,"The other factors it lists are component supply, downtime for factory upgrades and regulatory considerations.","component supply, downtime related to factory upgrades, regulatory considerations and other factors.","high","Page 6 footnote."),
("c11",0,"Tesla defines the Construction status as factory and infrastructure buildout plus tool installation.","Construction includes factory and infrastructure buildout as well as tool installation.","high","Page 6 footnote."),
("c12",0,"Tesla's supporting infrastructure table lists Cortex 1 in Texas at more than 105 MW of SI training compute, status Production.","Texas Cortex 1 >105 MW Production","high","Page 7. MW here measures compute capacity, and the document gives no grid draw figure."),
("c13",0,"The table lists Cortex 2 at more than 120 MW of SI training compute, status Production, in the row under the Texas region label.","Cortex 2 >120 MW Production","medium","Page 7. Texas by layout only, directly below the Texas Cortex 1 row."),
("c14",0,"The SI training compute rows exclude 40 MW of other compute that is not part of Cortex 1 or Cortex 2.","(1) Excludes 40 MW of other compute not part of Cortex 1 or Cortex 2.","high","Page 7 footnote. The document does not say where the 40 MW sits."),
("c15",0,"The table lists 4680 battery cell manufacturing in Texas at more than 40 GWh of annual capacity, status Production.","Texas 4680 >40 GWh Production","high","Page 7."),
("c16",0,"The table lists Cathode Materials at 10 GWh, status Early Ramp, in the rows under the Texas region label.","Cathode Materials 10 GWh Early Ramp","high","Page 7. Texas by layout, and the battery paragraph places cathode material production in Texas (c19)."),
("c17",0,"The table lists Lithium Refining at 30 GWh, status Early Ramp, in the rows under the Texas region label.","Lithium Refining 30 GWh Early Ramp","high","Page 7. The battery paragraph names lithium refining in Texas (c19)."),
("c18",0,"Tesla says Early Ramp capacity figures include expected capacity.","Early ramp capacity includes expected capacity.","high","Page 7 footnote."),
("c19",0,"The update's battery section names cathode material production and lithium refining in Texas among its critical projects.","Critical projects include vehicle pack capacity in Berlin, cathode material production and lithium refining in Texas","high","Page 7. A line break after 'cathode' is joined with one space."),
("c20",0,"The update ties increased 4680 cell production to the ramps of both Cybercab and Tesla Semi.","production of our 4680 cells to support the ramps of both Cybercab and Tesla Semi","high","Page 7. The sentence does not say which plant's cells."),
("c21",0,"Tesla plans to reach 400 MW of SI training compute by the end of the year. The update does not say where that compute will sit.","We plan to reach 400 MW of SI training compute by the end of the year","high","Page 7. A plan with no location."),
("c22",0,"Tesla says that compute supports development of both vehicle and humanoid robot autonomy software.","development of both vehicle and humanoid robot autonomy software.","high","Page 7."),
("c23",0,"Tesla continued construction of the Austin Fab during the quarter.","continued construction for the Austin Fab","high","Page 7."),
("c24",0,"Tesla plans to start commissioning equipment at the Austin Fab in 2027.","where we plan to start commissioning equipment in 2027","high","Page 7. A line break is joined with one space. A plan."),
("c25",0,"Tesla says it began production at Megafactory Texas.","We began production at Megafactory Texas.","high","Page 6. No production volume is given."),
("c26",0,"The update's highlights page also says Megafactory Texas began production.","Megafactory Texas began production, with planned","high","Page 3. The next line reads 'capacity of 50 GWh.'"),
("c27",0,"Optimus production began on high volume lines in Fremont, California, not in Texas.","Optimus production began in Fremont on our high- volume lines.","high","Page 6. 'high- volume' is the extractor's spacing, kept."),
("c28",0,"Tesla says it began deploying Cybercab into its Robotaxi fleet in Austin.","We began deployment of Cybercab into our Robotaxi fleet in Austin.","high","Page 8. No vehicle count is given."),
("c29",0,"The highlights say Tesla started providing Robotaxi rides using Cybercabs in Austin on September 3rd.","We started providing Robotaxi rides using Cybercabs on September 3 in Austin.","high","Page 3. NHTSA's resume dates the start September 3, 2026 (c39)."),
("c30",0,"Tesla's operations highlights list the launch of Cybercab into the Robotaxi fleet in Austin.","Launched Cybercab into the Robotaxi fleet in Austin","high","Page 3."),
("c31",0,"Tesla reported nearly two million cumulative unsupervised miles for its whole Robotaxi service as of the end of the quarter. The figure is not broken out for Austin.","nearly two million cumulative unsupervised miles for our Robotaxi service","high","Page 8. Service wide. A line break is joined with one space."),
("c32",0,"The highlights say cumulative unsupervised Robotaxi miles grew eightfold quarter over quarter across the service.","unsupervised Robotaxi miles grew eightfold quarter over quarter","high","Page 3. Service wide."),
("c33",0,"Robotaxi operating hours in Austin now run from 6am to midnight.","Operating hours in Austin are now 6am to midnight","high","Page 8."),
("c34",0,"Tesla's quarterly update gives no count of Cybercab vehicles built, deployed or carrying riders. Its Cybercab figure is installed capacity, which the update says is not the current production rate.","Installed capacity ≠ current production rate and there may be limitations discovered as production rates","high","Absence confirmed by reading every Cybercab mention in the extraction."),
("c35",1,"NHTSA's Office of Defects Investigation resume for AQ26002 shows the investigation as open.","Investigation: AQ26002 Open Resume Page 1 of 1","high","Page footer."),
("c36",1,"The audit query was opened on September 3rd, 2026, prompted by public information.","Prompted By: Public Information Date Opened: 09/03/2026","high","Two header lines joined with one space."),
("c37",1,"The audit query's subject is the FMVSS certification of the Tesla Cybercab.","Subject: Tesla Cybercab FMVSS Certification","high",""),
("c38",1,"NHTSA gives an estimated population of 1,000 vehicles for the audit query.","Population: 1,000 (Estimated)","high","Not a count of Cybercabs deployed."),
("c39",1,"According to NHTSA, Tesla began commercial deployment with a small number of Cybercab vehicles in Austin on September 3rd, 2026.","On September 3, 2026, Tesla began commercial deployment with a small number of its Cybercab vehicles in Austin, Texas","high","A line break is joined with one space."),
("c40",1,"Tesla notified NHTSA that it certified those Cybercab vehicles as compliant with all applicable Federal Motor Vehicle Safety Standards.","Tesla notified the Agency that it certified those Cybercab vehicles as compliant with all applicable Federal Motor Vehicle Safety Standards (FMVSS)","high","Tesla's self certification as reported by NHTSA."),
("c41",1,"Tesla also told NHTSA it plans to gradually expand Cybercab deployment to more vehicles and locations.","expand commercial deployment of the Cybercab to include additional vehicles and locations.","high",""),
("c42",1,"The Cybercab vehicles lack permanently attached conventional manual controls, such as a brake pedal, gas pedal, steering wheel and mirrors.","The vehicles lack permanently attached, conventional manual controls, such as a brake pedal, gas pedal, steering wheel, and mirrors.","high","Line breaks joined with one space."),
("c43",1,"NHTSA opened the audit query to examine the process and technical data Tesla relied on when certifying the Cybercab.","NHTSA is opening this AQ to examine the process and technical data on which Tesla relied when certifying the Cybercab","high","An audit query is an examination, not a finding."),
("c44",1,"NHTSA will consider how far Tesla's certification depended on determinations that certain FMVSS do not apply to the Cybercab.","NHTSA will consider the extent to which Tesla’s certification depended on determinations that certain FMVSS are inapplicable to the Cybercab.","high","The curly apostrophe is the source's own."),
]
out=[]
for cid,src,text,quote,conf,note in R:
    if src==0: c=dict(id=cid,item="tx-2026-0230",text=text,quote=quote,url=T,source_type="primary_corporate",retrieved="2026-10-24",confidence=conf,document="Tesla Q3 2026 Update",published="2026-10-21",version="quarterly_update")
    else: c=dict(id=cid,item="tx-2026-0140",text=text,quote=quote,url=N,source_type="primary_official",retrieved="2026-10-24",confidence=conf,document="NHTSA ODI resume, Audit Query AQ26002",published="2026-09-03",version="open_resume")
    c["source_note"]=(note+LOC).strip()
    out.append(c)
rej=[{"finding":"The update published October 21st as a standalone claim","reason":"The PDF prints no publication date; c1 claims the webcast date."},
{"finding":"Nearly two million unsupervised Robotaxi miles in Austin or by Cybercab","reason":"Page 8 gives the figure for the whole Robotaxi service."},
{"finding":"400 MW of training compute in Texas","reason":"The plan carries no location."},
{"finding":"Optimus production in Texas","reason":"The Texas row reads Construction; production began in Fremont."},
{"finding":"1,000 Cybercabs deployed","reason":"1,000 is NHTSA's estimated population for the audit query."},
{"finding":"Texas capacity rows as output","reason":"Installed capacity, which the footnote says is not the production rate."},
{"finding":"Megafactory Texas producing 50 GWh a year","reason":"Highlights call it planned capacity; neither reading is a production rate."},
{"finding":"Austin Fab as a semiconductor plant","reason":"Only a letter spaced photo caption says so; no usable verbatim quote."},
{"finding":"Fleet wide production and delivery totals","reason":"Not broken out for Texas."},
{"finding":"Independent live re-fetch of the quoted text","reason":"Both URLs answered WebFetch with undecodable PDFs; quotes rest on the run's own fetch_doc extraction."}]
json.dump({"claims":out,"rejected":rej},open("out/2026-10-24/claims.json","w"),indent=1,ensure_ascii=False)
# verify quotes against extraction
import re,sys; sys.path.insert(0,"scripts/site"); import reverify
for c in out:
    f="out/2026-10-24/tmp/src/"+("tesla_q3_2026.txt" if "tesla" in c["url"] else "nhtsa_aq26002.txt")
    t=reverify.norm_quote(open(f).read())
    if reverify.norm_quote(c["quote"]) not in t: print("NOT FOUND",c["id"],c["quote"][:60])
print(len(out))
