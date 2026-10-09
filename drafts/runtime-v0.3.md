# Open Standards for SI Edge Runtimes (Draft v0.3)

> **Status: Draft, not for implementation. No certification program exists.**
> Conformance profiles in this document are for discussion only. Before v1.0 any claim of conformance is a self-assessment and must not be presented as a certification. See [TRADEMARKS.md](../TRADEMARKS.md).

**Document:** SI Edge Runtimes (SIE-RT) · Draft v0.3 · roenu (@roenudev), Bern · 2026-10-09 · Supersedes v0.2 · Companions: [SI Edge-to-Edge Communication v0.1](edge-to-edge-communication-v0.1.md) (SIE-COM), [SI Edge Ready Provider v0.1](provider-v0.1.md) (SIE-PRV) · Shared terms: [TERMINOLOGY.md](../TERMINOLOGY.md) · Threats: [THREAT-MODEL.md](../THREAT-MODEL.md)

**Interpretation.** This is an open standard for a **personal SI**: an advanced AI agent runtime that runs natively on user-owned edge devices (phones, PCs, VPS instances, home servers, cars, robots) and **is the primary interface**. "SI" is shorthand used in these drafts for highly capable AI agent systems; it makes no claim that any system is superintelligent. Users talk to the runtime, and the runtime drives tools, apps, files, and hardware for them. The standard aims to be fast, efficient, secure, modular, adaptable, and open to everyone. It is model-agnostic: any local or remote model can be plugged in. Nothing here describes or implies any vendor's actual plans or products.

## 0. Conventions

- The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.
- **Profile tags.** Each normative rule starts with a tag such as **[R1]**, **[R2]**, or **[R3]**: the lowest conformance profile (§21) at which the rule applies. A rule tagged [R2] applies at R2 and R3. Below its tag, a rule is RECOMMENDED unless it says otherwise. Statements without a tag are non-normative.
- Each rule ends with a one-line *rationale*.

---

## 1. Scope and Terms

- **SI Runtime:** the on-device software that hosts agents, mediates every action, and presents the interface.
- **Runtime Core (Core):** the trusted part of the runtime. It enforces policy, permissions, egress, logging, and Trusted UI.
- **Edge Device:** hardware the owner controls that runs an SI Runtime or a shim (SIE-COM §B4).
- **Owner:** the person or organisation that controls a runtime, its policy, and its keys. **User:** a person who interacts with the runtime. On a personal device they are the same; on shared, family, or managed devices they can differ (§19).
- **Router Model:** a small local decision model ("System One", after the fast, intuitive mode of thinking in dual-process theory) that picks models and tools.
- **Control Plane:** a remote service that plans, orchestrates, or runs inference for the runtime (§12).
- **Provider:** any remote service the runtime calls, as defined in SIE-PRV.
- **Module:** any installable unit that ships with a signed manifest. Kinds: `feature`, `function`, `model`, `device-adapter` (software that connects to an external device or device API through its own protocol), `hardware` (installed or attached hardware discovered by the runtime, §4), `ui-kit`, and `legacy-adapter`.
- **Sideloaded module:** a module installed from outside the owner's chosen registries, including any self-signed module.
- **Capability:** an action exposed by the OS, an app, a module, or hardware.
- **Privacy Gateway:** the Core component that all outbound calls to cloud services pass through (§13). **Full gateway mode** is defined in §13.
- **Adaptation Profile:** the user-controlled description of how the runtime should communicate and work with them (§7).
- **Trusted UI:** fixed interface components rendered only by the Core (§5).
- **Egress:** any data that leaves the device. **Consequential Action:** an action that is irreversible, costs money, communicates externally, changes access rights, or moves something physically.
- **Residency tag:** an owner policy label that restricts where data may be processed and stored (§11).

## 2. Runtime Architecture

- **[R1]** The Core **MUST** be separate from models and modules. Models propose actions and the Core decides whether they run. *Rationale: a model must never be the security boundary.*
- **[R1]** The runtime **SHOULD** include a local Router Model that routes by sensitivity, cost, latency, and capability. *Rationale: sensitive and simple tasks stay local.*
- **[R1]** Remote models **MUST** be pluggable through a documented, vendor-neutral provider interface. *Rationale: no model lock-in.*
- **[R1]** Tools and apps **SHOULD** be reached through MCP (Model Context Protocol) or a compatible capability API (§6). *Rationale: reuse an open protocol.*
- **[R1]** The runtime **MUST** include a local memory store (§8) and a scheduler for persistent agents with per-agent budgets. *Rationale: durable state and controlled autonomy.*
- **[R1]** The runtime **MUST** work in a degraded, local-only mode without network access. *Rationale: losing the network must not make the device unusable or unsafe.*
- **[R1]** Everything outside the Core **MUST** be packaged as a module (§3), and the Core **SHOULD** be kept as small as practical. *Rationale: a small trusted base is easier to audit and keeps the system fast.*
- **[R1]** All model outputs, tool outputs, web content, provider responses, and peer content **MUST** be treated as untrusted data. An action proposed on the basis of untrusted content **MUST** pass Core policy checks and, if consequential, approval (§16). *Rationale: prompt injection can arrive through any content a model reads; this is a mitigation, not a guarantee.*

**Example connectors (non-normative).** The order of this list is not a ranking, and alphabetical order is not implied. Grok (xAI); then other hosted model providers; self-hosted open-weight models served locally (for example with llama.cpp, Ollama, or vLLM); and MCP-compatible tool servers. No vendor is endorsed or required. Examples are illustrative only, and any connector that implements the provider interface is equally conforming.

## 3. Modularity and Extensions

- **[R1]** Every feature, function, model, device adapter, UI kit, and legacy adapter outside the Core **MUST** be packaged as a module. *Rationale: one model for extending, auditing, and removing anything.*
- **[R1]** Each module **MUST** ship a signed manifest declaring: identity and publisher, version, kind (§1), compatibility range (a range of SIE-RT versions such as `>=0.3 <0.4`, and the minimum runtime profile), capabilities provided and required, permissions, data classes accessed, egress destinations and residency needs, resource and hardware needs, and an SBOM reference (§17). The machine-readable definition is [schemas/module-manifest.schema.json](../schemas/module-manifest.schema.json); signatures follow SIE-COM §A5.1 and extensions SIE-COM §A5.2. *Rationale: the owner and the Core know the blast radius before installing.*
- **[R1]** The Core **MUST** show the owner who signed each manifest (the `signer` in its signature block). Sideloaded modules (§1) **MAY** be self-signed, and **MUST** be labelled `sideloaded` in Trusted UI by the Core. *Rationale: open installation without hiding who vouches for the code.*
- **[R1]** Installation **MUST** require owner consent to the manifest's permissions. Any later expansion of permissions **MUST** require consent again. *Rationale: no silent privilege creep.*
- **[R1]** Modules **MUST** run sandboxed and limited to their manifest. Access beyond the manifest **MUST** be denied and logged. *Rationale: least privilege, enforced in practice.*
- **[R1]** Removing a module **MUST** revoke its capabilities and tokens, and **SHOULD** offer to delete its data. *Rationale: uninstalling has to actually remove access.*
- **[R1]** Model modules **MUST** identify their weights by cryptographic hash in the manifest, and the Core **MUST** verify the hash before loading. *Rationale: swapped or poisoned weights must be detectable.*
- **[R2]** Module registries **MUST** be open: anyone **MAY** run one, and runtimes **MUST** let the owner choose and add registries, including local sideloading. *Rationale: no single gatekeeper.*
- **[R2]** Registries **SHOULD** publish signatures to a public transparency log and publish revocation lists, and the runtime **MUST** honour revocations from the registries the owner uses. *Rationale: a compromised module needs a kill path.*
- **[R3]** Core and module builds **SHOULD** be reproducible and **SHOULD** publish build provenance (for example at a SLSA build level). *Rationale: attested devices need attestable inputs.*
- **[R1]** Legacy adapters (Methods 1 to 5, SIE-COM §B2 to §B6) **MUST** be modules and **MUST** carry the `legacy` and `unattested` labels defined there. *Rationale: compatibility code is held to the same rules.*

## 4. Hardware Discovery and Compatibility

- **[R1]** The runtime **SHOULD** detect installed and attached hardware (sensors, cameras, microphones, GPUs/NPUs, peripherals, vehicles, robots) and offer each item as a module of kind `hardware`. *Rationale: the runtime should use the device it actually runs on.*
- **[R1]** Each item **MUST** be described by a **capability descriptor**: type, functions, performance class (`constrained`, `standard`, or `high`), safety constraints, and whether it is attested. *Rationale: the router needs facts it can compare across devices.*
- **[R1]** Enabling any hardware module **MUST** require owner consent, and sensors and actuators **MUST** be gated individually with visible indicators while active. *Rationale: hardware is the most sensitive capability.*
- **[R1]** When hardware is missing or fails, the runtime **MUST** degrade gracefully: use another local option, offer a mesh device (with consent), or explain the limitation. *Rationale: the interface must not break silently.*
- **[R1]** Actuator modules (cars, robots) **MUST** declare safe-stop behaviour and **SHOULD** follow applicable sector safety standards (for example ISO 26262 for road vehicles, ISO 10218 or ISO 13482 for robots). *Rationale: physical consequences need physical safeguards.*

## 5. Interface Layer and Generated UI

- **[R1]** The runtime **MUST** support every input modality among text, voice, and vision that the hardware and installed models provide, and at least one of them. *Rationale: the runtime is the interface.*
- **[R1]** Each device **MAY** generate UI tailored to the task, the device, and the user's Adaptation Profile. Generated UI **MUST** be rendered by the Core from a declarative schema, not from arbitrary model-written code. *Rationale: generated UI is an attack surface.*
- **[R1]** **Trusted UI elements** (approval prompts, kill switch, egress and activity indicator, identity of the acting agent and model, `legacy`, `unattested`, and `sideloaded` labels) **MUST** be rendered only by the Core from fixed components. *Rationale: models and modules must not be able to fake or hide them.*
- **[R1]** Trusted UI elements **MUST** have the same meaning and behaviour on every conforming device and **MUST** be delivered through a channel that generated UI and modules cannot draw on or imitate (for example a reserved screen region, a secure overlay, a hardware indicator, or a reserved audio cue). Their presentation **MAY** adapt to the form factor and to accessibility settings, provided they stay distinguishable from generated UI. *Rationale: one trustworthy signal that still works for every body and device.*
- **[R2]** Generated UI **MUST NOT** use the reserved components, screen region, icons, or audio cues of Trusted UI, and the Core **MUST** reject generated layouts that do. *Rationale: a testable anti-spoofing rule.*
- **[R1]** Approvals given by voice alone **MUST** require a step that model-generated audio cannot complete on its own (for example a physical button, a device unlock, or repeating a one-time code that only the Core presents). *Rationale: a synthetic voice can imitate an approval prompt.*
- **[R1]** Legacy apps **MUST** remain available, and the user **MUST** be able to bypass the agent. *Rationale: the agent must never be the only way into the device.*
- **[R1]** The runtime **MUST** always show what the agent is doing (active task, tools, data leaving the device). *Rationale: delegated action has to be observable.*
- **[R1]** Visual interfaces **MUST** meet WCAG 2.2 level AA, approval prompts and the kill switch **MUST** be operable with assistive technology (screen reader, switch access, voice), and users **SHOULD** be able to switch modality mid-task. *Rationale: replacing the interface must not exclude anyone.*

## 6. Device and App Capability API

- **[R1]** The runtime **MUST** prefer declared capabilities over UI automation wherever both exist. Each capability **MUST** have a permission manifest listing capabilities, data classes, destinations, and consequential actions. *Rationale: structured actions are reliable and auditable.*
- **[R1]** Capabilities **SHOULD** use an MCP-compatible typed schema. *Rationale: one description works for every model.*
- **[R1]** UI automation **MAY** be used as a fallback under the same checks and logging, packaged as a legacy module (§3). *Rationale: fallbacks must not become loopholes.*

## 7. Onboarding, Progressive Learning, and Adaptation

- **[R1]** First start **MUST** collect only the basics: language, input preferences, privacy and egress choices, and the approval policy. Everything else **MUST** be optional. *Rationale: low friction and data minimisation from the first minute.*
- **[R1]** Further learning **MUST** be consented. The runtime **SHOULD** ask before storing a new kind of personal information and **MUST** show what it has learned. *Rationale: no hidden profiling.*
- **[R1]** The runtime **MUST** offer adaptation settings covering at least pacing, level of detail, literal versus figurative language, sensory preferences (motion, sound, density, contrast), and executive-function support (chunking, reminders, task breakdown), and **MUST** apply them across all output. It **SHOULD** support non-standard communication styles and neurodivergent users. *Rationale: an interface that replaces apps has to fit people as they are.*
- **[R1]** Adaptation **MUST NOT** label, infer, or record diagnoses or medical categories. It **MUST** describe preferences, not conditions. *Rationale: avoids sensitive inferences and stigma.*
- **[R1]** The **Adaptation Profile** **MUST** be visible, editable, resettable, and exportable by the user. The user **MAY** set it directly instead of letting the runtime learn it. *Rationale: the user controls how they are modelled.*
- **[R1]** The runtime **MUST NOT** present adapted communication styles as errors, and **MUST NOT** change Adaptation Profile settings back toward a default without the user's action. *Rationale: no normalising toward a default user.*
- **[R1]** The Adaptation Profile **MUST NOT** leave the device unless the egress policy explicitly allows it, and the Privacy Gateway **SHOULD NOT** include it, or style instructions derived from it, in provider calls unless the task needs them. *Rationale: it is sensitive personal data and a fingerprinting vector.*

## 8. Persistent Agents and Memory

- **[R1]** Memory **MUST** be structured (facts, preferences, episodes, skills, with source and timestamp), stored on-device, encrypted at rest, and kept in an open documented format (for example SQLite plus JSONL/Markdown). *Rationale: memory is the user's data and must be usable without the vendor.*
- **[R1]** Users **MUST** be able to inspect, edit, delete, and export memory in a documented format. *Rationale: supports the access, portability, and erasure rights in the nFADP and the GDPR.*
- **[R2]** Runtimes **MUST** import memory in the open memory format once it is published (README roadmap). Until then they **MUST** publish their export format. *Rationale: portability needs a shared format before it can be tested.*
- **[R1]** Memory **MUST** have per-agent scopes. Sharing between agents **MUST** be explicitly granted. *Rationale: least privilege for memory too.*
- **[R1]** Persistent agents **MUST** run under budgets and **MUST** be listable and stoppable. *Rationale: background autonomy needs visible limits.*
- **[R1]** The runtime **MUST** offer an encrypted backup of memory, Adaptation Profile, and policy that the owner can restore on a new device (§10). *Rationale: keys that never leave a device must not mean data that dies with it.*

## 9. Multi-Device Continuity

- **[R2]** A user's devices **MAY** form one runtime mesh with shared identity, policy, memory, and Adaptation Profile. If they do, sync **MUST** be end-to-end encrypted with keys only the owner's devices hold, and **SHOULD** be peer-to-peer where possible, as defined in SIE-COM (form F1). *Rationale: one assistant across many devices, without giving up sovereignty.*
- **[R1]** Each device **MUST** be individually revocable. *Rationale: losing one device must not compromise the others.*
- **[R2]** Policy **MUST** be able to restrict data by device (for example "health data never syncs to the VPS"). *Rationale: devices differ in trust and jurisdiction.*

## 10. Device Identity, Attestation, and Key Recovery

- **[R1]** Each device **MUST** have a cryptographic identity whose private key never leaves the device and **MUST** be rotatable and revocable by the owner. The key **SHOULD** be hardware-backed (TPM 2.0, a secure enclave, or a TEE). *Rationale: the owner controls trust.*
- **[R3]** Device keys **MUST** be hardware-backed. *Rationale: attested profiles need keys that cannot be copied.*
- **[R1]** The Core **MUST** be signed and verified at startup. *Rationale: an unsigned Core cannot be trusted with every interaction.*
- **[R3]** The device **MUST** support measured boot and remote attestation of the Core. *Rationale: peers and providers can verify what they talk to.*
- **[R1]** Peers and providers **MUST NOT** require remote attestation from a runtime that does not claim R3. *Rationale: verified trust without excluding DIY hardware.*
- **[R1]** The owner key **MUST** be distinct from device keys and **SHOULD** be held on a separate device or hardware token, or protected by a recovery scheme (for example threshold or social recovery), so that losing one device does not lose ownership. *Rationale: ownership must survive the loss of any single device.*
- **[R1]** The runtime **MUST** document a recovery path for the loss of all devices (for example restoring the §8 backup with an owner-held recovery secret). If the owner declines recovery, the runtime **MUST** warn at onboarding that data cannot be recovered. *Rationale: honest trade-off between security and loss.*
- **[R2]** When a device is revoked, the remaining mesh **MUST** rotate shared sync and group keys so the revoked device cannot read later data. *Rationale: revocation must cut off future access, not only new sessions.*
- **[R2]** The runtime **MUST** support a documented owner-key rotation that re-issues device and agent statements and notifies paired peers (SIE-COM §A2). *Rationale: a compromised owner key must be replaceable without starting over.*

## 11. Data Sovereignty, Egress, and Residency

- **[R1]** Data **MUST** stay on the device by default, and each egress destination **MUST** be approved by the owner. *Rationale: locality is the default.*
- **[R2]** Egress **MUST** follow an explicit, user-editable policy covering destination, data class, purpose, and residency tag. *Rationale: sharing is a deliberate, reviewable choice.*
- **[R2]** The Core **MUST** keep an append-only egress log. *Rationale: claims have to be checkable.*
- **[R2]** Egress and audit logs **MUST** be encrypted at rest, **MUST** have an owner-configurable retention period, and **MUST** support deleting entry content (for example by destroying per-entry keys) while keeping the hash chain verifiable. *Rationale: append-only logs must not defeat erasure or become a surveillance tool.*
- **[R2]** The runtime **MUST** record each provider's declared retention window (SIE-PRV §3) in the privacy report, and owner policy **MAY** block providers with any retention window. *Rationale: retention by remote parties is governed by the provider standard; the runtime makes it visible.*

**Residency tags.** Residency tags express the owner's policy about where data may be processed and stored. They are a policy choice and are stricter than the default rules of the Swiss nFADP and the EU GDPR, which allow transfers abroad under conditions such as adequacy decisions or appropriate safeguards. Tags can help an owner meet those rules; they are not a statement of what the law requires.

- **[R2]** Runtimes **MUST** support at least these tags: `CH` (processing and storage only in Switzerland), `EU` (only in EU and EEA member states), and `CH-EU` (in Switzerland or in EU and EEA member states). Owners **MAY** define additional tags; owner-defined tags **MUST** start with `x-` (lowercase letters, digits, and hyphens, at most 64 characters), so they never collide with future standard tags. *Rationale: shared, unambiguous meanings across runtimes and providers.*
- **[R2]** When several tags apply to the same data, they combine by intersection: the data may be processed and stored only where every tag allows. *Rationale: adding a tag must never widen where data may go.*
- **[R1]** Data classes used in egress policy, manifests, envelopes, and privacy reports **MUST** come from the data-class registry ([registries/data-classes.md](../registries/data-classes.md)) or start with `x-`. *Rationale: runtimes, modules, and providers must mean the same thing by "health data".*
- **[R2]** A destination that cannot confirm it honours a tag, and any tag the runtime does not recognise, **MUST** be treated as not allowed (fail closed). *Rationale: unknown means no.*

## 12. Remote Models and Control Plane

- **[R1]** Connections to a Control Plane or remote model **MUST** be initiated outbound by the device and mutually authenticated (mTLS with TLS 1.3, or SSH), with no open inbound port required. Peer-to-peer and mesh connections are governed by SIE-COM. *Rationale: small attack surface, works behind NAT.*
- **[R1]** Capabilities, the egress-policy hash, and the conformance profile **MUST** be negotiated on connect. *Rationale: limits agreed up front.*
- **[R1]** Every control-plane request **MUST** pass local permission checks, and the user **MUST** be able to detach instantly, falling back to local mode. *Rationale: a remote planner is an untrusted caller, and being able to leave is part of ownership.*

## 13. Private Cloud Calls

- **[R1]** All outbound calls to cloud models, public APIs, search, and the web **MUST** pass through the local **Privacy Gateway**. *Rationale: one enforcement point.*
- **[R1]** **Full gateway mode** means the Gateway applies all of the following: minimal context selection; local redaction and pseudonymisation of personal data in the data classes the policy marks as sensitive; stripping of tracking parameters and identifying headers; no account and no persistent identifiers across calls; a fresh anonymous credential per call where the provider supports one; and routing through a privacy relay (for example an Oblivious HTTP relay or an IP-hiding proxy). *Rationale: a precise baseline for untrusted providers.*
- **[R1]** If no relay is available, the runtime **MUST** warn the user and **MUST** block calls that contain data classes the policy marks as relay-required. *Rationale: "when available" must not silently become "never".*
- **[R1]** The Router **SHOULD** prefer local inference for tasks containing sensitive data classes, and owner policy **MAY** require it. *Rationale: the best protection is not sending data at all.*
- **[R1]** Runtimes **MUST** treat every provider as P0 (SIE-PRV §11) unless they have verified its profile as defined in SIE-PRV §12. Verification is REQUIRED at R3 and OPTIONAL below. *Rationale: trust is verified, not assumed.*
- **[R1]** For P0 providers the runtime **MUST** use full gateway mode, or let the user explicitly choose their own API key or account. Under that choice it **MUST** label clearly that the provider can link requests to that account. *Rationale: informed choice, never silent exposure.*
- **[R1]** Each call **MUST** produce a user-visible **privacy report** ([schemas/privacy-report.schema.json](../schemas/privacy-report.schema.json)): provider, provider profile (claimed, effective, and whether verified, with any downgrade), gateway mode, relay used, network identity exposed (relay or direct), account linkage, data classes and field names sent after redaction, data classes and field names redacted or pseudonymised, minimisation steps applied, a hash of the exact outbound payload, residency tags, the provider's declared retention window (an ISO 8601 duration, or `undeclared`), and the model identity when the provider returns one. Reports **MUST** list field names and data classes, never values, and **MUST NOT** contain redaction maps. *Rationale: the user can judge each call, from the same profile at which the Gateway is required.*
- **[R2]** Runtimes **MUST** provide **verifiable minimisation**: for each call the Gateway logs the exact outbound payload, or a reproducible hash plus redaction map, under the log protections in §11, and the privacy report's payload hash **MUST** match that log entry. Redaction maps **MUST NOT** leave the device. *Rationale: honesty, backed by evidence.*
- **[R2]** The Gateway **SHOULD** resolve DNS through the relay or an encrypted resolver and **SHOULD** pad or batch requests where practical. *Rationale: metadata reveals behaviour even when content is protected.*

*Note (non-normative): this standard does not claim that zero personal data leaves the device. Content itself can identify a person. The goal is minimisation that the user can verify.*

## 14. Model Routing Transparency

- **[R2]** Every run **MUST** record the model and version, where it ran (with region and provider profile), the routing reason, and the data classes sent. Records **MUST** be visible to the user and **SHOULD** be exportable as OpenTelemetry. *Rationale: users have to know which model saw what.*
- **[R1]** User routing rules **MUST** override router decisions. *Rationale: user policy outranks optimisation.*

## 15. Credentials and Secrets

- **[R1]** Credentials **MUST** stay on the device in an OS or hardware-backed keystore, and **MUST NOT** be included in any model context. Tools use secrets by reference, executed by the Core. *Rationale: a model that never sees a secret cannot leak it.*
- **[R3]** Credentials **MUST** be held in a hardware-backed keystore. *Rationale: attested profiles need non-exportable secrets.*
- **[R1]** Delegated access **SHOULD** use scoped, expiring, sender-bound tokens following the OAuth 2.0 Security Best Current Practice (RFC 9700), or OAuth 2.1 (an IETF Internet-Draft, cited as work in progress). *Rationale: least privilege.*

## 16. Permissions, Approval, and Kill Switch

- **[R1]** Consequential actions **MUST** require human approval through Trusted UI unless the user has pre-authorised a narrow policy. Prompts **MUST** show the action, target, proposing agent and model, and data involved, in plain language. *Rationale: informed human control.*
- **[R1]** Pre-authorised policies **MUST** be bounded by scope, amount, and time, and **MUST** be listable and revocable. Runtimes **SHOULD** group low-risk approvals and **SHOULD** warn when approval patterns suggest fatigue (for example many approvals in a short time). *Rationale: approvals that are clicked through protect no one.*
- **[R1]** A local kill switch **MUST** stop all agents and modules, revoke remote sessions, and work offline. Actuated devices **SHOULD** also have a hardware stop. *Rationale: the off switch belongs to the owner.*

## 17. Safety, Updates, and Supply Chain

- **[R1]** Core and module updates **MUST** be signed, verified, consented to by policy, and possible to roll back. *Rationale: the supply chain is an attack surface, and a bad update must not lock the user out.*
- **[R1]** Rollback **MUST NOT** install a version that is revoked or marked `sunset` (SIE-COM §B8). *Rationale: rollback must not become a downgrade attack.*
- **[R1]** Packages **MUST** ship SBOMs (SPDX or CycloneDX), referenced with a digest from the module manifest (§3). *Rationale: you cannot audit what you cannot list, and the manifest already requires the reference at R1.*

*Note (non-normative): module publishers and remote providers may need to document how their offerings map to EU AI Act obligations, using the Act's own roles (such as provider and deployer). This standard does not provide compliance with the Act.*

## 18. Efficiency, Energy, and Resources

- **[R1]** The Core **SHOULD** load modules and models lazily and unload idle ones. *Rationale: fast startup and low resource use on small devices.*
- **[R1]** The runtime **MUST** respect user budgets (battery, thermal, cost). *Rationale: running locally has hard limits.*
- **[R3]** The runtime **MUST** report per-task compute and estimated energy. *Rationale: local and remote options can be compared fairly.*

## 19. People, Shared Devices, and Vulnerable Users

- **[R1]** When the owner is not the user (for example an employer, a family administrator, or a guardian), every policy the owner applies to the user **MUST** be visible to that user in Trusted UI. *Rationale: no hidden control.*
- **[R1]** On devices used by more than one person, the runtime **MUST** keep memory, logs, and Adaptation Profiles separate per person, and **MUST NOT** let one person read another's data without consent, except under a guardian role (below). Any such access **MUST** be visible to the affected person. *Rationale: shared hardware must not mean shared private life.*
- **[R1]** The runtime **MUST NOT** offer covert monitoring of another adult user. *Rationale: an agent runtime must not become a stalkerware platform.*
- **[R1]** Runtimes intended for use by children **MUST** default to guardian approval for consequential actions and to conservative egress, **MUST** make guardian controls visible to the child, and **SHOULD** let autonomy grow with age. *Rationale: protection without secret surveillance.*
- **[R2]** Runtimes **SHOULD** offer protection against coercive co-users: a clear list of devices, people, and sessions with access; alerts when a device joins the mesh or logs are exported; and a quick safety mode that hides recent activity from the visible interface without destroying evidence. *Rationale: abusers often have physical access to the victim's devices.*
- **[R1]** Runtimes **SHOULD** let users name a trusted contact for help with high-stakes approvals, and **SHOULD** allow extra time and confirmation steps on request. *Rationale: support for vulnerable users without taking away their decisions.*

## 20. Security and Privacy Considerations (non-normative)

- Adversaries, assets, and the rules that address them are listed in [THREAT-MODEL.md](../THREAT-MODEL.md).
- Instruction and data separation (§2, SIE-COM §A5) reduces prompt injection but cannot remove it. Core policy checks and approvals are the backstop.
- Metadata (timing, sizes, DNS, sync patterns, writing style) can reveal behaviour even when content is protected. §7, §13, and SIE-COM §A8 address parts of this; complete metadata privacy is out of scope.
- Logs, memory, and Adaptation Profiles are among the most sensitive data a runtime holds. Their protection (§11, §19) matters as much as protection against remote parties.

## 21. Conformance Profiles

| Profile | Name | Requires |
|---|---|---|
| **R1** | Basic | Every rule tagged [R1]. In summary: Core/model separation, local mode, untrusted-content handling (§2); signed manifests, sandboxing, model hashes (§3); consented hardware (§4); Trusted UI, accessibility, legacy fallback (§5); capability manifests (§6); minimal onboarding and Adaptation Profile (§7); local exportable memory and backup (§8); device keys, signed Core, key recovery (§10); default-local data and registered data classes (§11); outbound control plane (§12); Privacy Gateway with full gateway mode and per-call privacy reports (§13); local secrets (§15); approvals and kill switch (§16); signed updates without unsafe rollback, SBOMs (§17); shared-device protections (§19); communication at C1 |
| **R2** | Sovereign | R1 + every rule tagged [R2]: open registries with revocation (§3), Trusted UI anti-spoofing (§5), memory import (§8), E2E mesh (§9), mesh re-keying and owner-key rotation (§10), egress policy, protected logs, residency tags (§11), verifiable minimisation (§13), routing records (§14); communication at C2 |
| **R3** | Attested | R2 + every rule tagged [R3]: reproducible builds (§3), hardware-backed keys, measured boot and remote attestation (§10), provider profile verification (§13), hardware-backed secrets (§15), resource reporting (§18); communication at C3 |

- Before v1.0, any claim of conformance is a **self-assessment** only. It **MUST NOT** be presented as a certification, and it **SHOULD** be published together with the evidence for each rule. *Rationale: there is no certification program, and claims must not imply one.*
- A self-assessment **SHOULD** be phrased as "Self-assessed against SI Edge Runtimes draft v0.3, profile R2". *Rationale: neutral wording that cannot be mistaken for a seal.*
- How R, C, and P profiles combine for one session is defined in the README ("How They Fit Together").

## 22. Open Questions

1. Who governs the module manifest schema and the capability descriptor vocabulary (hardware types and function names are not yet registered)?
2. How can adaptation profiles be portable across runtimes without becoming a fingerprinting vector?
3. Which redaction and pseudonymisation methods are good enough to count as "verifiable minimisation"?
4. How can Trusted UI channels be defined for very different form factors (watch, car, robot, terminal, voice-only)?
5. Can a VPS count as user-owned without confidential computing?
6. What age bands and guardian models work across jurisdictions without requiring identity checks?
7. Which recovery schemes are usable by non-experts without weakening owner keys?

## 23. References

BCP 14 (RFC 2119, RFC 8174); TLS 1.3 (RFC 8446); Oblivious HTTP (RFC 9458); OAuth 2.0 Security BCP (RFC 9700); OAuth 2.1 (draft-ietf-oauth-v2-1, work in progress); Model Context Protocol specification; TPM 2.0 (TCG); WCAG 2.2 (W3C); OpenTelemetry; SPDX; CycloneDX; SLSA; Swiss Federal Act on Data Protection (nFADP); EU General Data Protection Regulation (GDPR); EU AI Act (Regulation (EU) 2024/1689).

---
*Schema alignment revision (2026-10-09): module kinds including `hardware` and the sideloaded definition (§1), manifest contents and compatibility range syntax (§3), performance classes (§4), `x-` owner residency tags, tag intersection, and registered data classes (§11), privacy reports moved to R1 with defined contents (§13), SBOMs moved to R1 (§17).*

*v0.3 changes: added modularity (§3), hardware discovery (§4), generated UI with Trusted UI (§5), onboarding and adaptation (§7), key recovery (§10), Private Cloud Calls with full gateway mode (§13), efficiency (§18), people and shared devices (§19); profile tags on every rule; conformance profiles linked to C and P profiles. Full history in [CHANGELOG.md](../CHANGELOG.md).*
