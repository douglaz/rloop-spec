# A gate that cannot decide warns rather than blocks

**Status:** accepted (2026-09-22, after consulting three advisers — `opus`, `astra` and `sol` —
who agreed on the diagnosis and split on the remedy; two proposed this one independently)

The restatement and citation gates read prose and decide whether a sentence claims that a
quotation belongs to a requirement. Over the four Rounds that built them the Panel found four
distinct ways a real restatement escaped, each fix exposing the next. That alone is only a hard
problem. The decisive evidence is what it cost: `docs/adr/0006-*.md` was reworded from "the probe
`AGT-18` states" to "the probe from `AGT-18`" so that a gate would stop objecting to a sentence
that was correct.

**The class boundaries do not separate the cases.** The obvious rule — exclude the forms that
produce false positives, keep the forms that catch real misattributions — cannot be implemented,
because the same lexical shape produces both. Each of these was run against the gates:

| sentence | gate | truth |
|---|---|---|
| `` `SEQ-4` says the rule is `<RUN-16's words>` (`RUN-16`). `` | rejects | a real misattribution |
| `` `SEQ-4` says nothing about `one session` (`RUN-16`). `` | rejects | the sentence **denies** the attribution |
| `` `<RUN-16's words>` (`SEQ-4`; but see `RUN-16` …). `` | rejects | a real misattribution |
| `` rloop runs the probe `AGT-18` states … `<five-word span>` … `` | rejects | a relative clause claiming nothing |

"Says" and "says nothing about" are the same shape to a scanner and opposite in meaning. No
arrangement of grammatical categories separates them, because what separates them is sense.

**And a clean corpus is not evidence that the broad rule is safe.** This set passes both gates
today, but its one known false positive was removed from the corpus by rewording `ADR-0006`. The
corpus is clean partly because it was edited to be clean, which is selection bias, not a result.

So the gates get two tiers. A finite, unambiguous attribution grammar **fails the build**: forms
where the claim is explicit in the syntax rather than inferred — an identifier and a colon, a
possessive, a quotation immediately after its introducer, a parenthetical whose **ownership
prefix** is identifiers and separators, and a short enumerated set of introducing phrases. The
ownership prefix is the content before the explanatory marker `F2` already recognises, or the
whole content when there is none — so `` (`RUN-16`, `SEQ-4`) `` and
`` (`SEQ-4`; but see `RUN-16` …) `` both block on their leading claim, and the words after the
marker claim nothing. Testing the whole parenthetical instead would drop the second, which the
table above records as a real misattribution. Everything broader — ownership inferred across
unrestricted intervening prose — still runs, and reports, but **does not fail the build**.

## Consequences

- **A real misattribution may only warn.** `` `SEQ-4` says the rule is … `` is a genuine defect
  and, unless its introducer is in the enumerated set, it produces a warning a reader must act on
  rather than a red gate. That is the price, and it is paid deliberately: a check that blocks on
  an inference it cannot justify will be worked around by editing the prose, which is the failure
  this decision exists to stop.
- **`ADR-0006`'s original wording is restored**, and no sentence in this Specification is reworded
  to satisfy a scanner. If a gate objects to correct prose, the gate is wrong.
- **Controls assert the behaviour that occurs, never silence.** Closing one recognition route can
  re-open another: excluding a parenthetical from the citation route was measured to produce a
  restatement finding instead, because `tools/check_ids.py` treats a span as covered only when an
  owner was found for it. A control that demands silence would be unsatisfiable without a second
  exemption, which is a hole. Each control names concrete syntax and pairs with a positive one.
- **The nearest-citation fallback is part of the contract.** A form the explicit recogniser
  declines can still be caught by it; controls cover that route explicitly.
- `F2` in `07-open-findings.md` states which tier each form belongs to, and is where the boundary
  is read.

## Rejected

- **Exclude only the forms that produce false positives.** Not implementable: the counterexamples
  above sit in the same classes as the true positives. It is an outcome preference, not a
  recognition rule.
- **Narrow the quotation shape and register the exception.** Requiring a longer quoted phrase on
  the inferred route removes an unbounded class of false positives at no cost to any true positive
  — three lines, measured — and `ADR-0006`'s sentence could then be registered by digest so an
  edit reopens review. It was rejected as the boundary because it keeps the inferred route
  blocking, so the prose keeps bending, one registered sentence at a time. The narrowing remains
  available on its own merits for the advisory tier, where it reduces noise.
