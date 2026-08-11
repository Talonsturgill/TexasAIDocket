# Texas Grid Watch — what it measures and what it refuses to say

Research completed 2026-08-11. This is the design record for the daily numeric energy
instrument. Wave 5 builds from this document.

Verification marks used throughout: **[V]** corroborated by two or more independent sources or
a primary document, **[1S]** single source, **[?]** could not confirm, **[CONFLICT]** sources
disagree.

---

## 1. The finding that decides the product

There is **no daily, dated, archived, machine-readable Texas energy record**. Not from ERCOT,
not EIA, not GridStatus, not any newsletter, and not from any vendor whose data a legislative
staffer is permitted to cite. The slot is empty.

Four things are true at once in August 2026, and they will not all be true in six months:

1. **ERCOT publicly disowned its own headline load forecast.** Its preliminary 2026-2032
   forecast (released April 15th, 2026) showed peak demand reaching ~367,790 MW by 2032 with
   ~228,420 MW of data-center load. ERCOT itself said it "has concerns with using the
   preliminary load forecast values for the Reliability Assessment." By late July the working
   figure had been revised down to roughly 175,000 MW. **[V]**
2. **The Governor paused the industry pending an audit.** On August 3rd, 2026 Abbott ordered an
   audit of every data center in the ERCOT queue. ERCOT suspended its Batch Zero classification
   notices. The audit's central question is *how much of this is real* — which is precisely what
   the headline metric below measures. **[V]**
3. **The Legislature chartered a committee to worry about exactly this number.** The Senate
   Business and Commerce 2026 interim charge includes "progress made toward increasing
   confidence in ERCOT load forecasts." **[V]**
4. **The best-resourced newsroom in Texas published, on August 10th and 11th, 2026, that the
   information does not exist.** The Texas Tribune ran "Why it's so hard to find information
   about Texas data centers" and had to buy two private commercial databases to approximate a
   map, because "the state does not publicly track data center development." **[V]**

## 2. The headline metric

**Large-load utilization ratio = observed large-load peak MW / MW approved to energize**

| As of | Approved to energize | Observed peak (non-simultaneous) | Ratio |
|---|---|---|---|
| March 2025 | 9,042 MW | 3,883 MW | 43.0% |
| June 2026 | ~8,927 MW | ~3,900 MW (3,675 MW simultaneous) | ~43.7% (41.2% simultaneous) |

Stated in a sentence: *Texas has approved about 8.9 GW of large load to energize, and has
watched about 4.0 GW of it actually draw power.*

**Why this number and not another:**
- It is **symmetrically inconvenient**. It refutes "474 GW of demand is coming" and it equally
  refutes "data centers are not using anything yet." Neither camp can weaponize it, which is
  exactly why both will cite it.
- Both numerator and denominator are **measured**, not modeled. They are things ERCOT counts.
- It carries a natural residual, the same shape the Alaska instrument publishes: roughly
  **5,000 MW approved and idle**.

Publish it as four lines, never one: measured large-load draw today, approved-to-energize with
its publication date visibly attached, the residual, and queue requests **labeled as
applications** with the historical conversion rate attached (the request-to-operating funnel
runs near 1.6% **[1S]**).

**Operational cost to accept, not to wish away:** the denominator lives in monthly ERCOT TAC
and board PowerPoint decks that **do not machine-extract cleanly** (both the March 2026 TAC
report and the April 2026 Senate committee deck returned binary). Budget for a monthly
human-in-the-loop denominator update with a visible `as_of` date. The numerator is daily.

## 3. The other twelve numbers nobody computes

Ranked by value to a reporter times nobody-else-does-it:

1. **ERCOT's own day-ahead load forecast error, scored daily and kept forever.** ERCOT
   publishes forecasts and actuals; nobody keeps a public calibration record. This is the
   credibility instrument for the entire load-forecast fight.
2. **Days since last EEA, days since last conservation appeal, days since last firm load shed.**
   Trivial to compute, emotionally enormous, and the honest non-verdict answer to "is the grid
   okay." It reports the past and promises nothing.
3. **Minimum PRC of the day, and MW of headroom above the EEA-1 threshold (2,300 MW).** A daily
   closest-approach figure. Far more informative than a reserve margin.
4. **Net-load peak vs gross-load peak, and the delta.** The gross peak gets headlined; the net
   peak is what actually stresses the system. In ERCOT as of 2026 the binding constraint is net
   load at sunset, not gross load.
5. **Battery contribution at the exact net-peak minute.** During Winter Storm Fern batteries hit
   over 7,000 MW, 9.5% of supply. Publishing this daily turns a series of one-off record
   stories into a trend.
6. **Evening ramp magnitude in MW/hr.** Roughly 30 GW of solar rolling off is the defining
   daily physical event in ERCOT now.
7. **Wind and solar forecast error**, same treatment as #1. Both sides misuse "renewables
   underperformed"; only a kept scorecard settles it.
8. **The generation residual**, Alaska-pattern: served load minus measured generation by fuel
   minus DC tie net flows. Non-zero equals losses plus behind-the-meter plus measurement error.
   Publishing it and refusing to explain it away is the honesty signature.
9. **Texas Energy Fund funnel:** MW awarded / under construction / commercial / withdrawn.
   Roughly one third of originally identified TEF projects have been cancelled or withdrawn
   **[1S, verify]**. Nobody publishes this as a running series.
10. **Large-load queue funnel with time-in-stage:** requested, screened, officer letter,
    executed IA, approved to energize, energized, metered.
11. **DC tie utilization** as a percentage of roughly 1,220 MW total tie capacity. Directly
    informative to the grid-isolation debate.
12. **Days since the last preliminary peak was revised**, with the revision magnitude. Nobody
    audits ERCOT's own restatements.

## 4. What the page refuses to say

The Alaska instrument's line is "this page will never tell you whether the lights stay on."
Texas needs a paired version, because since June 2026 the Texas grid argument is no longer
mainly about reliability. It is about **cost and fairness**.

> **This page will never tell you whether the grid will hold, and it will never tell you what a
> data center did to your bill. It publishes what was measured, what was approved, and the gap
> between them.**

And for the queue, where the worst reporting lives:

> **A request is not a project. A project is not a megawatt. This page counts megawatts that
> moved.**

**Standing rules:**
- Never publish a forecast. Publish other people's forecasts beside the measured outcome and
  keep score of both.
- **Never publish a reserve margin.** The CDR is a planning study with deliberately conservative
  inclusion criteria, not a forecast, and "negative reserve margin in 2028" is routinely
  misread as a blackout prediction. Publish minimum PRC and headroom-to-EEA1 instead, both
  measured.
- Never attribute causation from fuel mix. Fuel mix at a moment reflects dispatch order, outage
  state and fuel price.
- **Never estimate a number the state itself failed to collect.** On water: a voluntary PUCT
  survey drew 28 responses from 377 companies, and a mandatory TWDB survey got a 17%
  data-center response rate despite non-compliance being a Class C misdemeanor. Publish the
  response rate. That is a fact. An estimate would be a claim.
- When ERCOT revises, **show the diff**. Never quietly restate.
- The gauge is a bar and never a dial, no severity ramp, one hue at one intensity. Carried over
  from the Alaska rules in CLAUDE.md.

## 5. The caveat block that ships with every number

As structured metadata fields, not footnotes:

1. **Measurement basis** — instantaneous / 15-minute integrated / hourly average. ERCOT
   reported the July 22nd 2026 peak as 91,308 MW instantaneous; EIA reported 91.1 GW hourly
   integrated. Both correct, different constructs, and failing to say which invites an accusation
   of error from someone quoting the other.
2. **Vintage** — preliminary / revised / settled. Settlement-quality data is 60 days behind.
3. **Boundary** — ERCOT only, roughly 90% of Texas load. El Paso is in WECC. Parts of the
   Panhandle and East Texas are in SPP/MISO.
4. **Behind-the-meter treatment** — ERCOT-reported demand **excludes** behind-the-meter and
   self-serve load.
5. **DC tie treatment** — netted or excluded.
6. **Capacity basis** — nameplate / HSL / seasonal rating / ELCC-derated. These differ by tens
   of GW.
7. **Large-load stage** — six different numbers are all called "data center MW" in press
   coverage. Say which one.
8. **Weather normalization** — peak comparisons across years without it are near-meaningless.
   Say "unnormalized" every time.
9. **Simultaneity** — ERCOT reports large-load peaks both non-simultaneous and simultaneous.
   Publish both or say which.
10. **Source and retrieval timestamp**, including how stale the slowest input is.

## 6. The one that works against us, published anyway

**Off-grid and behind-the-meter data center load is invisible to ERCOT and growing fast.**
Vantage/VoltaGrid on San Antonio's West Side, Chevron's Energy Forge One in Reeves County
(a 2 GW gas plant serving a data center and not connecting to the public grid), and Fermi
America near Amarillo are all deliberately off-grid.

So the numerator is a **lower bound, and it is becoming a worse one**. That sentence belongs on
the page every day, in the same place, unprompted and against our own interest. It is worth
more than the metric.

## 7. Revision log as a moat

ERCOT's real-time telemetry is preliminary and it revises without changelogs. The options are
to publish preliminary at T+1 with a hard revision policy, or to publish nothing useful.

Choose the first, and make the revision log a **feature**. Every daily record carries a
`data_vintage` field (`preliminary` / `revised` / `settled`) and every restatement gets a dated,
diffable entry. A published revision log is a competitive moat precisely because an institution
with a reputation to protect will not build one.

## 8. What a reporter needs, in order

1. One stable URL with the same layout every day. Muscle memory, not a dashboard.
2. Yesterday's peak with its all-time rank, prior record, and date.
3. The utilization ratio and residual, with the denominator's publication date attached.
4. Days-since counters. Reporters currently have to email ERCOT for these.
5. **A maintained "what is not public" page.** The single strongest trust artifact available,
   and nearly free to ship.
6. CSV and JSON of every number plus full history, under a license permitting republication.
7. A permanent dated archive where `/2026-08-11` resolves forever, unchanged.
8. A methods page with the formula, the endpoint, the update time, and the revision policy.
9. Zero adjectives. No "alarming," no "reassuring," no "tight."
10. A calendar of dated decisions.

## 9. Dated decisions to track

| Date | What |
|---|---|
| 2026-08-20 | PUCT open meeting, 9:30am: ERCOT good-cause exception on Batch Zero timelines |
| 2026-12-31 | Statutory deadline for PUCT to amend rules under SB 6 (16 TAC §25.194) |
| 2026-12-31 | Target implementation, transmission cost recovery 4CP to 12CP (PUCT Project 58484) |
| 2026-12 | Next Capacity Demand and Reserves report (May 2026 was skipped by good-cause exception) |
| 2027-01-12 | 90th Legislature convenes |
| 2027-09-01 | First deposit to the Texas Water Fund under Proposition 4 |

## 10. The competitive read

**Doug Lewin (Texas Energy and Power) is not a competitor. He is the distribution channel and
the credibility test.** Two to three posts a week, deeply trusted by both PUCT staff and clean
energy advocates, and he publishes **no dataset, no CSV, no API, no recurring numeric series** —
he synthesizes other people's reports, and much of it sits behind a paywall. If he cites our
number once, we exist. So design the number so he *can*: free, permanent URL, stated method, and
a series he can point at rather than a chart he has to screenshot.

**GridStatus.io** is the closest thing to a real competitor and it is not close: multi-ISO,
reactive, and its excellent record analysis of the July 22nd peak published ten days after the
event. A daily instrument's whole value is that **it publishes on boring days**.

**ERCOT's own dashboards** are real-time but have no memory, no derivation and no narrative. The
large-load data, the most newsworthy series ERCOT holds, is published only as slides inside
monthly PDFs that do not machine-extract.

## 11. Sources and access, settled

Use the keyless dashboard JSON at `ercot.com/api/1/services/read/dashboards/*.json` plus
`ercot.com/content/cdr/html/real_time_system_conditions.html`. Verified 11 endpoints returning
200 on 2026-08-11, 60-second cache, no throttle observed at 8 rapid requests, and neither path
is disallowed by robots.txt.

**Never** build on `mis.ercot.com` (now SiteMinder-gated) or `api.ercot.com` (requires both an
Azure subscription key and an OAuth password grant, which is too fragile for unattended cron).

EIA-930 respondent `ERCO` is the independent crosscheck. The six-month CSV is keyless but 47 MB,
so reserve it for monthly work and get a free EIA API key for daily slices.
