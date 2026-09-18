# The checkpoint repairs accidents and does not resist an adversary

**Status:** accepted (2026-09-17, after suggestions from Fable and gpt-6-astra)

The Task File and the Finished File belong to the Manager, but every agent runs as the same user
with the run directory's path in its environment, and the Implementer runs with permissions
bypassed. Three accidents were found before any code existed: a reused run directory whose old
Finished File ends the new Run with exit 0, an Implementer that writes its own completion report
where the Manager's goes, and an Implementer that ticks checkboxes in its brief so the Panel reviews
against a brief it changed.

rloop therefore keeps the brief each Round ran against as `task-<round>.md` and runs one checkpoint
twice per Round — after the Implementer and again after the Panel — that restores `task.md` from it
and moves anything a non-Manager wrote over the Manager's files to `rejected-<round>-*`, where the
judge prompt tells the Manager to read it as evidence. The run directory must not exist at start and
is created with one atomic `mkdir`; there is no resume. When the checkpoint cannot restore, the Run
exits 2.

**The threat model is a cooperative model making a mistake.** A forged snapshot, a symlink planted
in the run directory, one Reviewer overwriting another's Feedback File, and a change made and
reverted between checkpoints are all out of scope, and the specification says so rather than imply
integrity it does not have.

## Considered options

- **Exit 2 on any interference.** Rejected: a ticked checkbox would cost a four-hour Run.
- **A baseline held outside the run directory, or a verified digest** (astra). Rejected as defence
  against an adversary the threat model excludes; it is the first thing to add if that changes.
- **Invalidating a Panel whose brief changed under it** (astra). Rejected for the same reason; the
  Manager is told and judges.
- **Structural separation** — hidden paths, permissions, a copy for the Implementer. Permissions do
  not bind a bypassed agent, a hidden path breaks the environment contract the Conformance Suite's
  fakes rely on, and a copy is as editable as the original.
- **A run directory outside the repository** (astra). Rejected: agents without bypass would need an
  extra grant in their command line. It lives at `.rloop/runs/…` and rloop writes `.rloop/.gitignore`
  holding `*`, so it ignores itself in any worktree without touching `.git`.
- **A per-worktree lock.** Rejected: one Run per working tree is documented as the caller's job, and
  a lock left by a killed process costs more than it saves.
