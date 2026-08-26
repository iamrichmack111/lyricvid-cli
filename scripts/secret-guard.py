#!/usr/bin/env python3
"""LyricVid repository-specific secret scanner.

Scans tracked text files for credential material that is especially relevant to
LyricVid's YouTube OAuth workflow plus common cloud/dev credentials. It is
intentionally conservative: high-confidence findings fail CI, while filenames
that should never be tracked fail immediately.
"""
from __future__ import annotations

import argparse
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SENSITIVE_BASENAMES = {
    "youtube-oauth.json",
    "youtube-token.json",
    "credentials.json",
    "service-account.json",
    ".env",
    ".env.local",
    ".env.production",
}
SENSITIVE_PREFIXES = ("client_secret_",)
SENSITIVE_DIR_PARTS = {".secrets"}

SKIP_PATHS = {
    "scripts/secret-guard.py",
    "scripts/validate-no-secrets.sh",
}
SKIP_PREFIXES = (
    ".git/",
    ".venv/",
    "node_modules/",
    "dist/",
    "build/",
    ".pytest_cache/",
)

@dataclass(frozen=True)
class Rule:
    name: str
    regex: re.Pattern[str]
    remediation: str


def _rx(parts: list[str], flags: int = 0) -> re.Pattern[str]:
    # Joining fragments keeps the scanner source from trivially matching itself.
    return re.compile("".join(parts), flags)


RULES = [
    Rule(
        "private key",
        _rx([r"-----BEGIN ", r"(?:RSA |EC |OPENSSH |DSA )?", r"PRIVATE KEY-----"]),
        "remove the private key, rotate/revoke it, and clean Git history",
    ),
    Rule(
        "Google OAuth client secret",
        _rx([r'["\']client_', r'secret["\']\s*:\s*["\']', r'(?!(?:REDACTED|CHANGEME|EXAMPLE|YOUR_))[A-Za-z0-9_\-]{12,}', r'["\']'], re.I),
        "remove the OAuth JSON, rotate the client secret, and clean Git history",
    ),
    Rule(
        "Google OAuth refresh token",
        _rx([r'["\']refresh_', r'token["\']\s*:\s*["\']', r'(?!(?:REDACTED|CHANGEME|EXAMPLE|YOUR_))[A-Za-z0-9_\-\./]{20,}', r'["\']'], re.I),
        "revoke the OAuth grant/token and remove it from Git history",
    ),
    Rule(
        "Google OAuth access token",
        _rx([r'["\']access_', r'token["\']\s*:\s*["\']', r'(?!(?:REDACTED|CHANGEME|EXAMPLE|YOUR_))[A-Za-z0-9_\-\./]{20,}', r'["\']'], re.I),
        "revoke the token and remove it from Git history",
    ),
    Rule(
        "Google API key",
        _rx([r"AI", r"za[0-9A-Za-z_\-]{30,}"]),
        "revoke/rotate the Google API key and remove it from Git history",
    ),
    Rule(
        "Google service account private key id",
        _rx([r'["\']private_', r'key_id["\']\s*:\s*["\']', r'[0-9a-f]{20,}', r'["\']'], re.I),
        "disable the service-account key and remove the credential file",
    ),
    Rule(
        "AWS access key",
        _rx([r"AKIA", r"[0-9A-Z]{16}"]),
        "disable/rotate the AWS access key and clean Git history",
    ),
    Rule(
        "GitHub token",
        _rx([r"(?:gh[pousr]_", r"[0-9A-Za-z]{20,}|github_pat_", r"[0-9A-Za-z_]{20,})"]),
        "revoke the GitHub token and clean Git history",
    ),
    Rule(
        "OpenAI-style API key",
        _rx([r"sk-", r"[A-Za-z0-9_\-]{20,}"]),
        "revoke/rotate the API key and clean Git history",
    ),
    Rule(
        "Stripe secret key",
        _rx([r"sk_", r"(?:live|test)_", r"[A-Za-z0-9]{16,}"]),
        "roll the Stripe secret and clean Git history",
    ),
    Rule(
        "database URL with embedded password",
        _rx([r"(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis)://", r"[^\s:/]+:", r"[^\s@/$]{6,}@"], re.I),
        "move database credentials to environment/secret storage",
    ),
]

# OAuth client IDs are identifiers, not secrets, so they are reported only when
# they appear alongside secret-bearing fields in a JSON-like document.
GOOGLE_CLIENT_ID = _rx([r"[0-9]{6,}-", r"[a-z0-9]{16,}\.apps\.googleusercontent\.com"], re.I)
SECRET_FIELD = _rx([r'["\'](?:client_', r'secret|refresh_', r'token|private_', r'key)["\']\s*:'], re.I)


def tracked_files() -> list[Path]:
    try:
        output = subprocess.check_output(
            ["git", "ls-files", "-z"], cwd=ROOT, stderr=subprocess.DEVNULL
        )
        names = [x for x in output.decode().split("\0") if x]
        return [ROOT / name for name in names]
    except (subprocess.CalledProcessError, FileNotFoundError):
        files: list[Path] = []
        for p in ROOT.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(ROOT).as_posix()
            if any(rel.startswith(prefix) for prefix in SKIP_PREFIXES):
                continue
            files.append(p)
        return files


def sensitive_path(rel: str) -> bool:
    p = Path(rel)
    if any(part in SENSITIVE_DIR_PARTS for part in p.parts):
        return True
    if p.name in SENSITIVE_BASENAMES:
        return True
    return any(p.name.startswith(prefix) and p.name.endswith(".json") for prefix in SENSITIVE_PREFIXES)


def read_text(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw[:8192]:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def redact(value: str) -> str:
    value = value.strip()
    if len(value) <= 12:
        return "<redacted>"
    return value[:4] + "…" + value[-4:]


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def scan() -> int:
    failures: list[str] = []
    for path in tracked_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel in SKIP_PATHS or any(rel.startswith(p) for p in SKIP_PREFIXES):
            continue
        if sensitive_path(rel):
            failures.append(f"{rel}: sensitive credential filename/path must not be tracked")
            continue
        text = read_text(path)
        if text is None:
            continue
        for rule in RULES:
            for match in rule.regex.finditer(text):
                failures.append(
                    f"{rel}:{line_number(text, match.start())}: {rule.name}: {redact(match.group(0))} — {rule.remediation}"
                )
        if GOOGLE_CLIENT_ID.search(text) and SECRET_FIELD.search(text):
            failures.append(
                f"{rel}: Google OAuth client configuration appears to contain secret-bearing fields; store it outside the repository"
            )

    if failures:
        print("ERROR: repository-specific secret guard found credential material:", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        print(
            "\nIf any finding is real, revoke/rotate the credential before removing it from Git history.",
            file=sys.stderr,
        )
        return 1
    print("✓ Secret Guard: no LyricVid OAuth, cloud, token, private-key, or credential-path violations detected")
    return 0


def self_test() -> int:
    samples = {
        "google_secret": ('{"client_' + 'secret":"GOCSPX-' + 'A1b2C3d4E5f6G7h8"}', True),
        "refresh": ('{"refresh_' + 'token":"1//0gABCDEFGHIJKLMNOPQRSTUV"}', True),
        "private_key": ("-----BEGIN " + "PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----", True),
        "database": ("postgresql://user:supersecret@db.example/app", True),
        "placeholder": ('{"client_' + 'secret":"REDACTED"}', False),
        "client_id_only": ("1234567890-abcdefghijklmnop.apps.googleusercontent.com", False),
    }
    bad = []
    for name, (sample, expected) in samples.items():
        found = any(rule.regex.search(sample) for rule in RULES)
        if found != expected:
            bad.append((name, expected, found))
    if bad:
        for item in bad:
            print("self-test failure:", item, file=sys.stderr)
        return 1
    print("✓ Secret Guard self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    return self_test() if args.self_test else scan()


if __name__ == "__main__":
    raise SystemExit(main())
