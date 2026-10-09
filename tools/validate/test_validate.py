# Copyright 2026 The SI Edge Standards contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the SI Edge schemas, examples, and validator.

Run from the repository root:
  python -m unittest discover -s tools/validate -v
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate  # noqa: E402

FORBIDDEN_DASHES = ("\u2014", "\u2013")
TEXT_SUFFIXES = {".json", ".md", ".py", ".yml", ".yaml", ".txt"}


class SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = validate.load_schemas()
        cls.registry = validate.build_registry(cls.schemas)

    def test_schema_files_are_well_formed(self):
        self.assertEqual(validate.check_schema_files(self.schemas), [])

    def test_valid_examples_pass(self):
        for path in validate.example_files():
            if path.name.endswith(".invalid.json"):
                continue
            with self.subTest(example=path.name):
                problems = validate.validate_document(
                    validate.load_json(path), validate.schema_for_example(path), self.schemas, self.registry
                )
                self.assertEqual(problems, [], f"{path.name} should be valid")

    def test_invalid_examples_fail(self):
        for path in validate.example_files():
            if not path.name.endswith(".invalid.json"):
                continue
            with self.subTest(example=path.name):
                problems = validate.validate_document(
                    validate.load_json(path), validate.schema_for_example(path), self.schemas, self.registry
                )
                self.assertNotEqual(problems, [], f"{path.name} should be invalid")

    def test_every_schema_has_valid_and_invalid_examples(self):
        files = [p.name for p in validate.example_files()]
        for name in validate.SCHEMA_NAMES:
            with self.subTest(schema=name):
                mine = [f for f in files if validate.schema_for_example(Path(f)) == name]
                self.assertTrue(any(not f.endswith(".invalid.json") for f in mine), f"no valid example for {name}")
                self.assertTrue(any(f.endswith(".invalid.json") for f in mine), f"no invalid example for {name}")

    def test_invalid_examples_are_explained(self):
        readme = (validate.EXAMPLE_DIR / "README.md").read_text(encoding="utf-8")
        for path in validate.example_files():
            if path.name.endswith(".invalid.json"):
                with self.subTest(example=path.name):
                    self.assertIn(f"`{path.name}`", readme, "explain every invalid example in examples/README.md")

    def test_unknown_residency_tag_syntax(self):
        tag_schema = {"$ref": "common.schema.json#/$defs/residencyTag"}
        tag_schema["$id"] = validate.ID_PREFIX + "test-tag.schema.json"
        from jsonschema import Draft202012Validator

        checker = Draft202012Validator(tag_schema, registry=self.registry)
        for good in ("CH", "EU", "CH-EU", "x-home-only"):
            self.assertTrue(checker.is_valid(good), good)
        for bad in ("ch", "EU-CH", "Switzerland", "x-", ""):
            self.assertFalse(checker.is_valid(bad), bad)


def registry_codes(name: str) -> list[str]:
    """First-column codes of every table row in registries/<name>."""
    codes = []
    for line in (validate.REPO / "registries" / name).read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\| `([^`]+)` \|", line)
        if match:
            codes.append(match.group(1))
    return codes


class RegistryTests(unittest.TestCase):
    """Registries and schemas must list the same codes."""

    @classmethod
    def setUpClass(cls):
        cls.common = validate.load_schemas()["common"]["$defs"]

    def test_refusal_reasons_match(self):
        enum = self.common["refusalReason"]["anyOf"][0]["enum"]
        self.assertEqual(sorted(registry_codes("refusal-reasons.md")), sorted(enum))

    def test_si_intents_and_domains_match(self):
        codes = registry_codes("intents.md")
        si = [c for c in codes if c.startswith("si.")]
        domains = [c for c in codes if not c.startswith("si.")]
        self.assertEqual(sorted(si), sorted(self.common["intent"]["anyOf"][0]["enum"]))
        pattern = self.common["intent"]["anyOf"][1]["pattern"]
        self.assertEqual(sorted(domains), sorted(re.match(r"^\^\(([^)]*)\)", pattern).group(1).split("|")))

    def test_data_classes_match(self):
        pattern = self.common["dataClass"]["pattern"]
        classes = re.match(r"^\^\(\(([^)]*)\)", pattern).group(1).split("|")
        self.assertEqual(sorted(registry_codes("data-classes.md")), sorted(classes))


class SemanticTests(unittest.TestCase):
    def test_resource_coverage(self):
        self.assertTrue(validate.resource_covers("urn:a:b/*", "urn:a:b/c"))
        self.assertTrue(validate.resource_covers("urn:a:b", "urn:a:b"))
        self.assertFalse(validate.resource_covers("urn:a:b", "urn:a:b/c"))
        self.assertFalse(validate.resource_covers("urn:a:b/*", "urn:a:bc"))

    def test_dropping_a_parent_constraint_widens(self):
        parent = {"action": "pay", "resource": "urn:x", "constraints": {"max_uses": 2}}
        child = {"action": "pay", "resource": "urn:x"}
        self.assertFalse(validate.right_covered(child, parent))


class RepositoryStyleTests(unittest.TestCase):
    def test_no_em_or_en_dashes(self):
        roots = [validate.REPO / d for d in ("schemas", "examples", "tools", "registries", "drafts")]
        roots += sorted(validate.REPO.glob("*.md"))
        for root in roots:
            paths = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
            for path in paths:
                if path.suffix not in TEXT_SUFFIXES:
                    continue
                with self.subTest(file=str(path.relative_to(validate.REPO))):
                    text = path.read_text(encoding="utf-8")
                    for dash in FORBIDDEN_DASHES:
                        self.assertNotIn(dash, text)


if __name__ == "__main__":
    unittest.main()
