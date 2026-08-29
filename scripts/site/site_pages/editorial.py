"""Home, article, and video page renderers."""
from __future__ import annotations

from site_context import (
    HOIST, NAV, RAW, SCHEMA_CTX, SITE_NAME, SITE_URL, _dt, csp, dk, e, favicon,
    js_feed_date, json, load_runs, og, ordinal, page, re, schema, short_date,
    telemetry, texas_map, theme, video_count, video_feed,
)
from site_pages.docket import _place_facts, covers_section
from site_pages.watch import ask_box, county_links

def videos_page(today: str) -> str:
    """The Dispatch feed as a full-bleed vertical feed, one film per screen.

    GENERATED, AND STILL GENERATED NOW THAT IT HAS ITS OWN SHELL. The page used to be a grid
    inside the site's standard `page()` chrome, on the reasoning that a standalone page carries
    a hand-maintained copy of the masthead and this site's masthead changed twice in one
    afternoon. That reasoning was right about the failure and wrong about the cause. The danger
    is a nav somebody TYPES, not a nav that lives outside `page()`. So this document is built
    here, from `NAV` and `SITE_NAME` and the same palette every other page reads, and a section
    added to the site appears in this top bar without anyone touching this function.

    WHY IT IS NOT A GRID ANY MORE. A grid of posters asks a reader to choose before they have
    seen anything, and what they choose from is a still frame of a 2.5D film whose whole
    argument is that it moves. The sibling product's feed is one film per screen, muted, already
    rolling, and a thumb-flick away from the next one, which is the form every reader already
    knows. The measured difference is not subtle: a poster grid is a page you look at and a feed
    is a thing you stay in.

    THE FEED IS FETCHED RATHER THAN BAKED, unchanged and for the same reason as before:
    `docs/videos/videos.json` is written by `TexasAIDispatch` on its own schedule, and a build
    cannot know what shipped after it ran.

    WORKS WITH NO FEED AT ALL. Before the first video the file does not exist, the fetch fails,
    and the page says so in a sentence. It never renders a feed over nothing.

    Four things in the script below are load bearing and each is there for a failure the
    sibling shipped first, so none of them is decoration:

    - **Every feed value is HTML escaped before it reaches `innerHTML`.** A title carrying
      markup would otherwise run as script on this origin.
    - **The preload window is bounded.** Only the current card and its neighbour buffer, the
      two beyond them hold metadata, and everything else is DETACHED outright. Without it a
      reader who flicks through thirty entries leaves thirty live video elements behind and a
      phone gives up.
    - **The download resolves the URL before it checks the scheme.** Checking first rejects a
      relative `media_base` and leaves a dead button.
    - **The scrub sets `touch-action:none` on the grab area and the fill, not only on the
      track.** `touch-action` is not inherited, so setting it in one place lets the browser
      decide mid drag that the gesture was a scroll and take the feed out from under the thumb.

    And one that is this site's own: `prefers-reduced-motion` is honoured. Nothing autoplays for
    a reader who asked for that, the poster stays up, and the play glyph is the invitation. The
    sibling has no such branch, which for a page that is nothing but moving pictures is the one
    accessibility gap worth closing before copying anything else.
    """
    c = theme.palette()["dark"]
    flag = theme.tokens()["colour"]
    # The feed's palette IS the site's palette. Named locally only so the CSS below reads as
    # a feed rather than as a lookup, and sourced from `theme` so a token change reaches here.
    #
    # THE FLAG TOKENS ARE HERE BECAUSE THE MARK CAME OUT BLACK. `mark.flag_svg()` paints
    # nothing itself. Every one of its shapes carries a class and the fills live in
    # `site.css`, which this page does not load, so the first build of it put a black
    # rectangle in the masthead where the Lone Star goes. A standalone page pays for its
    # independence exactly here, and the way to pay it is to read the same tokens rather than
    # to type three hexes that will be right until brand.yaml moves.
    tokens = (
        f"--night:{c['bg']};--deep:{c['surface']};--panel:{c['raised']};--line:{c['rule']};"
        f"--snow:{c['ink-bright']};--body:{c['ink']};--mute:{c['ink-mute']};"
        f"--accent:{c['accent']};--deepaccent:{c['accent-deep']};--good:{c['sig-open']};"
        f"--flag-red:{flag['flag_red']};--flag-blue:{flag['flag_blue']};"
        f"--star:{flag['flag_white']};"
    )

    # THE TOP BAR IS THE SITE'S NAV, GENERATED. `hidesm` is applied by RULE rather than by
    # name, so a section added to `NAV` needs no edit here and cannot silently crowd a phone.
    #
    # The rule is the way out and where you are, and nothing else, because a phone has room for
    # two. Keeping the first four instead put eight items and a wordmark on a 390 px bar and
    # ran the last one off the right edge, which is the shape a hand-maintained nav goes wrong
    # in and the reason this one is generated at all.
    links = []
    for h, t in NAV:
        here = h == "videos/"
        cls = "on" if here else ("" if h == "" else "hidesm")
        a = f' class="{cls}"' if cls else ""
        links.append(f'<a href="../{h}"{a}>{e(t.upper())}</a>')
    nav = "".join(links)

    desc = ("One short film a day on artificial intelligence in Texas. Narrated, sourced, and "
            "built by the same machine that keeps the docket.")

    # THE MEDIA HOST, READ OUT OF THE FEED RATHER THAN TYPED. The films are served from
    # wherever `videos.json` says, which is a field `TexasAIDispatch` owns and this build only
    # reads. A preconnect saves the reader the TLS handshake on the first film, and getting it
    # from the feed means the hint can never point somewhere the media is not. No feed yet, or
    # a relative `media_base`, and there is simply no hint, which is correct rather than a
    # fallback: a preconnect to a host nothing is fetched from is a wasted connection.
    preconnect = ""
    host = str(video_feed().get("media_base") or "")
    m = re.match(r"(https://[^/]+)", host)
    if m:
        preconnect = f'<link rel="preconnect" href="{e(m.group(1))}" crossorigin>\n'

    css = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;background:var(--night);color:var(--body);
font-family:var(--body-face);overscroll-behavior-y:contain}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:3px}
a{color:inherit}

/* ---------- top bar, an overlay so the film keeps the whole screen ---------- */
.topbar{position:fixed;top:0;left:0;right:0;z-index:40;display:flex;align-items:center;
justify-content:space-between;gap:12px;padding:calc(10px + env(safe-area-inset-top)) 16px 10px;
background:linear-gradient(180deg,rgba(8,6,15,.9),rgba(8,6,15,.55) 70%,transparent);
pointer-events:none}
.topbar>*{pointer-events:auto}
.wordmark{display:flex;align-items:center;gap:9px;text-decoration:none;white-space:nowrap;
font-family:var(--mono-face);font-size:12.5px;letter-spacing:.14em;color:var(--snow)}
@media(max-width:520px){.wordmark{font-size:11px;letter-spacing:.1em}}
/* The mark carries classes and no fills of its own, because on every other page the fills
   come from site.css. This page does not load site.css, so it paints them here from the same
   tokens. Without this the Lone Star renders as a black rectangle. */
.wordmark svg{height:17px;width:auto;display:block;flex:none}
.m-blue{fill:var(--flag-blue)}
.m-white{fill:var(--star)}
.m-red{fill:var(--flag-red)}
.m-star{fill:var(--star)}
.f-lit{fill:#FFFFFF;opacity:.55}
.f-shade{fill:var(--flag-blue);opacity:.14}
.navlinks{display:flex;gap:14px;font-family:var(--mono-face);font-size:10.5px;letter-spacing:.12em}
.navlinks a{text-decoration:none;color:var(--mute);padding:6px 2px}
.navlinks a:hover{color:var(--snow)}
.navlinks a.on{color:var(--accent)}
@media(max-width:760px){.navlinks a.hidesm{display:none}}

/* ---------- the feed ---------- */
.feed{height:100dvh;overflow-y:scroll;scroll-snap-type:y mandatory;scrollbar-width:none}
.feed::-webkit-scrollbar{display:none}
.card{position:relative;height:100dvh;scroll-snap-align:start;scroll-snap-stop:always;
display:flex;align-items:center;justify-content:center;background:var(--night)}
/* the 9:16 stage. Full bleed on a phone, a centred column on a wide screen, because a
   letterboxed vertical film on a desktop is worse than an honest column. */
.stage{position:relative;height:100%;aspect-ratio:9/16;max-width:100vw;background:#000;
overflow:hidden}
@media(min-width:700px){.stage{height:min(94dvh,1000px);border-radius:14px;
border:1px solid var(--line);box-shadow:0 30px 80px rgba(0,0,0,.6)}}
.stage video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;background:#000}
.stage .poster{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
transition:opacity .35s}
.stage.playing .poster{opacity:0;pointer-events:none}

/* tap layer */
.tap{position:absolute;inset:0;border:0;background:transparent;cursor:pointer}
.pauseglyph{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%) scale(.8);
width:82px;height:82px;border-radius:50%;background:rgba(8,6,15,.55);border:1px solid var(--line);
display:flex;align-items:center;justify-content:center;opacity:0;
transition:opacity .2s,transform .2s;pointer-events:none}
.card.paused .pauseglyph{opacity:1;transform:translate(-50%,-50%) scale(1)}
.pauseglyph svg{width:33px;height:33px;fill:var(--snow);margin-left:5px}

/* the words over the picture */
.meta{position:absolute;left:0;right:64px;bottom:0;
padding:18px 16px calc(20px + env(safe-area-inset-bottom));
background:linear-gradient(0deg,rgba(8,6,15,.88),rgba(8,6,15,.45) 60%,transparent);
pointer-events:none}
.meta>*{pointer-events:auto}
.kicker{font-family:var(--mono-face);font-size:10px;letter-spacing:.16em;color:var(--accent);
text-transform:uppercase;margin-bottom:6px;display:flex;flex-wrap:wrap;gap:5px 9px}
.kicker .where{color:var(--mute)}
.title{font-family:var(--display-face);font-weight:600;font-size:clamp(19px,4.6vw,25px);
line-height:1.15;color:var(--snow);margin-bottom:7px;text-wrap:balance}
.cap{font-size:13.5px;line-height:1.5;color:var(--body);max-width:52ch;cursor:pointer;
display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.cap.open{-webkit-line-clamp:unset}

/* the right rail */
.rail{position:absolute;right:8px;bottom:calc(86px + env(safe-area-inset-bottom));z-index:5;
display:flex;flex-direction:column;gap:15px;align-items:center}
.rbtn{width:45px;height:45px;border-radius:50%;border:1px solid var(--line);cursor:pointer;
background:rgba(25,21,48,.72);display:flex;align-items:center;justify-content:center;
transition:transform .12s,border-color .12s;backdrop-filter:blur(6px)}
.rbtn:hover{transform:scale(1.08);border-color:var(--accent)}
.rbtn svg{width:21px;height:21px;fill:none;stroke:var(--snow);stroke-width:1.8;
stroke-linecap:round;stroke-linejoin:round}
.rbtn.toast svg{stroke:var(--good)}
.rbtn.busy{opacity:.45}

/* The progress hairline is scaleX only and never touches layout. Paused it becomes a real
   scrubber: the track thickens, a knob appears, and a thumb-sized grab area opens along the
   bottom. That area exists ONLY while the scrubber is up, since a permanent 44px strip would
   swallow every bottom-edge tap meant for play and pause. */
.prog{position:absolute;left:0;right:0;bottom:0;height:3px;background:rgba(237,230,214,.14);
z-index:6;touch-action:none;transition:height .16s,background-color .16s}
.prog i{display:block;height:100%;width:100%;
background:linear-gradient(90deg,var(--deepaccent),var(--accent));
transform:scaleX(0);transform-origin:0 50%;will-change:transform;touch-action:none}
.prog::before{content:"";position:absolute;left:0;right:0;bottom:0;height:0;touch-action:none}
.card.paused .prog::before,.card.scrubbing .prog::before{height:44px}
.card.paused .prog,.card.scrubbing .prog{height:6px;background:rgba(237,230,214,.26)}
.knob{position:absolute;top:50%;left:0;width:15px;height:15px;margin:-7.5px 0 0 -7.5px;
border-radius:50%;background:var(--accent);box-shadow:0 0 0 5px rgba(224,149,106,.22);
opacity:0;pointer-events:none;transition:opacity .16s}
.card.paused .knob,.card.scrubbing .knob{opacity:1}

/* double tap to skip, flashed on the side that was tapped */
.skip{position:absolute;top:50%;transform:translateY(-50%);width:34%;z-index:5;
pointer-events:none;display:flex;flex-direction:column;align-items:center;gap:5px;opacity:0;
transition:opacity .3s;font-family:var(--mono-face);font-size:11px;letter-spacing:.1em;
color:var(--snow)}
.skip.back{left:0}
.skip.fwd{right:0}
.skip.on{opacity:1;transition:opacity .06s}
.skip svg{width:31px;height:31px;fill:var(--snow)}

/* buffering */
.spin{position:absolute;top:50%;left:50%;width:34px;height:34px;margin:-17px 0 0 -17px;z-index:4;
border-radius:50%;border:3px solid rgba(237,230,214,.18);border-top-color:var(--accent);
opacity:0;transition:opacity .25s .2s;pointer-events:none;animation:vspin .8s linear infinite}
.card.buffering .spin{opacity:1}
@keyframes vspin{to{transform:rotate(360deg)}}

/* the sound invitation, up only while the feed is muted */
.unmute{position:fixed;z-index:45;left:50%;transform:translateX(-50%);
top:calc(58px + env(safe-area-inset-top));display:none;align-items:center;gap:8px;
background:rgba(25,21,48,.85);border:1px solid var(--accent);color:var(--snow);cursor:pointer;
font-family:var(--mono-face);font-size:11px;letter-spacing:.1em;padding:9px 16px;
border-radius:99px;backdrop-filter:blur(6px)}
body.feedready.muted .unmute{display:flex}
.unmute svg{width:15px;height:15px;fill:var(--accent)}

/* a mouse has no thumb, so a wide screen gets buttons */
.stepper{position:fixed;right:22px;top:50%;transform:translateY(-50%);z-index:40;
display:none;flex-direction:column;gap:10px}
@media(min-width:900px){body.feedready .stepper{display:flex}}
.stepper button{width:43px;height:43px;border-radius:50%;border:1px solid var(--line);
background:rgba(25,21,48,.72);color:var(--snow);font-size:16px;cursor:pointer}
.stepper button:hover{border-color:var(--accent);color:var(--accent)}

.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.notice{height:100dvh;display:flex;align-items:center;justify-content:center;text-align:center;
padding:0 24px;font-family:var(--mono-face);font-size:12px;letter-spacing:.14em;
line-height:2;color:var(--mute)}
noscript div{padding:40vh 22px 0;text-align:center;font-family:var(--mono-face);
font-size:12px;line-height:2;color:var(--mute)}

/* A reader who asked for less motion gets a still frame and a button, never an autoplay.
   CSS cannot reach media playback, so this only styles the state the script puts the page in. */
@media(prefers-reduced-motion:reduce){
  .stage .poster{transition:none}
  .pauseglyph{transition:none}
  .spin{animation:none}
}
"""

    script = r"""
(async function(){
  var feed = document.getElementById('feed');
  var notice = document.getElementById('notice');
  var calm = window.matchMedia && matchMedia('(prefers-reduced-motion:reduce)').matches;

  var manifest;
  try{ manifest = await (await fetch('videos.json')).json(); }
  catch(err){ notice.textContent = 'THE FEED DID NOT LOAD. TRY A REFRESH.'; return; }

  var base = manifest.media_base || '';
  var vids = (manifest.videos || []).filter(function(v){ return v && v.video; });
  if(!vids.length){ notice.textContent = 'NO FILM HAS SHIPPED YET. THE FIRST ONE APPEARS HERE THE DAY IT DOES.'; return; }

  var abs = function(u){ return /^https?:\/\//.test(u) ? u : base + u; };
  /* Every value below is written into innerHTML, so it is escaped first. A title or a caption
     carrying markup would otherwise run as script on this origin. */
  var esc = function(s){ return String(s == null ? '' : s).replace(/[&<>"']/g, function(ch){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]; }); };

""" + js_feed_date() + r"""  /* A deep link needs a stable handle. The publish step writes `id`; an entry from before it
     did gets one derived from its own date and title, which is stable for that entry. */
  var idOf = function(v, i){
    if(v.id) return String(v.id);
    var slug = String(v.title || '').toLowerCase().replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '').slice(0, 60);
    return (v.date || ('v' + i)) + (slug ? '-' + slug : '');
  };

  /* Source selection. A phone on a frontage road gets the 720p rendition and the jpeg thumb
     when the feed carries them; a wide screen on a healthy connection gets the master. An
     entry published before the renditions existed carries neither, so both fall back. */
  var conn = navigator.connection || {};
  var slowNet = !!(conn.saveData || /2g$/.test(conn.effectiveType || ''));
  var wantFull = window.innerWidth >= 900 && !slowNet;
  var srcOf = function(v){ return (!wantFull && v.video_mobile) ? abs(v.video_mobile) : abs(v.video); };
  var posterOf = function(v){
    var p = (!wantFull && v.poster_thumb) ? v.poster_thumb : v.poster;
    return p ? abs(p) : '';
  };

  var frag = document.createDocumentFragment();
  vids.forEach(function(v, i){
    var card = document.createElement('section');
    card.className = 'card' + (calm ? ' paused' : '');
    card.id = idOf(v, i);
    card.dataset.idx = i;
    var psrc = posterOf(v);
    var where = v.county ? '<span class="where">' + esc(v.county) + ' County</span>' : '';
    card.innerHTML =
      '<div class="stage">' +
        '<video playsinline loop muted preload="none" ' +
          (psrc ? 'poster="' + esc(psrc) + '" ' : '') +
          'data-src="' + esc(srcOf(v)) + '" aria-label="' + esc(v.title || 'Texas AI Dispatch') + '"></video>' +
        (psrc ? '<img class="poster" src="' + esc(psrc) + '" alt="" loading="lazy">' : '') +
        '<button class="tap" type="button" aria-label="Play or pause"></button>' +
        '<div class="pauseglyph" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></div>' +
        '<div class="spin" aria-hidden="true"></div>' +
        '<div class="meta">' +
          '<div class="kicker"><span>Texas AI Dispatch</span><span>' + esc(fmtFeedDate(v.date)) + '</span>' + where + '</div>' +
          '<h2 class="title">' + esc(v.title || '') + '</h2>' +
          (v.caption ? '<p class="cap" title="Tap to expand">' + esc(v.caption) + '</p>' : '') +
        '</div>' +
        '<div class="rail">' +
          '<button class="rbtn mutebtn" type="button" aria-label="Toggle sound">' +
            '<svg viewBox="0 0 24 24"><path class="spk" d="M4 9.5v5h3.5L12 18.5v-13L7.5 9.5H4z"/>' +
            '<path class="wave" d="M15.5 9a4.2 4.2 0 0 1 0 6M18 6.8a7.6 7.6 0 0 1 0 10.4"/></svg>' +
          '</button>' +
          '<button class="rbtn sharebtn" type="button" aria-label="Share this film">' +
            '<svg viewBox="0 0 24 24"><path d="M12 15V4m0 0L8 8m4-4 4 4M5 14v5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-5"/></svg>' +
          '</button>' +
          '<button class="rbtn dlbtn" type="button" aria-label="Download this film">' +
            '<svg viewBox="0 0 24 24"><path d="M12 4v11m0 0-4-4m4 4 4-4M5 14v5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-5"/></svg>' +
          '</button>' +
        '</div>' +
        '<div class="skip back" aria-hidden="true">' +
          '<svg viewBox="0 0 24 24"><path d="M11 6v12L2 12l9-6Zm11 0v12l-9-6 9-6Z"/></svg><span>10s</span></div>' +
        '<div class="skip fwd" aria-hidden="true">' +
          '<svg viewBox="0 0 24 24"><path d="M13 6v12l9-6-9-6ZM2 6v12l9-6L2 6Z"/></svg><span>10s</span></div>' +
        '<div class="prog" aria-hidden="true"><i></i><b class="knob"></b></div>' +
      '</div>';
    var vd = card.querySelector('video');
    vd.addEventListener('waiting', function(){ card.classList.add('buffering'); });
    vd.addEventListener('playing', function(){ card.classList.remove('buffering'); });
    vd.addEventListener('canplay', function(){ card.classList.remove('buffering'); });
    frag.appendChild(card);
  });
  notice.remove();
  feed.appendChild(frag);
  /* THE CONTROLS ARE GATED ON A FEED THAT LOADED. The sound pill and the desktop stepper are
     in the markup so they need no layout shift to appear, and their listeners are attached at
     the bottom of this function. Between those two facts is a window where a failed fetch
     leaves a reader looking at a button that does nothing, which is worse than no button. */
  document.body.classList.add('feedready');

  var cards = Array.prototype.slice.call(feed.querySelectorAll('.card'));
  var soundOn = false;
  var current = null;
  var videoOf = function(c){ return c.querySelector('video'); };

  /* A BOUNDED PRELOAD WINDOW. The current card and the next buffer in full, the previous and
     the one after next hold metadata, and every other card is DETACHED outright, src removed
     and reloaded empty. Without this a reader who flicks through a month of films leaves a
     month of live video elements behind and a phone gives up. */
  function attach(vd, pl){
    vd.preload = pl;
    if(!vd.getAttribute('src')) vd.src = vd.dataset.src;
  }
  function detach(c){
    var vd = videoOf(c);
    if(vd && vd.getAttribute('src')){
      if(!vd.paused) vd.pause();
      vd.removeAttribute('src');
      vd.load();
      c.querySelector('.stage').classList.remove('playing');
      c.classList.remove('buffering');
    }
  }
  function applyWindow(i){
    cards.forEach(function(c, j){
      var d = j - i;
      if(d === 0 || d === 1) attach(videoOf(c), 'auto');
      else if(d === -1 || d === 2) attach(videoOf(c), 'metadata');
      else detach(c);
    });
  }

  function play(c){
    var vd = videoOf(c);
    attach(vd, 'auto');
    vd.muted = !soundOn;
    vd.play().then(function(){
      c.querySelector('.stage').classList.add('playing');
      c.classList.remove('paused');
    }).catch(function(err){
      /* A real refusal, which on a phone in low power mode is the common one, has to leave the
         play glyph up so the poster is not a dead end. An AbortError from a fast flick is noise. */
      if(err && err.name === 'NotAllowedError') c.classList.add('paused');
    });
  }
  function pause(c){ var vd = videoOf(c); if(vd && !vd.paused) vd.pause(); }

  /* The incoming card starts as it crosses 40 percent mid flick, so it is already rolling when
     the snap settles, and it is committed as current at 60 percent. */
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      var c = en.target;
      if(en.intersectionRatio >= 0.6){
        if(current && current !== c) pause(current);
        current = c;
        applyWindow(+c.dataset.idx);
        if(!calm) play(c);
        bindProgress(c);
        history.replaceState(null, '', '#' + c.id);
      }else if(en.intersectionRatio >= 0.4){
        if(c !== current && !calm) play(c);
      }else{
        if(c !== current) pause(c);
      }
    });
  }, {root: feed, threshold: [0, .4, .6]});

  var SKIP = 10;
  function paint(c, f){
    var bar = c.querySelector('.prog i'), kn = c.querySelector('.knob');
    if(bar) bar.style.transform = 'scaleX(' + f + ')';
    if(kn) kn.style.left = (f * 100) + '%';
  }
  function flashSkip(c, dir){
    var el = c.querySelector(dir > 0 ? '.skip.fwd' : '.skip.back');
    if(!el) return;
    el.classList.add('on');
    clearTimeout(el._t);
    el._t = setTimeout(function(){ el.classList.remove('on'); }, 420);
  }
  function nudge(c, secs){
    var vd = videoOf(c);
    if(!vd || !isFinite(vd.duration) || !vd.duration) return;
    vd.currentTime = Math.max(0, Math.min(vd.duration, vd.currentTime + secs));
    paint(c, vd.currentTime / vd.duration);
    flashSkip(c, secs);
  }

  var tapT = 0, tapCard = null, tapWasPlaying = false;
  feed.addEventListener('click', function(ev){
    var tap = ev.target.closest('.tap');
    if(tap){
      var c = tap.closest('.card'), vd = videoOf(c);
      var r = tap.getBoundingClientRect();
      var rel = (ev.clientX - r.left) / r.width;
      var zone = rel < .35 ? -1 : (rel > .65 ? 1 : 0);
      var now = Date.now();
      /* A second tap on the same side inside 320ms UNDOES the play or pause the first one did,
         then seeks. Undoing is what keeps a single tap instant. Waiting 320ms to disambiguate
         would make every pause feel late, which is a worse trade than a brief flicker. */
      if(zone && tapCard === c && now - tapT < 320){
        if(tapWasPlaying){ play(c); } else { vd.pause(); c.classList.add('paused'); }
        nudge(c, zone * SKIP);
        tapT = 0; tapCard = null;
        return;
      }
      tapT = now; tapCard = c; tapWasPlaying = !vd.paused;
      if(vd.paused){ play(c); } else { vd.pause(); c.classList.add('paused'); }
      return;
    }
    var cap = ev.target.closest('.cap');
    if(cap){ cap.classList.toggle('open'); return; }
    var mb = ev.target.closest('.mutebtn');
    if(mb){ setSound(!soundOn); return; }
    var sb = ev.target.closest('.sharebtn');
    if(sb){
      var sc = sb.closest('.card');
      var url = location.origin + location.pathname + '#' + sc.id;
      var title = sc.querySelector('.title').textContent;
      if(navigator.share){
        navigator.share({title: title + ' - Texas AI Docket', url}).catch(function(){});
      }else if(navigator.clipboard){
        navigator.clipboard.writeText(url).then(function(){
          sb.classList.add('toast');
          setTimeout(function(){ sb.classList.remove('toast'); }, 1200);
        }).catch(function(){});
      }
      return;
    }
    var db = ev.target.closest('.dlbtn');
    if(db){
      var dc = db.closest('.card'), dv = videoOf(dc);
      var raw = dv && dv.dataset.src;
      if(!raw || db.classList.contains('busy')) return;
      /* Resolve against the document FIRST, then check the scheme. A bare scheme test rejects a
         relative media_base outright and leaves a dead button. Resolving handles both forms and
         still keeps javascript: and data: out of an href. */
      var src;
      try{ src = new URL(raw, location.href); }catch(err){ return; }
      if(src.protocol !== 'http:' && src.protocol !== 'https:') return;
      src = src.href;
      var name = (String(dc.id || '').replace(/[^a-z0-9_-]/gi, '') || 'texas-ai-dispatch') + '.mp4';
      var save = function(href){
        var a = document.createElement('a');
        a.href = href; a.download = name; a.rel = 'noopener';
        document.body.appendChild(a); a.click(); a.remove();
      };
      /* Blob first, because the download attribute is IGNORED cross origin and a plain link to
         the media host would navigate to the mp4 instead of saving it. The fetch fails only
         when CORS is absent, and then the plain link is still better than a dead button. */
      db.classList.add('busy');
      fetch(src).then(function(r){ return r.ok ? r.blob() : Promise.reject(0); }).then(function(b){
        var u = URL.createObjectURL(b);
        save(u);
        setTimeout(function(){ URL.revokeObjectURL(u); }, 60000);
        db.classList.remove('busy');
        db.classList.add('toast');
        setTimeout(function(){ db.classList.remove('toast'); }, 1400);
      }).catch(function(){ db.classList.remove('busy'); save(src); });
    }
  });

  /* SCRUB. The drag is tracked by pointer id rather than re-derived from the event target on
     every move, because deriving it ends the drag the instant the finger wanders off the strip,
     which on a phone is most of the way through a normal thumb roll. Moves are listened for on
     window for the same reason. Once the finger is down the bar owns the gesture until it lifts. */
  var drag = null, pendingF = -1, seekRaf = 0;
  function fracAt(c, clientX){
    var r = c.querySelector('.prog').getBoundingClientRect();
    return Math.min(1, Math.max(0, (clientX - r.left) / r.width));
  }
  function durOf(c){
    var vd = videoOf(c);
    return (vd && isFinite(vd.duration) && vd.duration) ? vd : null;
  }
  /* Painting is one transform and costs nothing, so it runs on every move and the bar tracks the
     thumb exactly. Assigning currentTime kicks a decoder seek and pointermove fires far faster
     than a phone can serve those, so the seek is coalesced to one a frame. */
  function commitSeek(){
    seekRaf = 0;
    if(!drag || pendingF < 0) return;
    var vd = durOf(drag.card);
    if(vd) vd.currentTime = pendingF * vd.duration;
  }
  function scrub(c, clientX){
    var f = fracAt(c, clientX);
    paint(c, f);
    pendingF = f;
    if(!seekRaf) seekRaf = requestAnimationFrame(commitSeek);
  }
  feed.addEventListener('pointerdown', function(ev){
    var pr = ev.target.closest('.prog');
    if(!pr || drag) return;
    var c = pr.closest('.card');
    drag = {card: c, id: ev.pointerId, bar: pr};
    c.classList.add('scrubbing');
    try{ pr.setPointerCapture(ev.pointerId); }catch(err){}
    scrub(c, ev.clientX);
    ev.preventDefault();
  });
  window.addEventListener('pointermove', function(ev){
    if(!drag || ev.pointerId !== drag.id) return;
    scrub(drag.card, ev.clientX);
    ev.preventDefault();
  }, {passive: false});
  function endScrub(ev){
    if(!drag || ev.pointerId !== drag.id) return;
    var c = drag.card;
    /* Land exactly where the finger left off. The last move may have been coalesced away by the
       frame budget, so the release seeks outright. */
    var vd = durOf(c), f = fracAt(c, ev.clientX);
    if(vd) vd.currentTime = f * vd.duration;
    paint(c, f);
    c.classList.remove('scrubbing');
    try{ drag.bar.releasePointerCapture(drag.id); }catch(err){}
    if(seekRaf){ cancelAnimationFrame(seekRaf); seekRaf = 0; }
    drag = null; pendingF = -1;
  }
  window.addEventListener('pointerup', endScrub);
  window.addEventListener('pointercancel', endScrub);

  function setSound(on){
    soundOn = on;
    document.body.classList.toggle('muted', !on);
    cards.forEach(function(c){ var vd = videoOf(c); if(vd) vd.muted = !on; });
    document.querySelectorAll('.mutebtn .wave').forEach(function(w){ w.style.opacity = on ? 1 : .25; });
    if(on && current && !calm){ var vd = videoOf(current); if(vd.paused) play(current); }
  }
  document.getElementById('unmute').addEventListener('click', function(){ setSound(true); });
  setSound(false);

  /* The hairline is driven by requestVideoFrameCallback on the active film, which is one paint
     aligned update a presented frame and suspends itself while paused. timeupdate is the
     fallback. scaleX never causes layout. */
  var hasRVFC = 'requestVideoFrameCallback' in HTMLVideoElement.prototype;
  var progVd = null, progBar = null, progKnob = null, progId = 0;
  function progTick(){
    if(progVd && progVd.duration){
      var f = progVd.currentTime / progVd.duration;
      progBar.style.transform = 'scaleX(' + f + ')';
      if(progKnob) progKnob.style.left = (f * 100) + '%';
    }
  }
  function progLoop(){
    progTick();
    progId = progVd.requestVideoFrameCallback(progLoop);
  }
  function bindProgress(c){
    var vd = videoOf(c);
    if(vd === progVd) return;
    if(progVd){
      if(hasRVFC && progId) progVd.cancelVideoFrameCallback(progId);
      if(!hasRVFC) progVd.removeEventListener('timeupdate', progTick);
      if(progBar) progBar.style.transform = 'scaleX(0)';
    }
    progVd = vd;
    progBar = c.querySelector('.prog i');
    progKnob = c.querySelector('.knob');
    if(hasRVFC){ progId = vd.requestVideoFrameCallback(progLoop); }
    else{ vd.addEventListener('timeupdate', progTick); }
  }

  function step(dir){
    var i = current ? +current.dataset.idx : 0;
    var t = cards[Math.min(cards.length - 1, Math.max(0, i + dir))];
    if(t) t.scrollIntoView({behavior: calm ? 'auto' : 'smooth'});
  }
  document.getElementById('prev').addEventListener('click', function(){ step(-1); });
  document.getElementById('next').addEventListener('click', function(){ step(1); });
  window.addEventListener('keydown', function(ev){
    if(ev.key === 'ArrowDown' || ev.key === 'PageDown'){ ev.preventDefault(); step(1); }
    if(ev.key === 'ArrowUp' || ev.key === 'PageUp'){ ev.preventDefault(); step(-1); }
    if(ev.key === ' '){
      ev.preventDefault();
      if(current){
        var vd = videoOf(current);
        if(vd.paused){ play(current); } else { vd.pause(); current.classList.add('paused'); }
      }
    }
    /* The keyboard equivalent of the double tap, which is also how seeking reaches anyone who
       cannot use a pointer at all. */
    if(ev.key === 'ArrowRight'){ ev.preventDefault(); if(current) nudge(current, SKIP); }
    if(ev.key === 'ArrowLeft'){ ev.preventDefault(); if(current) nudge(current, -SKIP); }
    if(ev.key.toLowerCase() === 'm'){ setSound(!soundOn); }
  });

  /* Jump before observing, so the observer's first pass attaches the linked card's window
     rather than card zero's. */
  if(location.hash){
    var t = document.getElementById(location.hash.slice(1));
    if(t) t.scrollIntoView();
  }
  cards.forEach(function(c){ io.observe(c); });
})();
"""

    ld = [{
        "@context": "https://schema.org", "@type": "CollectionPage",
        "@id": f"{SITE_URL}/videos/#page",
        "name": f"Videos · {SITE_NAME}", "url": f"{SITE_URL}/videos/",
        "description": desc, "inLanguage": "en-US",
        "isPartOf": {"@id": f"{SITE_URL}/#website"},
        "publisher": {"@id": f"{SITE_URL}/#org"},
    }]

    # ITS OWN SHELL MEANS ITS OWN POLICY. This page does not go through `page()`, so the
    # CSP that every other page inherits there has to be applied here too. It carries the
    # feed loader inline, which is exactly the kind of script the policy exists to pin.
    _doc = f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Videos · {e(SITE_NAME)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE_URL}/videos/">
<meta property="og:title" content="Videos · {e(SITE_NAME)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/videos/">
{og.head_html("../", SITE_URL, SITE_NAME, f"Videos · {SITE_NAME}", desc, "og.png", None)}
{favicon.head_html("../")}
{preconnect}<link rel="preload" href="videos.json" as="fetch" crossorigin>
<link rel="preload" href="../fonts/manrope.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../fonts/fraunces.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../fonts/jetbrainsmono.woff2" as="font" type="font/woff2" crossorigin>
<script type="application/ld+json">{json.dumps(ld, separators=(",", ":"))}</script>
<style>
@font-face{{font-family:Fraunces;src:url(../fonts/fraunces.woff2) format("woff2");
font-weight:100 900;font-display:swap}}
@font-face{{font-family:Manrope;src:url(../fonts/manrope.woff2) format("woff2");
font-weight:200 800;font-display:swap}}
@font-face{{font-family:JBMono;src:url(../fonts/jetbrainsmono.woff2) format("woff2");
font-weight:400 600;font-display:swap}}
:root{{{tokens}
--display-face:Fraunces,Georgia,"Times New Roman",serif;
--body-face:Manrope,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
--mono-face:JBMono,ui-monospace,SFMono-Regular,Menlo,monospace}}
{css}</style>
</head>
<body>

<nav class="topbar" aria-label="Sections">
  <a class="wordmark" href="../">{HOIST}<span>{e(SITE_NAME.upper())}</span></a>
  <div class="navlinks">{nav}</div>
</nav>

<button class="unmute" id="unmute" type="button">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4z"/></svg>
  TAP FOR SOUND
</button>

<div class="stepper" aria-hidden="true">
  <button id="prev" title="Previous film, or the up arrow">&#9650;</button>
  <button id="next" title="Next film, or the down arrow">&#9660;</button>
</div>

<h1 class="sr">Videos</h1>
<main class="feed" id="feed" tabindex="0" aria-label="Video feed">
  <div class="notice" id="notice">LOADING THE FEED</div>
</main>

<noscript><div>The feed needs JavaScript. Every film is also linked from
<a href="../">the front page</a>.</div></noscript>

<script>{script}</script>
</body>
</html>
"""
    return csp.apply(_doc)



def articles_page(runs: list, today: str) -> str:
    """Every carousel this project has shipped, newest first.

    HONEST WHEN EMPTY. Before the first run there is nothing here, and this says so in one
    sentence rather than rendering an empty grid under a confident heading. The same
    sentence is what a reader sees if every run fails for a week, which is the point: the
    page reports the state of the work rather than a state somebody hoped for.
    """
    cards = "".join(f"""<a class="deck" href="{e(r["date"])}/">
  <img src="{RAW}/runs/carousel/{e(r["date"])}/{e(r["cover"])}" width="1080" height="1350"
       loading="lazy" alt="Cover slide, {e(r["title"])}">
  <span class="meta" data-prose="data"><span class="tag">{e(ordinal(
    _dt.date.fromisoformat(r["date"])))}</span><span>{r["slides"]} slides</span></span>
  <h3>{e(r["title"])}</h3>
  {f'<p class="tease">{e(deck_preview(r))}</p>' if deck_preview(r) else ""}</a>""" for r in runs)

    body = f"""
<h1>Articles</h1>
<div class="prose">
  <p>One verified Texas and AI story at a time, drawn as a carousel. Newest first.</p>
</div>
{f'<div class="deckgrid">{cards}</div>' if runs else
 '<p class="gap">No article has shipped yet. The first one appears here the day it does.</p>'}
"""
    return page(title=f"Articles · {SITE_NAME}", depth=1, active="articles/",
                desc="Every article Texas AI Docket has published. One verified Texas and AI "
                     "story at a time.",
                body=body, today=today, canonical="articles/")


def article_page(r: dict, today: str, items: list) -> str:
    """One shipped carousel, as TEXT first and pictures second.

    THIS PAGE USED TO BE EIGHT IMAGES AND A TITLE. Everything the deck said was locked inside
    PNGs, so the page published nothing a search engine could index, nothing a screen reader
    could read, and nothing a reader with images off could see. The words were never missing:
    `copy.json` is the manifest `copy_sync_check` proves the render against, and `claims.json`
    holds every source those words rest on. They were simply never written into the page.

    The shape follows the sibling product's archive, which solved this first. The deck, then the
    story in the deck's own words, then every claim with the source it was checked against, then
    the beats. A reader who never loads an image still gets the whole thing.
    """
    d = _dt.date.fromisoformat(r["date"])
    # BY FILENAME, NEVER BY INDEX. See `load_runs`: generating `slide-{i:02d}.webp` from a count
    # published two broken images and dropped two slides entirely the first time the surviving
    # files were not a contiguous run.
    slides = "".join(
        f'<img src="{RAW}/runs/carousel/{e(r["date"])}/{e(name)}" width="1080"'
        f' height="1350" loading="lazy" alt="Slide {i} of {r["slides"]}">'
        for i, name in enumerate(r["files"], start=1))

    def say(block):
        return "".join(
            f"<blockquote>{e(s['text'])}</blockquote>" if s["quote"]
            else f"<p>{e(s['text'])}</p>" for s in block)

    story = "".join(say(b) for b in r.get("prose") or [])
    if not story:
        story = f'<p>{e(r["hook"] or r["title"])}</p>'

    # EVERY CLAIM, WITH WHAT IT WAS CHECKED AGAINST. The site's promise is that a fact traces to
    # a source a reader can open, and this is the page where the deck's facts live, so this is
    # where that promise has to be redeemable.
    def claim_row(i, c):
        kind = ("PRIMARY" if str(c.get("source_type", "")).startswith("primary") else "REPORT")
        url, title = str(c.get("url") or ""), str(c.get("source_title") or "")
        shown = e(title or url)
        cite = (f'<cite><a href="{e(url)}" rel="nofollow noopener">{shown}</a></cite>'
                if url else f"<cite>{shown}</cite>")
        quote = str(c.get("quote") or "").strip()
        block = f"<blockquote>{e(quote)}</blockquote>" if quote else ""
        checked = ""
        try:
            if c.get("retrieved"):
                checked = f' · checked {e(ordinal(_dt.date.fromisoformat(str(c["retrieved"]))))}'
        except ValueError:
            checked = ""
        return (f'<li><p>{e(str(c.get("text") or ""))}</p>{block}'
                f'<p class="meta" data-prose="data"><span class="tag">{kind}</span> {cite}'
                f'{checked}</p></li>')

    claims = r.get("claims") or []
    claims_html = ""
    if claims:
        rows = "".join(claim_row(i, c) for i, c in enumerate(claims, start=1))
        claims_html = f"""
<h2>What was verified</h2>
<p class="meta" data-prose="data"><span class="num">{len(claims)}</span> claims, each re-fetched
  from its source before this deck shipped.</p>
<ol class="claims">{rows}</ol>"""

    beats, entry = "", ""
    for it in items:
        if it.get("id") == r.get("story"):
            beats = (f'<h2>Beats</h2><p class="meta" data-prose="data">'
                     f'<span class="tag">{e(it.get("topic", ""))}</span></p>')
            entry = (f'<p class="meta" data-prose="data">The record entry for this decision is '
                     f'<a href="../../item/{e(it["id"])}/">{e(it["title"])}</a>.</p>')
            break

    body = f"""
<article>
<h1>{e(r["title"])}</h1>
<p class="meta" data-prose="data"><span class="tag">Published {e(ordinal(d))}</span>
  <span>{r["slides"]} slides</span></p>

<h2>The deck</h2>
<div class="slides">{slides}</div>

<h2>The story</h2>
<div class="prose">{story}{entry}</div>
{claims_html}
{beats}
<p class="meta" data-prose="data"><a href="../">Every article</a></p>
</article>
"""
    flat = [s["text"] for b in (r.get("prose") or []) for s in b if not s["quote"]]
    # THE FIRST SENTENCE IS NOT A DESCRIPTION. This took `flat[0]` and stopped, so an article
    # opening "August 7th came and went." shipped a twenty-five character description, which
    # is what a search result then had to sell itself with. Sentences are added until there is
    # enough to read, and the cut lands on a sentence boundary rather than mid-word.
    desc = ""
    for sentence in (flat or [r["title"]]):
        nxt = (desc + " " + " ".join(sentence.split())).strip()
        if desc and len(nxt) > 160:
            break
        desc = nxt
        if len(desc) >= 110:
            break
    desc = desc[:180]

    # THE ARTICLE SAYS WHAT IT IS. These three pages are the only reporting on the site and
    # they were the only pages with no schema of their own, no article date, and the generic
    # site card on every share. They are also the pages most likely to answer a topical
    # question, which is exactly the case where a crawler needs to be told what it is holding.
    art_url = f'{SITE_URL}/articles/{r["date"]}/'
    story_item = next((i for i in items if i.get("id") == r.get("story")), None)
    item_url = f'{SITE_URL}/item/{story_item["id"]}/' if story_item else None
    card = f'og/article-{r["date"]}.png'
    extra_ld = [
        schema.article_node(SCHEMA_CTX, r, desc, f"{SITE_URL}/{card}", item_url),
        schema.breadcrumbs(SCHEMA_CTX, [("Texas AI Docket", ""), ("Articles", "articles/"),
                                        (r["title"], f'articles/{r["date"]}/')]),
    ]
    return page(title=f'{r["title"]} · {SITE_NAME}', depth=2, active="articles/",
                desc=desc, body=body, today=today, extra_ld=extra_ld,
                og_image=card, og_alt=r["title"], og_type="article",
                canonical=f'articles/{r["date"]}/')


def deck_preview(r: dict, sentences: int = 2, budget: int = 210, floor: int = 12) -> str:
    """The deck's own opening lines, for a card that would otherwise carry a title and a gap.

    WHAT WAS THERE AND WHY IT WENT BLANK. The card printed `copy.json`'s top level `hook`, which
    does not exist, so it rendered an empty paragraph. The repair pointed it at the title of the
    DECISION the deck is about, which is real prose and correctly gated, and which is empty on
    any run whose `story` is empty. Two of the three shipped runs carry no story, so the front
    page and the articles index both ended up showing a headline, two buttons and nothing in
    between. A card that says only what it is called is not a preview.

    THE DECK'S OWN WORDS ARE THE PREVIEW, and they are safe to publish here for the same reason
    the article page publishes them. Every figure in them traces to that run's claims, and
    `_run_numerals` hands exactly those to whichever page renders them. The `tease` field is one
    sentence, which is what made the articles index thin in the first place, so this reads the
    opening slide instead and takes whole sentences up to a budget.

    QUOTED BLOCKS ARE SKIPPED. A quotation needs its attribution beside it to be honest, a card
    has no room for one, and house style exempts quoted material from rules this text is being
    shown under. The first slide with prose of its own supplies the preview, so a deck that
    opens on a quote is previewed by the words around it rather than by somebody else's.

    A SENTENCE COUNT IS NOT A LENGTH, which is the third way this card has gone thin and the
    first that was nobody's typo. Two sentences is the SHAPE the card wants. It guarantees
    nothing about how much gets said, because a deck is free to open on two short ones, and on
    August 27th one opened "Two releases. Neither names a room." Six words. The card was a
    headline, two buttons and a shrug, which is the same page the two earlier repairs were
    written to stop, reached by a route neither of them was looking at.

    So the cap is a floor as well. `sentences` is where this stops IF what it has is already
    worth reading, and it keeps taking whole sentences until `floor` words are in hand. The
    material is nearly always right there: that deck's slide one carried three more sentences
    the cap was throwing away. `budget` is still the only ceiling, so a deck that genuinely has
    little to say gets a short card rather than a long one padded out of the next slide.
    """
    picked: list[str] = []
    for slide in (r.get("prose") or []):
        for block in slide or []:
            if (block or {}).get("quote"):
                continue
            text = " ".join(str((block or {}).get("text") or "").split())
            if text:
                picked.append(text)
        if picked:
            break
    joined = " ".join(picked)
    if not joined:
        return " ".join(str(r.get("tease") or "").split())

    out, used = [], 0
    for part in re.split(r"(?<=[.!?])\s+", joined):
        if not part:
            continue
        # WHOLE SENTENCES ONLY. A preview cut mid clause reads as a fault rather than as a
        # taste, and the budget is a ceiling on what gets in rather than a place to chop.
        if out and used + len(part) > budget:
            break
        out.append(part)
        used += len(part) + 1
        if len(out) >= sentences and len(" ".join(out).split()) >= floor:
            break
    return " ".join(out)


def latest_article(runs: list, items: list) -> str:
    """The newest carousel, baked at build time.

    BAKED RATHER THAN FETCHED, unlike the video below it, and the difference is where the
    data lives. The runs are in this repository, so the build already knows them and a
    reader with script off still sees the article. The video feed is written by another
    repository on its own schedule, so the build's answer goes stale between rebuilds and
    has to be re-read in the page.

    Renders nothing at all when nothing has shipped. A section that explains its own
    emptiness is worse than a section that is not there.
    """
    if not runs:
        return ""
    r = runs[0]

    # WHAT THE CARD SAYS BESIDE THE COVER, and why it is not the deck's own words.
    #
    # This printed `copy.json`'s top level `hook`, which does not exist: hooks are per slide, so
    # the card carried a title and an empty paragraph. A reader saw "Terafab, Grimes County" and
    # nothing else, which says where but not what.
    #
    # The text comes from the DECISION the deck is about, not from the deck. `copy.json` names
    # its story, that item is already on this site, and its summary is already through the
    # numeral gate, the narration gate and the house style gate. Lifting a slide's prose here
    # instead would put figures on the front page that this build never computed, which is the
    # one thing the compute-not-generate law does not bend on.
    # THE ITEM'S TITLE, NOT THE FIRST SENTENCE OF ITS SUMMARY, and the reason is dates.
    #
    # These summaries open by dating the announcement, so the card read "August 16th" in its
    # own tag and then "Governor Greg Abbott announced on August 6th, 2026" in the paragraph
    # underneath. Two bare dates a line apart, meaning different things, with nothing saying
    # which was which. A reader cannot tell whether the story is ten days old or the page is.
    #
    # The item title says what happened without dating it, so the only date on the card is the
    # one in the tag, and the tag now says what that date IS.
    # The decision's title reads well and is empty on any run with no `story`, which is most of
    # them, so it is the SECOND choice now rather than the only one. See `deck_preview`.
    blurb = deck_preview(r)
    if not blurb:
        for it in items:
            if it.get("id") == r.get("story"):
                blurb = " ".join(str(it.get("title") or "").split())
                break

    story_link = (f'<a href="item/{e(r["story"])}/">the decision it is about</a>'
                  if r.get("story") else "")

    return f"""
<section data-reveal>
  <h2 data-voice="house">Our latest article</h2>
  <div class="latest">
    <a class="cover" href="articles/{e(r["date"])}/"><img
      src="{RAW}/runs/carousel/{e(r["date"])}/{e(r["cover"])}"
      width="1080" height="1350" loading="lazy"
      alt="Cover slide, {e(r["title"])}"></a>
    <div>
      <p class="meta" data-prose="data"><span class="tag">Published {e(ordinal(
        _dt.date.fromisoformat(r["date"])))}</span>
        <span>{r["slides"]} slides</span></p>
      <h3>{e(r["title"])}</h3>
      <p>{e(blurb)}</p>
      <div class="ctarow">
        <a class="cta ghost" href="articles/{e(r["date"])}/">Read it</a>
        {story_link and f'<a class="cta ghost" href="item/{e(r["story"])}/">The record entry</a>'}
        <a class="cta ghost" href="articles/">Every article</a>
      </div>
    </div>
  </div>
</section>"""


def latest_video() -> str:
    """The newest Dispatch, filled in by the page from the feed it fetches.

    THE SKELETON IS BAKED AND THE CONTENT IS NOT, because `docs/videos/videos.json` belongs
    to `TexasAIDispatch` and is appended to on a schedule this build knows nothing about. A
    video that ships an hour after a rebuild would sit invisible until the next one, which
    for a daily feed is most of its life.

    HIDDEN UNTIL IT HAS SOMETHING. The section starts `hidden` and is only revealed once a
    video is actually in the feed, so a reader never meets a heading over an empty frame,
    and the page is correct on the day the feed does not exist yet.

    The file only loads when the section scrolls into view. A muted autoplaying video at the
    top of a page costs a reader on a county road their data before they have chosen to
    watch anything.
    """
    return """
<section id="homevid" data-reveal hidden>
  <h2 data-voice="house">Our latest video</h2>
  <div class="latest">
    <!-- CONTROLS, ALWAYS. A roughly 60 second film looping forever beside the copy with no
         pause, stop or hide is a WCAG 2.2.2 failure, and `prefers-reduced-motion` cannot
         reach media playback from CSS. The reader gets a control and the script below asks
         before it starts anything. -->
    <div class="vidwrap"><video id="hv" muted playsinline loop controls preload="none"
      aria-label="The latest Texas AI video"></video></div>
    <div>
      <p class="meta" data-prose="data"><span class="tag" id="hvdate"></span></p>
      <h3 id="hvtitle"></h3>
      <p id="hvcap"></p>
      <div class="ctarow"><a class="cta ghost" href="videos/">Every video</a></div>
    </div>
  </div>
</section>
<script>
(function(){
  var sec=document.getElementById('homevid');
  if(!sec||!window.fetch)return;""" + js_feed_date() + """
  fetch('videos/videos.json').then(function(r){return r.json()}).then(function(m){
    var base=m.media_base||'';
    var vs=(m.videos||[]).filter(function(v){return v&&v.video});
    /* The counter re-reads the same fetch, so a video that landed after the last rebuild
       is counted the moment anybody loads the page. */
    var st=document.getElementById('vidstat');
    if(st&&vs.length){var n=vs.length;
      st.querySelector('.n').textContent=(n<10?'0':'')+n;}
    if(!vs.length)return;
    var v=vs[0], abs=function(u){return /^https?:\/\//.test(u)?u:base+u};
    var el=document.getElementById('hv');
    /* The thumb and the rendition when the publish step made them, the masters when it did
       not. This block is one frame and one film beside a paragraph, so it never needs the
       845 KB poster or the 3.5 Mbit master, and an entry from before the renditions existed
       still works. */
    var p=v.poster_thumb||v.poster;
    if(p)el.poster=abs(p);
    el.dataset.src=abs(v.video_mobile||v.video);
    document.getElementById('hvtitle').textContent=v.title||'';
    document.getElementById('hvcap').textContent=v.caption||'';
    document.getElementById('hvdate').textContent=fmtFeedDate(v.date);
    sec.hidden=false;
    var io=new IntersectionObserver(function(es){es.forEach(function(en){
      if(!en.isIntersecting)return;
      // AUTOPLAY ONLY IF NOBODY ASKED FOR LESS MOTION. The source still loads either way, so
      // pressing play is instant. Reduced motion is a request about movement, and a looping
      // film is the largest piece of movement on the page.
      if(!el.src){
        el.src=el.dataset.src;
        var calm=window.matchMedia&&window.matchMedia('(prefers-reduced-motion:reduce)').matches;
        if(!calm){var q=el.play();if(q&&q.catch)q.catch(function(){});}
      }
      io.disconnect();})},{rootMargin:'200px'});
    io.observe(sec);
  }).catch(function(){});
})();
</script>"""


def scan_teaser() -> str:
    """The Bottleneck Scanner's homepage front door.

    THE SIBLING PUTS THIS SECOND, directly under the hero. Here it is LAST, on the owner's call,
    and the placement is the argument. That site leads with a free tool. This one leads with a
    record, and a record that opens by selling something is a record that has told you what it
    is for. Somebody who has read down the whole page is also somebody who might want the scan.

    IT WEARS THE ASK BOX'S SHELL. This shipped as a `.leadform`, which is the stacked grid the
    contact and services pages use: a square cornered field at 34rem with a square button under
    it, in a full width section, a few screens below a full width rounded composer. Two form
    shapes on one page and neither explains the other.

    So the shell is now `.composer`, the same class the ask box wears, and the difference is the
    control: an arrow where the placeholder already said what the box does, a word where it has
    to name its own action. Shared as a class and not copied, because a shape written out twice
    is a shape that is wrong in both places at once.

    NO JS AND NO CAPTCHA HERE. The single field GETs to the scan page, which prefills it and runs
    the real flow behind its own captcha. A second Turnstile widget on the homepage would load a
    third party script on every visit to a page nobody came here to submit a form on.

    NO DIGITS, deliberately, same as the scan page. `numeral_lint` refuses a numeral the build
    did not compute, and "about twenty minutes" is a claim nobody measured.

    THE QUESTION IS THE READER'S, SO IT IS IN THEIR VOICE. The heading used to be "Would AI
    actually help your business", which is the record asking a prospect a question, and it read
    like a lead capture because that is the grammar of one. The question people actually have is
    first person, and `data-voice="reader"` is the existing, deliberate exemption for exactly
    that: the same mechanism the ask box's starter questions use. It does NOT license the record
    to speak as "we" anywhere else in this section, and it does not here.

    THE CREW IS NAMED BECAUSE IT IS REAL. Four agents run in the scanner repo and each has one
    job: `footprint-analyst`, `industry-scout`, `feasibility-mapper`, `scan-critic`. Describing
    what they each do is both the most futuristic thing this section can say and the most
    checkable, which is the only kind of impressive this site is allowed to be. The wording of
    each line is taken from that agent's own description, so it stays true by construction and a
    reader who later reads the report recognises the machinery.

    NOT COUNTED, deliberately. "Four agents" would be a figure about our own system that goes
    stale the day a fifth is added, and the page states no figures at all for the same reason
    the scan page does not: every number this section wants is a promise, not a measurement.
    """
    return """
<section data-reveal id="scan">
  <h2 class="scanq" data-voice="reader"><span>Would AI actually do anything for my business?</span></h2>
  <p class="scanlede">Drop your url in and an agent team goes to work on it.</p>
  <form class="composer scanform" action="scan/" method="get">
    <label class="vh" for="scan-url">Your website</label>
    <input type="text" name="url" id="scan-url" required placeholder="yourbusiness.com"
      autocomplete="url" inputmode="url">
    <button class="cta solid" type="submit">Run it</button>
  </form>
  <p class="chainlab">The agents on your run</p>
  <ol class="chain">
    <li><b>Footprint</b><span>your pages, cited</span></li>
    <li><b>Industry</b><span>what others already tried</span></li>
    <li><b>Feasibility</b><span>the lowest honest rung</span></li>
    <li><b>Critic</b><span>defaults to rejecting it</span></li>
  </ol>
  <p class="scanfoot">Free. One report. Every line links to the page it came from.</p>
</section>
"""


def home(items: list, today: str) -> str:
    proj = dk.project(items, today)
    act = proj["actionable_now"]
    lit = {c for it in items for c in (it.get("geography") or {}).get("counties") or []}
    svg = texas_map.render(lit=lit, links=county_links(items, today, 0),
                           counts=proj["by_county"])

    n_counties = len(lit)
    n_items = proj["counts"]["items"]
    n_claims = proj["counts"]["claims"]
    # The front page's index of the beats. Its figures are authorised by the same call that
    # renders them, which is why it hands back both.
    covers_html = covers_section(items, today)[1]
    runs = load_runs()
    n_videos = video_count()

    # THE LIVE ACTION RAIL. The old deadline cards were complete but arrived after the ask box
    # and the map, more than a phone screen below the headline. That made the page advertise a
    # count of open doors before it showed any of them. The same verified projection now supplies
    # a compact rail inside the hero, ordered by the date arithmetic in `dk.project`, so the most
    # perishable public opportunity is the first useful thing a reader meets.
    #
    # THREE ROWS IS A PREVIEW, NOT A SECOND RECORD. It keeps the hero finite if many agencies open
    # windows at once. The participation guide below the rows is the route to the full record.
    # Every date remains a `<time>` with its ISO value, every figure is computed, and the full
    # docket title stays in the document even though the visual treatment clamps it on small
    # screens. `data-prose="data"` narrows punctuation-density checks around those official titles
    # without weakening the date or forbidden-character checks.
    action_rows = []
    for a in act[:3]:
        days = a["days_left"]
        remaining = ("Closes today" if days == 0 else
                     f'{days} {"day" if days == 1 else "days"} left')
        state = "open" if days > 7 else "soon"
        state_label = "Open to you" if days > 7 else "Closing soon"
        action_rows.append(
            f'<li><a class="open-now-item {state}" href="item/{e(a["id"])}/">'
            f'<span class="open-now-date">'
            f'<time datetime="{e(a["closes"])}">{e(short_date(a["closes"]))}</time>'
            f'<span>{e(remaining)}</span></span>'
            f'<span class="open-now-copy"><span class="open-now-state">{state_label}</span>'
            f'<span class="open-now-title">{e(a["title"])}</span></span>'
            f'<span class="open-now-go" aria-hidden="true"></span></a></li>')
    action_rows_html = "".join(action_rows)

    if action_rows_html:
        open_now = f"""
  <aside class="open-now" id="open-now" aria-labelledby="open-now-title" data-prose="data">
    <div class="open-now-head">
      <p class="open-now-kicker"><span aria-hidden="true"></span>Open now</p>
      <p class="open-now-total"><span class="num">{len(act):02d}</span> verified</p>
    </div>
    <h2 id="open-now-title">Deadlines you can still meet</h2>
    <p class="open-now-intro">The closest verified public comment deadlines in the record.</p>
    <ol class="open-now-list">{action_rows_html}</ol>
    <a class="open-now-more" href="questions/taking-part/">See every way to take part</a>
  </aside>"""
    else:
        open_now = """
  <aside class="open-now empty" id="open-now" aria-labelledby="open-now-title">
    <div class="open-now-head">
      <p class="open-now-kicker checked"><span aria-hidden="true"></span>Checked today</p>
    </div>
    <h2 id="open-now-title">No comment window is open</h2>
    <p class="open-now-intro">Windows are checked every day. The next verified opening will appear here.</p>
    <a class="open-now-more" href="record/">Browse the full docket</a>
  </aside>"""

    # THE STAT ROW COUNTS WHAT THIS PROJECT HAS PUBLISHED, plus the one number a reader can
    # act on. It used to count quoted sources and counties touched, which are facts about the
    # record's internals rather than about the work: a reader has no use for 55 quotes and no
    # way to want a 56th. Articles and videos are the things that exist because this ran, and
    # the open doors are the reason to come back. All four are computed at build.
    #
    # `id="vidstat"` is read again at runtime. The video feed is appended to by another
    # repository on its own schedule, so a video that lands after today's build leaves this
    # number one behind until the next one. The front page re-reads the same feed it already
    # fetches for the latest-video block, so the figure is right whenever the page is loaded,
    # and the built number stays as the answer with script off.
    # A COUNTER THAT READS ZERO IS AN EMPTY SHELF, NOT A FACT WORTH THE FRONT PAGE.
    #
    # This row printed "00 ARTICLES WRITTEN" and "00 VIDEOS PUBLISHED" beside "58 DECISIONS
    # TRACKED", so half of it advertised nothing at all on a page whose whole argument is that
    # the record is substantial. Zero padded, "00" also reads as a broken widget rather than a
    # count. Nothing is hidden by leaving it out: both sections are in the navigation and a
    # reader who wants them can go and find them empty, honestly.
    #
    # So the row is a PRIORITY LIST and takes the first four that have something in them. The
    # published work leads once it exists, because a daily product proving it ships daily is
    # the strongest thing this row can say, and it comes back on its own the day the first
    # article lands rather than needing anybody to remember this rule.
    #
    # SOURCES CITED SITS BESIDE DECISIONS TRACKED, and the row takes five rather than four.
    # It used to be sixth of six behind a cap of four, which meant the figure never once
    # rendered. That was survivable while the sentence under "What this is" carried it, and
    # that section came off on 2026-08-21 as something a returning reader no longer needs.
    # Taking the section without moving the number would have quietly deleted the only count
    # on this page that says the record is SOURCED rather than merely long, which is the whole
    # claim the project rests on. The two belong next to each other because one qualifies the
    # other: sixty four decisions is a size, and sixty four decisions behind two hundred and
    # eighty three quoted sources is an argument.
    candidates = [
        (len(runs), "Articles written", False, "", ""),
        (n_videos, "Videos published", False, ' id="vidstat"', ""),
        (n_items, "Decisions tracked", False, "", ""),
        (n_claims, "Sources cited", False, "", ""),
        (len(act), "Doors open to you", True, "", "#open-now"),
        (n_counties, "Counties named", False, "", ""),
    ]
    stat_parts = []
    for v, label, hot, attrs, href in [c for c in candidates if c[0]][:5]:
        content = (f'<span class="n{" hot" if hot else ""}">{v:02d}</span>'
                   f'<span class="l">{e(label)}</span>')
        stat_parts.append(f'<a class="stat" href="{href}"{attrs}>{content}</a>' if href else
                          f'<div class="stat"{attrs}>{content}</div>')
    stats = "".join(stat_parts)

    body = f"""
<section class="hero rise">
  {telemetry(today)}
  <h1>AI is coming <em>South</em>.</h1>
  <p class="herolede">Every AI decision in Texas and the source behind it.</p>
  <div class="ctarow">
    <a class="cta solid" href="record/">The docket</a>
    <a class="cta ghost" href="grid/">The grid</a>
  </div>
{open_now}
  <div class="statrow">{stats}</div>
</section>

{ask_box(items, today)}

<section data-reveal>
  <h2>Where</h2>
  <div class="prose"><p>The lit counties are the ones this record currently touches,
  <span class="num">{n_counties}</span> of
  <span class="num">{_place_facts()["counties"]}</span>.</p></div>
  {svg}
  <p class="mapread" id="mapread" role="status" aria-live="polite" data-prose="data"></p>
  <button type="button" class="mapreset" id="mapreset" hidden>Show all of Texas</button>
</section>

{covers_html}

{latest_article(runs, items)}

{latest_video()}

{scan_teaser()}
"""
    # THE TITLE TAG IS THE HIGHEST WEIGHTED THING ON THE PAGE and this spent it on the brand
    # alone. The brand stays first, so the query "Texas AI Docket" still matches exactly, and
    # the half that was empty now says what the site is for every query that is not the name.
    # Same words as the hero lede, deliberately: a title that promises one thing and a page
    # that opens on another is the mismatch a reader bounces off.
    return page(title=f"{SITE_NAME} · Every AI decision in Texas and the source behind it",
                depth=0, active="", home_page=True,
                desc=("A fact-checked record of AI decisions in Texas. Who decided, by when, "
                      "and whether you can still comment."),
                body=body, today=today, canonical="",
                extra_css="home.css",
                # THE DATASET NODE THE WHOLE RECORD HANGS OFF. Every one of the 58 Reports says
                # it `isPartOf` this `@id`, so the node has to exist somewhere or all 58
                # references dangle. It is emitted here AND on `/record/`, which is legal and
                # is not duplication in the sense that matters: both come from one function, so
                # the two can never disagree. The homepage is where a data consumer lands.
                # NO BREADCRUMB HERE. The front page is the root of the trail, so a trail on it
                # would be a list of one, which says nothing and is the kind of markup added
                # for the sake of having markup.
                extra_ld=[{"@context": "https://schema.org",
                           **schema.dataset_node(SCHEMA_CTX, items, today)}])



__all__ = ['videos_page', 'articles_page', 'article_page', 'deck_preview', 'latest_article', 'latest_video', 'scan_teaser', 'home']

