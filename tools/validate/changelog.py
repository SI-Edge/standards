# Copyright 2026 The Selfkin Standards contributors
# SPDX-License-Identifier: Apache-2.0
"""Change fragments in changes/ and their assembly into CHANGELOG.md. See changes/README.md.

  python tools/validate/changelog.py check
  python tools/validate/changelog.py require --base BASE_SHA [--head HEAD]   (CI, pull requests)
  python tools/validate/changelog.py assemble [--date YYYY-MM-DD] [--dry-run] [--keep]
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[2]
CHANGES = "changes"
TYPES = ("normative", "clarification", "schema", "editorial", "tooling", "process")
NAME = re.compile(r"^(?:\d+|[a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
DASHES = ("\u2014", "\u2013")
# a pull request touching any of these needs a fragment
CHECKED = ("drafts/", "schemas/", "examples/", "registries/", "test-vectors/", "tools/", "rfcs/",
           "TERMINOLOGY.md", "THREAT-MODEL.md", "GOVERNANCE.md", "CONTRIBUTING.md", "PATENT-POLICY.md")


def parse(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("missing front matter (--- title/type ---)")
    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"bad front matter line: {line!r}")
        meta[key.strip()] = value.strip()
    return meta, m.group(2).strip("\n")


def problems(name: str, text: str) -> list[str]:
    out = []
    if not NAME.match(name):
        out.append("file name must be <pr-number>.md or <lowercase-slug>.md")
    try:
        meta, body = parse(text)
    except ValueError as exc:
        return out + [str(exc)]
    unknown = set(meta) - {"title", "type", "date"}
    if unknown:
        out.append(f"unknown front matter keys: {', '.join(sorted(unknown))}")
    if not meta.get("title"):
        out.append("title is required")
    if meta.get("type") not in TYPES:
        out.append(f"type must be one of {', '.join(TYPES)}")
    if "date" in meta:
        try:
            dt.date.fromisoformat(meta["date"])
        except ValueError:
            out.append("date must be YYYY-MM-DD")
    if not body.strip():
        out.append("body is empty")
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^#{1,2} ", line):
            out.append(f"line {i + 1}: use ### subheadings; # and ## are reserved for CHANGELOG.md")
        if re.match(r"^#{3,6} ", line) and i + 1 < len(lines) and lines[i + 1].strip():
            out.append(f"line {i + 1}: blank line needed after a heading")
    if any(d in text for d in DASHES):
        out.append("no em-dashes or en-dashes")
    return out


def is_fragment(path: str) -> bool:
    """True for changes/<name>.md, except changes/README.md and dotfiles.
    Other files in changes/ (for example .markdownlint-cli2.jsonc) and subfolders are not fragments."""
    folder, sep, name = path.partition("/")
    return (folder == CHANGES and bool(sep) and "/" not in name and name.endswith(".md")
            and name != "README.md" and not name.startswith("."))


def fragments(root: Path = REPO) -> list[Path]:
    return sorted(p for p in (root / CHANGES).iterdir() if p.is_file() and is_fragment(f"{CHANGES}/{p.name}"))


def render(root: Path, date: str) -> tuple[str, list[Path]]:
    items = []
    for p in fragments(root):
        meta, body = parse(p.read_text(encoding="utf-8"))
        items.append((meta.get("date", date), p.name, meta["title"], body))
    # newest date first; within a date, file-name order
    items.sort(key=lambda x: x[1])
    items.sort(key=lambda x: x[0], reverse=True)
    text = "".join(f"## {d}: {title}\n\n{body}\n\n" for d, _, title, body in items)
    return text, fragments(root)


def insert(changelog: str, section: str) -> str:
    i = changelog.find("\n## ")
    if i < 0:
        return changelog.rstrip("\n") + "\n\n" + section.rstrip("\n") + "\n"
    return changelog[: i + 1] + section + changelog[i + 1:]


def cmd_check(root: Path = REPO) -> int:
    bad = 0
    for p in fragments(root):
        for msg in problems(p.name, p.read_text(encoding="utf-8")):
            print(f"{p.relative_to(root)}: {msg}")
            bad += 1
    print(f"{len(fragments(root))} fragment(s), {bad} problem(s)")
    return 1 if bad else 0


def cmd_require(base: str, head: str, root: Path = REPO) -> int:
    def names(*args):
        out = subprocess.run(["git", "diff", "--name-only", *args, base, head], cwd=root, capture_output=True, text=True, check=True)
        return [n for n in out.stdout.splitlines() if n]
    changed = names()
    added = names("--diff-filter=A")
    if not any(n.startswith(CHECKED) or n in CHECKED for n in changed):
        print("no fragment needed: no checked paths changed")
        return 0
    new = [n for n in added if is_fragment(n)]
    if "CHANGELOG.md" in changed and not new:
        removed = [n for n in names("--diff-filter=D") if is_fragment(n)]
        if removed:
            print(f"release: CHANGELOG.md assembled from {len(removed)} fragment(s)")
            return 0
        print("edit changes/<pr-or-slug>.md instead of CHANGELOG.md (see changes/README.md)")
        return 1
    if not new:
        print("missing change fragment: add changes/<pr-or-slug>.md (see changes/README.md), "
              "or ask a maintainer for the no-changelog label")
        return 1
    print("fragment(s): " + ", ".join(new))
    return 0


def cmd_assemble(date: str | None, dry: bool, keep: bool, root: Path = REPO) -> int:
    if cmd_check(root):
        return 1
    date = date or dt.datetime.now(ZoneInfo("Europe/Zurich")).date().isoformat()
    section, used = render(root, date)
    if not used:
        print("no fragments")
        return 0
    if dry:
        print(section, end="")
        return 0
    path = root / "CHANGELOG.md"
    path.write_text(insert(path.read_text(encoding="utf-8"), section), encoding="utf-8")
    if not keep:
        for p in used:
            p.unlink()
    print(f"CHANGELOG.md: {len(used)} entr{'y' if len(used) == 1 else 'ies'} added" + ("" if keep else "; fragments removed"))
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    r = sub.add_parser("require")
    r.add_argument("--base", required=True)
    r.add_argument("--head", default="HEAD")
    a = sub.add_parser("assemble")
    a.add_argument("--date")
    a.add_argument("--dry-run", action="store_true")
    a.add_argument("--keep", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "check":
        return cmd_check()
    if args.cmd == "require":
        return cmd_require(args.base, args.head)
    return cmd_assemble(args.date, args.dry_run, args.keep)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
