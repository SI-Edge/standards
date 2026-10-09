# Selfkin JSON Schemas (v0.1)

> **Status: Draft, not for implementation. No certification program exists.** These schemas follow the drafts; where a schema and a draft disagree, the draft wins and the schema has a bug. Licensed under Apache-2.0 ([LICENSE-CODE](../LICENSE-CODE)).

Machine-readable versions of the data structures defined in the drafts, written in [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/schema). Examples are in [../examples](../examples), and the validator is in [../tools/validate](../tools/validate). Questions found while writing the schemas, how they were resolved in the drafts, and what remains open are listed in [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md).

## Schemas and Draft Sections

| Schema | `$id` (under `https://github.com/selfkin/standards/schemas/`) | Draft sections |
|---|---|---|
| [envelope.schema.json](envelope.schema.json) | `envelope.schema.json` | SK-COM A5 (fields), A1 (forms), A3 (pairing, F5), A4 (F7 setup), A6 (`cap_token`), A7 (untrusted `data`), A9 (`idem_key`, `seq`, `expires`), A10 (`model_ref`), B1 and B5 (labels and proxy `provenance`); SK-RT 11 (residency tags) |
| [capability-token.schema.json](capability-token.schema.json) | `capability-token.schema.json` | SK-COM A6 (capabilities, short-lived, sender-bound, attenuation, chain), A7 (budgets); SK-RT 15 (scoped, expiring, sender-bound tokens) |
| [module-manifest.schema.json](module-manifest.schema.json) | `module-manifest.schema.json` | SK-RT 3 (signed manifest, permissions, data classes, egress, residency, resources, SBOM, weight hashes, legacy labels), 4 (capability descriptor, safe stop), 6 (permission manifest), 17 (SBOM formats); SK-COM B1 to B6 (legacy methods) |
| [privacy-report.schema.json](privacy-report.schema.json) | `privacy-report.schema.json` | SK-RT 13 (privacy report, full gateway mode, verifiable minimisation, P0 handling), 11 (retention in report, residency, log protection), 14 (model identity); SK-PRV 3 (retention window), 12 (downgrade) |
| [provider-manifest.schema.json](provider-manifest.schema.json) | `provider-manifest.schema.json` | SK-PRV 8 (manifest contents), 2 (anonymous mode, credentials, billing, identified mode), 3 (no training, retention), 4 (no tracking, relays, OHTTP), 5 (attestation), 6 (envelope, residency), 7 (model identity, transparency reports, announced changes), 10 (audit), 11 (profile requirements, self-assessment) |
| [refusal.schema.json](refusal.schema.json) | `refusal.schema.json` | SK-COM A7 (refusal object, `sk.refused`), A5 (refusal envelopes); SK-PRV 6 (residency refusals), 9 (refusal format); [registries/refusal-reasons.md](../registries/refusal-reasons.md) |
| [common.schema.json](common.schema.json) | `common.schema.json` | Shared definitions: identifiers, timestamps, durations, digests, the signature block, residency tags (SK-RT 11, TERMINOLOGY), data classes and intents (registries), the `ext` object (SK-COM A5.2), profile tags (SK-RT 21, SK-COM Part C, SK-PRV 11), trust labels (TERMINOLOGY) |

## Design Rules

- **Fail closed, with one extension point.** Unknown members are rejected (`additionalProperties` or `unevaluatedProperties` set to `false`), except inside the optional `ext` object, whose member names start with `x-` and which receivers ignore if not understood (SK-COM A5.2).
- **Profiles are checked where the document states them.** The provider manifest carries a profile claim, so the schema checks that a P1, P2, or P3 claim states everything that profile requires. A claim is always a self-assessment (`basis: "self-assessment"`), never a certification. Envelopes carry no profile, so profile-dependent envelope rules (for example `attestation_ref` at C3) cannot be checked by the schema.
- **Structure here, semantics in the validator.** JSON Schema cannot compare values across members. tools/validate adds semantic checks: delegated capability tokens only narrow rights, lifetime, and budget, and keep the chain consistent; envelope `expires` is after `issued`; the envelope's token is bound to the sender and the recipient; module egress only uses declared data classes; provider audits are at most two years old.
- **Not checked at all:** signatures, key trust, revocation, replay, clocks, and residency enforcement. These need keys and runtime state.
- **Signatures.** Every signed object has a `sig` block with `alg`, `kid`, `canon` (`dcbor` or `jcs`), `value`, and for manifests `signer`. The signature covers the canonical encoding of the object with `sig` removed; `dcbor` is mandatory to implement (SK-COM A5.1).
- **Versioning.** `v` is `MAJOR.MINOR`, and these schemas accept exactly `0.1`. A document using a later minor version is checked against that version's schemas (SK-COM A5.2).
- **Registries.** Data classes, intents, and refusal reasons are restricted to [../registries](../registries/README.md) or `x-` private codes. The tests check that registries and schemas list the same codes.

## CBOR Encoding (non-normative note)

The JSON Schemas define the data model. A CBOR encoding follows the same data model, encoded as deterministic CBOR as defined in RFC 8949 section 4.2 (Core Deterministic Encoding Requirements), so that signatures over the canonical form are reproducible. Member names stay text strings, timestamps may be carried as CBOR tag 1 (epoch seconds), and binary values that JSON carries as base64url may be carried as CBOR byte strings. This note is non-normative; a normative CBOR profile, including the exact type mappings, is future work. Signatures already use deterministic CBOR (`canon: dcbor`) as the mandatory-to-implement encoding (SK-COM A5.1).

## Validate

```
pip install -r tools/validate/requirements.txt
python tools/validate/validate.py                         # all examples
python tools/validate/validate.py my-envelope.json --schema envelope
python -m unittest discover -s tools/validate -v          # tests
```
