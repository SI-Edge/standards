# Changelog

All notable changes to the Selfkin drafts. Dates are in Europe/Zurich time. All documents are **Draft, not for implementation**.

## 2026-10-09: SK-WIRE v0.1, Selfkin wire binding (proposal, #67)

New document, open for comments.

### Added

- `drafts/sk-wire/wire-binding-v0.1.md`: SK-WIRE v0.1 binds SK-COM to QUIC (ALPN `selfkin/1`) and WebSocket over TLS 1.3, DNS-SD discovery with rotating names, QR pairing, text, photo, view-on-demand and handoff messages, and relay-only delivery of sealed frames (HPKE with signed one-time and last-resort prekeys) through an owner-run mailbox. All identifiers are provisional. Hybrid post-quantum key exchange is preferred; the hybrid HPKE code point is provisional and the X25519 suite must always interoperate.
- `drafts/sk-wire/wire-binding-v0.1.cddl`: CDDL for frames, the QR payload, mailbox control messages, and SK-WIRE payloads.
- `test-vectors/` 0.4.0: category `wire` with 42 provisional vectors, operations `wire-frame-check`, `wire-qr-decode`, `wire-pairing-proof`, `wire-sas`, `wire-adv-name`, `wire-chunk-open`, `wire-hpke-seal`, `wire-hpke-open`, `wire-prekey-select`, and the X25519 test keys of RFC 9180 Appendix A.2.1.

### Changed

- README.md, TERMINOLOGY.md, docs/index.md: list SK-WIRE. README.md: CDDL files under `drafts/` are Apache-2.0 like schemas.

## 2026-10-09: Negotiation without `cap_token`, store-and-forward token time, Noise optional (proposal)

Normative change, open for comments.

### Changed

- SK-COM §A3, §A5, §B7: negotiation messages (`sk.negotiate`) may omit `cap_token` and never carry `instructions`; they grant no authority.
- SK-COM §A9: an envelope delivered through a store-and-forward node (F8) lives at most 7 days. Without `instructions`, its token is evaluated at `issued` and revocation is checked at receipt; with `instructions`, everything is evaluated at receipt.
- SK-COM §A4: TLS 1.3 or QUIC is the default building block also for peer-to-peer paths; the Noise Protocol Framework drops from SHOULD to MAY.
- `schemas/envelope.schema.json` and `registries/intents.md`: `sk.negotiate` joins pairing and refusals as the envelopes that may omit `cap_token`.
- THREAT-MODEL.md T9: revocation is checked at receipt for stored deliveries.
- `test-vectors/` 0.3.0: the `receive` operation gains the input `delivery`, the state `revoked`, and token time checks.

### Added

- Examples `envelope.f1-negotiate-offer.json` and `envelope.negotiate-with-instructions.invalid.json`.
- Test vectors `envelope.structure.017` and `.018` and `envelope.receive.013` to `.018`.

## 2026-10-09: Signature algorithm allowlist and key binding (proposal, #33)

Normative change, open for comments.

### Changed

- SK-COM §A5.1: `Ed25519` is mandatory to implement; `sig.alg` must be one of the algorithms in the new §B8 table (`Ed25519`, `ES256`, which every runtime must verify and may produce, and the deprecated name `EdDSA`, removed in v1.0), so `none` and MACs are refused with `bad-signature`; `kid` must resolve through the owner statements of `sender_agent`, `iss`, or `signer` to a key whose type matches `alg`.
- SK-COM §B8: table of signature algorithms with their status, and a non-normative note that ML-DSA is added only once stable JOSE and COSE registrations exist (to be reconsidered for v0.3).
- `schemas/common.schema.json`: `sig.alg` is an enum.

### Added

- Invalid examples `envelope.alg-none.invalid.json` and `capability-token.alg-hs256.invalid.json`.
- Test vectors `tokens/algorithms.json` and `signature.verify.013` to `.017` (`.015` and `.016` use the RFC 7515 P-256 test key); suite 0.2.1.

## 2026-10-09: Signing input for `dcbor`, chain links, and future `iat` (proposal, #10, #17, #47)

Normative change, open for comments.

### Changed

- SK-COM §A5.1 and new Appendix F: `dcbor` is the core deterministic encoding of RFC 8949 §4.2.1 over the JSON data model, with no type mapping and with numeric reduction (`50.0` is encoded as the integer `50`). Timestamps and base64url values stay text strings, never CBOR tag 1 or byte strings. dCBOR (draft-mcnally-deterministic-cbor-18) is cited as informative prior art only.
- SK-COM §A5, §A5.1: timestamps in signed objects are RFC 3339 in UTC with whole seconds (`YYYY-MM-DDTHH:MM:SSZ`); integral numbers stay in the I-JSON safe range and text is in Unicode Normalization Form C, so `dcbor` and `jcs` agree.
- SK-COM §A5: `max_clock_skew` (30 seconds) is defined once for every rule that allows clock skew.
- SK-COM §A6: every token is signed with `chain` set to its ancestors as carried; a token or link whose `exp` is not after `iat` is refused with `unauthorized`, and one whose `iat` is later than now plus `max_clock_skew` with the new code `not-yet-valid`.
- `schemas/common.schema.json`: new `signedTimestamp`, used for every timestamp in capability tokens, envelopes, and Provider Manifests (privacy reports keep `timestamp`); `not-yet-valid` added to the refusal reasons, and to `registries/refusal-reasons.md`.
- `tools/validate`: checks the number range and NFC in signed objects.
- `test-vectors/` 0.2.0: new status `withdrawn`; while the suite is 0.x, a changed expectation takes a minor bump and a CHANGELOG note. `envelope.structure.007` and `token.lifetime.003` (offsets in signed timestamps) are withdrawn and replaced by `envelope.signed-values.001` and `token.signed-values.001`. The key test accepts the published RFC 8032 and RFC 7515 test keys.

### Added

- Invalid examples `capability-token.offset-timestamp.invalid.json`, `capability-token.unsafe-integer.invalid.json`, and `envelope.fractional-seconds.invalid.json`.
- Test vectors: operation `dcbor-signing-input` with `signatures/dcbor-signing-input.json`, `dcbor` signing and verification including chain links (`signatures/sign.json`, `signatures/verify.json`), `tokens/signed-values.json`, and `envelope/signed-values.json`; features `dcbor` and `ES256`; `keys/rfc7515-test-keys.json` (the P-256 key from RFC 7515 Appendix A.3, test only).

## 2026-10-09: Markdown lint and link check in CI

Tooling change. No normative rule changed.

### Added

- `.github/workflows/docs-lint.yml`: markdownlint and a link check (lychee) run on every pull request and push to `main`; the link check also runs weekly.
- `.markdownlint-cli2.jsonc` and `lychee.toml`: settings for both tools. Links to reserved example names (RFC 2606) and local addresses are skipped, and rate limits (HTTP 429) do not fail the check.
- [CONTRIBUTING.md](CONTRIBUTING.md): how to run both checks locally.

### Changed

- Languages on a few code blocks and angle brackets around a few bare URLs, so the current files pass markdownlint.
- `test-vectors/README.md`: the paragraph after the status table no longer renders as a broken table row.

## 2026-10-09: Test vectors, phase 1

Tooling change. No normative rule changed.

### Added

- `test-vectors/`: 138 shared conformance test vectors for resource matching, capability token lifetime, attenuation, budgets and constraints, envelope structure and token binding, residency tags, and signatures (RFC 8032 known answers, `jcs` signing input, signing, and verification), plus multi-step sequence vectors for a receiver (replay, expiry, audience, `idem_key`, usage counting), with a JSON Schema for vector files and a README that defines each operation.
- `test-vectors/keys/rfc8032-test-keys.json`: the Ed25519 test keys from RFC 8032 section 7.1, test only.
- `tools/validate/test_vectors.py`: runs the vectors against the validator as part of the existing tests; provisional vectors are reported but do not fail.
- `.gitleaks.toml`: default rules, with `test-vectors/` allowlisted for the published test keys.
- Pointers from README.md, the project web page, and `tools/validate/README.md`.

## 2026-10-09: Owner residency tag length

Schema fix. No normative rule changed.

### Fixed

- `common.schema.json` `residencyTag`: owner-defined tags are limited to 64 characters in total, as SK-RT §11 says; the pattern accepted 65. Validator test covers exactly 64 (valid) and 65 (invalid).

## 2026-10-09: P1 anonymous privacy report example

### Added

- `examples/privacy-report.p1-anonymous.json`: valid example of an anonymous call to a verified P1 search provider over a relay, with 24 hour abuse-handling retention.

## 2026-10-09: Validator and CI review fixes

Tooling change. No normative rule changed.

### Fixed

- `tools/validate`: money amounts are compared as exact decimals, not floats (a child limit of `1.0000000000000001` CHF no longer passes under a parent limit of `1` CHF).
- `tools/validate`: a timestamp that matches the schema pattern but is not a real date is reported as a problem instead of crashing; unreadable or unnamed files on the command line are reported with exit status 2; a schema without `$id` fails with a clear message.

### Added

- Tests for exact money comparison, impossible timestamps, the egress and `resources.network` rule, and schemas without `$id`.
- Review issues #47 (future `iat`), #48 (dot segments in wildcard resources), and #49 (pairing session identifier reuse).

## 2026-10-09: Wording review

Editorial change. No normative rule changed.

### Changed

- [TERMINOLOGY.md](TERMINOLOGY.md): the note on the term "SI" no longer cites a specific government document; it only says that some usage calls advanced AI systems "SI".
- [TRADEMARKS.md](TRADEMARKS.md): the note on "Ready" style marks no longer makes statements about third-party registrations.

## 2026-10-09: Reference implementation linked

Repository and editorial change. No normative rule changed.

### Added

- Links to [selfkin/reference](https://github.com/selfkin/reference), a draft Python reference implementation (not for production), from [README.md](README.md) and the project web page.
- Open questions found while building it: issues #17 to #28, and a comment on #10 about timestamps in the dcbor signing input.

### Fixed

- "An Selfkin capability token" now reads "A Selfkin capability token" in SK-COM §A6 and in the `cap_token` description of `envelope.schema.json`.

## 2026-10-09: Renamed to Selfkin

Naming change, prepared for the move of the repository to <https://github.com/selfkin/standards>. No normative rule changed in substance.

### Changed

- Project name "SI Edge" is now **Selfkin**, with the tagline "Open standards for personal AI on your own devices". Documents: Selfkin Runtimes (SK-RT), Selfkin Edge-to-Edge Communication (SK-COM), Selfkin Provider Profiles (SK-PRV). Identifiers SIE-RT, SIE-COM, and SIE-PRV became SK-RT, SK-COM, and SK-PRV throughout, including earlier entries of this changelog.
- The neutral term is now **personal AI runtime**; "SI" is no longer used as shorthand. TERMINOLOGY notes that some usage calls such systems "SI".
- The "SI Envelope" is now the **Selfkin Envelope**; schema titles use "Selfkin".
- Wire identifiers: reserved intents `si.*` became `sk.*` (for example `sk.pairing.request`, `sk.refused`), the refusal media type became `application/vnd.selfkin.refusal+json`, the Provider Manifest field `si_request_header` became `runtime_request_header`, the reserved other-token format name `si-cap` became `sk-cap`, example URLs use `/selfkin/` paths, and the example headers became `Selfkin-Request` and `Selfkin-Model`. The defined term "SI request" in SK-PRV became "runtime request".
- Schema `$id` values, the CI badge, CITATION.cff, and the Pages site point to `github.com/selfkin/standards` and `selfkin.github.io/standards`.
- Example connector lists in SK-RT §2 and SK-PRV are in alphabetical order, with the neutrality note kept.
- Example `envelope.unknown-si-intent.invalid.json` renamed to `envelope.unknown-reserved-intent.invalid.json`.
- Superseded drafts in `drafts/history/` keep their original names as a historical record.

## 2026-10-09: Launch readiness

Repository change. No normative text changed.

### Added

- CI badge at the top of [README.md](README.md).
- [CITATION.cff](CITATION.cff) (version `v0.1-draft`, CC BY 4.0).
- [docs/](docs/): minimal project web page for GitHub Pages (Jekyll, own layout, no external scripts, fonts, analytics, or cookies; brand strings kept in `docs/_config.yml`).

## 2026-10-09: Provider document renamed to Selfkin Provider Profiles

Editorial and naming change. No normative rule changed; identifiers `SK-PRV` and profiles P0 to P3 are unchanged, and no schema field or enum changed.

### Changed

- The provider draft is now titled **Selfkin Provider Profiles Standard (SK-PRV)**, replacing the working name "Selfkin Ready Provider". Conformance claims are worded "self-assessed against SK-PRV profile P0 to P3" (§11).
- Cross-references in the runtime and communication drafts, README, TERMINOLOGY, and earlier CHANGELOG headings use the new name.
- [TRADEMARKS.md](TRADEMARKS.md): new section explaining that the project avoids "Edge Ready" style marks to avoid confusion with names used by others and any suggestion of certification, and that "Selfkin" is a provisional project name, not a certification mark.

## 2026-10-09: Interim patent policy

Repository and process change. No normative text changed.

### Added

- [PATENT-POLICY.md](PATENT-POLICY.md): interim royalty-free patent policy modelled on the W3C Patent Policy royalty-free commitments and the Open Web Foundation Agreement 1.0. Contributors make an irrevocable, worldwide, royalty-free non-assert covenant (and a royalty-free license on request) for their Essential Claims that read on their own Contributions, with defensive termination only. Includes disclosure guidance, scope after merge, and the founding maintainer's commitment for existing content. Draft, not legal advice, to be reviewed by counsel before v1.0.

### Changed

- [GOVERNANCE.md](GOVERNANCE.md): new Intellectual Property section; the path to neutral maintainership now refers to confirming or replacing the interim policy after counsel review.
- [CONTRIBUTING.md](CONTRIBUTING.md): new Patent Policy section; the DCO sign-off also confirms agreement to the policy.
- [README.md](README.md): License section and repository file list mention the Patent Policy.
- Pull request template: the sign-off checkbox refers to the Patent Policy.

## 2026-10-09: Schema alignment revision

Resolutions of the questions found while writing the v0.1 schemas, folded into the drafts with the stricter choice in each case (owner-approved). Draft version numbers are unchanged. Details and traceability: [schemas/OPEN-QUESTIONS.md](schemas/OPEN-QUESTIONS.md).

### Selfkin Edge-to-Edge Communication v0.1 (SK-COM)

- Pairing messages use reserved `sk.pairing.*` intents and carry no `instructions` (§A3).
- Envelope table rewritten: exactly one `aud`; `attestation_ref` always present and `null` unless the session is at C3; `cap_token` optional only for pairing and refusals; `idem_key` required with `instructions`; `data` and `payload_type` together; nonce and timestamp formats; provenance entry format; new optional `ext` (§A5). Residency tags combine by intersection.
- New §A5.1 Canonical Encoding and Signatures (`sig` excluded from signed bytes, `canon` member, `dcbor` mandatory to implement) and §A5.2 Versions and Extensions (`ext` with `x-` members; other unknown members rejected).
- §A6: Selfkin capability token format, 1 hour maximum lifetime, binding to the envelope, precise narrowing rules, other token formats, owner attribution for cross-owner checks.
- §A7: refusal object with registered reason codes, no free text.
- §B1, §B5: legacy labels on `provenance` entries. §B7: canonical encodings negotiated. Two new open questions (§D).

### Selfkin Runtimes v0.3 (SK-RT)

- Module kinds defined, including new `hardware` and `device-adapter` definitions; single definition of sideloaded modules (§1, §3).
- Manifest contents include kind and a compatibility range syntax (§3); performance classes (§4).
- `x-` owner residency tags, tag intersection, registered data classes (§11).
- Privacy reports moved from R2 to R1 with defined contents (names, never values; no redaction maps); verifiable minimisation stays at R2 (§13).
- SBOMs moved from R2 to R1 (§17); profile table updated (§21).

### Selfkin Provider Profiles v0.1 (SK-PRV)

- Retention window format and purpose (§3); the Selfkin Envelope itself is required at P2, equivalent mappings no longer count (§6); residency refusal codes (§6); model identity carrier (§7); manifest schema link (§8); refusal object (§9); audit validity bound (§10); P0 manifests allowed (§11); new open question on streaming (§13).

### Repository

- New `registries/`: data classes, intents, refusal reasons.
- New `schemas/refusal.schema.json`; all schemas gain the `ext` object; `v` fixed to `0.1`; data classes and intents restricted to the registries; module compatibility range syntax; provider `model_identity`.
- Validator enforces the 1 hour token lifetime; tests check that registries and schemas agree and that no Markdown file uses em-dashes or en-dashes.
- More examples (62 in total) and TERMINOLOGY updates (module kinds, canonical encoding, extensions, capability token, refusal, intent, data class, registry, `x-` residency tags, tier integers).

## 2026-10-09: v0.1 JSON Schemas, examples, and validator

Roadmap step 1 (first part). No normative text changed.

### Added

- `schemas/`: JSON Schema 2020-12 for the Selfkin Envelope (SK-COM A5), capability token (SK-COM A6), module manifest with capability descriptor (SK-RT 3, 4), privacy report (SK-RT 13), and Provider Manifest (SK-PRV 8, 11), plus shared definitions. `schemas/README.md` maps each schema to the draft sections.
- `schemas/OPEN-QUESTIONS.md`: ambiguities and inconsistencies found in the drafts while writing the schemas, with the conservative choice each schema makes.
- `examples/`: valid and deliberately invalid examples for every schema; `examples/README.md` explains why each invalid example fails.
- `tools/validate/`: Python validator (JSON Schema plus semantic checks such as capability attenuation) and tests (Apache-2.0).
- `.github/workflows/validate.yml`: GitHub Actions workflow that runs the validator and tests on every push and pull request.
- README: "Schemas and Tooling" section, including a non-normative note that CBOR encoding follows the same data model as deterministic CBOR (RFC 8949 section 4.2).

## 2026-10-09: Pre-publication revision

Repository prepared for public release.

### Repository

- Added LICENSE (CC BY 4.0, specification text) and LICENSE-CODE (Apache-2.0, schemas and code).
- Added CONTRIBUTING (with DCO sign-off), CODE_OF_CONDUCT (Contributor Covenant 2.1), SECURITY, GOVERNANCE, TRADEMARKS, TERMINOLOGY, THREAT-MODEL, RFC template, issue and pull request templates.
- Added a "Draft, not for implementation. No certification program exists." banner to every specification document (drafts, README, terminology, threat model, schemas, registries and examples).

### All drafts

- Renamed levels and certification levels to **conformance profiles**. Before v1.0, claims are self-assessments only; claim strings replaced by neutral self-assessment wording.
- Added a **profile tag** ([R1], [C2], [P3], ...) to every normative rule so that rule text and profile tables match.
- Replaced the RFC 2119 sentence with the full BCP 14 boilerplate (RFC 2119, RFC 8174).
- Reworded data residency: tags are an owner policy choice, stricter than the default transfer rules of the nFADP and GDPR. Defined `CH`, `EU`, and `CH-EU`; unknown tags fail closed.
- OAuth 2.1 now cited as an IETF Internet-Draft (work in progress), with RFC 9700 as the stable reference.
- Added non-normative "Example connectors" lists to the runtime and provider drafts, with a neutrality note.
- Added References sections and relative links between documents.

### Selfkin Runtimes v0.3 (SK-RT)

- Defined Owner, User, Edge Device, Control Plane, Provider, full gateway mode, and residency tags.
- Added rules: untrusted content and prompt injection (§2), sideloaded label and model weight hashes (§3), Trusted UI channel and accessibility-compatible consistency, voice approval step, WCAG 2.2 AA (§5), encrypted backup (§8), key recovery, owner key, mesh re-keying (§10), protected logs with deletable content (§11), relay fallback, metadata (§13), approval fatigue (§16), rollback restrictions (§17).
- New §19 People, Shared Devices, and Vulnerable Users; new §20 Security and Privacy Considerations.
- Moved remote retention duties to SK-PRV; turned the "zero data" statement into a non-normative note; EU AI Act note now uses the Act's own roles.
- Resolved conflicts: Core signing now R1, Privacy Gateway R1 with reports at R2, module packaging MUST with a small-Core SHOULD, outbound rule scoped to the Control Plane, every section now covered by a profile.

### Selfkin Edge-to-Edge Communication v0.1 (SK-COM)

- Companion reference corrected to runtime v0.3.
- F5 discovery exempt from E2E encryption (no payload allowed); F7 media frames use AEAD after a signed setup instead of per-frame signatures.
- Envelope: added `aud`, `session`, `seq`, `idem_key`, and a "Required" column.
- Legacy endpoints defined as C0; shims are native endpoints that cannot claim R profiles; Method 4 renamed Proxy Method; human-instruction safety rule (§B6); pin reset rules (§B7).
- Downgrade protection and cross-owner approvals now at C1; delegation chains across owners at C2; revocation bound defined.

### Selfkin Provider Profiles v0.1 (SK-PRV)

- "Certification Levels" renamed to Provider Conformance Profiles; certifiers and certificates replaced by independent audit for P2 and P3; P0 renamed "Unverified".
- Scoped no-training and no-tracking rules to runtime requests and anonymous mode; identified-mode linking must be declared.
- Relay acceptance at P1, Oblivious HTTP gateway at P2.
- Body rules aligned with the profile table.

### History

- runtime v0.1 and v0.2 marked Superseded; levels and claim strings withdrawn; v0.2 now uses model-neutral wording.

## 2026-10-09: Initial drafts

- Selfkin Devices v0.1 (first draft, remote attach).
- Selfkin Runtimes v0.2 (runtime-as-interface reframing).
- Selfkin Runtimes v0.3, Selfkin Edge-to-Edge Communication v0.1, Selfkin Provider Profiles v0.1 (then titled with a working name, renamed on 2026-10-09).
