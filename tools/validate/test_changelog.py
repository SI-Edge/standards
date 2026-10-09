# Copyright 2026 The Selfkin Standards contributors
# SPDX-License-Identifier: Apache-2.0
"""Tests for change fragments (changes/) and the CHANGELOG assembler."""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import changelog  # noqa: E402

GOOD = "---\ntitle: Something\ntype: tooling\n---\n\nNo normative rule changed.\n\n### Added\n\n- a thing\n"


class FragmentFormatTests(unittest.TestCase):
    def test_repository_fragments_are_well_formed(self):
        for path in changelog.fragments():
            with self.subTest(file=path.name):
                self.assertEqual(changelog.problems(path.name, path.read_text(encoding="utf-8")), [])

    def test_good_fragment(self):
        self.assertEqual(changelog.problems("62.md", GOOD), [])
        self.assertEqual(changelog.problems("signing-input.md", GOOD), [])

    def test_bad_fragments(self):
        cases = {
            "Bad_Name.md": GOOD,
            "x.md": GOOD.replace("type: tooling", "type: misc"),
            "y.md": GOOD.replace("title: Something\n", ""),
            "z.md": GOOD.replace("### Added\n\n", "### Added\n"),
            "w.md": GOOD.replace("### Added", "## Added"),
            "v.md": GOOD.replace("a thing", "a thing \u2014 dash"),
            "u.md": "no front matter\n",
            "t.md": "---\ntitle: T\ntype: tooling\n---\n\n",
            "s.md": GOOD.replace("type: tooling", "type: tooling\ndate: 9 Oct"),
        }
        for name, text in cases.items():
            with self.subTest(file=name):
                self.assertNotEqual(changelog.problems(name, text), [])


class AssembleTests(unittest.TestCase):
    def make(self, frags: dict[str, str]) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "changes").mkdir()
        (root / "changes" / "README.md").write_text("# Change Fragments\n")
        for name, text in frags.items():
            (root / "changes" / name).write_text(text)
        (root / "CHANGELOG.md").write_text("# Changelog\n\nPreamble.\n\n## 2026-10-01: Old\n\nOld body.\n")
        return root

    def test_assemble_order_and_removal(self):
        root = self.make({
            "63.md": GOOD.replace("Something", "Alg allowlist"),
            "62.md": GOOD.replace("Something", "Signing input"),
            "lint.md": GOOD.replace("Something", "Lint").replace("type: tooling", "type: tooling\ndate: 2026-10-09"),
        })
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(changelog.cmd_assemble("2026-10-23", dry=False, keep=False, root=root), 0)
        text = (root / "CHANGELOG.md").read_text()
        heads = [l for l in text.splitlines() if l.startswith("## ")]
        self.assertEqual(heads, ["## 2026-10-23: Signing input", "## 2026-10-23: Alg allowlist",
                                 "## 2026-10-09: Lint", "## 2026-10-01: Old"])
        self.assertTrue(text.startswith("# Changelog\n\nPreamble.\n\n## 2026-10-23: Signing input\n\nNo normative"))
        self.assertIn("### Added\n\n- a thing\n\n## 2026-10-23: Alg allowlist", text)
        self.assertEqual(changelog.fragments(root), [])
        self.assertTrue((root / "changes" / "README.md").exists())

    def test_assemble_refuses_bad_fragment(self):
        root = self.make({"bad.md": "nope\n"})
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(changelog.cmd_assemble("2026-10-23", dry=False, keep=False, root=root), 1)
        self.assertNotIn("nope", (root / "CHANGELOG.md").read_text())


if __name__ == "__main__":
    unittest.main()
