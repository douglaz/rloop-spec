# Wait for the same Manager inside a Round

**Status:** accepted (2026-10-22)

Amend `RUN-5`, `RUN-7`, `RUN-11`, `RUN-21` and `RUN-22`, add `RUN-24`, and amend `AGT-1`, `AGT-2`,
`AGT-4`, `AGT-14`, `AGT-15`, `DIR-4` and `OVR-1`: a Round checks before its Panel and again before
its judge, waits on session exhaustion, and retries a judge attempt the CLI cut off. `F29` holds the
owner's supplied evidence and the measured suite record. This reopens the Round portion of the
immediate-refusal rule in `RUN-22`, `At the pick rloop MUST refuse immediately, without waiting for
reset or retrying`. The Round portion of `rl-8ee8`'s item 4, "Refuse, do not wait", is
reopened; the pick keeps it.

A wait changes when, not who. It preserves `ADR-0008`'s refusal to substitute another model. A
judge refused hours after spawn cannot be protected by a check before spawn alone. The recognised
line is a CLI report (the supplied transcripts identify its model as `<synthetic>`), though byte
matching cannot authenticate its author. `RUN-24` owns the narrow trigger and file guard.

The judge remains one logical call (`RUN-7`, `RUN-11`); its terminal attempt supplies the result and
the unchanged decision table reads that result. `AGT-15` says `A call is complete only once its
process group has been reaped that way`: the output is read `only after that`. The wait's requested
sleeps share one Round ledger; slow checks extend wall time. Numbered captures preserve every check
and attempt, while the Panel's copy keeps the Consultation's evidence (`RUN-20`) stable.

## Rejected

- Waiting at the pick: a later Run's refusal must still stop a Sequence.
- Retrying the pick: it establishes a session and chooses work; the retry applies to the judge.
- A retry counter: paid sleeps already bound attempts under the shared budget.
- A wall-clock deadline: checks, calls and scheduling delays do not spend the sleep ledger.
- An off switch: both duration options have minimum 1 and waiting is the default policy.
- The narrower trigger proposed during review: the adopted byte prefix and file guard in
  `RUN-24` apply without requiring exit 1, empty stderr, a reset-shaped suffix or extra character
  exclusions.

## Limits

No live Run has yet demonstrated the wait. rloop-bash catching up is separate work. The supplied
readings, thresholds and fail-open policy remain `RUN-21`'s; there is no new prompt or agent
command line, and no change to `Rloop.decide`.
