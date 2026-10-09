# Test Vectors

> **Status: Draft, not for implementation.** Shared conformance test vectors for the Selfkin drafts, phase 1. Licensed under Apache-2.0 ([LICENSE-CODE](../LICENSE-CODE)).

Each vector is a fixed input with an expected result, so that the validator in [../tools/validate](../tools/validate), the [reference implementation](https://github.com/selfkin/reference), and any other implementation can check themselves against the same files.

## Layout

| Path | Contents |
|---|---|
| `VERSION` | Suite version |
| `vector.schema.json` | JSON Schema 2020-12 for every vector file |
| `keys/rfc8032-test-keys.json` | Ed25519 test keys copied from [RFC 8032, section 7.1](https://www.rfc-editor.org/rfc/rfc8032#section-7.1). **TEST ONLY** |
| `resource-matching/` | Whether a right resource covers a requested resource (SK-COM §A6) |
| `tokens/` | Capability token lifetime, attenuation rules (a) to (f), budgets and constraints (SK-COM §A6) |
| `envelope/` | Envelope structure and token binding (SK-COM §A5, §A5.2, §A6) |
| `residency/` | Residency tag syntax and intersection (SK-RT §11) |
| `signatures/` | RFC 8032 known answers, `jcs` signing input, signing, and verification (SK-COM §A5.1) |

## Vector Format

A file holds `suite`, `category`, `description`, and a list of `vectors`. Each vector has:

- `id`: stable and never reused, for example `token.narrowing.004`.
- `spec`: the rules it tests (document, version, section, profile tag).
- `operation`: what to run (below), with its `input`.
- `expected`: `{"result": "accept"}`, `{"result": "refuse", "reason": ...}`, or `{"value": ...}`. A `reason` is a code from [registries/refusal-reasons.md](../registries/refusal-reasons.md), or a list of acceptable codes where the drafts do not fix the order of checks. It is absent where the drafts do not fix a code; then any refusal passes.
- `status`: `normative` (follows from merged draft text) or `provisional` (an interim reading of an open question, named in `open_issue`). Provisional failures are reported but should not fail a run.
- Optional `requires` (features such as `EdDSA` or `jcs`; runners without them skip the vector) and `note` (for readers, never compared).

Each vector has one fault, so the expected result does not depend on check order. Signatures inside token and envelope inputs are placeholders, as in [examples/](../examples/); those operations do not check signatures.

## Operations

| Operation | Input | Output |
|---|---|---|
| `resource-covers` | `right`, `resource` (strings) | `value`: true if the right resource covers the resource |
| `token-check` | `token` | accept or refuse: schema, lifetime (at most 1 hour, `exp` after `iat`, `nbf` before `exp`) and attenuation of every link. No clock, signatures, `cnf`, or trust anchors |
| `envelope-check` | `envelope` | accept or refuse: version, schema, `expires` after `issued`, the token as in `token-check`, and token binding (`sub`, `aud`, rights cover the instruction). No clock, signatures, replay, or session state |
| `residency-regions` | `tags`, optional `owner_tags` (tag to list of regions) | `value`: sorted regions where the data may go (`CH` for Switzerland, `EU` for EU and EEA member states), `"any"` for no restriction, or refuse |
| `residency-tag-syntax` | `tag` | `value`: true if the tag is well-formed |
| `ed25519-sign` | `key` (name in the key file), `message_hex` | `value`: signature as hex |
| `jcs-signing-input` | `object` | `value`: RFC 8785 canonical JSON of the object without `sig`, as a string |
| `sign` | `object`, `key`, `canon` | `value`: the resulting `sig.value` (unpadded base64url) |
| `verify` | `object`, `public_key` (name in the key file) | accept or refuse with `bad-signature`. Whether the key belongs to the signer is out of scope |

## Keys

The only keys are the Ed25519 test keys published in [RFC 8032, section 7.1](https://www.rfc-editor.org/rfc/rfc8032#section-7.1) (TEST 1, 2, and 3), copied unchanged. They are public, **for tests only**, and must never be used to sign anything real. Ed25519 signatures are deterministic, so `sign` vectors have exact expected values. [../.gitleaks.toml](../.gitleaks.toml) allows these files in secret scans.

Not yet covered: `dcbor` signatures (open question #10) and signatures on delegated token chains (#17).

## Running

```
pip install -r tools/validate/requirements.txt
python -m unittest discover -s tools/validate -v   # includes the vectors
python tools/validate/test_vectors.py --summary    # pass, fail, and skip per file
```

The validator runs `resource-covers`, `token-check`, `envelope-check`, and `residency-tag-syntax`, comparing accept or refuse only because it has no refusal codes, and skips the rest. Other implementations can read the files directly: validate each file against `vector.schema.json`, run the operations they support, and compare results.

## Status and Versioning

Phase 1 covers rules already in the drafts. The resource-matching vectors, and two binding vectors that depend on them, are provisional until the matching rule proposed for #23 and #48 is merged. Later phases add `dcbor` and chain signatures (#10, #17), root issuers and `cnf` (#19, #20), and stateful receiver checks such as sequence windows, nonces, `idem_key`, clock skew, and budget counting (#21, #22, #24).

The suite follows semantic versioning in `VERSION`: patch for new vectors, minor for new operations or fields, major for changed expectations. A vector whose expectation changes gets a new `id`; old ids are never reused. [examples/](../examples/) stay as readable whole documents; vectors are minimal checks with expected results and do not refer to example files.
