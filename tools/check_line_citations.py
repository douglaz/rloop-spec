#!/usr/bin/env python3
"""Verify that a `<path>:<line>` citation still points where its sentence says.

`07-open-findings.md` carries such citations into source files, and they drift: a cited
comment block that grows or shrinks by a line moves every number below it, and until this
gate nothing but a reader noticed. The rule is any-of: for each `<path>:<n>` or
`<path>:<n>-<m>` in a backticked span, at least one *other* backticked literal from the
citing sentence must still appear in the cited line or range. The gate prints which
literal anchored each citation, and the count it checked, because an any-of rule is
decided by the weakest literal in the sentence and the count is what lets review notice
when the regex stops tracking the prose.

The citing sentence is the scope, not the enclosing block (`spec_text.clauses` over
`spec_text.units`): at block scope a stale number launders itself through a requirement
identifier the cited line happens to carry. For the same reason an anchor shorter than
four characters, or shaped like a requirement identifier (`check_ids.CITE_RE`), is
dropped. A bare continuation inherits the path of the nearest preceding explicit citation
in its sentence and is checked like any other.

Both sides pass through `spec_text.norm`, and each cited line first loses its indentation
and one leading comment marker, so a comment sentence that wraps across two `# ` lines --
`conformance/run:53-54` is the case -- still reads as one phrase.

Tiers (`ADR-0007`). An unanchored citation is *advisory*: it is evidence the number
drifted, never proof, since prose may describe lines rather than quote them, and a gate
that objects to correct prose is the thing that is wrong. A range that cannot exist --
`n < 1`, `m < n`, or `m` past the file's last line -- *blocks*, because that is decidable.
Exit 0 = no blocking finding; advisories may be present.

Known limits, each of which lives here and nowhere else:

  * The stripped comment marker is language-shaped. `#` covers shell, Python and Nix,
    which is every cited file today; a citation into `tools/formal/` would need `--`.
    Stripping only ever deletes at a line start, so it can create an anchor the raw text
    lacked but cannot mask one it had.
  * Only a range's start is really constrained. A range that grew or shrank by a line
    at its far end still contains its anchor, so this says nothing about where a range
    ends; tightening it would require rewording correct prose.
  * The regex sees only a backticked citation with no whitespace in it, in prose. One
    written out in words ("line 32 of `conformance/run`"), one inside a fenced block
    (`spec_text.prose` masks those) and one whose path holds a space would each be
    invisible to it. The count it prints is of the tokens the regex matched, not of
    the citations the prose holds.
  * A path that resolves to a file outside this repository is reported unchecked rather
    than skipped. `Path.is_file()` cannot tell a foreign path from a typo, so a silent
    skip would turn a mistyped in-repo path into a permanent blind spot. Containment is
    tested after resolution, so a symlink out of the tree is not a local target.
"""

from pathlib import Path
import re
import sys

from check_ids import CITE_RE
from spec_text import clauses, line_at, load, norm, prose, quotations, units

ROOT = Path(__file__).resolve().parent.parent

CITATION = re.compile(r"(\S*):(-?\d+)(?:-(-?\d+))?")
MARKER = re.compile(r"^\s*#[ ]?")
MIN_ANCHOR = 4


def citations(docs):
    """Yield (document, line, token, path, first, last, anchors) in document order."""
    for document, text in docs.items():
        for unit in units(prose(text)):
            code = [q for q in quotations(unit.text) if unit.text[q.start] == "`"]
            for clause in clauses(unit.text):
                here = [q for q in code if clause.start <= q.start < clause.end]
                path = None
                for quote in here:
                    m = CITATION.fullmatch(quote.text)
                    if not m:
                        continue
                    path = m[1] or path
                    anchors = [a for a in here
                               if a.start != quote.start
                               and len(norm(a.text)) >= MIN_ANCHOR
                               and not CITATION.fullmatch(a.text)
                               # CITE_RE spells its own delimiters; a.text is the inner text.
                               and not CITE_RE.fullmatch(f"`{a.text}`")]
                    yield (document, line_at(text, unit.start + quote.start), quote.text,
                           path, int(m[2]), int(m[3] or m[2]), anchors)


def resolve(path):
    """The cited file, or None when the path is not a file inside this repository."""
    if not path:
        return None
    target = (ROOT / path).resolve()
    return target if target.is_file() and target.is_relative_to(ROOT) else None


def main():
    docs, _ = load(ROOT)
    checked = unchecked = blocking = advisory = 0
    for document, line, token, path, first, last, anchors in citations(docs):
        where = f"{document}:{line}"
        target = resolve(path)
        if target is None:
            print(f"UNCHECKED LINE CITATION: {where} cites `{token}`: "
                  f"target unavailable in this repository, not checked.")
            unchecked += 1
            continue
        cited = f"{path}:{first}" + (f"-{last}" if last != first else "")
        body = target.read_text().splitlines()
        checked += 1
        if first < 1 or last < first or last > len(body):
            print(f"BLOCKING LINE CITATION: {where} cites {cited}, a line {path} does not "
                  f"have ({len(body)} lines).")
            blocking += 1
            continue
        text = norm(" ".join(MARKER.sub("", l) for l in body[first - 1:last]))
        hit = next((norm(a.text) for a in anchors if norm(a.text) in text), None)
        if hit:
            print(f"  anchored  {where}  {cited}  by `{hit}`")
        else:
            print(f"ADVISORY LINE CITATION: {where} cites {cited}, where no other literal "
                  f"from its sentence appears:")
            print("  " + (", ".join(f"`{norm(a.text)}`" for a in anchors)
                          or "(no eligible literal in the sentence)"))
            advisory += 1
    print(f"Line citations: {checked} checked, {unchecked} unchecked; "
          f"{blocking} blocking, {advisory} advisory.")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
