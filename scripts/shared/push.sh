#!/usr/bin/env bash
# push.sh — push a branch and answer, once, whether the remote now has it.
#
# WHY THIS EXISTS
#
# `git push` in this environment returns a non-zero exit and a `remote rejected` line for
# pushes that LANDED. Four times in one run, in two forms:
#
#     ! [remote rejected] <br> (cannot lock ref 'refs/heads/<br>': is at <new> but expected <old>)
#     ! [remote rejected] <br> (cannot lock ref 'refs/heads/<br>': reference already exists)
#
# Both are the server refusing a SECOND copy of a ref update whose first copy already applied.
# `git ls-remote` immediately after showed the new commit on the remote every time.
#
# THE ROOT CAUSE IS NOT ESTABLISHED and this script does not pretend otherwise. What was ruled
# out, by measurement rather than by argument:
#
#   - The proxy. `curl "$HTTPS_PROXY/__agentproxy/status"` reported `recentRelayFailures: []`
#     and no `gitConfigConflicts`, so nothing was being rejected or rewritten there.
#   - Git sending twice. Under `GIT_TRACE=1` a push runs exactly one `git send-pack`.
#   - Payload size and chunking. It reproduced on a one-file commit, which kills the
#     `http.postBuffer` theory that looked obvious because this repo pushes 10 MB carousels.
#   - `-u`. A brand new ref pushed with `--set-upstream` is clean, twice.
#
# So something above git runs the command a second time, and this script is deliberately a fix
# for the OUTCOME rather than a guess at the cause. Guessing already cost one wrong explanation
# committed to CLAUDE.md, which is worse than no explanation.
#
# WHAT IT COSTS WHEN UNHANDLED, which is the reason this is worth a file. The shell reports a
# failed push, so the session verifies with ls-remote, re-pushes, and verifies again. A run that
# pushes eight times pays that tax eight times. The worse half is that it teaches a session to
# read `remote rejected` as noise, and one day it will be real.
#
# THE ANSWER IS THE REMOTE REF, NOT THE PUSH'S OUTPUT. Same shape as `guards_local --verdict`,
# and for the same reason: a noisy stream cannot be read reliably, so ask for the state instead.
# This exits 0 if and only if the remote branch is at the commit being pushed. It says which.
#
#     scripts/shared/push.sh <branch>        push HEAD to origin/<branch> and confirm
#     scripts/shared/push.sh                 same, for the current branch
set -uo pipefail

BRANCH="${1:-$(git rev-parse --abbrev-ref HEAD)}"
if [ -z "$BRANCH" ] || [ "$BRANCH" = "HEAD" ]; then
  echo "push.sh: no branch to push (detached HEAD?)" >&2
  exit 2
fi

LOCAL="$(git rev-parse HEAD)"

# The push's own exit code is recorded and deliberately NOT used as the verdict. It is printed
# so a genuine rejection is still visible to a person reading the transcript.
set +e
OUT="$(git push -u origin "$BRANCH" 2>&1)"
CODE=$?
set -e
printf '%s\n' "$OUT"

REMOTE="$(git ls-remote origin "refs/heads/$BRANCH" 2>/dev/null | awk '{print $1}')"

if [ "$REMOTE" = "$LOCAL" ]; then
  if [ "$CODE" -ne 0 ]; then
    echo "push.sh: git exited $CODE, and origin/$BRANCH IS at ${LOCAL:0:12}. The push landed."
    echo "push.sh: treating this as success. See the header for what that rejection is."
  else
    echo "push.sh: origin/$BRANCH is at ${LOCAL:0:12}."
  fi
  exit 0
fi

# EVERY OTHER STATE IS A REAL FAILURE and gets the real exit code. A push that did not land
# must never be reported as one that did, which is the whole risk this file takes on.
echo "push.sh: PUSH DID NOT LAND. origin/$BRANCH is at '${REMOTE:-<no such ref>}'," >&2
echo "         and HEAD is at $LOCAL. git exited $CODE." >&2
exit "$([ "$CODE" -ne 0 ] && echo "$CODE" || echo 1)"
