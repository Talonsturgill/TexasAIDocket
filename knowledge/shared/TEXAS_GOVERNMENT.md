# How Texas government actually works

Compiled 2026-08-11 from statute and agency records fetched directly. Marks: **[DOC]** a statute
or primary source actually read, **[REP]** credible journalism actually read, **[UNV]** could not
confirm.

**Statutory citations here were read, not recalled.** Where a section number appears, the text was
retrieved from `tcss.legis.texas.gov`.

---

## 0. ROBOTS EXCLUSIONS THAT CONSTRAIN THIS PROJECT

**These are choices we honor, not obstacles to route around.** Recorded prominently because two
of them will otherwise be rediscovered the hard way.

| Host | Disallows | Consequence |
|---|---|---|
| **`gov.texas.gov`** | **ClaudeBot**, GPTBot, Amazonbot, Applebot, PerplexityBot | **The Governor's press releases and appointment announcements are off limits to us.** This is a real hole on this beat. Route legitimately: agencies republish the same facts, and press coverage quotes the documents |
| **`lrl.texas.gov`** (Legislative Reference Library) | **ClaudeBot and `anthropic-ai`** | Interim-charge archives unavailable |
| `senate.texas.gov/_assets` | all agents | Senate rules, 2026 interim charges and committee PDFs unavailable. Use the allowed `cmte.php` pages |
| `capitol.texas.gov` | `/BillLookup/`, `/Reports/`, `/Search/`, `/TLODOCS/` | **Bill history pages are NOT fetchable.** `/Committees/` IS allowed |
| `ercot.com` | `/AboutERCOT`, `/meetings`, `/committees`, `/about/governance/biography/` | `/about/governance/directors` IS allowed |
| `tacc.utexas.edu`, `data.capitol.texas.gov/api/` | ClaudeBot | Already recorded |

**`statutes.capitol.texas.gov` is now an Angular SPA** and returns a JavaScript shell for every
path. **The real document server is `tcss.legis.texas.gov/resources/{CODE}/htm/{CODE}.{CHAPTER}.htm`**,
with whole-code archives at `/resources/Zips/{CODE}.htm.zip`. Neither host has a robots.txt.

---

## 1. The four open questions, settled from statute

### The ERCOT Board Selection Committee

**Utilities Code 39.1513**, added by SB 2 (87th Legislature, 2021) `[DOC]`:

> "(a) The ERCOT board selection committee is composed of: (1) one member appointed by the
> governor; (2) one member appointed by the lieutenant governor; and (3) one member appointed by
> the speaker of the house of representatives."

Two under-reported clauses:

> "(d) The committee shall select members ... **and shall designate the chair and vice chair of the
> governing body** from those members."
>
> "(e) The ERCOT board selection committee shall **retain an outside consulting firm** to help
> select members of the governing body."

**The selection committee, not the board, picks ERCOT's chair.** And a private search firm
materially shapes who governs the grid. Members are unpaid, must be Texas residents, and there is
no Senate confirmation.

**Board composition, 39.151(g-1)** `[DOC]`: eight members selected by the committee, plus four ex
officio — the PUCT presiding officer (**nonvoting**), one other PUCT commissioner (**nonvoting**),
the ERCOT CEO (**nonvoting**), and **the OPUC Public Counsel, who is the only VOTING ex officio
member**. Legislators are barred; anyone with assets in the ERCOT market is disqualified
(39.151(g-3)); **a former director may not register as a lobbyist for two years** (39.151(g-5)).

**The most consequential sentence in the chapter, 39.151(d)** `[DOC]`:

> "An independent organization certified by the commission is **directly responsible and
> accountable to the commission**. The commission has complete authority to oversee and
> investigate the independent organization's finances, budget, and operations ... The commission
> may take appropriate action ... including **decertifying the organization** or assessing an
> administrative penalty."

**Current selection committee membership is `[UNV]`** — the announcements live on the
ClaudeBot-disallowed Governor's site. Only the Governor's 2021 appointee is known, and by
journalism.

### TCEQ, PUCT and TWDB rosters, and the pattern in them

**TCEQ** `[DOC]`: **Brooke Paup, Chairwoman** (January 2025; previously TWDB member and chair,
Comptroller legislative affairs, OAG); **Catarina R. Gonzales** (February 2024; **budget and policy
advisor, Office of the Governor**); **Tonya R. Miller** (October 2025, term to 2031; **TWDB
director**, then **CEO and Public Counsel of OPUC**, and earlier an **advisor in the Office of the
Governor**).

**PUCT** `[DOC]`, the October 2025 appointee is **Morgan Johnson**, term to September 1st, 2031,
previously **deputy general counsel for the Office of the Governor**. Full roster: **Thomas
Gleeson** (Chairman; **PUCT executive director from December 2020**, 15+ years inside the agency,
and before that a **Legislative Budget Board analyst**), **Kathleen Jackson** (**TWDB board
member**), **Courtney Hjaltman** (**OPUC Public Counsel**, and before that **deputy legislative
director for the Governor**), Morgan Johnson, **Patrick Rhode** (April 2026).

**TWDB** `[DOC]`, and note the statute **allocates seats by profession** (Water Code 6.052: one
engineering, one finance, one law or business): **L'Oreal Stepney, Chairwoman** (**30 years at
TCEQ**, rising to deputy executive director); **W. Brady Franks** (**State Budget Director, Office
of the Governor**, and before that **senior budget advisor to the Speaker**); **Ashley Morgan**
(Office of the Governor, OAG, Railroad Commission, TCEQ).

**The pattern is the finding.** Eleven of the twelve current commissioners across three agencies
came from the Governor's office, another Texas regulator, or the agency's own staff. **TWDB
functions as a farm team** (Paup, Jackson and Miller all moved from it). **OPUC, the consumer
advocate's office, is a stepping stone to the regulator** (Hjaltman and Miller both ran it first).

**The Governor designates the PUCT presiding officer "at the pleasure of the governor"**
(Utilities Code 12.052) `[DOC]`, which is the leash. **The commissioners, not the Governor, select
each agency's executive director** — and the TCEQ executive director signs the technical
determination on every permit before a commissioner ever sees it.

---

## 2. Counties cannot zone, and that is the whole local story

**Nearly half of the 248 planned Texas data centers will be built in unincorporated areas** `[REP]`.

**Local Government Code Chapter 231 is titled "County Zoning Authority." Here are its subchapters,
in full** `[DOC]`:

> General Provisions / Zoning on Padre Island / Zoning Near Amistad Recreation Area / Military
> Zones / Zoning Around Certain Lakes / Zoning Around Lake Tawakoni and Lake Ray Roberts / Zoning
> Around Lake Alan Henry, Lake Cooper, Lake Ralph Hall, Post Lake, and Lower Bois d'Arc Creek
> Reservoir / Zoning and Other Regulation in El Paso Mission Trail Historical Area / Zoning Around
> Lake Somerville / Development Regulations in Hood County / Zoning Around Falcon Lake /
> Regulation of Cottage Food Production Operations

**There is no general county zoning power in Texas. The entire chapter is a list of named lakes,
one island, one historical district and one county.** A Texas county cannot zone a data center out
because the Legislature never gave counties the power to zone at all. Article V Section 18(b)
confers only "such powers and jurisdiction over all county business, as is conferred by this
Constitution and the laws of the State" `[DOC]`.

**What a county CAN do:** plat and subdivision requirements under LG Chapter 232, including a
power that matters here — it may **"require that each purchase contract ... contain a statement
describing the extent to which water will be made available to the subdivision and, if it will be
made available, how and when"** (232.003) `[DOC]`. It can refuse a tax abatement, which is its
sharpest lawful tool. It can pass a symbolic resolution.

**What happens when a county overreaches, both 2026 cases** `[REP]`: **Hill County rescinded its
moratorium after a developer sued for $100 million.** **Hood County pulled its moratorium after a
state senator requested an Attorney General opinion.** An AG opinion request from a committee chair
is a preemption weapon requiring no lawsuit and no vote.

**Home-rule cities are different, and San Marcos is the test case.** There are 352 home-rule
cities `[REP]`. Zoning is a delegated police power under LG 211.003, reaching "the location and use
of buildings, other structures, **and land**" `[DOC]`. San Marcos voted 4-3 on June 16th, 2026 to
define data centers in its land development code and make them **ineligible for any zoning
district**. **The mechanism matters legally: it amended its zoning code, it did not issue a
moratorium**, which is the crux of whether HB 2559's 180-day moratorium cap reaches it at all
`[REP]`.

Cities that cannot afford litigation are doing something smarter: **Lockhart** confined data
centers to heavy industry zoning only, and **Kerrville** restricted where they can build and
**added water capacity approvals requiring developers to disclose cooling systems and water usage
amounts** `[REP]`.

---

## 3. Groundwater: the rule of capture, and where the leverage actually is

**Water Code 36.002** `[DOC]`: "the legislature recognizes that **a landowner owns the groundwater
below the surface of the landowner's land as real property**," but this does **not** entitle an
owner "to the right to capture a specific amount," and does not affect "defenses to liability
**under the rule of capture**."

**Districts are ELECTED, not appointed** — five to eleven directors, four-year terms, by precinct,
and creation itself requires a **confirmation election** (36.051, 36.059, 36.017) `[DOC]`. Special-law
districts may vary `[UNV]`.

**What a district can restrict (36.116)** `[DOC]`: spacing and production, including **"managed
depletion,"** with **different rules for different aquifers or geographic areas**, and it **may
preserve historic or existing use** — so an early mover locks in.

**Export is the real lever (36.122)** `[DOC]`: a district may weigh out-of-district transfer in
granting or denying, but **"may not impose more restrictive permit conditions on transporters than
the district imposes on existing in-district users."** Export fees are capped, **rising three
percent each calendar year** since 2024.

**The joint-planning machine (36.108)** `[DOC]`: within each Groundwater Management Area,
districts must **every five years propose Desired Future Conditions**, weighing nine factors
including subsidence, socioeconomic impact, and private property rights. Adoption needs **a
two-thirds vote of all district representatives**, then **no less than 90 days of public comment**.
The DFC becomes modeled available groundwater, and **that number governs every subsequent permit**.

**The citizen levers, and their price:**
- **DFC appeal (36.1083):** an affected person may petition within **120 days** for a SOAH
  contested case; TWDB must run a technical study within 120 days and **"shall make available
  relevant staff as expert witnesses."** Appeal to district court within 45 days on substantial
  evidence. **This is the strongest citizen lever on the beat and it is almost never used.**
- **Permit challenge (36.4051, 36.416):** the board first decides whether the requester **has
  standing and raised a justiciable issue**. If a SOAH hearing is requested, **"The party
  requesting the hearing ... shall pay all costs associated with the contract for the hearing and
  shall deposit with the district an amount sufficient to pay the contract amount before the
  hearing begins"** (36.416(c)). **The cost barrier is written into the statute.**

**The hole:** roughly 100 districts exist but **not every part of Texas has one**. In an
unregulated county the rule of capture is the only law and a data center can pump with no permit
at all. TCEQ can force the issue by designating a **Priority Groundwater Management Area**, and
**"The designation of a priority groundwater management area may not be appealed"** (35.008(i))
`[DOC]`.

---

## 4. The Legislature as a machine

**The Senate threshold is FIVE-NINTHS, not three-fifths.** Both Texas Legislative Council bill
process charts state it identically: floor consideration "Requires placement on the intent calendar
and **5/9 vote to suspend the regular order of business**" `[DOC]`. **That is 18 of 31, not 19.**
Two-thirds became three-fifths in 2015 and is now five-ninths. **A bare Republican caucus clears it
alone.** Correct this anywhere we have written otherwise.

**How a bill dies: the calendar, and now the mechanism has names.** House bills reported favorably
must be set by the **Committee on Calendars (Chair Todd Hunter, HD-32)** or **Local & Consent
Calendars (Chair Jared Patterson)** `[DOC]`. A bill never set is dead with no recorded vote against
it. The deadline chart compresses the last two weeks into single-day cliffs with 36-hour and
48-hour layout requirements, and TLC's own note says the quiet part: **"it normally takes a full day
or more for a measure to reach the Calendars Committee after ... being reported."** **A chair who
holds a bill four days in May has killed it.**

### The interim charges are next session's bills, and ours are published

House charges obtained in full, **Speaker Burrows, March 2026** `[DOC]`. The Senate's 2026 charges
are behind the robots-disallowed `/_assets` path and remain a gap.

- **STATE AFFAIRS, Charge 9, "Data Centers":** review the regulatory framework and recommend
  proposals "to streamline regulations while enabling communities to plan and manage growth
  responsibly," and **"Study the implementation of SB 6 and the Large Load Batch Study Process
  proposed by [ERCOT]."** State Affairs also carries **SB 6 monitoring** as Charge 1.
- **NATURAL RESOURCES, Charge 5, "Data Center Water Use and Conservation":** examine total water
  usage including direct and indirect, **"particularly in water-stressed regions."**
- **NATURAL RESOURCES, Charge 2, "Groundwater Management":** whether DFCs "provide sufficient
  protection," **"the adequacy of groundwater conservation districts' authority to address
  impacts"** of large-scale production **"including export projects,"** and **"how groundwater
  production in unregulated portions of the state impacts the aquifer management efforts of
  existing groundwater conservation districts."**

**That last charge is the tell. The House is already studying whether to give groundwater districts
authority over export projects and whether to close the unregulated-county hole. That is next
session's water-and-data-centers bill.**

**A jurisdiction split nobody covers:** TCEQ answers to **two different House committees** —
Natural Resources "as it relates to the regulation of water resources," Environmental Regulation
"as it relates to environmental regulation" `[DOC]`. **A TCEQ air permit and a TCEQ water right
answer to different chairs.**

**The people with veto points, named** `[DOC]`: **Todd Hunter** (House Calendars). **Adam Hinojosa**
(Senate Nominations — **every appointment on this beat passes through him**, and note that Gleeson
and Hjaltman **served and voted for over a year before Senate confirmation**, which is a durable
feature). **Charles Schwertner and Phil King** are chair and vice chair of Senate Business &
Commerce **and the authors of SB 6** — they wrote the statute and oversee its implementation.
**Ken King** chairs House State Affairs, which holds the Data Centers charge and jurisdiction over
the PUCT, OPUC and the Office of the Governor. **Cody Harris** chairs House Natural Resources.
**Paul Bettencourt** chairs Senate Local Government. **Giovanni Capriglione**, TRAIGA's author,
chairs Delivery of Government Efficiency. **Judith Zaffirini** is San Marcos's senator, vice chair
of Senate Natural Resources, and publicly backed the city's ban.

### Sunset: the whole electric apparatus opens in 2029

`[DOC]` The **2026 to 2027 cycle** is entirely health and human services. **Nothing on our beat.**

The **2028 to 2029 cycle** contains, in one block: **the PUCT, ERCOT, the Office of Public Utility
Counsel, the Railroad Commission, two river authorities, and the Texas Education Agency.**

Corroborated by the statutory abolition dates: **the PUCT is abolished September 1st, 2029** absent
continuation (Utilities Code 12.005); **ERCOT is reviewed on the same schedule but is never
abolished** (39.151(n)); **TCEQ is abolished September 1st, 2035** (Water Code 5.014), so it is not
in play this decade.

**The entire electric regulatory apparatus opens for statutory rewrite in the 2029 session, with
Sunset staff work running through 2028.** Chair: **Lois Kolkhorst**. Vice Chair: **Lacey Hull**.

> ### CORRECTION, 2026-08-11, same day
>
> An earlier version of this document, and the WORKLOG, called **SB 6's December 31st, 2026
> deadline for the PUC to amend 4CP transmission cost allocation** "the hardest date on the Texas
> data center calendar." **That claim is now CONTESTED and must not be published.**
>
> A second agent **fetched the full text of Utilities Code Chapter 39 and searched it for 2026
> deadline language. The only 2026 date in the chapter is a September 1st, 2026 reference
> elsewhere.** `[DOC, negative]`
>
> The deadline may still be real and sitting in **an uncodified section of the act**, which is
> common for transition and implementation provisions and which neither pass could reach.
> **Resolving it requires reading the enrolled bill**, which lives behind the ClaudeBot-disallowed
> `capitol.texas.gov/BillLookup/` path and therefore needs a human or another route.
>
> **This is exactly the failure the verification marks exist to catch.** The date arrived marked
> `[DOC]`, it was load-bearing, and it was wrong or at least unproven. Where the codified text is
> silent, the honest statement is that **PUCT Project 58482 is where SB 6 is actually being
> implemented**, and that is verifiable from the Interchange filing system today.

---

## 5. The courts, and a 2023 change that reroutes every case on this beat

**The Fifteenth Court of Appeals**, created by SB 1045 (88th Legislature), effective September 1st,
2023. **Seated in Austin, but "composed of all counties in this state" (Gov Code 22.201(p)), so its
justices are elected statewide, not by an Austin-area electorate** `[DOC]`.

**Its jurisdiction is exclusive, Gov Code 22.220(d)** `[DOC]`:

> "The Court of Appeals for the Fifteenth Court of Appeals District has **exclusive intermediate
> appellate jurisdiction** over the following matters arising out of or related to a civil case:
> (1) matters brought by or against the state or a board, commission, department, office, or other
> agency in the executive branch ... (2) matters in which a party ... challeng[es] the
> constitutionality or validity of a state statute or rule **and the attorney general is a party**"

What that means here:

- A challenge to a **PUCT order, TCEQ permit or TWDB action** is still filed in **Travis County
  district court** (Gov Code 2001.176(b)(1)), **but now appeals to the Fifteenth, not the Third.**
- **A constitutional challenge to HB 2127, HB 2559 or TRAIGA, with the AG as a party, goes to the
  Fifteenth.**
- **Eminent domain and condemnation are expressly carved OUT** (22.220(d)(1)(F)), so a transmission
  line condemnation fight still appeals through the ordinary district.

**The Legislature created a single statewide-elected appellate court, seated in Austin, that hears
every appeal against a state agency and every constitutional challenge the AG defends. It is now
the chokepoint for every legal challenge on this beat except condemnation.**

The standard of review for PUCT matters is **substantial evidence** (Utilities Code 15.001)
`[DOC]`, the most deferential ordinary standard. The same standard governs a DFC appeal.

**HB 2127 posture:** the challenge was **dismissed on standing on July 18th, 2025 and the law
stands** `[REP]`. It has never been tested on the merits, which is consistent with city council
members saying they are willing to try `[REP]`.

---

## 6. TRAIGA preempts all local AI regulation

**Business & Commerce Code 552.003** `[DOC]`:

> "This chapter **supersedes and preempts any ordinance, resolution, rule, or other regulation
> adopted by a political subdivision** regarding the use of artificial intelligence systems."

**And 552.101** `[DOC]`: "the **attorney general has exclusive authority** to enforce this chapter
... This chapter does not provide a basis for, and **is not subject to, a private right of
action**."

**Texas has one AI law, one enforcer, and zero local authority over AI use.** A city ordinance
about AI is void by statute. **A city ordinance about a data center building is a land use question
and survives on different ground.** Keeping those two categories distinct is the whole legal game
for municipalities.

**There appear to be TWO sandboxes, and conflating them is an error.** `[DOC]`

- **B&C Chapter 553**, created by TRAIGA, DIR-run, up to **36 months**, and while enrolled **"The
  attorney general may not file or pursue charges against a program participant for violation of a
  law or regulation waived under this chapter."** Carve-out: **Subchapter B of Chapter 552 may
  never be waived.** This one governs **private-sector** participants.
- **Government Code 2054.706**, added by **SB 1964, effective September 1st, 2025** — **four months
  BEFORE TRAIGA** — letting **eligible public entities** contract with registered vendors to test
  AI systems **"without full compliance with otherwise applicable regulations."** Quarterly
  participant reports, and **DIR must report to the Legislature by November 30th of each
  even-numbered year, making November 30th, 2026 the first reporting date.**

**The sandbox is widely attributed to TRAIGA. The public-entity one is not TRAIGA's.** Getting that
attribution right is a small correction that signals we read the statute.

**Whether DIR has actually stood either programme up is `[UNV]`.** No DIR page was fetched. **The
November 30th, 2026 report is the honest hook.**

**The Council (B&C Chapter 554)** `[DOC]`: **seven members — three appointed by the Governor, two
by the Lt. Governor, two by the Speaker. The Governor appoints the chair. No Senate confirmation.**
Administratively attached to DIR. Its charter includes evaluating **"potential instances of
regulatory capture, including undue influence by technology companies."**

**Current membership: `[UNV]`, and this is the highest-value unfilled name list on the beat.**

**A second pass could not find the Council in Government Code or in B&C 552 at all** `[DOC,
negative]`, and suggested it may have been cut in the Senate or left uncodified. **Note the two
passes searched different codes**, so this is not a clean contradiction: the first read B&C
Chapter 554 and quoted it. **Treat the Council's codified existence as CONTESTED until someone
reads B&C 554 and the enrolled bill against each other.** Either answer is publishable and
interesting: a seated-but-unnamed council, or a statutory body that never made it into the code.

### The codification conflict, and it is the strongest original finding in the seed set

`[DOC]` **Three separate acts of the 89th Legislature each added a "Subchapter S" to Government
Code Chapter 2054, and two of them number their sections identically. Section 2054.702 exists
TWICE with entirely different commands**, as do 2054.701 and 2054.703 through 2054.705.

**The codifier has flagged the conflict in the published code rather than resolved it. Which text
governs a state agency's AI duties is unsettled on the face of the statute.**

It was found by reading the code, it is visible in the state's own published text, and it appears
to have been reported nowhere.

**The honest framing, which must travel with it:** duplicate subchapter designations are a routine
artefact of a busy session and are usually cleaned up in the next non-substantive revision bill.
**The code currently carries a conflict. Nobody did anything wrong.** Worth checking whether a
later called session already fixed it.

---

## 7. JETI: seven elected trustees, thirty days, one hearing

Government Code Chapter 403 Subchapter T `[DOC]`. Three vetoes and one public hearing:

1. **Comptroller** recommends within **60 days**, and **may not** recommend unless it finds **"the
   agreement is a compelling factor in a competitive site selection determination and that, in the
   absence of the agreement, the applicant would not make the proposed investment in this state"**
   (403.609).
2. **Governor** must act **within 30 days** (403.610).
3. **School district** must decide **within 30 days**, and **"shall hold a public hearing on the
   application during the period"** (403.611), with Open Meetings Act notice **not later than the
   15th day before** carrying the applicant's name, the zone, a project description and the
   projected investment.

**That 15-day notice and that one hearing are the public's entire entry point into a multibillion
dollar abatement.**

All local incentive deals are published on the Comptroller's site **but are not categorized**, so a
searcher must already know the company name — which shell companies defeat `[REP]`. The Comptroller
has reported **147 projects** qualifying for a data center sales-tax exemption, many applied through
shell companies, and **how much any individual project forgoes is not public** `[REP]`.

---

## 8. The gap between the org chart and the outcome

**On August 3rd, 2026 the Governor ordered a pause on new data center approvals pending a state
audit, and ERCOT halted its Batch Zero study** `[REP]`. Bloomberg NEF estimated it could delay
49.8 GW and cost projects up to $15 billion.

**The Governor has no statutory power over ERCOT's interconnection queue.** He does not appoint its
directors. He acted by directive on a private nonprofit he does not control, and it worked.

**That gap between the org chart and the outcome is the single best illustration on this beat of
how Texas actually runs, and it is worth a deck by itself.**

---

## 9. Open assignments

The three **ERCOT Board Selection Committee** members; the **seven Texas AI Council** members and
chair (both blocked by the Governor's-site exclusion, so they need agency or journalism routes);
the **Senate 2026 interim charges**; the TCEQ and PUCT **executive directors' names**; **river
authority board appointment methods** (each in its enabling special law in the Special District
Local Laws Code, fetchable at `tcss.legis.texas.gov/resources/SD/htm/`); which **special-law
groundwater districts have appointed rather than elected boards**; and the **HB 2127 case citation**
from `search.txcourts.gov`.
