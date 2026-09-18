#!/usr/bin/env python3
"""Conformance-coverage gate.

Every requirement that is not itself a conformance item is either cited by at least one `CNF`
item in 06-conformance.md, or listed in that document's "Not testable black-box" table with a
reason. A requirement in neither is untested and unexplained, and this gate refuses it. There
is no ratchet baseline: the set is small enough to hold at zero.

Exit 0 = every requirement covered or excused, 1 = not.
"""

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_ids import DEF_RE, CITE_RE, prefix  # noqa: E402

DOC = "06-conformance.md"
ITEM_RE = re.compile(r"^(?:- )?\*\*(CNF-\d+[a-z]?)\*\*")
EXCUSE_RE = re.compile(r"^\|\s*`((?:OVR|RUN|AGT|PRM|DIR|SEQ)-\d+[a-z]?)`\s*\|", re.M)


def main():
    os.chdir(ROOT)
    defined = {}
    for f in sorted(glob.glob("*.md")):
        for m in DEF_RE.finditer(open(f).read()):
            defined.setdefault(m.group(1) or m.group(2), f)

    text = open(DOC).read()
    covered, current = set(), None
    for line in text.split("\n"):
        if line.startswith("#"):
            current = None
        m = ITEM_RE.match(line)
        if m:
            current = m.group(1)
        if current:
            covered.update(c.group(1) for c in CITE_RE.finditer(line))

    excused = set()
    idx = text.find("Not testable black-box")
    if idx != -1:
        excused = {m.group(1) for m in EXCUSE_RE.finditer(text[idx:])}

    reqs = sorted(k for k in defined if prefix(k) not in ("CNF", "F"))
    uncovered = [k for k in reqs if k not in covered and k not in excused]
    both = sorted(k for k in reqs if k in covered and k in excused)
    print(f"requirements: {len(reqs)} | cited by a CNF item: {len([k for k in reqs if k in covered])} "
          f"| excused: {len([k for k in reqs if k in excused])}")
    if uncovered:
        print("UNCOVERED (no CNF item cites it and it is not excused):", " ".join(uncovered))
    if both:
        print("BOTH covered and excused (pick one):", " ".join(both))
    if uncovered or both:
        return 1
    print("OK: every requirement is cited by a conformance item or excused with a reason")
    return 0


if __name__ == "__main__":
    sys.exit(main())
