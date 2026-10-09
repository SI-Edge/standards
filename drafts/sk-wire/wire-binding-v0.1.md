# Selfkin Wire Binding (Draft v0.1)

> **Status: Draft, not for implementation. No certification program exists.**
> This document binds SK-COM to concrete transports, discovery, pairing, message types, and encryption. Its identifiers are provisional and its test vectors are provisional. It depends on the SK-COM changes listed in section 10, proposed in separate pull requests. Any claim of conformance is a self-assessment; see [TRADEMARKS.md](../../TRADEMARKS.md).

**Document:** Selfkin Wire Binding (SK-WIRE) · Draft v0.1 · roenu (@roenudev) · 2026-10-09 · Binds [Selfkin Edge-to-Edge Communication v0.1](../../drafts/edge-to-edge-communication-v0.1.md) (SK-COM) · Data definitions: [wire-binding-v0.1.cddl](wire-binding-v0.1.cddl) · Test vectors: [test-vectors/wire](../../test-vectors/wire/) · Shared terms: [TERMINOLOGY.md](../../TERMINOLOGY.md) · Threats: [THREAT-MODEL.md](../../THREAT-MODEL.md)

**Purpose.** SK-COM says what must be true (signed envelopes, end-to-end encryption, mutual authentication, consented pairing, downgrade protection). SK-WIRE says how two runtimes do it on today's networks, so that two independent implementations interoperate: a phone behind carrier-grade NAT, a Linux VPS, and devices on a home LAN. It reuses the SK-COM envelope (§A5), its signing input (§A5.1), the algorithm table (§B8), capability tokens (§A6), `max_clock_skew` (§A5), `idem_key` and `seq` (§A9), and the registries. It adds no new cryptographic primitive; where it defines its own messages (pairing proof, mailbox control), section 11 explains why no existing protocol fits.

## Conventions

- The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in BCP 14 ([RFC 2119](https://www.rfc-editor.org/rfc/rfc2119), [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)) when, and only when, they appear in all capitals, as shown here.
- **Profile tags.** Each normative rule starts with a tag such as **[C1]**, **[C2]**, or **[C3]**: the lowest communication profile (SK-COM Part C) at which the rule applies, for an implementation that claims SK-WIRE. Below its tag, a rule is RECOMMENDED unless it says otherwise. Statements without a tag are non-normative.
- Each rule ends with a one-line *rationale*.
- Data structures are defined in CDDL ([RFC 8610](https://www.rfc-editor.org/rfc/rfc8610)) in [wire-binding-v0.1.cddl](wire-binding-v0.1.cddl). Rule names in `code` refer to that file.
- "Envelope" means a Selfkin Envelope (SK-COM §A5) in the JSON data model, encoded with `dcbor` (SK-COM §A5.1). Everything outside an envelope (frames, sealed boxes, chunks, control messages, the QR payload) is deterministic CBOR ([RFC 8949](https://www.rfc-editor.org/rfc/rfc8949) section 4.2.1) and may use byte strings.
- **Identifiers are provisional.** The ALPN identifier, service names, WebSocket subprotocol, well-known URI, media types, and QR prefix in this document are provisional and will be registered at v1.0 (section 9). Implementations **MUST** be ready for them to change before v1.0.
- Library and product names appear only in non-normative notes and are listed alphabetically; naming one is not an endorsement.

---

## 1. Overview

| Concern | SK-WIRE default | Fallback or alternative | Section |
|---|---|---|---|
| Transport | QUIC v1 with TLS 1.3, ALPN `selfkin/1`, UDP 443 | WebSocket over TLS 1.3 on TCP 443, subprotocol `selfkin.1` | 3 |
| Server authentication | Pinned TLS key (SPKI SHA-256), no CA | Raw public keys (RFC 7250), MAY | 3.4 |
| Client authentication | Signed `sk.negotiate` challenge and response inside the TLS channel | TLS client certificates, MAY | 6.1 |
| LAN discovery | DNS-SD over mDNS, `_selfkin._udp` and `_selfkin._tcp`, rotating instance names | QR only | 4.1 |
| Internet reachability | Owner's own runtime with a public address as rendezvous, relay (F9), and mailbox (F8); devices dial out | Direct device-to-device paths deferred to v0.2 | 4.2 |
| Pairing | QR code with key pin, one-time secret, and 300 s expiry; HMAC proof; SAS and consent on both sides | SAS-only pairing for devices without a camera, deferred | 4.3 |
| Wire format | One CBOR frame per QUIC stream or WebSocket message | none | 3.3 |
| Messages | `handoff.request`, `handoff.result`, `messaging.send`, `share.deliver`, `share.fetch`, `share.offer`, `sk.ack` | none | 5 |
| E2E, direct | TLS 1.3 between the two runtimes (ephemeral key exchange, forward secrecy); hybrid post-quantum group when available | none | 6.2 |
| E2E, relayed or stored | HPKE ([RFC 9180](https://www.rfc-editor.org/rfc/rfc9180)) to a signed one-time prekey, or to a signed last-resort prekey when none is left; sign then encrypt | MLS for the owner's devices in v0.2 | 6.3 |
| Mailbox | Owner-run mailbox host with a small control protocol | none | 6.4 |
| At rest | Per-object content keys, AES-256-GCM chunks, content-addressed by ciphertext hash | none | 5.2, 6.5 |
| Replay | `nonce`, `issued`/`expires`, `seq`, `idem_key`, `max_clock_skew` as in SK-COM | none | 6.6 |
| Post-quantum | Hybrid TLS group X25519MLKEM768 SHOULD; hybrid HPKE suite MLKEM768-X25519 preferred (provisional code point); X25519 suite always interoperates | C3: both REQUIRED | 6.2, 6.3 |
| Weak devices | Level `core`: WebSocket, text, thumbnails, acks | Bridges (Method 4) | 7 |

## 2. Identities and Keys

SK-WIRE uses the identity model of SK-COM §A2 and SK-RT §10. It fixes the key types and how peers learn them.

| Key | Purpose | Algorithm | Where it lives | Lifetime |
|---|---|---|---|---|
| Owner key | Signs device and agent statements (§A2) | `Ed25519` or `ES256` | Separate device or hardware token SHOULD (SK-RT §10) | Long; rotatable |
| Device key | Device identity; signs transport-key statements and prekeys | `Ed25519` (TEE) or `ES256` (StrongBox or another secure element) | Hardware keystore | Long; rotatable |
| Agent key | Signs envelopes (`sig`), proof of possession for tokens (`cnf.jkt`) | `Ed25519` | Issued by the Core, bound to the device; hardware keystore SHOULD | Medium; rotatable |
| Transport key | TLS 1.3 certificate or raw public key | `Ed25519` or ECDSA P-256 | Software keystore of the runtime | At most 30 days |
| One-time prekey | HPKE recipient key for one sealed delivery | X25519, or MLKEM768-X25519 | Software keystore; private key deleted after first use | Until used, at most 7 days |
| Last-resort prekey | HPKE recipient key when no one-time prekey is left | X25519, or MLKEM768-X25519 | Software keystore | At most 7 days |

- **[C1]** Device, agent, and owner identities **MUST** be `did:key` identifiers ([did:key method](https://w3c-ccg.github.io/did-key-spec/), a W3C CCG draft) for `Ed25519` and P-256 keys, and `kid` **MUST** be the DID followed by `#` and its multibase value. *Rationale: self-certifying identifiers need no resolver, registry, or network, which suits pairing on a LAN or behind NAT.*
- **[C1]** Receivers **MUST** verify both `Ed25519` and `ES256` signatures, as SK-COM §A5.1 and §B8 require once amended (section 10). Senders **MUST** sign envelopes with `Ed25519` agent keys and **MAY** use `ES256` for device and owner keys that live in hardware that cannot hold Ed25519 keys. *Rationale: on Android, StrongBox does not support Curve25519 while the TEE does from KeyMint v2 (Android 13), so a hardware-backed key may be P-256 only ([AOSP KeyMint HAL](https://android.googlesource.com/platform/hardware/interfaces/%2B/a742007dfaf46b6e23022ff1ff92c0983b2c2b98/security/keymint/aidl/android/hardware/security/keymint/IKeyMintDevice.aidl), [AOSP Keystore](https://source.android.com/docs/security/features/keystore)).*
- **[C1]** The device key **MUST** sign a statement that binds the current transport key (SHA-256 of its SubjectPublicKeyInfo), and **MUST** sign every prekey (`prekey` in the CDDL, signed with the SK-COM §A5.1 signing input). *Rationale: TLS and HPKE keys rotate often and live in software, while trust stays anchored in the hardware-backed device key; a mailbox host cannot substitute a prekey it does not hold the device key for.*
- **[C3]** Agent keys **MUST** be hardware-backed (SK-COM §A2), and `attestation_ref` **MUST** reference a key attestation of the device key. *Rationale: unchanged from SK-COM; SK-WIRE only names the key.*

## 3. Transport

### 3.1 Carriers

- **[C1]** An SK-WIRE implementation at level `full` **MUST** implement carrier Q: QUIC version 1 ([RFC 9000](https://www.rfc-editor.org/rfc/rfc9000)) secured with TLS 1.3 ([RFC 9001](https://www.rfc-editor.org/rfc/rfc9001), [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446)), with the ALPN ([RFC 7301](https://www.rfc-editor.org/rfc/rfc7301)) protocol identifier `selfkin/1`. *Rationale: QUIC gives stream multiplexing without head-of-line blocking, connection migration when a phone moves between Wi-Fi and mobile data, and a 1-RTT handshake on UDP.*
- **[C1]** Every SK-WIRE implementation, at any level, **MUST** implement carrier W: WebSocket ([RFC 6455](https://www.rfc-editor.org/rfc/rfc6455)) over TLS 1.3 on TCP, at the path `/.well-known/selfkin/1`, with the subprotocol `selfkin.1`. *Rationale: UDP is blocked or throttled on some networks, and WebSocket over HTTPS passes most firewalls and HTTP proxies; it is also available on every platform, including weak devices.*
- **[C1]** A client that supports both carriers **SHOULD** start Q first and W after 250 ms if Q has not completed its handshake, in the style of Happy Eyeballs ([RFC 8305](https://www.rfc-editor.org/rfc/rfc8305)), and **MUST** use the first that completes the SK-WIRE handshake (section 6.1). *Rationale: fast fallback without waiting for a UDP timeout.*
- **[C1]** Neither carrier **MAY** use TLS versions below 1.3 or TLS 0-RTT early data. *Rationale: forward secrecy and replay resistance for the first flight (SK-COM §A4); 0-RTT data is replayable.*
- **[C1]** Every path, including peer-to-peer and LAN paths, uses TLS 1.3 as above. The Noise Protocol Framework, which SK-COM §A4 allows as MAY once amended, is not used by SK-WIRE v0.1. *Rationale: one handshake on every path means one library to keep current and one set of rules to review.*
- HTTP/3 ([RFC 9114](https://www.rfc-editor.org/rfc/rfc9114)), WebSockets over HTTP/2 or HTTP/3 ([RFC 8441](https://www.rfc-editor.org/rfc/rfc8441), [RFC 9220](https://www.rfc-editor.org/rfc/rfc9220)), QUIC multipath ([draft-ietf-quic-multipath-21](https://datatracker.ietf.org/doc/draft-ietf-quic-multipath/), work in progress), and QUIC NAT traversal ([draft-seemann-quic-nat-traversal-03](https://www.ietf.org/archive/id/draft-seemann-quic-nat-traversal-03.html), work in progress) are candidate later carriers or extensions; SK-WIRE v0.1 does not define them.

### 3.2 Ports and Port 443

- **[C1]** On the Internet, a runtime **SHOULD** listen on port 443, UDP for Q and TCP for W. On a LAN, a runtime **MAY** use any port and **MUST** advertise it (section 4.1). Other Internet ports **MAY** be used and are carried in the QR payload (`endpoint`). *Rationale: 443 is the port most likely to pass NAT, carrier, and corporate firewalls.*
- **[C1]** TLS **MUST** terminate in the runtime itself or in a process on the same host that the same owner controls; a host that already serves HTTPS on 443 **SHOULD** route by ALPN or SNI without terminating TLS (TLS passthrough). *Rationale: the pinned TLS key must belong to the owner's runtime; a third-party TLS terminator would see all traffic.*
- *Note (non-normative): TLS passthrough is available in common open source proxies, for example [HAProxy](https://docs.haproxy.org/) and [nginx `ssl_preread`](https://nginx.org/en/docs/stream/ngx_stream_ssl_preread_module.html). If a web server already holds UDP 443 for HTTP/3, carrier Q needs another UDP port or an ALPN-aware UDP router; this is a deployment limit, not a protocol change.*

### 3.3 Framing

- **[C1]** On carrier Q, each `wire-frame` **MUST** be sent on its own unidirectional QUIC stream, and the stream **MUST** end after the frame. On carrier W, each `wire-frame` **MUST** be one binary WebSocket message; text messages **MUST** cause the connection to close with status 1003. *Rationale: the transport delimits frames, so there is no length prefix to get wrong.*
- **[C1]** A frame is one of `envelope-frame` (type 1, a signed envelope), `sealed-frame` (type 2, an HPKE sealed box, section 6.3), `chunk-frame` (type 3, an encrypted chunk, section 5.2), or `control-frame` (type 4, a mailbox control message, section 6.4). Receivers **MUST** refuse an unknown frame type with `malformed` and **MUST NOT** accept a frame larger than the negotiated `max_frame` (default 1048576 bytes). *Rationale: a closed set of frame types and a hard size limit.*
- **[C1]** Receivers **MUST** process envelopes of one session in `seq` order and **MAY** buffer up to 64 out-of-order envelopes per session; beyond that they **MUST** refuse with `out-of-sequence` (SK-COM §A5). *Rationale: QUIC streams are independent, so order is restored from `seq`.*
- Chunk and control frames are not envelopes. Chunks carry no signature because the signed manifest (section 5.2) lists their SHA-256 values; this follows the F7 pattern of SK-COM §A4 (a signed envelope, then authenticated frames). Control frames are protected by the authenticated session in which they are sent (section 6.4).

### 3.4 Connection Rules

- **[C1]** The server's TLS key **MUST** be verified only by comparing the SHA-256 of its SubjectPublicKeyInfo with the value pinned at pairing (section 4.3) or from a current transport-key statement (section 2). The server **MUST** present either a self-signed certificate or, when both sides support it, a raw public key ([RFC 7250](https://www.rfc-editor.org/rfc/rfc7250)). WebPKI validation **MUST NOT** be required and **MUST NOT** replace the pin. *Rationale: no CA, no domain name, and no paid certificate are needed, and a CA cannot impersonate the runtime; a raw public key is the same pin without certificate parsing.*
- **[C1]** QUIC idle timeout **SHOULD** be 30 seconds, and clients **SHOULD** send PING frames (QUIC) or WebSocket pings every 15 seconds while the app is in the foreground. *Rationale: keeps NAT bindings alive on mobile networks without draining the battery in the background.*
- **[C1]** A device in the background **SHOULD** close its connection and rely on a content-free wake-up (section 4.2) and the mailbox (section 6.4). *Rationale: mobile operating systems restrict background sockets.*

## 4. Discovery and Pairing

### 4.1 LAN Discovery (F5)

This section proposes an answer to SK-COM §D Q6 and [issue #5](https://github.com/selfkin/standards/issues/5) for mDNS.

- **[C1]** Runtimes **MAY** advertise on a LAN with DNS-SD ([RFC 6763](https://www.rfc-editor.org/rfc/rfc6763)) over mDNS ([RFC 6762](https://www.rfc-editor.org/rfc/rfc6762)) using the service types `_selfkin._udp` (carrier Q) and `_selfkin._tcp` (carrier W). *Rationale: available on common desktop and mobile systems without extra infrastructure.*
- **[C1]** The service instance name **MUST** be 16 lowercase hexadecimal characters: the first 8 bytes of HMAC-SHA256(`adv_key`, "selfkin/1 adv" followed by the 8-byte big-endian value of floor(Unix time / 900)). `adv_key` is a 32-byte secret exchanged at pairing. Paired peers **MUST** accept the current and the previous window. *Rationale: paired devices recognise each other, while others see a name that changes every 15 minutes and cannot be linked.*
- **[C1]** The TXT record **MUST** contain only `v=1`. The advertisement **MUST NOT** contain owner names, device models, agent lists, capabilities, or key fingerprints, and the mDNS host name **SHOULD** be a random label that rotates with the instance name. *Rationale: SK-COM §A3 requires minimal advertisements; device names such as "Alice's phone" leak identity.*
- **[C1]** A device in pairing mode **MAY** advertise the instance name `pair-` followed by 8 random hexadecimal characters for at most 300 seconds, and only while the owner has the pairing screen open. *Rationale: unpaired devices need a findable name, but only briefly and with consent.*

### 4.2 Internet Reachability

Phones are usually behind carrier-grade NAT and cannot accept inbound connections. SK-WIRE v0.1 uses the owner's own runtime with a public address (in the demo, a VPS) as rendezvous, relay, and mailbox.

- **[C1]** A device that cannot accept inbound connections **MUST** connect outbound to a paired runtime that has a public address. *Rationale: outbound connections to 443 work behind every common NAT, including carrier-grade NAT, without hole punching.*
- **[C1]** That runtime **MAY** act as relay (F9) and mailbox host (F8) for the owner's other devices. When it forwards for another device, it **MUST** forward only `sealed-frame` and `chunk-frame` values, never plaintext envelopes, and it **MUST** drop a sealed box after its `exp` (SK-COM §A9). *Rationale: the relay is infrastructure and must not read payloads (SK-COM §A4), even when the owner runs it.*
- **[C1]** Wake-ups for sleeping devices **MUST NOT** carry payload or metadata beyond "check your mailbox". *Rationale: no dependency on what a push service learns, because there is nothing to learn.*
- *Note (non-normative): a self-hosted [UnifiedPush](https://unifiedpush.org/) distributor (for example [ntfy](https://github.com/binwiederhier/ntfy), Apache-2.0) avoids a dependency on a platform push service; where only a platform push service can wake an app, the content-free rule still applies.*
- **[C1]** SK-WIRE v0.1 is relay-only: traffic between two devices that are not the TLS peers of each other (for example phone to phone, or phone to a home device) **MUST** go through the relay as sealed frames. *Rationale: one path that works behind every NAT; direct paths need NAT traversal that v0.1 does not specify.*
- *Note (non-normative): direct device-to-device paths across NATs are planned for v0.2 as an optional carrier specified by the IETF QUIC NAT traversal and multipath documents (an alternative to ICE, [RFC 8445](https://www.rfc-editor.org/rfc/rfc8445)). An implementation of that carrier could then use an existing library, for example [Iroh](https://github.com/n0-computer/iroh) (MIT OR Apache-2.0), provided the device key signs the library's endpoint key.*

### 4.3 QR Pairing

Pairing follows SK-COM §A3: explicit consent on both sides for F1, out-of-band verification, `sk.pairing.*` intents, no `instructions`, no `cap_token`.

1. **Display.** The presenter (for example the VPS, printing to the owner's SSH terminal, or a laptop screen) generates a 16-byte one-time secret and shows a QR code with `qr-payload`: its device DID, the SHA-256 of its TLS SubjectPublicKeyInfo, its endpoints, the secret, and an expiry at most 300 seconds ahead. The content is `SK1:` followed by base45 ([RFC 9285](https://www.rfc-editor.org/rfc/rfc9285)) of the CBOR bytes, so the QR code can use alphanumeric mode. The payload in test vector `wire.qr.001` is 243 characters.
2. **Connect.** The scanner connects to an endpoint and pins the TLS key from the QR code (section 3.4). This authenticates the presenter.
3. **Request.** The scanner sends `sk.pairing.request` with `proof` = HMAC-SHA256(secret, "selfkin/1 pairing request" || presenter DID || 0x00 || scanner device DID || presenter SPKI hash), its owner-signed statements, its transport SPKI hash, its last-resort prekey, and the forms it asks for. This proves the scanner saw the QR code.
4. **Consent.** The presenter checks the proof, the expiry, and that the secret is unused, and asks its owner to confirm, showing the requested forms and capabilities and a 6-digit code: the first 20 bits of HMAC-SHA256(secret, "selfkin/1 sas" || SHA-256 of the dcbor request envelope), as a decimal number modulo 1000000. The scanner shows the same code.
5. **Response.** After consent, the presenter sends `sk.pairing.response` with its statements, last-resort prekey, `adv_key`, the rights it grants, `record_expires`, and `proof` computed as in step 3 with the label "selfkin/1 pairing response".
6. **Confirm.** The scanner's owner confirms; the scanner sends `sk.pairing.confirm`. Either side may send `sk.pairing.reject` instead.

Presenter states:

| State | Event | Next state |
|---|---|---|
| `shown` | valid request (proof, expiry, unused secret) | `awaiting-consent` |
| `shown` | invalid proof (third failure) or expiry | `closed` (secret discarded) |
| `awaiting-consent` | owner confirms; send response | `awaiting-confirm` |
| `awaiting-consent` | owner declines; send reject | `closed` |
| `awaiting-confirm` | `sk.pairing.confirm` | `paired` (record stored, secret discarded) |
| `awaiting-confirm` | `sk.pairing.reject` or 300 s timeout | `closed` |

The scanner mirrors this: `scanned`, then `awaiting-response` after sending the request, then `awaiting-owner` after a valid response, then `paired` after sending the confirm.

- **[C1]** The one-time secret **MUST** be used for at most one successful pairing, **MUST** be discarded after its expiry or after 3 failed proofs, and **MUST NOT** be logged. *Rationale: a photographed or leaked code must be useless after use or expiry, and guessing is capped.*
- **[C1]** Each side **MUST** store a pairing record with the peer's identities, pinned transport key, last-resort prekey, allowed forms, allowed rights, and `record_expires`. The default `record_expires` **SHOULD** be 365 days for F1 and 30 days for F2. *Rationale: SK-COM §A3 requires records that state forms and capabilities and expire unless renewed.*
- **[C1]** A device without a camera **MAY** pair by showing the 6-digit code on both screens and asking the owner to compare them. In that case the secret is replaced by an ephemeral X25519 exchange inside the pinned TLS channel. *Rationale: SAS is a permitted out-of-band method in SK-COM §A3.* (The exact SAS-only exchange is left to a later revision.)

## 5. Message Types

All messages are envelopes with registered intents ([registries/intents.md](https://github.com/selfkin/standards/blob/main/registries/intents.md)) and the payload types below. `data` stays untrusted (SK-COM §A5): nothing in it grants authority. Payload media types use the provisional `vnd.selfkin.wire` prefix, following the existing `application/vnd.selfkin.refusal+json`.

| Message | `intent` | `payload_type` | `instructions` | CDDL |
|---|---|---|---|---|
| Text | `messaging.send` | `application/vnd.selfkin.wire.text+json` | none | `text-env` |
| Photo offer | `share.offer` | `application/vnd.selfkin.wire.photo-offer+json` | none | `offer-env` |
| Fetch (view on demand) | `share.fetch` | none | `share.fetch` | `fetch-env` |
| Deliver | `share.deliver` | `application/vnd.selfkin.wire.deliver+json` | none | `deliver-env` |
| Handoff request | `handoff.request` | `application/vnd.selfkin.wire.handoff-inputs+json` | `handoff.run` | `handoff-req-env` |
| Handoff result | `handoff.result` | `application/vnd.selfkin.wire.handoff-result+json` | none | `handoff-res-env` |
| Ack or receipt | `sk.ack` | `application/vnd.selfkin.wire.ack+json` | none | `ack-env` |
| Negotiation | `sk.negotiate` | `application/vnd.selfkin.wire.negotiate+json` | none | `negotiate-env` |
| Pairing | `sk.pairing.*` | `application/vnd.selfkin.wire.pairing+json` | none | `pairing-env` |

Messages refer to each other with `env-ref`: the `session`, `seq`, and SHA-256 of the complete dcbor encoding (including `sig`) of the referenced envelope.

- **[C1]** Resources in capability rights and `instructions` **MUST** be RFC 6920 names `ni:///sha-256;...` ([RFC 6920](https://www.rfc-editor.org/rfc/rfc6920)) for objects, or the `did:key` of the receiving agent for actions that the agent itself performs (`handoff.run`). A right for objects **MAY** use `ni:///*`, which covers every `ni` name (SK-COM §A6); the holder **MUST** still serve only objects it offered to that peer. *Rationale: content names are self-verifying and need no namespace registration; an agent DID already names the party that acts.*

### 5.1 Text

- **[C1]** A text message **MUST** carry 1 to 16384 bytes of UTF-8 text in Unicode Normalization Form C (SK-COM §A5.1), an optional BCP 47 `lang`, an optional `reply_to`, and an optional `thread`. It **SHOULD** carry `idem_key` so that a retried send is shown once. *Rationale: a small, fixed shape that every level can render.*

### 5.2 Photo Send: Chunked, Content-Addressed, Encrypted at Rest

- **[C1]** A photo is offered with `share.offer` whose `data` is a manifest (`photo-offer`): the `ni` name of the original plaintext, and one or more renditions (`original`, `preview`, `thumb`). *Rationale: one signed manifest describes every byte that will follow.*
- **[C1]** Each rendition **MUST** be encrypted with its own random 32-byte content key, in chunks of 262144 plaintext bytes (the last may be shorter), with AES-256-GCM, a 12-byte nonce equal to the chunk index (big-endian), and associated data "selfkin/1 chunk" || index (8 bytes) || chunk count (8 bytes). *Rationale: each key encrypts one rendition once, so index nonces never repeat; the associated data stops reordering and truncation.*
- **[C1]** Each chunk is addressed by `chunk-id` = SHA-256 of its ciphertext, and the manifest lists the chunk ids in order and the SHA-256 of the whole plaintext. Receivers **MUST** check every chunk id before decryption and the plaintext digest after. *Rationale: content addressing lets transfers resume and relays and stores hold chunks without being able to read or link them; hashing ciphertext, not plaintext, avoids confirming that two people hold the same photo.*
- **[C1]** Chunks and content keys **MUST** stay encrypted at rest: chunks are stored as received, and content keys are stored only under a key held by the device keystore. Deleting the content key **MUST** be treated as deleting the photo. *Rationale: encryption at rest without re-encrypting, and deletion that works on every copy (crypto-shredding).*
- **[C1]** The manifest **MAY** carry `thumb_inline` (at most 16384 bytes before base64url encoding). If `push` is true, the sender sends the `original` chunks right after the offer; otherwise the receiver fetches what it needs (section 5.3). *Rationale: a phone on mobile data sees the thumbnail at once and pays for the full photo only when the owner opens it.*
- **[C1]** The `key` member is a secret: logs (SK-COM §A10) **MUST** redact it, and residency and data-class rules apply to the manifest as to the photo (`media.photo`). *Rationale: the manifest unlocks the photo.*
- **[C1]** A manifest **MUST NOT** list more than 4096 chunks per rendition (1 GiB). *Rationale: bounded memory; video is out of scope for v0.1.*

### 5.3 View or Thumbnail on Demand

- **[C1]** A receiver requests a rendition with `share.fetch`: `instructions.action` is `share.fetch`, `resource` is the object name, `params.kind` is the rendition, and optional `params.chunks` lists the chunk indices it still needs. The request **MUST** carry `idem_key` and a `cap_token` with a right for `share.fetch` (SK-COM §A6). *Rationale: fetching is an action on the holder's data, so it needs a capability like any other.*
- **[C1]** The holder answers with `share.deliver` (listing the chunk indices that follow) and then the chunk frames, or with `inline` content when the rendition is at most 16384 bytes, or with `sk.refused`. *Rationale: one signed answer, then unsigned but content-addressed chunks.*
- **[C1]** A holder **MAY** create missing renditions (for example a `preview`) on request, or hand that work to a stronger device (section 5.4). *Rationale: weak devices ask for small renditions.*

### 5.4 Task Handoff to a Stronger Device (F6)

- **[C1]** A handoff request is `handoff.request` with form `F6`, `instructions.action` `handoff.run`, `instructions.resource` the receiving agent's DID, `params.task` (a short task name such as `audio.transcribe` or `photo.describe`), `params.deadline`, optional `priority`, `result_to`, and `max_model_class`, an `idem_key`, and a `cap_token` with a right for `handoff.run` on that agent. Inputs go in `data` as untrusted text (`prompt`) and references to offered objects (`inputs`). *Rationale: the action and its limits are structured and signed, while user content stays in `data` (SK-COM §A5).*
- **[C1]** `max_model_class` **MUST** be honoured: `local` means the receiving runtime **MUST NOT** call a remote provider; `remote-p2` and `remote-p3` allow providers of at least that SK-PRV profile. Residency tags on the request apply to every input and output. *Rationale: handing work to the VPS must not silently send data to a third party.*
- **[C1]** The receiver **SHOULD** send `sk.ack` with status `processing`, and **MUST** finish with `handoff.result` (`done`, `failed`, `cancelled`, or `partial`), carrying `model_ref` when a model produced content (SK-COM §A5, §A10). Below C2, handoff **MUST NOT** cross owners (SK-COM §A6). *Rationale: the requester always learns the outcome and which model produced it.*

### 5.5 Acks and Receipts

- **[C1]** A receiver **MUST** answer every envelope that carries `idem_key` with `sk.ack` or `sk.refused`. Status values are `received` (verified and queued), `stored` (persisted), `processing`, `done`, `failed` (with a refusal reason code), and `read`. *Rationale: the sender needs to know when it may stop retrying.*
- **[C1]** `read` receipts **MUST** be off by default and enabled per peer by the owner. *Rationale: read receipts reveal behaviour (`usage` data class).*
- **[C1]** An ack for a photo **MAY** carry `have` (chunk indices held) so that the sender resumes an interrupted transfer. A sender **MUST** retry an unacknowledged envelope with the same `idem_key` and a new `nonce`, `seq`, `issued`, and `expires`. *Rationale: retries are new envelopes (fresh replay fields) that receivers still execute at most once (SK-COM §A9).*

## 6. Security

### 6.1 Mutual Authentication and Session Setup

Some common TLS stacks make TLS client authentication and keying-material exporters awkward. SK-WIRE therefore authenticates the server with the pinned TLS key and the client with a signed challenge inside the channel.

- **[C1]** The first three envelopes on every connection **MUST** be `sk.negotiate` with `phase` `offer` (client), `select` (server), and `confirm` (client). The offer carries a fresh `challenge`; the select **MUST** echo it in `echo`, carry its own `challenge`, and carry `transcript` = SHA-256 of the dcbor offer envelope; the confirm **MUST** echo the server challenge and carry `transcript` = SHA-256 of the dcbor offer followed by the dcbor select. Each side **MUST** verify the other's signature, `aud`, freshness, and echo before accepting any other envelope or any control frame. *Rationale: a signed, challenge-bound transcript gives mutual authentication and satisfies SK-COM §B7.*
- **[C1]** `sk.negotiate` envelopes **MUST NOT** carry `instructions` and **MAY** omit `cap_token`, as SK-COM §B7 allows once amended (section 10); the offer always omits it, because no token exists before the session. *Rationale: like pairing, negotiation requests no action, and it runs before any capability is granted.*
- **[C1]** When both TLS stacks expose it, the offer and select **MUST** carry `cb`, the `tls-exporter` channel binding of [RFC 9266](https://www.rfc-editor.org/rfc/rfc9266), and the receiver **MUST** check it. **[C3]** `cb` is REQUIRED. *Rationale: without `cb`, binding to the channel rests on the pinned server key; `cb` binds the transcript to the session keys directly, which C3 should not do without.*
- **[C1]** The select and confirm **MUST** carry the capability token (`token`) that the sender grants its peer for this session, with `sub` = the peer's agent, `aud` = the sender's agent, `cnf.jkt` = the RFC 7638 thumbprint ([RFC 7638](https://www.rfc-editor.org/rfc/rfc7638)) of the peer's agent key, and rights within the pairing record. Before a token expires, the issuer **SHOULD** send a fresh one with `phase` `grant`. *Rationale: SK-COM §A6 limits tokens to 1 hour, so a long session needs in-band renewal; signing each envelope with the agent key is the proof of possession.*

*Open issue (non-normative): revisit TLS client authentication (client certificates per RFC 8446, or raw public keys per RFC 7250) to replace the in-channel challenge once the TLS libraries used by implementations support server-side client authentication and a keying-material exporter.*

Session states (each side):

| State | Event | Next state |
|---|---|---|
| `tls-up` | client sends offer / server receives valid offer | `offered` |
| `offered` | client receives valid select (echo, transcript, signature, `aud`) and sends confirm | `open` |
| `offered` | server sends select, then receives valid confirm | `open` |
| any before `open` | any other envelope, any control frame, invalid echo or transcript, or 10 s without progress | `closed` (with `sk.refused` where possible) |
| `open` | token about to expire; issuer sends `grant` | `open` |

### 6.2 End-to-End Encryption, Direct

- **[C1]** When the two communicating runtimes are the TLS endpoints, the TLS 1.3 channel provides the end-to-end encryption required by SK-COM §A4, and SK-WIRE adds no second layer. TLS key exchange **MUST** use an ephemeral key exchange. *Rationale: TLS 1.3 already gives confidentiality, integrity, and forward secrecy between the two runtimes.*
- **[C1]** Implementations **SHOULD** offer and prefer the hybrid group X25519MLKEM768 ([RFC 10024](https://www.rfc-editor.org/rfc/rfc10024)) when their TLS stack supports it. **[C3]** The TLS key exchange **MUST** use a hybrid post-quantum group (SK-COM §A4, §D Q2). *Rationale: recorded traffic can be decrypted later by a quantum computer, and the hybrid group costs about one kilobyte per handshake.*

### 6.3 End-to-End Encryption, Relayed or Stored (Sealed Frames)

This section proposes the envelope encryption layering asked for in [issue #32](https://github.com/selfkin/standards/issues/32). It follows the one-time prekey plus signed last-resort prekey pattern of [X3DH](https://signal.org/docs/specifications/x3dh/) and [PQXDH](https://signal.org/docs/specifications/pqxdh/), reduced to a single message per key (no ratchet).

- **[C1]** An envelope for a device that is not the TLS peer **MUST** be sent as a `sealed-frame`: sign first, then seal the complete `envelope-frame` bytes with HPKE single-shot base mode to a prekey of the recipient device, with `info` = "selfkin/1 sealed" || `rk`. The outer `sealed-box` exposes only the suite, an opaque 16-byte mailbox handle `to`, the prekey hash `rk`, and `exp`. *Rationale: relays and mailboxes see routing data only, never the sender, intent, residency, or instructions, and the inner signature still proves the sender.*
- **[C1]** Each device at level `full` **MUST** publish to each mailbox host it uses (section 6.4) a signed last-resort prekey for every HPKE suite it supports, and **MUST** keep a pool of at least 20 signed one-time prekeys published, replenishing it whenever it falls below 20. A sender **MUST** seal to a one-time prekey when it can obtain one, and **MAY** use the last-resort prekey only when none is available. *Rationale: a one-time key is used once and then deleted, so a later compromise of the recipient cannot open that message (forward secrecy); the last-resort key keeps delivery working when the stock runs out.*
- **[C1]** The recipient **MUST** delete the private key of a one-time prekey as soon as it has opened the sealed box addressed to it, and **MUST** refuse a second sealed box for the same one-time prekey. It **MUST** delete a last-resort private key once every sealed box addressed to it has expired, and **MUST** rotate the last-resort prekey at least every 7 days. *Rationale: deletion is what turns a one-time key into forward secrecy; for the last-resort key, rotation bounds the exposure window to 7 days, as SK-COM §A4 requires forward secrecy.*
- **[C1]** Before sealing, the sender **MUST** verify the prekey's signature against the recipient's device key from the pairing record, its `use`, its `not_after`, and that `device` is the intended recipient. *Rationale: the mailbox host hands out prekeys and must not be able to substitute its own.*
- **[C1]** Implementations at level `full` **MUST** support the HPKE suite DHKEM(X25519, HKDF-SHA256), HKDF-SHA256, ChaCha20Poly1305 (`[32, 1, 3]`, [RFC 9180](https://www.rfc-editor.org/rfc/rfc9180) section 7), and **SHOULD** support and prefer MLKEM768-X25519, HKDF-SHA256, ChaCha20Poly1305 (`[25722, 1, 3]`, from [draft-ietf-hpke-pq-05](https://datatracker.ietf.org/doc/draft-ietf-hpke-pq/), work in progress). The KEM identifier 25722 (0x647a) is **provisional** until draft-ietf-hpke-pq is published as an RFC or its entry in the IANA HPKE KEM registry is final; an implementation **MUST** be ready to change it. *Rationale: stored ciphertext is the easiest target for "record now, decrypt later", but a draft code point can still change.*
- **[C1]** The classical suite `[32, 1, 3]` **MUST** always interoperate: a device that publishes hybrid prekeys **MUST** also keep an X25519 last-resort prekey published and **MUST** accept sealed frames in suite `[32, 1, 3]`, and a sender that does not support the hybrid suite **MUST** seal with `[32, 1, 3]`. **[C3]** Senders and recipients **MUST** use a hybrid suite. *Rationale: hybrid HPKE is not yet in every library, and a peer without it must never be unable to deliver.*
- **[C1]** In a `claim`, the sender lists the suites it supports in order of preference (`suites`). The mailbox host **MUST** return a one-time prekey in the first listed suite for which it holds one; if it holds no one-time prekey in any listed suite, it **MUST** return the last-resort prekey in the first listed suite for which it holds one, and otherwise answer `error` `unsupported`. *Rationale: forward secrecy from a one-time key comes before the suite preference, and the order is fixed so that hosts behave alike.*
- **[C1]** Mailbox handles **SHOULD** be rotated when the last-resort prekey rotates. *Rationale: a stable handle lets the relay link deliveries over time.*
- **[C1]** When a message goes to several devices of one owner, the sender **MUST** seal a separate copy to a prekey of each device. *Rationale: one key per device keeps device removal simple (revoke its statements and stop sealing to it).*
- **[C2]** Groups of two or more devices that share a conversation or mesh state **SHOULD** use MLS ([RFC 9420](https://www.rfc-editor.org/rfc/rfc9420)) once SK-WIRE defines its binding, planned for v0.2. *Rationale: MLS gives forward secrecy and post-compromise security for groups and handles device removal, which SK-RT §10 requires after revocation; per-device sealing gives forward secrecy only per one-time key and no post-compromise security.*

### 6.4 Mailbox Host and Control Protocol

A mailbox host is a runtime of the same owner, with a public address, that stores sealed frames for the owner's devices and hands out their prekeys. Control messages (`control` in the CDDL) are sent in `control-frame` values inside a session in state `open` (section 6.1). Each request carries an `id` that the answer repeats.

| Request (device to host) | Answer (host to device) | Effect |
|---|---|---|
| `put-prekeys` (`handle`, `last_resort` list with at most one per suite, `one_time` list) | nothing on success, `error` on failure | Replaces the last-resort prekey of each listed suite; adds one-time prekeys; binds `handle` to the device |
| `claim` (`device`, `suites`) | `claim-result` with exactly one prekey and the device's current `handle` | Selects as in section 6.3; removes the returned one-time prekey from the store |
| a `sealed-frame` with `to` = a handle the host serves | `deposited` with `box` = SHA-256 of the sealed-frame bytes | Stores the box until `exp` |
| `fetch` (optional `max`, default 64) | the queued sealed frames, oldest first, then `fetch-end` with `count` and `more` | No deletion |
| `delete` (`boxes`) | nothing on success, `error` on failure | Deletes the listed boxes |

Box states at the host: `stored` (after `deposited`), `sent` (sent in answer to a `fetch`; still stored), `deleted` (after `delete`), and `expired` (after `exp`; deleted without delivery). One-time prekey states at the device: `published`, `claimed` (the host handed it out), `used` (a sealed box was opened; private key deleted), `expired`.

- **[C1]** A host **MUST** accept control messages only from devices of its own owner whose pairing record allows the `mailbox` feature, and **MUST** accept deposits only from paired devices of the same owner in v0.1. *Rationale: no open relay, and an F2 mailbox needs abuse controls that v0.1 does not define.*
- **[C1]** A host **MUST** hand out each one-time prekey at most once, **MUST NOT** hand out a prekey whose `not_after` has passed, and **MUST** answer `put-prekeys` from a device for another device with `error` `unauthorized`. *Rationale: reuse of a one-time key would remove the forward secrecy it exists for.*
- **[C1]** A device **MUST** delete a box from the host only after it has opened the box and either stored the envelope or refused it (SK-COM §A9). A host **MUST** delete every box at its `exp`, and **MUST NOT** keep a box longer than 7 days after its deposit. *Rationale: at-least-once delivery without letting the mailbox become an archive.*
- **[C1]** A sealed frame carries an F8 envelope whose `expires` is at most 7 days after `issued`; only `handoff.result`, `messaging.send`, `share.offer`, and `sk.ack` envelopes may use more than 600 seconds, and envelopes with `instructions` **MUST NOT** be queued for longer than 600 seconds. The receiver evaluates the token at `issued` and checks revocation at receipt (SK-COM §A9 as amended, section 10). *Rationale: messages must survive a phone being offline, but delayed commands are a risk; a stale command fails and the sender retries.*
- **[C1]** A host **SHOULD** send a content-free wake-up (section 4.2) when it stores a box for a device that is not connected. *Rationale: the device fetches when it wakes, so the push carries nothing.*

### 6.5 At Rest

- **[C1]** Photos and other objects follow section 5.2. Mailboxes **MUST** store sealed boxes as received. Local envelope logs **MUST** follow SK-COM §A10 and **MUST** redact content keys, prekey private keys, and pairing secrets. *Rationale: storage never holds more plaintext than the device that owns it needs.*

### 6.6 Replay Protection and Lifetimes

SK-WIRE adds no new replay fields. It fixes the values.

- **[C1]** Receivers **MUST** keep each accepted `nonce` per `sender_agent` until `expires` plus `max_clock_skew` (SK-COM §A5), and **MUST** refuse a repeated nonce with `replayed`. *Rationale: an envelope cannot be replayed within its validity, and after it the expiry check rejects it.*
- **[C1]** For live sessions, `expires` **SHOULD** be 300 seconds after `issued` and **MUST NOT** be more than 600 seconds after it. *Rationale: short validity for interactive traffic.*
- **[C1]** `idem_key` **MUST** be unique per sender for at least 7 days, and receivers **MUST** remember executed `idem_key` values for at least as long as they accept envelopes for that sender's session or mailbox. *Rationale: at-most-once execution over the longest delivery window.*

## 7. Negotiation and Backward Compatibility

### 7.1 Capability Negotiation and Versions

- **[C1]** The `sk.negotiate` offer **MUST** list `versions`, `canons`, `algs`, `hpke_suites`, `forms`, `profiles`, `level`, `features`, and `max_frame`; the select **MUST** pick one value for each single-valued item and the intersection for lists, preferring the highest profile both support and owner policy allows (SK-COM §B7). *Rationale: one negotiation that covers SK-COM and SK-WIRE parameters.*
- **[C1]** SK-WIRE itself is versioned by the ALPN identifier (`selfkin/1`), the WebSocket subprotocol (`selfkin.1`), and the QR prefix (`SK1:`). An incompatible revision **MUST** change all three; a compatible addition **MUST** be negotiated through `features`. *Rationale: a peer learns before any envelope whether it speaks the same binding.*
- **[C1]** Downgrade pinning of SK-COM §B7 **MUST** cover the carrier, the level, and the HPKE suite: a peer that once used level `full`, carrier Q, or a hybrid suite and now offers less **MUST** be shown to the owner before the session continues. *Rationale: an attacker who blocks UDP or strips an offer must not silently push a peer to a weaker path.* Falling back from Q to W is not a downgrade of security (both use TLS 1.3), so it needs no prompt; dropping a feature, level, or hybrid suite does.

### 7.2 Levels for Old or Weak Devices

| Level | Carriers | Features | Crypto | Typical device |
|---|---|---|---|---|
| `core` | W | `text`, `thumb`, acks, `share.fetch` for `thumb` and `preview`, pairing | `Ed25519` and `ES256` verify, TLS 1.3, no HPKE | Old phone, e-reader, watch, microcontroller with TLS |
| `full` | Q and W | everything in section 5, `sealed`, `relay`, `mailbox` | plus HPKE, AES-256-GCM chunks | Current phone, laptop, VPS |

- **[C1]** A `core` device **MUST** talk only directly over TLS with runtimes of its own owner (F1, F4) and **MUST NOT** be the recipient of sealed frames; its `full` peer **MUST** deliver to it only over the direct channel. *Rationale: without HPKE a relay could read its messages, so it gets none through relays.*
- Devices that cannot do TLS 1.3 at all are not SK-WIRE devices. They are legacy endpoints behind a proxy (section 7.3).

### 7.3 Bridges to Non-Selfkin Users

Email ([RFC 5322](https://www.rfc-editor.org/rfc/rfc5322)), [Matrix](https://spec.matrix.org/latest/), and XMPP ([RFC 6120](https://www.rfc-editor.org/rfc/rfc6120)) are bridged with the Proxy Method (SK-COM §B5).

- **[C1]** A bridge **MUST** run inside a runtime the owner controls and **MUST** wrap every inbound message as an envelope whose `provenance` lists the bridge with role `proxy` and method `proxy`, and the remote user with role `legacy-endpoint`, an identifier in that system's URI form (`mailto:`, `matrix:u/...` from the Matrix specification appendices, `xmpp:` per [RFC 5122](https://www.rfc-editor.org/rfc/rfc5122)), and the labels `legacy` and `unattested` (SK-COM §B1, §B5). *Rationale: the owner sees exactly which path a message took and that nobody vouches for it.*
- **[C1]** Inbound bridged messages **MUST** use only `messaging.send` and `share.offer`, **MUST NOT** carry `instructions`, and their content **MUST** be treated as untrusted `data`. *Rationale: an email must never become a command, which is the main prompt-injection path.*
- **[C1]** Outbound sends over a bridge **MUST** be shown as "Legacy connection: unattested" (SK-COM §B7) and **MUST** pass the owner's egress policy for the data classes involved; owner policy **MAY** forbid bridges for classes such as `finance` or `health`. *Rationale: no silent loss of end-to-end protection.*
- The bridge host can read bridged traffic. End-to-end encryption of the bridged system ends at the bridge, not at the phone. The Trusted UI should say so.

## 8. Security and Privacy Considerations (Non-Normative)

### 8.1 Security

- **No post-compromise security for stored and relayed messages in v0.1.** An attacker who copies a device's prekey private keys can open every sealed box addressed to the copied keys that the device has not yet opened, and every box sealed to its last-resort prekey until that prekey rotates (at most 7 days). Nothing in v0.1 heals the device after such a compromise: new boxes are safe again only after the device publishes fresh prekeys from an uncompromised state. Live sessions (section 6.2) get new keys with every TLS handshake. MLS, planned for v0.2, adds post-compromise security for the owner's devices.
- Forward secrecy for a sealed box starts when the recipient opens it and deletes the one-time private key. Boxes sealed to a last-resort prekey keep their exposure window until that prekey is deleted.
- The mailbox host is trusted for availability, not for confidentiality: it can delay, drop, or withhold, but it cannot read sealed boxes or forge prekeys.
- Envelope and prekey signatures are classical (`Ed25519`, `ES256`). Post-quantum signatures wait for SK-COM §B8.

### 8.2 Privacy

- The mailbox host sees connection times, sizes, mailbox handles, claim requests, and IP addresses of the owner's devices. Because the owner runs it, this is the owner's own metadata. A hosting provider with access to the VM can see the same and, for envelopes addressed to the host runtime itself, the content. Residency tags apply to the host location ([issue #37](https://github.com/selfkin/standards/issues/37)).
- A compromised mailbox host can withhold one-time prekeys and force senders onto the last-resort prekey. It cannot read sealed boxes or forge prekeys. Recipients can notice an unusual share of last-resort deliveries.
- mDNS reveals that some Selfkin device is present on the LAN and its IP and MAC addresses. Rotating instance and host names limit linking, not presence.
- QR codes contain a pairing secret for at most 300 seconds. A photographed code is useless after one pairing or expiry.

## 9. Provisional Identifiers (Non-Normative)

No registration is requested for v0.1. Every identifier below is provisional and is to be registered at v1.0, through the registry and policy shown.

| Identifier | Registry at v1.0 | Policy |
|---|---|---|
| ALPN `selfkin/1` | [TLS ALPN Protocol IDs](https://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml) | Expert Review ([RFC 7301](https://www.rfc-editor.org/rfc/rfc7301) section 6) |
| Service name `selfkin` (udp, tcp) | [Service Name and Port Number Registry](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml) | First Come First Served for names without a port ([RFC 6335](https://www.rfc-editor.org/rfc/rfc6335) section 7.2) |
| WebSocket subprotocol `selfkin.1` | [WebSocket Subprotocol Name Registry](https://www.iana.org/assignments/websocket/websocket.xhtml) | First Come First Served ([RFC 6455](https://www.rfc-editor.org/rfc/rfc6455) section 11.5) |
| Well-known URI suffix `selfkin` | [Well-Known URIs](https://www.iana.org/assignments/well-known-uris/well-known-uris.xhtml) | Specification Required ([RFC 8615](https://www.rfc-editor.org/rfc/rfc8615)) |
| Media types `application/vnd.selfkin.wire.*+json` | [Media Types](https://www.iana.org/assignments/media-types/media-types.xhtml) | Expert Review for the vendor tree ([RFC 6838](https://www.rfc-editor.org/rfc/rfc6838) section 3.2) |
| QR prefix `SK1:` | none (defined here) | none |

No port number is needed: SK-WIRE uses 443 and advertised ports. The HPKE code point `25722` (0x647a) belongs to draft-ietf-hpke-pq and is not an SK-WIRE identifier.

## 10. Dependencies and Deferrals

SK-WIRE v0.1 needs these SK-COM changes, proposed in separate pull requests:

- **SK-COM §A3, §A5, §B7, `registries/intents.md`, and `schemas/envelope.schema.json`:** `sk.negotiate` may omit `cap_token` and never carries `instructions` (section 6.1).
- **SK-COM §A9:** a store-and-forward envelope lives at most 7 days; without `instructions`, its token is evaluated at `issued` and revocation is checked at receipt (section 6.4).
- **SK-COM §A4:** TLS 1.3 or QUIC for every path; Noise drops from SHOULD to MAY (section 3.1).
- **SK-COM §A5.1 and §B8:** `ES256` is mandatory to verify and optional to sign (section 2).

Deferred to v0.2 or later: post-compromise security through the MLS binding for the owner's devices (D8), direct device-to-device paths with NAT traversal (D17), SAS-only pairing (D7), BLE and Wi-Fi Aware discovery (SK-COM §D Q6), and F2 mailboxes.

## 11. Own Methods and Why

SK-WIRE defines two things of its own. Both reuse standard primitives (HMAC-SHA256, HPKE, CBOR) and are specified above with their state machines and CDDL.

- **QR pairing proof (section 4.3).** Published alternatives either need both devices to have a camera (mutual QR scanning with key commitments, as in Briar's [BQP](https://code.briarproject.org/briar/briar-spec)), a password-authenticated key exchange for which no free library was verified on both demo platforms, or a vendor service. The one-sided QR with a pinned key and one-time secret works between a terminal and a phone and keeps the SAS as a second check.
- **Mailbox control protocol (section 6.4).** No standard covers depositing to and fetching from an owner-run mailbox with per-device prekeys: Signal's server interface is not a standard, Matrix homeservers keep messages as room history, and MIMI ([draft-ietf-mimi-arch-03](https://datatracker.ietf.org/doc/draft-ietf-mimi-arch/), work in progress) addresses provider-to-provider interoperability. The protocol here has five requests and is meant to be replaced by an MLS delivery service binding if v0.2 adopts MLS.

## 12. Checking

- CDDL: `cddl drafts/sk-wire/wire-binding-v0.1.cddl validate FILE.cbor` with the [`cddl` Ruby gem](https://rubygems.org/gems/cddl) 0.12.14 (see [RFC 8610 Appendix F](https://www.rfc-editor.org/rfc/rfc8610#appendix-F)) checks a frame or QR payload.
- Test vectors: [test-vectors/wire](../../test-vectors/wire/) holds provisional vectors (#67) for frame structure, QR decoding, pairing proofs, the SAS, advertisement names, chunk decryption, prekey selection and signatures, and a known-answer sealed frame for the mandatory HPKE suite `[32, 1, 3]` built from the [RFC 9180 Appendix A.2.1](https://www.rfc-editor.org/rfc/rfc9180#appendix-A.2.1) keys. The hybrid suite has no vector until its code point is final.

## 13. References

QUIC [RFC 9000](https://www.rfc-editor.org/rfc/rfc9000); QUIC-TLS [RFC 9001](https://www.rfc-editor.org/rfc/rfc9001); TLS 1.3 [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446); hybrid key exchange in TLS 1.3 [RFC 9954](https://www.rfc-editor.org/rfc/rfc9954); PQ/T hybrid key agreement mechanisms for TLS 1.3 [RFC 10024](https://www.rfc-editor.org/rfc/rfc10024); raw public keys in TLS [RFC 7250](https://www.rfc-editor.org/rfc/rfc7250); ALPN [RFC 7301](https://www.rfc-editor.org/rfc/rfc7301); WebSocket [RFC 6455](https://www.rfc-editor.org/rfc/rfc6455); Happy Eyeballs v2 [RFC 8305](https://www.rfc-editor.org/rfc/rfc8305); mDNS [RFC 6762](https://www.rfc-editor.org/rfc/rfc6762); DNS-SD [RFC 6763](https://www.rfc-editor.org/rfc/rfc6763); service names [RFC 6335](https://www.rfc-editor.org/rfc/rfc6335); HPKE [RFC 9180](https://www.rfc-editor.org/rfc/rfc9180); post-quantum HPKE [draft-ietf-hpke-pq-05](https://datatracker.ietf.org/doc/draft-ietf-hpke-pq/) (work in progress); MLS [RFC 9420](https://www.rfc-editor.org/rfc/rfc9420); TLS channel binding [RFC 9266](https://www.rfc-editor.org/rfc/rfc9266); JWK thumbprint [RFC 7638](https://www.rfc-editor.org/rfc/rfc7638); named information [RFC 6920](https://www.rfc-editor.org/rfc/rfc6920); base45 [RFC 9285](https://www.rfc-editor.org/rfc/rfc9285); CBOR [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949); CDDL [RFC 8610](https://www.rfc-editor.org/rfc/rfc8610); Ed25519 [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032); X25519 [RFC 7748](https://www.rfc-editor.org/rfc/rfc7748); ChaCha20-Poly1305 [RFC 8439](https://www.rfc-editor.org/rfc/rfc8439); ICE [RFC 8445](https://www.rfc-editor.org/rfc/rfc8445); well-known URIs [RFC 8615](https://www.rfc-editor.org/rfc/rfc8615); media types [RFC 6838](https://www.rfc-editor.org/rfc/rfc6838); documentation addresses [RFC 5737](https://www.rfc-editor.org/rfc/rfc5737); email [RFC 5322](https://www.rfc-editor.org/rfc/rfc5322); XMPP [RFC 6120](https://www.rfc-editor.org/rfc/rfc6120), [RFC 5122](https://www.rfc-editor.org/rfc/rfc5122); [Matrix specification](https://spec.matrix.org/latest/); [X3DH](https://signal.org/docs/specifications/x3dh/); [PQXDH](https://signal.org/docs/specifications/pqxdh/); [did:key method](https://w3c-ccg.github.io/did-key-spec/); [W3C DID v1.0](https://www.w3.org/TR/did-1.0/); [Noise Protocol Framework](https://noiseprotocol.org/noise.html).
