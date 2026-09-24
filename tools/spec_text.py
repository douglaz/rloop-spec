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
BOUNDARY = re.compile(r"\n[ \t]*\n|\n(?=\s*(?:[-*+] |\d+\. |\||#{1,6} ))")
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
    """A character rule, not a Markdown parser (F2 states why this is the boundary):
    every asterisk, backtick and tilde is removed wherever it occurs, code spans and
    paths included; every underscore is kept; whitespace runs, wrapping included,
    collapse to one space. Case, punctuation and words are preserved."""
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

# F2 / ADR-0007: no additional introducing phrases have been accepted.
INTRODUCING_PHRASES = ()
EXPLICIT_PREFIX = re.compile(r"\s*(?::|(?:'s|’s))")
PARENTHETICAL = re.compile(r"\s*\(([^()]*)\)")


def parenthetical_owners(content):
    """Retain broad recognition; only an ID/separator prefix blocks (F2)."""
    ownership = re.split(r";\s*but\s+see\b", content, maxsplit=1)[0]
    claims = list(CITE_RE.finditer(ownership))
    if not claims or ownership[:claims[0].start()].strip():
        return [], "ADVISORY"
    separators = CITE_RE.sub("", ownership)
    tier = "BLOCKING" if re.fullmatch(r"[\s,;/&]*", separators) else "ADVISORY"
    return [c[1] for c in claims], tier


def attributions(unit):
    """Yield (owner, quotation, tier) without dropping inferred relationships.

    Explicit shapes: ID: quote, ID says quote, ID's quote, quote (ID).
    Direct speech can cross ordinary prose, asides and input IDs, but stops at
    sentence punctuation or another quote. The latest explicit introducer wins.
    Every owner in an attached parenthetical is checked as well, including for
    short explicit quotes. A literal '; but see' (with flexible whitespace)
    begins an explanatory cross-reference; only preceding IDs claim ownership.
    Otherwise a normative backtick quote binds to the nearest citation in the
    association unit. Every such quote takes the same route in both gates.
    Colon/possessive and recognized introducers block only with whitespace-only
    quote attachment; ID/separator parenthetical prefixes also block.
    Intervening prose, continued quotes and the nearest-citation fallback are
    advisory; tiers belong to relationships.
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
        # An explicit speaker must not be replaced by a later pointer. Keep
        # parenthetical claims too; both relationships must verify if present.
        direct = [(c, "BLOCKING" if not text[m.end():q.start].strip() else "ADVISORY")
                  for c, m in intros if m.end() <= q.start and
                  re.fullmatch(r'[^.!?;`"“”]*', CITE_RE.sub("", text[m.end():q.start]))]
        if before and re.fullmatch(r"\s*(?::|(?:'s|’s))\s*", text[before[-1].end():q.start]):
            direct.append((before[-1], "BLOCKING"))
        owner = None
        tier = "ADVISORY"
        if direct:
            speaker, tier = max(direct, key=lambda pair: pair[0].start())
            owner = speaker[1]
        elif previous and re.fullmatch(r"\s*(?:,\s*)?(?:and|or|also)?\s*",
                                      text[previous[1].end:q.start]):
            owner = previous[0]
        parenthetical = []
        parenthetical_tier = "ADVISORY"
        attached = PARENTHETICAL.match(text, q.end) if phrase or owner else None
        if attached:
            # Keep the claimed owners before the explicit explanatory suffix;
            # its references do not claim to contain the quotation's words.
            parenthetical, parenthetical_tier = parenthetical_owners(attached[1])
        if not owner:
            if parenthetical:
                owner = parenthetical[0]
                tier = parenthetical_tier
            elif RFC.search(q.text) and text[q.start] == "`" and cites:
                owner = min(cites, key=lambda c: min(abs(c.end() - q.start),
                                                    abs(c.start() - q.end)))[1]
        relationships = dict.fromkeys(parenthetical, parenthetical_tier)
        if owner and (owner not in relationships or tier == "BLOCKING"):
            relationships[owner] = tier
        for claimed, severity in relationships.items():
            yield claimed, q, severity
        previous = (owner, q) if owner else None


def restatement_tier(unit, keyword, attributed):
    """Classify this uncovered modal, never borrow a different quote's tier.

    Unquoted colon/possessive clauses and attached ownership prefixes are
    explicit. Paragraph-wide association alone remains advisory. Quotations
    and sentence punctuation bound the unquoted clause used for this test.
    """
    text = unit.text
    quotes = [q for q in quotations(text)
              if not CITE_RE.fullmatch(text[q.start:q.end]) and
              re.search(r"\w", re.sub(r"\bNOT\b", "", RFC.sub("", norm(q.text))))]
    for q in quotes:
        if q.start <= keyword.start() < q.end:
            return ("BLOCKING" if any(a.start == q.start and tier == "BLOCKING"
                                       for _, a, tier in attributed) else "ADVISORY")
    start, end = 0, len(text)
    masked = list(text)
    # Punctuation inside quotes/parentheses must not split the outer clause.
    # Keep whitespace: PARENTHETICAL consumes the gap after outer punctuation,
    # and SENTENCE needs that gap for its lookahead. Masking preserves offsets.
    for span in quotes + [Span(m.start(), m.end(), m[0])
                          for m in PARENTHETICAL.finditer(text)]:
        masked[span.start:span.end] = re.sub(r"\S", "x", text[span.start:span.end])
    for boundary in SENTENCE.finditer("".join(masked)):
        if boundary.end() <= keyword.start():
            start = boundary.end()
        elif boundary.start() > keyword.start():
            end = boundary.start()
            break
    for q in quotes:
        if q.end <= keyword.start():
            start = max(start, q.end)
        elif q.start > keyword.start():
            end = min(end, q.start)
    if any(EXPLICIT_PREFIX.match(text, c.end())
           for c in CITE_RE.finditer(text, start, keyword.start())):
        return "BLOCKING"
    for attached in PARENTHETICAL.finditer(text, keyword.end(), end):
        owners, tier = parenthetical_owners(attached[1])
        if owners and tier == "BLOCKING":
            return tier
    return "ADVISORY"
