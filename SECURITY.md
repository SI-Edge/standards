# Security Policy

This repository contains specifications, not running software. A "vulnerability" here is a flaw in a specification that would let a conforming implementation be attacked or would weaken privacy, for example:

- a rule that permits a downgrade, replay, or impersonation attack;
- a gap that lets a module, peer, provider, or co-user bypass consent or Trusted UI;
- a privacy leak inherent in a required field, log, or flow;
- an incorrect statement about a cryptographic or legal reference that could mislead implementers.

## Reporting

Please report privately through **GitHub private vulnerability reporting** on this repository:

1. Go to the [Security tab of selfkin/standards](https://github.com/selfkin/standards/security).
2. Choose **Report a vulnerability** (opens a private security advisory: <https://github.com/selfkin/standards/security/advisories/new>).
3. Describe the affected document, section, and rule, the attack or leak, and a suggested fix if you have one.

Do not open public issues or pull requests for unfixed security or privacy flaws. Do not send reports by email.

## What to Expect

- Acknowledgement within 7 days.
- An initial assessment within 30 days.
- Fixes are made in the drafts and recorded in [CHANGELOG.md](CHANGELOG.md). With your consent, you are credited in the advisory and the changelog.
- We ask for coordinated disclosure: please wait until a fix is published, or 90 days, whichever comes first.

## Scope

In scope: everything under `drafts/`, [TERMINOLOGY.md](TERMINOLOGY.md), [THREAT-MODEL.md](THREAT-MODEL.md), and future schemas and test suites in this repository. Out of scope: third-party implementations (report to their maintainers) and the third-party standards referenced by the drafts.

## Public Design Discussion

The documents here are drafts, and nothing implements them in production. Design level weaknesses in the drafts (for example a missing requirement or an underspecified check) may be filed as public issues with the `review` label, so they can be discussed in the open. Use private reporting for anything that could harm a deployed system, including bugs in the reference implementation once people run it.
