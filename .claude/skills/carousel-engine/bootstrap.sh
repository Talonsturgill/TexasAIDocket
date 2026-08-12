#!/usr/bin/env bash
# bootstrap.sh — idempotent dependency setup for the carousel engine.
# Chromium is pre-installed in the cloud environment (PLAYWRIGHT_BROWSERS_PATH);
# never run "playwright install".
set -e

python3 - <<'EOF'
import importlib, subprocess, sys
need = []
for mod, pkg in [("playwright", "playwright"), ("pypdf", "pypdf"),
                 ("img2pdf", "img2pdf"), ("PIL", "pillow"),
                 ("numpy", "numpy"), ("yaml", "pyyaml")]:
    try:
        importlib.import_module(mod)
    except BaseException:   # BaseException: pyo3 PanicException is not an ImportError
        need.append(pkg)
if need:
    print("installing:", " ".join(need))
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "--break-system-packages", "-q", *need])
else:
    print("all python deps present")

# pypdf must IMPORT cleanly, not just be installed: Debian's cryptography 41
# ships a broken pyo3 rust binding that panics at import time and would kill
# the vector-PDF path in assemble.py mid-run (2026-07-08 incident). Probe in
# a subprocess (a panic can poison the interpreter) and repair by upgrading
# cryptography to a working wheel.
probe = [sys.executable, "-c", "from pypdf import PdfReader, PdfWriter"]
if subprocess.run(probe, capture_output=True).returncode != 0:
    print("pypdf import broken (likely cryptography rust-binding panic); repairing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "--user", "--upgrade", "-q", "cryptography"])
    if subprocess.run(probe, capture_output=True).returncode != 0:
        print("WARNING: pypdf still broken after cryptography upgrade; "
              "vector PDF will fall back to raster", file=sys.stderr)
    else:
        print("pypdf import: repaired")
else:
    print("pypdf import: ok")
EOF

# sanity: a launchable chromium must exist
if ls /opt/pw-browsers/chromium*/chrome-linux/chrome >/dev/null 2>&1 || \
   command -v chromium >/dev/null 2>&1; then
  echo "chromium: ok"
else
  echo "WARNING: no chromium found under /opt/pw-browsers — render.py may fail" >&2
fi
echo "bootstrap complete"
