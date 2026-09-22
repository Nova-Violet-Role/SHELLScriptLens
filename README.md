# SHELLScriptLens — From Raw Experience to Skill Consumption, for Shell Artifacts

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.13+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Verdicts](https://img.shields.io/badge/verdicts-measured_not_judged-16a34a?style=for-the-badge)]()
[![Licence](https://img.shields.io/badge/Licence-AGPL--3.0--or--later_OR_EUPL--1.2-764ba2?style=for-the-badge)](#-license)
[![Ko-fi](https://img.shields.io/badge/Support-Ko--fi-FF5E5B?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/saimonokuma)

</div>

## ✨ Overview

**SHELLScriptLens** is a SkillLens-shaped lab for systematically studying
*model-generated judgment skills* over shell artifacts (`.sh`, exit codes,
byte descriptions, sweep outputs, installer decisions) across their full
lifecycle: **experience generation → skill extraction → skill consumption**.
It is built to answer the core question:

> *What makes model-generated shell judgment actually correct, and what
> drives skill utility across the experience → extraction → consumption
> lifecycle?*

The framework provides:

- 🖥️ **Exit-code verdicts, named** — control trip codes (0/1/2/124),
  timeout semantics (including timeout-0 disables and the C≈S race), every
  code measured by running the control, never recited.
- 🧾 **Byte-description verdicts** — `verifyFile` readings (CR count, BOM,
  UTF-8 validity) from byte-exact fixtures, including the traps
  (UTF-16 BOM is not a BOM; NUL is valid UTF-8).
- 📦 **Installer-decision verdicts** — WROTE/SKIP/KEEP/die/planned,
  measured in a throwaway target lab, plus dry-run plans that write nothing.
- 📊 **Reproducible consumption audits** — held-out test deltas per suite,
  EE/TE readings, and a negative-transfer watch that blocks adoption on any
  negative cell.
- 🎚️ **Bench presets** — `hard`, `very-hard`, `really-hard`, plus user
  contributions (see below).

## 🚀 Quick Start

```bash
pip install shellscriptlens
# or, from source:
uv venv --python 3.13 .venv
uv pip install --python .venv/Scripts/python.exe -e .
```

```bash
shellscriptlens suites                         # 73 items across 7 suites
shellscriptlens check <file> <dir>             # measured verdict
shellscriptlens preset --check all             # verify the bench programs
```

## 🧩 Pipeline

| Stage | Command | What it does |
|---|---|---|
| **1. Raw experience generation** | engine `eval_only` | Runs the target model on the exam with the seed skill and writes raw rollouts. |
| **2. Schema normalization** | engine `normalize_trajectories` + `shellscriptlens validate` | Converts raw outputs into unified `Trajectory` records; the validator proves conformance. |
| **3. Skill extraction** | engine `train` | Distills the experience pool into a skill (gated accepts only). |
| **4. Skill consumption** | `shellscriptlens audit` | Re-runs the target on held-out tests with the extracted skill and reports per-suite deltas. |

## 📚 Benchmarks

Seven exam suites (73 items: 35 train / 24 val / 14 test — the selection
was expanded Lean-managed mid-program after a saturation pre-flight).
Every expected value was measured before the manifest was written.
Held-out test scores of the extracted skill (from empty seed, witnessed
run) are shown.

| Suite | Domain | Test (extracted) |
|---|---|---|
| **sweepverdicts** | Readings off sweep output lines (+ derived arithmetic) | 1.00 |
| **controlstrip** | Control exit codes, named (0/1/2/124) | 0.50 |
| **ceilings** | Timeout exit semantics, timeout-0, C≈S race | 1.00 |
| **encoding** | `verifyFile` verdicts from byte descriptions | 1.00 |
| **manifests** | Installer WROTE/SKIP/KEEP/die/planned | 0.50 |
| **real-v1** | Verdicts on real shell artifacts | 0.50 (flat, held) |
| **real-v3** | Nested ceilings, gate search, noisy dry-runs | 0.50 sel / 1.00 test |

Overall held-out test: 0.60 → 0.80 (delta +0.20).

## 🎚️ Presets

| Preset | Tier | Epochs | Budget | Demands |
|---|---|---|---|---|
| `hard` | 1 | 4 | 4 | verdicts |
| `very-hard` | 2 | 6 | 6 | verdicts + evidence |
| `really-hard` | 3 | 8 | 8 | verdicts + evidence + chains |

```bash
shellscriptlens preset --list          # hard, very-hard, really-hard
shellscriptlens preset --show hard     # tier, epochs, suites, description
shellscriptlens preset --check all     # every preset verified against data
```

Contribute yours: add `presets/<name>.yaml` (format in `presets/README.md`),
verify with `shellscriptlens preset --check <name>`, propose it.

## ⚙️ Configuration

Bench configs live beside the engine (`skillopt`-side `configs/shellscript-*.yaml`);
the lab owns the data, the oracles and the suite definitions.

The held-out test split is committed under `data/suites/*/test/`.

## 📖 Study grounding

The exam design is grounded in measured instrument behavior: timeout exits
measured through git-bash (`timeout 0` disables — counter-intuitive,
measured), byte verdicts measured through `verifyFile` on byte-exact
fixtures, installer decisions measured in a throwaway target (created,
forced, modified, uninstalled, manifest-checked, then removed), sweep
readings off real sweep output. Pre-flight policy throughout: never train
on a saturated exam — expand first (the selection grew 10 → 20 on a
saturation finding).

## 🔎 Veridicity: how this differs from SkillLens

- **No agent benchmarks.** The subjects are shell behaviors and their
  traces, not SWE-bench-style agents.
- **No LLM-as-judge.** Exit codes are read, byte counts are counted,
  installer decisions are observed. A verdict no instrument can produce is
  not an exam.
- **No sequential/parallel mode extraction.** Extraction is SkillOpt's gated
  loop from an empty seed; the lab owns the exam, the engine owns the loop.
- **Documented frontiers.** controlstrip/manifests at 0.5 (mechanism
  verdicts resist) are recorded, not smoothed over.
- **Single extractor × single target so far.** EE/TE readings are
  single-cell deltas, honestly labeled.
- **Licensed for reuse.** `AGPL-3.0-or-later OR EUPL-1.2` (see `LICENSE.md`);
  this repo publishes to PyPI and GitHub under Nova-Violet-Role.

Ground-truth oracles live in `shellscriptlens/oracle.py` (byte verification,
check verdicts, gate readings — all read-only); the schema and validator in
`shellscriptlens/schema.py`, shared verbatim with the sibling lens labs.

## 🧰 CLI reference

```bash
shellscriptlens suites                       # count every suite split
shellscriptlens check <file> <dir>            # measured rdc verdict
shellscriptlens validate <trajectories.jsonl> # schema conformance
shellscriptlens audit <results.jsonl> ...     # per-suite delta tables
shellscriptlens preset --list/--show/--check  # bench programs
```

## 💬 Community

- Falsified a claim in these docs? The `false claim` issue form is the
  fastest contribution — credited, not punished.
- Bug with a repro? `bug report` form (commands + exit codes, read directly).
- Proposal? Argue the problem, the cost and the rejected alternatives.
- Questions in Discussions (Q&A); ideas in Ideas; Show and tell for work.
  Security issues go through the private advisory form (see `SECURITY.md`).
- Read `CONTRIBUTING.md` before proposing; presets have their own guide in
  `presets/README.md`.

## 📜 License

`AGPL-3.0-or-later OR EUPL-1.2` — see `LICENSE.md`.
Support the work: [ko-fi.com/saimonokuma](https://ko-fi.com/saimonokuma).
