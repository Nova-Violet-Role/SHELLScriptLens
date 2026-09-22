# Contributing a preset

A preset binds a strictness tier to a bench program: which suites run, how
many epochs, what edit budget, and which assertion tier gates. Users
contribute presets by adding one YAML file per preset under `presets/`.

## File format (`presets/<name>.yaml`)

```yaml
name: my-preset            # slug; must match the filename
description: >             # one paragraph: what it proves
  ...
tier: 2                    # 1 = verdicts, 2 = +evidence, 3 = +chains
epochs: 6                  # train epochs
edit_budget: 6             # max edits per gate step
batch_size: 25
gate: hard                 # gate metric
suites:                    # subset of data/suites/* (must all exist)
  - sweepverdicts
  - ceilings
```

## Rules

- `name` matches the filename (`my-preset` lives in `my-preset.yaml`).
- `tier` is 1, 2, or 3 — the assertion tiers the manifests already carry
  (`min_tier`). No new assertion kinds without a manifest change.
- Every suite in `suites` must exist under `data/suites/`.
- Verify with the bound command before proposing:
  `shellscriptlens preset --check my-preset`.
