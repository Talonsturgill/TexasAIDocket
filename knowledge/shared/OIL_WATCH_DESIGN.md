# Texas Oil Watch — what it measures, and why it is weekly

Research completed 2026-08-11. Every data-source claim below was tested live over HTTP on that
date. Verification marks: **[V]** verified against a primary source, **[1S]** single source,
**[?]** could not confirm.

---

## 1. The honest cadence finding, first

**Oil is a weekly instrument with a daily price ticker. It is not a daily instrument.**

The grid has five-minute SCADA. Oil has a Wednesday report. The keyless EIA bulk file was
**five days stale** when tested (queried 2026-08-11, last modified 2026-08-06, newest daily WTI
observation 2026-08-03). Daily freshness requires the free EIA API key.

| Layer | Cadence | Lag |
|---|---|---|
| WTI, Brent, Henry Hub spot | daily, weekdays | 1 to 2 days (5+ on keyless bulk) |
| Weekly Petroleum Status Report | Wednesdays after 10:30am | ~4 days |
| Baker Hughes rig count | Fridays | same day |
| Texas state production | monthly | **~2.5 months** |
| Texas flaring | **annual** | **~19 months** |

If the product promises symmetry with the grid instrument it will under-deliver. Name the
asymmetry in the methodology rather than papering over it.

## 2. The headline number

> **Texas holds 72.6% of America's Strategic Petroleum Reserve. Since August 2025 that reserve
> has fallen 98 million barrels, about 24%, and most of it is lent, not sold.**

It is measured, it is Texan, and it defuses its own panic in the same breath.

**Per-site inventory, DOE, as of 2026-06-25 [V]:**

| Site | State | MMbbl |
|---|---|---|
| **Bryan Mound** | **Texas** | **155.4** |
| **Big Hill** | **Texas** | **89.1** |
| West Hackberry | Louisiana | 53.1 |
| Bayou Choctaw | Louisiana | 39.2 |
| Total | | 336.8 |

Texas = 244.5 of 336.8 = **72.6%**. Authorized capacity is 714 MMbbl.

**Weekly aggregate [V]**, EIA series `PET.WCSSTUS1.W`: 304,809 thousand bbl at 2026-07-31,
against 402,976 a year earlier. Five-week average draw about 4.17 MMbbl/week.

**The correction that must travel with it:** the 2026 decline is mostly an **exchange**, not a
liquidation. DOE ran a 172 MMbbl exchange program as part of an IEA collective release of 400
MMbbl, with borrowers returning oil late 2026 to 2029 **with an 18 to 24% premium in kind**.
An instrument showing the SPR falling without the contracted repayment schedule is publishing a
scare.

**Fragility to disclose:** per-site inventory is **HTML only**, on an unversioned DOE page,
updated irregularly. It was already about six weeks stale when read. Build the staleness flag
before building the headline.

## 3. The Iran shock was real, and EIA says so

This is the rare case where the alarming version is the true one. EIA *Today in Energy*
(id=67865) confirms **[V]**:

- Actual disruption to crude and product flows **through the Strait of Hormuz in Q2 2026**,
  with Middle Eastern countries shutting in production
- Brent **high $118/bbl on April 29th, 2026**; **low $72/bbl on June 26th, 2026**
- Average daily Brent swings of **$4/bbl in Q2 2026 against $1/bbl in 2025**
- **June 17th, 2026:** a US-Iran memorandum of understanding seeking to resume Strait traffic
- Estimated **5.1 million b/d** global crude inventory decline in Q2

**Unresolved and must be stated as such [?]:** whether the Strait was ever *fully* closed or
only severely restricted. Sources conflict. **Do not publish "$126 oil"** — that figure appears
in secondary sources and conflicts with EIA's $118. Use EIA's number and date.

**Also flag:** a naive search surfaces "EIA forecasts oil to average $51.26 in 2026." That is an
obsolete pre-war STEO figure, now wrong by roughly 60%, and it will contaminate research.

## 4. Two computable Texas numbers nobody publishes

### The Texas Discount
Brent minus WTI Cushing is running **$5 to $11** against a normal $3 to $5. A Hormuz disruption
prices *waterborne* crude, and WTI is landlocked at Cushing, so **Texas crude is not capturing
the full crisis premium.**

At 2026-08-03 **[V]**: WTI $81.96, Brent $88.90, spread $6.94.

Framed for the reader who actually cares:
> Brent is $88.90. WTI is $81.96. Texas crude is selling about $6.94 under the world price, and
> Midland gets less than that. We can't tell you how much less. That number is paywalled.

That last sentence is the product.

### Texas is flat while New Mexico grows
From `PET.MCRFPTX2.M` and `PET.MCRFPNM2.M` **[V]**:

| Month | Texas kb/d | New Mexico kb/d | TX share of TX+NM |
|---|---|---|---|
| 2026-02 | 5,814 | 2,303 | 71.6% |
| 2026-05 | 5,802 | 2,394 | 70.8% |

**Through the largest oil price shock since 2022, Texas crude production did not grow. New
Mexico's did.** Free, monthly, two series, and nobody publishes it as a Texas-framed metric.

Caveat: four months is short and monthly EIA state data is revised. Publish as a tracked series
with revision history, never as a trend claim.

### The announced-versus-measured gap
Rig counts fell (Permian 242 in late January 2026, down 20.1% year over year), operators
*announced* rig additions after the price spike, and **measured Texas barrels did neither**.
Drilling permits sat flat near 750/month all year. Texas responded with words faster than
barrels, and that gap is itself an instrument.

## 5. What ships weekly

**Daily** (free EIA API key; always stamp the observation date, never today's date):
`PET.RWTC.D` WTI Cushing · `PET.RBRTE.D` Brent · `NG.RNGWHHD.D` Henry Hub · derived **Texas
Discount** with a trailing five-year mean as the modeled reference and the gap as the residual.

**Weekly**, from the keyless `https://ir.eia.gov/wpsr/table1.csv`:
SPR total and **Texas share** (with staleness flag) · commercial crude ex-SPR ·
**Gulf Coast PADD 3 refinery utilization** (97.3%, the most Texas-proximate weekly measured
value that exists) · PADD 3 refiner net crude input · US crude exports · US crude production.

**Monthly:** Texas crude and Texas share of TX+NM · Texas marketed gas · RRC drilling permits
and completions · Comptroller severance tax against the pre-war estimate.

## 6. The "not public" list

- **WTI Midland differential** (Argus, paid). Now in the Brent basket, so firmly paywalled.
- **Waha hub gas price** (NGI/Platts, paid) — *the most important missing Texas number*.
  Secondary reporting **[1S, unverified]** says Waha averaged negative on 118 of the first 131
  flow days of 2026, hitting −$9.52/MMBtu on April 16th. If true it is the most extraordinary
  energy price in America: Permian producers paying to dispose of gas while data centers next
  door hunt for fuel. **Publish the story, cite the source, never republish the number.**
- **Well-level production faster than monthly** (Enverus, paid)
- **Flare-gas-to-compute volumes** — does not exist anywhere, publicly or privately audited
- **Per-site SPR in machine-readable form** — HTML only
- **Monthly Texas flaring** — the EIA series exists and returns null for every 2026 month
- **Deliverable versus nominal SPR inventory** — secondary reporting claims over 25% of
  inventory is undeliverable due to cavern outages **[?]**. Worth pursuing, do not publish.

**A staleness clock is itself a publishable number:** days since the last official Texas flaring
figure. Currently about 19 months, while satellites see flares nightly.

## 7. Flaring got worse, and the record is stale

`NG.N9040TX2.A` **[V]**: 99,698 MMcf (2022) → 156,021 (2023) → 163,512 (2024). **Up about 64% in
two years.** The improvement narrative is out of date. The monthly series returns null for 2026,
so the latest usable official figure is annual and 19 months old, while NOAA VIIRS and the Earth
Observation Group at Colorado School of Mines observe flares nightly. Note that EOG is moving to
a new calibration in 2026 which will break comparability with prior years.

## 8. The AI thread — announcements, not operations

The strongest intersection in Texas energy, and it is almost entirely **pre-operational**:

- **Chevron "Project Kilby"** — subsidiary Energy Forge One LLC, a **20-year PPA with Microsoft**
  for a co-located **2.67 GW** gas plant in **Reeves County**. Announced about June 22nd, 2026,
  with an **SEC 8-K dated 2026-06-30** **[V]**. FID expected end-2026, **first power 2028**.
- **Crusoe and Lancium** — $3.4B JV, **1.0 GW** campus in **Childress**, announced July 7th, 2026.
  Crusoe added 4.5 GW of gas and expanded Abilene to 1.2 GW.
- **FO Permian Partners** — over 5 GW off-grid gas across 3,200 acres in Midland County.
- **Pacifico "GW Ranch"** — 7.65 GW gas-and-data-center complex, reportedly the largest US air
  permit ever issued **[?, verify with TCEQ before republishing the superlative]**.

**The inversion worth reporting:** SLB and Baker Hughes are no longer only selling AI *into*
oilfields. They are selling oilfield power expertise *into* AI data centers. SLB's Data Center
Solutions is tracking to a $1B quarterly run rate exiting 2026.

**The regulatory finding is an absence:** no RRC decision was found specifically about powering
data centers with oilfield gas. The action is **TCEQ air permits** and PUCT/ERCOT interconnection.
Behind-the-meter Permian compute is being built largely outside the oil regulator's remit, and
that split is why nobody has a single tracker.

**Therefore the honest instrument line, held at zero until it moves:**
> **Measured operating AI load on Permian gas: 0 MW.**

Held at zero for two years and then moved, that would be the most credible thing the project
publishes.

## 9. What it refuses to say

1. **No price forecasts.** No targets, no "analysts expect," no futures curve as prophecy.
2. **No "days until the SPR is empty."** It computes to about 73 weeks at the recent draw rate,
   which is arithmetically trivial, emotionally explosive and analytically worthless, because
   the draw is an exchange with contracted returns. **Publish the repayment schedule instead.**
3. **No "peak Permian" declaration.** Four flat months is not a peak. Publish the series and let
   it argue.
4. **No attributing earthquakes to named operators.** Publish RRC seismic response area
   boundaries, injection limits and dates. Never causation.
5. **No jobs forecasts for Midland or Odessa.** A projected layoff number in a one-industry town
   is a self-fulfilling harm. Publish BLS actuals with the lag disclosed.
6. **No war forecasting.** Report what happened, dated.
7. **No unaudited flare-gas-compute figures.** A company claim is published as a company claim,
   attributed, never as a measurement.
8. **No pretending daily means fresh.** If the value is from the 3rd and today is the 11th, the
   page says the 3rd. Given the measured five-day bulk staleness this will happen regularly, so
   handle it in the schema, not the prose.

## 10. Legal risk to settle before shipping

**Baker Hughes rig count.** The landing page carries **no terms of use, copyright notice, or
republication license**. Absence of a license is not permission, and Baker Hughes has
historically asserted ownership of the rig count. Republishing it under CC BY 4.0 is the
clearest legal exposure in the plan.

Three options: get written permission (`OilfieldKnowledgeCenter2@bakerhughes.com`), cite and
link without redistributing values, or omit rig count entirely. **Until settled, do not publish
rig counts.**

Also note the weekly file is served from a `/static-files/<GUID>` path where the GUID changes
each week, so the landing page must be scraped every Friday to find it.

## 11. What not to build in v1

**Texas Railroad Commission bulk ingestion.** Most RRC production data is **EBCDIC**, IBM
mainframe encoding, released monthly around the 20th to 27th, with RRC stating outright that
conversion is the user's problem. The online queries are ASP.NET and Struts forms with no
export. Decoding it is a multi-week engineering project with ongoing breakage risk, for data
that is monthly and late.

Use the **RRC monthly drilling permit press releases** instead. They are the practical fast RRC
number, and they already tell the story: permits flat near 750/month through a price shock.
