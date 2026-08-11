# Texas AI companies and deployed applications

Compiled 2026-08-11. This is the beat record for the technology half of the coverage: who is
building AI in Texas, and where AI is actually running in the state, in the cities and outside
them.

**Verification marks used throughout, and they are load bearing:**

| Mark | Meaning |
|---|---|
| `[V]` | A first-party page was fetched and it said this |
| `[V-listing]` | Appears in a curated trade directory, sourced to the company's own claim |
| `[P]` | The page was fetched but the specific number or date was not on it |
| `[U]` | Unverified, from secondhand or prior knowledge. **Must be re-checked before publishing** |
| `[X]` | Attempted and blocked. The blocking itself is recorded because it is operationally useful |

**Nothing marked `[U]` or `[X]` may be published.** The claims file is the gate, not this file.
This document is a map of where to look and what to distrust, not a source.

---

## 1. The one structural rule this beat needs

Almost everything written about AI companies is an announcement wearing the clothes of a
deployment. The research pass ran into this constantly, and the pattern is sharp enough to be
worth building the schema around rather than handling case by case.

**Every AI application this publication reports carries a maturity field, and it is one of four
values:**

| Value | Test it must pass |
|---|---|
| `announced` | Somebody said they will do it. A press release, a keynote, an MOU. |
| `piloted` | It is running on real inputs at limited scope, and the operator says so. |
| `deployed` | It is running in production, and the operator names a scale, a site or a date. |
| `verified_by_third_party` | Someone with no stake in the claim checked it and published. |

Two live examples of why this is not pedantry:

- **MD Anderson's data science institute says on its own page that its AI work is in pilots and
  initiatives in development, not deployed patient care** `[V]`. A publication that reports
  "MD Anderson uses AI to predict surgical complications" has misrepresented a source that was
  being careful with the reader.
- **Aurora's June 25th, 2026 independent safety assessment by Edge Case** `[V]` is the only
  `verified_by_third_party` item the whole research pass found. That rarity is itself the story,
  and a schema that can express it is a schema that can report it.

No existing Texas outlet tags this. Doing so would make the record more useful than anything
currently published on the beat, and it costs one enum field.

---

## 2. The framing correction to carry into every transport story

**The "I-45 Dallas to Houston lane" framing is out of date.** Verified 2026 driverless activity
in Texas is:

- **Fort Worth to El Paso**, the Werner pilot on Aurora's own homepage `[V]`. That is I-20 and
  I-10 West Texas, not I-45.
- **The Permian Basin**, Kodiak driverless trucks running oilfield logistics for Atlas Energy
  Solutions, expanded July 31st, 2026 `[V]`.
- **Houston to Dallas**, Bot Auto, which is the one that fits the old framing `[V]`.

National coverage still writes the I-45 version. Repeating it would be the tell that we read the
coverage instead of the sources.

---

## 3. Verified deployments, strongest evidence first

### Autonomous trucking, the best-evidenced AI deployment in Texas

| Operator | Status | Evidence |
|---|---|---|
| **Aurora Innovation** (Pittsburgh HQ, Texas operations) | Commercially driverless since **May 1st, 2025**. Day and night since **August 7th, 2025**. Second-generation driverless trucks launched **July 22nd, 2026**, hauling customer freight with nobody in the seat | `[V]` aurora.tech/newsroom, ir.aurora.tech |
| **Bot Auto** (Houston) | 40 mile driverless validation on I-10 with no onboard personnel, **September 2025**. First US humanless commercial freight run, **about May 8th, 2026** | `[V]` bot.auto/news |
| **Kodiak AI** (California HQ, Texas operations center) | Driverless in the **Permian Basin** with Atlas Energy Solutions, expanded **July 31st, 2026**. Cumulative **2.6M+ autonomous miles, 7,000+ loads** | `[V]` kodiak.ai/news |
| **Waabi** | Nothing verified | `[U]` |

Aurora's 2026 customer announcements, which are `announced` and not `deployed`: Charger Logistics
(July 28th), Value Truck (July 27th), AVI-SPL (June 18th), **Volvo Autonomous Solutions and DSV
in Texas (May 13th)** `[V]` from the IR release index.

Aurora's exact driverless mileage is `[P]`. The homepage says only "millions of autonomous miles"
and the Q2 2026 results release was not retrievable. Do not publish a figure.

### Robotaxis

- **Dallas** `[V]`: launched February 2026, open to all public riders **August 4th, 2026**,
  **nearly 150,000 riders** since February. Testing autonomous freeway operation and Dallas Love
  Field terminals.
- **Austin** `[V]`: live, hailed through the Uber app rather than Waymo's. Included in the
  May 13th, 2026 expansion. Fleet size and service area for Austin specifically are `[P]`.
- **Houston** `[P]`: named in the May 13th expansion, operational status not confirmed.
- **San Antonio** `[V-absent]`: Waymo does not mention it.

### Rural and agricultural, the most under-covered material on the beat

`agrilifetoday.tamu.edu` is fully fetchable including its `?s=` search, has a deep archive, and
publishes dated AI work with named researchers every few weeks. **Nobody outside agriculture
reads it.** It is the single best rural AI source in Texas.

- **Cotton digital twins, Coastal Bend** `[V]`, April 22nd, 2026. **11 cotton producers are
  receiving output now.** Drone and satellite remote sensing building digital twins, near daily
  crop development updates, canopy heat maps, crop termination timing, lint yield forecasts.
  Team at the Corpus Christi center: Juan Landivar (director), Josh McGinty, Yuri Calil,
  Mahendra Bhandari, Pankaj Pal, Jose Landivar, Lei Zhao. **This is `deployed`, not `announced`.**
- **Thrips forecasting, High Plains** `[V]`, April 30th, 2026. Machine learning population
  forecasting at **about 88 percent accuracy in open fields and 85 percent in high tunnels**.
  Kiran Gadhave with Arinder Arora and Nolan Anderson, at Bushland and Canyon. **Farmer
  availability is not stated**, which is the actual story.
- **Rangeland drones** `[V]`, July 9th, 2026. Humberto Perotto's lab, seven FAA certified student
  pilots, invasive species identification producing a geolocated map of plants inches tall across
  hundreds of acres in an hour. **Explicitly research and not deployed on working ranches.**
- Also verified: livestock sustainability decision modeling (Karun Kaniyamattam), soil and water
  ML in the Rolling Plains (Chris Cobos, Gurjinder Baath), rice phenotyping, deep learning protein
  design for plant immunity, AI for tuberculosis drug discovery.

### Enterprise, where AI touches the most Texas workers

All company-stated `[V-listing]` from the Dallas Innovates AI 75, March 30th, 2026. Treat as
`deployed` only with the "company-stated" qualifier attached.

Toyota North America (Plano), enterprise AI serving **500,000+ North American users**. Keurig
Dr Pepper (Dallas), **700+ agentic use cases in production**. AT&T (Dallas), thousands of
autonomous agents. Everseen (Dallas), computer vision across **8,600 retail stores**. DFW Airport,
digital twins and autonomous ground operations, **a public entity whose records are requestable**.
Sabre Labs (Southlake) on Google Gemini. Oculon Intelligence (Dallas), agentic market surveillance
**for the Texas Stock Exchange**. 7-Eleven, Toshiba Global Commerce, Vizient, CorroHealth, Axxess,
Lockheed Martin Skunk Works, Airbus US (autonomous UH-72 Lakota), Caterpillar (**$100M workforce
development commitment**).

---

## 4. Companies worth tracking

Highest-confidence first-party findings:

- **Saronic Technologies** (Austin) `[V]`. Autonomous surface vessels. Funding ladder verified on
  their own newsroom: Series A $55M, B $175M at $1B, C $600M, **D $1.75B at a $9.25B valuation**.
  Building **Port Alpha in Brownsville**, plus $300M into a Louisiana yard, partnered with Samsung
  Heavy Industries, NVIDIA and Hornbeck Offshore. The most valuable Texas-headquartered AI-native
  company the pass could verify, and among the least covered.
- **Apptronik** (Austin `[U]`) `[V]` on partners only: Google DeepMind, NVIDIA, GXO,
  Mercedes-Benz, Jabil, Synology. Their site does **not** state HQ or funding and `/news` is 404.
  **Apollo's deployment status is not claimed on their own homepage**, so "deployed at Mercedes"
  is pilot-level until proven.
- **Avathon** (Austin `[U]`) `[V]` on product and customers: National Grid, Aramco, Ørsted,
  BAE Systems, UBS, Airbus. **The site does not confirm the SparkCognition rename** `[U]`.
- **Bot Auto** (Houston), $20M October 2024 `[V]`. CEO Xiaodi Hou, ex-TuSimple.

Houston `[V-headline]` from InnovationMap: VC funding **neared $1B in H1 2026** across 15+
startups; **Applied Computing** (London) chose Houston for its first US office after a $20M raise;
**Rice won a $19M NSF grant** for an AI-driven quantum materials lab.

---

## 5. Negative findings, which are reportable

Absence is a finding when it is checked. Each of these was actually looked for.

- **Cerebras lists no Texas facility** `[V]`. HQ is 1237 E. Arques Ave, Sunnyvale. Mentions North
  American datacenter expansion without naming Texas.
- **SambaNova shows no Texas presence** `[V]`. Founded Palo Alto, sovereign AI partners in the UK,
  EU and Australia, no Texas location on the About page.
- **Abridge's own press page names no Texas health system** `[V]`, while announcing WVU Medicine
  expanding across **rural** hospitals. If Texas systems run ambient AI they run it on someone
  else's vendor or without a joint announcement.
- **Virtual fencing has essentially no public Texas record** `[V-absent]`. A search of the entire
  A&M AgriLife archive returned one hit, a demonstration at the 2024 Beef Cattle Short Course.
  Montana, Colorado and Australia are scaling it. In a state with millions of cattle, that gap
  wants an explanation.
- **TxDOT's newsroom carries no AI, connected-vehicle or data-analytics stories** `[V-absent]`.
- **No Texas institution's own site claimed an NSF AI Institute designation** in anything fetched
  `[V-absent]`. Check NSF's own list before asserting either way.

---

## 6. Research institutions

- **Rice, Ken Kennedy Institute** `[V]`. Focus stated as responsible AI with emphasis on health,
  urban communities and resilient futures. Runs a Corporate Partner Program. Lydia Kavraki and
  Rebecca Richards-Kortum.
- **Texas A&M, TAMIDS** `[V]`. SciML Lab (Ulisses Braga-Neto), SPARTA Lab, Generative AI Literacy
  Initiative, RAISE. **Joined OpenAI's NexGenAI Consortium**, which is specific and citable.
- **MD Anderson, IDSO** `[V]`. Caroline Chung and David Jaffray. Pilots, not deployments, per
  their own page. A Center for Cellular Language Intelligence announced April 28th, 2026.
- **TCU** `[V]`, a $10M "AI²" initiative under Reuben Burch.
- **East Texas A&M (Commerce)** `[V]`, Semantic AI and Creativity Laboratory under Christian
  Hempelmann. **A rural-serving regional university with a named AI lab**, which is unusual.
- **TACC** `[X]`. `tacc.utexas.edu` returns 403 domain-wide. **Nothing about Vista, Horizon,
  Frontera, Stampede3 or Lonestar6 is verified.** Do not publish their status, cost or hardware
  from memory. Find an NSF or UT System mirror.
- **UTSA** `[X]`, JS-only newsroom. Only the existence of a College of AI, Cyber and Computing is
  confirmed `[V-nav]`.

---

## 7. Source accessibility, an operational record

A publication that re-verifies every fact daily needs to know which sources a machine can
actually reach. This is a pipeline constraint, not trivia.

**Fetchable and high yield:** agrilifetoday.tamu.edu (plus `?s=` search), dallasinnovates.com,
houston.innovationmap.com, aurora.tech and ir.aurora.tech, kodiak.ai, bot.auto, waymo.com/blog,
gov.texas.gov/news, greentownlabs.com, kenkennedy.rice.edu, tamids.tamu.edu, mdanderson.org
institute pages, and the company sites for Saronic, Apptronik and Avathon.

**CORRECTION, 2026-08-11, same day.** An earlier draft of this section listed texastribune.org and
texasstandard.org as returning 403. **That was wrong, and the way it was wrong matters more than
the fact.** A later pass fetched the same Tribune article URL at the same moment with `curl` and
got **HTTP 200, 292,873 bytes, correct headline**. The 403 was the fetching tool's, not the site's.

**The lesson is a standing rule: a tool-level failure is not a property of the source.** Before any
domain goes on a blocked list that automations will inherit, it must be retested with a second
client. Writing off the best news source in Texas on a single tool's error would have quietly
degraded every run, and nothing would have thrown.

Genuinely unreachable, retested: tacc.utexas.edu (403 domain wide), hpcwire.com (403),
therobotreport.com (403), texasattorneygeneral.gov (402), news.utsa.edu (JS only),
utsouthwestern.edu/newsroom (JS only), porthouston.com (404), newsroom.heb.com (empty),
flocksafety.com/newsroom (404), tea.texas.gov deep links (404), comptroller.texas.gov BEAD
sub-pages (404). **These carry the same caveat**: each was blocked for one client, and the
`www.ferc.gov` case is the only one independently confirmed against two.

Full source detail lives in `SOURCES_REGISTRY.md`.

---

## 8. The gaps, in priority order

These are open assignments, not findings.

1. **TEA's STAAR automated scoring engine.** Probably the most consequential AI the State of
   Texas has deployed on its own citizens, because it grades children. Both the agency page and
   the Tribune were unreachable. `[X]` **Nothing about it may be published yet.**
2. **Texas BEAD and broadband allocation numbers.** Rural broadband gates every rural application
   in this document, and the public accounting was not retrievable. The absence of a public
   tracker is itself a story.
3. **TACC**, blocked domain-wide.
4. **Dallas Fed Texas Business Outlook Surveys.** Their special questions have historically asked
   Texas firms about AI adoption and employment effects. This is the best available evidence
   source for AI displacement in Texas and it was not retrieved.
5. **San Antonio entirely.** UTSA, USAA, the cyber cluster, the National Security Collaboration
   Center. All JS-gated.
6. **Public safety.** Flock ALPR, gunshot detection, 911 triage. Zero verified coverage.
7. **Rural healthcare AI.** The largest hole relative to its importance.
8. Big-corporate Texas operations: NVIDIA/Foxconn Houston, Wistron Dallas, Samsung Taylor,
   TI Sherman, Dell, and whether Oracle's HQ is still in Austin `[U]`, which prior knowledge
   suggests moved to Nashville in 2024 and would make the common phrasing wrong.

---

## 9. Story angles the record supports

Ranked by verifiability and by whether they make this read like Texas rather than like Austin.

1. **The Permian is the real driverless proving ground, not I-45.** Verifiable from both
   companies' own sites, and filed by everyone else under oilfield logistics rather than AI.
2. **Nobody maintains a Texas driverless scoreboard.** Three operators at three maturity levels
   on three different road types. Operator, road, county, trucks, miles, last verified. **This is
   exactly what a docket is for** and it would be ours.
3. **Eleven cotton farmers in the Coastal Bend are already living in it.** The most concrete
   deployed rural AI in Texas, with named researchers, and no general-audience coverage.
4. **An 88 percent accurate pest forecast with no delivery mechanism.** The story is the last
   mile, and whether rural broadband is what stands in it.
5. **Virtual fencing has not come to Texas and nobody has asked why.**
6. **Ambient AI's Texas blind spot.** A vendor announcing rural West Virginia and no Texas system
   at all, while the flagship Texas cancer center says its own AI is not deployed.
7. **The enterprise layer nobody writes about because it is not a startup.** Where AI actually
   touches Texas workers, while the tech press covers seed rounds.
8. **A new national stock exchange in Dallas is regulating itself with agentic AI from day one.**
9. **An AI defense company is building a shipyard in Brownsville.** AI manufacturing capital
   landing in one of the poorest metros in the country.
10. **Rural broadband is the precondition and nobody can tell you where it stands.**

The recurring question that would differentiate this publication permanently, asked of every
rural result: **can a producer, a county clinic, or a 300 student district actually get this, and
what does it cost?**

---

## 10. Handle with care

- **The Dallas Innovates AI 75 is trade-press profiles built on company-stated claims.** It is the
  densest Texas AI directory that exists and it is DFW only, people-centric, and carries no
  funding data. Cite it as what it is.
- **There is no statewide Texas AI company tracker.** Austin, Houston and San Antonio have nothing
  comparable to the AI 75. That is an opening, and it is also why our coverage will be uneven by
  metro unless we work at it.
- **Houston Community College rendered its own name as "Houston City College"** on the program
  page `[U]`. Possible rebrand. Check before printing either.
- **USAA is San Antonio headquartered**, but its AI 75 honoree is Dallas-based. Do not relocate the
  company on the strength of the listing.
- **Greentown Labs Houston is hardware and climatetech oriented, not AI oriented** `[V]`. Its own
  member page surfaces no AI companies. Do not use it as an AI proxy.
