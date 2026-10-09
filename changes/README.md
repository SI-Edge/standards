# Change Fragments

Every pull request that changes the drafts, schemas, examples, registries, test vectors, or tooling adds one
fragment here instead of editing [CHANGELOG.md](../CHANGELOG.md). At release, the fragments are assembled into
CHANGELOG.md and removed. Separate files never conflict, so pull requests no longer need CHANGELOG rebases.

## Format

File name: `changes/<pr-number>.md` once the pull request exists, or `changes/<short-slug>.md` before that
(lowercase letters, digits, and hyphens, for example `changes/signing-input.md`).

```markdown
---
title: Test vector suite version in one place
type: tooling
---

No normative rule changed.

### Changed

- `test-vectors/VERSION` is the only place the suite version is recorded.
```

- `title` (required): the CHANGELOG heading, without the date.
- `type` (required): `normative`, `clarification`, `schema`, `editorial`, `tooling`, or `process`.
- `date` (optional, `YYYY-MM-DD`, Europe/Zurich): the date shown in CHANGELOG.md. Without it the release date is used.
- Body: the CHANGELOG entry text. It must not be empty. Use `###` subheadings (`Added`, `Changed`, `Fixed`,
  `Removed`) with a blank line after each heading. Plain ASCII punctuation, no em-dashes or en-dashes.
- Write file paths as code (`schemas/README.md`), not as relative links: a link that works from `changes/`
  breaks once the entry moves into CHANGELOG.md, and the other way round.

## Assembling a Release

```sh
python tools/validate/changelog.py check                 # format of every fragment
python tools/validate/changelog.py assemble --dry-run    # print the CHANGELOG section
python tools/validate/changelog.py assemble              # write CHANGELOG.md and delete the fragments
```

Entries are placed at the top of CHANGELOG.md, newest first; entries of the same date keep file-name order.
CI checks the format of every fragment, and on pull requests that a fragment was added. A pull request that
changes only files outside the checked paths (for example `.github/` or `docs/`), or that carries the
`no-changelog` label, needs no fragment.
