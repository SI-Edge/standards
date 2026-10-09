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
| `keys/rfc9180-test-keys.json` | X25519 test keys copied from [RFC 9180, Appendix A.2.1](https://www.rfc-editor.org/rfc/rfc9180#appendix-A.2.1). **TEST ONLY** |
| `resource-matching/` | Whether a right resource covers a requested resource (SK-COM §A6) |
| `tokens/` | Capability token lifetime, attenuation rules (a) to (f), budgets and constraints (SK-COM §A6) |
| `envelope/` | Envelope structure and token binding (SK-COM §A5, §A5.2, §A6), and receive sequences (§A5, §A6, §A9) |
| `residency/` | Residency tag syntax and intersection (SK-RT §11) |
| `signatures/` | RFC 8032 known answers, `dcbor` and `jcs` signing input, signing, and verification (SK-COM §A5.1, Appendix F) |
| `wire/` | Frames, QR pairing, advertisement names, chunks, sealed frames, and prekeys of the wire binding ([SK-WIRE](../drafts/sk-wire/wire-binding-v0.1.md)); all provisional |

## Vector Format

A file holds `suite`, `category`, `description`, and a list of `vectors`. Each vector has:

- `id`: stable and never reused, for example `token.narrowing.004`.
- `spec`: the rules it tests (document, version, section, profile tag).
- `operation`: what to run (below), with its `input`.
- `expected`: `{"result": "accept"}`, `{"result": "refuse", "reason": ...}`, or `{"value": ...}`. A `reason` is a code from [registries/refusal-reasons.md](../registries/refusal-reasons.md), or a list of acceptable codes where the drafts do not fix the order of checks. It is absent where the drafts do not fix a code; then any refusal passes.
- `status`: `normative` (follows from merged draft text), `provisional` (an interim reading of an open question, named in `open_issue`), or `withdrawn` (no longer valid because the drafts changed; its `note` names the replacement). Provisional failures are reported but should not fail a run. Withdrawn vectors stay in their file so that the id is never reused, and are never run.
- Optional `requires` (features such as `EdDSA`, `ES256` (producing ES256 signatures; verifying them is mandatory), `jcs`, or `dcbor`; runners without them skip the vector) and `note` (for readers, never compared).

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
| `receive` (sequence steps) | `envelope`, optional `delivery` (`direct`, the default, or `store-and-forward`); state `receiver` (its identity), optional `seen_nonces`, optional `revoked` (identities and token ids revoked before the first step) | accept or refuse, and `executed`. Everything `envelope-check` covers, plus `aud` against the receiver, `expires` against `now`, the time validity of the token and its chain at `now` (at the envelope's `issued` for `store-and-forward` delivery without `instructions`, SK-COM §A9), the 7-day lifetime and `issued` not after `now` for `store-and-forward`, revocation, replayed nonces, `idem_key` at most once, and usage counting. Signatures, sender identity, pairing, residency, `cnf`, root issuer trust, and local policy are assumed to pass; the requested action has a local handler |
| `wire-frame-check` | `frame_hex` (CBOR) | accept or refuse with `malformed`: the frame against `wire-frame` in [wire-binding-v0.1.cddl](../drafts/sk-wire/wire-binding-v0.1.cddl). Structure only: no signatures, tokens, clocks, or state |
| `wire-qr-decode` | `qr` (string) | `value`: `version`, `presenter`, `spki_hex`, `endpoints` (host, port, carrier), `secret_hex`, `expires`; or refuse with `malformed` (prefix other than `SK1:`, invalid base45, or a payload outside `qr-payload`) |
| `wire-pairing-proof` | `secret_hex`, `label` (`request` or `response`), `presenter`, `scanner`, `spki_hex` | `value`: the pairing proof (SK-WIRE §4.3), unpadded base64url |
| `wire-sas` | `secret_hex`, `request_hash_hex` (SHA-256 of the `dcbor` pairing request envelope) | `value`: the 6-digit comparison code as a string (SK-WIRE §4.3) |
| `wire-adv-name` | `adv_key_hex`, `unix_time` | `value`: the 16-character service instance name (SK-WIRE §4.1) |
| `wire-chunk-open` | `key_hex`, `index`, `count`, `chunk_id_hex`, `ct_hex` | `value`: plaintext as hex, or refuse if the chunk id or the decryption fails (SK-WIRE §5.2) |
| `wire-hpke-seal` | `suite`, `public_key` (recipient), `ephemeral_key` (names in the key file), `plaintext_hex` | `value`: `enc_hex` and `ct_hex` of HPKE base mode with `info` = "selfkin/1 sealed" followed by the SHA-256 of the recipient public key and empty associated data (SK-WIRE §6.3). Only for known answers: real senders use a fresh ephemeral key |
| `wire-hpke-open` | `key` (recipient, name in the key file), `frame_hex` (sealed frame) | `value`: the opened envelope frame as hex, or refuse if `rk` does not name the key, the suite is not supported, or opening fails |
| `wire-prekey-select` | `suites` (the sender's, most preferred first), `stock` (`one_time` and `last_resort` lists of `kid` and `suite`) | `value`: the `kid` the mailbox host returns for a `claim` (SK-WIRE §6.3), or refuse if no prekey matches a listed suite |

## Keys

The only keys are the Ed25519 test keys published in [RFC 8032, section 7.1](https://www.rfc-editor.org/rfc/rfc8032#section-7.1) (TEST 1, 2, and 3), the ECDSA P-256 key published in [RFC 7515, Appendix A.3](https://www.rfc-editor.org/rfc/rfc7515#appendix-A.3), and the X25519 keys published in [RFC 9180, Appendix A.2.1](https://www.rfc-editor.org/rfc/rfc9180#appendix-A.2.1), copied unchanged. Wire vectors also carry fixed test secrets inline as hex (a pairing secret, an `adv_key`, a chunk content key), derived from fixed strings; they are test values, not keys. They are public, **for tests only**, and must never be used to sign anything real. Ed25519 signatures are deterministic, so `sign` vectors have exact expected values; ECDSA signatures are randomized, so P-256 keys appear only in `verify` vectors. [../.gitleaks.toml](../.gitleaks.toml) allows these files in secret scans.

Signatures on delegated token chains (#17) are covered by `verify` on a link whose `chain` was already rebuilt; an operation that rebuilds the chain itself is not yet defined.

## Running

```sh
pip install -r tools/validate/requirements.txt
python -m unittest discover -s tools/validate -v   # includes the vectors
python tools/validate/test_vectors.py --summary    # pass, fail, and skip per file
```

The validator runs `resource-covers`, `token-check`, `envelope-check`, and `residency-tag-syntax`, comparing accept or refuse only because it has no refusal codes, and skips the rest, including `receive` sequences. It does check that every envelope a `receive` step expects to be accepted is a valid envelope. Other implementations can read the files directly: validate each file against `vector.schema.json`, run the operations they support, and compare results.

## Status and Versioning

The suite has 221 vectors: 152 normative, 67 provisional, and 2 withdrawn.

| Category | Normative | Provisional | Withdrawn |
|---|---|---|---|
| Resource matching | 0 | 19 (#23) | 0 |
| Tokens | 54 | 0 | 1 |
| Envelope (single) | 27 | 2 (#23) | 1 |
| Envelope (receive sequences) | 10 | 4 (#22, #24) | 0 |
| Residency | 24 | 0 | 0 |
| Signatures | 37 | 0 | 0 |
| Wire binding (SK-WIRE) | 0 | 42 (#67) | 0 |

The resource-matching vectors, and two binding vectors that depend on them, are provisional until the matching rule proposed for #23 and #48 is merged. `open_issue` may name an issue or a pull request. Receive sequences about how a repeated `idem_key` is answered (#22) and how usage is counted (#24) are provisional; replay, expiry, audience, and at-most-once execution are normative. The `dcbor` signing input, `dcbor` signatures, chain link signatures, and the timestamp, number, and text rules for signed objects (#10, #17) were added in 0.2.0. Later phases add freshness checks against a clock, such as a future `iat` (#47) and `max_clock_skew`, root issuers and `cnf` (#19, #20), and more stateful receiver checks such as sequence windows, clock skew, nonce retention, and chain-wide budget counting (#21, #22, #24).

The wire vectors (added in 0.4.0) are provisional until SK-WIRE is accepted (#67). The hybrid HPKE suite has no vector while its code point is provisional.

Also in 0.2.0: `envelope.structure.007` and `token.lifetime.003` accepted timestamps with an offset in signed objects and are `withdrawn`; `envelope.signed-values.001` and `token.signed-values.001` replace them.

The suite follows semantic versioning in `VERSION`: patch for new vectors, minor for new operations or fields. A changed expectation is a major change from 1.0; while the suite is 0.x, it takes a minor bump and a CHANGELOG note instead. A vector whose expectation changes is marked `withdrawn` and replaced by a vector with a new `id`; old ids are never reused. Every file's `suite` equals `VERSION`. [examples/](../examples/) stay as readable whole documents; vectors are minimal checks with expected results and do not refer to example files.
