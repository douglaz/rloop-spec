#!/usr/bin/env python3
"""Verify quoted attribution against the cited requirement's own body.

Port of /home/master/projects/provisiond-spec/tools/check_citations.py's QUOTED
rule and direct-speech/possessive patterns. spec_text adds rloop's backtick and
parenthetical forms and shares the route used by check_ids' restatement rule.

Only whitespace and Markdown emphasis are normalized. A quote must be a
contiguous phrase in its owner's body, with word boundaries; no document/ADR
fallback, ellipsis splicing, historical/teaching exemption or baseline can make
a false current attribution pass. Explicit quotations in historical discussion
are still checked: describe removed wording without attributing it to a current
identifier, or cite the historical revision in prose.

Not ported: the unquoted direct-speech ratchet, obligation checker, provisiond
declaration-name index, baseline and historical-revision selftest. Summary prose,
implicit attribution across independent blocks, fenced examples and semantic contradictions
remain review duties. See spec_text.attributions for supported lexical shapes and
tools/test_citation_gates.py for isolated controls. Exit 0 = clean, 1 = false quote.
"""

from pathlib import Path
import re
import sys

from spec_text import attributions, line_at, load, norm, prose, units

ROOT = Path(__file__).resolve().parent.parent


def find(docs, reqs):
    bad = []
    for document, text in docs.items():
        for unit in units(prose(text)):
            for owner, quote in attributions(unit):
                body = norm(reqs[owner].text) if owner in reqs else ""
                phrase = norm(quote.text)
                if not phrase or not re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", body):
                    bad.append((document, unit.start + quote.start, owner, quote.text))
    return bad


def main():
    docs, reqs = load(ROOT)
    bad = find(docs, reqs)
    for document, position, owner, quote in bad:
        source = reqs[owner].document if owner in reqs else "undefined owner"
        print(f"CITATION: {document}:{line_at(docs[document], position)} attributes "
              f"to {owner} ({source}) words absent from its body:")
        print(f"  {norm(quote)}")
    print(f"FAIL: {len(bad)} unverifiable quoted attribution(s)." if bad else
          "Quoted attributions verified: clean")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
