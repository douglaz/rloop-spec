# rloop refuses a seat it cannot fill and never substitutes

**Status:** accepted (2026-09-22)

`ADR-0006` decided that rloop reads a vendor's quota report and fails open. That decision was taken
for the Panel, where a Reviewer that cannot answer is recorded in place and the Round carries on
with the rest. It left the Manager's and the Implementer's Seats unguarded, and the cost showed
itself the same week: a Run started with the defaults sat for seven minutes with
`manager-pick.out` and `manager-pick.err` both empty, against a model the Probe reports as
`Current week (Fable): 100% used`, and would have sat for the full hour `--manager-timeout` allows
before exiting 2 having written nothing.

A Panel is a group, so removing a member leaves a Panel. A Seat is not. There is one Manager, it
judges every Round, and `SEQ-8` is what holds it to leaving the tree clean.

## The decision

The Probe runs before the pick as well as before each Round's Panel, and records a verdict for
every Seat. rloop refuses to start — exit 2, no agent spawned — when the Manager's Seat, the
Implementer's Seat, or every Reviewer's Seat is recorded `unavailable`, naming the Seat, the model
and the reset time the report gave. It never substitutes another model.

Substitution was the obvious alternative, and rloop-spec#3 states the reason it was rejected:
`Removal is honest; substitution needs to be asked for.` A Sequence that quietly moved from one
judge to the next would produce Runs judged by different models with nothing in the record saying
which. An operator who wants the other model passes `--manager-model`, which the refusal message
tells them to do.

Refusing spawns no agent even though the Probe has run, because `CONTEXT.md` already settles that
the Probe is `Not an agent`.

## Why the Implementer's Seat too, and why that is not RUN-14

`RUN-14` says `An Implementer call that exits non-zero or times out MUST NOT end the Run by
itself`, and `Rloop.implementer_failure_ends_nothing` proves it. That governs a call that was made.
This refusal happens before the pick, where there is no call, no Task File and no Manager
judgement to overrule: the Run does not begin, rather than ending early.

The waste it avoids is the largest in the tool. `--implementer-timeout` defaults to 14400 seconds
and `--max-rounds` to 10, so an Implementer Seat that cannot answer is worth up to forty hours of
empty Rounds, each one followed by a Panel reviewing a Round in which nothing happened.

## The Reviewers are judged on a stale reading, deliberately

Every other guard here reads a Probe next to the calls it guards: the one before the pick guards
the Manager, called seconds later, and the Implementer, called minutes later; a Round's guards the
Panel and the judge that follow it. The Reviewers are the exception. An Implementer may run for
hours between the pick and the Panel, and a weekly limit resets at a fixed time, so a Reviewer
recorded unavailable at the pick may be able to answer by the time the Panel starts.

Refusing anyway is accepted because it changes no verdict. `RUN-15` already requires that
`When **every** Reviewer of a Panel is down — failed, or not run — rloop MUST exit 2 without
calling the judge`, and a Reviewer recorded unavailable is not run, so the same exit is reached
either way. The only difference is whether an Implementer Round was paid to reach it. Being wrong
costs a Run the operator restarts; being right saves hours.

## Consequences

- **The Probe is one concept with two call sites.** `CONTEXT.md`'s entry widens to cover the pick
  and the Seats, and `preflight` leaves its avoided-aliases list: the word was banned for implying
  a single check before everything, which is now exactly what the call before the pick is.
- **`Seat` becomes a glossary term.** The Specification was already using it in `ADR-0006` and in
  `07-open-findings.md` without defining it, and a normative rule about Seats cannot be the first
  place a reader meets the word.
- **The Probe's record is keyed by Seat, not by Reviewer.** A verdict is a property of a model
  family, so reading a Reviewer's line as the Manager's answer works only while the two share a
  model. The record therefore carries one line per Seat, and rloop writes down every verdict it
  acts on. This reopens the byte contract `rl-vcq` already asks about, which is why the two are
  settled together rather than in sequence.
- **A Manager that runs out mid-Run is caught at the next judge**, from the Probe the Round already
  runs, instead of after another `--manager-timeout` of silence. `RUN-11` decides
  `After every Manager call`, so a judge call that was never made is outside its table and the
  table does not change.

## Rejected

- **Substitute the counterpart model**, fable to opus. Keeps a Sequence draining overnight, which
  is the one case an operator flag cannot cover, but it changes which model judged the work without
  saying so. Rejected on rloop-spec#3's wording above.
- **Split the rule on whether anyone is watching** — refuse for a lone Run, substitute under
  `--auto`. This makes the identity of the judge depend on a flag about unattendedness, which is
  the least predictable place to put it.
- **Guard the Implementer on every Round, not only at the pick.** It would need a second Probe at
  the top of each Round, because the existing one is placed after the Implementer and cannot move
  without going stale for the Panel. The Round-level version also has to answer what happens next,
  and the only answer compatible with `RUN-14` is to skip the call and let the Round continue to a
  Panel with nothing to review. Available on its own merits; not this decision.
