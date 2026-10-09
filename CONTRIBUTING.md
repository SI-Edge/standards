# Contributing

Thank you for helping improve the SI Edge drafts. All drafts are early and **not for implementation**; feedback of every size is welcome.

## Ways to Contribute

- **Clarification or bug:** open an issue with the "Spec bug or clarification" template. Quote the file and section.
- **Small fix** (typo, broken link, wording that does not change meaning): open a pull request directly.
- **Substantial change** (new rule, changed MUST/SHOULD, new section, new profile requirement): open an issue with the "Proposal" template first. If maintainers ask for it, write an RFC from [rfcs/0000-template.md](rfcs/0000-template.md). See [GOVERNANCE.md](GOVERNANCE.md).
- **Security or privacy flaw in a spec:** do not open a public issue. Follow [SECURITY.md](SECURITY.md).

## Developer Certificate of Origin (DCO)

Every commit must be signed off under the [Developer Certificate of Origin 1.1](https://developercertificate.org/). By signing off you certify that you wrote the contribution or otherwise have the right to submit it under this project's licenses.

Add the sign-off with `git commit -s`. It adds a line like:

```
Signed-off-by: Your Name <your.email@example.com>
```

You may use a pseudonym and a GitHub noreply address, as long as it is consistent and lets maintainers contact you through GitHub.

## Licensing of Contributions

- Contributions to specification text and documentation are licensed under **CC BY 4.0** ([LICENSE](LICENSE)).
- Contributions of schemas, test suites, and code are licensed under the **Apache License 2.0** ([LICENSE-CODE](LICENSE-CODE)).
- Do not contribute text or code you cannot license this way, and do not paste text from other standards beyond short quotations with attribution.
- Patent commitments for all Contributions are covered by the [Patent Policy](PATENT-POLICY.md) (see above).

## Patent Policy

All Contributions are made under the royalty-free [Patent Policy](PATENT-POLICY.md). In short: for your essential patent claims that read on your own Contribution, you promise not to assert them against anyone who implements the Specifications, worldwide and royalty-free. The only exception is defensive termination against someone who sues over an Implementation (section 6 of the policy).

- **Your DCO sign-off also confirms that you agree to the Patent Policy for that Contribution.**
- If you contribute for an employer, make sure you are allowed to make this commitment for it, or say so in the pull request so maintainers can hold the merge.
- If you know of a patent that may affect a Specification, please tell the maintainers (open an issue with the `ip` label, or use the private channel in [SECURITY.md](SECURITY.md)). You are not required to search for patents.
- The policy is an interim draft and is not legal advice; it will be reviewed by counsel before v1.0.

## Style Rules for Specification Text

- Use the BCP 14 key words (RFC 2119, RFC 8174) in capitals only when you mean them normatively.
- Start every normative rule with a profile tag ([R1], [C2], [P3], ...) and end it with a one-line *Rationale*.
- Keep rules testable: avoid words like "promptly" or "reasonable" without a measurable bound.
- Keep the drafts vendor-neutral. Vendor and product names may appear only in clearly marked, non-normative example lists that carry a neutrality note. Never state or imply anything about a vendor's plans, products, or practices.
- Do not describe legal requirements unless you are sure they are accurate; prefer "can help with" over "required by".
- Use plain ASCII punctuation. Do not use em-dashes or en-dashes.
- Update [CHANGELOG.md](CHANGELOG.md) and the change note at the end of the affected draft.

## Pull Requests

- Fill in the pull request template.
- One topic per pull request.
- Keep cross-references and [TERMINOLOGY.md](TERMINOLOGY.md) in sync when you rename or add terms.

## Conduct

Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
