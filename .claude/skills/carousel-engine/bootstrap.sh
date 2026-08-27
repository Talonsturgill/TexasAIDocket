#!/usr/bin/env bash
# bootstrap.sh — idempotent dependency setup for the carousel engine.
# Chromium is pre-installed in the cloud environment (PLAYWRIGHT_BROWSERS_PATH);
# never run "playwright install".
set -e

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../../.." && pwd)"

python3 -m pip install --break-system-packages --quiet \
  --no-deps --requirement "$REPO_ROOT/requirements-carousel.txt"
python3 -c "from pypdf import PdfReader, PdfWriter"
echo "pypdf import: ok"

# sanity: a launchable chromium must exist
if ls /opt/pw-browsers/chromium*/chrome-linux/chrome >/dev/null 2>&1 || \
   command -v chromium >/dev/null 2>&1; then
  echo "chromium: ok"
else
  echo "WARNING: no chromium found under /opt/pw-browsers — render.py may fail" >&2
fi
echo "bootstrap complete"
