# Examples

> **Status: Draft, not for implementation.** Examples for the v0.1 JSON Schemas in [../schemas](../schemas). Licensed under Apache-2.0 ([LICENSE-CODE](../LICENSE-CODE)).

File names follow `<schema>.<case>.json` for valid examples and `<schema>.<case>.invalid.json` for examples that must fail. The validator in [../tools/validate](../tools/validate) picks the schema from the file name and checks both layers: JSON Schema and the semantic checks that JSON Schema cannot express.

Notes that apply to every example:

- **Signatures are placeholders.** Every `sig.value` is a dummy string. The validator checks structure, not cryptography.
- **Identities are fictional.** They use `did:example`, `urn:example`, and `example.org`/`example.com`/`example.net` names. No real person, provider, or product is described.
- **Times are fixed.** Timestamps are around 2026-10-09 and are not checked against the current clock, so examples do not expire.
- The `data` member of `envelope.f2-action-request.json` deliberately contains a prompt-injection sentence. It is valid: `data` is untrusted content and grants no authority (SK-COM section A5), so the schema has no reason to reject it. The receiving Core must ignore such text as an instruction.

## Valid examples

| File | Shows |
|---|---|
| `capability-token.root.json` | Root token from an owner to a planner agent, sender-bound with `cnf.jkt`, with rights, constraints, and budget |
| `capability-token.delegated.json` | F6 delegation one hop down: narrower resource, fewer rights, shorter lifetime, smaller budget, full chain carried |
| `envelope.f2-action-request.json` | Cross-owner (F2) action request with separate `instructions` and `data`, `aud`, `session`, `seq`, `idem_key`, `CH-EU` residency, delegated `cap_token`, and `model_ref` |
| `envelope.f1-pairing-request.json` | Pairing message (`sk.pairing.*` intent): no `cap_token`, no `instructions` |
| `envelope.f2-refusal.json` | Refusal (`sk.refused`) with a refusal object as `data`, no `cap_token`, no `instructions` |
| `envelope.with-extension.json` | The action request with an `ext` member using an `x-` key (SK-COM section A5.2) |
| `envelope.f3-legacy-via-proxy.json` | Telemetry from a legacy Modbus device through a proxy (Method 4): proxy in `provenance`, legacy endpoint labelled `legacy` and `unattested`, opaque attenuable token |
| `module-manifest.feature-calendar.json` | Feature module with permissions, consequential flag, egress with residency, SBOM, and SLSA provenance |
| `module-manifest.model-local.json` | Local model module with weight hashes and no egress |
| `module-manifest.legacy-proxy.json` | Self-signed (sideloaded) legacy adapter carrying `legacy` and `unattested` |
| `module-manifest.hardware-actuator.json` | Hardware module with a capability descriptor and declared safe-stop behaviour |
| `refusal.rate-limited.json` | Refusal object with a registered reason, a reference to the refused message, and `retry_after` |
| `refusal.profile-too-low.json` | Refusal stating the communication profile that would be accepted |
| `privacy-report.p0-full-gateway.json` | Call to an unverified (P0) provider in full gateway mode through an OHTTP relay, retention undeclared |
| `privacy-report.p2-verified.json` | Call to a verified P2 provider with a Privacy Pass credential and `CH-EU` residency |
| `provider-manifest.p1-search.json` | P1 self-assessment of a search service with a declared 24 hour abuse-handling retention window and identified-mode linking |
| `provider-manifest.p2-models.json` | P2 self-assessment of a model provider with OHTTP, envelope support, residency, transparency log, and audit |
| `privacy-report.p1-anonymous.json` | Anonymous call to a verified P1 search provider over a relay, with `EU` residency and declared 24 hour abuse-handling retention |

## Invalid examples

Each invalid example changes one thing in a valid example. Examples were generated from fictional data; registered codes come from [../registries](../registries). The comment explains which rule it breaks.

| File | Comment: why it must fail |
|---|---|
| `capability-token.lifetime-over-one-hour.invalid.json` | Root token valid for 3 hours. The maximum lifetime is 1 hour (SK-COM section A6). Semantic check |
| `capability-token.longer-lifetime.invalid.json` | Delegated token expires after its parent. Delegation may only shorten lifetime (SK-COM section A6). Semantic check |
| `capability-token.not-sender-bound.invalid.json` | No `cnf` member, so the token is a bearer token. Tokens must be sender-bound (SK-COM section A6) |
| `capability-token.widened-budget.invalid.json` | Delegated token raises the message budget above its parent's. Budgets may only narrow (SK-COM section A6). Semantic check |
| `capability-token.widened-rights.invalid.json` | Delegated token adds a `payments.send` right the parent never had. Rights may only narrow (SK-COM section A6). Semantic check |
| `envelope.bad-residency-tag.invalid.json` | Residency tag `switzerland` is neither `CH`, `EU`, `CH-EU`, nor an `x-` owner tag (SK-RT section 11) |
| `envelope.data-without-payload-type.invalid.json` | `data` is present without `payload_type` (SK-COM section A5) |
| `envelope.expires-before-issued.invalid.json` | `expires` is earlier than `issued`, so the envelope is never fresh. Semantic check |
| `envelope.ext-without-x-prefix.invalid.json` | Extension member `project` without the `x-` prefix (SK-COM section A5.2) |
| `envelope.higher-minor-version.invalid.json` | `v` is `0.2`, a version these v0.1 schemas do not define. Members and versions beyond the negotiated version are rejected (SK-COM section A5.2) |
| `envelope.refusal-with-free-text.invalid.json` | Refusal object with a free-text `detail`. Refusals carry codes only (SK-COM section A7) |
| `envelope.refusal-with-instructions.invalid.json` | Refusal that also requests an action. Refusals never carry `instructions` (SK-COM section A5, A7) |
| `envelope.unknown-reserved-intent.invalid.json` | Intent `sk.admin` is not one of the reserved `sk.*` intents (registries/intents.md) |
| `envelope.unregistered-data-class.invalid.json` | Data class `healthcare` is neither registered nor `x-` prefixed (registries/data-classes.md) |
| `envelope.unregistered-intent.invalid.json` | Intent domain `gossip` is neither registered nor `x-` prefixed (registries/intents.md) |
| `envelope.f5-advertisement.invalid.json` | Form F5 in an envelope. Discovery advertisements are not envelopes (SK-COM section A3, A5) |
| `envelope.instructions-without-idem-key.invalid.json` | Requests an action without `idem_key`. State-changing messages need one (SK-COM section A9) |
| `envelope.legacy-not-unattested.invalid.json` | Legacy endpoint in `provenance` is labelled `legacy` but not `unattested` (SK-COM section B1, B5) |
| `envelope.missing-aud.invalid.json` | No `aud`. Every envelope names its recipient (SK-COM section A5) |
| `envelope.missing-cap-token.invalid.json` | Non-pairing message without `cap_token` (SK-COM section A5) |
| `envelope.token-not-bound-to-sender.invalid.json` | The capability token's holder (`sub`) is not the sending agent. Semantic check |
| `envelope.unknown-member.invalid.json` | Unknown top-level member `grant`. Unknown members are rejected (fail closed) |
| `module-manifest.actuator-without-safe-stop.invalid.json` | Actuator hardware without declared safe-stop behaviour (SK-RT section 4) |
| `module-manifest.bad-runtime-range.invalid.json` | Compatibility range `0.3 or newer` is not in the comparator syntax (`>=0.3 <0.4`, SK-RT section 3) |
| `module-manifest.legacy-not-unattested.invalid.json` | Legacy adapter without the `unattested` label (SK-RT section 3, SK-COM section B1) |
| `module-manifest.model-without-weights-hash.invalid.json` | Model module without weight hashes (SK-RT section 3) |
| `module-manifest.no-sbom.invalid.json` | No SBOM reference (SK-RT section 3) |
| `module-manifest.signer-missing.invalid.json` | Signature without `signer`, so the Core cannot show who signed (SK-RT section 3) |
| `module-manifest.undeclared-egress-data.invalid.json` | Egress sends the data class `health`, which the manifest does not declare. Semantic check |
| `privacy-report.direct-but-says-relay.invalid.json` | No relay was used but the report claims the network identity was hidden by a relay |
| `privacy-report.p0-without-full-gateway.invalid.json` | P0 provider called anonymously without full gateway mode (SK-RT section 13) |
| `privacy-report.redaction-map-included.invalid.json` | Contains a redaction map. Redaction maps must not leave the device and are never part of a report (SK-RT section 13) |
| `privacy-report.retention-missing.invalid.json` | No retention declaration; the report must show it, even if `undeclared` (SK-RT section 11, section 13) |
| `privacy-report.unverified-claim-used.invalid.json` | Effective profile P2 although the claim was not verified. Unverified providers are P0 (SK-RT section 13, SK-PRV section 12) |
| `provider-manifest.audit-older-than-two-years.invalid.json` | Audit valid for three years. Audits are renewed at least every two years (SK-PRV section 10). Semantic check |
| `provider-manifest.claims-certification.invalid.json` | Claim basis `certification`. Before v1.0 only self-assessments exist (SK-PRV section 11) |
| `provider-manifest.identified-linking-undeclared.invalid.json` | Identified mode offered without declaring how requests are linked (SK-PRV section 2, section 4) |
| `provider-manifest.model-identity-without-envelope.invalid.json` | Model identity declared to travel in the envelope although the provider does not accept envelopes (SK-PRV section 7) |
| `provider-manifest.p1-trains-on-requests.invalid.json` | Claims P1 but trains on runtime requests (SK-PRV section 3) |
| `provider-manifest.p2-without-ohttp.invalid.json` | Claims P2 without an Oblivious HTTP gateway (SK-PRV section 4) |
| `provider-manifest.p2-without-envelope.invalid.json` | Claims P2 without accepting the Selfkin Envelope. Equivalent mappings are not accepted (SK-PRV section 6) |
| `provider-manifest.p3-without-attestation.invalid.json` | Claims P3 without attestation endpoints, reference values, or retention evidence (SK-PRV section 3, section 5) |
| `provider-manifest.retention-without-purpose.invalid.json` | Non-zero retention window without a stated purpose (abuse handling or legal duty, SK-PRV section 3) |
| `refusal.free-text.invalid.json` | Free-text `detail` member. A refusal must not include content beyond codes and references (SK-COM section A7) |
| `refusal.unregistered-reason.invalid.json` | Reason `too-busy` is neither registered nor `x-` prefixed (registries/refusal-reasons.md) |
