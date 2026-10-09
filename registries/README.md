# SI Edge Registries

> **Status: Draft, not for implementation. No certification program exists.**

Minimal shared vocabularies referenced by the drafts. Each registry lists codes in its first column; the [schemas](../schemas) enforce the same lists, and the tests in [tools/validate](../tools/validate) check that registries and schemas agree.

| Registry | Used by |
|---|---|
| [data-classes.md](data-classes.md) | `residency.data_classes` and egress policy (SIE-RT §11, §13), module manifests (SIE-RT §3), privacy reports (SIE-RT §13), capability token constraints (SIE-COM §A6) |
| [intents.md](intents.md) | Envelope `intent` (SIE-COM §A5), pairing (SIE-COM §A3), refusals (SIE-COM §A7) |
| [refusal-reasons.md](refusal-reasons.md) | Refusal object (SIE-COM §A7, SIE-PRV §6, §9) |

## Rules

- Codes are lowercase ASCII. Registered codes never change meaning; a code that is withdrawn is marked `deprecated` and is never reused.
- **Private codes** start with `x-` (for example `x-garden.watering` or `x-acme-sensor`). They need no registration, are never registered, and receivers that do not understand them treat them as unknown (fail closed where the draft says so).
- New codes are added by pull request following [GOVERNANCE.md](../GOVERNANCE.md). A change that alters the meaning of an existing code is a substantial change and needs an RFC.
- Before v1.0 all registries are drafts and may change.
