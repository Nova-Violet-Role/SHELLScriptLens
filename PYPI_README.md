# SHELLScriptLens — harness usage

Deterministic oracles + benchmark suites for shell judgment
(sweep verdicts, control trip-proof, ceilings, encoding, manifests).
No model required to run the harness — every verdict is computed,
byte-exact, on your machine.

## Requirements

- Python 3.11–3.13 (`3.13` recommended; `3.14` is not supported)
- `PyYAML >= 6` (only dependency)
- A POSIX shell (only to run the *reference* artifacts the oracles
  mirror; the oracles themselves are pure Python)
- No GPU. No network. No model key for oracle use.

## Install

```bash
pip install shellscriptlens
# or: uv pip install shellscriptlens
```

## Commands

All five verbs are read-only and offline:

```bash
shellscriptlens suites                    # list suites + item counts
shellscriptlens check <file> <dir>        # verdict over one file
shellscriptlens validate                  # validate every bundled manifest
shellscriptlens audit <results...>        # score rollout results vs manifests
shellscriptlens preset --list             # list bench presets
shellscriptlens preset --show hard        # show a preset (tier/epochs/suites)
shellscriptlens preset --check all        # verify presets against the data
```

(`python -m shellscriptlens.cli` works identically.)

## What each command does

- `suites` — inventory: suite names with train/val/test counts
  (sweepverdicts, controlstrip, ceilings, encoding, manifests, real-v1,
  real-v3).
- `check` — shell-artifact verdicts: sweep readings, ceilings, trip
  controls, encodings, dry-run plans, gate readings. Exit 0 with the
  verdict plus per-assertion detail.
- `validate` — schema-checks every bundled `items.json`.
- `audit` — scores model rollouts against manifests: hard, soft,
  per-tier. The same metric the published deltas were measured with.
- `preset` — the bench programs: `hard` (tier 1), `very-hard` (tier 2),
  `really-hard` (tier 3).

## Examples

```bash
shellscriptlens check data\fixtures\encoding\E00_clean.md data\fixtures\encoding
# VERDICT: ok

shellscriptlens preset --show hard
# name: hard
# tier: 1  epochs: 4  budget: 4  gate: hard
# suites: sweepverdicts, controlstrip, ceilings, encoding, manifests, real-v1, real-v3
```

## Contribute a preset

Add `presets/<name>.yaml` (see `presets/README.md` for the format),
then `shellscriptlens preset --check <name>` before proposing it.

## Capabilities and limits

- Judges shell-shaped artifacts: sweep outputs, timeout ceilings,
  control files, encodings, install manifests, gate readings.
- Does not train models, does not call networks, does not write files.
- Verdicts are deterministic: same bytes in, same verdict out.

## License and support

`AGPL-3.0-or-later OR EUPL-1.2` (see `LICENSE.md`).
Support the work: [ko-fi.com/saimonokuma](https://ko-fi.com/saimonokuma).
Falsified a claim in these docs? File it — the fastest contribution:
`false claim` issue form.
