# Governance

> **Status:** interim governance for the draft phase (before v1.0).

## Maintainers

| Maintainer | GitHub | Role |
|---|---|---|
| roenu | [@roenudev](https://github.com/roenudev) | Founding editor and maintainer |

Maintainers review and merge changes, triage issues, and keep the drafts consistent. New maintainers are added by agreement of the existing maintainers, based on sustained, constructive contribution.

## Decisions

- **Small changes** (typos, links, clarifications that do not change meaning) are merged by a maintainer after review.
- **Substantial changes** (new or changed normative rules, profile requirements, new documents) go through a proposal issue and, where requested, an RFC using [rfcs/0000-template.md](rfcs/0000-template.md).
- RFCs are open for comment for at least 14 days. Maintainers aim for consensus. If consensus is not reached, the maintainers decide and record the reasoning in the RFC.
- Accepted RFCs are numbered and merged into `rfcs/`, and the drafts and [CHANGELOG.md](CHANGELOG.md) are updated.

## Document Status Labels

| Label | Meaning |
|---|---|
| **Draft** | Under active development. Not for implementation. May change completely |
| **Candidate** | Feature-complete for its version; open for implementation feedback and test suites |
| **Stable** | Released version; changes only through a new version |
| **Superseded** | Replaced by a newer document; kept for history |

All current documents are **Draft**. Superseded drafts live in `drafts/history/`.

## Versioning

- Each document has its own version (for example runtime v0.3, communication v0.1).
- Before v1.0, any version may introduce breaking changes.
- Conformance profiles become claimable beyond self-assessment only after a v1.0 release and a separately agreed conformance process.

## Path to Neutral Maintainership

Before any document reaches v1.0, the project intends to:

1. add maintainers from more than one organisation and jurisdiction;
2. decide on a long-term home (an open working group, a foundation, or an existing standards organisation);
3. confirm or replace the interim royalty-free [Patent Policy](PATENT-POLICY.md) after review by counsel (an interim policy is in force for the draft phase);
4. clarify the trademark status of the project names (see [TRADEMARKS.md](TRADEMARKS.md)).

## Intellectual Property

- **Copyright:** specification text is licensed under CC BY 4.0 ([LICENSE](LICENSE)); schemas, test suites, and code under Apache-2.0 ([LICENSE-CODE](LICENSE-CODE)).
- **Patents:** all Contributions are made under the royalty-free [Patent Policy](PATENT-POLICY.md): contributors promise not to assert their essential patent claims against implementations, with defensive termination only. Maintainers do not merge normative Contributions from contributors who have said they cannot agree to it.
- **Disclosures:** known patents that may affect a Specification are recorded in its open questions (see [PATENT-POLICY.md](PATENT-POLICY.md) section 5).
- **Changes:** the Patent Policy changes only through an RFC, and a change never reduces a commitment already made.
- The interim Patent Policy is **not legal advice** and must be reviewed by counsel before any document reaches v1.0.

## Code of Conduct

All participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
