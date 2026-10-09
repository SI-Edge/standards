# Selfkin Edge-to-Edge Communication Standard (Draft v0.1)

> **Status: Draft, not for implementation. No certification program exists.**
> Conformance profiles in this document are for discussion only. Before v1.0 any claim of conformance is a self-assessment and must not be presented as a certification. See [TRADEMARKS.md](../TRADEMARKS.md).

**Document:** Selfkin Edge-to-Edge Communication (SK-COM) · Draft v0.1 · roenu (@roenudev), Bern · 2026-10-09 · Companion to [Selfkin Runtimes v0.3](runtime-v0.3.md) (SK-RT) and [Selfkin Provider Profiles v0.1](provider-v0.1.md) (SK-PRV) · Shared terms: [TERMINOLOGY.md](../TERMINOLOGY.md) · Threats: [THREAT-MODEL.md](../THREAT-MODEL.md)

**Purpose.** This document defines secure, model-agnostic rules for every way personal AI runtimes communicate with each other, with devices, and with people (Part A). It also defines how runtimes interoperate with legacy endpoints that cannot speak the new protocol (Part B). It uses the terms of SK-RT §1 (Runtime Core, Router Model, Capability, Control Plane, Egress, Consequential Action, Owner, User, residency tag) and its profiles R1 to R3. It does not describe any vendor's plans or products.

## Conventions

- The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.
- **Profile tags.** Each normative rule starts with a tag such as **[C1]**, **[C2]**, or **[C3]**: the lowest communication profile (Part C) at which the rule applies. A rule tagged [C2] applies at C2 and C3. Below its tag, a rule is RECOMMENDED unless it says otherwise. Statements without a tag are non-normative.
- Each rule ends with a one-line *rationale*.

---

# Part A: Secure Edge-to-Edge Communication

## A1. Communication Forms

**[C1]** Every message **MUST** be classified as one of the following forms, and the form **MUST** be recorded in its envelope (or, for F5, in the advertisement). *Rationale: each form calls for different trust, approval, and egress rules.*

| Form | Description | Default trust |
|---|---|---|
| **F1 Mesh** | Runtime to runtime, same owner | High, still authenticated |
| **F2 Peer** | Runtime to runtime, different owners (agent-to-agent negotiation) | Untrusted |
| **F3 Device** | Runtime to sensor, robot, car, or IoT device | Scoped to capability |
| **F4 Human-device** | Runtime to the owner's phone, wearable, or display UI | High, needs presence checks for sensitive actions |
| **F5 Discovery** | Broadcast and advertisement | Untrusted |
| **F6 Handoff** | Delegating a task to another runtime | Attenuated from the delegator |
| **F7 Stream** | Voice, video, telemetry | Bound to a session |
| **F8 Store-and-forward** | Offline or delayed delivery through intermediaries | Intermediary untrusted |
| **F9 Relay** | Through a control plane or rendezvous relay | Relay untrusted for content |

## A2. Identity

- **[C1]** Each device **MUST** hold a signing key that never leaves the device, and the key **SHOULD** be hardware-backed (TPM 2.0, a secure enclave, or a TEE). *Rationale: keys held only in software can be copied.*
- **[C3]** Device and agent keys **MUST** be hardware-backed. *Rationale: attested profiles need keys that cannot be copied.*
- **[C1]** Agent identity **MUST** be separate from device identity. Each agent gets its own key, issued by the Runtime Core and bound to the device. *Rationale: several agents share one device and need separate accountability and revocation.*
- **[C1]** Owner identity **MUST** be bound to devices and agents through owner-signed statements. *Rationale: a peer has to know whose agent it is dealing with.*
- Identities **MAY** be expressed as Decentralized Identifiers (DIDs). Claims such as "owner verified" or "R3 attested" **MAY** be expressed as Verifiable Credentials with selective disclosure (for example SD-JWT VC or BBS signatures). *Rationale: open identity formats with no central registry.*
- **[C1]** Keys **MUST** be rotatable. A revocation **MUST** be applied by each mesh device no later than its next successful sync, and online mesh devices **SHOULD** apply it within 5 minutes of the owner's action. *Rationale: a lost device must not keep its access.*
- **[C2]** Peers **MUST** check revocation status before accepting a cross-owner session (F2, F6). *Rationale: revoked keys must not keep working with strangers.*
- **[C1]** After an owner-key rotation (SK-RT §10), the runtime **MUST** send re-issued statements to paired peers. *Rationale: peers must learn about the new key from the owner, not by guessing.*
- **[C1]** A peer **MUST NOT** need to learn the owner's real-world identity unless the task requires it. *Rationale: pseudonymous by default.*

## A3. Discovery and Pairing

- Local discovery **MAY** use mDNS, BLE, NFC, or QR codes. Remote discovery **MAY** use a rendezvous or relay service. *Rationale: use proven mechanisms.*
- **[C1]** Discovery advertisements (F5) **MUST** reveal as little as possible (no owner name, agent list, or capabilities in clear text) and **MUST NOT** carry payload data. *Rationale: broadcasts reach everyone nearby and cannot be end-to-end encrypted.*
- **[C1]** Pairing **MUST** require explicit owner consent on at least one side, and on both sides for F1 and F2. *Rationale: no silent trust relationships.*
- **[C1]** Pairing messages **MUST** use an `intent` from the reserved `sk.pairing.*` namespace ([registries/intents.md](../registries/intents.md)) and **MUST NOT** carry `instructions`. Together with refusals (§A7), they are the only envelopes that **MAY** omit `cap_token`. *Rationale: before pairing there is no capability to present, so pairing must not be able to request actions.*
- **[C1]** Pairing **MUST** include out-of-band verification: a short authentication string, a QR scan, or NFC proximity. *Rationale: defeats man-in-the-middle attacks at the moment trust is set up.*
- **[C1]** A pairing record **MUST** state the forms and capabilities it allows, and it **SHOULD** expire unless renewed. *Rationale: trust should be specific and time-bound.*

## A4. Transport and Cryptography

- **[C1]** All forms except F5 advertisements **MUST** use end-to-end encryption between the communicating runtimes. Relays, proxies, and store-and-forward nodes **MUST NOT** be able to read the payload. *Rationale: infrastructure is not a trusted party.*
- **[C1]** Every session (any exchange after pairing) **MUST** use mutual authentication. Before pairing, the exchange is authenticated by the out-of-band step in A3. *Rationale: both sides must prove who they are.*
- **[C1]** Key exchange **MUST** provide forward secrecy. *Rationale: protects past traffic if a key is later stolen.*
- **[C3]** Key exchange **MUST** use a hybrid classical plus post-quantum construction. Below C3 it is RECOMMENDED where implementations are available. *Rationale: protects against attacks that record traffic now and decrypt it later.*
- Implementations **SHOULD** build on established building blocks: TLS 1.3 or QUIC for client/server and relay paths, the Noise Protocol Framework for peer-to-peer and constrained links, and MLS for group messaging within a mesh or multi-party sessions. *Rationale: do not invent your own cryptography.*
- **[C1]** Streams (F7) **MUST** be set up with a signed Selfkin Envelope that establishes per-session keys. Media frames **MUST** then be protected with authenticated encryption under those keys (for example SRTP or QUIC). Per-frame signatures are not required. Streams **SHOULD** support rekeying during long sessions. *Rationale: strong protection without signing every frame.*
- **[C1]** Cipher suite negotiation **MUST** be protected against downgrade (B7). *Rationale: attackers target negotiation.*

## A5. Message Envelope

**[C1]** Every message **MUST** use a common, signed **Selfkin Envelope** with a versioned schema and a canonical encoding (§A5.1). The only exceptions are F5 advertisements (A3) and F7 media frames after stream setup (A4); the form F5 therefore never appears in an envelope. *Rationale: one structure to verify, log, and enforce.*

The machine-readable definition is [schemas/envelope.schema.json](../schemas/envelope.schema.json). Where the schema and this text disagree, this text wins.

Fields:

| Field | Required | Purpose |
|---|---|---|
| `v` | Always | Schema version as `MAJOR.MINOR` (§A5.2) |
| `form` | Always | F1 to F9, except F5 |
| `sender_agent` / `sender_device` | Always | Agent and device identity |
| `aud` | Always | Exactly one intended recipient: an agent, device, or provider identity, or the identifier of an MLS group the sender belongs to |
| `session` | Always | Session or conversation identifier |
| `seq` | Always | Sequence number within the session |
| `attestation_ref` | Always; `null` unless the session was negotiated at C3 | Reference to the device's attestation or profile claim. **MUST NOT** be `null` in a session negotiated at C3 (§B7) |
| `cap_token` | Always, except pairing messages (§A3) and refusals (§A7) | Capability token authorising this message (§A6) |
| `intent` | Always | Declared purpose, from the intent registry ([registries/intents.md](../registries/intents.md)) |
| `instructions` | When an action is requested | Requested action, structured (`action`, optional `resource`, `params`, `consequential`). Authenticated by `sig`; there is no separate signature (§A5.1) |
| `data` | When there is content | Payload content, always treated as untrusted data |
| `payload_type` | When `data` is present, and only then | Media type or schema URI of `data` |
| `residency` | Always | Residency tags (SK-RT §11) and data classes ([registries/data-classes.md](../registries/data-classes.md)) of the content |
| `idem_key` | Whenever `instructions` is present; **MAY** be used on other messages | Idempotency key so retries do not repeat an action |
| `nonce` / `issued` / `expires` | Always | Replay protection and freshness. `nonce` has at least 128 bits of randomness. Timestamps are RFC 3339 with an explicit offset (CBOR tag 1 in CBOR) |
| `provenance` | Always; empty if there is no prior hop | Prior hops, oldest first (F6, F8, B5). Each entry has `role` (`origin`, `delegator`, `proxy`, `relay`, `store-and-forward`, or `legacy-endpoint`), `id`, and optional `device`, `method`, `labels`, and `at` |
| `model_ref` | When a model produced content | Which agent and model produced the content |
| `ext` | Optional | Extensions (§A5.2) |
| `sig` | Always | Signature block by the agent key (§A5.1) |

- **[C1]** Receivers **MUST** reject envelopes that are unsigned, expired, replayed, not addressed to them (`aud`), out of sequence beyond a configured window, or of an unknown major version. *Rationale: fail closed.*
- **[C1]** `instructions` and `data` **MUST** be separate fields, and the receiving Core **MUST NOT** grant any authority based on text inside `data`. *Rationale: a structural mitigation for prompt injection. It is not a complete defence, because a model reading `data` can still be steered; SK-RT §2 requires policy checks on every resulting action.*
- **[C1]** Every envelope that carries `instructions` **MUST** carry an `idem_key`. *Rationale: any requested action may change state, so retries must be safe by default.*
- **[C1]** `data` and `payload_type` **MUST** appear together or not at all. *Rationale: untrusted content must always be typed before it is parsed.*
- **[C1]** In a session negotiated at C3, receivers **MUST** reject envelopes whose `attestation_ref` is `null`. *Rationale: the negotiated profile is bound to the session by the signed transcript (§B7), so the receiver knows when attestation is required.*
- **[C1]** Residency tags in one envelope combine by intersection: the content may go only where every tag allows. An empty tag list means the owner set no residency restriction for this content; all other egress rules still apply. *Rationale: several tags must never widen where data may go.*

### A5.1 Canonical Encoding and Signatures

- **[C1]** A signature **MUST** be computed over the canonical encoding of the signed object with its `sig` member removed. The `sig` block contains `alg` (JOSE or COSE algorithm name), `kid` (signing key), `canon`, `value`, and, for manifests, `signer`. `canon` names the encoding: `dcbor` (deterministic CBOR, RFC 8949 §4.2) or `jcs` (JSON Canonicalization Scheme, RFC 8785). *Rationale: both sides must hash exactly the same bytes.*
- **[C1]** Every runtime **MUST** be able to produce and verify `dcbor` signatures. Senders **MUST** use `dcbor` unless the receiver announced `jcs` support during negotiation (§B7). *Rationale: one mandatory-to-implement encoding guarantees interoperability.*
- **[C1]** `instructions` have no separate signature; they are authenticated only as part of the signed envelope. *Rationale: one signature, one verification path.*
- The same rules apply to every signed Selfkin object: capability tokens (§A6), module manifests (SK-RT §3), and Provider Manifests (SK-PRV §8).

### A5.2 Versions and Extensions

- **[C1]** `v` is `MAJOR.MINOR`. Senders **MUST NOT** use members defined in a minor version higher than the one negotiated (§B7). *Rationale: a receiver must understand every standard member it is given.*
- **[C1]** Receivers **MUST** reject envelopes that contain members which are neither defined for the negotiated version nor inside `ext`. *Rationale: fail closed.*
- **[C1]** Extensions **MUST** be placed in the `ext` object, with member names that start with `x-`. Receivers **MUST** ignore `ext` members they do not understand. `ext` content **MUST NOT** grant authority, relax policy, or change the meaning of standard members. *Rationale: room to experiment without weakening the core.*
- These rules apply to every Selfkin schema object (capability tokens, module manifests, privacy reports, refusals, Provider Manifests). *Rationale: one extension rule for the whole ecosystem.*

## A6. Authorization

- **[C1]** Authorization **MUST** be capability-based. A token grants specific actions on specific resources, for a specific audience and time window. *Rationale: least privilege, with no ambient authority.*
- **[C1]** An Selfkin capability token has the members `v`, `id`, `iss` (issuer), `sub` (holder), `aud` (exactly one audience), `iat`, optional `nbf`, `exp`, `cnf` (proof-of-possession key binding), `rights` (each an `action` on a `resource`, with optional `constraints`), optional `budget`, `chain`, optional `ext`, and `sig` ([schemas/capability-token.schema.json](../schemas/capability-token.schema.json)). *Rationale: one token format that every runtime can verify.*
- **[C1]** A token's `exp` **MUST** be no more than 1 hour after its `iat`. Owner policy **MAY** set a shorter maximum. Longer tasks **MUST** obtain fresh tokens. *Rationale: a testable bound for "short-lived".*
- **[C1]** When a token authorises an envelope, its `sub` **MUST** equal the envelope's `sender_agent`, its `aud` **MUST** equal the envelope's `aud`, and its rights **MUST** cover the action in `instructions`. *Rationale: a token is useful only to its holder, toward its audience, for its actions.*
- **[C1]** Other attenuable token formats **MAY** be used, wrapped as `{format, token}` in `cap_token`. The receiver **MUST** verify attenuation natively for that format, and **MUST** refuse with `unsupported-token-format` if it cannot. *Rationale: alternative formats must not bypass attenuation.*
- **[C1]** Tokens **MUST** be short-lived and sender-bound (proof of possession, for example DPoP, RFC 9449, or mTLS-bound tokens, RFC 8705). They **SHOULD** follow the OAuth 2.0 Security BCP (RFC 9700) or OAuth 2.1 (an IETF Internet-Draft, work in progress), or use an attenuable token format. *Rationale: a stolen token alone is useless.*
- **[C1]** Below C2, F6 delegation **MUST NOT** cross owners. *Rationale: cross-owner delegation needs verifiable chains.*
- **[C2]** Delegation (F6) **MUST** only attenuate. Each hop can narrow scope, lifetime, or budget but never widen them, and the full chain **MUST** be verifiable end to end. *Rationale: delegating a task must never escalate privilege.*
- **[C2]** A delegated token narrows its parent only if all of the following hold, and receivers **MUST** reject it otherwise: (a) its `iss` equals the parent's `sub`; (b) its `aud` equals the parent's `aud`; (c) its `exp` is not later than the parent's; (d) every right has the same `action` as a parent right and a `resource` that is equal to the parent's or lies below a parent resource ending in `/*`; (e) every constraint and budget limit the parent sets is present and not higher, and constrained data classes are a subset; (f) the full chain is carried in `chain`, root first, with at most 16 links. *Rationale: precise rules make attenuation testable.*
- **[C1]** The owners of `iss` and `sub` are determined from owner-signed statements (§A2); a chain whose links cannot be attributed to owners **MUST** be treated as crossing owners. *Rationale: the cross-owner rule above needs a way to tell owners apart.*
- **[C1]** Consequential actions requested by another owner (F2, or F6 across owners) **MUST** get human approval on the receiving side, unless the owner has pre-authorised a narrow policy for them. *Rationale: a stranger's agent must not act on your behalf by default.*
- **[C1]** Every request **MUST** also pass the receiving runtime's local permission checks. Tokens never override local policy. *Rationale: the receiver's owner decides.*

## A7. Agent-to-Agent Safety

- **[C1]** All peer content **MUST** be treated as untrusted data. It **MUST NOT** change the receiving agent's system instructions, permissions, or memory without passing local policy. *Rationale: other agents may be compromised or adversarial.*
- **[C1]** Runtimes **MUST** enforce per-peer rate limits and budgets (messages, compute, money). *Rationale: limits denial-of-service and runaway loops between agents.*
- Runtimes **MAY** maintain local reputation scores for peers, and **SHOULD NOT** depend on one central reputation authority. *Rationale: useful signal without a single point of control.*
- **[C1]** Refusals **MUST** use the refusal object ([schemas/refusal.schema.json](../schemas/refusal.schema.json)) with a reason code from [registries/refusal-reasons.md](../registries/refusal-reasons.md) or a private `x-` code. It is sent as the `data` of an envelope with intent `sk.refused` and `payload_type` `application/vnd.selfkin.refusal+json`; such an envelope **MUST NOT** carry `instructions`. A refusal **MUST NOT** include free text, memory, Adaptation Profile data, or other content that was not already in the request. *Rationale: predictable negotiation without accidental disclosure.*
- **[C1]** Negotiations that commit the owner (purchases, agreements, sharing data) **MUST** produce a signed summary for the human. *Rationale: owners need a clear record of what their agent agreed to.*

## A8. Privacy

- **[C2]** Metadata **MUST** be minimised. Relays **SHOULD** see only routing identifiers, and implementations **SHOULD** support padding and batching where practical. *Rationale: metadata reveals relationships.*
- **[C2]** The egress policy (SK-RT §11) **MUST** be enforced on every hop, including F1 mesh traffic. *Rationale: an owner's own devices can sit in different jurisdictions.*
- **[C2]** Residency tags **MUST** be honoured with the meanings defined in SK-RT §11. A runtime **MUST NOT** forward tagged data to a destination outside the tag's region, and **MUST** treat unknown tags as not allowed. *Rationale: residency travels with the data.* Residency tags are an owner policy choice that is stricter than the default transfer rules of the Swiss nFADP and the EU GDPR; they are not a statement of what those laws require.
- Runtimes **SHOULD** use selective disclosure (proving a claim without revealing the underlying data) where formats support it. *Rationale: share the minimum.*

## A9. Reliability

- **[C1]** Store-and-forward queues (F8) **MUST** keep envelopes encrypted and **MUST** respect `expires`. *Rationale: delayed delivery must not mean data at rest is exposed.*
- **[C1]** Messages that change state **MUST** carry an `idem_key`, and receivers **MUST** execute each `idem_key` at most once. *Rationale: retries must not duplicate a payment or an action.*
- **[C1]** Ordering **MUST** be tracked per session with `seq`. *Rationale: agents reason over sequences.*
- **[C2]** Mesh sync **SHOULD** use conflict-free merge strategies (for example CRDTs) for memory and policy, and **MUST** surface conflicts it cannot resolve to the owner. *Rationale: offline devices diverge.*

## A10. Audit and Transparency

- **[C1]** Every runtime **MUST** keep a local log of envelopes sent and received, with their form, peer, intent, and decision. Logs **MUST NOT** contain secrets. *Rationale: accountability across agents depends on evidence.*
- **[C2]** The log **MUST** be tamper-evident (hash-chained), **MUST** include `model_ref`, and **MUST** follow the log protections in SK-RT §11 (encryption at rest, retention period, deletable content). *Rationale: evidence that cannot be quietly edited, without becoming a surveillance store.*
- **[C1]** Users **MUST** be able to see which agent and model produced every message, sent or received. *Rationale: provenance is part of the interface.*
- Logs **SHOULD** be exportable as OpenTelemetry traces. *Rationale: use standard tooling.*

## A11. Existing Protocols as Carriers

- MCP **SHOULD** be used as the carrier for tool and capability calls, with the Selfkin Envelope carried inside or alongside it. *Rationale: reuse the open tool protocol.*
- Other agent-to-agent protocols **MAY** carry Selfkin Envelopes, provided the security properties in A4 to A10 are preserved end to end. *Rationale: stay compatible without depending on any single protocol.*
- **[C1]** A carrier **MUST NOT** be treated as providing security that the envelope itself does not provide. *Rationale: the envelope is the trust anchor.*

---

# Part B: Backward Compatibility with Legacy Endpoints

A **legacy endpoint** is any device, app, or OS that does not itself sign and verify Selfkin Envelopes. An endpoint running a shim (Method 3) that implements the envelope is a native endpoint with a shim profile, not a legacy endpoint.

Legacy endpoints are below C1. The hop to a legacy endpoint has the effective profile **C0 (legacy)**. This does not lower the runtime's own profile for other sessions.

## B1. General Rules

- **[C1]** Every legacy endpoint **MUST** be labelled `legacy` and `unattested` in the envelope (on its `provenance` entry, role `legacy-endpoint`, §A5), the logs, and the interface. Any endpoint without verified attestation **MUST** be labelled `unattested`. *Rationale: users have to see where trust is weaker.*
- **[C1]** An adapter **MUST** generate a permission manifest for each legacy endpoint before first use, and the owner **MUST** approve it. *Rationale: same consent model as native capabilities.*
- **[C1]** Egress policy and approvals **MUST** be enforced by the personal AI runtime on the adapter side, since a legacy endpoint cannot enforce them. *Rationale: enforcement lives where trust lives.*
- When several methods are possible, runtimes **SHOULD** prefer, in order: native, Method 3, Method 2, Method 4, Method 1, Method 5. *Rationale: prefer structured, enforceable paths over brittle ones.*

## B2. Method 1: App Method

**When to use:** the device runs a modern OS, but the target app has no Selfkin support.
- The runtime **MAY** drive apps through app intents, shortcuts, deep links, accessibility APIs, or, as a last resort, UI automation. *Rationale: it reaches existing apps today.*
- **[C1]** UI automation **MUST** be limited to the approved app and **MUST** run every action through the Core's permission checks. *Rationale: screen control is powerful and brittle.*
- **[C1]** Content read from the app's screen **MUST** be treated as untrusted data. *Rationale: on-screen text can carry injected instructions.*
- **[C2]** The app's network egress **SHOULD** be monitored where the OS allows. *Rationale: apps can egress on their own.*
- **Profile:** usable at any runtime profile; the app endpoint is C0.

## B3. Method 2: OS Method

**When to use:** the OS allows a privileged bridge or system service (for example a system extension or automation framework).
- **[C1]** The bridge **MUST** be a module of the local runtime: sandboxed, signed, and limited to declared system actions. *Rationale: OS privileges carry a large blast radius.*
- **[C1]** The bridge **MUST** expose actions as typed capabilities (MCP-compatible) with manifests. *Rationale: structured actions can be enforced.*
- **[C1]** The bridge **MUST NOT** hold model credentials or user secrets beyond what each action needs. *Rationale: limits the damage if it is compromised.*
- **Profile:** the OS functions behind the bridge are C0, unless the bridge and the functions it calls are covered by the device's attestation, in which case actions through it **MAY** count toward R3. *Rationale: attestation must cover what acts.*

## B4. Method 3: Runtime Method (Shim)

**When to use:** the endpoint can install software but cannot run a full runtime (older PCs, low-end phones, small servers).
- **[C1]** A lightweight **shim** **MUST** implement the Selfkin Envelope, mutual authentication, and local permission checks for the capabilities it exposes. *Rationale: lets old hardware become a real endpoint.*
- **[C1]** The shim **MUST** be signed, updatable, and possible to roll back (never to a revoked or `sunset` version), and it **MUST NOT** run models unless it meets the full runtime standard. *Rationale: a minimal, auditable surface.*
- **[C1]** A shim without a hardware root of trust **MUST** label itself `unattested`. *Rationale: honest profile claims.*
- **Profile:** a shim **MUST NOT** claim any R profile, because it is not a runtime. Without hardware-backed keys it can reach at most C2; with hardware-backed keys and verified attestation it **MAY** reach C3. *Rationale: capability depends on the hardware.*

## B5. Method 4: Proxy Method

**When to use:** the endpoint cannot run anything new, such as old IoT, HTTP APIs, Bluetooth peripherals, Matter, Modbus, and other legacy protocols.
- A nearby personal AI runtime acts as a **proxy**. It translates legacy protocols into capabilities and wraps every exchange in the Selfkin Envelope on the Selfkin side. *Rationale: brings legacy endpoints under one policy.*
- **[C1]** The proxy **MUST** be treated as holding the trust for its legacy endpoints. Its identity **MUST** appear in every envelope's `provenance` with role `proxy`, and the legacy endpoint **MUST** appear there with role `legacy-endpoint` and the labels `legacy` and `unattested`. *Rationale: trust must be explicit about who actually vouches.*
- **[C1]** The proxy **MUST** isolate each legacy endpoint (separate credentials, and a separate network segment where possible) and **MUST** keep legacy credentials in its own keystore. *Rationale: one weak device must not compromise others.*
- **[C1]** Consequential and physical actions through a proxy **MUST** require approval unless pre-authorised. *Rationale: legacy devices have weak safety interlocks.*
- **Profile:** the proxy runtime can hold any R and C profile, but the legacy endpoint stays C0. *Rationale: a proxy cannot attest for what it does not control.*

## B6. Method 5: Human-in-the-Loop Fallback

**When to use:** no automated path exists or the risk is too high.
- **[C1]** The runtime **MUST** be able to give the human clear, step-by-step instructions and record the outcome they confirm. *Rationale: the human is always the final compatibility layer.*
- **[C1]** The runtime **MUST NOT** pretend that a step done by a human was automated, or the reverse. *Rationale: honest audit trail.*
- **[C1]** Instructions to a human that originate from another owner's agent (F2, F6) **MUST** be shown in Trusted UI with their origin, and **MUST NOT** ask the human to reveal secrets, codes, or credentials, or to approve payments, outside the normal approval flow (SK-RT §16). *Rationale: a malicious peer must not use the human as an attack path.*

## B7. Negotiation, Version Fallback, and Downgrade Protection

- **[C1]** Peers **MUST** negotiate envelope version, crypto suites, canonical encodings (§A5.1), forms, and profile at session start, and **MUST** select the highest profile both support and owner policy allows. *Rationale: always use the best available security.*
- **[C1]** The negotiation transcript **MUST** be signed and bound to the session keys. *Rationale: prevents an attacker from forcing legacy mode.*
- **[C1]** A runtime **MUST** remember a peer's highest previously seen profile and **MUST** refuse, or require owner approval, before dropping below it. The owner **MAY** reset a pin, and a peer that announces a planned profile change in a signed statement **MAY** be re-pinned after owner approval. *Rationale: trust on first use with downgrade pinning, and a way out for legitimate changes.*
- **[C1]** Falling back to a legacy method **MUST** be shown to the user explicitly (for example "Legacy connection: unattested"). *Rationale: no silent loss of security.*
- Owner policy **MAY** forbid legacy methods for given data classes or actions. *Rationale: some data should never touch weak paths.*

## B8. Deprecation and Sunset Policy

- **[C1]** Every envelope version and crypto suite **MUST** have a published status: `current`, `deprecated`, or `sunset`. *Rationale: predictable migration.*
- **[C1]** Deprecated versions **SHOULD** stay supported for a published transition period and **MUST** trigger warnings for the user. *Rationale: time to migrate without surprise breakage.*
- **[C1]** Sunset versions **MUST** be refused, except through an explicit owner override that is logged as a security exception. *Rationale: weak crypto must eventually be retired.*
- **[C1]** A suite with a known practical break **MUST** move to `sunset` immediately. *Rationale: security outranks compatibility.*

---

# C. Communication Conformance Profiles

| Profile | Aligned with | Requires |
|---|---|---|
| **C0** | n/a | Legacy hop (Part B). Not a conformance profile; shown to the user as `legacy` |
| **C1 Basic** | R1 | Every rule tagged [C1]. In summary: forms (A1), device, agent, and owner identity (A2), minimal discovery and consented pairing (A3), E2E encryption with mutual auth and forward secrecy, stream protection, downgrade protection (A4, B7), signed Selfkin Envelope with `aud`, `seq`, `idem_key` (A5), capability tokens, cross-owner approvals, local checks (A6), untrusted-data handling (A7), reliability (A9), local logs (A10), legacy labelling and human-fallback safety (Part B) |
| **C2 Sovereign** | R2 | C1 + every rule tagged [C2]: revocation checks (A2), attenuated cross-owner delegation chains (A6), metadata minimisation, egress and residency on every hop (A8), CRDT mesh sync (A9), tamper-evident protected logs with `model_ref` (A10) |
| **C3 Attested** | R3 | C2 + every rule tagged [C3]: hardware-backed device and agent keys, attestation references verified by peers (A2), hybrid post-quantum key exchange (A4) |

- A session's effective communication profile is the **lowest** profile of any party, shim, or proxy hop in the path. *Rationale: a chain is only as strong as its weakest link.*
- Before v1.0, any claim of conformance is a **self-assessment** only and **MUST NOT** be presented as a certification. A self-assessment **SHOULD** be phrased as "Self-assessed against Selfkin Edge-to-Edge Communication draft v0.1, profile C2". *Rationale: no certification program exists.*

# D. Open Questions

1. [registries/](../registries/) now holds minimal intent, data-class, and refusal-reason registries. Who should maintain them after v1.0, and how should application domains grow?
2. Which post-quantum hybrid constructions (for example X25519MLKEM768) should become mandatory for C3, and when?
3. How can reputation work across owners without creating a central authority or a way to track people?
4. How should proxies prove correct translation for legacy protocols that have no integrity protection?
5. How should liability and approval work when an agent-to-agent negotiation spans owners in different jurisdictions (for example CH and a non-EU country)?
6. What is the format of an F5 discovery advertisement (fields, size limits, rotation of identifiers)?
7. How are F7 streams to several recipients set up when `aud` names one MLS group, and which streaming paths provide relay separation comparable to Oblivious HTTP?

# E. References

BCP 14 (RFC 2119, RFC 8174); RFC 3339 (timestamps); TLS 1.3 (RFC 8446); QUIC (RFC 9000); Noise Protocol Framework; MLS (RFC 9420); deterministic CBOR (RFC 8949 §4.2); JSON Canonicalization Scheme (RFC 8785); DPoP (RFC 9449); OAuth 2.0 mTLS-bound tokens (RFC 8705); OAuth 2.0 Security BCP (RFC 9700); OAuth 2.1 (draft-ietf-oauth-v2-1, work in progress); W3C Decentralized Identifiers (DID) v1.0; W3C Verifiable Credentials Data Model 2.0; SD-JWT VC (IETF, work in progress); Model Context Protocol specification; OpenTelemetry; Swiss nFADP; EU GDPR.

---
*Schema alignment revision (2026-10-09): pairing intents and refusals (§A3, §A7), envelope field formats, `attestation_ref` always present, `idem_key` with `instructions`, intersection of residency tags (§A5), canonical encoding and signatures (§A5.1), versions and the `ext` extension rule (§A5.2), token format, 1 hour maximum lifetime, envelope binding, and precise narrowing rules (§A6), provenance labels for legacy endpoints (§B1, §B5). Full history in [CHANGELOG.md](../CHANGELOG.md).*
