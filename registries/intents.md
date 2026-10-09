# Registry: Intents

> **Status: Draft, not for implementation.** See [README.md](README.md) for registry rules.

The envelope `intent` declares the purpose of a message (SK-COM §A5). It is a dot-separated lowercase name with at least two labels. The first label is either `sk` (reserved control intents, fully listed below), a registered **application domain**, or an `x-` private prefix. The rest of the name is free, for example `scheduling.propose` or `telemetry.report.hourly`. An intent never grants authority; the capability token and local policy do (SK-COM §A6).

## Reserved Control Intents (`sk.*`)

Only these `sk.*` intents exist. Any other `sk.*` intent is invalid.

| Intent | Purpose | Section |
|---|---|---|
| `sk.pairing.request` | Start pairing | SK-COM §A3 |
| `sk.pairing.response` | Answer a pairing request (out-of-band verification data) | SK-COM §A3 |
| `sk.pairing.confirm` | Confirm pairing after owner consent | SK-COM §A3 |
| `sk.pairing.reject` | Decline pairing | SK-COM §A3 |
| `sk.negotiate` | Version, suite, form, and profile negotiation | SK-COM §B7 |
| `sk.refused` | Refusal; `data` is a refusal object | SK-COM §A7 |
| `sk.ack` | Receipt acknowledgement | SK-COM §A9 |
| `sk.revocation` | Key or device revocation notice | SK-COM §A2 |
| `sk.statement` | Owner-signed identity statements, for example after owner-key rotation | SK-COM §A2 |
| `sk.stream.setup` | Stream setup with per-session keys (F7) | SK-COM §A4 |
| `sk.stream.rekey` | Stream rekeying (F7) | SK-COM §A4 |
| `sk.summary` | Signed summary of a negotiation that commits the owner | SK-COM §A7 |
| `sk.sync` | Mesh synchronisation (F1) | SK-COM §A9 |

Pairing messages (`sk.pairing.*`) and refusals (`sk.refused`) are the only envelopes that may omit `cap_token`, and they never carry `instructions` (SK-COM §A3, §A5, §A7).

## Application Domains

| Domain | Purpose | Examples |
|---|---|---|
| `task` | Generic task requests and results | `task.request`, `task.result` |
| `scheduling` | Meetings and appointments | `scheduling.propose`, `scheduling.accept` |
| `messaging` | Sending or relaying messages for a person | `messaging.send` |
| `telemetry` | Sensor and device readings | `telemetry.report` |
| `control` | Commands to devices and actuators | `control.set`, `control.stop` |
| `negotiation` | Agent-to-agent negotiation | `negotiation.offer`, `negotiation.counter` |
| `purchase` | Orders and quotes | `purchase.quote`, `purchase.order` |
| `payment` | Payment requests and confirmations | `payment.request` |
| `share` | Sharing data or files | `share.offer`, `share.deliver` |
| `query` | Questions and lookups, including provider calls | `query.search`, `query.inference` |
| `notify` | Notifications without a requested action | `notify.info` |
| `handoff` | Delegating a task to another runtime (F6) | `handoff.request`, `handoff.result` |
