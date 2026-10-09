# Threat Model

> **Status: Draft, not for implementation. No certification program exists.**

This document lists the assets the Selfkin drafts protect, the adversaries they consider, and the rules that address each threat. It is non-normative; the rules live in the drafts. Section references: **RT** = [runtime v0.3](drafts/runtime-v0.3.md), **COM** = [communication v0.1](drafts/edge-to-edge-communication-v0.1.md), **PRV** = [provider v0.1](drafts/provider-v0.1.md).

## Assets

- Personal data: memory, files, messages, Adaptation Profile, sensor data.
- Credentials and keys: device, agent, and owner keys; API keys; tokens.
- Control: the ability to take consequential and physical actions.
- Logs and privacy reports (sensitive in themselves).
- Metadata: who talks to whom, when, and how much.

## Assumptions

- The Core and the device's hardware root of trust (where present) work as specified.
- The owner can see Trusted UI and make decisions, possibly with help (RT §19).
- Cryptographic building blocks (TLS 1.3, Noise, MLS, signatures) are secure when used correctly.

## Adversaries and Mitigations

| # | Adversary or threat | Example | Main mitigations |
|---|---|---|---|
| T1 | Malicious or compromised module | Exfiltrates data, escalates permissions | Signed manifests, signer shown, sandboxing, consent on expansion, revocation (RT §3); SBOMs (RT §17) |
| T2 | Malicious or compromised registry | Ships a backdoored update | Owner-chosen registries, transparency logs, revocation, reproducible builds (RT §3); signed updates (RT §17) |
| T3 | Poisoned or swapped model weights | Model behaves maliciously on triggers | Weight hashes verified before load (RT §3); Core/model separation (RT §2) |
| T4 | Prompt injection via content | Web page or email tells the agent to send files | Untrusted content rule and policy checks (RT §2); instruction/data separation (COM §A5); approvals (RT §16). Residual risk remains |
| T5 | Malicious peer agent | Negotiates deceptively, floods requests, social-engineers the human | Untrusted peer content, rate limits, refusals (COM §A7); cross-owner approvals (COM §A6); human-instruction rule (COM §B6) |
| T6 | Curious or malicious provider | Logs, trains on, or profiles requests | Privacy Gateway and full gateway mode (RT §13); provider rules and verification (PRV §3, §4, §12) |
| T7 | Relay colluding with provider | Joins network identity to content | OHTTP separation (PRV §4); privacy report shows exposure (RT §13). Residual risk if both collude |
| T8 | Network attacker | Man-in-the-middle, replay, downgrade | E2E with mutual auth (COM §A4); envelope `aud`, `nonce`, `seq` (COM §A5); signed transcripts and pinning (COM §B7) |
| T9 | Lost or stolen device | Thief uses keys or reads memory | Hardware-backed keys, encryption at rest (RT §8, §10); device revocation and mesh re-keying (RT §10, COM §A2); kill switch (RT §16) |
| T10 | Owner key loss or compromise | Owner locked out, or attacker takes over the mesh | Separate owner key, recovery scheme, rotation (RT §10) |
| T11 | Compromised Core update or rollback | Old vulnerable version reinstalled | Signed updates, no rollback to revoked or sunset versions (RT §17, COM §B8); measured boot at R3 (RT §10) |
| T12 | Trusted UI spoofing | Generated UI or synthetic voice imitates an approval prompt | Core-only rendering on a reserved channel, anti-spoofing, voice approval step (RT §5) |
| T13 | Coercive co-user | Abusive partner, controlling parent or employer with device access | Visible owner policies, per-person separation, no covert monitoring, safety mode (RT §19); protected logs (RT §11) |
| T14 | Metadata observer | Infers relationships from timing and size | Minimal advertisements (COM §A3); metadata minimisation, padding (COM §A8, RT §13). Partial only |
| T15 | Physical attacker on actuators | Forces unsafe movement | Safe-stop declarations, hardware stop, approvals (RT §4, §16); proxy approvals (COM §B5) |
| T16 | Approval fatigue | User clicks through prompts | Bounded pre-authorisations, grouping, fatigue warnings (RT §16) |

## Out of Scope

- Attacks on the hardware root of trust itself (for example side channels on TEEs).
- A fully compromised OS kernel below the Core on devices without attestation.
- Global passive adversaries that see all network traffic.
- Legal compulsion of the owner.

## Open Issues

- Measuring and proving redaction quality (RT §22 Q3).
- Correct translation by proxies for unprotected legacy protocols (COM §D Q4).
- Attestation for distributed inference (PRV §13 Q4).
