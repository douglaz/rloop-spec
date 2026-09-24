#!/usr/bin/env python3
"""Requirement-identifier gate.

  * every requirement id is defined exactly once      (duplicate ids)
  * every cited id is defined somewhere               (dangling citations)
  * no id is missing from a namespace's sequence      (renumbering / gaps)
  * every cited ADR exists on disk                    (bad ADR references)
  * a cited normative clause has one home or quotes its owner (restatements)

Identifiers are append-only (README.md, *Requirement conventions*). A withdrawn id may be absent
from the documents only if the README's "Withdrawn identifiers" table lists it.

Restatements use F2's blocking/advisory boundary (ADR-0007); identifier
integrity failures always block. Exit 0 = no blocking findings, 1 = failures.
"""

import glob
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAMESPACES = ["OVR", "RUN", "AGT", "PRM", "DIR", "SEQ", "CNF", "F"]
NS = "|".join(NAMESPACES)

# A requirement is defined as `**RUN-7** ...` at the start of a line, optionally as a bullet
# (`- **CNF-1** ...`), or as a heading `### F1`.
DEF_RE = re.compile(
    r"^(?:[-*]\s+(?:\[[ x]\]\s+)?)?\*\*((?:%s)-?\d+[a-z]?)\*\*"
    r"|^#{1,6}\s+\**((?:%s)-?\d+[a-z]?)\**" % (NS, NS),
    re.M,
)
CITE_RE = re.compile(r"`((?:%s)-?\d+[a-z]?)`" % NS)
ADR_RE = re.compile(r"`?ADR-(\d{4})`?")
WITHDRAWN_RE = re.compile(r"^\|\s*`?((?:%s)-?\d+[a-z]?)`?\s*\|" % NS, re.M)


def number(rid):
    return int(re.match(r"[A-Z]+-?(\d+)", rid).group(1))


def prefix(rid):
    return re.match(r"([A-Z]+)", rid).group(1)


# Reviewed clauses are recorded only when they define their enclosing
# requirement's own rule. Exact text as spec_text.norm sees it, never an id or
# document exemption: an edit reopens the ownership question. See F2.
def clause_key(home, text):
    from spec_text import norm
    return home, hashlib.sha256(norm(text).encode()).hexdigest()


def reviewed_homes():
    with open(os.path.join(ROOT, "tools", "restatement-homes.json")) as f:
        return {(r["owner"], r["sha256"]): r["reason"] for r in json.load(f)}


def restatements(docs, reqs):
    from spec_text import RFC, attributions, clauses, containing, norm, prose, restatement_tier, units

    failures = []
    homes = reviewed_homes()
    for document, text in docs.items():
        for unit in units(prose(text)):
            cites = list(CITE_RE.finditer(unit.text))
            keywords = list(RFC.finditer(unit.text))
            if not cites or not keywords:
                continue
            position = unit.start + len(unit.text) - len(unit.text.lstrip())
            home = containing(reqs, document, position)
            if all(c[1] == home for c in cites):
                continue
            # A modal alone (including MUST NOT) does not quote a rule. Any
            # phrase with content beyond its modal can take the quotation route;
            # the citation gate verifies the actual words against their owner.
            attributed = list(attributions(unit))
            quoted = [q for _, q, _ in attributed
                      if unit.text[q.start] == "`" and
                      re.search(r"\w", re.sub(r"\bNOT\b", "", RFC.sub("", norm(q.text))))]
            defining = [c for c in clauses(unit.text) if clause_key(home, c.text) in homes]
            uncovered = [k for k in keywords
                         if not any(q.start <= k.start() < q.end for q in quoted + defining)]
            # Keep each tier visible in a mixed paragraph. A different explicit
            # quotation cannot turn an inferred restatement into a blocker.
            reported = set()
            for keyword in uncovered:
                tier = restatement_tier(unit, keyword, attributed)
                if tier not in reported:
                    failures.append((document, unit.start + keyword.start(),
                                     sorted({c[1] for c in cites}), norm(unit.text), tier))
                    reported.add(tier)
    return failures


def main():
    os.chdir(ROOT)
    root_md = sorted(glob.glob("*.md"))
    adr_md = sorted(glob.glob("docs/adr/*.md"))

    defined, dupes = {}, []
    for f in root_md:
        for m in DEF_RE.finditer(open(f).read()):
            rid = m.group(1) or m.group(2)
            if rid in defined:
                dupes.append((rid, defined[rid], f))
            else:
                defined[rid] = f

    cited = set()
    for f in root_md + adr_md:
        cited.update(m.group(1) for m in CITE_RE.finditer(open(f).read()))

    withdrawn = set()
    if os.path.exists("README.md"):
        readme = open("README.md").read()
        idx = readme.find("Withdrawn identifiers")
        if idx != -1:
            withdrawn = {m.group(1) for m in WITHDRAWN_RE.finditer(readme[idx:])}

    dangling = sorted(c for c in cited if c not in defined and c not in withdrawn)

    gaps, outliers = {}, {}
    for ns in NAMESPACES:
        nums = sorted(number(k) for k in defined if prefix(k) == ns)
        if not nums:
            continue
        body = nums
        while len(body) > 1 and body[-1] - body[-2] > 50:
            outliers.setdefault(ns, []).append(body[-1])
            body = body[:-1]
        sep = "" if ns == "F" else "-"
        missing = [n for n in range(1, max(body) + 1)
                   if n not in body and f"{ns}{sep}{n}" not in withdrawn]
        if missing:
            gaps[ns] = missing[:20] + ([f"... and {len(missing) - 20} more"] if len(missing) > 20 else [])

    adrs = {os.path.basename(p)[:4] for p in adr_md}
    bad_adrs = set()
    for f in root_md + adr_md:
        for m in ADR_RE.finditer(open(f).read()):
            if m.group(1) not in adrs:
                bad_adrs.add(m.group(1))

    items = sum(1 for k in defined if prefix(k) == "CNF")
    print(f"requirements: {len(defined)} | md files: {len(root_md)} | ADRs: {len(adrs)}")
    print(f"conformance items: {items}")
    print("DUPES:", dupes or "none")
    print("DANGLING:", dangling or "none")
    print("NUMBER GAPS:", gaps or "none")
    print("OUTLIER IDS:", outliers or "none")
    print("BAD ADR REFS:", sorted(bad_adrs) or "none")
    from spec_text import line_at, load
    docs, reqs = load(ROOT)
    repeated = restatements(docs, reqs)
    for document, position, owners, clause, tier in repeated:
        column = position - docs[document].rfind("\n", 0, position)
        print(f"{tier} RESTATEMENT: {document}:{line_at(docs[document], position)}:{column} "
              f"cites {', '.join(owners)} outside its owning definition:")
        print(f"  {clause}")
        print("  Review ownership; F2 describes quotation coverage and reviewed defining clauses.")
    if not repeated:
        print("RESTATEMENTS: none")
    blocking = any(tier == "BLOCKING" for *_, tier in repeated)
    return 1 if (dupes or dangling or gaps or outliers or bad_adrs or blocking) else 0


if __name__ == "__main__":
    sys.exit(main())
