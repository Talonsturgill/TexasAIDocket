#!/usr/bin/env python3
"""site_build.py — the published site, generated from the ledgers.

THE READER THIS IS BUILT FOR

Someone busy and sceptical, often on a phone, sometimes sitting in a county commissioners
meeting. They have one question the rest of the internet does not answer for them:

    Is anything being decided near me, and can I still say something about it?

So the site answers that first, above everything else, computed fresh on every build. Everything
after it exists to make the answer checkable.

THREE RULES THIS FILE OBEYS

  1 docs/ IS A PURE FUNCTION OF THE LEDGERS. Nothing here reads the previous build, and no page
    is ever hand-edited. `site_fresh_check.py` proves it by rebuilding into a temp directory and
    requiring byte equality. That is what makes it structurally impossible for a bad run to
    corrupt the live site: the worst case is a stale build, never a broken one.
  2 EVERY NUMERAL IS COMPUTED. Counts come from `len()`, days come from date arithmetic. No
    figure is typed here, and `docket_build`'s gates already refused any that were typed into
    the record.
  3 NOTHING IS CLAIMED THAT THE RECORD DOES NOT HOLD. Where the record is thin the page says so
    and publishes the size of the gap. An empty docket draws an empty map.

    site_build.py --out docs
    site_build.py --self-test
"""
from __future__ import annotations

# This module remains the compatibility façade and the one build orchestrator. Shared page
# chrome and write-time gates live in site_context; renderer bodies live by page family. The
# wildcard imports are deliberate here only: schema checks and maintenance scripts historically
# import renderer helpers from site_build, so the façade re-exports that stable surface.
from site_context import *
from site_pages.watch import *
from site_pages.docket import *
from site_pages.feeds import *
from site_pages.editorial import *
from site_pages.datacenters import *

def build(out: Path, today: str) -> dict:
    items = dk.load(LEDGER)
    runs = load_runs()
    # blocking_only: a stale record still rebuilds, loudly. See NON_BLOCKING_FOR_BUILD in
    # docket_build. Refusing to rebuild because the input is old leaves the reader with an
    # even older page, which is the wrong party paying for the run's debt.
    bad, results = dk.run_gates(items, today, blocking_only=True)
    stale = [r for r in results if r.name in dk.NON_BLOCKING_FOR_BUILD and r.status == "FAIL"]
    if bad:
        dk.report(results)
        raise SystemExit("site_build: the record does not pass its own gates; refusing to build")
    if stale:
        dk.report(results)
        print("site_build: BUILDING ANYWAY, but the record is stale and `--validate` will fail. "
              "Re-verify the items named above. This is a debt, not a pass.")

    # THE ONE FILE THIS BUILD DOES NOT OWN AND MUST NOT DESTROY.
    #
    # `ownership.yaml` says of `docs/videos/videos.json`: "No build in this repo may write,
    # reformat, or delete it, and site_build copies it through verbatim." It did not copy it
    # through. The wipe below removes everything not in this build's manifest, and the feed is
    # written by the publish step in `TexasAIDispatch` rather than produced here, so an in-place
    # rebuild deleted the sibling repo's only artifact in this repo.
    #
    # Worse, and this is why it went unnoticed: `video_feed()` reads the file from the repo root,
    # so after the wipe a rebuild counted ZERO videos and wrote an index that disagreed with the
    # feed still sitting in git. `site_fresh_check` cannot see any of it, because it builds into
    # a temp directory where the deletion never touches the real file.
    #
    # Found on 2026-08-19, when the first Dispatch feed entry was published and CI went red on a
    # single stat tile. Carried through here, byte for byte, exactly as the ownership note says.
    carried: dict[Path, bytes] = {}
    for rel in CARRY_THROUGH:
        src = out / rel
        if src.is_file():
            carried[rel] = src.read_bytes()

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    for rel, blob in carried.items():
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)

    # THE NUMERAL GATE, OVER EVERY PAGE. The authorised set is assembled from the projection
    # rather than declared, so a page is entitled to exactly what the build worked out and
    # nothing else. BuildContext keeps that scope unchanged across extracted page families.
    authorised = _authorised_numerals(items, today)
    by_item = {it["id"]: _item_numerals(it, today) for it in items}
    context = BuildContext(out=out, today=today, items=items, runs=runs,
                           authorised=authorised, by_item=by_item)
    written = context.written
    unauthorised = context.unauthorised
    broken = context.broken
    connect_seen = context.connect_seen
    pages = context.pages
    w = context.write
    listed = context.listed

    w("site.css", theme.css())
    # THE THREE SERIES GO OUT FIRST, BEFORE ANY PAGE IS RENDERED, and the order is load
    # bearing rather than tidy.
    #
    # They used to be written down among the pages that publish them, which reads well and
    # was wrong. The build wipes the out directory and starts empty, so for most of a run
    # these files do not exist. Anything rendered before them that wanted a reading got
    # nothing, silently, and the two places that do are both in the ask box.
    #
    # The pack escaped it by being written near the end, after the grid and the water but
    # BEFORE the weather, so it has been shipping with no weather in it since the day the
    # weather was added and no gate could see that. The ask box's citation map did not
    # escape it, and shipped covering two of its four families.
    #
    # Nothing here needs a page. Each one is a ledger read and a json dump, so there is no
    # reason beyond habit for them to run late, and running first means every reader of them
    # downstream reads THIS build's own output rather than whatever the last build left.
    # The grid watch as open data, in the same shape the page was built from. A reader who
    # doubts a figure here can recompute it without refetching anything from ERCOT.
    w("gridwatch.json", json.dumps(
        {"_spec": {"version": dk.SPEC_VERSION, "generated": today,
                   "note": "One settled ERCOT day per record. Hourly series included so every "
                           "published figure is recomputable. Unverified days carry no "
                           "numbers rather than yesterday's."},
         "readings": gridwatch_page.load()}, indent=2, ensure_ascii=False) + "\n")
    w("waterwatch.json", json.dumps(
        {"_spec": {"version": dk.SPEC_VERSION, "generated": today,
                   "note": "One day per record, per reservoir, so every roll up is "
                           "recomputable. Out of state reservoirs and flood control dams with "
                           "no conservation pool are excluded, and both exclusions are named "
                           "in each record."},
         "readings": waterwatch_page.load()}, indent=2, ensure_ascii=False) + "\n")
    # The heat clock as open data, on the same terms as the other two series. It has no page
    # of its own, because it is one line at the top of the front page rather than a subject,
    # so the data page is where a reader finds it.
    w("weather.json", json.dumps(
        {"_spec": {"version": dk.SPEC_VERSION, "generated": today,
                   "note": "Observed daily maximum and minimum at one anchor station, from "
                           "NCEI daily summaries. A day with no observation is absent rather "
                           "than zero. Normals are the 1991 to 2020 period computed from the "
                           "same record and shipped beside it."},
         "normals": frontchip.normals(),
         "readings": frontchip.load()}, indent=2, ensure_ascii=False) + "\n")

    # SERVED TO THE ONE PAGE THAT HAS A CALENDAR. See theme.record_css for why it is not in
    # the sheet every other page waits on.
    w("record.css", theme.record_css())
    w("facility.css", theme.facility_css())

    # THE CUSTOM DOMAIN, told to GitHub Pages. Derived from SITE_URL rather than typed, so the
    # domain the pages claim as canonical and the domain Pages actually serves cannot disagree.
    #
    # It has to be IN THE ARTIFACT, not only in the repository's Pages settings. This site
    # deploys through Actions, and an Actions deploy publishes exactly what the artifact
    # contains: a custom domain set in settings but missing from the upload gets dropped on the
    # next deploy, and the site silently reverts to the github.io hostname.
    (out / "CNAME").write_text(SITE_URL.split("//", 1)[1].rstrip("/") + "\n", encoding="utf-8")
    written.append("CNAME")

    # THE FILM GRAIN, as its own asset. It used to be a 12 KB base64 data URI inside site.css,
    # which is close to incompressible and sat in the middle of a render blocking download, so a
    # decorative texture was delaying first paint on every page. Written from the generator rather
    # than copied, because it is computed from three named constants and is byte-deterministic.
    (out / theme.GRAIN_FILE).write_bytes(grain.png())
    written.append(theme.GRAIN_FILE)

    # THE TAB ICON. Every page declares it, and `favicon.ico` also sits at the site root for the
    # request a browser makes on its own before it has parsed any markup. Generated from the same
    # statute as the wordmark rather than committed as a binary, for grain.py's reason: an icon
    # that can go missing without throwing puts the generic globe back on a green build.
    # THE SOCIAL CARD. Absolute url in the tags, so a scraper resolving against its own base
    # cannot miss it, which is the most common way a card silently fails.
    # THE INDEXNOW OWNERSHIP FILE. Served at the site root, containing the key and nothing
    # else. Without it every submission fails verification, so it is written by the build
    # rather than committed by hand and hoped for.
    w(indexnow.KEY_FILE, indexnow.key_file_contents())

    for name, blob in og.files(items, runs).items():
        # The per-decision cards live in their own directory, which has to exist first. The
        # site card sits at the root beside the favicon.
        (out / name).parent.mkdir(parents=True, exist_ok=True)
        (out / name).write_bytes(blob)
        written.append(name)

    for name, blob in favicon.files().items():
        (out / name).write_bytes(blob)
        written.append(name)

    # THE TYPE. Copied verbatim from the committed subsets rather than generated here: the
    # byte-equal rebuild guarantee cannot depend on a compression library's version, and a copy
    # is deterministic where a subsetting run is not. See scripts/site/fonts_build.py, which
    # exists because brand.yaml named three faces, the stylesheet wrote them into every font
    # stack, and nothing served them, so every reader got Georgia and system-ui instead.
    (out / "fonts").mkdir(parents=True, exist_ok=True)
    for face in fonts_build.manifest()["faces"]:
        shutil.copyfile(fonts_build.WEB / face["file"], out / "fonts" / face["file"])
        written.append(f'fonts/{face["file"]}')
    # The licence ships beside the fonts, because the repository is public and all three faces
    # are redistributed under the Open Font License.
    shutil.copyfile(fonts_build.WEB / "OFL.txt", out / "fonts" / "OFL.txt")
    written.append("fonts/OFL.txt")

    w("index.html", home(items, today),
      _home_numerals(items, today) | listed(items) | covers_section(items, today)[0]
      | (_run_numerals(runs[0]) if runs else set()))
    # THE RECORD IS NOT PUBLISHED AS A FILE, on the owner's call. `docket.json` was the whole
    # docket as one parseable download under CC BY, which is the single most expensive thing
    # this project makes handed over in one fetch. The record is still READ here, item by item,
    # with every claim and every source. What is gone is the bulk import.
    #
    # The instrument series stay open. They are derived from ERCOT, USGS and NOAA, anyone can
    # rebuild them from the same public sources, and they are what backs the promise that a
    # figure on this site can be recomputed rather than taken on trust.
    for it in items:
        w(f'item/{it["id"]}/index.html', item_page(it, today), by_item[it["id"]])
        # The Markdown twin. A crawler that fetches this gets the record without parsing HTML,
        # and a model quoting from it is far less likely to mangle a figure.
        w(f'item/{it["id"]}/index.md', item_markdown(it, today))
    w("atom.xml", atom(items, today))
    w("feed.json", feed_json(items, today))
    # THE TWO HUBS. Views over the record, never doorway pages: every sentence on them is
    # computed from the ledger, and the questions page shares `schema.qa_pairs` with the
    # structured data so the page and the JSON-LD cannot say different things.
    _quoted = _quoted_numerals(items)
    _allnums = (set().union(*(schema.authorised_numerals(i, today) for i in items))
                if items else set())
    _qfig, _qhtml = questions_hub(items, today)
    w("questions/index.html", _qhtml, extra=_allnums | _quoted | _qfig)
    # ONE PAGE PER KIND OF QUESTION. The hub above walks the same map, and `questions_check`
    # fails the build if the map and the frames disagree either way, so a kind cannot be
    # answered on the site without being linked from the hub or listed without existing.
    for _kind in schema.QUESTION_KINDS:
        _kfig, _khtml = questions_kind_page(items, today, _kind)
        w(f"questions/{_kind[1]}/index.html", _khtml, extra=_allnums | _quoted | _kfig)
    _sfig, _shtml = sources_page(items, today)
    w("sources/index.html", _shtml, extra=_quoted | _sfig)
    # ONE PAGE PER PUBLISHER, written straight after the hub that ranks them, so the family
    # reads as a family here the way the beats and the question kinds do. Each one lands in
    # the sitemap by being an index.html, which is the rule the loop at the end of this build
    # already applies to every other page.
    for _sslug, _ssfig, _sshtml in source_pages(items, today):
        w(f"sources/{_sslug}/index.html", _sshtml, extra=_quoted | _ssfig)
    w("llms.txt", llms_txt(items, today))

    # THE BUILD STAMP, WHOSE ONLY JOB IS TO BE PROBED.
    #
    # livecheck asks two questions of the live site. Does it answer at all, and is what it
    # serves as new as what this repository holds. It asked both of `docket.json`, a file
    # published for an entirely unrelated reason, and on 2026-08-23 that reason ended and the
    # file came down. livecheck then reported THE SITE IS DARK every four hours against a site
    # that was perfectly healthy, and worse, the half of it that answers "has the deploy
    # landed" is exactly the alarm that would have caught the outage that started the next day.
    # The watchman was watching a door that had been bricked up.
    #
    # So the probe gets a target that exists for no other purpose and can never be removed as a
    # side effect of a decision about something else. Three integers and a date. It carries no
    # part of the record, only its size, which every listing page states anyway.
    w("status.json", json.dumps(
        {"built": today, "items": len(items), "spec": dk.SPEC_VERSION}, indent=2) + "\n")
    # THE WHOLE RECORD IN ONE FETCH, built from the same twins the item pages ship so the one
    # fetch and the 58 fetches can never disagree.
    w("llms-full.txt", llms_full_txt(items, today))
    # RSS beside Atom and JSON Feed. Atom is the better spec and RSS is the one every reader
    # actually supports, so shipping only the better one is a purity that costs readers.
    w("feed.xml", feed_xml(items, today))
    # A 404 THAT IS A WAY BACK IN, not a dead end. GitHub Pages serves docs/404.html for any
    # unknown path, and without one a mistyped decision id lands a reader on the host's default
    # page with no navigation, no search and no sign the site is even ours.
    w("404.html", not_found_page(today, items))
    # THE RECORD AUTHORISES ITS OWN ARITHMETIC. `listed` covers the figures the items carry;
    # the calendar's counts, day numbers and years are computed on the page and come back with
    # it, so the two sets are unioned rather than one silently standing in for the other.
    _rec_html, _rec_figs = docket_index(items, today)
    w("record/index.html", _rec_html, listed(items) | _rec_figs)
    # THE HUB, THEN THE BEATS. Written above the loop so the family reads as a family, and
    # so a reader or a crawler arriving at /topic/ finds a page rather than a 404.
    _tfig, _thtml = topics_index(items, today)
    w("topic/index.html", _thtml, extra=_tfig)
    for t in sorted({i["topic"] for i in items}):
        w(f"topic/{t}/index.html", topic_page(t, items, today),
          listed([i for i in items if i["topic"] == t]))

    # A PAGE PER RESEARCHED FACILITY. The registry names 151 data centers and gives five
    # fields each. These are the ones somebody actually researched, and each gets a real url
    # so a reader who searches the facility by name can land on it. The dialog on the grid
    # page renders the SAME `panel` call, so the two surfaces cannot drift.
    _doss = facility_dossier.load()
    # THE SECOND REGISTER, ON THE PAGE A READER ACTUALLY OPENS. Computed once for the whole
    # registry, because deciding whether a party is a single purpose entity or a parent company
    # is a question about all 151 rows and not about one of them.
    _fil = facility_filings(entities.load(), tdlr_projects.load())
    # A FALSE GAP IS WORSE THAN NO GAP. It tells a reader to stop looking for something this
    # build is holding. Hard, like the numeral gate, because a gap nobody checks is a claim.
    _cg = contradicted_gaps(_doss.get("dossiers") or [], _fil)
    if _cg:
        for _line in _cg:
            print(f"  gap: {_line}", file=sys.stderr)
        raise SystemExit(
            f"site_build: {len(_cg)} dossier gap(s) say a field is not public while the "
            f"construction filing this build read carries it. Publish the field as a fact, or "
            f"reword the gap to say which register lacks it.")
    for _d in _doss.get("dossiers") or []:
        _m = _fil.get(_d["name"]) or []
        _n = facility_dossier.authorised({"dossiers": [_d]})
        if _m:
            _t = tdlr_projects.totals(_m)
            _n |= {tdlr_projects.money(_t["cost"]), f"{_t['filings']:,}", f"{_t['sqft']:,}"}
            for _r in _m:
                _n |= {tdlr_projects.money(_r.get("cost")), (_r.get("start") or "")[:4]}
                if _r.get("sqft"):
                    _n.add(f"{_r['sqft']:,}")
                _n |= set(re.findall(r"\d[\d,]*", _r.get("project") or ""))
        w(f"facility/{_d['slug']}/index.html", facility_page(_d, today, _m), _n)

    # WHO IS BEHIND THE REGISTRY. The same 151 rows read down their columns. Every count on
    # these pages is computed from the certified list, and the resolution that makes the counts
    # correct is in entities.py with the comma problem it exists for.
    _ent = entities.load()
    _dmap = {x["name"]: x for x in (_doss.get("dossiers") or [])}
    _enums = entities.authorised(_ent)
    w("company/index.html", companies_index(_ent, today), _enums)

    # WHAT THE STATE QUIETLY CHANGED. A pure function of the raw snapshots the collector keeps.
    _rc = registry_changes.load()
    if _rc["readings"] >= 2:
        _rcnums = {entities.n0(_rc["readings"])}
        for _h in _rc["history"]:
            _rcnums |= {entities.n0(len(_h[k])) for k in ("added", "removed", "substantive")}
            _rcnums |= {_h["from"], _h["to"]}
        for _f in _ent["facilities"]:
            if _f.get("effective"):
                _rcnums.add(str(_f["effective"]))
        w("registry-changes/index.html", registry_changes_page(_rc, today), _rcnums)
    # THE SECOND STATE REGISTER. Every numeral on that page is computed by tdlr_projects from
    # the filings, so the authorised set is built by calling the same functions rather than by
    # listing figures here.
    _tp = tdlr_projects.load()
    if _tp.get("projects"):
        _tracked = [r for r in _tp["projects"] if tdlr_projects.brand(r)]
        _dc = [r for r in _tracked if tdlr_projects.is_datacenter(r)]
        _other = [r for r in _tracked if not tdlr_projects.is_datacenter(r)]

        def _bn(v):
            return (f"${v / 1_000_000_000:.2f} billion" if v >= 1_000_000_000
                    else f"${entities.n0(v)}")

        _tnums = set()
        for _set in (_dc, _other):
            _t = tdlr_projects.totals(_set)
            _tnums |= {entities.n0(_t[k]) for k in ("filings", "sqft", "sqft_known", "counties")}
            _tnums |= {_bn(_t["cost"]), _t["first"], _t["last"],
                       facility_dossier.ordinal(_t["first"]),
                       facility_dossier.ordinal(_t["last"])}
        for _y in tdlr_projects.by_year(_dc):
            _tnums.add(str(_y["year"]))
        for _b in tdlr_projects.by_brand(_dc):
            _tnums |= {_bn(_b["cost"]), entities.n0(_b["sqft"]), entities.n0(_b["filings"]),
                       entities.n0(len(_b["counties"]))}
        _cty = {}
        for _r in _dc:
            if _r.get("county"):
                _cty[_r["county"]] = _cty.get(_r["county"], 0) + (_r.get("cost") or 0)
        for _c, _v in _cty.items():
            _tnums |= {_bn(_v), entities.n0(sum(1 for _r in _dc if _r.get("county") == _c))}
        for _c in tdlr_projects.campuses(_dc):
            # THE CAMPUS NAME IS AN IDENTIFIER AND HAS TO BE AUTHORISED LIKE ONE, which the
            # facility loop eight lines down already does with `_tnums.add(_f["name"])`.
            # `Project Gold Phase 2 - DFW44` carries digits from a filing rather than a
            # measurement, and this loop authorised the three figures and never the name.
            #
            # IT PASSED FOR WEEKS ON A COINCIDENCE IN A DIFFERENT SUBSYSTEM. The authorised set
            # is site wide, `by_room["open_meeting"]` happened to be 44, and so "44" was allowed
            # as a count of open meeting rooms. The August 23rd run admitted one item carrying
            # an open_meeting room, the count moved to 45, the cover came off, and a correct
            # page failed the build. That run could not fix it, because this file is `human`
            # owned and it stamps `daily`, so a whole day of record work sat blocked on one
            # token rather than the run gaming a gate with the record.
            _tnums |= {_bn(_c["cost"]), entities.n0(_c["sqft"]),
                       entities.n0(_c["buildings"]), _c["project"]}
        # The join, priced per facility, by the same call the page makes.
        _byp = {}
        for _r in _dc:
            _byp.setdefault(entities.normalise(_r.get("owner", "")), []).append(_r)
        _parties = [{entities.normalise(_x) for _k in ("owners", "occupants", "operators")
                     for _x in (_f.get(_k) or [])} for _f in _ent["facilities"]]
        _spec = tdlr_projects.joinable(_parties)
        for _f, _ps in zip(_ent["facilities"], _parties):
            _m = tdlr_projects.filings_for(_ps, _spec, _byp)
            if _m:
                _tnums |= {_bn(sum(_x.get("cost") or 0 for _x in _m)), entities.n0(len(_m)),
                           _f["name"]}
        for _f in _ent["facilities"]:
            _tnums.add(_f["name"])
        w("construction/index.html", construction_page(_tp, _ent, today), _tnums)

    _elist, _glist = entities.published(_ent)
    for _x in _elist:
        w(f"company/{_x['slug']}/index.html",
          company_page(_x, _ent, _dmap, False, today), _enums)
    for _g in _glist:
        w(f"company/{_g['slug']}/index.html",
          company_page(_g, _ent, _dmap, True, today), _enums)
    # THE INDEX SHOWS EVERY RUN, so its authorised set is the union of every run's own
    # figures and not a byte wider. `_run_numerals` derives each from that run's claims and
    # its `computed.json`, never from what a slide happened to print, so this stays the
    # non-circular allowlist the per-article pages already use.
    w("articles/index.html", articles_page(runs, today),
      extra=set().union(*(_run_numerals(r) for r in runs)) if runs else set())
    w("videos/index.html", videos_page(today))
    # THE FEED ITSELF IS EXTERNAL DATA and is copied through byte for byte. It is written by
    # `TexasAIDispatch` and `ownership.yaml` gives it to that actor, so no build here may
    # write it, reformat it, or invent one when it is missing.
    feed_src = REPO_ROOT / "docs" / "videos" / "videos.json"
    if feed_src.exists() and feed_src.resolve() != (out / "videos" / "videos.json").resolve():
        (out / "videos").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(feed_src, out / "videos" / "videos.json")
        written.append("videos/videos.json")
    for r in runs:
        # THE DECK'S OWN NUMERALS, AUTHORISED WHERE THEY WERE COMPUTED AND QUOTED.
        #
        # This page now publishes the deck's prose and every claim behind it, so it carries
        # figures this site build did not compute. That is exactly the case the law already
        # covers at the docket layer: a numeral reaches published copy either by being computed
        # from data or by being QUOTED FROM A SOURCE. Both sets come from the run's own
        # artifacts, so nothing here is authorised by being typed.
        #
        # PER PAGE, NEVER SITE-WIDE, for the reason `_authorised_numerals` records twice over:
        # both times this gate was silently disabled, the cause was an allowlist that grew
        # wider than the page it guarded. Only this article page gets this article's figures.
        w(f'articles/{r["date"]}/index.html', article_page(r, today, items),
          extra=_run_numerals(r))
    # PER PLACE. The index, then a page for every metro the record touches and every
    # touched county that is in no metro. Nothing falls between the two.
    #
    # THIS COMMENT PROMISED AN INDEX FOR MONTHS AND THERE WAS NONE. It is written now, and it
    # is written first, because 73 pages reachable only sideways from whichever item names
    # them is the largest family on this site being crawled as strangers.
    _plfig, _plhtml = places_index(items, today)
    w("place/index.html", _plhtml, extra=_plfig)
    for pl in all_places(items, today):
        w(f'place/{pl["id"]}/index.html', place_page(pl, items, today),
          listed([i for i in items if i["id"] in set(pl["items"])]))
    w("grid/index.html", grid_page(today), _watch_numerals(gridwatch_page))
    # The catalogue size is the one figure this page states, and it is the length of the
    # list the page is shipping. It passed the gate before the metro questions existed
    # only because the count was 121 and the state has 121 counties in no metro, which is
    # the coincidence `numeral_lint`'s docstring admits it cannot see through.

    w("scan/index.html", scan_page(today))
    w("scan/watch/index.html", watch_page(today))
    w("services/index.html", services_page(items, today))
    w("water/index.html", water_page(today), _watch_numerals(waterwatch_page))

    # THE ANSWERING RECORD, published as two files beside the site.
    #
    # ask-pack.json is the whole record as prose, which is what the written answer lane puts in
    # front of the model. ask-corpus.json is the answer key the worker marks the reply against,
    # and its numeral allow-list is READ OFF THE PACK rather than off the ledger, so the promise
    # is exact: the model may state a number only if that number was in what it was shown.
    #
    # IT RUNS HERE, AFTER THE FEEDS, AND READS THEM OUT OF THIS BUILD'S OWN OUTPUT. Reading
    # them from the repository's docs/ instead made the pack depend on whatever the LAST build
    # left on disk, so a rebuild into a temp directory picked up stale instrument readings and
    # produced a different pack. site_fresh_check caught exactly that, which is what it is for.
    # A build has to be a pure function of the ledgers or the freshness promise is hollow.
    #
    # Published rather than bundled into the worker because both change daily with the record
    # and the worker does not. A worker carrying its own copy would answer from yesterday's
    # docket the morning after a run, and nothing would say so.
    corpus, pack = ask_corpus.write(out / "ask-corpus.json", out / "ask-pack.json",
                                    today, docs_dir=out)
    written.extend(["ask-corpus.json", "ask-pack.json"])
    # THE DATA CENTERS TAB. Its numerals come from three registers and each is authorised by
    # the call that renders it: the roster panel authorises its own, the campus totals come
    # from `campuses()`, and the tiles are counted here.
    _dcent = entities.load()
    _dcpj = tdlr_projects.load()
    _dcdc = [r for r in (_dcpj.get("projects") or [])
             if tdlr_projects.brand(r) and tdlr_projects.is_datacenter(r)]
    # ITS OWN FORMATTER. `_bn` above is defined inside a branch that only runs when the
    # construction ledger has rows, so borrowing it makes this block depend on that.
    def _dcbn(v):
        return (f"${v / 1_000_000_000:.2f} billion" if v >= 1_000_000_000
                else f"${entities.n0(v)}")

    _dcn = beyond_panel.authorised(beyond_panel.figures(beyond_panel.load()))
    _dcn |= {entities.n0(len(_dcent["facilities"])),
             entities.n0(sum(1 for x in _dcent["entities"] if x["reach"] > 1)),
             entities.n0(len(facility_dossier.load().get("dossiers") or [])),
             _dcbn(tdlr_projects.totals(_dcdc)["cost"])}
    for _c in tdlr_projects.campuses(_dcdc):
        _dcn |= {_dcbn(_c["cost"]), entities.n0(_c["sqft"]),
                 entities.n0(_c["buildings"])}
    for _x in _dcent["entities"]:
        _dcn.add(entities.n0(_x["reach"]))
    w("datacenters/index.html", datacenters_page(today), _dcn)

    # A permissive robots.txt is the product strategy, not a concession. For a record built to
    # be cited, blocking the crawlers that cite it would be self-defeating.
    #
    # THE ONE EXCEPTION, AND IT COSTS NOTHING. Every item, topic and place page ships a Markdown
    # twin beside it for machine readers. The twin is the same content at a second URL, and a
    # .md file can carry no `rel="canonical"` while GitHub Pages can set no `X-Robots-Tag`
    # header, so there is no way to tell a search engine which of the pair is the real page.
    # Google reported the twins as "Duplicate without user-selected canonical" on August 25th,
    # which is Google saying it had to guess. It normally guesses the HTML. Nothing makes it,
    # and the failure mode is a raw Markdown file in the results in place of the designed page.
    #
    # So Googlebot alone is told to skip them, and every other crawler is left exactly as it
    # was. Google loses nothing, because the identical content is on the HTML page it already
    # indexes. The AI crawlers the twins were built for never see this group at all, since a
    # robots.txt group applies only to the agent it names.
    #
    # THE GROUP MUST REPEAT `Allow: /`. A crawler that matches a specific user-agent group obeys
    # THAT GROUP ONLY and ignores `User-agent: *` entirely, so a group holding just the Disallow
    # would read to Googlebot as a site with no Allow at all.
    w("robots.txt",
      "# The Texas AI Docket wants to be read, indexed, cited and learned from.\n"
      "# Content-Signal is the only machine readable way to say yes rather than no.\n"
      "Content-Signal: search=yes, ai-input=yes, ai-train=yes\n\n"
      "User-agent: *\nAllow: /\n\n"
      "# The Markdown twins are for machine readers, not for the index. They duplicate the\n"
      "# HTML page they sit beside and cannot declare a canonical, so search skips them.\n"
      "User-agent: Googlebot\nAllow: /\nDisallow: /*.md$\n\n"
      f"Sitemap: {SITE_URL}/sitemap.xml\n")

    # EVERY PAGE'S OWN REVISION DATE, computed once and spent twice.
    #
    # This stamped `today` on all 222 urls, which told Google the whole site changed this
    # morning every morning. Google's position on a `lastmod` it finds unreliable is to stop
    # reading it, so the one field that says "this page is worth fetching again" was being
    # spent on 222 pages that were not worth fetching again. The colophon printed the same
    # untruth in words under every page.
    #
    # `lastmod.py` derives the date from the only record that actually holds it, which is the
    # history of the generated bytes themselves. The substitution happens here, after every
    # page exists, because a page cannot be compared against its committed self while it is
    # still being written.
    revised = lastmod.dates_for(pages, items=items, runs=runs)
    for path, (text, extra) in pages.items():
        iso = revised.get(path)
        stamped = lastmod.apply(text, iso, ordinal)
        own = set()
        if iso:
            d = _dt.date.fromisoformat(iso)
            # The date is a ledger field, so its numerals are authorised. Per page rather than
            # site wide, because a page is entitled to its own date and not another's.
            own = {str(d.day), f"{d.day:02d}", str(d.year), iso, *iso.split("-")}
        stray = numeral_lint.scan(stamped, authorised | extra | own)
        if stray:
            unauthorised.append(f"{path}: {', '.join(stray[:8])}")
        # THE POLICY IS CHECKED HERE, AGAINST `stamped`, and the position is the point. The
        # policy was computed inside `page()` and `lastmod.apply` has rewritten the document
        # since, so auditing any earlier string would check bytes nobody serves. If that
        # substitution ever reaches inside a script or a style block, the hash it invalidates
        # is caught on this line rather than by a reader whose page quietly stopped working.
        if path.endswith(".html"):
            broken.extend(f"{path}: {v}" for v in csp.audit(stamped, SITE_URL))
            connect_seen |= csp.connect_targets(stamped)
        (out / path).write_text(stamped, encoding="utf-8")

    # A url with no honest date carries no `lastmod`. The element is optional and an absent one
    # reads as "no claim", which is true, where a wrong one costs the whole field its
    # credibility across every url on the site.
    urls = [u for u in written if u.endswith("index.html")]
    locs = "".join(
        f"<url><loc>{SITE_URL}/{u[:-10]}</loc>"
        + (f"<lastmod>{revised[u]}</lastmod>" if u in revised else "")
        + "</url>"
        for u in urls)
    w("sitemap.xml",
      f'<?xml version="1.0" encoding="UTF-8"?>'
      f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{locs}</urlset>')

    # AND THE OTHER DIRECTION, which needs every page and so cannot live in a per-page audit.
    # A declared origin nothing targets widens the policy for free. The entry for the scan
    # intake outlived the intake by a day and no gate said so, because an over-wide policy
    # refuses nothing and therefore reports nothing.
    broken.extend(csp.unused_connect(connect_seen))
    # THE FILMS' OWN ORIGIN, checked against the policy this build just wrote. Neither video
    # surface writes the address into markup, so `csp.audit`'s attribute patterns see nothing on
    # a site whose every film is being refused. The manifest is where the origin actually lives,
    # and TexasAIDispatch can change it without a byte of this repo changing.
    broken.extend(csp.unaudited_media(video_feed(), SITE_URL))

    # THE GATE FIRES HERE, after every page is written, so the report names all of them
    # rather than the first. A build that would publish a typed numeral does not publish.
    # A CSP FAILURE IS SILENT AND TOTAL, so it stops the build the same way a typed numeral does.
    # A policy that misses one inline script does not warn anybody: the browser refuses that
    # script, the page half works, and every other gate here stays green.
    if broken:
        for line in broken:
            print(f"  csp: {line}", file=sys.stderr)
        raise SystemExit(
            f"site_build: {len(broken)} content security policy finding(s). A page loads or "
            f"posts to an origin its own policy refuses, carries an inline block nobody "
            f"hashed, or the policy declares an origin no page targets. The allowlist is "
            f"scripts/site/csp.py and it is checked BOTH WAYS: add the origin there if a page "
            f"should be reaching it, remove it if nothing does, and otherwise the page should "
            f"not be reaching it.")

    if unauthorised:
        for line in unauthorised:
            print(f"  numeral: {line}", file=sys.stderr)
        raise SystemExit(
            f"site_build: {len(unauthorised)} page(s) print a numeral this build did not "
            f"compute. Every published figure traces to data, which is the reason a reader "
            f"should believe one here. Compute it, or authorise it where it is computed.")

    return {"pages": len(urls), "files": len(written), "items": len(items),
            "numerals_authorised": len(authorised)}


def self_test() -> int:
    import tempfile
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    # THE TOPIC VOCABULARY LIVES IN TWO FILES AND THEY HAVE TO AGREE.
    #
    # `docket_build.TOPICS` decides what the record may admit. `TOPIC_BLURBS` decides what
    # /topic/ and the front page can say about it. Adding a beat to the first and not the second
    # is a build that dies at Phase 16 with the deck already made, which is the most expensive
    # minute of the run to discover it in. Adding it to the second only is a blurb nothing
    # renders, which nobody notices at all.
    #
    # So it is checked HERE, where it costs a second and CI runs it on the pull request that
    # adds the beat. The error names the missing side, because the whole point is that whoever
    # trips it should not have to read this file to know what to do.
    # THE CERTIFIED LIST NAMES A FACILITY TWICE AND THE JOIN HAS TO SURVIVE IT.
    #
    # Four names in the registry carry two rows each, because a campus can be certified more than
    # once. Both rows render to one slug and one dossier, so the join is a question about names
    # and never about rows. Two things break if rows are counted instead. The second row's result
    # overwrites the first, so a page shows one certification's parties as though they were all
    # of them. And the parent company test counts how many FACILITIES a party names, so a
    # facility certified three times makes its own single purpose entity look like a company
    # naming three projects, and the join refuses the row it exists to serve. Both are replayed
    # here on the exact shape the live registry has.
    # THE OWNER STRINGS CARRY A TRACKED BRAND ON PURPOSE. `facility_filings` drops any filing
    # `brand()` does not recognise before it joins anything, so a fixture owner invented for the
    # occasion is filtered out and every assertion below passes by finding nothing. The first
    # cut of these tests did exactly that, and the one asserting an EMPTY result passed while
    # proving nothing at all.
    _reg = {"facilities": [
        {"name": "Twice Certified DC", "owners": ["Vantage Alpha LLC"]},
        {"name": "Twice Certified DC", "owners": ["Vantage Alpha LLC", "Vantage Parent Inc"]},
        {"name": "Thrice Certified DC", "owners": ["Vantage Beta LLC"]},
        {"name": "Thrice Certified DC", "owners": ["Vantage Beta, LLC"]},
        {"name": "Thrice Certified DC", "owners": ["Vantage Beta LLC"]},
    ]}
    _pj = {"projects": [
        {"number": "A1", "owner": "VANTAGE ALPHA LLC", "project": "Data Center", "cost": 1,
         "start": "2024-01-01"},
        {"number": "B1", "owner": "VANTAGE BETA LLC", "project": "Data Center", "cost": 2,
         "start": "2024-01-01"},
    ]}
    _got = facility_filings(_reg, _pj)
    check("the fixture reaches the join at all, rather than being filtered before it",
          set(_got) == {"Twice Certified DC", "Thrice Certified DC"}, repr(sorted(_got)))
    check("a facility certified twice keeps every party either row named",
          [r["number"] for r in _got.get("Twice Certified DC", [])] == ["A1"], repr(_got))
    check("...and one certified three times is still one facility, not a parent company",
          [r["number"] for r in _got.get("Thrice Certified DC", [])] == ["B1"], repr(_got))
    # AND THE PARENT COMPANY REFUSAL STILL BITES, which is what stops the fix above from
    # becoming a join on anything. A name on three DIFFERENT facilities is a company. Asserted
    # against the same party joining fine on two, so an empty result cannot pass by accident.
    _party = lambda n: {"facilities": [{"name": f"Site {i}", "owners": ["Vantage Parent Inc"]}
                                       for i in range(n)]}
    _one = {"projects": [{"number": "P1", "owner": "VANTAGE PARENT INC", "project": "Data Center",
                          "cost": 1, "start": "2024-01-01"}]}
    check("a party naming two facilities is specific enough to join on",
          len(facility_filings(_party(2), _one)) == 2, repr(facility_filings(_party(2), _one)))
    check("...and the same party naming three joins to none of them",
          facility_filings(_party(3), _one) == {}, repr(facility_filings(_party(3), _one)))
    # A GAP IS A CLAIM ABOUT THE WORLD AND NO GATE COULD CHECK ONE. Nine dossiers carried
    # "The street address is not public" while the address sat in the construction filing this
    # same build reads. The dossier gate checks that gaps exist and carry no digits, and has no
    # way to know whether one is true. This checks the class that is checkable.
    _g = [{"name": "F", "gaps": ["The street address is not public"], "facts": []}]
    _f = {"F": [{"address": "1 Way", "county": "Travis"}]}
    check("a gap saying the address is not public fails when the filing has one",
          len(contradicted_gaps(_g, _f)) == 1, contradicted_gaps(_g, _f))
    check("...and the county half of the rule bites too",
          len(contradicted_gaps([{"name": "F", "gaps": ["The county is not public"],
                                  "facts": []}], _f)) == 1)
    # THE THREE WAYS IT MUST STAY QUIET, each of which is a correct page.
    check("...but not when a fact on the same page supplies the address",
          contradicted_gaps([{**_g[0], "facts": [{"label": "Address on the construction filing",
                                                  "text": "1 Way"}]}], _f) == [])
    check("...nor when the facility has no construction filing at all",
          contradicted_gaps(_g, {}) == [])
    check("...nor when the gap is about something the filing does not carry",
          contradicted_gaps([{"name": "F", "gaps": ["Capacity is not public"], "facts": []}],
                            _f) == [])
    check("the live ledger has no contradicted gap",
          contradicted_gaps(facility_dossier.load().get("dossiers") or [],
                            facility_filings(entities.load(), tdlr_projects.load())) == [])

    missing = sorted(dk.TOPICS - set(TOPIC_BLURBS))
    check(f"every admitted beat has a blurb (missing {missing or 'none'})", not missing,
          "add one line per slug to TOPIC_BLURBS in scripts/site/site_build.py")
    orphan = sorted(set(TOPIC_BLURBS) - dk.TOPICS)
    check(f"...and no blurb describes a beat the record cannot admit ({orphan or 'none'})",
          not orphan, "remove it, or add the slug to TOPICS in scripts/site/docket_build.py")
    # A BLURB THAT SAYS NOTHING PASSES THE CHECK ABOVE AND FAILS THE READER. It is published as
    # the page's meta description, which is the sentence a search result shows.
    thin = sorted(t for t, b in TOPIC_BLURBS.items() if len(b.split()) < 8)
    check(f"...and every blurb is a sentence rather than a placeholder ({thin or 'none'})",
          not thin, "a meta description under eight words tells a search result nothing")

    today = "2026-08-11"
    with tempfile.TemporaryDirectory() as td:
        stats = build(Path(td) / "a", today)
        check("the site builds", stats["pages"] >= 4, str(stats))
        idx = (Path(td) / "a" / "index.html").read_text(encoding="utf-8")
        # WHAT THIS PROTECTS IS THE ANSWER, NOT ONE DRAFT'S PHRASING. It used to look for the
        # literal words "still say something", which lived in the first headline, so shortening
        # the headline failed a check about whether the page answers the reader's question. The
        # question is whether somebody can still act. The page answers it with a COUNTED number
        # of ways in, marked hot so it reads first, and with the sentence that teaches what the
        # green means. Both of those are structural and survive a rewrite. A quoted fragment of
        # a headline is a copy of the copy, and it only ever fails for the wrong reason.
        check("the home page counts the ways a reader can still act",
              'class="n hot"' in idx and "Doors open to you" in idx)
        # THE SENTENCE THIS USED TO CHECK IS GONE, on the owner's call that every word has to
        # earn its space. It read "Green means a door is open to you", and the check asserted the
        # page taught the signal. The counted, hot-marked figure above is what carries the answer
        # now, and a check with no subject left is worse than no check at all.
        check("the map is inline, so it needs no second request", "<svg class=\"txmap\"" in idx)
        check("Dataset structured data is emitted", '"@type":"Dataset"' in idx)
        _rb = (Path(td) / "a" / "robots.txt").read_text()
        check("robots says yes rather than no", "ai-train=yes" in _rb)
        # THE MARKDOWN TWINS ARE OUT OF THE INDEX AND STILL OPEN TO EVERYONE ELSE. Both halves
        # are asserted, because the easy wrong version of this fix is a Disallow under
        # `User-agent: *`, which would shut the twins to the AI crawlers they exist for.
        check("...and the Markdown twins are kept out of the search index",
              "User-agent: Googlebot" in _rb and "Disallow: /*.md$" in _rb, _rb)
        check("...while every other crawler is still allowed everything",
              _rb.split("User-agent: Googlebot")[0].count("Disallow:") == 0, _rb)
        # A crawler matching a named group obeys that group ONLY, so the group needs its own
        # Allow or Googlebot reads a site with a Disallow and no Allow at all.
        check("...and Googlebot's own group still allows the rest of the site",
              "User-agent: Googlebot\nAllow: /\n" in _rb, _rb)
        check("the advertised feed exists", (Path(td) / "a" / "atom.xml").exists())
        check("a Markdown twin exists for every item",
              len(list((Path(td) / "a" / "item").rglob("index.md"))) == stats["items"])
        md = next((Path(td) / "a" / "item").rglob("index.md")).read_text(encoding="utf-8")
        check("the Markdown twin carries the source's own words", "> " in md)
        check("llms.txt claims nothing it cannot back",
              "## The whole record, by beat" in (Path(td) / "a" / "llms.txt").read_text(encoding="utf-8"))

        # Rule 1: docs/ is a pure function of the ledgers.
        b = Path(td) / "b"
        build(b, today)
        diff = [p for p in (Path(td) / "a").rglob("*") if p.is_file()
                and (b / p.relative_to(Path(td) / "a")).read_bytes() != p.read_bytes()]
        check("two builds are byte identical", not diff, f"{len(diff)} differ")

        # An item page must show the source's own words, or the proof is only asserted.
        items = dk.load(LEDGER)
        one = (Path(td) / "a" / "item" / items[0]["id"] / "index.html").read_text(encoding="utf-8")
        check("an item page quotes its sources", "<blockquote>" in one)

        # A CARD THAT SAYS ONLY WHAT IT IS CALLED IS NOT A PREVIEW, and this has now gone
        # blank twice for two different reasons, which is what makes it worth a check rather
        # than a careful edit. First the card printed `copy.json`'s top level `hook`, a field
        # that does not exist, so the paragraph rendered empty. The repair pointed it at the
        # title of the DECISION the deck is about, which is real prose and correctly gated and
        # is empty on any run carrying no `story`. Two of the three shipped runs carry none, so
        # the front page and the articles index both went back to a headline, two buttons and a
        # gap in between.
        #
        # Neither failure could redden anything. An empty paragraph is valid HTML, the numeral
        # gate has no numeral to trace, and house style has no words to judge, so every gate on
        # this site agreed the page was fine while the page said nothing. That is the shape
        # GATE_LESSONS keeps recording: the checks all observed the copy and not the ABSENCE of
        # it. So this counts the cards and reads what is under each title, on the BUILT page.
        arts = (Path(td) / "a" / "articles" / "index.html").read_text(encoding="utf-8")
        cards = re.findall(r"<h3>(.*?)</h3>\s*(?:<p class=\"tease\">(.*?)</p>)?", arts, re.S)
        bare = [" ".join(re.sub(r"<[^>]+>", "", t).split()) for t, tease in cards
                if len(re.sub(r"<[^>]+>", "", tease or "").split()) < 8]
        check(f"every article card carries a preview and not just a title ({len(cards)} card(s))",
              cards and not bare, f"thin: {bare[:3]}; widen deck_preview's sentence budget")
        # The same card on the front page, which is where a reader meets it first and where the
        # blank one was found. It is built by a different function off the same helper, so one
        # of the two staying right proves nothing about the other.
        home_card = idx[idx.find("Our latest article"):]
        home_card = home_card[:home_card.find("</section>")]
        blurbs = [" ".join(re.sub(r"<[^>]+>", "", m).split())
                  for m in re.findall(r"<p[^>]*>(.*?)</p>", home_card, re.S)]
        check("...and so does the one on the front page",
              any(len(b.split()) >= 8 for b in blurbs), f"got: {blurbs}")

        # THE PLACE LINKS RUN BOTH WAYS. The place pages listed their items from the
        # first build and nothing pointed back, which looks correct from either end: every
        # place page is fully connected when you are standing on it. Checked here as a
        # round trip rather than as "the item page contains the word place", because the
        # thing worth guaranteeing is that a reader can get from an item to a place page
        # and find that same item waiting there.
        located = [i for i in items
                   if ((i.get("geography") or {}).get("counties") or [])]
        round_trip = []
        for i in located:
            page_html = (Path(td) / "a" / "item" / i["id"] / "index.html").read_text("utf-8")
            for pid in set(re.findall(r'href="\.\./\.\./place/([^"/]+)/"', page_html)):
                target = Path(td) / "a" / "place" / pid / "index.html"
                if not target.exists() or f'item/{i["id"]}/' not in target.read_text("utf-8"):
                    round_trip.append(f'{i["id"]} -> {pid}')
        check("every located item links to a place page that lists it back",
              located and not round_trip, f"broken: {round_trip[:3]}")
        check("...and an item with no county says so rather than linking nowhere",
              all("appears on no place page" in
                  (Path(td) / "a" / "item" / i["id"] / "index.html").read_text("utf-8")
                  for i in items if i not in located
                  and not (i.get("geography") or {}).get("statewide")))

        # THE NUMERAL GATE, PROVEN TO FIRE, AND PROVEN TO BE NARROW.
        #
        # This gate has been green and inert twice, for two unrelated reasons, and the
        # suite reported clean through both. First its per page sets were unioned into one
        # site wide set, and the grid watch's several hundred hourly and fuel mix figures
        # authorised almost any number on any page. Then, after that was fixed, the
        # scanner still deleted authorised strings as SUBSTRINGS, so the ten single digits
        # every page authorises within a few counts and dates dissolved every multi digit
        # figure on the site one character at a time.
        #
        # Neither was found by a test. Both were found by planting a figure by hand and
        # watching the build sail through. So the plant is a test now, and it plants twice:
        # once with a number nothing computed, and once with a number that IS computed on
        # a DIFFERENT page, which is the only way to catch a set that has quietly widened.
        import contextlib as _cl, io as _io
        real_docket, real_home = docket_index, home

        def planted(fn, find, ins):
            """Plant a figure in a page builder's html, whatever shape it hands back.

            `docket_index` returns (html, the numerals it computed) so the calendar's counts
            can be authorised where they are computed. A helper that assumed a bare string
            broke this gate the moment that changed, which would have been a self-test failing
            for a reason that has nothing to do with the law it guards.
            """
            def go(*a, **k):
                out = fn(*a, **k)
                if isinstance(out, tuple):
                    html, *rest = out
                    return (html.replace(find, find + ins, 1), *rest)
                return out.replace(find, find + ins, 1)
            return go

        for label, name, real, ins, want in (
                ("a figure nothing computed", "docket_index", real_docket,
                 "<p>Roughly 8,927 megawatts.</p>", "8,927"),
                ("a figure computed on another page", "docket_index", real_docket,
                 "<p>Energy served was 1,743,297 MWh.</p>", "1,743,297"),
                ("a figure planted on the front page", "home", real_home,
                 "<p>Some 41,203 filings.</p>", "41,203")):
            anchor = "<h1>The record</h1>" if name == "docket_index" else "</h1>"
            globals()[name] = planted(real, anchor, ins)
            err, fired = _io.StringIO(), False
            try:
                with _cl.redirect_stderr(err):
                    build(Path(td) / "planted", today)
            except SystemExit:
                fired = True
            finally:
                globals()[name] = real
            check(f"the numeral gate reddens the build on {label}", fired)
            check(f"...and names {want}, so it can be found", want in err.getvalue(),
                  err.getvalue()[:200])

        check("the gate is still green once the plants are removed",
              build(Path(td) / "clean", today)["pages"] == stats["pages"])

        # NO ORPHAN PAGE BUILDERS. docket_index() shipped once defined and never called, so
        # nothing listed the whole record and no gate noticed: an unreferenced function does
        # not throw, which is the same failure mode the port audit's wiring check exists for.
        import inspect, re as _re
        src = inspect.getsource(build)
        builders = [n for n, o in globals().items()
                    if callable(o) and (n.endswith("_page") or n in {"home", "docket_index"})]
        orphans = [n for n in builders if not _re.search(rf"\b{n}\s*\(", src)]
        check("every page builder is reached by build()", not orphans, f"orphaned: {orphans}")
        families = {
            "site_pages.editorial", "site_pages.docket", "site_pages.watch",
            "site_pages.feeds", "site_pages.datacenters",
        }
        owners = {globals()[name].__module__ for name in builders}
        check("page builders stay in explicit family modules",
              owners == families, f"expected {sorted(families)}, got {sorted(owners)}")

        # LINK DEPTH. Moving a page one directory deeper silently breaks every relative link
        # inside it, and it renders fine, so nothing notices until a reader clicks. The port
        # audit catches it repo-wide; catching it here means a broken build never gets written.
        import re as _re2
        root = Path(td) / "a"
        broken = []
        # Script blocks are stripped first. A URL built at runtime, like the ask engine's
        # "../item/" + id + "/", is not a static href and cannot be resolved by reading it.
        # The links it produces are covered instead by the data check below, which is the
        # honest way to check them: verify every id it could use, not the string that uses it.
        script = _re2.compile(r"<script\b.*?</script>", _re2.DOTALL | _re2.IGNORECASE)
        for f in root.rglob("*.html"):
            text = script.sub(" ", f.read_text(encoding="utf-8"))
            for href in _re2.findall(r'href="([^"#?:]+)"', text):
                if href.startswith(("http", "//", "mailto")):
                    continue
                t = (f.parent / href).resolve()
                if not (t.exists() or (t / "index.html").exists()):
                    broken.append(f"{f.relative_to(root)} -> {href}")
        # THE ASK ENGINE'S LINKS, CHECKED AS DATA. Every item the index can route to must
        # have a page built for it. This is what the static scan above structurally cannot do.
        ask_idx = ask_answers.index(dk.load(LEDGER), "2026-08-11")
        missing_pages = [i["id"] for i in ask_idx["items"]
                         if not (root / "item" / i["id"] / "index.html").exists()]
        check("every item the ask engine can route to has a page",
              not missing_pages, str(missing_pages[:5]))
        ask_routes = {c["route"]["view"] for c in ask_answers.catalogue(ask_idx)}
        check("every route the catalogue emits is one the engine implements",
              ask_routes <= set(ask_answers.VIEWS), str(ask_routes - set(ask_answers.VIEWS)))

        check("every relative link resolves from its own page", not broken,
              f"{len(broken)} broken, first: {broken[:1]}")
        check("an item page links the source", "rel=\"nofollow noopener\"" in one)

    # ---------------------------------------------------------------- next_door
    # WHAT COUNTS AS A DOOR A READER CAN STILL WALK THROUGH. `llms.txt` published 28 finished
    # votes of 47 entries under a heading promising a dated way in, because it filtered on the
    # KIND of access recorded rather than on whether the door is open.
    def door(**over):
        it = {"public_access": {"room": "open_meeting", "closes": None},
              "key_dates": [{"date": "2026-09-04", "kind": "hearing", "note": ""}],
              "status": "pending"}
        it.update(over)
        return it

    check("a future hearing is a door", next_door(door(), "2026-08-16") == "2026-09-04")
    check("a past hearing is not",
          next_door(door(key_dates=[{"date": "2026-07-01", "kind": "hearing"}]),
                    "2026-08-16") is None)
    check("the door is today's, when it is today",
          next_door(door(key_dates=[{"date": "2026-08-16", "kind": "hearing"}]),
                    "2026-08-16") == "2026-08-16")
    check("the NEAREST future door is the one reported",
          next_door(door(key_dates=[{"date": "2026-11-03", "kind": "hearing"},
                                    {"date": "2026-09-04", "kind": "hearing"}]),
                    "2026-08-16") == "2026-09-04")

    # A DECIDED ITEM WITH A FUTURE DOOR KEEPS IT, which is why this is not a status filter.
    # League City has decided, and what it decided was to order a November 3rd election.
    check("a decided item with a future door still has one",
          next_door(door(status="decided"), "2026-08-16") == "2026-09-04")

    # A clock on an agency is not a room a Texan can stand in.
    check("a statutory deadline is not a public door",
          next_door(door(key_dates=[{"date": "2026-09-04", "kind": "statutory_deadline"}]),
                    "2026-08-16") is None)
    check("...nor is the date a rule takes effect",
          next_door(door(key_dates=[{"date": "2027-02-16", "kind": "effective"}]),
                    "2026-08-16") is None)

    # A CANCELED SITTING IS NOT A DOOR, AND IT IS A FIELD RATHER THAN A SENTENCE. This read the
    # note with a regex first, which worked and would have gone quiet the day somebody wrote
    # "called off". gate_schema keeps the note from disagreeing with the flag.
    check("a canceled hearing is not a door",
          next_door(door(key_dates=[{"date": "2026-09-04", "kind": "hearing",
                                     "canceled": True, "note": "since canceled"}]),
                    "2026-08-16") is None)
    check("...and the prose alone no longer decides it",
          next_door(door(key_dates=[{"date": "2026-09-04", "kind": "hearing",
                                     "note": "since canceled"}]),
                    "2026-08-16") == "2026-09-04",
          "the flag is the truth; gate_schema is what refuses this item at build time")

    if failures:
        print(f"\nsite_build self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nsite_build self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(REPO_ROOT / "docs"))
    ap.add_argument("--today", default=_dt.date.today().isoformat())
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    stats = build(Path(a.out), a.today)
    print(f"site: {stats['pages']} pages, {stats['files']} files, {stats['items']} items")
    # THE OUTSTANDING EXEMPTIONS, ON A GREEN BUILD TOO. See `docket_build.backlog`.
    for line in dk.backlog(dk.load(LEDGER)):
        print(f"  backlog: {line}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:                                       # noqa: BLE001
        print(f"site_build: broke: {exc}", file=sys.stderr)
        sys.exit(2)
