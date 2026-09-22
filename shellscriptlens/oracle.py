# SPDX-License-Identifier: AGPL-3.0-or-later OR EUPL-1.2
# Copyright 2026 Saimonokuma.
"""Oracles: byte verification, check verdicts, gate readings.

Every expected value in every suite was measured by running one of these
instruments (or the timeout/installer labs whose outputs they wrap).
Nothing here judges; everything measures. Requires node on PATH.
"""

import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def _pkg_data(sub):
    """Installed package data (importlib.resources), source fallback."""
    try:
        from importlib.resources import files

        base = files(__package__) / sub
        if base.is_dir():
            return str(base)
    except Exception:
        pass
    return os.path.normpath(os.path.join(HERE, "..", sub))


VENDOR = _pkg_data("vendor")
_LIB = os.environ.get("RDC_LIB", "C:/Users/Saimono/.config/opencode/lib")
_SHIPPED_GATE = os.path.join(VENDOR, "lib", "ai-slop.mjs")
_GATE = (_SHIPPED_GATE if os.path.isfile(_SHIPPED_GATE)
         else os.path.join(_LIB, "ai-slop.mjs"))


def _node(script, *args, timeout=120):
    p = subprocess.run(
        ["node", script, *args], capture_output=True, text=True, timeout=timeout
    )
    raw = p.stdout.strip()
    start = raw.find("{")
    if start < 0:
        raise RuntimeError(f"no JSON from {script}: {raw[-200:]}")
    return p.returncode, json.loads(raw[start:])


def verify_bytes(path):
    """Measured verifyFile reading: {bytes, cr, bom, utf8, ok}."""
    _rc, doc = _node(
        os.path.join(VENDOR, "ecma_probe.mjs"),
        "verifyFile",
        json.dumps(os.path.abspath(path)),
    )
    if not doc.get("ok"):
        raise RuntimeError(doc.get("error"))
    return doc["out"]


def check_verdict(path, base_dir):
    """Measured rdc check verdict: (ok, error_codes)."""
    _rc, doc = _node(
        os.path.join(VENDOR, "rdc_check.mjs"),
        os.path.abspath(path),
        os.path.abspath(base_dir),
    )
    codes = [
        f.get("code", "") for f in doc.get("findings", []) if f.get("level") == "error"
    ]
    return bool(doc.get("ok")), codes


def gate_reading(path):
    """Measured ai-slop gate reading: (alive, failing_measure_names)."""
    p = subprocess.run(
        ["node", _GATE, os.path.abspath(path), "--json"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    raw = p.stdout
    doc = json.loads(raw[raw.find("{") :])
    failing = [m["name"] for m in doc.get("measures", []) if not m.get("holds", True)]
    return bool(doc.get("alive")), failing
