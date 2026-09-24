# 04 — The Run Directory

Everything a Run writes goes to one directory; the Manager owns two files in it; rloop keeps the
Manager's files as the Manager left them. `ADR-0003` is the decision behind the Checkpoint and its
threat model.

## Where it is

**DIR-1** `--run-dir PATH` names the Run Directory. The path MUST NOT exist when rloop starts;
rloop MUST create it with one atomic `mkdir` (not `mkdir -p` on the last component) and MUST exit
2, spawning nothing, when that fails — the directory already exists, or its parent does not. *An
existing directory is yesterday's Run; a Finished File found in it would end today's with
yesterday's report. There is no emptiness scan and no resume.*

**DIR-2** When `--run-dir` is omitted, the Run Directory MUST be
`<toplevel>/.rloop/runs/<UTC timestamp>-<pid>/` under the git toplevel — the timestamp precise
enough that two Runs of one Sequence, which share the pid, get distinct names — and rloop MUST
ensure
`<toplevel>/.rloop/.gitignore` exists holding exactly the two bytes `*` and a newline before
creating it, rewriting a file whose bytes differ. *The directory ignores itself: no tracked file
changes, `.git` is never touched, and it works in a worktree, where `.git` is a file.* In a
Sequence each Run gets its own directory this way and `--run-dir` is a usage error (`SEQ-3`).
*Amended 2026-09-23 (`rl-exact-bytes-nul-gitignore-pjc`): the rule used to say `containing the
single line *`, which a check by eye satisfies for a pre-existing file of `*` followed by two
newlines and for `*` with no newline at all; both are now rewritten. The bytes follow the set's
convention for the files it writes, as `RUN-21` says of its records: `Every line of either
record ends with a newline, the last one included`.*

**DIR-3** A Run Directory MUST be used by exactly one Run. There is no flag to reuse one.

## What is in it

**DIR-4** The Run Directory MUST hold exactly these names, and an Implementation MUST NOT add
others:

| file | written by | when |
|---|---|---|
| `task.md` | the Manager | the pick, and any judge call that continues the Run |
| `task-<r>.md` | rloop | the brief Round `r` ran against (`DIR-5`) |
| `finished.md` | the Manager | the call that ends the Run |
| `manager-pick.out`, `manager-pick.err` | rloop, from the pick's stdout and stderr | the pick |
| `manager-judge-<r>.out`, `manager-judge-<r>.err` | rloop, from the judge call's stdout and stderr | Round `r` |
| `implementer-<r>.out`, `implementer-<r>.err` | rloop, from the Implementer's stdout and stderr | Round `r` |
| `feedback-<r>-<reviewer>.md` | rloop, from the Reviewer's stdout, or rloop's own when the Reviewer was not called (`RUN-15`) | Round `r`, one per Reviewer (`fable`, `opus`, `astra`, `sol`) |
| `reviewer-<r>-<reviewer>.err` | rloop, from the Reviewer's stderr; empty when it was not called | Round `r` |
| `probe-pick.out`, `probe-pick.err` | rloop, from the availability probe's stdout and stderr | before the pick (`RUN-21`) |
| `probe-pick.md` | rloop | before the pick: one `<seat>:<verdict>` line per Seat (`RUN-21`) |
| `probe-<r>.out`, `probe-<r>.err` | rloop, from the availability probe's stdout and stderr | Round `r`, before the Panel (`RUN-21`) |
| `probe-<r>.md` | rloop | Round `r`: one `<seat>:<verdict>` line per Seat (`RUN-21`) |
| `rejected-<r>-task.md`, `rejected-<r>-finished.md` | rloop | the Checkpoint (`DIR-6`) |
| `session` | rloop | the pick: the Manager's session id, one line |

Every agent's standard output, and the probe's, goes to its file entire and unmodified; rloop
MUST NOT interleave its own text into any of them. rloop reads some of them and changes no byte of
any: under `--manager codex` the pick's standard output carries the Manager's session id, which
`RUN-16` tells rloop to take from there, and the probe's standard output carries the lines `RUN-21`
reads. `probe-pick.md` and `probe-<r>.md` are rloop's own writing, not an agent's, as is a Feedback File for a Reviewer that was never called (`RUN-15`).
*The Implementer's `.out` is what the Manager reads about a failed
Implementer (`RUN-14`), and `feedback-*.md` is what it reads about the Panel.* *This sentence read
"entire and unparsed" until 2026-09-20; the word banned a reading that `RUN-16` now requires,
where what the rule protects is the file's bytes.*

A Run refused at the pick (`RUN-22`) MUST leave the Run Directory holding `probe-pick.out`,
`probe-pick.err` and `probe-pick.md` and nothing else: no `session`, which `RUN-16` writes for a
pick and there was none, and no Manager output.

**DIR-5** After the pick and after every judge call whose verdict is *next Round*, rloop MUST copy
`task.md` to `task-<r>.md` where `r` is the Round about to run. `task-<r>.md` is the **snapshot**:
the brief Round `r` ran against, the baseline `RUN-12` compares against after Round `r`, and the
history of the Run's briefs, which nothing else keeps since the Manager rewrites `task.md` in
place.

## The Checkpoint

**DIR-6** At the two Checkpoints of a Round `r` — after the Implementer and after the Panel
(`RUN-7`) — rloop MUST:

1. if `task.md` is not byte-identical to `task-<r>.md`: move `task.md` to `rejected-<r>-task.md`,
   copy `task-<r>.md` to `task.md`, and log one line to standard error;
2. if `finished.md` exists: move it to `rejected-<r>-finished.md` and log one line.

A move that finds `rejected-<r>-*` already present (the second Checkpoint of the same Round) MUST
overwrite it. A restore MUST create `task.md` anew — unlink, then write — rather than write through
the existing path. *A `rejected-*` file is evidence, not garbage: an Implementer's own `STATUS:
blocked` is information (`PRM-2` tells the Manager to read it), and deleting it would lose it.*
`Rloop.checkpoint_non_interference` proves a Run with interference exits and spawns exactly as one
without; `Rloop.checkpoint_off_believes_forgery` is the forged `done` that ends a Run with exit 0
when the Checkpoint is off.

**DIR-7** The no-decision baseline is the snapshot (`RUN-12`), never `task.md` as the Implementer
left it. `Rloop.ticked_is_no_decision` and `Rloop.checkpoint_off_reads_edit_as_rewrite` are the
pair: an Implementer's edit to its brief, followed by a Manager that writes nothing, is no decision
— and, without the Checkpoint, would read as a Manager rewrite and start a second Round.

**DIR-8** When a Checkpoint cannot do its work — `task-<r>.md` is missing, the Run Directory is
gone, `task.md` cannot be replaced — rloop MUST exit 2. It MUST NOT reconstruct a Run Directory or
rebuild a snapshot from memory. *An Implementer running `git clean -fdx` is a plausible accident
and the Run it happened to is over.*

**DIR-9** **The threat model is a cooperative model making a mistake** — a ticked checkbox in the
brief, a completion report written where the Manager's goes — and the Checkpoint is sized to it.
Out of scope, and an Implementation MUST NOT be held to them: a forged or edited `task-<r>.md`, a
symlink planted in the Run Directory, one Reviewer overwriting another's Feedback File, and a
change made and reverted between two Checkpoints. *Every agent runs as the same user with the
directory's path in its environment; an adversary there is an adversary with the user's rights, and
`ADR-0003` records why the Specification says so rather than imply integrity it does not have.*

**DIR-10** Every agent prompt MUST carry the sentence `PRM-5` states telling the agent not to write
under the Run Directory except where the prompt names. The Checkpoint is for when a model does not
listen; the sentence is so that it usually does.
