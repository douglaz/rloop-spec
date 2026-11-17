# Only P0/P1 send a Round back; the Manager files P2 and P3 as follow-ups

**Status:** accepted (2026-11-11, `rl-uoso`)

Amend `PRM-1`, `PRM-2` and `PRM-4`. The owner's direction was: "we should make it focus on
fixing high severity/p0 and leaving medium/minor ones as follow up beads". Here that means P0
and P1 for high severity, P2 for medium and P3 for minor. `F32` records the measurement that
motivated the change, its limits and the still-open rollout evaluation.

## The decision and its homes

`PRM-4` owns the scale: `Start each with its severity — [P0], [P1], [P2] or [P3] — then file:line
evidence and what you verified, by reading or by running.` `PRM-2` owns judgment: `Rate every
finding yourself on the Reviewers' scale, P0 to P3`; `a Reviewer's tag is evidence, not a
verdict`. Neither agent sees the other's prompt, so `PRM-2` repeats the scale for the Manager:
`The rest of the Reviewers' scale`. Findings remain advice, as in `ADR-0011`, rather than votes on a
Panel question.

`PRM-2` owns acceptance: `Send back only a P0 or P1 defect that this Run's changes since
{{BASE}} introduce or that leaves the brief unmet; a P2, a P3 or a suggestion never sends a
Round back.` The base covers the whole Run (`RUN-2`: `The base is what Reviewers are told to
diff against` and `is never recomputed during the Run`).

The owner ruled on P2, verbatim: "I would suggest leaving P2 as beads because solving them may
generate more Px". Repairing a lower-severity defect adds work and a fresh chance of defects
even when a higher-severity repair already requires another Round. `PRM-2` carries that choice:
`A P2 or P3 you accept is a follow-up: it is never repaired in this Run, not even when the Round
goes back for a P0 or P1, the next brief lists it, and it is filed when the Run ends.`

Asked "What should happen to purely cosmetic P3 findings (nits like a wrong comment or
wording)?", the owner picked "One bead per nit", whose text was "File each P3 as a priority-3
bead labelled review-nit, which drains skip unless you ask." This explicitly amends the
2026-09-30 filing rule (`rl-no-cosmetic-beads-z0q1`). Its bar remains the distinction between
P2 and P3, rather than a reason to discard P3. The historical note under `PRM-2` is retained.

`PRM-2` options A and B own filing and retaining the list, including on `STATUS: blocked`;
option A says `one issue per distinct defect` and `First search the open issues`.
For suggestions, `An accepted suggestion is not filed: it is listed once in the report.`
`PRM-1` owns picking: `Do not pick a task labelled review-nit unless the caller's instruction
names it or asks for nits.` The exit-2 recovery instructions are in `README.md`, *Using rloop*;
`F10` records why a promised follow-up needs that recovery path.

## Why prompt text

The rb-lite history in `00-overview.md`, *Where it comes from*, records a tool that parsed
Reviewer tags and applied a severity floor. A floor in the executable would restore that
judgment to the tool, let a tag decide a finding's fate and prevent the Manager from weighing
its evidence. `OVR-1` instead states `It MUST NOT parse a Reviewer's output, an Implementer's
output, or any part of the Finished File beyond its first line.` There is no `--min-severity`
flag: rating and disposition are the Manager's judgment under `PRM-2`.

Markdown remains the prompt home (`ADR-0001`), with regenerated fixtures under `CNF-12`:
`For each role the recorded prompt argument equals the fixture in conformance/fixtures/prompts/
rendered by PRM-6 with the values the suite knows`. That checks literal delivery, not whether a
live Manager follows the policy. No semantic severity parser or severity tests are added.
The decision table and formal model remain the control-flow home (`ADR-0002`); agent judgment
is outside that model. `F32` leaves the policy's effect for live measurement.

## Amended 2026-11-17: the owner's words, a recorded rating, the last Round

An audit of 2026-11-17 read this set against the owner's rule, whose scale is:

> - P0: money or data loss, a secret, security, core function broken, or the brief fundamentally failed.
> - P1: blocks acceptance: wrong behaviour in a supported case, a brief requirement unmet, a check that cannot
>   fail, or a requirement made false. Any money, secret or data-loss defect on a reachable path is at least P1.
> - P2: a real defect that does not block.
> - P3: changes no behaviour, requirement or check.
>
> The judge re-rates; lowering a P0/P1 needs file:line evidence, and raising one to P0/P1 names the clause.

Three amendments follow, all to prompt text:

- **The owner's P0 and P1.** `PRM-4` and `PRM-2` now carry the owner's P0 and P1 lines word for
  word; `PRM-4`'s P0 line reads `money or data loss, a secret, security, core function broken, or
  the brief fundamentally failed`. The old P0 limited broken core function to a crash or corruption. The old P1 added a test
  or gate that fails for the wrong reason, a contradictory requirement and misdirected money, which
  widened it beyond the owner's text; `F34` records raises that rested on a clause of that kind and
  did not hold. P2 and P3 keep their examples, which illustrate the owner's lines without widening
  them.
- **A recorded rating.** `PRM-2` asked for evidence and clauses (`when you rate a Reviewer's P0 or
  P1 lower, give the reason with file:line evidence`) but gave them nowhere to go, so neither could
  be checked after the Run. Every judge reply now ends with the ratings: each finding's Reviewers
  and tags, the Manager's rating, the evidence for a lowering or the clause for a raise, and the
  clause every P0 or P1 meets. rloop already keeps that reply: `DIR-4` lists
  `manager-judge-<r>.out` as written by `rloop, from judge attempt 1's stdout and stderr`.
- **The last Round.** Nothing told the Manager that the Round it judged was the last. A Manager
  that chose B there ended the Run with exit 2, since `RUN-13` says `a verdict of *next Round*
  becomes exit 2`, and the follow-ups its brief listed were filed only if the caller rebuilt them
  from the Run Directory. `PRM-2` now has the last Round end through option A, and the follow-ups
  filed either way. It ends blocked when the Round surfaced an ambiguity, as `RUN-19` requires
  `when the task turns on a point the repository's specifications or instructions leave ambiguous
  or contradictory`; when a choice is unsettled, since `RUN-20` says `A choice the advisers leave
  unsettled MUST end the Run`; or when a P0 or P1 that sends a Round back remains, naming each
  one. It ends done otherwise. A blocked last Round leaves the task open in the tracker, as the
  cap's exit 2 did before. The one exception is option A's own: `SEQ-8` says `A hook failure that
  needs a code change is a finding like any other and goes back through a Round`, so a commit that
  needs a code change still chooses B, and in the last Round that Run ends at the cap's exit 2 as
  before. The same exit 2 still catches a Manager that does not listen.

The same day the owner capped a change to a project's own test tooling at two review Rounds:
later findings become follow-ups, except one that touches money, machine deletion or secrets, or
a check that can pass when it should fail. Applying it is the caller's choice of
`--max-rounds`, so it lands as guidance in `README.md`, *Using rloop*. The default stays 10.

Rejected on the way:

- **The ratings in the next brief.** Option B's brief goes to an Implementer that
  `will not see the feedback` (`PRM-2`), and to Reviewers who would read the Manager's ratings
  before forming their own.
- **A ratings file in the Run Directory.** `DIR-4` says `The Run Directory MUST hold exactly
  these names, and an Implementation MUST NOT add others`. A new name needs a placeholder, a
  Checkpoint rule and conformance items, for a record the kept judge output already holds.
- **A tooling preset or a lower default.** rloop cannot tell what a task touches, and `OVR-1`
  says `It MUST NOT parse a Reviewer's output, an Implementer's output, or any part of the
  Finished File beyond its first line.` The caller knows, so the caller sets `--max-rounds`.
