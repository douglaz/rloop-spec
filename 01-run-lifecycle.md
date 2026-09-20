# 01 — The Run

A Run is one task: from the Manager picking it to the Manager declaring it finished. This document
is the control flow between agent calls. What each call looks like is `02-agents.md`; what it is
told is `03-prompts.md`; where its files go is `04-run-directory.md`; how Runs chain is
`05-sequence.md`.

```text
pick ──► decide ──► [ Round: Implementer ─ Checkpoint ─ Panel ─ Checkpoint ─ judge ──► decide ]* ──► exit
```

## Starting

**RUN-1** rloop MUST run inside a git working tree and MUST exit 2 before spawning any agent when
`git rev-parse --show-toplevel` fails. Everything below assumes the tree.

**RUN-2** rloop MUST record the **base** once, before the pick: the commit `HEAD` names, or the
ref `--base` supplies. The base is what Reviewers are told to diff against (`PRM-4`) and is never
recomputed during the Run. *A base recomputed per Round would hide the earlier Rounds' changes from
the later Rounds' Reviewers.*

**RUN-3** rloop MUST record, once before the pick, the paths `git status --porcelain` lists, as the
**dirty-at-start list** (`PRM-2`'s `{{DIRTY_AT_START}}`). A lone Run MAY start on a dirty tree; a
Run inside a Sequence MUST NOT (`SEQ-4`). *The list is how the Manager tells the caller's unrelated
edits from the Implementer's work when it commits (`SEQ-8`). A path the Run itself dirties after
the list is taken — the tracker file the Manager claims the task in at the pick — is neither the
caller's nor the Implementer's; it is the Manager's, and `SEQ-8` has the Manager commit it with
the accepted work. A Sequence that finds it uncommitted at the next Run stops there (`SEQ-4`),
which is the check working, not a defect.*

**RUN-4** rloop MUST create the Run Directory (`DIR-1`–`DIR-3`) before the pick and MUST NOT
create any other file outside it, save the `.rloop/.gitignore` `DIR-2` names.

## The pick

**RUN-5** The Run MUST begin with exactly one Manager call — the **pick** — using `AGT-3`'s command
line and `PRM-1`'s prompt, with the caller's instruction, if any, rendered into it. The Manager is
expected to leave behind a Task File, or a Finished File, or both; what rloop does with what it
finds is `RUN-11`.

**RUN-6** After the pick, when the verdict is *next Round*, rloop MUST copy the Task File to
`task-1.md` (`DIR-5`) and start Round 1.

## The Round

**RUN-7** A Round `r` (from 1) MUST consist of, in this order and nothing else:

1. one Implementer call (`AGT-5` or `AGT-6`, `PRM-3`), started fresh — no session is carried from
   any earlier Round or earlier Run;
2. the Checkpoint (`DIR-6`);
3. the Panel: all four Reviewer calls (`AGT-7`–`AGT-10`, `PRM-4`), started concurrently and all
   waited for;
4. the Checkpoint again;
5. one Manager call — the **judge** — resuming the pick's session (`AGT-4`, `PRM-2`);
6. the decision (`RUN-11`).

*Fresh Implementers are the design: a brief that only makes sense with the previous Round's
conversation is a bad brief, and `PRM-2` tells the Manager so.*

**RUN-8** The Panel's Reviewers MUST be spawned so that none waits for another to finish, and rloop
MUST wait for every one of them before the Checkpoint that follows. Each Reviewer's standard output
is its Feedback File (`DIR-4`).

## What the Manager leaves behind

**RUN-9** The **Finished File** is `finished.md` in the Run Directory. Its first line MUST be read
as one of exactly four cases:

| first line, byte for byte | case |
|---|---|
| `STATUS: done` | done |
| `STATUS: blocked` | blocked |
| `STATUS: idle` | idle — valid at the pick only; after a Round it is the fourth case |
| anything else, or an empty file | other |

The line is the bytes up to the first newline, compared exactly: no trimming, no case folding, no
CRLF tolerance. *The Manager writes what `PRM-2` tells it to write; a tool that tolerates
variations is a tool with a second grammar nobody wrote down.* Nothing after the first line is
read by rloop; it is for the caller (`RUN-10`).

**RUN-10** rloop's exit status MUST be:

| exit | meaning |
|---|---|
| 0 | the Finished File says done |
| 1 | the Finished File says blocked |
| 3 | the Finished File says idle: the Manager found nothing to pick and changed nothing |
| 2 | everything else: the Manager failed or made no decision, the Finished File's first line is not one of the three, the round cap was reached, no Reviewer survived a Panel, the run directory or the tree refused the Run, rloop was interrupted, or a usage error |

On 0, 1 and 3 rloop MUST write the Finished File, entire, to standard output and nothing else to
standard output. On 2 standard output MUST be empty. Progress and diagnostics go to standard error
and their wording is not specified. *A caller — a human, a skill, a Sequence — reads the report from
one place and the outcome from one number.*

## The decision

**RUN-11** After every Manager call rloop MUST decide by the following table and nothing else,
reading the columns left to right and stopping at the first that settles it. "Task File vs.
snapshot" compares `task.md`'s bytes with the snapshot the Manager was given — `task-<r>.md` after
Round `r`, nothing at the pick — and "cap reached?" is whether the Round just judged is
`--max-rounds` (at the pick: whether `--max-rounds` is 0). The Finished File wins over a rewritten
brief: a Manager that wrote both has finished.

<!-- formal: Rloop.Render.decisionTable -->
| call | Manager exit | Finished File first line | Task File vs. snapshot | cap reached? | verdict |
|---|---|---|---|---|---|
| pick | non-zero | none | absent | no | **exit 2** |
| judge | non-zero | `STATUS: done` | rewritten | no | **exit 2** |
| pick | 0 | `STATUS: done` | written | no | **exit 0** |
| pick | 0 | `STATUS: blocked` | written | no | **exit 1** |
| pick | 0 | `STATUS: idle` | written | no | **exit 3** |
| pick | 0 | anything else | written | no | **exit 2** |
| judge | 0 | `STATUS: done` | rewritten | no | **exit 0** |
| judge | 0 | `STATUS: blocked` | rewritten | no | **exit 1** |
| judge | 0 | `STATUS: idle` | rewritten | no | **exit 2** |
| judge | 0 | anything else | rewritten | no | **exit 2** |
| pick | 0 | none | absent | no | **exit 2** |
| pick | 0 | none | written | no | **next Round** |
| pick | 0 | none | written | yes | **exit 2** |
| judge | 0 | none | absent | no | **exit 2** |
| judge | 0 | none | unchanged | no | **exit 2** |
| judge | 0 | none | rewritten | no | **next Round** |
| judge | 0 | none | rewritten | yes | **exit 2** |
<!-- /formal -->

The table is rendered from `Rloop.decide` in `tools/formal/Rloop/Loop.lean`, which is total: a
combination the table does not show is one an earlier column settled. "Manager exit non-zero"
includes a timeout (`AGT-14`) and a session that could not be resumed (`RUN-16`). *A Manager that
wrote `STATUS: done` and then crashed is a Manager whose report was not finished: exit 2, the file
left in place for a human.*

**RUN-12** When a judge call exits 0, leaves no Finished File, and leaves `task.md` byte-identical
to `task-<r>.md`, the Manager made **no decision** and rloop MUST exit 2 rather than start another
Round. *Without this a Manager that ends its turn with a question re-runs the Implementer on the
brief it already built.* `Rloop.no_decision_ends` proves it; `Rloop.no_decision_off_burns` is the
Run that burns every Round without it.

**RUN-13** `--max-rounds N` (default 10) MUST bound the Implementer calls of a Run: after judging
Round `N`, a verdict of *next Round* becomes exit 2. `Rloop.implementers_le_maxRounds` proves the
bound for every Behaviour; `Rloop.cap_off_overruns` shows the second Implementer that runs without
it. On exit 2 for the cap rloop SHOULD print the Manager's session id to standard error, so that a
human can `claude --resume` it and ask why.

**RUN-14** An Implementer call that exits non-zero or times out MUST NOT end the Run by itself:
the Round MUST continue to the Panel and the judge, whose prompt names the Implementer's log
(`PRM-2`). *The Manager decides whether half-built work is worth another Round or a `blocked`; the
tool cannot.* `Rloop.implementer_failure_ends_nothing` proves that replacing every Implementer
outcome changes neither the exit code nor the number of Implementers run.

**RUN-15** A Reviewer call that exits non-zero or times out MUST leave its Feedback File holding
the line `REVIEWER FAILED (exit <status>)` — appended to whatever it wrote — and the Round MUST
continue. When **every** Reviewer of a Panel failed, rloop MUST exit 2 without calling the judge.
*One Reviewer down is a degraded Panel the Manager can weigh; four down is a broken environment.*
`Rloop.panel_none_aborts` and `Rloop.panel_abort_off_judges` are the pair.

**RUN-16** The Manager MUST be one session for the whole Run: the pick establishes it, every
judge call resumes it (`AGT-3`, `AGT-4`), and rloop MUST write its id to the `session` file
(`DIR-4`). Under `--manager claude` the id is one rloop chose before the pick. Under `--manager
codex` it is the `thread_id` of the first `thread.started` event on the pick's standard output,
which rloop reads for this and for nothing else (`DIR-4`). A pick that reports no id, and a judge
call whose resume fails, are each a failed Manager call: exit 2. *Until 2026-09-20 this read "the
pick MUST start the Manager's session under an id rloop chose", which only one of the two presets
can do: `codex` has no flag that sets a session id and mints its own.*

## Decisions the Manager may not make alone

**RUN-19** A Run MUST end `blocked`, never `done`, when the task turns on a point the
repository's specifications or instructions leave ambiguous or contradictory — two readings that
lead to different behaviour — and the Manager MUST NOT choose a reading. The Finished File names
the document and the passage, the readings, and the clarification the Manager recommends; the
prompts (`PRM-1`, `PRM-2`) say so at the pick and at the judge. *A clarification is the
specification owner's to make. A Manager that picks a reading buries a decision in a brief, and
the next Run inherits it as fact; a blocked Run stops a Sequence (`SEQ-6`) exactly so that the
human is asked first.*

**RUN-20** An implementation decision the specifications leave to the implementer — a choice of
how, not of what — that a brief must settle MUST NOT be made by the Manager alone: the prompts
tell it to put the question and the options to two advisers, `fable` and `astra`, read-only, by
running the two command lines `PRM-1` states, and to record the question, the answers and its
choice in the Task File. When the two advisers disagree the Manager puts the same question to two
more, `opus` and `sol`; when the four do not settle it, the question was not an implementation
decision and the Run ends `blocked` as under `RUN-19`, the answers in the report. A choice the
brief does not need to settle is the Implementer's. *This
is a Consultation, not a Panel: rloop does not run it, the Manager does, in its own session,
which is why it costs the control flow nothing and why only a live Run can show it happens
(`CNF-22`).*

## What a Run leaves

**RUN-17** On every exit rloop MUST leave the Run Directory as it is: no cleanup, no deletion, on
success or failure. It is the evidence.

**RUN-18** rloop MUST NOT commit, and MUST NOT tell an Implementer whether to commit: the
repository's own instructions decide that. The Manager's obligations at `done` are `SEQ-8`.
