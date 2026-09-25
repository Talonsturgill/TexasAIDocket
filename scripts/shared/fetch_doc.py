#!/usr/bin/env python3
"""fetch_doc.py — fetch a web document into the run's own scratch and read its text.

WHY THIS EXISTS

On 2026-09-25 the daily run needed the text of a PDF, a TxDMV handout on SB 2807. WebFetch saved
the file where Claude Code keeps tool results, under `~/.claude/projects/<project>/tool-results/`,
and the run copied it out with a shell command so it could extract the text. Every path under a
`.claude` directory is a protected path. Claude Code asks a human before any write to one in
every mode a routine can run in, and the dialog named the file being copied as the file being
edited. It was raised at 06:53 UTC and nobody was there to answer it, so the run stopped.

Nothing told the run how to read a PDF, so it improvised, and the improvisation went through a
directory it must never touch. This is the route that needs no approval at all: one ordinary
download into `out/<date>/tmp/src/`, inside the working tree, and the text beside it.

    python3 scripts/shared/fetch_doc.py <url>
    python3 scripts/shared/fetch_doc.py <url> --name txdmv_sb2807 --chars 8000
    python3 scripts/shared/fetch_doc.py --self-test

It writes `<name>.<ext>` (the bytes exactly as served, `<name>.source.txt` for plain text so the
bytes and the text never share a path), `<name>.txt` (the text, always UTF-8) and
`<name>.meta.json` (the url, the final url after redirects, the status, the content type, the
size, the sha256 and the fetch time), then prints where they are and the opening of the text.
`--date` is a calendar date and the scratch directory is checked to sit under `out/`.

IT ASKS THE CRAWL BOUNDARY FIRST, AND ON EVERY REDIRECT. `scripts/shared/crawl_boundary.py` reads
the boundary `knowledge/shared/SOURCES_REGISTRY.md` states, and a url it refuses is never
requested. The first version of this file skipped that, and the session that wrote it proved the
cost in its own test by fetching two bills from `capitol.texas.gov/tlodocs/`, a path the registry
puts off limits because robots.txt disallows it. Codex caught it in review the same hour. A
registry that cannot be read refuses everything, because a boundary nobody could parse is not a
boundary that allows. And a url the checker has NO rule for is not thereby permitted: the routine
still reads the registry before any fetch, as it always has.

EXIT CODES, read by exit code and never by the last line

  0  fetched, and there is text to read
  1  not fetched: an HTTP error, a refused connection, a timeout, or a file over the size cap
  2  fetched, and no text came out of it. A scanned PDF is the usual case, and so is a PDF whose
     every page failed to extract. The bytes are saved, so the Read tool can look at the pages.
  3  refused by the crawl boundary, before any request, or on a redirect into it. Nothing saved.

A CLAIM STILL TRACES TO THE SOURCE URL, NEVER TO THIS FILE. `out/` is scratch and dies with the
container. The saved copy is for reading and quoting, and the claims file cites the url.
"""
from __future__ import annotations

import argparse
import codecs
import datetime as _dt
import hashlib
import html
import io
import json
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import crawl_boundary  # noqa: E402  the one reader of the registry's boundary

REPO_ROOT = Path(__file__).resolve().parents[2]
BRAND_YAML = REPO_ROOT / "config" / "brand.yaml"
TIMEOUT = 60
MAX_BYTES = 50 * 1024 * 1024

OK, UNREACHABLE, NO_TEXT, REFUSED = 0, 1, 2, 3

_TAG = re.compile(r"<(script|style|noscript)\b.*?</\1>", re.S | re.I)
_ANY = re.compile(r"<[^>]+>")
_WS = re.compile(r"[ \t\f\v]+")
_BLANKS = re.compile(r"\n\s*\n+")
_CHARSET = re.compile(r"charset\s*=\s*['\"]?([A-Za-z0-9._:-]+)", re.I)
_XML_ENC = re.compile(r"<\?xml[^>]*\bencoding\s*=\s*['\"]([A-Za-z0-9._:-]+)", re.I)
# UTF-32 first, because its little endian mark begins with UTF-16's.
_BOMS = ((codecs.BOM_UTF32_LE, "utf-32-le"), (codecs.BOM_UTF32_BE, "utf-32-be"),
         (codecs.BOM_UTF8, "utf-8"), (codecs.BOM_UTF16_LE, "utf-16-le"),
         (codecs.BOM_UTF16_BE, "utf-16-be"))


class Refused(Exception):
    """A url the crawl boundary refuses, met before a request or on a redirect."""


def site() -> str:
    """The public host, read from `config/brand.yaml` rather than kept as a copy here.

    CLAUDE.md's account of the public URL is a list of surfaces that each kept their own copy of
    this string, User-Agents among them, and went stale together. So this reads the one value,
    `visual.constellation.site`, and a brand file without it is an error rather than a fallback.
    """
    import yaml  # PyYAML, in requirements.txt

    value = (((yaml.safe_load(BRAND_YAML.read_text(encoding="utf-8")) or {})
              .get("visual") or {}).get("constellation") or {}).get("site")
    if not value:
        raise SystemExit(f"fetch_doc: {BRAND_YAML} has no visual.constellation.site")
    return str(value).strip()


def user_agent() -> str:
    return f"TexasAIDocket/1.0 source fetch (+https://{site()})"


def run_date() -> str:
    """The run's date from its branch, `claude/daily-<date>`, or today in UTC."""
    try:
        ref = (REPO_ROOT / ".git" / "HEAD").read_text(encoding="utf-8")
        m = re.search(r"claude/daily-(\d{4}-\d{2}-\d{2})", ref)
        if m:
            return m.group(1)
    except OSError:
        pass
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")


def safe_name(name: str) -> str:
    """A bare file name stem. Separators and dots at the ends are taken out, so no name, given or
    derived, can point a write anywhere but the scratch directory."""
    n = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._-")[:80]
    return n or "doc"


def slug(url: str) -> str:
    """A name from the url's last path segment, with a short hash so two documents both called
    `index` or `download` do not overwrite each other."""
    path = urllib.parse.urlparse(url).path.rstrip("/")
    stem = Path(urllib.parse.unquote(path)).stem or urllib.parse.urlparse(url).netloc or "doc"
    return f"{safe_name(stem.lower())[:60]}_{hashlib.sha256(url.encode()).hexdigest()[:8]}"


def is_pdf(body: bytes, content_type: str) -> bool:
    return body[:5] == b"%PDF-" or "application/pdf" in content_type.lower()


def decode(body: bytes, content_type: str, sniff: bool) -> str:
    """Bytes to text in the charset the server declared, then the one the document declares,
    then UTF-8. Decoding everything as UTF-8 turned a windows-1252 page's quotation marks into
    replacement characters, which is a quote this project would then have misquoted."""
    # A BYTE ORDER MARK OUTRANKS EVERY DECLARATION, which is the order the encoding standard
    # gives. UTF-16 XML read as ASCII hides its own `encoding=` behind NUL bytes, so without this
    # it fell through to UTF-8 and came out mangled with an exit of 0 (Codex, PR 361).
    for bom, codec in _BOMS:
        if body.startswith(bom):
            return body[len(bom):].decode(codec.replace("-sig", ""), "replace")
    m = _CHARSET.search(content_type or "")
    if not m and sniff:
        head = body[:4096].decode("ascii", "replace")
        m = _XML_ENC.search(head) or _CHARSET.search(head)
    name = m.group(1) if m else "utf-8"
    try:
        codecs.lookup(name)
    except LookupError:
        name = "utf-8"
    return body.decode(name, "replace")


def _reader(body: bytes):
    from pypdf import PdfReader  # installed by bootstrap.sh and requirements-ci.txt

    return PdfReader(io.BytesIO(body))


def pdf_text(body: bytes) -> tuple[str, int, int]:
    """(text, pages, characters actually extracted). Each page is marked so a quote can be found
    again by page. A page that fails leaves a marker in the text and adds nothing to the count,
    so a PDF whose every page failed reads as having no text, which is what it has."""
    reader = _reader(body)
    parts, real = [], 0
    for i, page in enumerate(reader.pages, 1):
        try:
            t = (page.extract_text() or "").strip()
            real += len(re.sub(r"\s+", "", t))
        except Exception as e:  # noqa: BLE001  one bad page must not lose the rest
            t = f"[page {i} could not be read: {type(e).__name__}]"
        parts.append(f"--- page {i} ---\n{t}")
    return "\n\n".join(parts), len(reader.pages), real


def html_text(raw: str) -> str:
    t = _TAG.sub(" ", raw)
    t = re.sub(r"<(br|p|div|li|tr|h[1-6])\b[^>]*>", "\n", t, flags=re.I)
    t = html.unescape(_ANY.sub(" ", t))
    t = _WS.sub(" ", t)
    return _BLANKS.sub("\n\n", "\n".join(line.strip() for line in t.splitlines())).strip()


class _BoundaryRedirects(urllib.request.HTTPRedirectHandler):
    """Follows a redirect only when the crawl boundary does not refuse where it points."""

    def __init__(self, boundary: list[dict]):
        super().__init__()
        self.boundary = boundary

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        why = crawl_boundary.forbidden(newurl, self.boundary)
        if why:
            raise Refused(f"a {code} redirect to {newurl}: {why}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url: str, boundary: list[dict], opener=None) -> dict:
    """{state, status, final_url, content_type, body}. Never raises for a network failure."""
    req = urllib.request.Request(url, headers={"User-Agent": user_agent(), "Accept": "*/*"})
    op = opener or urllib.request.build_opener(_BoundaryRedirects(boundary)).open
    try:
        with op(req, timeout=TIMEOUT) as r:
            body = r.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                return {"state": UNREACHABLE, "status": f"over {MAX_BYTES} bytes"}
            return {"state": OK, "status": getattr(r, "status", 200),
                    "final_url": r.geturl() if hasattr(r, "geturl") else url,
                    "content_type": (r.headers.get("Content-Type", "") if r.headers else "") or "",
                    "body": body}
    except Refused as e:
        return {"state": REFUSED, "status": str(e)}
    except urllib.error.HTTPError as e:
        return {"state": UNREACHABLE, "status": e.code}
    except Exception as e:  # noqa: BLE001  a refusal, a timeout and a bad tls mean the same here
        return {"state": UNREACHABLE, "status": type(e).__name__}


def fetch_doc(url: str, out_dir: Path, name: str | None = None, opener=None,
              boundary: list[dict] | None = None) -> tuple[int, dict]:
    """Ask the boundary, fetch, save and extract. Returns (exit code, report)."""
    try:
        b = crawl_boundary.rules() if boundary is None else boundary
    except crawl_boundary.BoundaryUnreadable as e:
        return REFUSED, {"url": url, "status": f"the crawl boundary could not be read, so nothing "
                                               f"is fetched: {e}"}
    why = crawl_boundary.forbidden(url, b)
    if why:
        return REFUSED, {"url": url, "status": why}
    got = fetch(url, b, opener)
    if got["state"] != OK:
        return got["state"], {"url": url, "status": got["status"]}
    final = got.get("final_url") or url
    why = crawl_boundary.forbidden(final, b)
    if why:  # belt and braces behind the redirect handler: nothing from it is kept
        return REFUSED, {"url": url, "status": f"it ended at {final}: {why}"}

    body, ctype = got["body"], got["content_type"]
    # THE MEDIA TYPE, WITHOUT ITS PARAMETERS. `application/ld+json; charset=utf-8` failed a
    # suffix test on the whole header and was saved as an unreadable .bin (Codex, PR 361).
    mt = ctype.split(";", 1)[0].strip().lower()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    name = safe_name(name) if name else slug(url)
    pages, real = None, 0
    if is_pdf(body, mt):
        ext = ".pdf"
        try:
            text, pages, real = pdf_text(body)
        except Exception as e:  # noqa: BLE001  a damaged PDF is still a saved PDF
            text, pages = "", 0
            got["status"] = f"{got['status']}, the PDF could not be parsed: {type(e).__name__}"
    elif "html" in mt or body.lstrip()[:15].lower().startswith((b"<!doctype", b"<html")):
        ext, text = ".html", html_text(decode(body, ctype, sniff=True))
        real = len(text.strip())
    elif mt.startswith("text/") or mt in ("application/json", "application/xml") \
            or mt.endswith(("+xml", "+json")):
        # THE SOURCE BYTES NEVER SHARE A NAME WITH THE TEXT. A text/plain source saved as
        # `<name>.txt` was left undecoded at the path reported as its text, so a windows-1252
        # file broke the first UTF-8 read of it (Codex, PR 361).
        sub = mt.split("/", 1)[-1]
        ext = (".json" if sub.endswith("json") else ".xml" if sub.endswith("xml")
               else ".source.txt" if sub in ("plain", "") else f".{safe_name(sub)}")
        text = decode(body, ctype, sniff=sub.endswith("xml"))
        real = len(text.strip())
    else:
        ext, text = ".bin", ""
    raw_path = out_dir / f"{name}{ext}"
    txt_path = out_dir / f"{name}.txt"
    meta_path = out_dir / f"{name}.meta.json"
    if len({raw_path, txt_path, meta_path}) != 3:
        raise SystemExit(f"fetch_doc: {name} would write two artifacts to one path")
    for p in (raw_path, txt_path, meta_path):
        if p.resolve().parent != out_dir:
            raise SystemExit(f"fetch_doc: refusing to write {p}, which is outside {out_dir}")
    raw_path.write_bytes(body)
    txt_path.write_text(text, encoding="utf-8")
    meta = {
        "url": url,
        "final_url": final,
        "status": got["status"],
        "content_type": ctype,
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
        "pages": pages,
        "text_chars": real,
        "fetched_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "saved": str(raw_path),
        "text": str(txt_path),
    }
    meta_path.write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    return (OK if real else NO_TEXT), {**meta, "_text": text}


def _rel(p: str) -> str:
    try:
        return str(Path(p).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return p


def iso_date(value: str) -> str:
    """`--date` is a calendar date and nothing else. `--date ../../escape` built a scratch path
    outside the repository before any other check ran (Codex, PR 361)."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value or ""):
        raise argparse.ArgumentTypeError(f"--date must be YYYY-MM-DD, got {value!r}")
    _dt.date.fromisoformat(value)
    return value


def scratch_dir(date: str) -> Path:
    root = (REPO_ROOT / "out").resolve()
    d = (root / iso_date(date) / "tmp" / "src").resolve()
    if root not in d.parents:
        raise SystemExit(f"fetch_doc: refusing scratch directory {d}, which is outside {root}")
    return d


def main_fetch(a) -> int:
    out_dir = scratch_dir(a.date or run_date())
    code, rep = fetch_doc(a.url, out_dir, a.name)
    if code == REFUSED:
        print(f"fetch_doc: REFUSED {a.url}. {rep['status']} Nothing was requested or saved. Find "
              "the source the registry allows instead.")
        return code
    if code == UNREACHABLE:
        print(f"fetch_doc: NOT FETCHED {a.url} ({rep['status']}). Nothing was saved. A claim can't "
              "rest on a page that did not answer.")
        return code
    print(f"fetch_doc: saved {_rel(rep['saved'])} ({rep['bytes']} bytes, "
          f"{rep['content_type'] or 'no content type'}, sha256 {rep['sha256'][:12]})")
    pages = f", {rep['pages']} pages" if rep["pages"] is not None else ""
    print(f"fetch_doc: text  {_rel(rep['text'])} ({rep['text_chars']} characters extracted{pages})")
    if code == NO_TEXT:
        print("fetch_doc: NO TEXT came out of it. A scanned PDF is the usual reason. The file is "
              "saved, so the Read tool can look at its pages.")
        return code
    print("-" * 72)
    print(rep["_text"][: a.chars])
    if len(rep["_text"]) > a.chars:
        print(f"[... {len(rep['_text']) - a.chars} more characters in {_rel(rep['text'])}]")
    return OK


# ---------------------------------------------------------------------------- self test


def _tiny_pdf(text: str) -> bytes:
    """A one page PDF carrying `text`, built by hand so the test needs no fixture file."""
    stream = f"BT /F1 18 Tf 72 700 Td ({text}) Tj ET".encode()
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out, offsets = io.BytesIO(), []
    out.write(b"%PDF-1.4\n")
    for i, o in enumerate(objs, 1):
        offsets.append(out.tell())
        out.write(f"{i} 0 obj\n".encode() + o + b"\nendobj\n")
    xref = out.tell()
    out.write(f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode())
    for off in offsets:
        out.write(f"{off:010d} 00000 n \n".encode())
    out.write(f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return out.getvalue()


class _Resp:
    def __init__(self, url, body, ctype, status=200):
        self._url, self._body, self.status = url, body, status
        self.headers = {"Content-Type": ctype}

    def read(self, n=-1):
        return self._body if n < 0 else self._body[:n]

    def geturl(self):
        return self._url

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _server(pages: dict, calls: list):
    def op(req, timeout=None):
        url = req.full_url
        calls.append(url)
        if url not in pages:
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
        body, ctype, *final = pages[url]
        return _Resp(final[0] if final else url, body, ctype)
    return op


def self_test() -> int:
    fails: list[str] = []

    def ok(cond: bool, what: str) -> None:
        print(f"  {'ok  ' if cond else 'FAIL'} {what}")
        if not cond:
            fails.append(what)

    quote = "The board’s “final” rule"
    pages = {
        "https://x.gov/sb2807.pdf": (_tiny_pdf("Senate Bill 2807 law enforcement"), "application/pdf"),
        "https://x.gov/download?id=7": (_tiny_pdf("served without a pdf extension"), "application/octet-stream"),
        "https://x.gov/scan.pdf": (_tiny_pdf(""), "application/pdf"),
        "https://x.gov/page": (b"<!doctype html><html><head><style>p{}</style><script>var a=1</script>"
                               b"</head><body><p>The board <strong>adopted</strong> the rule.</p>"
                               b"<p>Second&nbsp;paragraph &amp; more.</p></body></html>", "text/html"),
        "https://x.gov/cp1252": (f"<html><body><p>{quote}</p></body></html>".encode("cp1252"),
                                 "text/html; charset=windows-1252"),
        "https://x.gov/meta1252": (f"<html><head><meta charset=\"windows-1252\"></head><body>{quote}"
                                   "</body></html>".encode("cp1252"), "text/html"),
        "https://x.gov/data.json": (b'{"docket": "58482"}', "application/json"),
        "https://x.gov/plain1252": (quote.encode("cp1252"), "text/plain; charset=windows-1252"),
        "https://x.gov/utf16.xml": (codecs.BOM_UTF16_LE + f'<?xml version="1.0" encoding="UTF-16"?>'
                                    f"<r>{quote}</r>".encode("utf-16-le"), "application/xml"),
        "https://x.gov/ld": (b'{"@context": "https://schema.org", "name": "Docket"}',
                             "application/ld+json; charset=utf-8"),
        "https://x.gov/moved": (b"%PDF-1.4 whatever", "application/pdf",
                                "https://capitol.texas.gov/tlodocs/89R/x.pdf"),
    }
    calls: list[str] = []
    op = _server(pages, calls)
    boundary = crawl_boundary.rules()
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)

        print("the crawl boundary comes first")
        n = len(calls)
        code, rep = fetch_doc("https://capitol.texas.gov/tlodocs/89R/billtext/pdf/SB02807F.pdf", d,
                              opener=op, boundary=boundary)
        ok(code == REFUSED and len(calls) == n, "a /tlodocs/ url is refused and never requested")
        code, rep = fetch_doc("https://CAPITOL.texas.gov/TLODOCS/x.pdf", d, opener=op, boundary=boundary)
        ok(code == REFUSED, "and so is the same path in capitals")
        n = len(calls)
        code, rep = fetch_doc("http://capitol.texas.gov./TLODOCS/x.pdf", d, opener=op, boundary=boundary)
        ok(code == REFUSED and len(calls) == n, "and so is the host spelled with its trailing dot")
        code, rep = fetch_doc("https://capitol.texas.gov/Committees/../%74lodocs/x.pdf", d, opener=op,
                              boundary=boundary)
        ok(code == REFUSED and len(calls) == n, "and a path that only reaches it once decoded")
        code, rep = fetch_doc("https://x.gov/moved", d, opener=op, boundary=boundary)
        ok(code == REFUSED and not list(d.glob("moved*")),
           "a response that ended inside the boundary is refused and nothing is kept")
        h = _BoundaryRedirects(boundary)
        try:
            h.redirect_request(urllib.request.Request("https://x.gov/a"), None, 302, "Found", {},
                               "https://capitol.texas.gov/tlodocs/y.pdf")
            ok(False, "a redirect into the boundary is refused before it is followed")
        except Refused:
            ok(True, "a redirect into the boundary is refused before it is followed")
        real_rules = crawl_boundary.rules
        try:
            def broken(*a, **k):
                raise crawl_boundary.BoundaryUnreadable("test")
            crawl_boundary.rules = broken
            n = len(calls)
            code, rep = fetch_doc("https://x.gov/sb2807.pdf", d, opener=op)
            ok(code == REFUSED and len(calls) == n,
               "a registry that can't be read refuses everything, before any request")
        finally:
            crawl_boundary.rules = real_rules

        print("reading what came back")
        code, rep = fetch_doc("https://x.gov/sb2807.pdf", d, opener=op, boundary=boundary)
        ok(code == OK, "a PDF is fetched and exits 0")
        ok("Senate Bill 2807 law enforcement" in rep.get("_text", ""), "its text is extracted")
        ok(rep.get("pages") == 1 and "--- page 1 ---" in rep.get("_text", ""), "and marked by page")
        ok(Path(rep["saved"]).read_bytes()[:5] == b"%PDF-", "the bytes are saved as served")
        meta = json.loads(Path(rep["saved"]).with_suffix(".meta.json").read_text())
        ok(meta["url"] == "https://x.gov/sb2807.pdf" and len(meta["sha256"]) == 64,
           "the metadata carries the url and the sha256")

        code, rep = fetch_doc("https://x.gov/download?id=7", d, opener=op, boundary=boundary)
        ok(code == OK and rep["saved"].endswith(".pdf"), "a PDF is recognised by its bytes when the url says nothing")

        code, rep = fetch_doc("https://x.gov/scan.pdf", d, opener=op, boundary=boundary)
        ok(code == NO_TEXT, "a PDF with no text exits 2, not 0")

        global _reader
        real_reader = _reader

        class _BadPage:
            def extract_text(self):
                raise ValueError("broken")

        try:
            _reader = lambda body: type("R", (), {"pages": [_BadPage(), _BadPage()]})()  # noqa: E731
            code, rep = fetch_doc("https://x.gov/sb2807.pdf", d, name="allbad", opener=op, boundary=boundary)
            ok(code == NO_TEXT and "could not be read" in rep["_text"],
               "a PDF whose every page fails exits 2, with the failures marked, not counted as text")
        finally:
            _reader = real_reader

        code, rep = fetch_doc("https://x.gov/page", d, opener=op, boundary=boundary)
        ok(code == OK and "The board adopted the rule." in rep["_text"], "HTML is flattened to what a reader sees")
        ok("var a" not in rep["_text"] and "p{}" not in rep["_text"], "scripts and styles are dropped")

        code, rep = fetch_doc("https://x.gov/cp1252", d, opener=op, boundary=boundary)
        ok(code == OK and quote in rep["_text"], "a declared windows-1252 charset is honoured")
        code, rep = fetch_doc("https://x.gov/meta1252", d, opener=op, boundary=boundary)
        ok(code == OK and quote in rep["_text"], "and so is one declared only in a meta tag")

        code, rep = fetch_doc("https://x.gov/data.json", d, opener=op, boundary=boundary)
        raw = Path(rep["saved"]).read_bytes()
        ok(raw == b'{"docket": "58482"}' and hashlib.sha256(raw).hexdigest() == rep["sha256"],
           "a JSON document keeps its own bytes, and its metadata goes beside it")

        code, rep = fetch_doc("https://x.gov/plain1252", d, opener=op, boundary=boundary)
        ok(code == OK and Path(rep["saved"]).read_bytes() == quote.encode("cp1252")
           and Path(rep["text"]).read_text(encoding="utf-8") == quote,
           "plain text keeps its source bytes apart from its decoded text")
        code, rep = fetch_doc("https://x.gov/utf16.xml", d, opener=op, boundary=boundary)
        ok(code == OK and quote in rep["_text"], "UTF-16 XML is read through its byte order mark")
        code, rep = fetch_doc("https://x.gov/ld", d, opener=op, boundary=boundary)
        ok(code == OK and rep["saved"].endswith(".json") and "Docket" in rep["_text"],
           "a +json type with a charset parameter is read as JSON, not saved as .bin")

        code, rep = fetch_doc("https://x.gov/missing", d, opener=op, boundary=boundary)
        ok(code == UNREACHABLE and rep["status"] == 404, "a 404 exits 1 and saves nothing")
        ok(not list(d.glob("missing*")), "nothing is written for a page that did not answer")

        print("names stay inside the directory")
        for bad in ("../escaped", "/etc/escaped", "..", "a/../../b"):
            code, rep = fetch_doc("https://x.gov/sb2807.pdf", d / "src", name=bad, opener=op,
                                  boundary=boundary)
            ok(code == OK and Path(rep["saved"]).parent == (d / "src").resolve(),
               f"--name {bad!r} writes inside the scratch directory")
        ok(not (d / "escaped.pdf").exists(), "and nothing landed beside it")
        a, b = slug("https://x.gov/a/index.html"), slug("https://y.gov/b/index.html")
        ok(a != b and a.startswith("index_"), "two documents with the same name do not collide")

    print("the scratch directory stays under out/")
    for bad in ("../../escape", "/tmp/escape", "2026-13-40", "2026-09-25/../..", ""):
        try:
            scratch_dir(bad)
            ok(False, f"--date {bad!r} is refused")
        except (argparse.ArgumentTypeError, ValueError, SystemExit):
            ok(True, f"--date {bad!r} is refused")
    good = scratch_dir("2026-09-25")
    ok((REPO_ROOT / "out").resolve() in good.parents, "--date 2026-09-25 lands under out/")

    ua = user_agent()
    ok(site() in ua and "github.io" not in ua, f"the User-Agent carries brand.yaml's site ({site()})")
    print(f"fetch_doc self-test: {'FAILED, ' + str(len(fails)) + ' check(s)' if fails else 'all checks passed'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("url", nargs="?")
    ap.add_argument("--name", help="file name stem, default derived from the url")
    ap.add_argument("--date", type=iso_date,
                    help="run date for out/<date>/tmp/src, YYYY-MM-DD, default from the branch")
    ap.add_argument("--chars", type=int, default=4000, help="how much text to print")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.url:
        ap.error("a url is required")
    return main_fetch(a)


if __name__ == "__main__":
    sys.exit(main())
