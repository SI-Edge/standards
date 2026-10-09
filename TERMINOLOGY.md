# Terminology

> **Status: Draft, not for implementation. No certification program exists.**

Shared terms for all Selfkin drafts. Where a draft defines a term normatively, the section is given. Document IDs: **SK-RT** (runtime), **SK-COM** (communication), **SK-PRV** (Selfkin Provider Profiles).

| Term | Meaning | Defined in |
|---|---|---|
| **SI** | Not used as a term in these drafts. Some official and public usage calls advanced AI systems "SI" (super intelligence); these drafts say personal AI runtime instead and make no claim that any system is superintelligent | Informative |
| **Personal AI** | A personal AI runtime that acts for one person on hardware they control and serves as their primary interface | README, SK-RT intro |
| **Edge Device** | Hardware the owner controls that runs a personal AI runtime or a shim | SK-RT §1 |
| **Personal AI runtime** | On-device software that hosts agents, mediates every action, and presents the interface | SK-RT §1 |
| **Runtime Core (Core)** | The trusted part of the runtime that enforces policy, permissions, egress, logging, and Trusted UI | SK-RT §1 |
| **Owner** | The person or organisation that controls a runtime, its policy, and its keys | SK-RT §1, §19 |
| **User** | A person who interacts with the runtime; may differ from the owner | SK-RT §1, §19 |
| **Router Model** | Small local decision model that picks models and tools | SK-RT §1 |
| **Control Plane** | Remote service that plans, orchestrates, or runs inference for the runtime | SK-RT §1, §12 |
| **Module** | Installable unit with a signed manifest. Kinds: `feature`, `function`, `model`, `device-adapter`, `hardware`, `ui-kit`, `legacy-adapter` | SK-RT §1, §3 |
| **Hardware module** | Module of kind `hardware`: installed or attached hardware, described by a capability descriptor | SK-RT §1, §4 |
| **Device adapter** | Module of kind `device-adapter`: software that connects to an external device or device API through its own protocol | SK-RT §1 |
| **Sideloaded module** | Module installed from outside the owner's chosen registries, including any self-signed module | SK-RT §1, §3 |
| **Capability** | An action exposed by the OS, an app, a module, or hardware | SK-RT §1, §6 |
| **Capability descriptor** | Description of a hardware item: type, functions, performance class (`constrained`, `standard`, `high`), safety constraints, attestation | SK-RT §4 |
| **Trusted UI** | Fixed interface components rendered only by the Core through a channel others cannot imitate | SK-RT §5 |
| **Adaptation Profile** | User-controlled description of how the runtime communicates and works with them | SK-RT §7 |
| **Privacy Gateway** | Core component that all outbound cloud calls pass through | SK-RT §13 |
| **Full gateway mode** | Strictest Gateway setting used for unverified (P0) providers | SK-RT §13 |
| **Privacy report** | Per-call, user-visible summary of what was sent and what the provider could see | SK-RT §13 |
| **Egress** | Any data that leaves the device | SK-RT §1 |
| **Consequential Action** | Irreversible, costs money, communicates externally, changes access rights, or moves something physically | SK-RT §1 |
| **Selfkin Envelope** | Common signed message structure with versioned schema and canonical encoding | SK-COM §A5 |
| **Canonical encoding** | Byte-exact encoding a signature is computed over: `dcbor` (deterministic CBOR, mandatory to implement) or `jcs` (JSON Canonicalization Scheme), named in `sig.canon` | SK-COM §A5.1 |
| **Extension (`ext`)** | Object for non-standard members with `x-` names; ignored if not understood, never grants authority. Unknown members outside `ext` are rejected | SK-COM §A5.2 |
| **Capability token** | Signed, sender-bound grant of rights for one audience, valid at most 1 hour, that can only narrow on delegation | SK-COM §A6 |
| **Refusal** | Code-only machine-readable answer to a refused request, sent with intent `sk.refused` | SK-COM §A7 |
| **Intent** | Declared purpose of an envelope from the intent registry | SK-COM §A5, [registries/intents.md](registries/intents.md) |
| **Data class** | Label for a kind of personal data, from the data-class registry or `x-` prefixed | SK-RT §11, [registries/data-classes.md](registries/data-classes.md) |
| **Registry** | Shared list of codes (data classes, intents, refusal reasons); private codes start with `x-` | [registries/](registries/README.md) |
| **Form (F1 to F9)** | Classification of a message by communication pattern | SK-COM §A1 |
| **Legacy endpoint** | Device, app, or OS that does not itself sign and verify Selfkin Envelopes | SK-COM Part B |
| **Shim** | Lightweight software that lets an endpoint speak the envelope without a full runtime | SK-COM §B4 |
| **Proxy** | Personal AI runtime that translates legacy protocols for legacy endpoints (Method 4) | SK-COM §B5 |
| **Provider** | Any remote service a runtime calls | SK-PRV §1 |
| **Provider Manifest** | Signed, machine-readable description of a provider's capabilities, policies, and claimed profile | SK-PRV §8 |
| **Anonymous mode / Identified mode** | Requests without account credentials / with the user's own account | SK-PRV §1 |
| **Conformance profile** | Set of rules a self-assessment can claim (R1 to R3, C1 to C3, P0 to P3). Not a certification | All drafts |
| **Profile tag** | Marker such as [R2] at the start of a rule giving the lowest profile it applies to | All drafts, Conventions |
| **Self-assessment** | The only form of conformance claim before v1.0. Provider claims are worded "self-assessed against SK-PRV profile P0 to P3" | All drafts |

## Residency Tags

Defined normatively in SK-RT §11. Residency tags are an **owner policy choice**. They are stricter than the default rules of the Swiss nFADP and the EU GDPR, which allow transfers abroad under conditions such as adequacy decisions or appropriate safeguards.

| Tag | Allowed processing and storage locations |
|---|---|
| `CH` | Switzerland only |
| `EU` | EU and EEA member states only |
| `CH-EU` | Switzerland, or EU and EEA member states |
| `x-...` | Owner-defined, for example `x-home-only`. Any tag a runtime or provider does not recognise is treated as not allowed |

Several tags on the same data combine by **intersection**: the data may be processed and stored only where every tag allows. An empty tag list means the owner set no residency restriction; all other egress rules still apply.

## Profile Tiers

| Tier | Runtime | Communication | Provider |
|---|---|---|---|
| 0 Unverified | n/a | C0 (legacy hop) | P0 |
| 1 Basic | R1 | C1 | P1 |
| 2 Sovereign | R2 | C2 | P2 |
| 3 Attested | R3 | C3 | P3 |

A session's effective tier is the lowest tier of the runtime, every communication hop, and every provider in its path. Machine-readable documents give the tier as the integer 0 to 3 (for example `effective_tier` in a privacy report).

## Labels Shown in Trusted UI

`legacy` (legacy endpoint), `unattested` (no verified attestation), `sideloaded` (module installed from outside the owner's chosen registries, including self-signed modules). In envelopes, `legacy` and `unattested` appear on the legacy endpoint's `provenance` entry (SK-COM §A5).
