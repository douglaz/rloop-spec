"""Shared Markdown spans for the identifier and citation gates.

Only root Markdown defines requirements; root Markdown and ADRs cite them.
Offsets stay in the original text, including wrapped code spans. Fenced examples
are not prose. Requirement bodies stop at the next definition or section heading.
"""

from dataclasses import dataclass
from pathlib import Path
import re

from check_ids import CITE_RE, DEF_RE

RFC = re.compile(r"\b(?:MUST|SHALL|SHOULD|MAY|REQUIRED|RECOMMENDED|OPTIONAL)\b")
INLINE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)
DOUBLE = re.compile(r'“([^”\n]*(?:\n(?!\s*\n)[^”\n]*)*)”|"([^"\n]*(?:\n(?!\s*\n)[^"\n]*)*)"')
BOUNDARY = re.compile(r"\n[ \t]*\n|\n(?=\s*(?:[-*] |\d+\. |\||#{1,6} ))")
SENTENCE = re.compile(r"[.!?;](?:[*_]+)?(?=\s|$)")


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    text: str


@dataclass(frozen=True)
class Requirement:
    document: str
    start: int
    end: int
    text: str


def norm(text):
    """Ignore wrapping and Markdown emphasis, not case, punctuation or words."""
    return " ".join(re.sub(r"[*`~]", "", text).split())


def prose(text):
    """Mask fenced blocks without moving offsets (their bytes remain in bodies)."""
    lines, fence = [], None
    for line in text.splitlines(keepends=True):
        marker = re.match(r"\s*(`{3,}|~{3,})", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            lines.append(re.sub(r"[^\n]", " ", line))
        elif marker:
            fence = marker[1]
            lines.append(re.sub(r"[^\n]", " ", line))
        else:
            lines.append(line)
    return "".join(lines)


def quotations(text):
    # Parse each structural unit independently: an unmatched delimiter cannot
    # consume the next paragraph, list item, table row or requirement definition.
    spans = []
    for unit in units(text):
        inline = [Span(m.start(), m.end(), m[2]) for m in INLINE.finditer(unit.text)]
        double = [Span(m.start(), m.end(), m[1] if m[1] is not None else m[2])
                  for m in DOUBLE.finditer(unit.text)
                  if not any(s.start <= m.start() < s.end for s in inline)]
        spans.extend(Span(unit.start + q.start, unit.start + q.end, q.text)
                     for q in inline + double)
    return sorted(spans, key=lambda s: s.start)


def units(text):
    """Association units retain punctuation and wrapping, but not block boundaries."""
    boundaries = {0, len(text)}
    for m in BOUNDARY.finditer(text):
        boundaries.update((m.start(), m.end()))
    boundaries.update(m.start() for m in DEF_RE.finditer(text))
    points = sorted(boundaries)
    for start, end in zip(points, points[1:]):
        if text[start:end].strip():
            yield Span(start, end, text[start:end])


def clauses(text):
    """Smaller spans for exact defining-clause fingerprints, not association."""
    masked = list(text)
    for q in quotations(text):
        masked[q.start:q.end] = "x" * (q.end - q.start)
    start = 0
    for m in SENTENCE.finditer("".join(masked)):
        end = m.end()
        if text[start:end].strip():
            yield Span(start, end, text[start:end])
        start = m.end()
    if text[start:].strip():
        yield Span(start, len(text), text[start:])


def load(root):
    root = Path(root)
    paths = sorted(root.glob("*.md")) + sorted(root.glob("docs/adr/*.md"))
    docs = {str(p.relative_to(root)): p.read_text() for p in paths}
    reqs = {}
    for name, text in docs.items():
        if "/" in name:
            continue
        visible = prose(text)
        boundaries = sorted({m.start() for m in DEF_RE.finditer(visible)} |
                            {m.start() for m in re.finditer(r"^#{1,6} ", visible, re.M)} |
                            {len(text)})
        for m in DEF_RE.finditer(visible):
            end = next(p for p in boundaries if p > m.start())
            reqs.setdefault(m[1] or m[2], Requirement(name, m.start(), end, text[m.end():end]))
    return docs, reqs


def containing(reqs, document, position):
    return next((rid for rid, r in reqs.items()
                 if r.document == document and r.start <= position < r.end), None)


def line_at(text, position):
    return text.count("\n", 0, position) + 1


# Ported from provisiond-spec's direct-speech / possessive attribution patterns.
SPEECH = r"says|said|states|stated|reads|read"
NOUN = r"rule|claim|wording|statement|sentence|words|text"
INTRO = re.compile(r"(?:'s|’s)?\s+(?:own\s+)?(?:" + SPEECH + r")\b"
                   r"|(?:'s|’s)\s+(?:own\s+)?(?:" + NOUN + r")\s+that\b"
                   r"|\s+gives\b[^.;]{0,100}?\bmeaning as\b")


def attributions(unit):
    """Yield (owner, quotation) for explicit shapes and normative backtick spans.

    Explicit shapes: ID: quote, ID says quote, ID's quote, quote (ID).
    Direct speech can cross an input ID; the quote otherwise follows its verb
    immediately (optionally with 'that', a colon or a dash).
    Otherwise a normative backtick quote binds to the nearest citation in the
    association unit. Every such quote takes the same route in both gates.
    """
    text = unit.text
    cites = list(CITE_RE.finditer(text))
    quotes = [q for q in quotations(text) if not CITE_RE.fullmatch(text[q.start:q.end])]
    intros = [(c, INTRO.match(text, c.end())) for c in cites]
    intros = [(c, m) for c, m in intros if m]
    previous = None
    for q in quotes:
        # Parenthetical labels often cite a command/file definition, rather
        # than attributing prose. Explicit introducers also check short quotes.
        phrase = len(norm(q.text).split()) >= 4 or RFC.search(q.text)
        before = [c for c in cites if c.end() <= q.start]
        after = [c for c in cites if c.start() >= q.end]
        # An explicit speaker must not be replaced by a later pointer. Keep
        # parenthetical claims too; both relationships must verify if present.
        direct = [(c, m) for c, m in intros if m.end() <= q.start and
                  re.fullmatch(r"\s*(?:that\s+)?[:—-]?\s*",
                               CITE_RE.sub("", text[m.end():q.start]))]
        owner = None
        if direct:
            owner = direct[-1][0][1]
        elif before and re.fullmatch(r"\s*(?::|(?:'s|’s))\s*", text[before[-1].end():q.start]):
            owner = before[-1][1]
        elif previous and re.fullmatch(r"\s*(?:,\s*)?(?:and|or|also)?\s*",
                                      text[previous[1].end:q.start]):
            owner = previous[0]
        parenthetical = (after[0][1] if phrase and after and
                         re.fullmatch(r"\s*\(\s*", text[q.end:after[0].start()]) else None)
        if owner:
            yield owner, q
            if parenthetical and parenthetical != owner:
                yield parenthetical, q
        else:
            if parenthetical:
                owner = parenthetical
            elif RFC.search(q.text) and text[q.start] == "`" and cites:
                owner = min(cites, key=lambda c: min(abs(c.end() - q.start),
                                                    abs(c.start() - q.end)))[1]
            if owner:
                yield owner, q
        previous = (owner, q) if owner else None
