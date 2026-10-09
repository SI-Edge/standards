# Open Questions from Writing the v0.1 Schemas

> **Status: Draft, not for implementation.**

Writing the schemas showed places where the drafts are ambiguous, silent, or inconsistent. For each one the schemas take the **conservative** option (stricter, fail closed) and record it here. Each item should become a spec bug or proposal issue (see [CONTRIBUTING.md](../CONTRIBUTING.md)) and be resolved in the drafts, after which the schema follows the draft.

## Envelope (SIE-COM A5)

1. **No field marks a pairing message.** A5 says `cap_token` is required "Always, except pairing messages", but nothing in the envelope says a message is a pairing message. *Schema choice:* the intent namespace `si.pairing.*` is reserved for pairing; only those envelopes may omit `cap_token`, and they may not carry `instructions`. *Proposal:* define pairing intents in the intent vocabulary, or add a pairing form or flag.
2. **Trust labels have no field.** SIE-COM B1 requires legacy endpoints to be labelled `legacy` and `unattested` "in the envelope", and B5 requires the proxy in `provenance`, but A5 has no labels field. *Schema choice:* labels live on `provenance` hops; a hop with role `legacy-endpoint` must carry both labels. *Proposal:* add this to the A5 table or define the provenance entry format.
3. **`attestation_ref` "at C3" cannot be checked.** The envelope carries no profile, so a receiver (or schema) cannot tell from the envelope whether C3 applies. *Schema choice:* the member is always present and is `null` when empty. *Proposal:* bind the negotiated profile into the envelope or reference the signed negotiation transcript (B7).
4. **"State-changing" is not defined.** A9 requires `idem_key` on state-changing messages. *Schema choice:* `idem_key` is required whenever `instructions` is present.
5. **Instructions "signed by the sender".** A5 says `instructions` are signed by the sender, but the whole envelope is already signed by the agent key. *Schema choice:* the envelope `sig` covers `instructions`; there is no separate signature. *Proposal:* say so explicitly, or define a detached signature if instructions are forwarded without the envelope.
6. **Signature input and canonical form.** A5 allows deterministic CBOR or JCS but does not say which one a signature uses, or that `sig` is excluded. *Schema choice:* `sig.canon` names the encoding (`dcbor` or `jcs`); the signature covers the object without `sig`. *Proposal:* make one encoding mandatory for interoperability (for example deterministic CBOR on the wire, JCS for JSON transports).
7. **Single or multiple recipients.** `aud` is "intended recipient" (singular), but MLS groups and multi-party sessions (A4) have several. *Schema choice:* exactly one recipient.
8. **Owner-defined residency tags have no syntax.** SIE-RT 11 lets owners define additional tags. *Schema choice:* owner tags use an `x-` prefix (`x-home-only`) so they can never collide with future standard tags. Unknown tags still fail closed at runtime.
9. **Several residency tags on one message.** No draft says how several tags combine. *Schema choice:* documented as intersection (most restrictive). An empty tag list means the owner set no residency restriction; that reading needs confirmation.
10. **Data-class vocabulary.** SIE-RT 11 and 13 use data classes ("data classes the policy marks as sensitive", "relay-required"), but no vocabulary exists. *Schema choice:* lowercase dotted names; no fixed list. *Proposal:* a registered core vocabulary (health, location, contacts, finance, ...) plus extensions.
11. **Intent and refusal vocabularies** (SIE-COM D Q1). *Schema choice:* lowercase dotted names; `si.pairing.*` and `si.refused` are reserved. The refusal message format (A7, SIE-PRV 6 and 9) has no schema yet.
12. **F5 and envelopes.** A1 says the form is recorded in the envelope "or, for F5, in the advertisement". *Schema choice:* `F5` is not allowed in an envelope. The advertisement format is undefined.
13. **Nonce length and timestamp format** are not specified. *Schema choice:* nonces of at least 128 bits (22 base64url characters); RFC 3339 timestamps with an explicit offset.
14. **Data with no type.** A5 requires `payload_type` "when data is present". *Schema choice:* `data` and `payload_type` must appear together.

## Capability Token (SIE-COM A6)

15. **"Short-lived" has no bound.** A6 requires short-lived tokens, but gives no maximum lifetime. This conflicts with the CONTRIBUTING rule that rules must be testable. *Schema choice:* none enforced; the validator only checks `exp` after `iat` and child `exp` not after parent `exp`. *Proposal:* a default maximum (for example 1 hour, owner-configurable).
16. **Attenuation semantics for resources and constraints are undefined.** *Validator choice:* a child right is covered by a parent right with the same action and an equal resource, or a parent resource ending in `/*` that prefixes it; numeric constraints and budgets may only go down; a constraint or budget limit the parent set cannot be dropped; the audience stays the same along the chain; each child's `iss` is the parent's `sub` (holder).
17. **Other token formats.** A6 allows "an attenuable token format". *Schema choice:* the envelope accepts such tokens wrapped as `{format, token}`, but their attenuation cannot be checked by this validator.
18. **Token and envelope binding.** *Validator choice:* an SI token in an envelope must have `sub` equal to `sender_agent`, `aud` equal to the envelope `aud`, and must grant the requested `instructions.action`.
19. **Cross-owner delegation below C2** must not happen (A6), but tokens carry no owner identity, so this cannot be checked from the token. *Proposal:* add an owner claim or rely on owner statements (A2).

## Module Manifest (SIE-RT 3, 4)

20. **SBOM level conflict.** SIE-RT 3 [R1] requires an SBOM reference in every manifest, but SIE-RT 17 makes shipping SBOMs REQUIRED only at [R2]. *Schema choice:* the SBOM reference is always required (stricter reading). *Proposal:* align 3 and 17.
21. **"Runtime version" in the compatibility range** could mean the standard version or an implementation version, and no range syntax is defined. *Schema choice:* the standard version, as a free-form range string.
22. **Hardware modules.** SIE-RT 1 lists module kinds without hardware, but SIE-RT 4 offers each hardware item "as a module". *Schema choice:* an extra kind `hardware` that must carry a capability descriptor, distinct from `device-adapter`. Clarify the difference.
23. **Capability descriptor vocabulary** (type, functions, performance class) is undefined (SIE-RT 22 Q1).
24. **`sideloaded` definition differs.** TERMINOLOGY says "signed outside the owner's registries"; SIE-RT 3 ties it to self-signed sideloaded modules. The label is applied by the Core, so the manifest has no field for it.

## Privacy Report (SIE-RT 13)

25. **Fields, not values.** SIE-RT 13 lists "fields sent after redaction" and "what was redacted". *Schema choice:* field names and data classes only, never values; redaction maps are rejected (they must not leave the device, and reports are stored and possibly exported).
26. **Residency and model identity** are not in the SIE-RT 13 list but are needed to judge a call (SIE-RT 11, 14). *Schema choice:* included; residency required, model optional (some calls are not model calls).
27. **Retention format.** SIE-PRV 3 requires a declared window but no format. *Schema choice:* ISO 8601 duration (`PT0S` for none) or `undeclared`. "Short" has no bound.
28. **Report level versus gateway level.** Full gateway mode is [R1], but the privacy report is [R2], so an R1 runtime can call a P0 provider with no report. Intended?

## Provider Manifest (SIE-PRV 8, 11)

29. **"Equivalent mapping" of the envelope** (SIE-PRV 6) cannot be described in a manifest. *Schema choice:* a P2 claim requires `envelope.accepted: true`.
30. **Audit renewal.** "Renewed at least every two years" (SIE-PRV 10) is read as `valid_until` at most two years after `issued`.
31. **Model identity per response** (SIE-PRV 7) has no response format; only the manifest side is covered here.
32. **OHTTP is for non-streaming requests**, and no private path for streaming is defined.
33. **P0 manifests.** P0 means "no claims", but a provider may still publish a manifest; the schema allows a P0 claim with no other requirements.

## General

34. **Extensions and minor versions.** The schemas reject unknown members (fail closed). SIE-COM A5 rejects unknown *major* versions, which suggests minor versions may add members. *Proposal:* define an extension mechanism (for example an `ext` object with namespaced keys) and the rule that a receiver ignores unknown members only inside it.
35. **Tier numbers.** The README defines tiers 0 to 3 by name; the privacy report uses the integer for `effective_tier`.
