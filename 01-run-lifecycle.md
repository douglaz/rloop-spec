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
**dirty-at-start list** (`PRM-2`'s `{{DIRTY_AT_START}}`). A lone Run MAY start on a dirty tree;
`SEQ-4` owns the clean-tree check for a Run inside a Sequence. *The list is how the Manager tells
the caller's unrelated edits from the Implementer's work when it commits (`SEQ-8`). A path the Run
itself dirties after the list is taken — the tracker file the Manager claims the task in at the
pick — is neither the caller's nor the Implementer's; it is the Manager's, and `SEQ-8` has the Manager commit it with
the accepted work. A Sequence that finds it uncommitted at the next Run stops there (`SEQ-4`),
which is the check working, not a defect.*

**RUN-4** rloop MUST create the Run Directory (`DIR-1`–`DIR-3`) before the pick and MUST NOT
create any other file outside it, save the `.rloop/.gitignore` `DIR-2` names.

## The pick

**RUN-5** The Run MUST begin with exactly one Manager call — the **pick**, unless withheld
(`RUN-22`) — using `AGT-3`'s command line and `PRM-1`'s prompt, with the caller's instruction, if
any, rendered into it. The Manager is expected to leave behind a Task File, or a Finished File, or
both; what rloop does with what it finds is `RUN-11`.

**RUN-6** After the pick, when the verdict is *next Round*, rloop MUST copy the Task File to
`task-1.md` (`DIR-5`) and start Round 1.

## The Round

**RUN-7** A Round `r` (from 1) MUST consist of, in this order and nothing else:

1. one Implementer call (`AGT-5` or `AGT-6`, `PRM-3`), started fresh — no session is carried from
   any earlier Round or earlier Run;
2. the Checkpoint (`DIR-6`);
3. the availability probe (`RUN-21`, `AGT-18`), waited for before the Panel starts;
4. the Panel: a call for every Reviewer `RUN-21` did not record `unavailable` (`AGT-7`–`AGT-10`,
   `PRM-4`), started concurrently and all waited for, and a Feedback File written in place for
   each one that was (`RUN-15`);
5. the Checkpoint again;
6. one Manager call — the **judge**, unless withheld (`RUN-22`) — resuming the pick's session (`AGT-4`, `PRM-2`);
7. the decision (`RUN-11`).

*Fresh Implementers are the design: a brief that only makes sense with the previous Round's
conversation is a bad brief, and `PRM-2` tells the Manager so.*

**RUN-8** The Panel's Reviewers that are called MUST be spawned so that none waits for another to
finish, and rloop MUST wait for every one of them before the Checkpoint that follows. Each called
Reviewer's standard output is its Feedback File (`DIR-4`).

**RUN-21** rloop MUST run the availability probe (`AGT-18`) at two call sites: once before the
pick — after the Run Directory exists (`RUN-4`) and before the pick's Manager call — and once
immediately before each Round's Panel, each call bounded by `--probe-timeout` (`AGT-1`). After
each call it MUST record for every Seat exactly one verdict — `unavailable` or `unknown` — in
`probe-pick.md` before the pick and in `probe-<r>.md` in Round `r` (`DIR-4`), one
`<seat>:<verdict>` line per Seat in the order `manager`, `implementer`, `fable`, `opus`, `astra`,
`sol`. Every line of either record ends with a newline, the last one included. The Manager's
Seat's model is `<manager model>` (`AGT-3`), the Implementer's is `<implementer model>` (`AGT-5`,
`AGT-6`), and each Reviewer's is the one its command line fixes (`AGT-11`).

A Seat is **`unavailable`** only when the probe exited zero within its bound and some line of
its standard output **begins** with `Current week (<family>): 100% used` — anchored at the start
of the line, with whatever follows ignored — where `<family>` is the Seat's model's family by
this table and nothing else:

| model | family |
|---|---|
| `claude-fable-5-1` | `Fable` |
| `claude-opus-5` | `Opus` |

Every other case is **`unknown`**: the probe exited non-zero, hit its bound, wrote nothing, wrote
output with no such line, named a percentage below 100, or the Seat's model is not in that table.
The last holds whatever the probe wrote: a Reviewer is `unknown` whenever the Reviewer's model is
not in that table — which is every codex Reviewer, since that vendor publishes no quota at all —
and so are the Manager's and the Implementer's Seats for any `--manager-model` or
`--implementer-model` value the table does not name. An absent family line is `unknown`, never
`unavailable`: the probe lists only families it has something to report.

The match is anchored because the probe's output is a model's turn, not a machine format: an
unanchored search would let a refusal or an explanation that merely repeats those words remove a
Reviewer or refuse a Run, and that is the one direction fail-open does not protect. The aggregate
`Current week (all models)` line is deliberately **not** read: no family is named in it, nobody
has observed what the probe prints when a whole account is exhausted, and a rule written against
an unobserved format is a guess. That case therefore reads `unknown` and saves nothing, which is
the honest outcome until someone sees it.

*Fail open is the whole design. A verdict is evidence about one moment, the format belongs to a
vendor and will drift, and a wrong `unavailable` silently shrinks the Panel or refuses a Run that
would have worked — so only a positive, unambiguous reading counts, and everything else means
"spawn it". This is also what keeps a typo loud: a misspelled model name fails fast and non-zero,
while an exhausted one hangs and writes nothing, and the two are not confusable.* What a Panel
does with an `unavailable` Reviewer is `RUN-15`'s; what a Run does with an `unavailable` Manager's
or Implementer's Seat is `RUN-22`'s.

**RUN-22** When `probe-pick.md` records the Manager's Seat `unavailable`, or the Implementer's Seat
`unavailable`, rloop MUST exit 2 without spawning any agent, and MUST write to standard error a
message naming the Seat — both, when both are — its model, and the reset the probe reported, which
it names by quoting the probe's matching line verbatim. The message SHOULD name the flag that
chooses another model, `--manager-model` or `--implementer-model` (`AGT-1`). *The line is carried,
not parsed: `RUN-21` reads nothing past `100% used`, and `AGT-17` records that the reset's format
already drifted once.*

rloop MUST NOT make Round `r`'s judge call when `probe-<r>.md` records the Manager's Seat
`unavailable`; it MUST exit 2, with the message above for the Manager's Seat. The Round's Panel and
both Checkpoints still run as `RUN-7` orders — the rule removes only the judge call, and the
Feedback Files are what a human reads about the Round — and the exit takes the judge's place.
This precedes `RUN-11` rather than adding a row to it: that requirement decides `After every
Manager call`, and a call that was never made is not one. `Rloop.decide` and the table it renders
do not change. A Round's verdict on the Implementer's Seat is recorded and nothing acts on it.

*Why a Seat that cannot answer is refused and never filled by another model, and why the Reviewers
are left to `RUN-15`, is `ADR-0008`'s.* `Rloop.seat_out_refused` proves that a Run so recorded
before the pick spawns nothing and `Rloop.pick_refusal_off_picks` is each Seat's pick spawned
without the rule; `Rloop.judged_only_when_manager_answers` proves every judge call is for a Round
whose probe read the Manager's Seat `unknown`, and `Rloop.manager_out_skips_judge` and
`Rloop.judge_refusal_off_judges` are the pair for a Manager that runs out in Round 2.

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
human can resume that session with the preset that started it — `AGT-4`'s two command lines are
the shapes — and ask why. *This said `claude --resume` until 2026-09-20, which cannot resume a
session `--manager codex` minted.*

**RUN-14** An Implementer call that exits non-zero or times out MUST NOT end the Run by itself:
the Round MUST continue to the Panel and the judge, whose prompt names the Implementer's log
(`PRM-2`). *The Manager decides whether half-built work is worth another Round or a `blocked`; the
tool cannot.* `Rloop.implementer_failure_ends_nothing` proves that replacing every Implementer
outcome changes neither the exit code nor the number of Implementers run.

**RUN-15** A Reviewer call that exits non-zero or times out MUST leave its Feedback File holding
the line `REVIEWER FAILED (exit <status>)` — appended to whatever it wrote — and the Round MUST
continue.

A Reviewer that `RUN-21` recorded `unavailable` MUST NOT be called at all. It stays a Reviewer of
the Panel, and rloop MUST write its Feedback File in its place holding exactly
`REVIEWER NOT RUN (unavailable)` followed by a newline, and nothing else — no other content; the
terminating newline is part of the line. *A call that never happened has no exit status,
so `REVIEWER FAILED (exit <status>)` cannot describe it, and `PRM-2` gives the Manager that line's
meaning as `a Reviewer that crashed or timed out`. Two different things the Manager weighs
differently need two different lines. Whether `and nothing else` excluded the newline was asked
by `rl-vcq`; the owner settled on 2026-09-22 that it does not, which is what rloop-bash already
wrote — 31 bytes.*

Both count as down. When **every** Reviewer of a Panel is down — failed, or not run — rloop MUST
exit 2 without calling the judge. *One Reviewer down is a degraded Panel the Manager can weigh;
four down is a broken environment.*
`Rloop.panel_none_aborts` and `Rloop.panel_abort_off_judges` are the pair for failed Reviewers;
`Rloop.not_run_and_failed_aborts` and `Rloop.not_run_down_off_judges` are the pair for Reviewers
not run, and `Rloop.none_called_aborts` is the Panel that called none.

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
tell it to put the question and the options to two advisers, read-only, by running the command
lines `PRM-1` states. Which two, and what the Manager records, this requirement settles below.

A Consultation MUST have answers from two distinct models to settle a choice; one answer is
not enough. An answer is a call that completes within its bound, exits zero and states a
position on the question. A timeout, non-zero exit, empty output, output consisting only of an
error, a refusal, or output taking no position is not an answer. Whether hedged prose states a
position is the Manager's judgment.

The adviser pairs are `fable` with `astra`, then `opus` with `sol`. The Manager MUST replace an
adviser that did not answer by its counterpart in the other pair: `fable`↔`opus`, `astra`↔`sol`,
not by roster order. A model that did not answer MUST NOT be called again in the same Run;
subsequent Consultations start with eligible counterparts. The Manager MUST continue with
eligible models until it has two answers or none remain within the Consultation's budget. It
SHOULD prefer one claude answer and one codex answer; when neither model of one vendor answers,
two answers from the other vendor are enough, and the record below MUST say the Consultation was
single-vendor.

An adviser whose model the relevant Probe record reads `unavailable`, under the Reviewer Seat of
the same name, MUST be treated as an adviser that did not answer, without being called, and
replaced by its counterpart as above; it counts as a model that did not answer for the rest of the
Run. The relevant record is `probe-pick.md` for a Consultation at the pick, and Round `r`'s
`probe-<r>.md`, as that Round's Feedback Files show it, for one at Round `r`'s judge.

*This is the Consultation's parallel to `RUN-15`'s `rloop MUST write its Feedback File in its place`
for a Reviewer that was never called. The verdicts are `RUN-21`'s; the pick prompt lists them
(`PRM-1`) and the judge prompt reads them off the Feedback Files (`PRM-2`), because a weekly limit
resets at a fixed time and an Implementer may run for hours, so by the judge the pick's reading is
the stale one. A Round's record only adds to the models excluded; it never restores one.*

The Manager MUST bound each adviser call through its shell tool and budget the whole
Consultation to leave enough of its turn to write whichever file the outcome calls for — the
Task File when the Consultation settles the choice, the Finished File when it blocks. Before
calling advisers, it MUST choose the per-call maximum durations, the total Consultation budget
and the time reserved for that file; it MUST record those durations, the bounds used and each
call's elapsed time
so a reader can check the limits. A tool returning while an adviser still runs is not a
completed call; the bound MUST cover the call through completion or termination.

When two answering advisers agree the Manager chooses with them. When they disagree it puts
the same question to the remaining eligible advisers, within those bounds. A choice the advisers
leave unsettled MUST end the Run `blocked`, with the question, every answer and the Manager's
recommendation in the Finished File. The report MUST name the models that did not answer and say
whether those that did answer agreed. Silence is neither agreement nor disagreement: a non-answer does not
reclassify the question or require a Clarification.

The Manager MUST record every model called and what each did — answered, did not answer (with
the reason), or refused — alongside the question and the answers: in the Task File with the
choice it settled, or in the Finished File with its recommendation when the Consultation blocked
before a brief was written. An adviser skipped for its Probe verdict is recorded as one that did
not answer, with that verdict as the reason. The bounds and timing record
belongs with that account. A choice the brief does not need to settle is the Implementer's.

*This is a Consultation, not a Panel: rloop does not run it, the Manager does, in its own
session (`RUN-16`: `The Manager MUST be one session for the whole Run`), which is why it costs
the control flow nothing and why only a live Run can show it happens (`CNF-22`).*

## What a Run leaves

**RUN-17** On every exit rloop MUST leave the Run Directory as it is: no cleanup, no deletion, on
success or failure. It is the evidence.

**RUN-18** rloop MUST NOT tell an Implementer whether to commit: the repository's own instructions
decide that. `OVR-3` owns rloop's prohibition on git mutations. The Manager's obligations at
`done` are `SEQ-8`.
