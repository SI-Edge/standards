# Changelog

All notable changes to the Selfkin drafts. Dates are in Europe/Zurich time. All documents are **Draft, not for implementation**.

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

Naming change, prepared for the move of the repository to https://github.com/selfkin/standards. No normative rule changed in substance.

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
