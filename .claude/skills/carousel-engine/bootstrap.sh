#!/usr/bin/env bash
# bootstrap.sh — idempotent dependency setup for the carousel engine.
# Chromium is pre-installed in the cloud environment (PLAYWRIGHT_BROWSERS_PATH);
# never run "playwright install".
set -e

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../../.." && pwd)"

# A DISTRO-OWNED PACKAGE MAKES THE PLAIN INSTALL FAIL, AND IT FAILS THE WHOLE FILE.
# On 2026-08-30 this exited 1 with "Cannot uninstall PyYAML 6.0.1, RECORD file not found. Hint:
# The package was installed by debian." pip wanted to replace the distro's PyYAML to satisfy the
# pin, could not, and gave up before installing ANYTHING. `set -e` then stopped the script, so
# numpy and Pillow were never installed and the run carried on without them.
#
# That is not a cosmetic failure. `qa.py` imports numpy and `ship_images.py` needs both, and
# ship_images is a HARD STOP at Phase 16, so the run would have died at the ship gate hours later
# with the cause four phases behind it. The full guard suite caught it here as two red steps that
# had nothing to do with the code they were testing.
#
# So the fallback re-runs with --ignore-installed, which leaves the distro's copy alone rather
# than trying to uninstall it. It is only reached when the fast path fails, so an ordinary
# container still pays the quick install.
if ! python3 -m pip install --break-system-packages --quiet \
     --no-deps --requirement "$REPO_ROOT/requirements-carousel.txt" 2>/dev/null; then
  echo "bootstrap: plain install failed, retrying without touching distro-owned packages" >&2
  python3 -m pip install --break-system-packages --quiet \
    --no-deps --ignore-installed --requirement "$REPO_ROOT/requirements-carousel.txt"
fi

python3 -c "from pypdf import PdfReader, PdfWriter"
echo "pypdf import: ok"

# THE TWO THE GUARD SUITE ACTUALLY FAILED ON. Asserted here rather than assumed, because the
# failure above was silent about them and the cost of finding out later is a dead ship gate.
python3 -c "import numpy, PIL; print(f'numpy {numpy.__version__}, Pillow {PIL.__version__}: ok')"

# sanity: a launchable chromium must exist
if ls /opt/pw-browsers/chromium*/chrome-linux/chrome >/dev/null 2>&1 || \
   command -v chromium >/dev/null 2>&1; then
  echo "chromium: ok"
else
  echo "WARNING: no chromium found under /opt/pw-browsers — render.py may fail" >&2
fi
echo "bootstrap complete"
