# Selfkin: Open standards for personal AI on your own devices

[![Validate schemas and examples](https://github.com/selfkin/standards/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/selfkin/standards/actions/workflows/validate.yml)

> **Status: Draft, not for implementation. No certification program exists.**
> These are early drafts for discussion. Conformance profiles are not certifications, and before v1.0 any claim of conformance is a self-assessment only. A trademark check for the name "Selfkin" is pending (see [TRADEMARKS.md](TRADEMARKS.md)).

**Maintainer:** roenu (@roenudev), Bern · Working index · 2026-10-09

## Goal

A **personal AI** is an advanced AI agent runtime that runs on hardware the user owns and becomes their primary interface to devices, apps, services, and other agents. These drafts define open standards so that such runtimes are fast, efficient, secure, modular, adaptable, and open to everyone, whatever model, vendor, or device they use. Data, credentials, and memory stay with the user by default. Remote models and services are used only through verifiable, minimal, user-visible channels.

## Documents

| Document | File | Scope |
|---|---|---|
| **Selfkin Runtimes v0.3** (SK-RT, current) | [drafts/runtime-v0.3.md](drafts/runtime-v0.3.md) | The on-device runtime: Core, modules, hardware, interface and Trusted UI, adaptation, memory, key recovery, Privacy Gateway, approvals, shared devices. Profiles **R1 to R3** |
| **Selfkin Edge-to-Edge Communication v0.1** (SK-COM) | [drafts/edge-to-edge-communication-v0.1.md](drafts/edge-to-edge-communication-v0.1.md) | All communication forms (F1 to F9), identity, pairing, E2E crypto, the signed Selfkin Envelope, delegation, agent-to-agent safety, legacy compatibility Methods 1 to 5. Profiles **C1 to C3** |
| **Selfkin Provider Profiles v0.1** (SK-PRV) | [drafts/provider-v0.1.md](drafts/provider-v0.1.md) | What cloud models, APIs, search, and web services should do: anonymous access, no retention or training, no tracking, attested inference, residency. Profiles **P0 to P3**. Claims are worded "self-assessed against SK-PRV profile P0 to P3" |
| Terminology | [TERMINOLOGY.md](TERMINOLOGY.md) | Shared glossary, residency tags, profile tiers |
| Threat model | [THREAT-MODEL.md](THREAT-MODEL.md) | Adversaries, assets, and the rules that address them |
| Registries | [registries/](registries/README.md) | Data classes, intents, and refusal reasons shared by all drafts |
| History: Edge Devices v0.1 (superseded) | [drafts/history/runtime-v0.1.md](drafts/history/runtime-v0.1.md) | First draft, focused on remote attach |
| History: Edge Runtimes v0.2 (superseded) | [drafts/history/runtime-v0.2.md](drafts/history/runtime-v0.2.md) | Runtime-as-interface reframing |

## How They Fit Together

- The **runtime** standard defines what happens on a device and who decides: the Core, not the model.
- The **communication** standard defines how runtimes, devices, people, and legacy systems exchange messages, using one signed envelope that carries residency tags, capability tokens, and provenance.
- The **provider** standard defines what the outside world should offer before the runtime's Privacy Gateway trusts it beyond full gateway mode.
- Every normative rule carries a profile tag (for example [R2], [C1], [P3]) that says from which profile it applies.

Profiles group into tiers:

| Tier | Runtime | Communication | Provider |
|---|---|---|---|
| 0 Unverified | n/a | C0 (legacy hop) | P0 |
| 1 Basic | R1 | C1 | P1 |
| 2 Sovereign | R2 | C2 | P2 |
| 3 Attested | R3 | C3 | P3 |

A session's **effective tier** is the lowest tier of the runtime, of every communication hop, and of every provider in its path. For example, an R3 runtime that calls a P1 provider runs that call at tier 1, and a hop through a legacy endpoint runs at tier 0. Runtimes show the effective tier to the user.

## Schemas and Tooling

- [schemas/](schemas/): JSON Schema 2020-12 files for the Selfkin Envelope, capability token, module manifest, privacy report, refusal, and Provider Manifest, with a [map to the draft sections](schemas/README.md) and the [open questions](schemas/OPEN-QUESTIONS.md) that remain. The schemas follow the drafts; where they disagree, the draft wins.
- [registries/](registries/README.md): minimal data-class, intent, and refusal-reason vocabularies, kept in sync with the schemas by the tests.
- [examples/](examples/): valid and deliberately invalid examples for every schema, with the reason each invalid one fails.
- [tools/validate/](tools/validate/): a small Python validator (JSON Schema plus semantic checks such as capability attenuation) and its tests. A GitHub Actions workflow in [.github/workflows/validate.yml](.github/workflows/validate.yml) runs them on every push and pull request.
- [selfkin/reference](https://github.com/selfkin/reference): a draft Python reference implementation of identities, the signed Selfkin Envelope, capability tokens with delegation, refusals, privacy reports, and a simplified end-to-end session, with a runnable demo (`python -m selfkin_ref.demo`). Not for production. Where the drafts leave details open, its interpretation choices are tracked as [open questions](https://github.com/selfkin/standards/issues?q=is%3Aissue+label%3Aopen-question).
- CBOR (non-normative): a CBOR encoding follows the same data model, encoded as deterministic CBOR (RFC 8949 section 4.2). A normative CBOR profile is future work.

```
pip install -r tools/validate/requirements.txt
python tools/validate/validate.py
```

## Repository

- [CONTRIBUTING.md](CONTRIBUTING.md): how to propose changes, DCO sign-off, style rules
- [GOVERNANCE.md](GOVERNANCE.md): maintainers, decisions, status labels, path to neutral maintainership
- [rfcs/0000-template.md](rfcs/0000-template.md): template for substantial change proposals
- [CHANGELOG.md](CHANGELOG.md): version history
- [SECURITY.md](SECURITY.md): how to report security or privacy flaws in the specifications
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md): Contributor Covenant 2.1
- [TRADEMARKS.md](TRADEMARKS.md): status of names, third-party marks, no endorsement
- [PATENT-POLICY.md](PATENT-POLICY.md): interim royalty-free patent policy for contributions
- [CITATION.cff](CITATION.cff): how to cite this repository
- [docs/](docs/): source of the project web page at https://selfkin.github.io/standards/ (no trackers, no cookies, no third-party assets)

## License

- Specification text (everything under `drafts/` and the Markdown documentation) is licensed under the **Creative Commons Attribution 4.0 International License** (CC BY 4.0). See [LICENSE](LICENSE).
- Schemas, test suites, and reference code added to this repository are licensed under the **Apache License, Version 2.0**. See [LICENSE-CODE](LICENSE-CODE).
- Contributions are accepted under the same licenses with a DCO sign-off (see [CONTRIBUTING.md](CONTRIBUTING.md)).
- **Patents:** contributors make a royalty-free non-assert commitment for their essential patent claims, with defensive termination only. See the interim [Patent Policy](PATENT-POLICY.md) (draft, not legal advice, to be reviewed by counsel before v1.0).
- The licenses do not grant rights to use the project names as marks; see [TRADEMARKS.md](TRADEMARKS.md).

## Next Steps / Roadmap

1. **Envelope schema:** publish the Selfkin Envelope, module manifest, capability descriptor, open memory format, and Provider Manifest as JSON Schema plus a deterministic CBOR profile. *Started in v0.1 of [schemas/](schemas/): envelope, capability token, module manifest (with capability descriptor), privacy report, refusal, and Provider Manifest, aligned with the drafts. Still open: open memory format, normative CBOR profile.*
2. **Reference implementation:** a minimal Core prototype with a local router model, MCP tool layer, Privacy Gateway, Trusted UI components, and one proxy module for a legacy device. Start on a PC and a VPS, then add a phone.
3. **Test suite:** conformance tests for R1, C1, and P1 first, including downgrade, prompt-injection, and Trusted UI spoofing tests.
4. **Governance:** the RFC process in [GOVERNANCE.md](GOVERNANCE.md), an open module registry template, and neutral maintainership before v1.0.
5. **Review:** invite security, privacy, and accessibility review, including neurodivergent users, and legal review against the nFADP, the GDPR, and the EU AI Act.
