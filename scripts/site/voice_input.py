"""Shared dictation assets. Recognition only edits fields and never submits a form."""
import hashlib
from pathlib import Path

SCRIPT = Path(__file__).with_suffix(".js").read_text(encoding="utf-8")
CSS = Path(__file__).with_suffix(".css").read_text(encoding="utf-8")
VERSION = hashlib.sha256((SCRIPT + CSS).encode()).hexdigest()[:12]


def head(prefix: str) -> str:
    return (f'<link rel="stylesheet" href="{prefix}voice-input.css?v={VERSION}">\n'
            f'<script defer src="{prefix}voice-input.js?v={VERSION}"></script>')
