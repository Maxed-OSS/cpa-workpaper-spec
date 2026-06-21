#!/usr/bin/env python3
"""CPA Workpaper Spec conformance runner.

Runs the conformance manifest (``conformance/manifest.json``) against a
validator and reports whether each fixture is accepted/rejected as the spec
requires. Use this to prove that an implementation conforms: point it at the
bundled schemas (the default) or wire your own validator into the same
manifest.

By default it uses the reference Python validator in ``validator/validate.py``.

Usage:
    python3 conformance/run.py            # run the whole suite
    python3 conformance/run.py -v         # verbose: print each case

Exit code is 0 when every case behaves as the manifest requires, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "validator"))

from validate import build_store, load_schemas, validate_document  # noqa: E402

CONFORMANCE_DIR = REPO_ROOT / "conformance"
MANIFEST = CONFORMANCE_DIR / "manifest.json"


def load_manifest() -> dict:
    with MANIFEST.open(encoding="utf-8") as fh:
        return json.load(fh)


def run(verbose: bool = False) -> int:
    manifest = load_manifest()
    schemas = load_schemas()
    store = build_store(schemas)

    passed = 0
    failed = 0
    for case in manifest["cases"]:
        doc_path = CONFORMANCE_DIR / case["file"]
        expect = case["expect"]  # "valid" | "invalid"
        with doc_path.open(encoding="utf-8") as fh:
            document = json.load(fh)
        errors = validate_document(document, case["schema"], schemas, store)
        accepted = not errors
        ok = (accepted and expect == "valid") or (not accepted and expect == "invalid")
        if ok:
            passed += 1
            if verbose:
                print(f"PASS  [{expect:>7}] {case['file']}")
        else:
            failed += 1
            got = "accepted" if accepted else "rejected"
            print(f"FAIL  [{expect:>7}] {case['file']} (validator {got} it)")
            for line in errors:
                print(line)

    total = passed + failed
    print(f"\nconformance: {passed}/{total} cases behaved as required")
    return 0 if failed == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the CPA Workpaper Spec conformance suite.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print each case.")
    args = parser.parse_args(argv)
    return run(verbose=args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
