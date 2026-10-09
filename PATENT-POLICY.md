# Patent Policy

> **Status: Draft, not for implementation. No certification program exists.**
> This is an interim, royalty-free patent policy for the draft phase. **It is not legal advice.** It has not yet been reviewed by a lawyer and must be reviewed by qualified counsel before any document reaches v1.0. Until then, maintainers may correct it through the process in section 11.

## 1. Purpose

The Selfkin drafts aim to be open to everyone. Anyone should be able to build a conforming runtime, device, or provider without asking for permission and without paying patent royalties. This policy asks everyone who contributes to the specifications to promise not to use their patents against people who implement them.

The policy is modelled on two well-known approaches:

- the royalty-free commitments of the [W3C Patent Policy](https://www.w3.org/policies/patent-policy/), and
- the [Open Web Foundation Agreement 1.0](https://www.openwebfoundation.org/the-agreements/the-owf-1-0-agreements-granted-claims/owfa-1-0) (OWFa 1.0), in the form of a patent non-assert covenant.

It is shorter than either. Where this policy is unclear, it should be read in the spirit of those documents: royalty-free, worldwide, and with defensive termination only.

## 2. Definitions

- **Specification:** any document in this repository that contains normative rules (BCP 14 key words such as MUST, SHOULD, MAY), in any version and any status (Draft, Candidate, Stable). Today this means the documents in `drafts/`, the files in `schemas/` and `registries/`, and any later document that the [governance process](GOVERNANCE.md) adds.
- **Normative portion:** the parts of a Specification that a conforming implementation must or may follow. Examples, rationale lines, notes, open questions, and documents marked non-normative are **not** normative portions.
- **Contribution:** any text, schema, example, or code that a person or organisation submits to this repository, for example through a commit, pull request, issue, RFC, or review suggestion that a maintainer merges.
- **Contributor:** the person or organisation that makes a Contribution, together with its Affiliates. If you contribute as part of your job, your employer is the Contributor unless your employer has told the maintainers otherwise in writing.
- **Affiliate:** any entity that controls, is controlled by, or is under common control with the Contributor, where "control" means owning more than 50% of the voting rights or having the power to direct its management.
- **Essential Claim:** a claim in any patent or patent application, anywhere in the world, that would necessarily be infringed by implementing a normative portion of a Specification, because there is no technically feasible way to implement that portion without infringing it. A claim is not essential just because a non-infringing alternative is more expensive or less convenient. Claims that cover only enabling technologies (for example a semiconductor process, an operating system, a programming language, or a general-purpose cryptographic primitive that the Specification only references) are not Essential Claims.
- **Implementation:** any product, service, software, hardware, or part of one that implements one or more normative portions of a Specification, to the extent it does so.

## 3. The Royalty-Free Commitment

By making a Contribution, each Contributor makes the following commitment for its **Essential Claims that read on its own Contribution**, as that Contribution appears in any version of a Specification published in this repository:

1. **Non-assert covenant.** The Contributor irrevocably promises, subject only to section 6, not to assert those Essential Claims against anyone for making, having made, using, selling, offering for sale, importing, or otherwise distributing an Implementation.
2. **Royalty-free license on request.** If anyone needs a written license instead of the covenant, the Contributor will grant one for the same Essential Claims, worldwide, royalty-free, non-exclusive, and on otherwise reasonable and non-discriminatory terms, with no conditions other than those in sections 4 and 6.
3. **Who benefits.** The commitment benefits everyone who makes or uses Implementations, whether or not they ever contributed. No registration, fee, or notice is required.
4. **Future patents.** The commitment covers Essential Claims that the Contributor owns or controls when it contributes and those it acquires later.
5. **Transfers.** If the Contributor transfers a patent that contains such an Essential Claim, it must make the transfer subject to this commitment.

The commitment is limited to Essential Claims and to Implementations of normative portions. It gives no rights to use patents for anything else, and it does not cover changes made by others after the Contribution unless those changes are necessary consequences of the Contribution.

## 4. Scope and Duration

- **Withdrawing before merge.** A Contribution can be withdrawn at any time before a maintainer merges it. A withdrawn Contribution is not covered and creates no commitment.
- **After merge.** Once a Contribution is merged, the commitment for it is permanent for every version of a Specification that includes it, also if the Contributor later stops participating. A Contributor that leaves the project does not make commitments for Contributions others make after it left.
- **Later versions.** If a later version still contains the Contribution, or a part of it, the commitment continues for that part.

## 5. Disclosure

- Participants are **not** required to search their or anyone else's patent portfolios.
- If you know of a patent or patent application, held by you or by anyone else, that you believe may contain an Essential Claim **not** covered by this policy, please tell the maintainers. Open an issue with the label `ip`, or, if you prefer, use the private channel in [SECURITY.md](SECURITY.md). Give the patent number if you can and the affected section.
- Maintainers will record disclosures in the affected Specification's open questions. The project may then change the Specification to avoid the claim.

## 6. Defensive Termination

A Contributor may end its commitment under section 3 **for one specific party** (and that party's Affiliates) if that party, or anyone acting for it, starts or joins a lawsuit or other proceeding claiming that an Implementation infringes an Essential Claim of any Specification in this repository.

This does not apply if the party only does so:

- as a counterclaim or defence in a proceeding that someone else started first against it about Essential Claims, or
- to defend against a claim that its own Implementation infringes.

Termination affects only that party. The commitment stays in force for everyone else.

## 7. Copyright and Code

- Copyright in specification text is licensed under **CC BY 4.0** ([LICENSE](LICENSE)).
- Copyright in schemas, test suites, and code is licensed under the **Apache License 2.0** ([LICENSE-CODE](LICENSE-CODE)). Section 3 of the Apache License contains its own patent license for code contributions. This policy adds to it and does not limit it.

## 8. No Other Rights

Except as stated in section 3, no license or other right is granted, by implication or otherwise. In particular, this policy grants no rights to use any name, logo, or mark of the project or of any Contributor. See [TRADEMARKS.md](TRADEMARKS.md). Nothing in this policy is a promise that an Implementation does not infringe the patents of people who never contributed.

## 9. How Contributors Agree

- Every commit must carry a **Developer Certificate of Origin (DCO)** sign-off (`git commit -s`), as described in [CONTRIBUTING.md](CONTRIBUTING.md).
- **By signing off a commit, or by submitting a Contribution in any other way, the Contributor agrees to this policy for that Contribution.** This is in addition to the DCO and the copyright licenses.
- If you contribute for an employer or another organisation, you confirm that you are allowed to make this commitment for it. If you are not sure, ask your employer before contributing, or say so in the pull request so maintainers can hold the merge.
- If you cannot agree to this policy, please do not contribute normative text. Issues that only report problems are always welcome.

## 10. Founding Maintainer

The founding maintainer, roenu (@roenudev), makes the commitment in section 3 for all content that was in this repository when this policy was adopted, as if it had been contributed under this policy.

## 11. Changes to This Policy

- Changes go through the RFC process in [GOVERNANCE.md](GOVERNANCE.md), with at least 14 days for comment, and are recorded in [CHANGELOG.md](CHANGELOG.md).
- A change can never reduce a commitment already made for an earlier Contribution.
- Before v1.0, the project expects to replace or confirm this policy after review by counsel, possibly by adopting the full W3C Patent Policy, OWFa 1.0, or the policy of the organisation that becomes the project's long-term home. Questions that counsel should review include: the governing law and jurisdiction, how employer contributions are confirmed, whether a separate signed agreement is needed in addition to the DCO, and whether contributors should be able to exclude specific claims during a review period, as the W3C policy allows.

## 12. Not Legal Advice

This document was written to make the project's intent clear in plain language. It is not legal advice and may not be enforceable in every jurisdiction as written. Contributors and implementers who need certainty should get their own legal advice.
