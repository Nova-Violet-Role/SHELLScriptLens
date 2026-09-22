# SPDX-License-Identifier: AGPL-3.0-or-later OR EUPL-1.2
# Copyright 2026 Saimonokuma.
"""lens-trajectory/v1: the unified Trajectory schema + validator.

Shared verbatim across the three lens labs: one schema, three file classes.
A record without a conversation was not observed; a claim standing on it is
not measured.
"""

import json

SCHEMA = "lens-trajectory/v1"

REQUIRED = {
    "schema",
    "lens",
    "suite",
    "phase",
    "item_id",
    "task_type",
    "scores",
    "assertion_results",
    "model",
    "backend",
    "has_conversation",
}


def validate_record(r):
    """Return a list of problems (empty = valid)."""
    problems = []
    if r.get("schema") != SCHEMA:
        problems.append("schema")
    missing = REQUIRED - set(r.keys())
    if missing:
        problems.append("keys:" + ",".join(sorted(missing)))
    sc = r.get("scores", {})
    if sc.get("hard") not in (0, 1, 0.0, 1.0):
        problems.append("hard-range")
    try:
        soft = float(sc.get("soft", -1))
    except (TypeError, ValueError):
        soft = -1
    if not 0.0 <= soft <= 1.0:
        problems.append("soft-range")
    if "outcome" in r and r["outcome"] not in ("resolved", "unresolved", "error"):
        problems.append("outcome")
    for a in r.get("assertion_results", []):
        if not isinstance(a.get("pass"), bool):
            problems.append("assert-pass-bool")
            break
    u = r.get("usage")
    if u is not None:
        for k in ("prompt_tokens", "completion_tokens", "total_tokens"):
            if not isinstance(u.get(k), int) or u[k] < 0:
                problems.append("usage")
                break
    return problems


def validate_file(path):
    """Validate a trajectories.jsonl file. Returns (n, bad_list)."""
    bad = []
    n = 0
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            n += 1
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                bad.append((i, ["bad-json"]))
                continue
            problems = validate_record(r)
            if problems:
                bad.append((i, problems))
    return n, bad
