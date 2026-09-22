# SPDX-License-Identifier: AGPL-3.0-or-later OR EUPL-1.2
# Copyright 2026 Saimonokuma.
"""shellscriptlens CLI: suites | check | validate | audit. Read-only, offline."""

import argparse
import glob
import json
import os
import sys

import yaml

from .oracle import check_verdict
from .schema import validate_file

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _pkg_data(sub):
    """Installed package data (importlib.resources), source fallback."""
    try:
        from importlib.resources import files
        base = files(__package__) / sub
        if base.is_dir():
            return str(base)
    except Exception:
        pass
    return os.path.join(ROOT, sub)


DATA = _pkg_data("data")
PRESETS = _pkg_data("presets")


def cmd_suites(_args):
    rows = []
    for split in ("train", "val", "test"):
        for path in sorted(
            glob.glob(os.path.join(DATA, "suites", "*", split, "items.json"))
        ):
            with open(path, encoding="utf-8") as f:
                items = json.load(f)
            suite = path.split(os.sep)[-3]
            rows.append((suite, split, len(items)))
    total = sum(n for _, _, n in rows)
    for suite, split, n in rows:
        print(f"{suite:14s} {split:5s} {n}")
    print(f"total: {total} items")
    return 0


def cmd_check(args):
    ok, codes = check_verdict(args.file, args.dir)
    print(f"VERDICT: {'ok' if ok else 'FAIL ' + ','.join(codes)}")
    return 0 if ok else 1


def cmd_validate(args):
    n, bad = validate_file(args.trajectories)
    print(f"records: {n} invalid: {len(bad)}")
    for i, problems in bad[:5]:
        print(f"  line {i}: {problems}")
    return 0 if not bad else 1


def cmd_audit(args):
    per_suite = {}
    for path in args.results:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                key = (str(r.get("skill", "?")), str(r.get("task_type", "?")))
                cell = per_suite.setdefault(key, [0, 0])
                cell[1] += 1
                cell[0] += 1 if r.get("hard") == 1 else 0
    total_hit = sum(h for h, _ in per_suite.values())
    total_n = sum(n for _, n in per_suite.values())
    for (skill, task), (h, n) in sorted(per_suite.items()):
        print(f"{skill:12s} {task:26s} hard={h}/{n}={h / n:.4f}")
    print(f"overall hard={total_hit}/{total_n}={total_hit / total_n:.4f}")
    return 0


def _preset_dir():
    return PRESETS


def _load_preset(name):
    path = os.path.join(_preset_dir(), f"{name}.yaml")
    if not os.path.isfile(path):
        return None, path
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f), path


def _check_preset(name):
    doc, path = _load_preset(name)
    problems = []
    if doc is None:
        return [f"no such preset: {path}"]
    if doc.get("name") != name:
        problems.append(f"name {doc.get('name')!r} != filename {name!r}")
    if doc.get("tier") not in (1, 2, 3):
        problems.append(f"tier {doc.get('tier')!r} not in 1..3")
    for key in ("epochs", "edit_budget", "batch_size"):
        v = doc.get(key)
        if not isinstance(v, int) or v <= 0:
            problems.append(f"{key} {v!r} not a positive int")
    if doc.get("gate") != "hard":
        problems.append(f"gate {doc.get('gate')!r} != 'hard'")
    suites = doc.get("suites", [])
    if not suites:
        problems.append("suites is empty")
    for s in suites:
        if not os.path.isdir(os.path.join(DATA, "suites", s)):
            problems.append(f"suite missing: {s}")
    return problems


def cmd_preset(args):
    if args.list:
        names = sorted(f[:-5] for f in os.listdir(_preset_dir()) if f.endswith(".yaml"))
        for n in names:
            print(n)
        return 0
    if args.check:
        bad = 0
        targets = (
            [args.check]
            if args.check != "all"
            else sorted(
                f[:-5] for f in os.listdir(_preset_dir()) if f.endswith(".yaml")
            )
        )
        for n in targets:
            problems = _check_preset(n)
            if problems:
                bad += 1
                print(f"FAIL {n}:")
                for p in problems:
                    print(f"  - {p}")
            else:
                print(f"ok   {n}")
        return 1 if bad else 0
    doc, path = _load_preset(args.show)
    if doc is None:
        print(f"no such preset: {path}")
        return 2
    print(f"name: {doc.get('name')}")
    print(
        f"tier: {doc.get('tier')}  epochs: {doc.get('epochs')}  "
        f"budget: {doc.get('edit_budget')}  gate: {doc.get('gate')}"
    )
    print(f"suites: {', '.join(doc.get('suites', []))}")
    print(str(doc.get("description", "")).strip())
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="shellscriptlens")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("suites").set_defaults(fn=cmd_suites)
    p = sub.add_parser("check")
    p.add_argument("file")
    p.add_argument("dir")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("validate")
    p.add_argument("trajectories")
    p.set_defaults(fn=cmd_validate)
    p = sub.add_parser("audit")
    p.add_argument("results", nargs="+")
    p.set_defaults(fn=cmd_audit)
    p = sub.add_parser("preset")
    p.add_argument("--list", action="store_true")
    p.add_argument("--show", type=str, default=None)
    p.add_argument("--check", type=str, default=None)
    p.set_defaults(fn=cmd_preset)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
