# Test Vectors

> **Status: Draft, not for implementation.** Shared conformance test vectors for the Selfkin drafts, phase 1. Licensed under Apache-2.0 ([LICENSE-CODE](../LICENSE-CODE)).

Each vector is a fixed input with an expected result, so that the validator in [../tools/validate](../tools/validate), the [reference implementation](https://github.com/selfkin/reference), and any other implementation can check themselves against the same files.

## Layout

| Path | Contents |
|---|---|
| `VERSION` | Suite version |
| `vector.schema.json` | JSON Schema 2020-12 for every vector file |
| `keys/rfc8032-test-keys.json` | Ed25519 test keys copied from [RFC 8032, section 7.1](https://www.rfc-editor.org/rfc/rfc8032#section-7.1). **TEST ONLY** |
| `keys/rfc7515-test-keys.json` | ECDSA P-256 test key copied from [RFC 7515, Appendix A.3](https://www.rfc-editor.org/rfc/rfc7515#appendix-A.3). **TEST ONLY** |
| `resource-matching/` | Whether a right resource covers a requested resource (SK-COM §A6) |
| `tokens/` | Capability token lifetime, attenuation rules (a) to (f), budgets and constraints (SK-COM §A6) |
| `envelope/` | Envelope structure and token binding (SK-COM §A5, §A5.2, §A6), and receive sequences (§A5, §A6, §A9) |
| `residency/` | Residency tag syntax and intersection (SK-RT §11) |
| `signatures/` | RFC 8032 known answers, `dcbor` and `jcs` signing input, signing, and verification (SK-COM §A5.1, Appendix F) |

## Vector Format

A file holds `suite`, `category`, `description`, and a list of `vectors`. Each vector has:

- `id`: stable and never reused, for example `token.narrowing.004`.
- `spec`: the rules it tests (document, version, section, profile tag).
- `operation`: what to run (below), with its `input`.
- `expected`: `{"result": "accept"}`, `{"result": "refuse", "reason": ...}`, or `{"value": ...}`. A `reason` is a code from [registries/refusal-reasons.md](../registries/refusal-reasons.md), or a list of acceptable codes where the drafts do not fix the order of checks. It is absent where the drafts do not fix a code; then any refusal passes.
- `status`: `normative` (follows from merged draft text), `provisional` (an interim reading of an open question, named in `open_issue`), or `withdrawn` (no longer valid because the drafts changed; its `note` names the replacement). Provisional failures are reported but should not fail a run. Withdrawn vectors stay in their file so that the id is never reused, and are never run.
- Optional `requires` (features such as `EdDSA`, `ES256`, `jcs`, or `dcbor`; runners without them skip the vector) and `note` (for readers, never compared).

### Sequence Vectors

A vector with `"kind": "sequence"` has an initial `state` and ordered `steps` instead of `operation`, `input`, and `expected`. Each step has its own `operation`, `now` (the receiver's clock for that step), `input`, and `expected`, and sees the state left by the steps before it (seen nonces, executed `idem_key` values, usage counters). A step's `expected` has `result` (with an optional `reason`), `executed` (whether the requested action ran), or both; absent members are not compared. Steps are in time order. A runner that does not support every step skips the whole vector.

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
| `dcbor-signing-input` | `object` | `value`: the `dcbor` signing input of the object without `sig` (SK-COM §A5.1, Appendix F), as lowercase hex |
| `jcs-signing-input` | `object` | `value`: RFC 8785 canonical JSON of the object without `sig`, as a string |
| `sign` | `object`, `key`, `canon` | `value`: the resulting `sig.value` (unpadded base64url) |
| `verify` | `object`, `public_key` (name in the key file) | accept or refuse with `bad-signature`. Whether the key belongs to the signer is out of scope |
| `receive` (sequence steps) | `envelope`; state `receiver` (its identity), optional `seen_nonces` | accept or refuse, and `executed`. Everything `envelope-check` covers, plus `aud` against the receiver, `expires` against `now`, replayed nonces, `idem_key` at most once, and usage counting. Signatures, sender identity, pairing, residency, `cnf`, root issuer trust, and local policy are assumed to pass; the requested action has a local handler |

## Keys

The only keys are the Ed25519 test keys published in [RFC 8032, section 7.1](https://www.rfc-editor.org/rfc/rfc8032#section-7.1) (TEST 1, 2, and 3) and the ECDSA P-256 key published in [RFC 7515, Appendix A.3](https://www.rfc-editor.org/rfc/rfc7515#appendix-A.3), copied unchanged. They are public, **for tests only**, and must never be used to sign anything real. Ed25519 signatures are deterministic, so `sign` vectors have exact expected values; ECDSA signatures are randomized, so P-256 keys appear only in `verify` vectors. [../.gitleaks.toml](../.gitleaks.toml) allows these files in secret scans.

Signatures on delegated token chains (#17) are covered by `verify` on a link whose `chain` was already rebuilt; an operation that rebuilds the chain itself is not yet defined.

## Running

```sh
pip install -r tools/validate/requirements.txt
python -m unittest discover -s tools/validate -v   # includes the vectors
python tools/validate/test_vectors.py --summary    # pass, fail, and skip per file
```

The validator runs `resource-covers`, `token-check`, `envelope-check`, and `residency-tag-syntax`, comparing accept or refuse only because it has no refusal codes, and skips the rest, including `receive` sequences. It does check that every envelope a `receive` step expects to be accepted is a valid envelope. Other implementations can read the files directly: validate each file against `vector.schema.json`, run the operations they support, and compare results.

## Status and Versioning

The suite has 164 vectors: 140 normative, 22 provisional, and 2 withdrawn.

| Category | Normative | Provisional | Withdrawn |
|---|---|---|---|
| Resource matching | 0 | 19 (#23) | 0 |
| Tokens | 48 | 0 | 1 |
| Envelope (single) | 25 | 2 (#23) | 1 |
| Envelope (receive sequences) | 11 | 1 (#22) | 0 |
| Residency | 24 | 0 | 0 |
| Signatures | 32 | 0 | 0 |

The resource-matching vectors, and two binding vectors that depend on them, are provisional until the matching rule proposed for #23 and #48 is merged. `open_issue` may name an issue or a pull request. Receive sequences about how a repeated `idem_key` is answered (#22) are provisional; replay, expiry, audience, at-most-once execution, and usage counting along the whole chain (#24, from 0.2.1) are normative. The `dcbor` signing input, `dcbor` signatures, chain link signatures, and the timestamp, number, and text rules for signed objects (#10, #17) were added in 0.2.0. Later phases add freshness checks against a clock, such as a future `iat` (#47) and `max_clock_skew`, root issuers and `cnf` (#19, #20), and more stateful receiver checks such as sequence windows, clock skew, and nonce retention (#21, #22), and `compute_units` and `money` charging, which needs a cost input for `receive` steps (#24).

Also in 0.2.0: `envelope.structure.007` and `token.lifetime.003` accepted timestamps with an offset in signed objects and are `withdrawn`; `envelope.signed-values.001` and `token.signed-values.001` replace them.

The suite follows semantic versioning in `VERSION`: patch for new vectors, minor for new operations or fields. A changed expectation is a major change from 1.0; while the suite is 0.x, it takes a minor bump and a CHANGELOG note instead. A vector whose expectation changes is marked `withdrawn` and replaced by a vector with a new `id`; old ids are never reused. Every file's `suite` equals `VERSION`. [examples/](../examples/) stay as readable whole documents; vectors are minimal checks with expected results and do not refer to example files.
