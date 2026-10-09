# Registry: Refusal Reasons

> **Status: Draft, not for implementation.** See [README.md](README.md) for registry rules.

Reason codes for the refusal object ([schemas/refusal.schema.json](../schemas/refusal.schema.json); SK-COM §A7, SK-PRV §6, §9). A refusal carries a code, never free text, so it cannot leak memory, Adaptation Profile data, or other content (SK-COM §A7). Private codes start with `x-`; a receiver that does not understand a code treats it as `policy-denied`.

| Code | Meaning | Section |
|---|---|---|
| `malformed` | Not a valid envelope or object for the negotiated version | SK-COM §A5 |
| `bad-signature` | Missing or invalid signature | SK-COM §A5 |
| `unsupported-version` | Unknown major version, or a member from a higher minor version | SK-COM §A5, §B7 |
| `sunset-version` | Version or crypto suite is `sunset` | SK-COM §B8 |
| `unsupported-form` | Form not allowed by the pairing record or not supported | SK-COM §A1, §A3 |
| `unsupported-intent` | Intent not understood or not accepted | SK-COM §A5 |
| `unsupported-token-format` | Token format whose attenuation the receiver cannot verify | SK-COM §A6 |
| `unauthorized` | Missing token, or rights do not cover the request | SK-COM §A6 |
| `expired` | Envelope or token expired | SK-COM §A5, §A6 |
| `replayed` | Nonce or `idem_key` already seen | SK-COM §A5, §A9 |
| `wrong-audience` | `aud` does not name the receiver | SK-COM §A5 |
| `out-of-sequence` | `seq` outside the configured window | SK-COM §A5 |
| `revoked` | Key, device, token, or module revoked | SK-COM §A2 |
| `policy-denied` | Local policy forbids the request | SK-COM §A6 |
| `approval-denied` | The human declined | SK-COM §A6 |
| `approval-timeout` | No human decision in time | SK-COM §A6 |
| `rate-limited` | Per-peer or per-credential rate limit reached | SK-COM §A7, SK-PRV §9 |
| `budget-exceeded` | Message, compute, or money budget exhausted | SK-COM §A7 |
| `residency-unsupported` | Destination cannot honour a residency tag | SK-PRV §6, SK-RT §11 |
| `residency-unknown-tag` | Residency tag not recognised | SK-PRV §6, SK-RT §11 |
| `data-class-forbidden` | Egress policy forbids a data class for this destination | SK-RT §11 |
| `profile-too-low` | Peer or provider profile below the pin or the owner's minimum | SK-COM §B7, SK-PRV §12 |
| `legacy-forbidden` | Owner policy forbids legacy methods for this data or action | SK-COM §B7 |
| `proof-required` | Extra proof needed (fresh anonymous credential, proof-of-work, reduced quota) | SK-PRV §9 |
| `unavailable` | Temporarily unable to process; retry later | SK-COM §A9 |
