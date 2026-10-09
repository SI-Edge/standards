# Registry: Refusal Reasons

> **Status: Draft, not for implementation.** See [README.md](README.md) for registry rules.

Reason codes for the refusal object ([schemas/refusal.schema.json](../schemas/refusal.schema.json); SIE-COM §A7, SIE-PRV §6, §9). A refusal carries a code, never free text, so it cannot leak memory, Adaptation Profile data, or other content (SIE-COM §A7). Private codes start with `x-`; a receiver that does not understand a code treats it as `policy-denied`.

| Code | Meaning | Section |
|---|---|---|
| `malformed` | Not a valid envelope or object for the negotiated version | SIE-COM §A5 |
| `bad-signature` | Missing or invalid signature | SIE-COM §A5 |
| `unsupported-version` | Unknown major version, or a member from a higher minor version | SIE-COM §A5, §B7 |
| `sunset-version` | Version or crypto suite is `sunset` | SIE-COM §B8 |
| `unsupported-form` | Form not allowed by the pairing record or not supported | SIE-COM §A1, §A3 |
| `unsupported-intent` | Intent not understood or not accepted | SIE-COM §A5 |
| `unsupported-token-format` | Token format whose attenuation the receiver cannot verify | SIE-COM §A6 |
| `unauthorized` | Missing token, or rights do not cover the request | SIE-COM §A6 |
| `expired` | Envelope or token expired | SIE-COM §A5, §A6 |
| `replayed` | Nonce or `idem_key` already seen | SIE-COM §A5, §A9 |
| `wrong-audience` | `aud` does not name the receiver | SIE-COM §A5 |
| `out-of-sequence` | `seq` outside the configured window | SIE-COM §A5 |
| `revoked` | Key, device, token, or module revoked | SIE-COM §A2 |
| `policy-denied` | Local policy forbids the request | SIE-COM §A6 |
| `approval-denied` | The human declined | SIE-COM §A6 |
| `approval-timeout` | No human decision in time | SIE-COM §A6 |
| `rate-limited` | Per-peer or per-credential rate limit reached | SIE-COM §A7, SIE-PRV §9 |
| `budget-exceeded` | Message, compute, or money budget exhausted | SIE-COM §A7 |
| `residency-unsupported` | Destination cannot honour a residency tag | SIE-PRV §6, SIE-RT §11 |
| `residency-unknown-tag` | Residency tag not recognised | SIE-PRV §6, SIE-RT §11 |
| `data-class-forbidden` | Egress policy forbids a data class for this destination | SIE-RT §11 |
| `profile-too-low` | Peer or provider profile below the pin or the owner's minimum | SIE-COM §B7, SIE-PRV §12 |
| `legacy-forbidden` | Owner policy forbids legacy methods for this data or action | SIE-COM §B7 |
| `proof-required` | Extra proof needed (fresh anonymous credential, proof-of-work, reduced quota) | SIE-PRV §9 |
| `unavailable` | Temporarily unable to process; retry later | SIE-COM §A9 |
