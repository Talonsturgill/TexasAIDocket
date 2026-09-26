#!/usr/bin/env python3
"""no_stall.py: an unattended run never waits on a dialog nobody is there to answer.

THE OWNER, 2026-09-25, on the morning a scheduled run sat all day on one permission dialog:
"every day the run comes up with another reason to stop and prompt for permission, but
obviously nobody's there to answer." And: "i want you to really ban it from stopping to ask me,
cause its not just this time ... it happens nearly everyday, always for a different reason."
Approved on 2026-09-26: "Yes, write the no-stall hook under .claude/".

WHY A HOOK, AFTER A MONTH OF RULES. Every earlier fix removed one cause and the next run found
another: a stamp file, a worklog, a copy out of ~/.claude/. A rule tells the model what not to
do and does nothing when the model does it anyway. A cloud run can't be put in bypass mode and a
routine has no permission setting (CLAUDE.md quotes the documentation). What a repository CAN
ship is a hook, and Claude Code runs a `PermissionRequest` hook the moment it is about to show a
dialog. The hook's answer replaces the dialog.

WHAT IT DOES, IN AN UNATTENDED SESSION ONLY

  PermissionRequest  every dialog is DENIED at once, with a message naming the route that needs
                     no approval. Nothing is ever approved, so the hook grants no permission the
                     run did not already have. It turns "wait all day" into "no, carry on".
  PreToolUse         a write to a protected path, a question to the user and entering plan mode
                     are refused before the harness would ask.
  Elicitation        a connector asking for input is declined.
  Notification       a dialog still unanswered after about six seconds is LOGGED. That is the
                     one kind this file can't answer, and the log names it.
  SessionStart       logs that the hook is armed, so prompt_audit.py can say whether it was.

In an attended session every handler prints nothing, and every dialog reaches the person.

WHAT IT CAN'T DO. Claude Code runs no PermissionRequest hook for a sandboxed command's network
request (hooks reference, "PermissionRequest"). That dialog can still wait. The Notification
handler logs it, prompt_audit.py measures the wait, and the email names both.

UNATTENDED MEANS ANY ONE OF THESE, checked in this order

  TXDOCKET_UNATTENDED=1 or =0      forces the answer either way. For tests. It wins over all
  CLAUDE_CODE_SESSION_ATTENDED=0   the host saying nobody is attending
  the branch is `claude/daily-*`   the routine's own branch, from Phase 0 step 3 on
  the session opened with the      the first line of prompts/ROUTINE_PROMPT.txt, which covers the
    routine's trigger                minutes before that branch exists

Nothing else is. A session on any other branch is attended, because denying a dialog a person is
there to answer is the one way this file can make anything worse.

IT FAILS OPEN. Unreadable input, a crash or a timeout prints nothing, and Claude Code then shows
the dialog exactly as it did before this file existed (hooks reference, "Exit code output").

IT LIVES UNDER .claude/ ON PURPOSE. That directory is `human` lane in ownership.yaml and a
protected path to the host, so no run, the self-editing retro included, can weaken its own guard.

    python3 .claude/hooks/no_stall.py --self-test
    python3 .claude/hooks/no_stall.py --report [--json]     what this session refused
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path

HOOK = Path(__file__).resolve()
HOOK_REPO = HOOK.parents[2]

# ITS OWN FOLDER, out/no_stall/<run date>.jsonl, and never inside a run's out/<date>/. Session
# start logs in every session, attended ones included, and two gates read a missing
# runs/carousel/<date>/ as "look in out/<date>/ instead". A log that created out/<date>/ would
# hand them an empty run.
LOG_DIR = Path("out") / "no_stall"
DAILY_PREFIX = "claude/daily-"
TRIGGER_FILE = Path("prompts") / "ROUTINE_PROMPT.txt"
# The first line of prompts/ROUTINE_PROMPT.txt, and of the prompt stored on the routine itself,
# both read on 2026-09-26. Used only when the file can't be read.
TRIGGER_FALLBACK = ("Read prompts/daily_routine.md from main in Talonsturgill/TexasAIDocket and "
                    "execute it in full.")
YES = frozenset({"1", "true", "yes", "on"})
NO = frozenset({"0", "false", "no", "off"})

# THE PROTECTED PATHS, as code.claude.com/docs/en/permission-modes lists them under "Protected
# paths", read on 2026-09-26. A write to one is prompted in default and acceptEdits mode whatever
# the allow rules say, which in a scheduled cloud run means it waits for nobody.
PROTECTED_DIRS = frozenset({".git", ".vscode", ".idea", ".husky", ".cargo", ".devcontainer",
                            ".yarn", ".mvn", ".claude"})
PROTECTED_DIR_PAIRS = ((".config", "git"),)
EXEMPT_CHILD = {".claude": "worktrees"}  # where Claude Code keeps its own git worktrees
PROTECTED_FILES = frozenset({
    ".gitconfig", ".gitmodules",
    ".bashrc", ".bash_profile", ".bash_login", ".bash_aliases", ".bash_logout", ".zshrc",
    ".zprofile", ".zshenv", ".zlogin", ".zlogout", ".profile", ".envrc",
    ".npmrc", ".yarnrc", ".yarnrc.yml", ".pnp.cjs", ".pnp.loader.mjs", ".pnpmfile.cjs",
    "bunfig.toml", ".bunfig.toml",
    ".bazelrc", ".bazelversion", ".bazeliskrc",
    ".pre-commit-config.yaml", "lefthook.yml", "lefthook.yaml", ".lefthook.yml", ".lefthook.yaml",
    "gradle-wrapper.properties", "maven-wrapper.properties",
    ".devcontainer.json",
    ".ripgreprc", "pyrightconfig.json",
    ".mcp.json", ".claude.json",
})

# The tools the PreToolUse handler judges. `.claude/settings.json` must register exactly these,
# and the self-test reads that file to prove it does.
FILE_TOOLS = {"Write": "file_path", "Edit": "file_path", "MultiEdit": "file_path",
              "NotebookEdit": "notebook_path"}
PRE_TOOL_TOOLS = frozenset(FILE_TOOLS) | {"AskUserQuestion", "EnterPlanMode"}
DIALOG_NOTIFICATIONS = frozenset({"permission_prompt", "elicitation_dialog",
                                  "elicitation_url_dialog", "agent_needs_input"})

WHY = ("This is an unattended scheduled run, so nobody is here to answer a dialog. The no-stall "
       "hook in .claude/hooks/no_stall.py answered this one at once so the run does not wait, as "
       "the owner ordered and CLAUDE.md records under 'A run never stops to ask about "
       "permissions'.")
ROUTES = ("Routes that need no approval: write only inside the working tree, with scratch in "
          "out/<date>/tmp/. Never write, copy, move or edit a path inside a .claude or .git "
          "directory, the repository's or ~/.claude. Read a web document with "
          "python3 scripts/shared/fetch_doc.py <url>. A change that needs a protected path goes "
          "in knowledge/carousel/UPGRADE_BACKLOG.md as a proposal. The same call is refused the "
          "same way if it is retried. This refusal is logged, and prompt_audit.py reports it for "
          "the email.")
ASK = ("Nobody can answer a question in this run. The run decides from CLAUDE.md and "
       "prompts/daily_routine.md, writes the decision and its reason in the run record, and "
       "carries on.")
PLAN = ("Plan mode needs a person to approve the plan, and nobody is attending this run. The run "
        "plans in its run record and carries on without plan mode.")


# ------------------------------------------------------------------ is anybody there

def project_root(env) -> Path:
    d = env.get("CLAUDE_PROJECT_DIR")
    return Path(d) if d else HOOK_REPO


def git_branch(root: Path) -> str:
    """The checked out branch, read off .git/HEAD. No subprocess, so it costs one file read."""
    git = root / ".git"
    try:
        if git.is_file():  # a linked worktree says `gitdir: <path>`
            m = re.match(r"gitdir:\s*(\S.*)", git.read_text(encoding="utf-8").strip())
            if not m:
                return ""
            gitdir = Path(m.group(1).strip())
            git = gitdir if gitdir.is_absolute() else root / gitdir
        head = (git / "HEAD").read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    prefix = "ref: refs/heads/"
    return head[len(prefix):] if head.startswith(prefix) else ""


def _norm(text: str) -> str:
    return " ".join(str(text).lower().split())


def trigger_line() -> str:
    try:
        for line in (HOOK_REPO / TRIGGER_FILE).read_text(encoding="utf-8").splitlines():
            if line.strip():
                return _norm(line)
    except OSError:
        pass
    return _norm(TRIGGER_FALLBACK)


def opening_messages(transcript: str, want: int = 3, max_lines: int = 200,
                     max_bytes: int = 8_000_000) -> list[str]:
    """The first few things this session was told, read off its transcript.

    Transcript lines are JSON, and what a person or a trigger said is `"type": "user"` with the
    text in `message.content`. Tool results and the harness's own `isMeta` entries are skipped.
    Reading stops early, because a transcript can run to hundreds of megabytes.
    """
    out: list[str] = []
    if not transcript:
        return out
    seen = 0
    try:
        with open(transcript, encoding="utf-8", errors="replace") as f:
            for _ in range(max_lines):
                line = f.readline(2_000_000)
                if not line:
                    break
                seen += len(line)
                if seen > max_bytes:
                    break
                if '"user"' not in line:
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(obj, dict) or obj.get("type") != "user" or obj.get("isMeta"):
                    continue
                msg = obj.get("message")
                content = msg.get("content") if isinstance(msg, dict) else None
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    text = "\n".join(str(c.get("text", "")) for c in content
                                     if isinstance(c, dict) and c.get("type") == "text")
                else:
                    text = ""
                if text.strip():
                    out.append(text)
                    if len(out) >= want:
                        break
    except OSError:
        pass
    return out


def verdict(event: dict, env) -> tuple[bool, str]:
    """(unattended, the signal that said so)."""
    forced = str(env.get("TXDOCKET_UNATTENDED") or "").strip().lower()
    if forced in YES:
        return True, "TXDOCKET_UNATTENDED=1"
    if forced in NO:
        return False, "TXDOCKET_UNATTENDED=0"
    if str(env.get("CLAUDE_CODE_SESSION_ATTENDED") or "").strip().lower() in NO:
        return True, "CLAUDE_CODE_SESSION_ATTENDED=0"
    branch = git_branch(project_root(env))
    if branch.startswith(DAILY_PREFIX):
        return True, f"the routine's branch, {branch}"
    trigger = trigger_line()
    opening = opening_messages(str(event.get("transcript_path") or ""))
    if trigger and any(trigger in _norm(text) for text in opening):
        return True, "the session opened with the routine's trigger"
    return False, "no unattended signal"


# ------------------------------------------------------------------ what the host asks about

def protected(path, root: Path) -> str | None:
    """Why the host always asks before a write to this path, or None when it doesn't."""
    if not isinstance(path, str) or not path.strip():
        return None
    p = Path(os.path.expanduser(path.strip()))
    if not p.is_absolute():
        p = root / p
    forms = {os.path.normpath(str(p))}
    try:
        forms.add(os.path.realpath(str(p)))
    except (OSError, ValueError):
        pass
    for form in sorted(forms):
        parts = Path(form).parts
        if not parts:
            continue
        name = parts[-1]
        if name in PROTECTED_FILES or name.lower() in PROTECTED_FILES:
            return f"`{name}` is a protected file"
        dirs = [d.lower() for d in parts[:-1]]
        for i, d in enumerate(dirs):
            if d in PROTECTED_DIRS:
                child = EXEMPT_CHILD.get(d)
                if child and i + 1 < len(dirs) and dirs[i + 1] == child:
                    continue
                return f"it is inside a `{parts[i]}` directory"
            for a, b in PROTECTED_DIR_PAIRS:
                if d == a and i + 1 < len(dirs) and dirs[i + 1] == b:
                    return f"it is inside `{a}/{b}`"
    return None


def _short(path: str, root: Path) -> str:
    if not path:
        return ""
    p = Path(os.path.expanduser(path))
    if not p.is_absolute():
        p = root / p
    p = Path(os.path.normpath(str(p)))
    for base, label in ((root, ""), (Path.home(), "~/")):
        try:
            return label + str(p.relative_to(base))
        except ValueError:
            continue
    return str(p)


def target_of(tool: str, tool_input, root: Path) -> str:
    """What the call was aimed at, with nothing that could carry a secret.

    A path is kept, because it is the whole diagnosis and a path is not a credential. A shell
    command keeps its first word, and its subcommand when there is one, as prompt_audit.py does:
    the arguments can carry a token or a private url, and this ends up in a committed record.
    """
    if not isinstance(tool_input, dict):
        return ""
    if tool in FILE_TOOLS:
        return _short(str(tool_input.get(FILE_TOOLS[tool]) or ""), root)[:200]
    if tool == "Bash":
        cmd = str(tool_input.get("command") or "").strip()
        words = cmd.split()
        kept = words[:1]
        if len(words) > 1 and re.fullmatch(r"[a-z][a-z-]*", words[1]):
            kept.append(words[1])
        names = sorted(d for d in (".claude", ".git")
                       if re.search(r"(^|[\s/'\"=])" + re.escape(d) + r"(/|\s|$|['\"])", cmd))
        text = " ".join(kept) + (" ..." if len(words) > len(kept) else "")
        return (text + (f" (names {', '.join(names)})" if names else ""))[:200]
    return ""


def hint(tool: str, tool_input, root: Path) -> str:
    ti = tool_input if isinstance(tool_input, dict) else {}
    if tool in FILE_TOOLS:
        path = str(ti.get(FILE_TOOLS[tool]) or "")
        why = protected(path, root)
        if why:
            return (f"The write was to {_short(path, root)}, and {why}, which the host always asks "
                    f"about.")
        return (f"The write was to {_short(path, root)}, which is outside what this run may write "
                f"without approval.")
    if tool == "Bash":
        cmd = str(ti.get("command") or "")
        if re.search(r"\.claude/projects/", cmd):
            return ("The command named a file under ~/.claude/projects/, where WebFetch keeps what "
                    "it saves. Read such a file with the Read tool and never copy it. Fetch a "
                    "document you need as a file with fetch_doc.py.")
        if ti.get("dangerouslyDisableSandbox"):
            return "The command asked to run outside the sandbox, which needs a person's approval."
        return ("The command needed approval, because it names a protected path or reaches "
                "something no allow rule covers.")
    if tool == "AskUserQuestion":
        return ASK
    if tool in ("EnterPlanMode", "ExitPlanMode"):
        return PLAN
    if tool.startswith("mcp__"):
        return (f"The connector tool {tool} asked for approval. Nobody can give it, so this step "
                f"does not run here, and the email should say so.")
    return f"The {tool or 'tool'} call needed approval."


# ------------------------------------------------------------------ the log

def run_date(root: Path) -> str:
    m = re.match(r"claude/daily-(\d{4}-\d{2}-\d{2})", git_branch(root))
    return m.group(1) if m else _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")


def log(root: Path, event: dict, decision: str, because: str, tool: str, target: str,
        **extra) -> None:
    record = {
        "at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "session": str(event.get("session_id") or ""),
        "event": str(event.get("hook_event_name") or ""),
        "decision": decision,
        "tool": tool,
        "target": target,
        "because": because,
    }
    if event.get("agent_type"):
        record["agent"] = str(event.get("agent_type"))
    record.update(extra)
    try:
        d = root / LOG_DIR
        d.mkdir(parents=True, exist_ok=True)
        with open(d / f"{run_date(root)}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        pass  # a log that can't be written never costs the run its answer


# ------------------------------------------------------------------ the handlers

def on_permission_request(event: dict, env) -> dict | None:
    unattended, because = verdict(event, env)
    if not unattended:
        return None
    root = project_root(env)
    tool = str(event.get("tool_name") or "")
    ti = event.get("tool_input")
    log(root, event, "deny", because, tool, target_of(tool, ti, root))
    return {"hookSpecificOutput": {
        "hookEventName": "PermissionRequest",
        "decision": {"behavior": "deny", "message": f"{WHY} {hint(tool, ti, root)} {ROUTES}"},
    }}


def on_pre_tool_use(event: dict, env) -> dict | None:
    tool = str(event.get("tool_name") or "")
    ti = event.get("tool_input")
    root = project_root(env)
    if tool in FILE_TOOLS:
        path = ti.get(FILE_TOOLS[tool]) if isinstance(ti, dict) else None
        if not protected(path, root):
            return None  # an ordinary write needs no verdict and gets no answer
        reason = f"{WHY} {hint(tool, ti, root)} {ROUTES}"
    elif tool == "AskUserQuestion":
        reason = f"{WHY} {ASK}"
    elif tool == "EnterPlanMode":
        reason = f"{WHY} {PLAN}"
    else:
        return None
    unattended, because = verdict(event, env)
    if not unattended:
        return None
    log(root, event, "deny", because, tool, target_of(tool, ti, root))
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}


def on_elicitation(event: dict, env) -> dict | None:
    unattended, because = verdict(event, env)
    if not unattended:
        return None
    log(project_root(env), event, "decline", because,
        f"mcp:{event.get('mcp_server_name') or '?'}", str(event.get("mode") or ""))
    return {"hookSpecificOutput": {"hookEventName": "Elicitation", "action": "decline"}}


def on_notification(event: dict, env) -> None:
    kind = str(event.get("notification_type") or "")
    if kind not in DIALOG_NOTIFICATIONS:
        return None
    unattended, because = verdict(event, env)
    if unattended:
        log(project_root(env), event, "waited", because, kind,
            str(event.get("message") or "")[:160])
    return None  # a Notification hook can't answer anything, it can only say what is waiting


def on_session_start(event: dict, env) -> None:
    # Prints nothing: a SessionStart hook's stdout becomes context for the model.
    unattended, because = verdict(event, env)
    log(project_root(env), event, "armed", because, "", str(event.get("source") or ""),
        unattended=unattended)
    return None


HANDLERS = {
    "PermissionRequest": on_permission_request,
    "PreToolUse": on_pre_tool_use,
    "Elicitation": on_elicitation,
    "Notification": on_notification,
    "SessionStart": on_session_start,
}
ALIASES = {"permission-request": "PermissionRequest", "pre-tool-use": "PreToolUse",
           "elicitation": "Elicitation", "notification": "Notification",
           "session-start": "SessionStart"}


def handle(raw: str, env, hint_event: str = "") -> str:
    """The whole hook: stdin text in, stdout text out. It never raises."""
    try:
        event = json.loads(raw) if raw and raw.strip() else {}
        if not isinstance(event, dict):
            return ""
        name = str(event.get("hook_event_name") or ALIASES.get(hint_event, hint_event))
        handler = HANDLERS.get(name)
        if handler is None:
            return ""
        event["hook_event_name"] = name
        out = handler(event, env)
        return json.dumps(out) if out else ""
    except Exception:  # noqa: BLE001  FAILS OPEN: no output is the dialog exactly as it was
        return ""


# ------------------------------------------------------------------ the report

def records(root: Path, session: str | None = None) -> list[dict]:
    rows: list[dict] = []
    for path in sorted((root / LOG_DIR).glob("*.jsonl")):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict) and (not session or row.get("session") == session):
                rows.append(row)
    rows.sort(key=lambda r: str(r.get("at")))
    return rows


def summary(root: Path | None = None, session: str | None = None) -> dict:
    rows = records(root or HOOK_REPO, session)
    armed = [r for r in rows if r.get("decision") == "armed"]
    return {
        "session": session,
        "armed": bool(armed),
        "armed_at": armed[0].get("at") if armed else None,
        "refused": [r for r in rows if r.get("decision") in ("deny", "decline")],
        "waited": [r for r in rows if r.get("decision") == "waited"],
    }


def report_lines(s: dict) -> list[str]:
    if s.get("armed"):
        lines = [f"no-stall hook: armed at {s.get('armed_at')}"]
    else:
        lines = ["no-stall hook: NOT ARMED in this session. The hooks in .claude/settings.json "
                 "did not run here, so a dialog could have waited"]
    refused = s.get("refused") or []
    if refused:
        lines.append(f"  refused {len(refused)} call(s) that would have needed a person:")
        for r in refused:
            lines.append(f"    {r.get('at', '?')}  {str(r.get('event', '?')):17s}  "
                         f"{r.get('tool', '?')}  {r.get('target', '')}".rstrip())
    else:
        lines.append("  refused nothing")
    waited = s.get("waited") or []
    if waited:
        lines.append(f"  {len(waited)} dialog(s) it can't answer waited past six seconds:")
        for r in waited:
            lines.append(f"    {r.get('at', '?')}  {r.get('tool', '?')}  "
                         f"{r.get('target', '')}".rstrip())
    return lines


# ------------------------------------------------------------------ the self-test

def self_test() -> int:
    import subprocess
    import tempfile
    import time

    fails: list[str] = []

    def ok(cond, label, extra=""):
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + str(extra)[:300]}")
        if not cond:
            fails.append(label)

    def repo(base: Path, name: str, branch: str) -> Path:
        r = base / name
        (r / ".git").mkdir(parents=True)
        (r / ".git" / "HEAD").write_text(f"ref: refs/heads/{branch}\n", encoding="utf-8")
        return r

    def transcript(base: Path, name: str, opener: str) -> str:
        p = base / name
        rows = [{"type": "queue-operation", "operation": "enqueue"},
                {"type": "user", "isMeta": True, "message": {"role": "user", "content": "meta"}},
                {"type": "user", "message": {"role": "user", "content": opener}},
                {"type": "assistant", "message": {"role": "assistant", "content": []}}]
        p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        return str(p)

    def pr(tool: str, tool_input: dict, tpath: str = "") -> dict:
        return {"session_id": "sess-1", "transcript_path": tpath, "hook_event_name":
                "PermissionRequest", "tool_name": tool, "tool_input": tool_input}

    def pre(tool: str, tool_input: dict, tpath: str = "") -> dict:
        return {"session_id": "sess-1", "transcript_path": tpath, "hook_event_name": "PreToolUse",
                "tool_name": tool, "tool_input": tool_input, "tool_use_id": "toolu_x"}

    # THE COMMAND THAT STOPPED 2026-09-25, with a stand-in for what its arguments could carry.
    sept25 = ("cp /root/.claude/projects/-home-user-TexasAIDocket/c12a/tool-results/"
              "webfetch-1.pdf out/2026-09-25/tmp/src/sb2807_le.pdf && python3 -c 'SECRET'")

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        daily = repo(base, "daily", "claude/daily-2026-09-26")
        dev = repo(base, "dev", "tsturg/some-work")
        e_daily = {"CLAUDE_PROJECT_DIR": str(daily)}
        e_dev = {"CLAUDE_PROJECT_DIR": str(dev)}
        t_routine = transcript(base, "routine.jsonl", TRIGGER_FALLBACK + "\n\nThat file is ...")
        t_person = transcript(base, "person.jsonl", "can you fix the css on the record page")

        print("who is there")
        ok(verdict({}, e_dev) == (False, "no unattended signal"),
           "a maintainer's branch with nothing else is ATTENDED, so its dialogs reach the person")
        ok(verdict({}, e_daily)[0], "the routine's claude/daily- branch is unattended")
        ok(verdict({}, {**e_dev, "CLAUDE_CODE_SESSION_ATTENDED": "0"})[0],
           "the host's CLAUDE_CODE_SESSION_ATTENDED=0 is unattended")
        ok(not verdict({}, {**e_dev, "CLAUDE_CODE_SESSION_ATTENDED": "1"})[0],
           "...and =1 on a maintainer's branch stays attended")
        ok(verdict({"transcript_path": t_routine}, e_dev)[0],
           "a session that opened with the routine's trigger is unattended before its branch exists")
        ok(not verdict({"transcript_path": t_person}, e_dev)[0],
           "a session a person opened is attended")
        ok(verdict({}, {**e_daily, "TXDOCKET_UNATTENDED": "0"}) == (False, "TXDOCKET_UNATTENDED=0"),
           "TXDOCKET_UNATTENDED=0 forces attended even on the routine's branch")
        ok(verdict({}, {**e_dev, "TXDOCKET_UNATTENDED": "1"})[0], "=1 forces unattended")
        ok(trigger_line() == _norm(TRIGGER_FALLBACK),
           "prompts/ROUTINE_PROMPT.txt still opens with the sentence the routine is stored with",
           trigger_line())
        ok(opening_messages(t_routine)[:1] and "meta" not in opening_messages(t_routine),
           "the harness's own meta entries are not read as the opening message")

        print("which writes the host always asks about")
        cases = [
            (".claude/settings.json", True), (".claude/hooks/no_stall.py", True),
            ("/root/.claude/projects/x/tool-results/y.pdf", True), (".git/ACTOR", True),
            (".GIT/config", True), ("~/.bashrc", True), (".mcp.json", True),
            ("sub/pyrightconfig.json", True), (".config/git/config", True),
            (".claude/worktrees/wt/.claude/settings.json", True),
            (".claude/worktrees/wt/notes.txt", False), (".config/other/x", False),
            ("runs/carousel/2026-09-26/RUN_RECORD.md", False), (".githooks/pre-commit", False),
            ("out/2026-09-26/tmp/src/x.pdf", False), ("", False),
        ]
        for path, want in cases:
            got = protected(path, dev)
            ok(bool(got) == want, f"{path or '(empty)'} is {'protected' if want else 'ordinary'}",
               got)

        print("the answers, in an unattended session")
        out = on_permission_request(pr("Bash", {"command": sept25}), e_daily)
        decision = (out or {}).get("hookSpecificOutput", {}).get("decision", {})
        ok(out and out["hookSpecificOutput"].get("hookEventName") == "PermissionRequest"
           and decision.get("behavior") == "deny",
           "the 2026-09-25 dialog is DENIED at once instead of waiting", out)
        ok("interrupt" not in decision, "...and the run is not interrupted, it carries on")
        msg = decision.get("message", "")
        ok("Read tool" in msg and "fetch_doc.py" in msg,
           "...and the message names the route that needs no approval", msg)
        ok("unattended" in msg and "retried" in msg, "...and says why, and that a retry is refused")
        for tool, ti, needle in [
            ("Write", {"file_path": str(daily / "notes" / "x.md")}, "outside"),
            ("mcp__Gmail__create_draft", {}, "connector"),
            ("AskUserQuestion", {"questions": []}, "question"),
            ("ExitPlanMode", {}, "Plan mode"),
            ("WebFetch", {"url": "https://x.gov"}, "needed approval"),
        ]:
            o = on_permission_request(pr(tool, ti), e_daily)
            d = (o or {}).get("hookSpecificOutput", {}).get("decision", {})
            ok(d.get("behavior") == "deny" and needle in d.get("message", ""),
               f"a {tool} dialog is denied with a message about it", d)

        o = on_pre_tool_use(pre("Write", {"file_path": str(daily / ".claude" / "settings.json"),
                                          "content": "x"}), e_daily)
        h = (o or {}).get("hookSpecificOutput", {})
        ok(h.get("hookEventName") == "PreToolUse" and h.get("permissionDecision") == "deny"
           and ".claude" in h.get("permissionDecisionReason", ""),
           "a write under .claude/ is refused before the harness asks", o)
        o = on_pre_tool_use(pre("Edit", {"file_path": "/root/.claude/projects/p/x.jsonl"}), e_daily)
        ok((o or {}).get("hookSpecificOutput", {}).get("permissionDecision") == "deny",
           "an edit under ~/.claude/ is refused too")
        o = on_pre_tool_use(pre("NotebookEdit", {"notebook_path": str(daily / ".git" / "x")}),
                            e_daily)
        ok((o or {}).get("hookSpecificOutput", {}).get("permissionDecision") == "deny",
           "and a notebook edit inside .git/, which names its path differently")
        ok(on_pre_tool_use(pre("Write", {"file_path": str(daily / "runs" / "x.md")}), e_daily)
           is None, "an ordinary write in the working tree gets no answer at all")
        o = on_pre_tool_use(pre("AskUserQuestion", {"questions": [{"question": "?"}]}), e_daily)
        ok("run record" in (o or {}).get("hookSpecificOutput", {}).get("permissionDecisionReason", ""),
           "a question to nobody is refused and the run is told to decide and record it", o)
        o = on_pre_tool_use(pre("EnterPlanMode", {}), e_daily)
        ok((o or {}).get("hookSpecificOutput", {}).get("permissionDecision") == "deny",
           "entering plan mode is refused, since nobody can approve the plan")
        ok(on_pre_tool_use(pre("Bash", {"command": "ls"}), e_daily) is None,
           "a tool this handler does not judge gets no answer")
        o = on_elicitation({"hook_event_name": "Elicitation", "mcp_server_name": "Gmail",
                            "message": "sign in", "mode": "url"}, e_daily)
        ok((o or {}).get("hookSpecificOutput", {}) == {"hookEventName": "Elicitation",
                                                       "action": "decline"},
           "a connector asking for input is declined", o)
        ok(on_notification({"hook_event_name": "Notification", "notification_type":
                            "permission_prompt", "message": "Claude needs your permission",
                            "session_id": "sess-1"}, e_daily) is None,
           "a waiting dialog is only logged, since a Notification hook can't answer it")
        ok(on_session_start({"hook_event_name": "SessionStart", "source": "startup",
                             "session_id": "sess-1"}, e_daily) is None,
           "session start prints nothing, because its output would become context")

        print("and in an attended session, nothing")
        ok(on_permission_request(pr("Bash", {"command": sept25}), e_dev) is None,
           "a dialog in a maintainer's session is left for the person")
        ok(on_pre_tool_use(pre("Write", {"file_path": str(dev / ".claude" / "settings.json")}),
                           e_dev) is None,
           "...and so is a write under .claude/, which the person can approve")
        ok(on_pre_tool_use(pre("AskUserQuestion", {"questions": []}), e_dev) is None,
           "...and a question, which the person can answer")
        ok(on_elicitation({"hook_event_name": "Elicitation", "mcp_server_name": "x"}, e_dev)
           is None, "...and a connector's form")
        ok(not (dev / "out").exists(),
           "an attended session's dialogs leave nothing in the log, not even a folder")

        print("the log")
        logfile = daily / LOG_DIR / "2026-09-26.jsonl"
        ok(logfile.is_file(), "the run's refusals land in out/no_stall/<run date>.jsonl", logfile)
        ok(sorted(p.name for p in (daily / "out").iterdir()) == ["no_stall"],
           "and nothing else under out/, so no run directory is ever created by the hook")
        text = logfile.read_text(encoding="utf-8") if logfile.is_file() else ""
        ok("SECRET" not in text and "webfetch-1" not in text,
           "a command's arguments never reach the log, since it feeds a committed record")
        ok("cp ... (names .claude)" in text, "...while the command and what it named do", text)
        s = summary(daily, "sess-1")
        ok(s["armed"] and len(s["refused"]) >= 10 and len(s["waited"]) == 1,
           "the summary finds it armed, every refusal and the dialog that waited", s)
        lines = report_lines(s)
        ok(lines[0].startswith("no-stall hook: armed") and any("refused" in l for l in lines),
           "the report says so in words", lines[:3])
        ok(report_lines(summary(dev, "sess-9"))[0].startswith("no-stall hook: NOT ARMED"),
           "a session the hook never saw is reported NOT ARMED rather than clean")

        print("it fails open")
        env = {**e_daily}
        try:
            silent = handle("", env) == "" and handle("not json", env) == "" \
                and handle("[1, 2]", env) == ""
        except Exception:  # noqa: BLE001  a raise here IS the defect being replayed
            silent = False
        ok(silent, "unreadable input prints nothing, so the dialog shows as it always did")
        real = HANDLERS["PermissionRequest"]
        try:
            def broken(event, env):
                raise RuntimeError("boom")
            HANDLERS["PermissionRequest"] = broken
            ok(handle(json.dumps(pr("Bash", {"command": "x"})), env) == "",
               "a handler that crashes prints nothing rather than a half answer")
        finally:
            HANDLERS["PermissionRequest"] = real
        ok(handle(json.dumps(pr("Bash", "not a dict")), env).startswith("{"),
           "a malformed tool_input still gets the denial rather than a crash")

        print("the real process, the way Claude Code runs it")
        base_env = {k: v for k, v in os.environ.items()
                    if k not in ("CLAUDE_CODE_SESSION_ATTENDED", "TXDOCKET_UNATTENDED")}
        t0 = time.monotonic()
        run = subprocess.run([sys.executable, str(HOOK), "permission-request"],
                             input=json.dumps(pr("Bash", {"command": sept25})),
                             capture_output=True, text=True, timeout=60,
                             env={**base_env, **e_daily})
        took = time.monotonic() - t0
        try:
            parsed = json.loads(run.stdout)
        except ValueError:
            parsed = {}
        ok(run.returncode == 0 and parsed.get("hookSpecificOutput", {}).get("decision", {})
           .get("behavior") == "deny", "exit 0 with a denial Claude Code can parse",
           (run.returncode, run.stdout[:200], run.stderr[-300:]))
        ok(took < 5, f"and it answers in {took:.2f}s, far inside its 10s timeout")
        run = subprocess.run([sys.executable, str(HOOK), "permission-request"],
                             input=json.dumps(pr("Bash", {"command": "ls"})),
                             capture_output=True, text=True, timeout=60,
                             env={**base_env, **e_dev})
        ok(run.returncode == 0 and run.stdout == "",
           "an attended session gets exit 0 and no output, which leaves the dialog alone",
           (run.returncode, run.stdout[:200]))
        run = subprocess.run([sys.executable, str(HOOK), "pre-tool-use"],
                             input="{broken", capture_output=True, text=True, timeout=60,
                             env={**base_env, **e_daily})
        ok(run.returncode == 0 and run.stdout == "", "garbage on stdin is exit 0 and silence")

    print("the registration in .claude/settings.json")
    try:
        settings = json.loads((HOOK_REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        settings = {}
        ok(False, ".claude/settings.json parses", exc)
    hooks = settings.get("hooks") or {}

    def commands(event: str) -> list[tuple[str, dict]]:
        out = []
        for group in hooks.get(event) or []:
            for h in group.get("hooks") or []:
                if h.get("type") == "command" and "no_stall.py" in str(h.get("command") or ""):
                    out.append((str(group.get("matcher") or ""), h))
        return out

    def names(matcher: str) -> set[str] | None:
        if matcher in ("", "*"):
            return None  # matches everything
        return {m.strip() for m in re.split(r"[|,]", matcher) if m.strip()}

    for event, need in [("PermissionRequest", None), ("PreToolUse", PRE_TOOL_TOOLS),
                        ("Elicitation", None), ("Notification", DIALOG_NOTIFICATIONS),
                        ("SessionStart", None)]:
        regs = commands(event)
        good = [h for m, h in regs
                if (names(m) is None or (need is not None and need <= names(m)))
                and "${CLAUDE_PROJECT_DIR}" in str(h.get("command"))
                and 0 < float(h.get("timeout") or 60) <= 30]
        ok(bool(good), f"{event} runs this hook for everything it handles, from the project "
                       f"root, with a short timeout", regs)

    print()
    print(f"no_stall self-test: {'FAILED, ' + str(len(fails)) + ' check(s)' if fails else 'all passed'}")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    if "--report" in argv:
        s = summary(project_root(os.environ), os.environ.get("CLAUDE_CODE_SESSION_ID") or None)
        print(json.dumps(s, indent=1) if "--json" in argv else "\n".join(report_lines(s)))
        return 0
    try:
        raw = sys.stdin.read()
    except Exception:  # noqa: BLE001
        return 0
    out = handle(raw, os.environ, argv[1] if len(argv) > 1 else "")
    if out:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
