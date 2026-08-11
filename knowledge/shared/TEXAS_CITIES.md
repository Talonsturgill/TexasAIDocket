# Texas metros — structure, utilities, and why per-city filtering is not optional

Research compiled 2026-08-11. Confidence marks: **[V]** verified against a fetched source that
day, **[K]** high-confidence but not re-verified, **[U]** unverified, do not publish without
checking.

The research pass exhausted its search budget partway through, so the data center, Flock/ALPR
and per-city AI policy sections are thinner than the rest. Those gaps are listed in section 8
as a verification queue, not presented as findings.

---

## 1. The finding that must be built in on day one

**Three cities in our coverage area are not on the ERCOT grid at all.**

| City | Interconnection | Utility | Retail choice |
|---|---|---|---|
| **El Paso** | **WECC** (Western Interconnection) | El Paso Electric, vertically integrated | No |
| **Amarillo** | **SPP** | Xcel / Southwestern Public Service, vertically integrated | No |
| **Beaumont and Port Arthur** | **MISO South** | Entergy Texas, vertically integrated | No |

That is roughly **1.5 million Texans** for whom an ERCOT conservation appeal, an ERCOT price
spike, or an ERCOT emergency alert is **factually irrelevant**. Far northeast Texas on SWEPCO is
SPP as well.

"The Texas grid" is really four grids. A publication that sends an ERCOT alert to an El Paso
reader has told them something untrue about their own city, and they will never trust it again.
**This belongs in the notification logic and the per-metro filter from the first line of code,
not as a later refinement.**

## 2. The utility table — the structure that explains who decides

Ownership type determines what a ratepayer can actually do, which is the most useful thing this
publication can explain repeatedly.

| City | Utility | Type | Who sets rates | Retail choice | ERCOT zone |
|---|---|---|---|---|---|
| Houston | CenterPoint Houston Electric | IOU, wires only | PUCT, city has original jurisdiction | Yes | LZ_HOUSTON / Coast |
| Dallas, Fort Worth, Waco, Tyler, Killeen, Midland, Odessa | Oncor | IOU, wires only | PUCT, city original jurisdiction | Yes | LZ_NORTH or LZ_WEST |
| **San Antonio** | **CPS Energy** | **Municipal** | **5-member board, mayor sits ex officio; Council confirms and approves rates** | No | LZ_CPS |
| **Austin** | **Austin Energy** | **Municipal** | **City Council IS the governing body** | No | LZ_AEN |
| **El Paso** | **El Paso Electric** | **IOU, vertically integrated** | **City Council adjudicates first**, then PUCT; NMPRC in New Mexico; FERC wholesale | No | **not in ERCOT** |
| Corpus Christi, McAllen, Laredo, Abilene | AEP Texas | IOU, wires only | PUCT | Yes | LZ_SOUTH or LZ_WEST |
| **Lubbock** | **Lubbock Power and Light** | **Municipal** | LP&L board and Council | partial **[U]** | migrated SPP to ERCOT **[K]** |
| **Brownsville** | **Brownsville PUB** | **Municipal**, since 1907 | PUB board and City Commission | No | LZ_SOUTH |
| **College Station and Bryan** | CSU and BTU | **Two adjacent municipals** | Council / BTU board | No | ERCOT |
| Amarillo | Xcel / SPS | IOU, vertically integrated | PUCT, FERC | No | **not in ERCOT** |
| Beaumont, Port Arthur | Entergy Texas | IOU, vertically integrated | PUCT, FERC | No | **not in ERCOT** |

Load zone and weather zone cells are **[U]** — the research could not reach an authoritative
ERCOT zone definition. Verify every one before publishing.

### The four-way comparison worth reusing forever

*"My bill went up. Who do I call?"* has four completely different answers in one state:

- **San Antonio** — the mayor you elected sits on the utility board, and the council you elected
  confirms its trustees.
- **Austin** — the council you elected **is** the utility board.
- **El Paso** — your city council adjudicates the rate case before the state ever sees it.
- **Houston or Dallas** — you file at the PUCT in Austin, before five commissioners appointed by
  the Governor.

Chart it once and it explains a hundred stories.

### Municipal utilities are also tax collectors
CPS Energy sends roughly **$500 million a year to San Antonio's general fund [V]**, about a
quarter of it. Austin Energy likewise returns profits to the city **[V]**. That is a structural
argument that municipal utilities are under-capitalized *because* they double as revenue, and it
is a serious original piece with public numbers behind it.

### The comparison that kills a lazy framing
**Austin Energy** (municipal) failed badly in the **February 1st, 2023 ice storm [V]**.
**CenterPoint** (investor-owned, retail choice) failed badly in **Hurricane Beryl, July 8th,
2024 — 2.2 million customers, the largest outage in Texas history [V]**. Both were
distribution-side failures driven by vegetation management and hardening decisions. Ownership
did not determine the outcome. Anyone arguing public-good-versus-private-bad from Texas
reliability data is arguing past the evidence.

## 3. City government structure

**Houston is the only strong-mayor big city in Texas.** The mayor is the executive officer, runs
the city, presides over Council **and votes [V]**. Everywhere else of size is council-manager,
where an appointed city manager is the chief executive.

Reporting consequence: **in Houston "the city decided" means the mayor decided. In Dallas or San
Antonio it means the city manager proposed and the council ratified.** That single difference
should shape the verb in every city story.

Notable: Dallas has a **Republican mayor** (Eric Johnson, switched parties 2023), the largest US
city with one. Amarillo has just **five at-large commissioners on two-year terms**, the smallest
and most at-large body on the list, which makes it unusually easy for one organized faction to
take the whole council.

**Machine-readable municipal data:** most large Texas cities run **Granicus Legistar**, which
exposes a documented REST API at `https://webapi.legistar.com/v1/{client}/` covering events,
agenda items, matters, attachments and persons. Dallas is confirmed at `cityofdallas.legistar.com`
**[V]**. **One Legistar poller would give agendas, ordinance text and votes for most of Tier 1
without scraping HTML.** Client slugs for the others are **[U]**.

## 4. Preemption — why city politics and state politics collide

Texas cities are home rule: they may do anything state law does not forbid. Since roughly 2015
the Legislature's answer has been to forbid more.

- **HB 40 (2015)** — passed after Denton banned hydraulic fracturing by referendum, preempting
  local oil and gas regulation statewide. The template for everything after.
- **HB 2127 (2023), the "Death Star" law** — *field* preemption rather than ordinance-by-ordinance.
  Forbids local regulation in any field covered by eight state codes unless expressly authorized,
  and creates a private right of action so anyone "adversely affected" can sue a city. Signed
  June 14th, 2023, effective September 1st, 2023 **[V]**. A Travis County judge ruled it
  unconstitutional the day before it took effect; the State's appeal superseded the judgment, so
  it has been in force throughout. **Current posture [U] — check the Fifteenth Court of Appeals
  and Texas Supreme Court dockets before writing about it.**
- **SB 2038 (2023)** — lets landowners unilaterally release themselves from a city's
  extraterritorial jurisdiction. Quietly one of the most consequential for our beat, because it
  strips growing cities of regulatory reach over their fringe, **which is exactly where data
  centers and large industrial loads want to site.**
- **TRAIGA (HB 149)**, effective January 1st, 2026, is understood to **preempt local AI
  regulation [U — verify the exact clause]**. If that reading holds, the whole "which cities have
  AI policies" question changed on that date: a city can still set an internal procurement and
  use policy for its own employees, but likely cannot regulate AI within its borders. **Get a
  lawyer's read before publishing this.**

**The governance twist that matters most:** the largest projects are landing in **unincorporated
county territory**, where there is no city council, no home rule and no ordinance authority —
only a county judge and four commissioners. So the per-city product needs a **per-county
dimension** to cover the biggest stories at all.

## 5. Abilene is the signature beat

Population **131,588**, five-year growth +5.1%. Largest employers are Dyess Air Force Base
(8,864) and Hendrick Health (2,896) **[V]**. Three Christian universities. Local press capacity:
a Gannett daily behind a paywall and a university public radio station.

And **the Stargate campus is operating there at about 1.2 GW with more than 6,400 workers on
site**, developed by a Blue Owl / Crusoe / Primary Digital joint venture, leased to Oracle, with
a $2.3 billion JPMorgan loan **[V]**.

A 1.2 GW campus in a semi-arid West Texas city of 131,000 is a **water and workforce story before
it is a chip story**, and the mismatch between the size of the story and the local media capacity
to cover it is precisely the gap this publication exists to fill.

## 6. Water is the binding constraint, not power

For most of these cities the AI story is a water story wearing an electricity costume.

Lubbock and Amarillo sit on the **Ogallala**. San Antonio's **Edwards Aquifer** is legally capped
by pumping regulation and federal endangered-species litigation, so its water is constrained in a
way Houston's is not. El Paso leads the nation in reuse and inland desalination. Corpus Christi
is fighting over seawater desalination against local opposition. The Valley is short on **treaty
water from Mexico** under the 1944 agreement, which has already destroyed its sugar industry.
Austin's supply comes from the Highland Lakes, controlled by **LCRA — an entity Austin voters do
not elect**.

## 7. Structural facts worth keeping

- **Fort Worth is now larger than Austin.** Both crossed one million in the 2025 estimates
  **[V]**. Fort Worth grew 11.9% since 2020, the fastest of the big cities.
- **The shrinking cities are all Gulf Coast petrochemical towns**: Beaumont −2.0%, Port Arthur
  −0.4%, Corpus Christi −0.2% **[V]**. Their industrial output and capital investment are rising
  while their populations fall, because refining and LNG are capital-intensive rather than
  labor-intensive, and repeated hurricanes have driven residential out-migration.
- **The real growth is suburban**: Georgetown +59%, New Braunfels +36%, Conroe +33%, Denton +21%,
  McKinney +21%, Temple +20% **[V]**. Several of these are **municipal-utility cities**, so the
  fastest-growing places in Texas are disproportionately places where the city council sets the
  electric rate.
- **Extreme single-employer exposure**: Killeen (Fort Cavazos, 32,000), College Station (Texas
  A&M System, 16,248), Laredo (over 47% of all US trade headed to Mexico crosses there), Port
  Arthur (Motiva, the second-largest US refinery at 600,000 bpd), Midland and Odessa (the WTI
  price) **[V]**.
- **The Valley thinks regionally.** McAllen–Edinburg–Mission is the **fifth-largest metro in
  Texas** at 921,549, and with Brownsville–Harlingen the Valley is about 1.36 million **[V]**.
  It needs a single "the Valley" filter as well as per-city ones.
- **Houston Landing shut down in 2025 [K]** — do not list it as an active outlet.

## 8. Verification queue, ordered by how badly it is needed

1. **ERCOT load zone and weather zone for every city.** Every such cell above is unverified.
2. **Data center projects, operators and MW by county**, from ERCOT Large Load Working Group
   materials and the interconnection queue, plus Oncor, CenterPoint and AEP large-load totals.
3. **Fermi America near Amarillo** — potentially the largest project in the state, and if real it
   is being built on **SPP, not ERCOT**, a distinction almost nobody is covering.
4. **Flock and ALPR contract status city by city**, via EFF's Atlas of Surveillance filtered to
   Texas plus Legistar searches for "Flock" in contract agenda items. Verified anchors already
   exist: Austin cancelled its program, Fort Worth's crime statistics claims are disputed, and a
   Johnson County agency queried 83,000 cameras nationwide in a 2025 abortion investigation
   **[V]**. High-differentiation beat, genuinely under-covered.
5. **Per-city AI use and procurement policies**, and whether TRAIGA preempted the field.
6. **HB 2127 litigation posture.**
7. **Mayoral term end dates** for Fort Worth, El Paso, San Antonio and all of Tier 2, plus Waco's
   current mayor.
8. **Median household income for all 21 cities** — only Dallas ($54,747, 2020) and San Antonio
   ($53,571, 2019) were verifiable, both stale. One pass over Census QuickFacts closes it.
9. **Lubbock Power and Light's ERCOT migration completion and retail-choice status.**
10. **El Paso Electric's WECC membership and any Western EIM or EDAM participation.**
11. **RSS availability** across every outlet domain, by automated probe.
12. **Legistar client slugs** for Austin, San Antonio, El Paso, Fort Worth and Houston.
