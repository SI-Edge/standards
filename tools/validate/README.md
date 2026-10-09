# SI Edge Validator

> **Status: Draft, not for implementation.** Licensed under Apache-2.0 ([LICENSE-CODE](../../LICENSE-CODE)).

Checks JSON documents against the v0.1 schemas in [../../schemas](../../schemas) in two layers: JSON Schema 2020-12, then semantic checks that JSON Schema cannot express (for example that a delegated capability token only narrows its parent). It does not check signatures, key trust, revocation, replay, or clocks.

```
pip install -r tools/validate/requirements.txt
python tools/validate/validate.py                          # all examples, with expected results
python tools/validate/validate.py doc.json --schema envelope
python -m unittest discover -s tools/validate -v           # tests
```

The tests check that every schema is valid JSON Schema 2020-12 with the required `$id`, `title`, and `description`; that every valid example passes and every `*.invalid.json` example fails; that every schema has both kinds of example; that every invalid example is explained in [examples/README.md](../../examples/README.md); and that no em-dashes or en-dashes are used.

## Continuous Integration

[ci/validate.yml](ci/validate.yml) is a GitHub Actions workflow that runs the validator and the tests on every push and pull request. To activate it, move it to `.github/workflows/validate.yml`. It is kept here for now because adding files under `.github/workflows/` needs a token with the GitHub "Workflows" permission.
