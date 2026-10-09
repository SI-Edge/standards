---
title: SK-RT pointers to SK-COM for device keys, revocation, mesh sync, and peer connections
type: clarification
---

No new requirement. Each pointer names the SK-COM rule that the runtime profile already requires through its communication profile (SK-RT §21: R1 with C1, R2 with C2, R3 with C3). Algorithms are not named here. The pointer to a signature algorithm waits on #63, and the other open bindings stay open for roenu to decide.

### Changed

- `drafts/runtime-v0.3.md` §9: mesh sync follows SK-COM §A4 and §B7; revocation is applied as defined in SK-COM §A2.
- `drafts/runtime-v0.3.md` §10: the device identity is the device signing key of SK-COM §A2; hardware-backed device keys at R3 as in SK-COM §A2; the owner key binds devices and agents through owner-signed statements (SK-COM §A2).
- `drafts/runtime-v0.3.md` §12: peer-to-peer and mesh connections are governed by SK-COM §A4 and §B7.
- `drafts/runtime-v0.3.md` §15: hardware-backed keystore at R3 defined as for device keys in SK-COM §A2.
