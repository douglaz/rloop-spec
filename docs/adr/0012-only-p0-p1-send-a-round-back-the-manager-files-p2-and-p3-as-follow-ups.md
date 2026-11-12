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
