# Registry: Intents

> **Status: Draft, not for implementation.** See [README.md](README.md) for registry rules.

The envelope `intent` declares the purpose of a message (SIE-COM §A5). It is a dot-separated lowercase name with at least two labels. The first label is either `si` (reserved control intents, fully listed below), a registered **application domain**, or an `x-` private prefix. The rest of the name is free, for example `scheduling.propose` or `telemetry.report.hourly`. An intent never grants authority; the capability token and local policy do (SIE-COM §A6).

## Reserved Control Intents (`si.*`)

Only these `si.*` intents exist. Any other `si.*` intent is invalid.

| Intent | Purpose | Section |
|---|---|---|
| `si.pairing.request` | Start pairing | SIE-COM §A3 |
| `si.pairing.response` | Answer a pairing request (out-of-band verification data) | SIE-COM §A3 |
| `si.pairing.confirm` | Confirm pairing after owner consent | SIE-COM §A3 |
| `si.pairing.reject` | Decline pairing | SIE-COM §A3 |
| `si.negotiate` | Version, suite, form, and profile negotiation | SIE-COM §B7 |
| `si.refused` | Refusal; `data` is a refusal object | SIE-COM §A7 |
| `si.ack` | Receipt acknowledgement | SIE-COM §A9 |
| `si.revocation` | Key or device revocation notice | SIE-COM §A2 |
| `si.statement` | Owner-signed identity statements, for example after owner-key rotation | SIE-COM §A2 |
| `si.stream.setup` | Stream setup with per-session keys (F7) | SIE-COM §A4 |
| `si.stream.rekey` | Stream rekeying (F7) | SIE-COM §A4 |
| `si.summary` | Signed summary of a negotiation that commits the owner | SIE-COM §A7 |
| `si.sync` | Mesh synchronisation (F1) | SIE-COM §A9 |

Pairing messages (`si.pairing.*`) and refusals (`si.refused`) are the only envelopes that may omit `cap_token`, and they never carry `instructions` (SIE-COM §A3, §A5, §A7).

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
