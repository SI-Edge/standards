# Open Questions from Writing the v0.1 Schemas

> **Status: Draft, not for implementation.**

Writing the v0.1 schemas showed 35 places where the drafts were ambiguous, silent, or inconsistent. The owner approved resolving them with the stricter choices the schemas had made, and the 2026-10-09 schema alignment revision folded those resolutions into the drafts (see [CHANGELOG.md](../CHANGELOG.md)). This file lists what was resolved, so reviewers can trace each choice, and what genuinely remains open.

## Still Open

1. **F5 advertisement format.** Advertisements are not envelopes, and their fields, size limits, and identifier rotation are undefined (SK-COM §D Q6).
2. **Capability descriptor vocabulary.** Performance classes are defined (`constrained`, `standard`, `high`), but hardware types and function names have no registry yet (SK-RT §22 Q1).
3. **Maximum provider retention window.** The format is fixed (ISO 8601 duration, purpose required if non-zero), but no maximum exists (SK-PRV §13 Q3).
4. **Private path for streaming provider responses.** Oblivious HTTP covers non-streaming requests only (SK-PRV §13 Q6).
5. **Multi-recipient streams.** `aud` may name one MLS group, but stream setup for groups is not specified (SK-COM §D Q7).
6. **Normative CBOR profile.** Deterministic CBOR is mandatory for signatures, but exact type mappings (timestamps, byte strings, integers) are only a non-normative note ([README.md](README.md)).
7. **Registry stewardship.** Minimal registries exist in [../registries](../registries/README.md); who maintains them after v1.0 and how application domains grow is open (SK-COM §D Q1).

## Resolved in the Drafts

| # | Question | Resolution | Where |
|---|---|---|---|
| 1 | No field marked a pairing message | Pairing uses the reserved `sk.pairing.*` intents, carries no `instructions`, and may omit `cap_token` | SK-COM §A3, §A5; registries/intents.md |
| 2 | Legacy labels had no envelope field | `legacy` and `unattested` sit on the legacy endpoint's `provenance` entry (role `legacy-endpoint`); provenance entry format defined | SK-COM §A5, §B1, §B5 |
| 3 | `attestation_ref` "at C3" not checkable | Always present, `null` unless the session was negotiated at C3; the negotiated profile is bound by the signed transcript, so receivers reject `null` in C3 sessions | SK-COM §A5 |
| 4 | "State-changing" undefined | `idem_key` required whenever `instructions` is present | SK-COM §A5 |
| 5 | Separate signature on `instructions`? | No; authenticated only by the envelope signature | SK-COM §A5.1 |
| 6 | Signature input and canonical encoding | Signature over the canonical encoding without `sig`; `sig.canon` is `dcbor` or `jcs`; `dcbor` mandatory to implement; `jcs` only if negotiated | SK-COM §A5.1, §B7 |
| 7 | One or several recipients | Exactly one `aud`, which may be an MLS group identifier | SK-COM §A5 |
| 8 | Owner-defined residency tag syntax | Must start with `x-` | SK-RT §11, TERMINOLOGY |
| 9 | Several residency tags | Combine by intersection; empty list means no residency restriction set | SK-RT §11, SK-COM §A5 |
| 10 | Data-class vocabulary | Minimal registry; other classes start with `x-` | SK-RT §11; registries/data-classes.md |
| 11 | Intent and refusal vocabularies; refusal format | Intent registry with reserved `sk.*` intents and application domains; refusal object schema and reason-code registry | SK-COM §A5, §A7; schemas/refusal.schema.json; registries/ |
| 12 | F5 in envelopes | F5 never appears in an envelope (advertisement format still open, above) | SK-COM §A5 |
| 13 | Nonce length, timestamp format | Nonce at least 128 bits; RFC 3339 with explicit offset (CBOR tag 1 in CBOR) | SK-COM §A5 |
| 14 | `data` without type | `data` and `payload_type` appear together or not at all | SK-COM §A5 |
| 15 | "Short-lived" tokens had no bound | At most 1 hour from `iat` to `exp`; owner policy may set less | SK-COM §A6 |
| 16 | Attenuation semantics | Rules (a) to (f): `iss` equals parent `sub`, same `aud`, no later `exp`, rights covered by same action and equal or `/*`-prefixed resource, constraints and budgets present and not higher, chain root first with at most 16 links | SK-COM §A6 |
| 17 | Other token formats | Allowed as `{format, token}`; receiver verifies attenuation natively or refuses with `unsupported-token-format` | SK-COM §A6 |
| 18 | Token and envelope binding | Token `sub` equals `sender_agent`, `aud` equals envelope `aud`, rights cover `instructions.action` | SK-COM §A6 |
| 19 | Cross-owner delegation not checkable | Owners determined from owner-signed statements; unattributable chains count as cross-owner | SK-COM §A6 |
| 20 | SBOM at R1 or R2 | SBOM reference and SBOMs both at R1 | SK-RT §3, §17, §21 |
| 21 | Compatibility range meaning and syntax | Range of SK-RT versions with comparators, for example `>=0.3 <0.4` | SK-RT §3 |
| 22 | Hardware as a module kind | New kind `hardware`, distinct from `device-adapter`; both defined | SK-RT §1, §4 |
| 23 | Capability descriptor vocabulary | Performance classes defined; types and functions still open (above) | SK-RT §4 |
| 24 | Two definitions of `sideloaded` | One definition: installed from outside the owner's chosen registries, including self-signed modules | SK-RT §1, §3, TERMINOLOGY |
| 25 | Field values in privacy reports | Field names and data classes only; redaction maps never included | SK-RT §13 |
| 26 | Residency and model identity in reports | Both part of the report | SK-RT §13 |
| 27 | Retention format | ISO 8601 duration or `undeclared` (maximum still open, above) | SK-RT §13, SK-PRV §3 |
| 28 | Report at R2 but gateway at R1 | Privacy reports moved to R1; verifiable minimisation (protected log) stays at R2 and the report hash must match it | SK-RT §13, §21 |
| 29 | "Equivalent mapping" of the envelope | P2 requires the Selfkin Envelope itself | SK-PRV §6 |
| 30 | Audit renewal | Validity ends no later than two years after issue | SK-PRV §10 |
| 31 | Model identity per response | In the response envelope's `model_ref`, or a response header named in the manifest | SK-PRV §7, §8 |
| 32 | Streaming and OHTTP | Recorded as an open question in the provider draft (above) | SK-PRV §13 |
| 33 | P0 manifests | A manifest may claim P0 | SK-PRV §11 |
| 34 | Extensions and minor versions | `ext` object with `x-` members, ignored if not understood, never grants authority; other unknown members rejected; no members from a higher minor version than negotiated | SK-COM §A5.2 |
| 35 | Tier numbers | Machine-readable tier is the integer 0 to 3 | TERMINOLOGY |
