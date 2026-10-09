# Selfkin Registries

> **Status: Draft, not for implementation. No certification program exists.**

Minimal shared vocabularies referenced by the drafts. Each registry lists codes in its first column; the [schemas](../schemas) enforce the same lists, and the tests in [tools/validate](../tools/validate) check that registries and schemas agree.

| Registry | Used by |
|---|---|
| [data-classes.md](data-classes.md) | `residency.data_classes` and egress policy (SK-RT §11, §13), module manifests (SK-RT §3), privacy reports (SK-RT §13), capability token constraints (SK-COM §A6) |
| [intents.md](intents.md) | Envelope `intent` (SK-COM §A5), pairing (SK-COM §A3), refusals (SK-COM §A7) |
| [refusal-reasons.md](refusal-reasons.md) | Refusal object (SK-COM §A7, SK-PRV §6, §9) |

## Rules

- Codes are lowercase ASCII. Registered codes never change meaning; a code that is withdrawn is marked `deprecated` and is never reused.
- **Private codes** start with `x-` (for example `x-garden.watering` or `x-acme-sensor`). They need no registration, are never registered, and receivers that do not understand them treat them as unknown (fail closed where the draft says so).
- New codes are added by pull request following [GOVERNANCE.md](../GOVERNANCE.md). A change that alters the meaning of an existing code is a substantial change and needs an RFC.
- Before v1.0 all registries are drafts and may change.
