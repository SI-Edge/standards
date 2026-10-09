# Test Vectors

> **Status: Draft, not for implementation.** Shared conformance test vectors for the Selfkin drafts, phase 1. Licensed under Apache-2.0 ([LICENSE-CODE](../LICENSE-CODE)).

Each vector is a fixed input with an expected result, so that the validator in [../tools/validate](../tools/validate), the [reference implementation](https://github.com/selfkin/reference), and any other implementation can check themselves against the same files.

## Layout

| Path | Contents |
|---|---|
| `VERSION` | Suite version, the only place it is recorded |
| `vector.schema.json` | JSON Schema 2020-12 for every vector file |
| `keys/rfc8032-test-keys.json` | Ed25519 test keys copied from [RFC 8032, section 7.1](https://www.rfc-editor.org/rfc/rfc8032#section-7.1). **TEST ONLY** |
| `resource-matching/` | Whether a right resource covers a requested resource (SK-COM §A6) |
| `tokens/` | Capability token lifetime, attenuation rules (a) to (f), budgets and constraints (SK-COM §A6) |
| `envelope/` | Envelope structure and token binding (SK-COM §A5, §A5.2, §A6), and receive sequences (§A5, §A6, §A9) |
| `residency/` | Residency tag syntax and intersection (SK-RT §11) |
| `signatures/` | RFC 8032 known answers, `jcs` signing input, signing, and verification (SK-COM §A5.1) |
| `slice/` | Vertical slice: a session record in a Core-signed envelope, one privacy report per egress, and the Core-rendered effective tier display (SK-RT §5, §13, §21) |

## Vector Format

A file holds `category`, `description`, and a list of `vectors`. Files do not record the suite version; it lives only in `VERSION`. Each vector has:

- `id`: stable and never reused, for example `token.narrowing.004`.
- `spec`: the rules it tests (document, version, section, profile tag).
- `operation`: what to run (below), with its `input`.
- `expected`: `{"result": "accept"}`, `{"result": "refuse", "reason": ...}`, or `{"value": ...}`. A `reason` is a code from [registries/refusal-reasons.md](../registries/refusal-reasons.md), or a list of acceptable codes where the drafts do not fix the order of checks. It is absent where the drafts do not fix a code; then any refusal passes.
- `status`: `normative` (follows from merged draft text) or `provisional` (an interim reading of an open question, named in `open_issue`). Provisional failures are reported but should not fail a run.
- Optional `requires` (features such as `EdDSA` or `jcs`; runners without them skip the vector) and `note` (for readers, never compared).

### Sequence Vectors

A vector with `"kind": "sequence"` has an initial `state` and ordered `steps` instead of `operation`, `input`, and `expected`. Each step has its own `operation`, `now` (the receiver's clock for that step), `input`, and `expected`, and sees the state left by the steps before it (seen nonces, executed `idem_key` values, usage counters). A step's `expected` has `result` (with an optional `reason`), `executed` (whether the requested action ran), or both; absent members are not compared. Steps are in time order. A runner that does not support every step skips the whole vector.

Each vector has one fault, so the expected result does not depend on check order. Signatures inside token and envelope inputs are placeholders, as in [examples/](../examples/); those operations do not check signatures. The `slice/` vectors are the exception: their signatures are real Ed25519 signatures over `jcs` with the test keys, so a runner can verify them.

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
| `session-check` | `envelope`, `core_kid`, `public_key` (name in the key file of the Core key) | accept or refuse: the envelope as in `envelope-check`, signed by the Core key, carrying a session record (`schemas/session-record.schema.json`) whose core is the sender; every egress has a report with the same payload digest; the tier display is for this session, signed by the Core key, shows every runtime, hop, and provider profile of the session, and is not higher than their lowest tier; an R0 session shows `prototype`. Runners with `EdDSA` and `jcs` also verify the envelope and display signatures against `public_key`; the token signature is by `rfc8032-test-3` (owner) |
| `receive` (sequence steps) | `envelope`; state `receiver` (its identity), optional `seen_nonces` | accept or refuse, and `executed`. Everything `envelope-check` covers, plus `aud` against the receiver, `expires` against `now`, replayed nonces, `idem_key` at most once, and usage counting. Signatures, sender identity, pairing, residency, `cnf`, root issuer trust, and local policy are assumed to pass; the requested action has a local handler |

## Keys

The only keys are the Ed25519 test keys published in [RFC 8032, section 7.1](https://www.rfc-editor.org/rfc/rfc8032#section-7.1) (TEST 1, 2, and 3), copied unchanged. They are public, **for tests only**, and must never be used to sign anything real. Ed25519 signatures are deterministic, so `sign` vectors have exact expected values. [../.gitleaks.toml](../.gitleaks.toml) allows these files in secret scans.

Not yet covered: `dcbor` signatures (open question #10) and signatures on delegated token chains (#17).

## Running

```sh
pip install -r tools/validate/requirements.txt
python -m unittest discover -s tools/validate -v   # includes the vectors
python tools/validate/test_vectors.py --summary    # pass, fail, and skip per file
```

The validator runs `resource-covers`, `token-check`, `envelope-check`, `residency-tag-syntax`, and `session-check` (key binding by `kid`, no signature verification), comparing accept or refuse only because it has no refusal codes, and skips the rest, including `receive` sequences and every vector that lists `requires`. It does check that every envelope a `receive` step expects to be accepted is a valid envelope. Other implementations can read the files directly: validate each file against `vector.schema.json`, run the operations they support, and compare results.

## Status and Versioning

Phase 1 covers rules already in the drafts, and the slice covers the rules it adds to SK-RT: 157 vectors, 132 normative and 25 provisional.

| Category | Normative | Provisional |
|---|---|---|
| Resource matching | 0 | 19 (#23) |
| Tokens | 44 | 0 |
| Envelope (single) | 24 | 2 (#23) |
| Envelope (receive sequences) | 4 | 4 (#22, #24) |
| Residency | 24 | 0 |
| Signatures | 17 | 0 |
| Slice (session record and tier display) | 19 | 0 |

The resource-matching vectors, and two binding vectors that depend on them, are provisional until the matching rule proposed for #23 and #48 is merged. `open_issue` may name an issue or a pull request. Receive sequences about how a repeated `idem_key` is answered (#22) and how usage is counted (#24) are provisional; replay, expiry, audience, and at-most-once execution are normative. Later phases add `dcbor` and chain signatures (#10, #17), root issuers and `cnf` (#19, #20), and more stateful receiver checks such as sequence windows, clock skew, nonce retention, and chain-wide budget counting (#21, #22, #24).

The current suite version is `0.2.0`. `VERSION` is its only source, and a test checks that this sentence matches it, so a version bump changes `VERSION` and this line and nothing else. The suite follows semantic versioning: patch for new vectors, minor for new operations or fields, major for changed expectations. A vector whose expectation changes gets a new `id`; old ids are never reused. [examples/](../examples/) stay as readable whole documents; vectors are minimal checks with expected results and do not refer to example files.
