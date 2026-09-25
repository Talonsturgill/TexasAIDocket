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
    python3 scripts/shared/fetch_doc.py <url> --name sb2807_le --chars 8000
    python3 scripts/shared/fetch_doc.py --self-test

It writes `<name>.<ext>` (the bytes as served), `<name>.txt` (the text) and `<name>.json` (the url,
the final url after redirects, the status, the content type, the size, the sha256 and the fetch
time), then prints where they are and the opening of the text.

EXIT CODES, read by exit code and never by the last line

  0  fetched, and there is text to read
  1  not fetched: an HTTP error, a refused connection, a timeout, or a file over the size cap
  2  fetched, and no text came out of it. A scanned PDF is the usual case. The bytes are saved,
     so the Read tool can still look at the pages as images.

A CLAIM STILL TRACES TO THE SOURCE URL, NEVER TO THIS FILE. `out/` is scratch and dies with the
container. The saved copy is for reading and quoting, and the claims file cites the url.

A TEXAS LEGISLATURE PDF IS NOT A SAFE SOURCE FOR A VERBATIM QUOTE, measured on 2026-09-25 against
the enrolled SB 2807 at capitol.texas.gov. Its font maps the non-breaking space to the letter A,
so the extracted text reads `S.B.ANo.A2807` and `SECTIONA1.AASubchapter J`. Read the bill in the
PDF if that is what there is, and take the quote from the same bill's HTML text, which carries
real spaces. Nothing here rewrites the letters, because a real A is indistinguishable.
"""
from __future__ import annotations

import argparse
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

REPO_ROOT = Path(__file__).resolve().parents[2]

# The brand URL, never the Pages host. CLAUDE.md, "The public URL".
UA = "TexasAIDocket/1.0 source fetch (+https://texasaidocket.com)"
TIMEOUT = 60
MAX_BYTES = 50 * 1024 * 1024

OK, UNREACHABLE, NO_TEXT = 0, 1, 2

_TAG = re.compile(r"<(script|style|noscript)\b.*?</\1>", re.S | re.I)
_ANY = re.compile(r"<[^>]+>")
_WS = re.compile(r"[ \t\f\v]+")
_BLANKS = re.compile(r"\n\s*\n+")


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


def slug(url: str) -> str:
    """A filesystem-safe name from the url's last path segment, with a short hash so two
    documents both called `index` or `download` do not overwrite each other."""
    path = urllib.parse.urlparse(url).path.rstrip("/")
    stem = Path(urllib.parse.unquote(path)).stem or urllib.parse.urlparse(url).netloc or "doc"
    stem = re.sub(r"[^a-z0-9._-]+", "_", stem.lower()).strip("._-")[:60] or "doc"
    return f"{stem}_{hashlib.sha256(url.encode()).hexdigest()[:8]}"


def is_pdf(body: bytes, content_type: str) -> bool:
    return body[:5] == b"%PDF-" or "application/pdf" in content_type.lower()


def pdf_text(body: bytes) -> tuple[str, int]:
    """(text, pages). Each page is marked so a quote can be found again by page."""
    from pypdf import PdfReader  # installed by bootstrap.sh and requirements-ci.txt

    reader = PdfReader(io.BytesIO(body))
    parts = []
    for i, page in enumerate(reader.pages, 1):
        try:
            t = page.extract_text() or ""
        except Exception as e:  # noqa: BLE001  one bad page must not lose the rest
            t = f"[page {i} could not be read: {type(e).__name__}]"
        parts.append(f"--- page {i} ---\n{t.strip()}")
    return "\n\n".join(parts), len(reader.pages)


def html_text(body: bytes) -> str:
    t = body.decode("utf-8", "replace")
    t = _TAG.sub(" ", t)
    t = re.sub(r"<(br|p|div|li|tr|h[1-6])\b[^>]*>", "\n", t, flags=re.I)
    t = html.unescape(_ANY.sub(" ", t))
    t = _WS.sub(" ", t)
    return _BLANKS.sub("\n\n", "\n".join(line.strip() for line in t.splitlines())).strip()


def fetch(url: str, opener=None) -> dict:
    """{state, status, final_url, content_type, body}. Never raises for a network failure."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    op = opener or urllib.request.urlopen
    try:
        with op(req, timeout=TIMEOUT) as r:
            body = r.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                return {"state": UNREACHABLE, "status": f"over {MAX_BYTES} bytes"}
            return {"state": OK, "status": getattr(r, "status", 200),
                    "final_url": r.geturl() if hasattr(r, "geturl") else url,
                    "content_type": r.headers.get("Content-Type", "") if r.headers else "",
                    "body": body}
    except urllib.error.HTTPError as e:
        return {"state": UNREACHABLE, "status": e.code}
    except Exception as e:  # noqa: BLE001  a refusal, a timeout and a bad tls mean the same here
        return {"state": UNREACHABLE, "status": type(e).__name__}


def fetch_doc(url: str, out_dir: Path, name: str | None = None, opener=None) -> tuple[int, dict]:
    """Fetch, save and extract. Returns (exit code, report)."""
    got = fetch(url, opener)
    if got["state"] != OK:
        return UNREACHABLE, {"url": url, "status": got["status"]}
    body, ctype = got["body"], got["content_type"]
    out_dir.mkdir(parents=True, exist_ok=True)
    name = name or slug(url)
    pages = None
    if is_pdf(body, ctype):
        ext = ".pdf"
        try:
            text, pages = pdf_text(body)
        except Exception as e:  # noqa: BLE001  a damaged PDF is still a saved PDF
            text = ""
            pages = 0
            got["status"] = f"{got['status']}, the PDF could not be parsed: {type(e).__name__}"
    elif "html" in ctype.lower() or body.lstrip()[:15].lower().startswith((b"<!doctype", b"<html")):
        ext, text = ".html", html_text(body)
    elif ctype.lower().startswith(("text/", "application/json", "application/xml")):
        ext, text = ".txt" if "json" not in ctype else ".json", body.decode("utf-8", "replace")
    else:
        ext, text = ".bin", ""
    raw_path = out_dir / f"{name}{ext}"
    txt_path = out_dir / f"{name}.txt"
    raw_path.write_bytes(body)
    if ext != ".txt":
        txt_path.write_text(text, encoding="utf-8")
    real_text = re.sub(r"--- page \d+ ---", "", text).strip()
    meta = {
        "url": url,
        "final_url": got.get("final_url", url),
        "status": got["status"],
        "content_type": ctype,
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
        "pages": pages,
        "text_chars": len(real_text),
        "fetched_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "saved": str(raw_path),
        "text": str(txt_path),
    }
    (out_dir / f"{name}.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    return (OK if real_text else NO_TEXT), {**meta, "_text": text}


def _rel(p: str) -> str:
    try:
        return str(Path(p).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return p


def main_fetch(a) -> int:
    out_dir = REPO_ROOT / "out" / (a.date or run_date()) / "tmp" / "src"
    code, rep = fetch_doc(a.url, out_dir, a.name)
    if code == UNREACHABLE:
        print(f"fetch_doc: NOT FETCHED {a.url} ({rep['status']}). Nothing was saved. A claim can't "
              "rest on a page that did not answer.")
        return code
    print(f"fetch_doc: saved {_rel(rep['saved'])} ({rep['bytes']} bytes, {rep['content_type'] or 'no content type'}, "
          f"sha256 {rep['sha256'][:12]})")
    pages = f", {rep['pages']} pages" if rep["pages"] is not None else ""
    print(f"fetch_doc: text  {_rel(rep['text'])} ({rep['text_chars']} characters{pages})")
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


def _server(pages: dict):
    def op(req, timeout=None):
        url = req.full_url
        if url not in pages:
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
        body, ctype = pages[url]
        return _Resp(url, body, ctype)
    return op


def self_test() -> int:
    fails: list[str] = []

    def ok(cond: bool, what: str) -> None:
        print(f"  {'ok  ' if cond else 'FAIL'} {what}")
        if not cond:
            fails.append(what)

    pages = {
        "https://x.gov/sb2807.pdf": (_tiny_pdf("Senate Bill 2807 law enforcement"), "application/pdf"),
        "https://x.gov/download?id=7": (_tiny_pdf("served without a pdf extension"), "application/octet-stream"),
        "https://x.gov/scan.pdf": (_tiny_pdf(""), "application/pdf"),
        "https://x.gov/page": (b"<!doctype html><html><head><style>p{}</style><script>var a=1</script>"
                               b"</head><body><p>The board <strong>adopted</strong> the rule.</p>"
                               b"<p>Second&nbsp;paragraph &amp; more.</p></body></html>", "text/html"),
    }
    op = _server(pages)
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        code, rep = fetch_doc("https://x.gov/sb2807.pdf", d, opener=op)
        ok(code == OK, "a PDF is fetched and exits 0")
        ok("Senate Bill 2807 law enforcement" in rep.get("_text", ""), "its text is extracted")
        ok(rep.get("pages") == 1 and "--- page 1 ---" in rep.get("_text", ""), "and marked by page")
        ok(Path(rep["saved"]).read_bytes()[:5] == b"%PDF-", "the bytes are saved as served")
        ok(Path(rep["saved"]).parent == d and Path(rep["text"]).exists(), "inside the given directory only")
        meta = json.loads((d / (Path(rep["saved"]).stem + ".json")).read_text())
        ok(meta["url"] == "https://x.gov/sb2807.pdf" and len(meta["sha256"]) == 64,
           "the metadata carries the url and the sha256")

        code, rep = fetch_doc("https://x.gov/download?id=7", d, opener=op)
        ok(code == OK and rep["saved"].endswith(".pdf"), "a PDF is recognised by its bytes when the url says nothing")

        code, rep = fetch_doc("https://x.gov/scan.pdf", d, opener=op)
        ok(code == NO_TEXT, "a PDF with no text exits 2, not 0")

        code, rep = fetch_doc("https://x.gov/page", d, opener=op)
        ok(code == OK and "The board adopted the rule." in rep["_text"], "HTML is flattened to what a reader sees")
        ok("var a" not in rep["_text"] and "p{}" not in rep["_text"], "scripts and styles are dropped")

        code, rep = fetch_doc("https://x.gov/missing", d, opener=op)
        ok(code == UNREACHABLE and rep["status"] == 404, "a 404 exits 1 and saves nothing")
        ok(not list(d.glob("missing*")), "nothing is written for a page that did not answer")

        a, b = slug("https://x.gov/a/index.html"), slug("https://y.gov/b/index.html")
        ok(a != b and a.startswith("index_"), "two documents with the same name do not collide")
        ok("/" not in slug("https://x.gov/../../etc/passwd"), "a url cannot steer the file out of the directory")

    ok("texasaidocket.com" in UA and "github.io" not in UA, "the User-Agent names the brand URL")
    print(f"fetch_doc self-test: {'FAILED, ' + str(len(fails)) + ' check(s)' if fails else 'all checks passed'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("url", nargs="?")
    ap.add_argument("--name", help="file name stem, default derived from the url")
    ap.add_argument("--date", help="run date for out/<date>/tmp/src, default from the branch")
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
