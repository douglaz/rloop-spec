# A Consultation calls every available adviser at once

**Status:** accepted (2026-10-02)

Until this decision a Consultation was serial. The Manager asked a first pair of advisers, `fable`
and `astra`; an adviser that did not answer was replaced by its counterpart in the other pair,
`fable` by `opus` and `astra` by `sol`, and not by the next name on the roster; a model that did
not answer was not called again for the rest of the Run; and when the two that answered disagreed,
the same question went to the advisers that remained, inside a total budget chosen beforehand.

That policy needed three things the Manager had to get right: an order of calls, a counterpart for
each adviser, and a memory of who was excluded that lasted the whole Run. Each raised questions
the text did not answer. By 2026-10-02 they had left six open points with two readings each —
among them when the budget's clock starts, whether a Probe record no Consultation read still
excludes a model, and what replaces an adviser whose counterpart is already gone — and `CNF-22`,
which mapped the live observations to the policy obligation by obligation, grew a new edge case
with every fix: four Runs on that one day, `4a8bc1d`..`3975a71`.

The order did more than raise questions. Under serial escalation, on the reading that any two
agreeing answers settle, the order of calls could pick the outcome. With `fable` answering A and
`astra` answering B, asking `opus` first and getting A settled A; asking `sol` first and getting B
settled B. The same four advisers holding the same four positions gave two results.

## The decision

A Consultation calls every available adviser at once. `RUN-20` owns the rule; its shape is:

- **Every available adviser, together.** The Manager calls each of `fable`, `opus`, `astra` and
  `sol` that the Consultation's relevant Probe record does not read `unavailable`, and starts all
  the calls together, each bounded through completion or termination.
- **No memory within the Run.** A model that did not answer in an earlier Consultation is called
  again, and a model a Probe read `unavailable` is called again once a later relevant record no
  longer reads it so. This is what `RUN-21` already does for the Panel, probing every Seat again
  before each Round's Panel.
- **The unique leading position of at least two settles.** Once every call has ended, the position
  held by more answering advisers than any other, and by at least two, is the choice. Two distinct
  models must still answer.
- **Ties block.** A tie, or fewer than two answers, leaves the choice unsettled and the Run ends
  `blocked`.
- **A one-vendor win is recorded rather than blocked.** When neither model of one vendor answers
  and the other vendor's two agree, the choice settles and the record says the Consultation was
  single-vendor. When the settling position is held by one vendor's answers only while the other
  vendor answered and dissented, the choice settles and the record says so.

With every call started together there is no order for the Manager to choose, so the order cannot
choose the outcome; with every available adviser called there is no counterpart; and with nothing
carried from one Consultation to the next there is no per-Run exclusion to keep.

## The trade-off

Up to twice the adviser calls when the first two would have agreed: four calls where two would
have settled it. In exchange the Manager chooses no call order, there are no counterparts, and no
model is excluded for the rest of a Run. A model that hangs costs one bounded call in each
Consultation, running beside the others rather than ahead of them, so it adds nothing to the
Consultation's length beyond its own bound.

## What this does not change

`RUN-21`'s Probe, the Panel, and `ADR-0008`. rloop still runs no Consultation: the Manager does,
in its own session. What counts as an answer, the quorum of two distinct models, and the
Manager's judgment on hedged prose are as they were.

## Rejected

- **The pair-and-counterpart policy**, described at the top: a first pair, replacement by
  counterpart, exclusion for the rest of the Run, and escalation to the remaining advisers on a
  disagreement. It saves calls whenever the first two advisers agree, which is its whole merit and
  the reason a later reader may be tempted to restore it. It is recorded here so that they do not:
  the saving was paid for with the call order, the counterparts and the per-Run exclusion, and
  those three produced the six open points and the four Runs of `CNF-22` edge cases above, and let
  the order of calls decide a choice the advisers had split on.
