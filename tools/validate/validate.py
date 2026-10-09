#!/usr/bin/env python3
# Copyright 2026 The Selfkin Standards contributors
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
"""Validate Selfkin JSON documents against the v0.1 JSON Schemas.

Two layers of checks:

1. Structural checks with JSON Schema 2020-12 (schemas/*.schema.json).
2. Semantic checks that JSON Schema cannot express, for example that a
   delegated capability token only narrows its parent (SK-COM section A6).

The validator does not check signatures, clocks, revocation, or replay.
Those depend on keys and receiver state and belong to a runtime.

Usage:
  python tools/validate/validate.py                 # check every example
  python tools/validate/validate.py FILE --schema envelope
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

REPO = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO / "schemas"
EXAMPLE_DIR = REPO / "examples"
ID_PREFIX = "https://github.com/selfkin/standards/schemas/"
SCHEMA_NAMES = (
    "envelope",
    "capability-token",
    "module-manifest",
    "privacy-report",
    "provider-manifest",
    "refusal",
    "session-record",
)
SESSION_RECORD_TYPE = "application/vnd.selfkin.session-record+json"  # SK-RT section 13
MAX_TOKEN_LIFETIME = timedelta(hours=1)  # SK-COM section A6


# ---------------------------------------------------------------- loading


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_schemas(schema_dir: Path = SCHEMA_DIR) -> dict[str, dict]:
    """Return all schemas keyed by short name (file name without suffix)."""
    schemas = {}
    for path in sorted(schema_dir.glob("*.schema.json")):
        schemas[path.name[: -len(".schema.json")]] = load_json(path)
    return schemas


def build_registry(schemas: dict[str, dict]) -> Registry:
    resources = []
    for name, schema in schemas.items():
        schema_id = schema.get("$id") if isinstance(schema, dict) else None
        if not isinstance(schema_id, str) or not schema_id:
            raise ValueError(f"{name}: schema has no $id, run check_schema_files for details")
        resources.append((schema_id, Resource.from_contents(schema, default_specification=DRAFT202012)))
    return Registry().with_resources(resources)


def make_validator(name: str, schemas: dict[str, dict], registry: Registry) -> Draft202012Validator:
    return Draft202012Validator(schemas[name], registry=registry, format_checker=FormatChecker())


def check_schema_files(schemas: dict[str, dict]) -> list[str]:
    """Meta-validate every schema and check the repository conventions."""
    problems = []
    for name, schema in schemas.items():
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # noqa: BLE001 - report any metaschema error
            problems.append(f"{name}: not a valid 2020-12 schema: {exc}")
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            problems.append(f"{name}: $schema must be JSON Schema 2020-12")
        if schema.get("$id") != f"{ID_PREFIX}{name}.schema.json":
            problems.append(f"{name}: $id must be {ID_PREFIX}{name}.schema.json")
        for key in ("title", "description"):
            if not schema.get(key):
                problems.append(f"{name}: missing {key}")
    for name in SCHEMA_NAMES:
        if name not in schemas:
            problems.append(f"missing schema: {name}")
    return problems


# ---------------------------------------------------------------- helpers


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def decimal(value: str) -> Decimal:
    """Exact decimal for money amounts (common.schema.json money.amount is a decimal string)."""
    return Decimal(value)


def resource_covers(parent: str, child: str) -> bool:
    """True if the parent resource covers the child resource."""
    if parent == child:
        return True
    if parent.endswith("/*"):
        prefix = parent[:-1]
        return child.startswith(prefix)
    return False


def right_covered(child: dict, parent: dict) -> bool:
    if child["action"] != parent["action"]:
        return False
    if not resource_covers(parent["resource"], child["resource"]):
        return False
    pc = parent.get("constraints", {})
    cc = child.get("constraints", {})
    if "max_amount" in pc:
        if "max_amount" not in cc:
            return False
        if cc["max_amount"]["currency"] != pc["max_amount"]["currency"]:
            return False
        if decimal(cc["max_amount"]["amount"]) > decimal(pc["max_amount"]["amount"]):
            return False
    if "max_uses" in pc and ("max_uses" not in cc or cc["max_uses"] > pc["max_uses"]):
        return False
    if "data_classes" in pc:
        if "data_classes" not in cc or not set(cc["data_classes"]) <= set(pc["data_classes"]):
            return False
    return True


def budget_problems(child: dict, parent: dict) -> list[str]:
    problems = []
    pb = parent.get("budget", {})
    cb = child.get("budget", {})
    for key in ("messages", "compute_units"):
        if key in pb and (key not in cb or cb[key] > pb[key]):
            problems.append(f"budget.{key} widens the parent budget")
    if "money" in pb:
        cm = cb.get("money")
        if cm is None or cm["currency"] != pb["money"]["currency"] or decimal(cm["amount"]) > decimal(pb["money"]["amount"]):
            problems.append("budget.money widens or drops the parent budget")
    return problems


# ---------------------------------------------------------------- semantic checks


def check_token(token: dict, where: str = "token") -> list[str]:
    """Attenuation and lifetime checks for a Selfkin capability token (SK-COM A6)."""
    problems = []
    links = list(token.get("chain", [])) + [token]
    for index, link in enumerate(links):
        label = where if index == len(links) - 1 else f"{where}.chain[{index}]"
        if parse_time(link["exp"]) <= parse_time(link["iat"]):
            problems.append(f"{label}: exp must be later than iat")
        elif parse_time(link["exp"]) - parse_time(link["iat"]) > MAX_TOKEN_LIFETIME:
            problems.append(f"{label}: lifetime exceeds the 1 hour maximum (SK-COM section A6)")
        if "nbf" in link and parse_time(link["nbf"]) >= parse_time(link["exp"]):
            problems.append(f"{label}: nbf must be earlier than exp")
    for index in range(1, len(links)):
        parent, child = links[index - 1], links[index]
        label = where if index == len(links) - 1 else f"{where}.chain[{index}]"
        if child["iss"] != parent["sub"]:
            problems.append(f"{label}: iss must equal the parent's sub (holder delegates)")
        if child["aud"] != parent["aud"]:
            problems.append(f"{label}: aud must equal the parent's aud (audience cannot change on delegation)")
        if parse_time(child["exp"]) > parse_time(parent["exp"]):
            problems.append(f"{label}: exp is later than the parent's exp (lifetime widened)")
        for right in child["rights"]:
            if not any(right_covered(right, p) for p in parent["rights"]):
                problems.append(f"{label}: right {right['action']} on {right['resource']} is not covered by the parent (rights widened)")
        problems.extend(f"{label}: {p}" for p in budget_problems(child, parent))
    return problems


def check_envelope(env: dict) -> list[str]:
    problems = []
    if parse_time(env["expires"]) <= parse_time(env["issued"]):
        problems.append("expires must be later than issued")
    token = env.get("cap_token")
    if isinstance(token, dict) and "rights" in token:
        problems.extend(check_token(token, "cap_token"))
        if token["aud"] != env["aud"]:
            problems.append("cap_token.aud must equal the envelope aud")
        if token["sub"] != env["sender_agent"]:
            problems.append("cap_token.sub must equal sender_agent (token is sender-bound)")
        instr = env.get("instructions")
        if instr and not any(r["action"] == instr["action"] for r in token["rights"]):
            problems.append("instructions.action is not granted by cap_token")
    return problems


def check_module_manifest(manifest: dict) -> list[str]:
    problems = []
    declared = set(manifest["data_classes"])
    for index, dest in enumerate(manifest["egress"]):
        extra = set(dest["data_classes"]) - declared
        if extra:
            problems.append(f"egress[{index}] sends undeclared data classes: {sorted(extra)}")
    if manifest["egress"] and manifest.get("resources", {}).get("network") is False:
        problems.append("egress is declared but resources.network is false")
    return problems


def check_provider_manifest(manifest: dict) -> list[str]:
    problems = []
    audit = manifest.get("transparency", {}).get("audit")
    if audit:
        issued = parse_time(audit["issued"])
        until = parse_time(audit["valid_until"])
        if until <= issued:
            problems.append("audit.valid_until must be later than audit.issued")
        if until > issued + timedelta(days=731):
            problems.append("audit must be renewed at least every two years (SK-PRV section 10)")
    return problems


def check_privacy_report(report: dict) -> list[str]:
    problems = []
    overlap = set(report["sent"]["fields"]) & set(report["redacted"]["fields"])
    if overlap:
        problems.append(f"fields listed as both sent and redacted: {sorted(overlap)}")
    return problems


def profile_tier(profile: str) -> int:
    """Tier of a runtime, communication, or provider profile tag: R0 to R3, C0 to C3, P0 to P3."""
    return int(profile[1])


def session_profiles(record: dict) -> set[str]:
    profiles = {record["runtime_profile"]}
    profiles.update(hop["profile"] for hop in record["hops"])
    profiles.update(egress["provider_profile"] for egress in record["egress"])
    return profiles


def check_session_record(record: dict) -> list[str]:
    """Report links and the effective tier display (SK-RT section 5, section 13, section 21)."""
    problems = []
    for index, egress in enumerate(record["egress"]):
        if egress["report"]["payload_digest"] != egress["payload_digest"]:
            problems.append(f"egress[{index}]: the report's payload_digest does not match the egress (no matching report)")
    display = record["tier_display"]
    if display["session"] != record["session"]:
        problems.append("tier_display.session is not this session")
    if display["sig"]["kid"] != record["core"]["kid"]:
        problems.append("tier_display is not signed by the Core key")
    if "signer" in display["sig"] and display["sig"]["signer"] != record["core"]["agent"]:
        problems.append("tier_display signer is not the Core")
    profiles = session_profiles(record)
    hidden = profiles - set(display["shows"])
    if hidden:
        problems.append(f"tier_display hides profiles of the session: {sorted(hidden)}")
    extra = set(display["shows"]) - profiles
    if extra:
        problems.append(f"tier_display shows profiles the session does not have: {sorted(extra)}")
    effective = min(profile_tier(p) for p in profiles)
    if display["tier"] > effective:
        problems.append(f"tier_display.tier {display['tier']} is higher than the effective tier {effective}")
    if record["runtime_profile"] == "R0" and "prototype" not in display["labels"]:
        problems.append("an R0 runtime must show the prototype label")
    return problems


def check_session(envelope: dict, core_kid: str, schemas: dict[str, dict], registry: Registry) -> list[str]:
    """A session record as received: a valid envelope signed by the Core key, carrying a valid session record.

    Checks key binding (kid), not cryptography: like the rest of the validator it does not verify signatures.
    """
    problems = validate_document(envelope, "envelope", schemas, registry)
    if problems:
        return problems
    if envelope.get("payload_type") != SESSION_RECORD_TYPE:
        return [f"payload_type must be {SESSION_RECORD_TYPE}"]
    if envelope["sig"]["kid"] != core_kid:
        problems.append("envelope is not signed by the Core key")
    record = envelope["data"]
    problems.extend(f"data: {p}" for p in validate_document(record, "session-record", schemas, registry))
    if problems:
        return problems
    if record["core"]["kid"] != core_kid:
        problems.append("data.core.kid is not the Core key")
    if record["core"]["agent"] != envelope["sender_agent"]:
        problems.append("data.core.agent is not the envelope sender")
    if record["session"] != envelope["session"]:
        problems.append("data.session is not the envelope session")
    return problems


SEMANTIC = {
    "envelope": check_envelope,
    "capability-token": check_token,
    "module-manifest": check_module_manifest,
    "provider-manifest": check_provider_manifest,
    "privacy-report": check_privacy_report,
    "refusal": lambda document: [],
    "session-record": check_session_record,
}


# ---------------------------------------------------------------- validation


def validate_document(document, name: str, schemas: dict[str, dict], registry: Registry) -> list[str]:
    """Return a list of problems; empty means the document is valid."""
    validator = make_validator(name, schemas, registry)
    problems = []
    for error in sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path)):
        location = "/".join(str(p) for p in error.absolute_path) or "(root)"
        message = error.message
        if len(message) > 200:
            message = f"failed '{error.validator}' check at {'/'.join(str(p) for p in error.absolute_schema_path)}"
        problems.append(f"{location}: {message}")
    if not problems:
        try:
            problems.extend(SEMANTIC[name](document))
        except ValueError as exc:  # for example a timestamp that matches the pattern but is not a real date
            problems.append(f"(semantic): {exc}")
    return problems


def schema_for_example(path: Path) -> str:
    matches = [n for n in SCHEMA_NAMES if path.name.startswith(n + ".")]
    if not matches:
        raise ValueError(f"{path.name}: file name must start with a schema name")
    return max(matches, key=len)


def example_files(example_dir: Path = EXAMPLE_DIR) -> list[Path]:
    return sorted(example_dir.glob("*.json"))


def load_checked() -> tuple[dict[str, dict], Registry]:
    """Load the schemas and build the registry, failing with a clear message."""
    schemas = load_schemas()
    problems = check_schema_files(schemas)
    if problems:
        raise SystemExit("schema problems:\n" + "\n".join(f"SCHEMA  {p}" for p in problems))
    return schemas, build_registry(schemas)


def run_examples(verbose: bool = True) -> int:
    schemas, registry = load_checked()
    failures: list[str] = []
    files = example_files()
    if not files:
        failures.append("no examples found")
    for path in files:
        name = schema_for_example(path)
        expect_valid = not path.name.endswith(".invalid.json")
        problems = validate_document(load_json(path), name, schemas, registry)
        ok = (not problems) == expect_valid
        status = "ok  " if ok else "FAIL"
        expectation = "valid" if expect_valid else "invalid"
        if verbose or not ok:
            print(f"{status}  {path.relative_to(REPO)} (expected {expectation}, schema {name})")
            for problem in problems if (verbose and not expect_valid) or not ok else []:
                print(f"        - {problem}")
        if not ok:
            failures.append(str(path))
    print(f"\n{len(files)} examples checked, {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", type=Path, help="JSON files to validate (default: all examples)")
    parser.add_argument("--schema", choices=SCHEMA_NAMES, help="schema to use for FILES (default: from file name)")
    parser.add_argument("-q", "--quiet", action="store_true", help="only print failures")
    args = parser.parse_args(argv)
    if not args.files:
        return run_examples(verbose=not args.quiet)
    schemas, registry = load_checked()
    status = 0
    for path in args.files:
        try:
            name = args.schema or schema_for_example(path)
            document = load_json(path)
        except (OSError, ValueError) as exc:  # unreadable file, bad JSON, or unknown file name
            print(f"ERROR   {path}: {exc}")
            status |= 2
            continue
        problems = validate_document(document, name, schemas, registry)
        print(f"{'valid  ' if not problems else 'INVALID'} {path} ({name})")
        for problem in problems:
            print(f"        - {problem}")
        status |= 1 if problems else 0
    return status


if __name__ == "__main__":
    sys.exit(main())
