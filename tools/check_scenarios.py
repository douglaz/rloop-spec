#!/usr/bin/env python3
"""Scenario gate (ADR-0002): `conformance/scenarios.tsv` is what the model enumerates.

The Conformance Suite replays the committed file so that an Implementation repository needs no
Lean; this gate holds the committed copy to `lake exe scenarios`'s output, which
`tools/check_formal.sh` wrote to `tools/formal/.lake/scenarios.tsv`. It also prints the count,
so that growth shows in review. `--write` copies the fresh output over the committed file.

Exit 0 = identical, 1 = drift, 2 = the formal build's output is missing.
"""

import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRESH = os.path.join(ROOT, "tools", "formal", ".lake", "scenarios.tsv")
COMMITTED = os.path.join(ROOT, "conformance", "scenarios.tsv")


def main(write):
    if not os.path.exists(FRESH):
        print(f"FAIL: {FRESH} missing -- run tools/check_formal.sh first")
        return 2
    fresh = open(FRESH, "rb").read()
    n = fresh.count(b"\n") - 1
    if write:
        shutil.copyfile(FRESH, COMMITTED)
        print(f"wrote {n} scenarios to conformance/scenarios.tsv")
        return 0
    cur = open(COMMITTED, "rb").read() if os.path.exists(COMMITTED) else b""
    if cur != fresh:
        print("FAIL: conformance/scenarios.tsv is not what the model enumerates; run with --write")
        return 1
    print(f"scenarios: {n}, the committed file is what the model enumerates")
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
