# SI Edge Ready Provider Standard (Draft v0.1)

> **Status: Draft, not for implementation. No certification program exists.**
> "SI Edge Ready" is a provisional working name pending a trademark check (see [TRADEMARKS.md](../TRADEMARKS.md)). Conformance profiles in this document are for discussion only. Before v1.0 any claim of conformance is a self-assessment and must not be presented as a certification.

**Document:** SI Edge Ready Provider (SIE-PRV) · Draft v0.1 · roenu (@roenudev), Bern · 2026-10-09 · Companion to [SI Edge Runtimes v0.3](runtime-v0.3.md) (SIE-RT) and [SI Edge-to-Edge Communication v0.1](edge-to-edge-communication-v0.1.md) (SIE-COM) · Shared terms: [TERMINOLOGY.md](../TERMINOLOGY.md)

**Purpose.** This document defines what cloud model providers, APIs, search engines, and web services should do to be safe to call from a personal SI runtime without exposing the user beyond what the task needs. It is model-agnostic and vendor-neutral, and makes no claims about any provider's current practices or plans. Runtimes use these profiles to decide how much to trust a provider and when to use full gateway mode (SIE-RT §13).

## Conventions

- The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.
- **Profile tags.** Each normative rule starts with a tag such as **[P1]**, **[P2]**, or **[P3]**: the lowest provider profile (§11) at which the rule applies. A rule tagged [P2] applies at P2 and P3. Below its tag, a rule is RECOMMENDED unless it says otherwise. Rules tagged [Runtime] apply to runtimes, not providers. Statements without a tag are non-normative.
- Each rule ends with a one-line *rationale*.

**Example connectors (non-normative).** The order of this list is not a ranking, and alphabetical order is not implied. Grok (xAI); then other providers such as hosted model APIs, search APIs, and web services, and self-hosted open-weight models exposed through the same provider interface. No vendor is endorsed or required, and listing a provider here says nothing about its conformance to any profile. Examples are illustrative only.

---

## 1. Terms

- **Provider:** any remote service a runtime calls (inference, API, search, content, payment).
- **Provider Manifest:** a signed, machine-readable description of the provider's capabilities, pricing, policies, and claimed profile (§8).
- **Anonymous Credential:** a token that proves the right to access (for example "paid" or "not abusive") without identifying or linking the user.
- **Anonymous mode:** requests sent without account credentials, through the Privacy Gateway, optionally with an anonymous credential. **Identified mode:** requests sent with the user's own account or API key.
- **SI request:** a request in anonymous mode, or one marked as coming from an SI runtime by an SI Envelope or by a request header declared in the Provider Manifest.
- **Provider profile:** a provider conformance profile, P0 to P3 (§11).

## 2. Anonymous and Pseudonymous Access

- **[P1]** Providers **MUST** offer an anonymous mode that does not require an account tied to a real-world identity. *Rationale: the user's identity is not part of the task.*
- **[P2]** Providers **MUST** accept at least one privacy-preserving token scheme (for example Privacy Pass or blind-signature anonymous credentials) for authorisation and quota. *Rationale: proves entitlement without linking requests.*
- **[P2]** Billing **MUST** be unlinkable from usage: prepaid token batches, anonymous credits, or payment schemes that separate who paid from what was requested. *Rationale: payment records should not become usage logs.*
- **[P1]** Where a provider also offers identified mode, it **MUST** say so in its manifest, and runtimes will label it accordingly (SIE-RT §13). *Rationale: informed choice.*

## 3. No Training, No Retention

- **[P1]** Providers **MUST NOT** train on, fine-tune on, or build profiles from SI requests or their responses. *Rationale: requests come from people's personal devices.*
- **[P1]** Providers **MUST NOT** retain SI request or response content after the response is delivered, except for a short retention window strictly for abuse handling or legal duty. *Rationale: data that is not kept cannot leak.*
- **[P1]** Any retention window **MUST** be declared in the manifest as an ISO 8601 duration (`PT0S` for none). A non-zero window **MUST** state its purpose: abuse handling, legal duty, or both. *Rationale: runtimes show it in the privacy report, and owners can block providers that retain anything (SIE-RT §11).*
- **[P3]** The declared retention window **MUST** be covered by attestation or audit evidence. *Rationale: retention claims need proof.*
- **[P1]** Operational logs for SI requests **MUST** exclude content and **MUST NOT** contain persistent user identifiers. *Rationale: metadata can identify people too.*

## 4. No Tracking or Fingerprinting

- **[P1]** For SI requests, providers **MUST NOT** set tracking cookies, use device fingerprinting, or link requests across sessions through IP addresses, TLS fingerprints, or similar signals. Linking inherent to identified mode is exempt, but **MUST** be declared (§2). *Rationale: tracking defeats pseudonymous access.*
- **[P1]** Providers **MUST** accept requests through IP-hiding relays (for example MASQUE proxies or other privacy relays) and **MUST NOT** penalise relayed traffic beyond the abuse controls in §9. *Rationale: relays are how runtimes hide network identity.*
- **[P2]** Providers **MUST** operate an Oblivious HTTP gateway (RFC 9458) with a published key configuration for non-streaming requests. *Rationale: OHTTP separates who asks from what is asked, but requires the provider to run its gateway side.*
- **[P1]** Responses **MUST NOT** embed tracking pixels, unique links, or other identifiers meant to follow the user. *Rationale: tracking can enter through the response as well.*

## 5. Confidential and Attested Inference

- **[P1]** Providers **SHOULD** run inference inside confidential computing environments (TEEs or confidential VMs) where available. *Rationale: protects content even from the operator.*
- **[P3]** Endpoints **MUST** offer remote attestation that binds the TLS or session key to a measured environment and a published code or model identity. *Rationale: the runtime can check what it is talking to before sending data.*
- **[P3]** Attestation evidence **MUST** be verifiable by the runtime without contacting the provider's own servers, aside from published reference values. *Rationale: verification should not depend on trusting the party being verified.*

## 6. Envelope and Residency Support

- **[P2]** Providers **MUST** accept the SI Envelope itself ([SIE-COM §A5](edge-to-edge-communication-v0.1.md#a5-message-envelope)), including its canonical encoding and signature rules (SIE-COM §A5.1). Equivalent mappings do not satisfy this rule. *Rationale: one protocol across the ecosystem, and a mapping cannot be verified the same way.*
- **[P2]** Providers **MUST** honour residency tags with the meanings defined in [SIE-RT §11](runtime-v0.3.md#11-data-sovereignty-egress-and-residency): data tagged `CH`, `EU`, or `CH-EU` is processed and stored only in the corresponding regions. *Rationale: residency travels with the data.* Residency tags are an owner policy choice that is stricter than the default transfer rules of the Swiss nFADP and the EU GDPR; they are not a statement of what those laws require.
- **[P2]** If a provider cannot honour a tag, or does not recognise it, it **MUST** refuse with the refusal object (§9) and the reason `residency-unsupported` or `residency-unknown-tag`, not process the request elsewhere. Several tags combine by intersection (SIE-RT §11). *Rationale: fail closed.*
- **[P2]** Providers **MUST** respect the envelope's `expires`, `aud`, and `idem_key` fields. *Rationale: reliability and replay protection.*

## 7. Transparency and Model Identity

- **[P1]** Every response **MUST** carry a model identity (model name, version, and region) and the provider's currently claimed profile. Providers that accept the SI Envelope carry it in the response envelope's `model_ref`; others carry it in a response header named in the manifest (`model_identity`). Below P3 this is a declaration that the runtime cannot verify. *Rationale: runtimes record which model saw what (SIE-RT §14).*
- **[P2]** Providers **MUST** publish periodic transparency reports covering legal requests, retention practice, incidents, and changes to policy. *Rationale: accountability over time.*
- **[P1]** Material changes to model or policy **MUST** be announced in the manifest before they take effect. *Rationale: runtimes can re-evaluate trust.*

*Note (non-normative): providers may need to document how their services map to EU AI Act obligations, using the Act's own roles (such as provider and deployer). This standard does not provide compliance with the Act.*

## 8. Capability and Pricing Discovery

- **[P1]** Providers **MUST** publish a signed **Provider Manifest** ([schemas/provider-manifest.schema.json](../schemas/provider-manifest.schema.json)) at a well-known location. Signatures follow SIE-COM §A5.1 and extensions SIE-COM §A5.2. It covers capabilities (models, modalities, context limits, tools), pricing, accepted credentials, retention, regions, residency support, attestation endpoints, identified-mode linking, how model identity is carried (§7), and the claimed profile with a link to the self-assessment. *Rationale: runtimes can compare and choose automatically.*
- **[P1]** The manifest **MUST** be versioned. **[P2]** It **MUST** be logged in a public transparency log. *Rationale: makes silent edits detectable.*
- **[P1]** Fetching the manifest **MUST NOT** require authentication or identify the runtime. *Rationale: discovery itself must not track anyone.*

## 9. Abuse Handling without Identification

- **[P2]** Rate limits **MUST** be enforced per anonymous credential or per token batch, not per person or device. *Rationale: abuse control without surveillance.*
- **[P1]** Providers **MAY** require extra proof (for example a fresh anonymous credential, proof-of-work, or reduced quota) when they detect abuse, and **MUST NOT** require deanonymisation for normal use. *Rationale: proportionate responses.*
- **[P1]** Refusals **MUST** use the standard refusal object ([SIE-COM §A7](edge-to-edge-communication-v0.1.md#a7-agent-to-agent-safety), [schemas/refusal.schema.json](../schemas/refusal.schema.json)) with a code from [registries/refusal-reasons.md](../registries/refusal-reasons.md), in an `si.refused` envelope or, without envelope support, as an HTTP response body with media type `application/vnd.si-edge.refusal+json`, and **MUST NOT** include identifying information. *Rationale: predictable behaviour without leaking anything.*

## 10. Independent Audit

- Before v1.0 there is no certification program, no accreditation of auditors, and no certificates issued under this standard.
- **[P2]** A P2 or P3 self-assessment **MUST** be supported by an independent third-party audit report, renewed at least every two years (its stated validity ends no later than two years after issue), with a public summary linked from the manifest. *Rationale: self-declarations are not enough for higher trust.*
- **[P2]** The auditor **MUST** be independent of the provider and **SHOULD** publish its method. *Rationale: credible evidence.*
- **[P2]** Audit statements **SHOULD** be issued as Verifiable Credentials referenced from the manifest, with published revocation status. *Rationale: runtimes can check them automatically.*

## 11. Provider Conformance Profiles

| Profile | Name | Requires |
|---|---|---|
| **P0** | Unverified | No claims, or claims the runtime has not verified. A provider **MAY** publish a manifest that claims P0. The runtime uses full gateway mode or the user's explicit identified-mode choice (SIE-RT §13) |
| **P1** | Private | Every rule tagged [P1]: anonymous mode (§2), no training and declared short retention (§3), no tracking and relay acceptance (§4), model identity per response (§7), signed versioned manifest (§8), proportionate abuse handling (§9). Self-assessed |
| **P2** | Sovereign | P1 + every rule tagged [P2]: anonymous credentials and unlinkable billing (§2), Oblivious HTTP gateway (§4), SI Envelope and residency enforcement (§6), transparency reports (§7), logged manifest (§8), per-credential rate limits (§9), independent audit (§10) |
| **P3** | Attested | P2 + every rule tagged [P3]: attested or audited retention (§3), attested confidential inference bound to the session (§5) |

- Before v1.0, any claim of conformance is a **self-assessment** only and **MUST NOT** be presented as a certification or seal. A self-assessment **SHOULD** be phrased as "Self-assessed against SI Edge Ready Provider draft v0.1, profile P2". *Rationale: no certification program exists.*

## 12. Runtime Verification and Downgrade

- **[Runtime]** Runtimes that verify provider profiles (REQUIRED at R3, SIE-RT §13) **MUST** fetch and verify the Provider Manifest signature before first use and whenever it changes. *Rationale: trust starts from verified claims.*
- **[Runtime]** For P2, runtimes **MUST** verify the audit statement and its revocation status. For P3, they **MUST** also verify attestation before sending any envelope. *Rationale: each profile is only as strong as its check.*
- **[Runtime]** If any check fails, has expired, or cannot be completed, the runtime **MUST** treat the provider as P0, use full gateway mode, and show the downgrade in the privacy report. *Rationale: fail toward privacy, visibly.*
- **[Runtime]** Owner policy **MAY** set a minimum profile per data class (for example "health data: P3 or local only"). *Rationale: sensitivity-based routing.*
- **[Runtime]** Runtimes **MUST** pin a provider's highest verified profile and treat a drop as a policy event that needs owner attention. The owner **MAY** reset the pin, and a drop announced in the manifest in advance **MAY** be accepted after owner approval. *Rationale: protects against downgrade attacks while allowing legitimate change.*

## 13. Open Questions

1. Which anonymous credential schemes are mature enough to require at P2?
2. How can unlinkable billing satisfy tax and anti-fraud obligations in CH and the EU?
3. What retention window, if any, is justifiable for abuse handling, and how should it be attested? (The format is now fixed; a maximum is not.)
4. How should attestation work for models served across many machines or accelerators?
5. Who could accredit auditors in future, and how can that ecosystem avoid capture by large providers?
6. Oblivious HTTP (§4) covers non-streaming requests only. Which private path should P2 require for streaming responses?

## 14. References

BCP 14 (RFC 2119, RFC 8174); Privacy Pass (RFC 9576, RFC 9577, RFC 9578); Oblivious HTTP (RFC 9458); MASQUE (IETF working group); W3C Verifiable Credentials Data Model 2.0; Swiss nFADP; EU GDPR; EU AI Act (Regulation (EU) 2024/1689).

---
*Schema alignment revision (2026-10-09): retention window format and purpose (§3), full SI Envelope required at P2 with no equivalent mappings, residency refusal codes (§6), model identity carrier (§7), manifest schema link (§8), refusal object (§9), audit validity bound (§10), P0 manifests allowed (§11). Full history in [CHANGELOG.md](../CHANGELOG.md).*
