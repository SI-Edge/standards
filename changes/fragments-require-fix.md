---
title: Change fragment check counts only fragment files
type: tooling
---

Tooling change. No normative rule changed.

### Fixed

- `tools/validate/changelog.py require`: only `changes/<name>.md` counts as a fragment. `changes/README.md`, dotfiles such as `changes/.markdownlint-cli2.jsonc`, other file types, and files in subfolders no longer satisfy the check or mark a release. `check` and `assemble` skip Markdown dotfiles too. Tests in `tools/validate/test_changelog.py`.
