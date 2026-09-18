#!/usr/bin/env python3
"""Fixture gate (ADR-0001): the Conformance Suite's fixtures are the documents' verbatim blocks.

`03-prompts.md` states each prompt in a ```prompt block under its `PRM-n`; `02-agents.md` states
each agent command line in a ```text block under its `AGT-n`. The Markdown is the home, the
suite compares what its fakes received against `conformance/fixtures/`, and this gate holds the
two identical so that neither can drift from the other.

  prompts/PRM-n.txt       the block's lines joined by newlines, no trailing newline -- the bytes
                          of the one argument the prompt is passed as (PRM-6)
  argv/AGT-n[-k].txt      one argument per line; a `<placeholder>` is one argument however many
                          words it holds; k numbers the blocks of a requirement that has several

`--write` regenerates the fixtures from the documents. Exit 0 = identical, 1 = drift or a
fixture with no block (or a block with no fixture).
"""

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "conformance", "fixtures")

HEAD = re.compile(r"^\*\*((?:PRM|AGT)-\d+)\*\*")
ARG = re.compile(r"<[^>]+>|\S+")


def blocks(path, fence):
    """(requirement id, block index, text) for every fenced block of that language."""
    rid, k, out, cur, lang = None, 0, [], None, None
    for line in open(path).read().split("\n"):
        m = HEAD.match(line)
        if m:
            rid, k = m.group(1), 0
        if cur is None and line.startswith("```"):
            lang, cur = line[3:].strip(), []
            continue
        if cur is not None:
            if line.startswith("```"):
                if lang == fence and rid:
                    k += 1
                    out.append((rid, k, "\n".join(cur)))
                cur, lang = None, None
            else:
                cur.append(line)
    return out


def expected():
    want = {}
    for rid, _, text in blocks(os.path.join(ROOT, "03-prompts.md"), "prompt"):
        want[os.path.join("prompts", f"{rid}.txt")] = text
    per_req = {}
    for rid, k, text in blocks(os.path.join(ROOT, "02-agents.md"), "text"):
        first = text.split("\n", 1)[0]
        if not (first.startswith("claude ") or first.startswith("codex ")):
            continue
        per_req.setdefault(rid, []).append(first)
    for rid, lines in per_req.items():
        for k, line in enumerate(lines, 1):
            name = f"{rid}.txt" if len(lines) == 1 else f"{rid}-{k}.txt"
            want[os.path.join("argv", name)] = "\n".join(ARG.findall(line)) + "\n"
    return want


def main(write):
    want = expected()
    have = {os.path.relpath(p, FIX) for p in glob.glob(os.path.join(FIX, "*", "*.txt"))}
    failures = 0
    for rel, text in sorted(want.items()):
        path = os.path.join(FIX, rel)
        cur = open(path, "rb").read().decode() if os.path.exists(path) else None
        if cur != text:
            if write:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                open(path, "wb").write(text.encode())
                print(f"  wrote {rel}")
            else:
                print(f"  {rel}: {'missing' if cur is None else 'differs from the document'}")
                failures += 1
    for rel in sorted(have - set(want)):
        print(f"  {rel}: fixture with no block in the documents")
        failures += 1
    if failures:
        print(f"\nFAIL: {failures} fixture(s) out of step with the documents; the Markdown is the home, "
              f"edit it and run with --write")
        return 1
    print(f"fixtures: {len(want)} ({sum(1 for k in want if k.startswith('prompts'))} prompts, "
          f"{sum(1 for k in want if k.startswith('argv'))} command lines), each its document's block")
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
