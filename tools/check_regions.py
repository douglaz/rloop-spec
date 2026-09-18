#!/usr/bin/env python3
"""Rendering gate (ADR-0002): a marked region in a document is what its declaration emits.

`ADR-0002` moved a formalized clause's calculation, predicate or table into a Lean
declaration and promised that "the rendering is kept honest by a gate, not by
discipline". Two hand-kept copies drift, so the copy
in the Markdown is either generated from the declaration or diffed against it.

A region is the lines between two markers, each on a line of its own:

    <!-- formal: Rloop.Render.ldg31Table -->
    | event | ... |
    <!-- /formal -->

The name is a declaration `lake exe gate` indexed (so it is tagged with the
requirement it formalizes), and `lake exe render` emits its text. Two kinds:

  render  Pure computation -- a worked table, a diagram. Compared line for line;
          `--write` rewrites the region from the declaration.

  match   A table whose cells carry prose and citations the declaration does not
          emit. The first column is the row's key: its emitted tokens must appear
          in the document's cell, in order. Every other column is compared on the
          tokens the declaration determines -- backticked and bold spans drawn
          from the vocabulary the emitted table uses (a state, a close reason, the
          fence column's verdict) -- and those must match exactly. A row's
          rationale is free; its outcome is not. A `match` region holds the
          table and nothing else: a line that is not a table row is refused. What
          this does NOT catch: the header row, which is never compared, and prose
          in an outcome cell that contradicts the tokens beside it.

Three more refusals, each `DEF-16`'s green check in another form: a region naming
a declaration the index does not carry; a region sitting in a requirement other
than the one its declaration is tagged with; and a region the declarations emit
that no document renders.

Reads the files `tools/check_formal.sh` writes, so `check-all.sh` runs that gate
first. A missing index is a red gate, not a skipped one (`AGENTS.md`).

Exit 0 = every region is what its declaration emits, 1 = drift or a structural
refusal, 2 = the formal build's output is missing.
"""

import difflib
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIONS = os.path.join(ROOT, "tools", "formal", ".lake", "regions.jsonl")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_ids import DEF_RE as HEAD_RE  # noqa: E402  -- one requirement-head regex, not two

INDEX = os.path.join(ROOT, "tools", "formal", ".lake", "index.jsonl")


def read_index():
    """decl -> requirement id, from what `lake exe gate` printed."""
    if not os.path.exists(INDEX):
        print(f"FAIL: {INDEX} missing -- run tools/check_formal.sh first")
        sys.exit(2)
    out = {}
    for line in open(INDEX):
        if line.strip():
            row = json.loads(line)
            out[row["decl"]] = row["req"]
    return out

BEGIN = re.compile(r"^<!-- formal: (Rloop\.[A-Za-z0-9_.]+) -->$")
END = "<!-- /formal -->"
TOKEN = re.compile(r"`[^`\n]+`|\*\*[^*\n]+\*\*")


def load_formal():
    index = read_index()
    if not os.path.exists(REGIONS):
        print(f"FAIL: {REGIONS} missing -- run tools/check_formal.sh first "
              f"(check-all.sh orders it before this gate)")
        sys.exit(2)
    regions = {}
    for line in open(REGIONS):
        if line.strip():
            row = json.loads(line)
            regions[row["decl"]] = (row["kind"], row["text"].split("\n"))
    return index, regions


def find_regions(lines):
    """Yield (decl, begin_index, end_index) for each marked region; end is the END line."""
    open_at = None
    for i, line in enumerate(lines):
        m = BEGIN.match(line.rstrip("\n"))
        if m:
            if open_at is not None:
                raise ValueError(f"line {i + 1}: region opened inside the one at line {open_at[1] + 1}")
            open_at = (m.group(1), i)
        elif line.rstrip("\n") == END:
            if open_at is None:
                raise ValueError(f"line {i + 1}: '{END}' with no open region")
            yield open_at[0], open_at[1], i
            open_at = None
    if open_at is not None:
        raise ValueError(f"line {open_at[1] + 1}: region {open_at[0]} never closed")


def requirement_at(lines, i):
    """The requirement whose body holds line i, or None."""
    for j in range(i, -1, -1):
        m = HEAD_RE.match(lines[j])
        if m:
            return m.group(1) or m.group(2)
    return None


def cells(row):
    parts = [c.strip() for c in row.strip().split("|")]
    return parts[1:-1] if len(parts) >= 2 else parts


def table_body(lines):
    """The data rows of a Markdown table: everything after the |---| separator."""
    rows = [l for l in lines if l.lstrip().startswith("|")]
    for k, r in enumerate(rows):
        if re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", r.strip()):
            return rows[k + 1:]
    return rows


def match_table(doc_lines, emitted_lines):
    """Return the list of drift messages for a `match` region."""
    stray = [l for l in doc_lines if l.strip() and not l.lstrip().startswith("|")]
    if stray:
        return [f"a line that is not a table row: {stray[0].strip()[:80]!r}"]
    doc, want = table_body(doc_lines), [l for l in emitted_lines if l.strip()]
    if len(doc) != len(want):
        return [f"{len(doc)} row(s) in the document, {len(want)} emitted"]
    vocab = {t for row in want for c in cells(row)[1:] for t in TOKEN.findall(c)}
    out = []
    for n, (d, w) in enumerate(zip(doc, want), 1):
        dc, wc = cells(d), cells(w)
        if len(dc) != len(wc):
            out.append(f"row {n}: {len(dc)} cell(s), {len(wc)} emitted")
            continue
        key, dkey = TOKEN.findall(wc[0]), TOKEN.findall(dc[0])
        it = iter(dkey)
        if not all(any(t == k for t in it) for k in key):
            out.append(f"row {n}, key column: expected {key} in order, document has {dkey}")
        for col in range(1, len(wc)):
            got = [t for t in TOKEN.findall(dc[col]) if t in vocab]
            exp = TOKEN.findall(wc[col])
            if got != exp:
                out.append(f"row {n}, column {col + 1}: declaration says {exp}, document says {got}")
    return out


def main(write=False):
    os.chdir(ROOT)
    index, regions = load_formal()
    seen, failures = {}, 0
    for f in sorted(glob.glob("*.md")) + sorted(glob.glob("docs/adr/*.md")):
        lines = open(f).read().split("\n")
        try:
            found = list(find_regions(lines))
        except ValueError as exc:
            print(f"  {f}: {exc}")
            failures += 1
            continue
        rewritten = False
        for decl, b, e in reversed(found):  # reversed: rewriting keeps earlier offsets valid
            body = lines[b + 1:e]
            where = f"{f}:{b + 1}"
            if decl not in regions:
                print(f"  {where}: region names {decl}, which the declarations do not emit")
                failures += 1
                continue
            if decl in seen:
                print(f"  {where}: region {decl} already rendered at {seen[decl]}")
                failures += 1
            seen[decl] = where
            req = index.get(decl)
            holder = requirement_at(lines, b)
            if req is None:
                print(f"  {where}: {decl} is not in the index -- a region's declaration is tagged")
                failures += 1
            elif holder != req:
                print(f"  {where}: {decl} is tagged {req} but sits in {holder}")
                failures += 1
            kind, emitted = regions[decl]
            if kind == "render":
                doc = [l.rstrip() for l in body]
                want = [l.rstrip() for l in emitted]
                if doc != want:
                    if write:
                        lines[b + 1:e] = emitted
                        rewritten = True
                        print(f"  {where}: rewrote {decl}")
                    else:
                        print(f"  {where}: {decl} drifted from its declaration:")
                        for d in difflib.unified_diff(doc, want, "document", "declaration", lineterm="", n=0):
                            print(f"      {d}")
                        failures += 1
            elif kind == "match":
                for msg in match_table(body, emitted):
                    print(f"  {where}: {decl}: {msg}")
                    failures += 1
            else:
                print(f"  {where}: {decl} has unknown kind {kind!r}")
                failures += 1
        if rewritten:
            open(f, "w").write("\n".join(lines))
    for decl in sorted(set(regions) - set(seen)):
        print(f"  {decl} is emitted but no document renders it")
        failures += 1
    if failures:
        print(f"\nFAIL: {failures} rendering failure(s). A marked region is what its declaration "
              f"emits; change the declaration, then `--write` the render regions.")
        return 1
    print(f"rendered regions: {len(seen)}, each what its declaration emits")
    return 0


if __name__ == "__main__":
    sys.exit(main(write="--write" in sys.argv))
