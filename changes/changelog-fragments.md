---
title: Change fragments instead of direct CHANGELOG edits
type: process
---

Process change. No normative rule changed.

### Added

- `changes/`: one fragment per pull request (`changes/<pr-number>.md` or `changes/<slug>.md`) with a `title`, a `type`, and the entry text; `changes/README.md` defines the format.
- `tools/validate/changelog.py`: checks fragments, checks on pull requests that a fragment was added, and assembles the fragments into CHANGELOG.md at release. Tests in `tools/validate/test_changelog.py`.
- CI: the validate job checks the fragment format; a new `Change fragment` job checks that a pull request adds one, unless it carries the `no-changelog` label or changes no checked path.

### Changed

- `CONTRIBUTING.md` and the pull request template: add a fragment instead of editing CHANGELOG.md.
