# 06 — Conformance

What an Implementation must demonstrate, and how: every item below is executed by
`conformance/run`, the Conformance Suite this repository ships. Each item names the requirements
it proves. Nothing here is ticked by hand — the suite's output is the tick — and an item that
cannot be executed is in the last section, with the reason.

## The suite's contract

**CNF-1** `conformance/run <path to an rloop executable>` MUST run every item below against that
executable and exit 0 only if every one passed, printing each item's identifier and verdict. It
needs `bash`, `git`, GNU coreutils, `grep`, `sed`, `awk`, `cmp` (diffutils) and `find` (findutils)
on `PATH` and nothing else — no Lean, no Python, no network — so that an Implementation repository
in any language runs it from the submodule. `TMPDIR` is where it makes its scratch tree, and the
suite MUST expand every path it reads without splitting it on whitespace. The tree's root is a
directory whose name the suite gives a space and a tab, so every path the suite hands the
executable holds whitespace whatever the caller exported.
(`00-overview.md`)

**CNF-2** The suite puts fake `claude`, `codex` and `grok` executables first on `PATH`. A fake reads
`RLOOP_ROLE`, `RLOOP_ROUND`, `RLOOP_RUN`, `RLOOP_REVIEWER` and `RLOOP_RUN_DIR` (`AGT-13`) to find
its scripted part, records what it received — argument list, environment, working directory,
whether standard input was at end of file — and acts: writes a Task File or Finished File, exits
non-zero, sleeps, ignores a signal, spawns a grandchild, or interferes with the Manager's files,
as the scenario says. The fake never reads a prompt and never parses a flag, which is what keeps
the suite's control flow independent of `02` and `03`. Before the suite runs the executable, it
resolves the tools `CNF-1` names for an Implementation to absolute paths and builds one private
directory of symlinks under those exact names; a name the host lacks is left out and named once
on standard error. The executable, and so every fake it spawns, runs with `PATH` set to the fakes
directory, then that private directory, and nothing else; for the `CNF-19` items the `git` shim's
directory sits between the two. The fakes directory and the private directory are under the
scratch root `CNF-1` describes, so both entries of that `PATH` hold a space and a tab. `cmp` and
`find` are the suite's own and are not on the executable's `PATH`. An executable that relies on
anything more brings it itself; a wrapper that puts its own inputs on `PATH`, as a nix
`writeShellApplication` does, satisfies this. *Why the
host's `PATH` is withheld: rloop-bash `02c6206` compared `task.md` against `task-<r>.md` with
`cmp`, which its flake did not wrap, and read a missing `cmp` as "differs". The Run `RUN-12`
describes — `rloop MUST exit 2 rather than start another Round` — then burns every remaining
Round on the same brief instead of ending at the no-decision one, and every Round's Task File
goes where `DIR-6`'s `move task.md to rejected-<r>-task.md` sends it; on a host with diffutils on
`PATH`, the suite could not tell.* (`AGT-13`)

## The scenarios

**CNF-3** For every line of `conformance/scenarios.tsv` the suite MUST run the executable in a fresh
git repository with the line's script loaded into the fakes, `--max-rounds` set to the line's cap,
`--quota-wait` and `--quota-poll` to short whole-second values (overridden by the wait block's
`quota` and `poll` fields), the `cuts` field loaded into the fake, and each Seat's preset and model
set from the line's `seats` column, and assert the exit status equals the line's and the recorded
spawns equal the line's trace — repeated judge attempts projected to one logical judge token per
Round, pick tokens never collapsed; a Panel compared as the set of the Reviewers rloop called, the
rest in order, and a Run refused at the pick as no spawn at all. The file is what `tools/formal/`
enumerates (`ADR-0002`, `tools/check_scenarios.py`). In `seats`, `fable` and `opus` select claude
with that Reviewer's model; `claude` selects claude with the off-table model `claude-sonnet-5`;
`codex-fable` and `codex-opus` select codex with the corresponding table model; an unnamed Seat
selects codex with that same off-table model literal. `pick=<shape>` scripts the Probe before the
pick; `-` selects codex for both Seats and a clear pick Probe. *The preset is independent of model
spelling. An off-table claude model still reads the session cap, while the codex replay keeps the
older family-only scenarios independent of Manager and Implementer exhaustion.* This item is the
executable form of the decision table and the Round: (`RUN-5`, `RUN-6`, `RUN-7`, `RUN-9`, `RUN-10`,
`RUN-11`, `RUN-12`, `RUN-13`, `RUN-14`, `RUN-15`, `RUN-21`, `RUN-22`, `RUN-24`, `DIR-5`, `DIR-6`,
`DIR-7`, `OVR-1`)

*Amended 2026-10-08 (`rl-8ee8`): the replay encodes preset identity separately from family
membership and includes session readings.*

**CNF-4** The suite MUST be able to fail: run with `--self-check` it flips one expected exit in
a copy of the scenario file, replays it, and requires a red result. The scenario file is shown
sensitive to each guard by `lake exe scenarios --controls` in `tools/check_formal.sh`, which
counts the lines each guard's absence would change and refuses zero. *A suite that cannot go red
is a green check that asserts nothing.* (`RUN-11`)

## Starting and stopping

**CNF-5** Each of these invocations exits 2, spawns nothing, and writes to standard error: an
unknown option; `--max-rounds 0`; `--max-rounds x`; `--reviewer-timeout -1`;
`--reviewer-timeout 0`; `--probe-timeout 0`; `--kill-after 0`; two `INSTRUCTION` arguments;
`--auto --base HEAD`; `--auto --run-dir d`; `--auto --run-dir ''`, the value empty;
`--implementer-model --max-rounds 1`, the value swallowed; `--=x`; `--auto=1`; `--help=x`;
`--version=x`; `--manager gpt-6-astra`, a value outside the preset's set and the mistake a caller
makes who means `--manager codex --manager-model gpt-6-astra`. `--version` and `--help` exit 0
and spawn nothing. `--auto --max-runs 08` with a Manager fake scripted idle spawns exactly one
pick and exits 0; with nine scripted done, it stops after exactly eight picks and exits 2.

The quota-option arms also reject zero, missing and nonnumeric values for each quota option,
with exit 2, a diagnostic and nothing spawned. (`AGT-1`, `AGT-2`, `SEQ-3`, `SEQ-5`, `SEQ-6`)

**CNF-6** Outside a git working tree the executable exits 2 and spawns nothing. (`RUN-1`)

**CNF-7** With `--run-dir` naming an existing directory (empty or not) or a path whose parent does
not exist, the executable exits 2 and spawns nothing. With `--run-dir` naming a fresh path, the
directory exists afterwards and is the only one created. (`DIR-1`, `DIR-3`)

**CNF-8** Without `--run-dir`, in a repository whose path the suite gives a space and a tab
independently of `TMPDIR`, the Run Directory is created under `<toplevel>/.rloop/runs/`,
`<toplevel>/.rloop/.gitignore` holds exactly `*` and a newline — compared byte for byte — and
`git status --porcelain` prints nothing after a Run whose fakes changed no tracked file.
Separate Runs, also without `--run-dir` and with fakes that change no tracked file, use
repositories that are `mktemp`-named directories under the suite's scratch root, whose name the
suite gives a space and a tab (`CNF-1`). A pre-existing `.gitignore` of
either shape a check by eye accepts, `*` followed by two newlines or `*` with no newline, holds
those same two bytes after its Run, and the tree is clean. (`DIR-2`, `RUN-4`, `RUN-23`)

**CNF-9** After a two-Round Run the Run Directory holds exactly the names `DIR-4` lists for two
Rounds and nothing else, `probe-pick.out`, `probe-pick.err` and `probe-pick.md` among them; each
agent's `.out` and `.err` hold that fake's standard output and standard error entire; `session`
holds the Manager's session id as a UUID, whichever preset established it (`RUN-16`); and the
directory is intact after a Run that ended 2. One further two-Round Run has the repository's own
path hold a space and a tab, and its `--run-dir` a space as well, and leaves that same listing; the
suite makes that path itself rather than reading it out of `TMPDIR`, since an item that sees
whitespace only when the caller exports it gives a verdict that moves with `TMPDIR`. That arm reads
what the Run Directory holds afterwards; what the agents were handed is `CNF-11`'s and `CNF-12`'s.

The layout comparisons include the numbered Panel-site and judge-site records, in C locale.
(`DIR-4`, `RUN-17`, `RUN-23`)

## What agents receive

**CNF-10** Every fake records the variables in `AGT-13`'s environment table with the values
applicable to its role and Round, `RLOOP_REVIEWER` unset except for Reviewers, its working
directory equal to the git toplevel, and standard input at end of file on first read. Under the
default Manager preset, pick and every judge record `BASH_MAX_TIMEOUT_MS` equal to the Manager
timeout in milliseconds, at both the default timeout and a non-default `--manager-timeout`,
overriding a different inherited value in each Run. The non-default-timeout Run also selects a
different Manager model. Missing required records or values and wrong values fail the item.
The suite makes no assertion about `BASH_MAX_TIMEOUT_MS` for codex Managers, Implementers,
Reviewers or Probes. (`AGT-12`, `AGT-13`)

One further Run inherits exported `SHELLOPTS=braceexpand:hashall:interactive-comments`.
The pick, Implementer, each named Reviewer, both judge attempts (the first cut, then retried),
and every Probe record that variable exported and byte-identical to the supplied value.
A launcher used only for this Run reads the raw value with GNU coreutils `env -S` before bash
starts; the fake records it with `printf %q` so embedded or trailing newlines survive comparison.
The export bit comes from bash's `declare -p SHELLOPTS`, captured before the fake changes its shell
options. Exact per-tag and total argv and environment
record counts reject missing or extra calls. This Run also inherits exported `out`, set to a
sentinel containing a tab and newlines: every call, each judge attempt and every Probe included,
records it set and byte-identical before the fake assigns any variable. An unset or changed `out`
fails. Only these inherited variables are compared in this Run. (`AGT-13`)

A separate one-Round Run, the pick writing a Task File, the Implementer and all five Reviewers
succeeding and the judge writing `STATUS: done`, starts rloop with `SHELLOPTS` removed from its
environment. Every call, the Probes included, records `SHELLOPTS_EXPORTED=0`. A nonzero Run exit,
a missing or extra call, a missing export-bit record or an exported `SHELLOPTS` fails. These arms
exercise `AGT-13`'s `the environment rloop itself received plus exactly the variables set below, subject to the table's conditions`: neither `out` nor `SHELLOPTS` appears in that table.

*Amended 2026-10-24 (`rl-jeo2`): add caller-exported `out` preservation to the inherited-variable
Run and the separate Run checking that an unexported `SHELLOPTS` stays unexported.*

*Amended 2026-10-24 (`rl-ypm7`): add the `SHELLOPTS` Run above. It exercises `AGT-13`'s
`the environment rloop itself received plus exactly the variables set below, subject to the table's conditions`.*

*Amended 2026-10-24 (`rl-ypm7`): read the inherited value before bash starts and escape its
record; bash rebuilds `SHELLOPTS` on startup, hiding dropped options and empty values in the
earlier comparison. The export-bit check is unchanged.*

**CNF-11** For each role the recorded argument list equals the fixture in
`conformance/fixtures/argv/` with the placeholders filled in: the pick's `<session id>` is the
`session` file's content and each Run's Round 1 judge call, the one read here, carries that same
id — the item that reads a Run's judge calls all is `CNF-23` under `--manager codex` and `CNF-33`
under the default preset; `<manager model>` is `--manager-model`'s value, or the preset's default;
`<implementer model>` is `--implementer-model`'s value, or the preset's default, asserted for the
default model of each preset and a non-default value given on the command line under each,
without changing the selected preset or its literal effort;
`--manager codex` produces `AGT-3`'s and `AGT-4`'s second lists and the default produces their
first; omitting `--implementer` and `--implementer-model` produces `AGT-6`'s list with
`gpt-6.1-sol`, explicit `--implementer codex` produces that same list and model, and explicit
`--implementer claude` produces `AGT-5`'s list with `claude-opus-5-5`; the five
Reviewers' lists are `AGT-7`, `AGT-8`, `AGT-10` and `AGT-19`'s, one each, with their `RLOOP_REVIEWER` names.
One further Run has the repository's own path and its `--run-dir` path each hold a space and a tab,
and every role's list — the pick's, the Implementer's, the five Reviewers' and the judge's — equals
its fixture with those paths' bytes unchanged; the suite makes both paths itself rather than
reading either out of `TMPDIR`, so no verdict here moves with what the caller exported. (`AGT-1`, `AGT-3`,
`AGT-4`, `AGT-5`, `AGT-6`, `AGT-7`, `AGT-8`, `AGT-10`, `AGT-11`, `AGT-19`, `RUN-16`, `RUN-23`, `OVR-2`)

*Amended 2026-10-08 (`rl-4i7t`): default-model expectations and the generated argv fixtures now include the new
models and explicit Implementer effort; the Manager override uses Fable to differ from its default.*

*Amended 2026-10-13 (`rl-9uu1`): the omitted Implementer preset now witnesses codex, explicit claude
retains its own argv witness, and each preset has a model-override Run. `F27` records the decision's
evidence and verification.*

**CNF-12** For each role the recorded prompt argument equals the fixture in
`conformance/fixtures/prompts/` rendered by `PRM-6` with the values the suite knows: the Run
Directory's paths, the base hash, the Round, `--max-rounds`, the caller's instruction (given and
absent), the dirty-at-start list (a tree with one modified and one untracked path, and a clean
tree), the unavailable list, empty in each of these Runs since no Probe before the pick here
reports anything exhausted (`CNF-32` asserts it populated, and empty in a Run of its own), and the
five Feedback File paths in order. One further Run gives an instruction holding placeholder names
(`{{TASK_FILE}}`, `{{UNAVAILABLE}}`, `{{ROUND}}`) together with a backslash, `&` and `%s`, and a
`--run-dir` path holding `{{INSTRUCTION}}`; its pick, Implementer and judge prompts equal their
fixtures with each value's bytes unchanged, as `PRM-6` renders them. A further Run, the one
`CNF-11` reads the argument lists of, has the repository's own path and its `--run-dir` path each
hold a space and a tab; every role's prompt — the pick's, the Implementer's, the five Reviewers'
and the judge's — equals the fixture rendered with the paths the suite handed the executable, byte
for byte. Each rendered prompt ends with `PRM-5`'s sentence. (`PRM-1`, `PRM-2`, `PRM-3`, `PRM-4`,
`PRM-5`, `PRM-6`, `RUN-3`, `RUN-23`, `DIR-10`)

*Amended 2026-10-13 (`rl-9uu1`): the hostile-value prompt Run explicitly selects claude, while the
omitted-preset and whitespace-path Runs use codex; prompt comparisons remain byte-exact. `F27`
records the decision's evidence and verification.*

**CNF-13** `{{BASE}}` is the full hash of `HEAD` at start, and with `--base <ref>` the full hash of
that ref; a commit the fake Implementer makes during Round 1 does not change the base rendered
into Round 2's prompts. The base is read out of each Round's `fable` Reviewer call and Round 2's
judge call, and the item cannot pass on absent evidence: a record of one of those calls missing is
red. (`RUN-2`)

## Output

**CNF-14** For a Run ending 0, 1 or 3, standard output is byte-identical to `finished.md` and
nothing else; for a Run ending 2, standard output is empty and standard error is not, whether no
Finished File was written (a pick that fails) or one is on disk (a pick whose first line is not a
status; a pick whose first line is `STATUS: done` with a NUL byte inside it; a judge that wrote
`STATUS: idle` after a Round). *The NUL case is there because `RUN-9` compares the first line
`byte for byte` and a reader that drops NUL bytes sees `done`.* (`RUN-9`, `RUN-10`)

**CNF-15** A Reviewer fake that exits 7 after writing a line leaves its Feedback File holding that
line followed by `REVIEWER FAILED (exit 7)`; a Round with one such Reviewer proceeds to the judge.
A focused Run has only Grok fail while the original Reviewers succeed: every identity starts,
Grok's recorded outcome is failure, its progress without a separating newline, partial output and
appended note are compared byte for byte, and the judge is reached. The same mixed-class Round
once more with `--kill-after 2`, every Reviewer fake spawning a child that ignores
SIGTERM and, once its own fake has exited, writing to the standard output it inherited — its
Reviewer's Feedback File (`AGT-13`, `DIR-4`): the Run ends 0 and each failing Reviewer's Feedback
File opens with that Reviewer's line, **ends** with `REVIEWER FAILED (exit 7)`, and carries at least
one line of its straggler's between the two. (`RUN-15`)
*The straggler's own lines are in the file because its Reviewer's group lives the grace out, and the
note's byte-exact form is the row above, which has no straggler; what this row adds is that the note
is on the far side of the straggler's writes. The child inherits the Feedback File's descriptor and
with it that descriptor's file offset, and `AGT-15` has `A call is complete only once its process
group has been reaped that way`, so an Implementation that appends the note before that reaping
leaves it at the offset the child's next write overwrites — and the Manager then reads a crashed
Reviewer's partial output as ordinary feedback. That a straggler line is there at all is asserted
because a child that wrote nothing leaves the note nothing to survive, and no arm of this suite may
pass on absent evidence. `--kill-after 2` rather than 1 so that the child is certainly scheduled to
write inside the grace; nothing here is clock-measured.*

**CNF-37** With the original Reviewers failing and only Grok successful, require every fixed
identity's start and its own recorded outcome, exact Panel membership, successful Grok output,
the judge-site Probe and judge call, a done Finished File and exit 0. Pair this with all Reviewers
failed: require those same starts and each failed outcome, exit 2, no judge-site Probe or judge,
and no Finished File. The exact spawn trace is compared in each arm. These are individual
outcomes the model's abstract Panel classes cannot prove. Failure-marker bytes belong to
`CNF-15`; quota omission and chronology belong to `CNF-24`–`CNF-31`.
(`AGT-11`, `AGT-19`, `RUN-8`, `RUN-15`)

## Concurrency, time and signals

**CNF-16** With every Reviewer fake sleeping 2 seconds, a Round's Panel completes in under 5
seconds, and every Reviewer's recorded start precedes every Reviewer's recorded end. Exact
identity membership and one successful end per Reviewer are required. (`RUN-8`)

**CNF-17** With `--reviewer-timeout 1 --kill-after 1`, one Reviewer fake sleeping 30 seconds and
spawning a child that ignores SIGTERM, and the other four answering, once with slow fable and
once with slow Grok: the Run exits 0, the slow
Reviewer's Feedback File carries `REVIEWER FAILED`, the other four hold the fakes' answer, the
judge is called, and neither the slow Reviewer's own process nor its child is running when the
judge starts — the judge's own record of the calls and of the children still running at its start
lists neither — nor once the executable has returned. With `--implementer-timeout 1 --kill-after 1`
and an Implementer fake that ignores SIGTERM, the Implementer is not running when any Reviewer
starts — no Reviewer's own record of the calls still running at its start lists it — nor once the
executable has returned, and the Run reaches the Panel and returns within 10 seconds. With
`--manager-timeout 1 --kill-after 1`, a sleeping pick that spawns the same child: the Run exits 2
and, when the executable has returned, neither the fake nor its child is running. (`AGT-14`,
`AGT-15`, `AGT-16`, `RUN-14`) *The Manager row is the shape the astra Reviewer found on rloop-bash
on 2026-09-23: an Implementation that waits for its `timeout` wrapper alone returned 2 with the
SIGTERM-ignoring child alive, since the wrapper returns the moment the fake itself dies.*

**CNF-34** With `--kill-after 1` and a Run of one Round that every role completes — the pick writes
a Task File, the Implementer and all five Reviewers succeed and the judge writes `STATUS: done` —
each Manager fake exiting 0 having spawned a child that ignores SIGTERM: the Run exits 0; no call of
the Run records any of those children among the children alive when it started, nor the pick's or
the Implementer's own process among the calls alive when it started; and once the executable has
returned, neither a fake that spawned one nor any of the children is running. Only in this ordinary
Manager-spawner Run does the pick wait one second after writing its files before exiting; every
other Run described in this item omits that delay. The same Run with the Implementer fake spawning
that child instead of the Manager's. The same Run with every Reviewer fake spawning it: the
judge-site Probe's record — the first call to start once every Reviewer has exited — carries no
Reviewer's child among the children alive when it started and no Reviewer's own process among the
calls alive when it started. The same Run with every Probe spawning it, each Probe waiting one
second after spawning its child before exiting — a sleep every other Run described in this item
omits: the pick's record carries neither the child nor the own process of the probe before the pick,
and each of the Panel's five records carries neither the child nor the own process of the Panel-site
Probe; the judge's record carries neither the child nor the own process of the judge-site Probe.
Neither of those two Runs can pass on absent evidence: a missing record, a missing snapshot
line, a missing recorded pid or child readiness and a Panel of other than five records are each red. A further Run of
the Implementer's shape, the Implementer fake also appending to the Task File and its child polling
for `rejected-1-task.md` under the Run Directory rather than sleeping: the Run exits 0,
`rejected-1-task.md` is there, the child recorded that it was watching before its fake exited, and
it never found the file — so the Implementer's group was gone before the Checkpoint that follows its
call, and not only before the next call. Further Runs of the probes' shape cover the pick, Panel and
judge sites, every probe's child polling under the Run Directory rather than sleeping for its own
record: `probe-pick.md`, `probe-1-panel-1.md` or `probe-1-judge-1.md`. In each the Run exits 0, that
record is there, the probe whose own record is the watched one recorded that it was watching before
its fake exited, and its child never found the file — so that probe's group was gone before rloop
wrote that record, and not only before the next call. No watching Run passes on absent evidence
either: a missing record, a missing readiness marker, a fake that exited before its child published
one and a child whose pid is unrecorded or still running once the executable has returned are each
red. A last Run of the probes' shape, for the read of a probe's output rather than for the record:
every probe's child writing to the standard output it inherited rather than sleeping — one second
after its own fake has exited, the line `Current week (Opus): 100% used` — with `--implementer
claude`, both Seats at the claude preset's default model and `--kill-after 4`. The Run exits 2, the
probe before the pick is the only call it makes, that line is in `probe-pick.out`, `probe-pick.md`
records the Manager's Seat, the Implementer's and `opus` unavailable and the other four unknown,
and the child's pid is recorded and not running once the executable has returned — so rloop read
that probe's output after reaping its group and not before. Nor does that Run pass on absent
evidence: a line that never reached the capture leaves the read nothing to witness and is red.

Further watching Runs establish these step boundaries, each with `--kill-after 1`:

- The pick's child watches `task-1.md` in a one-Round Run.
- Every Reviewer's child watches `rejected-1-task.md` in a one-Round Run with only the `fable`
  Reviewer appending to the Task File. The rejected file contains the Reviewer's edit: the
  Implementer leaves the Task File unchanged, so the first Checkpoint has no edit to reject.
- The first judge's child watches `task-2.md` in a Run where that judge rewrites the Task File,
  the next Round runs and its judge finishes done.

Each Run exits 0, the watched file exists, every relevant child recorded readiness before its fake
exited and none recorded seeing the file. The pick and first judge each have their own record and
the next Round's Implementer record; neither their own process nor their child appears alive in
that later record. The Panel has every Reviewer's record and the judge's, which carries neither
process nor child of any Reviewer. The Run has no `WATCH_NOT_READY=` record, and neither a fake
that spawned a child nor its child survives. Missing evidence is red, including the recorded pid
and expected later call. Only the relevant tag's observation counts: a later Manager's child may
find a snapshot that already exists. These witnesses establish the pick's snapshot, the second
Checkpoint and the first judge's *next Round* decision through its snapshot effect. They do not
establish every decision path or detect a decision computed early with all effects deferred until
after reaping. `F17` records that measured limitation.

*A call that exits 0 is what `AGT-14`'s `At the limit` never reaches, and leaving a check running is
a habit `07-open-findings.md`'s `F16` records: the child of a healthy Implementer writes into the
working tree through the whole Panel and the Manager's commit. `CNF-17` reads the same record for
the reaping after a timeout. The pick's and the Implementer's own processes are read from every
later record, each Reviewer's from the judge-site Probe's record alone, and each Probe's from the
call that follows it (`RUN-21`, `RUN-7`). What `RUN-8` forecloses is a *sibling* Reviewer's record,
having the Panel's Reviewers spawned so that `none waits for another to finish`: a Reviewer that
finds a sibling's process — or a sibling's child — alive has found that working, which is why the
judge-site Probe, the first call after the whole Panel, is where a Reviewer is read. The Checkpoint
starts no call, so no record of a later one speaks for that boundary and the straggler is the
witness; the appended Task File is what makes `DIR-6` `move task.md to rejected-<r>-task.md` there,
and the child's recorded readiness is what keeps its silence from passing for compliance. Each
probe's record starts no call either, and `AGT-15`'s `A call is complete only once its process group
has been reaped that way` puts it after the reaping, so the same straggler witnesses it;
`RLOOP_FAKE_WATCH=probe:@own` gives each child its own record name. Each site has a Run that reads
the watching probe's tag and record index for boundary evidence, with an arm-wide `WATCH_NOT_READY=`
guard; `watched_nothing`'s comment in `conformance/run` owns the scope rationale. What that
straggler establishes is the record and not the read: `AGT-15` has `rloop MUST read the call's
output, and do anything else that follows the call` come `only after that`, and a child that never
finds the record witnesses the second of those and not the first. Reading the output leaves no file
for a straggler to poll, so the last Run gives the read a straggler that writes where those poll:
into the capture `DIR-4` has the probe's standard output reach `entire and unmodified`, so that an
executable which reads before reaping reads bytes that line has not arrived in yet. The probe before
the pick is that Run's site because `RUN-22` ends the Run on its verdicts — `exit 2 without spawning
any agent` — which makes a verdict derived from the wrong bytes a Run that calls the pick and goes
on. Its window has margin at both ends: the child's first write is a second after its own fake
exits, which a read before the reaping is well inside, and `--kill-after 4` keeps that child alive
three seconds past that write, which a read after the reaping falls past, the line having reached
the capture three seconds before that read. The pick's exit delay makes its own process observable
after its Task File exists, without opening standard input or changing its child; each probe's sleep
in the probes' ordinary Run does the same for the probe's own process at the call that follows it.
`F17` records the separate own-process and child measurements. The watching Runs use `RUN-6`'s `copy
the Task File to` `task-1.md`, `RUN-7`'s `the Checkpoint again`, and `DIR-5`'s `After the pick and
after every judge call whose verdict is *next Round*` as observable steps. `F17` owns the remaining
limitations.*

Further arms put late output in a cut attempt's stdout while its group is reaped: that output stays
in the original capture, the line is no longer a cut and no retry follows. The output-read boundary
is driven on attempt 1 and on a retry. An attempt's group is gone before its post-cut check; a
retried attempt's group is gone before the next-Round snapshot; a re-check's group is gone before
its own numbered verdict. Readiness and recorded child identities keep absent witnesses red.
(`AGT-15`, `AGT-16`, `DIR-4`, `DIR-5`, `DIR-6`, `RUN-6`, `RUN-7`, `RUN-8`, `RUN-11`, `RUN-21`,
`RUN-22`, `RUN-24`)

Two further one-Round Runs exercise `AGT-16`'s `with no shell in between`: the pick writes a
Task File, the Implementer and all five Reviewers succeed and the judge writes `STATUS: done`.
In the no-bash Run, `bash` remains on the executable's private `PATH` as a shim that records its
PID and parent PID before execing the real bash. In the bash-env Run, real bash is on `PATH` and
`BASH_ENV` names a file recording the same identities except when the fake itself starts.
Each fake uses a runtime-generated absolute-bash shebang and records its own PID and parent PID,
including every Probe. Each Run exits 0 and leaves `manager-judge-1.out` and
`manager-judge-1.err`; their existence alone is checked. An absent fake PID record fails.
Starting at the executable's launched PID, every logged shell whose parent is already in that
chain joins it. Outside this start chain, a logged shell PID equal to a fake's PID or parent PID
fails the item. The checks compare only process identities; they assert no capture contents.
`F30` records the start-chain exception and the measured limits.

*Amended 2026-10-24 (`rl-jeo2`): add the no-bash and bash-env PID checks above to this item's
single verdict.*

*Amended 2026-10-08: the probe-output read witness reports Opus exhaustion to refuse the default
Seats, with the corresponding Reviewer verdict; its timing and absence-of-evidence checks remain.*

*Amended 2026-10-13 (`rl-9uu1`): the Probe-output read Run explicitly selects a claude Implementer
so the same exhausted Seats still witness the read boundary. `F27` records the decision's evidence
and verification.*

**CNF-35** With one Round, `--kill-after 1`, the `fable` Reviewer fake sleeping 10 seconds while the
other four answer at once, and every Reviewer fake spawning a child that ignores SIGTERM: the child
the `opus` fake left is gone within 6 seconds of `opus`'s own recorded exit, and at that moment the
Panel is five Reviewer records each carrying a child, `fable`'s own recorded process is running and
`fable` has not recorded its exit; the Run ends 0, and neither a fake that spawned a child nor any
child is running once the executable has returned. Then the same Round with `--kill-after 5` and no
Reviewer sleeping, so that the five exit within a moment of one another: each of the five children
is gone within 9 seconds of its own Reviewer's recorded exit. Neither row passes on absent
evidence: a Panel of other than five records, a Reviewer that recorded no child or readiness, and one whose fake
recorded no exit, are each red. (`AGT-15`, `RUN-8`)
*`AGT-15` has `Reviewers run concurrently` and `so each Reviewer's group is reaped as that Reviewer
exits`, and these are the two ways an Implementation reaps them in some other order anyway. The
first row is the roster: a Panel waited for in the fixed order `fable`, `opus`, `astra`, `sol`, `grok` keeps
an early Reviewer's group until every Reviewer named before it has exited too — up to
`--reviewer-timeout` of an orphaned build or check writing into the working tree while the rest of
the Panel reviews it — and `opus` is the one read because `fable`, the Reviewer ahead of it, is the
one still running. That `fable` runs is read from `fable`'s own recorded process, and the Panel's
records are counted rather than assumed, because every other read of the row is about `opus` alone:
an Implementation that called one Reviewer would satisfy all of them, and the survival clause says
nothing about a record that was never written. `fable`'s missing end line is read as well and not
instead, a Reviewer the executable has not yet reaped being a zombie whose pid still answers. The
second row is the grace: a reap that blocks the wait loop leaves the Reviewer that exits next
unsignalled until the previous group's grace has ended, so the second child of five goes two graces
past its own Reviewer's exit and the fourth four. `CNF-34` sees neither, reading each Reviewer
against `the first call to start once every Reviewer has exited`, by which time every
delay above has ended. Each bound is its row's grace and a margin, five seconds and four, because
the claim is that a group goes with its own Reviewer and not that it goes in any particular tenth of
a second: these rows, `CNF-16`, `CNF-17` and `CNF-36`'s interruption rows are the suite's
clock-measured claims, and a
tight bound is a flaky suite. `--kill-after 5` in the second row rather than 1 is what carries the
shape it separates from past nine seconds at all, and that margin is not wide at every child: the
second Reviewer's two graces are ten seconds and clear the bound by one. It is the third child and
the fourth, three graces and four — fifteen seconds and twenty — that the bound separates widely,
while the first, whose group waits on nothing, is not separated at all.*

**CNF-18** SIGINT sent to the executable while an Implementer fake sleeps, having spawned a child
that ignores SIGTERM: the fake records SIGTERM, the executable exits 2 with `interrupted` on
standard error, neither the fake nor its child survives, and the Run Directory is intact. The
same with SIGTERM. Separate SIGINT and SIGTERM Runs interrupt active Grok: all fixed identities
have started, Grok's own recorded process and child are positively alive before the signal,
Grok records SIGTERM, exit is 2 with `interrupted`, the snapshot remains and neither survives.
The same once more with a **Probe** (`AGT-18`) in the Implementer's place: SIGINT
while the probe `RUN-21` runs `once before the pick` sleeps, having spawned such a child, under a
`--probe-timeout` well above the sleep so that `AGT-14`'s `At the limit` is not what ends the call —
the probe's record carries SIGTERM, the executable exits 2 with `interrupted` on standard error,
neither the process it recorded nor the child it recorded survives, and the Run Directory is still
there. No clause of that Run passes on absent evidence: its record is found by counting what matched
rather than by reading an unmatched glob, and a missing record, an unrecorded process and an
unrecorded child are each a failure. A second SIGINT while a fake ignores SIGTERM ends it at once,
and so does a second SIGINT delivered while a call's **group** is being reaped rather than during
the call: with `--kill-after 20` and an Implementer fake that exits at once having spawned a child
that ignores SIGTERM, two SIGINTs 200 ms apart once that fake's own process is gone leave the child
dead within 5 seconds — a quarter of the grace the reap would otherwise run out — and the executable
exits 2 with `interrupted` on standard error. That row does not pass on absent evidence either: the
child is read alive immediately before each of the two signals, and is red if it is not, since a
group already empty leaves the bound nothing to measure.
(`AGT-15`, `AGT-16`, `AGT-18`, `OVR-4`, `RUN-4`, `RUN-17`, `RUN-21`)
*The Probe Run is here because `AGT-15` binds the interruption to `every live group`, and `AGT-16`
has the Probe started `in its own process group` as every agent process is: an Implementation that
runs the Probe by a path of its own, keeping no group for the handler to reach, passes the two
Implementer Runs and still leaves a straggler behind on a SIGINT during a probe. Reaping a group
once the call has returned is `CNF-34`'s to witness, at the pick-site, Panel-site and judge-site
checks; registering it with the handler is this item's, and the Probe is the role whose call an
Implementation is likeliest to write inline rather than through the machinery every agent call
shares. The call site driven is `RUN-21`'s
`once before the pick`, which the fake's one probe-sleep knob already lands on, so the Round's probe
is never reached and the Run costs no new knob. The probe before the pick is the Run's first call,
and `RUN-21` has it `after the Run Directory exists`, `RUN-4` owning the creation. Of the probe's
captures `DIR-4` says `from the availability probe's stdout and stderr`; `DIR-4`'s `before the pick`
fixes which call they belong to and not the moment they appear, so an Implementation may open them
as it spawns the probe and another may write them only once the probe has returned, and an arm that
read them there would hold every Implementation to one of the two. The Run-Directory clause of the
Probe Run is therefore the weaker one deliberately: at the instant that probe is interrupted, the
directory itself is all the suite can portably read. `RUN-17`'s `no cleanup, no deletion` is what
forbids removing the directory on the way out; `task-1.md`, the witness of work left as it is, stays
the Implementer Runs'. The second SIGINT stays on an Implementer fake: escalation is the handler's
second-signal branch and not per-role. The reap it is delivered into besides is where `AGT-15`'s
`A second SIGINT during that wait MUST send SIGKILL at once` reaches a group whose call has already
returned: an Implementation that takes a group off the set its handler signals before reaping it
passes every clause above, the group being on that set for the whole of the call, while neither
signal reaches it there and the group runs the whole `--kill-after` grace out. `--kill-after 20` is
what makes that grace long enough to signal into and the 5-second bound generous inside it.*

## Git

**CNF-19** With a logging `git` shim first on `PATH` (before the real `git`, which the shim
forwards to), a two-Round Run and a three-Run Sequence invoke git only with the subcommands
`rev-parse`, `status`, `diff` and `log`, and `HEAD` and the reflog are unchanged afterwards when
no fake commits. (`OVR-3`, `RUN-18`, `SEQ-9`)

## The Sequence

**CNF-20** With `--auto` and Manager fakes scripted per `RLOOP_RUN` as done, done, idle: exit 0;
three Run Directories; standard output is `== run 1 ==`, the first Finished File, `== run 2 ==`,
…, and nothing else; the three picks carry three distinct session ids; and the instruction is
rendered into all three pick prompts. Scripted done, blocked, idle: exit 1 after two Runs.
Scripted done forever with `--max-runs 3`: exit 2 after three Runs. Scripted done, done, then a
pick that fails: exit 2, and standard output holds exactly two `== run` blocks. Scripted done, then
a Run that ends 2 with a Finished File on disk (a pick whose first line is not a status; a judge
that wrote `STATUS: idle` after a Round): exit 2, two Run Directories, and standard output is
byte-identical to `== run 1 ==`, the first Finished File, and nothing else. (`SEQ-1`, `SEQ-2`,
`SEQ-5`, `SEQ-6`, `SEQ-7`, `RUN-10`)

**CNF-21** With `--auto` and a Run 1 Manager fake that writes `STATUS: done` and leaves an
untracked file in the tree: exit 2 before Run 2's pick, with no second pick spawned. A lone Run
whose fake leaves the tree dirty exits by its Finished File, with a warning on standard error.
(`SEQ-4`, `SEQ-8`)

## Live: what no fake can show

**CNF-22** Once per Implementation release, by hand: a lone Run and a two-Run Sequence against
the real CLIs at the versions `AGT-17` names, on a repository with a tracker, ending `done`, with
the Manager's commits following the repository's conventions and carrying no attribution, and
the flags in `02` accepted by every prescribed CLI; a Run on a task that turns on a deliberately ambiguous
passage of the repository's specifications, ending `blocked` with the passage and a recommended
clarification in the report; and the Consultation observations that follow, against the same
CLIs.

Each Consultation observation is named by the condition it is made under: one the observer
arranges, or, for Blocked and Skip, one that is waited on and induced where it can be. It is made
only when everything its item states is seen; a Run in which the condition held and one of those
was not seen is a failed observation, not a missing one. `RUN-20` owns the Consultation, and its
relevant Probe record is the one `RUN-20` names. What an item says of a call — made, not made,
ended — is what the observer saw of the adviser processes the Manager started, set against the
record; the record's own word that a call was or was not made witnesses nothing.
One Run may satisfy more than one of these observations, provided each one's conditions and
evidence are met.

- **Settled.** Every adviser the relevant Probe record does not read `unavailable` is called, all
  of them together, a choice settles, and the brief holds the record, with each recorded maximum
  duration at least 600 seconds.
  Every adviser process observed ran its model's command line from `PRM-1`, including the model,
  effort and the `--dangerously-skip-permissions` and `--disallowedTools` flags for claude and
  the `--dangerously-bypass-approvals-and-sandbox` flag for codex as stated there.
- **Hang.** Under each `--manager` preset, one adviser hangs rather than failing fast. Its call
  is bounded and terminated, the remaining answers decide, and the record holds the chosen
  durations, the bounds and each call's elapsed time.
- **Single-vendor.** Neither model of one vendor answers, and the other vendor's two agree. The
  choice settles and the record says the Consultation was single-vendor.
- **Blocked.** Where it can be induced: a tie, or fewer than two answers, ends the Run `blocked`
  with the full record in the Finished File and the silent models named.
- **Skip.** Where it can be induced: an adviser whose relevant Probe record reads `unavailable`
  is not called and is recorded with that verdict. Where a later relevant record in the same Run
  no longer reads it so, it is called again.

Blocked and Skip wait on conditions a release cannot produce at will. When the Runs observed for
a release held no unsettled Consultation, or no Consultation whose relevant Probe record read an
adviser `unavailable`, a statement kept with the record MUST say so, for each of the two that is
missing, so that a missing observation is a stated fact and not an omission.

The Run Directories and the commits are kept as the record. (`AGT-9`, `AGT-17`, `SEQ-8`,
`SEQ-10`, `RUN-19`, `RUN-20`, `PRM-1`)

*Amended 2026-10-15 (`rl-pq3d`, `gh-13`): Settled now names the permission-bypass and claude
deny-list flags in the prescribed adviser lines. The model and effort checks and observation
of the actual adviser processes remain; `F28` records the supplied evidence and the live
Consultation observation still open.*

**CNF-23** With `--manager codex` a Run that judges `done` ends 0 with that Finished File, the
`session` file holds the `thread_id` of the `thread.started` event the fake wrote as the pick's
first line of standard output, every judge call is given that same id, and `manager-pick.out`
still holds that output byte for byte. That Run has two Rounds — Round 1 sends the brief back,
Round 2 judges `done` — and the judge call of each is read, not the first alone. A pick that
exits 0 having written no `thread.started` event exits 2 with no Round run and the Run Directory
kept. *The ordinary Run is asserted here and not left to `CNF-11`, which reads the argument lists
and would stay green over a preset that spawns every call correctly and then exits 2.*
(`RUN-16`, `AGT-3`, `AGT-4`, `DIR-4`)

**CNF-24** The pick runs the probe exactly once, before the pick's Manager call, with `RLOOP_ROUND`
`0`, `RLOOP_ROLE` `probe`, standard input at end of file and the git toplevel as its working
directory; `probe-pick.out` holds the probe's bytes and `probe-pick.err` exists. Every ordinary
Round runs a Panel-site check after its Implementer and before any Reviewer, then a judge-site check
after every Reviewer and before its judge. The fake's own record ordinals establish this order,
separately from the executable's record names. Each check keeps its numbered `probe-<r>-panel-1.*`
or `probe-<r>-judge-1.*` captures and verdicts, with `probe-<r>.*` copying the Panel reading. An
all-down Panel makes no judge-site check and exits 2 without a judge, leaving only the Panel-site
numbered record and its copy. A Run of successive Rounds leaves each Round's records and no
`probe-0.*`: the pick's record is named for the pick, not for a Round. Each call's recorded argument
list equals `conformance/fixtures/argv/AGT-18.txt`.

The codex Manager arm independently checks the Panel-site and judge-site call order from the
fake records. (`RUN-7`, `RUN-21`, `AGT-18`, `AGT-12`, `AGT-13`, `DIR-4`, `OVR-2`, `RUN-15`)

**CNF-25** `probe-<r>.md` names every Seat exactly once, in the order `manager`, `implementer`,
`fable`, `opus`, `astra`, `sol`, `grok`, each with `unavailable` or `unknown` and nothing else, every line
ending with a newline, the last included — compared byte for byte, since command substitution
sees neither a missing final newline nor an extra blank line. With both Seats using claude
presets and their models off
`RUN-21`'s table and the probe scripted to report `Current week (Fable): 100% used`, `fable` reads
`unavailable` and the other six read `unknown` — `opus` because no line names its family,
`astra`, `sol`, `grok` and the two Seats because no model of theirs is in `RUN-21`'s table. With
`Current week (Opus): 100% used` instead, the verdicts swap: `opus` alone reads `unavailable`.
*Both rows are asserted because one row cannot tell a working table from a rule that hardcodes
`fable`.* With `--implementer claude --implementer-model claude-fable-5-1`, the Manager's model
off the table and the
`Fable` report, `implementer` reads `unavailable` and `manager` `unknown`, and the Run still
reaches its judge and ends 0. *The record is per Seat, read from each Seat's own model rather than
copied from a Reviewer's line, and a Round's verdict on the Implementer's Seat stops nothing.*
Grok's row is always `unknown`, including reports naming Grok or its model at 100%; the
unlisted-family arms and the Grok false-family mutant exercise that rule (`CNF-31`).
(`RUN-21`, `RUN-22`, `DIR-4`)

*Amended 2026-10-13 (`rl-9uu1`): the family verdict Runs explicitly select a claude Implementer,
including its Fable override. `F27` records the decision's evidence and verification.*

**CNF-26** With both Seats using claude presets and their models off `RUN-21`'s table, every Seat
reads `unknown` — `probe-1.md`
compared byte for byte, as in `CNF-25` — and the Panel still runs in full, when the probe writes
nothing; when it writes output carrying no `Current week` line; when it reports only
`Current week (all models): 100% used`; when it reports a family at `99% used`; when it writes
`Current week (Fable): 100% used` other than at the start of a line; when a family line's
`100% used` is split by a NUL byte; when it reports a family at `100% used` but **exits non-zero**;
and when it does not finish within its bound, however complete the output it would have written. In
each case the Run reaches its judge and ends exactly as the same Run does with a probe reporting
nothing exhausted. The same assertions apply to session readings at 89, 90, 99 and 101;
session text off the start of the line; a nonnumeric or NUL-split session percentage; a session
100 report with a non-zero exit; and a Probe scripted to print session 100 after exceeding its
one-second bound. Both Seats still use claude with off-table models, so their Round verdicts are
exercised too. *These are the fail-open paths and the Round boundary checks for `RUN-21`. The
NUL-split line does not begin with `RUN-21`'s prefix,
however it reads once a byte is dropped. An item that only ever saw a well-formed probe would be a
green check over a rule nobody tested. `CNF-31` drives these shapes again at
`the probe before the pick`, and says how the two sets differ.*

A failed re-check at each Round site and after a cut ends the wait and the Run finishes. (`RUN-21`,
`RUN-24`)

*Amended 2026-10-13 (`rl-9uu1`): the fail-open and Round-boundary Runs explicitly select a claude
Implementer. `F27` records the decision's evidence and verification.*

**CNF-27** With both Seats' models off `RUN-21`'s table and the probe scripted to report
`Current week (Fable): 100% used`, the Round runs no
`fable` Reviewer at all — no argument list is recorded for it — while `opus`, `astra`, `sol` and `grok` all
run; `feedback-<r>-fable.md` holds exactly `REVIEWER NOT RUN (unavailable)`, carries no
`REVIEWER FAILED`, and `reviewer-<r>-fable.err` is empty; and the Round reaches its judge and the
Run ends 0. With both `Current week (Fable): 100% used` and `Current week (Opus): 100% used` on
separate lines, `probe-1.md` records `manager:unknown`, `implementer:unknown`,
`fable:unavailable`, `opus:unavailable`, `astra:unknown`, `sol:unknown` and `grok:unknown`, in that order, each
line ending with a newline. Neither `fable` nor `opus` is called; `astra`, `sol` and `grok` all run.
Each omitted Reviewer's Feedback File contains exactly the not-run line above, with its terminating
newline and no extra content, and its `.err` file exists and is empty. In both cases the judge
is called with every Panel Feedback File path, including those of the omitted Reviewers; with
the called Reviewers succeeding and the judge scripted to finish done, the Run produces its
Finished File and exits 0. With `fable` omitted and every called Reviewer failing, the Run
instead exits 2, calls neither the judge-site Probe nor the judge and produces no Finished File. With both Seats using the codex
preset and off-table models, a Round reporting session 100 has the same exact record, omitted
Reviewer files, surviving Reviewers, judge arguments and successful completion as the both-family
arm. The preset recommendations are not asserted: `RUN-22` states the message
`SHOULD instead name the relevant preset flag`.
`CNF-15` owns the other literal. *An Implementation that reused one literal for both would pass
every other item, and the Manager reads the two as different things (`PRM-2`).* (`RUN-7`, `RUN-8`, `RUN-15`,
`RUN-21`, `PRM-2`, `DIR-4`)

*Amended 2026-10-13 (`rl-9uu1`): the all-down arm explicitly selects a claude Implementer; the
explicit codex session arm and Reviewer omission assertions are preserved. `F27` records the
decision's evidence and verification.*

**CNF-28** With `--implementer claude`, both Seats at the claude preset's default model and the
probe before the pick scripted to report
`Current week (Opus): 100% used · resets Sep 24, 3pm (UTC)`, the executable exits 2, and **no
Manager, Implementer or Reviewer argument list is recorded** — the probe's own is, exactly once;
standard output is empty; standard error names `claude-opus-5-5`, that line, reset and all, and
both `manager` and `implementer`, since both Seats are `unavailable` and `RUN-22`'s message names
`the Seat — both, when both are`; the Run Directory holds exactly `probe-pick.out`,
`probe-pick.err` and `probe-pick.md`; and `probe-pick.md` reads `manager:unavailable`, `implementer:unavailable`,
`fable:unknown`, `opus:unavailable`, then `unknown` for `astra`, `sol` and `grok`. With `--manager-model
claude-fable-5-1`, the Implementer's model off the table and `Current week (Fable): 100% used`
instead, the Run is refused the same way and standard error names `claude-fable-5-1`. The pick is
scripted to fail. Here and in `CNF-29` and `CNF-30`, standard error names a Seat when the Seat's
word stands whole in what is left of standard error once every `manager-model` and
`implementer-model` is deleted together with any dashes before it, then `--manager` and
`--implementer` are removed.
*The spawn record is the
assertion: a Run that spawned a Manager which then failed also exits 2, so the status alone passes
an Implementation that ignores the refusal. The second Run is there because one row cannot tell a
Seat read from its own model from a rule that hardcodes `opus`. The flag names go first because
`RUN-22`'s message `SHOULD name the flag that chooses another model` for family refusals and
recommends preset flags for session refusals, and each flag's name carries a
Seat's word, so a message naming the flag and no Seat would otherwise pass.* (`RUN-22`, `RUN-21`,
`DIR-4`, `RUN-10`)

*Amended 2026-10-08 (`rl-4i7t`): the default-model refusal now exercises Opus and the Manager override exercises
Fable, preserving both family rows.*

With session 90 before the pick, `--implementer claude` and both Seats at the claude preset's
default model, the same refusal assertions hold, now
with both claude Reviewers `unavailable` too and the session line quoted verbatim, reset included.
With a codex Implementer, independently refuse only the claude Manager, both on its default model
and on `claude-sonnet-5` and `gpt-6-astra`, under session 90, 090 and 101. Each exact record has
only `manager`,
`fable` and `opus` unavailable. This exposes base-ten reading, the pick's inclusive threshold,
and off-table session exhaustion. Under `--auto`, session 90 exits 2 with empty standard output,
no agent spawned and exactly one Probe before the pick: the Sequence stops there (`SEQ-6`).
The recommended flags are not pass/fail assertions: `RUN-22` states
`SHOULD instead name the relevant preset flag`.

*Amended 2026-10-13 (`rl-9uu1`): the two-Seat refusals explicitly select a claude Implementer at
that preset's default model, preserving independent Manager refusal coverage. `F27` records the
decision's evidence and verification.*

With the default codex Implementer and default claude Manager, a pick report with session 100
followed by Opus 100 refuses only the Manager's Seat: exit 2, no agent call, empty standard output,
and only the pick captures in the Run Directory. The exact record has only `manager`, `fable` and
`opus` unavailable. Standard error quotes both full lines, reset text included, in report order,
comparing their first byte offsets in the whole stream without constraining line layout or
surrounding text.

*Amended 2026-10-23 (`rl-kyhr`): add the pick refusal with both readings exhausting the Manager's
Seat, requiring both quoted lines in report order under `RUN-22`.*

**CNF-29** With `--implementer claude`, the Manager's model off `RUN-21`'s table, the
Implementer's at the claude preset's default and the probe before the pick reporting
`Current week (Opus): 100% used`, the executable exits 2 with no
Manager, Implementer or Reviewer argument list recorded, standard output empty, the Run Directory
holding the three `probe-pick.*` files alone, `probe-pick.md` reading `manager:unknown` and
`implementer:unavailable`, and standard error naming `implementer`, `claude-opus-5-5` and the
probe's line. With `--implementer-model claude-fable-5-1` and `Current week (Fable): 100% used`
instead, the Run is refused the same way and standard error names `claude-fable-5-1`. Of standard
error the item asserts presence only. `RUN-22` states `a message naming the Seat — both, when both
are — its model, and the reset the probe reported`, and bounds the stream no further; `RUN-10`
states `Progress and diagnostics go to standard error and their wording is not specified`. The pick
is scripted to fail. *Again the spawn record, not the status, is what an Implementation that
refuses only for the Manager's Seat fails. The second Run is there because one row cannot tell a
Seat read from its own model from a rule that hardcodes `opus`, and a per-Seat or per-site lookup
can get one Seat's row right and another's wrong. A message naming both Seats unavailable when only
one is passes here, since no sentence in the set forbids it; the per-Seat reading stays asserted
where it is observable, in `probe-pick.md` above.* (`RUN-22`, `RUN-21`, `DIR-4`, `RUN-10`)

*Amended 2026-10-08 (`rl-4i7t`): the default Implementer refusal now exercises Opus and its override exercises
Fable, preserving both family rows.*

With a codex Manager and session 90 before the pick, independently refuse the claude Implementer
on its default model and on `claude-sonnet-5` and `gpt-6.1-sol`. Each Run satisfies the same refusal
assertions,
including the model, Seat and verbatim session line with reset on standard error, and an exact
record with `implementer`, `fable` and `opus` unavailable and the other Seats unknown.

*Amended 2026-10-13 (`rl-9uu1`): Implementer refusals explicitly select claude, preserving both
family rows and session readings on default and overridden models. `F27` records the decision's
evidence and verification.*

**CNF-30** With `--implementer claude`, the Manager's model at its default and the Implementer's off
`RUN-21`'s table, the probes before the pick and in Round 1 reporting nothing exhausted, Round 2's
reporting `Current week (Opus): 100% used`, and Round 1 judged `rewrite`: the executable exits 2;
`manager-judge-1.out` exists and **`manager-judge-2.out` does not**, nor is a Round 2 judge argument
list recorded; Round 2's Implementer ran and its Panel ran without `opus` — `fable`, `astra`,
`sol` and `grok` called, `feedback-2-opus.md` exactly the not-run line; `probe-2.md` reads
`manager:unavailable` and `opus:unavailable`, every other Seat `unknown`; there is no Finished File
and standard output is empty; and standard error names `manager`, `claude-opus-5-5` and the probe's
`Opus` line, reset and all, since `RUN-22` exits `with the message above for the Manager's Seat`,
which names the reset by `quoting verbatim every line that establishes that Seat's exhaustion`. With
Round 1's probe reporting `Opus` instead, the Run exits 2 with no `manager-judge-1.out`, and
standard error names the same three. With `--manager-model claude-fable-5-1` and `Current week
(Fable): 100% used` instead, both Runs go the same way with `fable` in `opus`'s place, and standard
error names `claude-fable-5-1`. The withheld judge is scripted to fail. *The missing judge is the
assertion: a Run whose judge was called and failed also exits 2. The second pair of Runs is there
because one row cannot tell a Seat read from its own model from a rule that hardcodes `opus`, and a
per-Seat or per-site lookup can get one Seat's row right and another's wrong.*

With `--implementer claude` and both Seats on off-table models, repeat a Round 1 refusal for
session 100 and 0100.
The exact Probe record makes both Seats and both claude Reviewers unavailable, leaving astra,
sol and grok unknown. The pick and Implementer each ran once; both codex Reviewers and Grok ran once; neither
claude Reviewer nor the judge ran. Each omitted Reviewer has the exact not-run Feedback File and
an existing empty `.err`; no judge output or Finished File exists, standard output is empty, exit
is 2 and standard error names the Manager, its model and the session line verbatim with its reset.
For each reading, separate Runs inject Task File and Finished File Interference after the
Implementer and after the Panel (using the surviving astra Reviewer). Each leaves the Task File
equal to its snapshot and both rejected files present, demonstrating both Checkpoints despite the
withheld judge.

Further arms recover at either Round site from session 100 to clear: the Panel calls its claude
Reviewers after recovery, and the judge-site recovery re-runs no review; each Reviewer identity is
recorded exactly once. Numbered captures keep the initial reading, each site's exact names, final
byte-exact verdicts and the Panel's byte-identical copy. An Opus Manager waits on session 100 beside
an exhausted Fable family, since that family does not exhaust its Seat. A matching weekly reading,
alone or beside session 100, expires at once at either site and in a post-cut wait, quoting the
matching family line in family-only arms, and both full lines, reset text included, in the report's
order when both match. A separate Panel-site arm reports Opus before session 100 to distinguish
report order from a fixed order. The first occurrence of each full line in the whole standard error
is compared by byte offset, allowing either line layout and surrounding text. Expiry before the
Panel still completes it and the Checkpoint and makes no judge-site check; expiry at the judge site
preserves the Panel copy. The expiry arms use `--quota-wait 5 --quota-poll 2`, assert exact fake
call counts, retained Checkpoint evidence and the last check's reset line on stderr, with differing
reset text on that last check alone. (`RUN-22`, `RUN-21`, `RUN-7`, `RUN-10`, `DIR-4`, `RUN-24`,
`DIR-6`)

*Amended 2026-10-08 (`rl-4i7t`): the default Manager now exercises Opus in both Rounds; the Fable pair
uses an explicit Manager override.*

*Amended 2026-10-13 (`rl-9uu1`): the refusal and Checkpoint Runs explicitly select a claude
Implementer. `F27` records the decision's evidence and verification.*

*Amended 2026-10-23 (`rl-kyhr`): require both quoted lines in report order at the Panel, judge and
post-cut sites when both readings exhaust the Manager's Seat, including a report with Opus first.*

**CNF-31** With both Seats using claude presets and their models off `RUN-21`'s table and the
probe before the pick reporting
`Current week (Fable): 100% used`, or `Fable` and `Opus` both at 100%, the Run starts — the pick
is called — and ends 0, and `probe-pick.md` reads `manager:unknown`, `implementer:unknown` and
the Reviewers' lines `CNF-25` and `CNF-27` give those reports. With both Seats using claude presets
explicitly on
`claude-fable-5-1`, matching the family in the malformed, failed and timed-out reports, the Run
starts and ends 0, every Seat `unknown` in `probe-pick.md`, when the probe before the pick writes
nothing; writes no usage line; reports only `Current week (all models): 100% used`; reports only
families outside the table, including Grok and its model; reports `99% used`; writes `Current week (Fable): 100% used` other
than at the start of a line; writes a family line whose `100% used` is split by a NUL byte;
reports a family at `100% used` but **exits non-zero**; or does not finish within `--probe-timeout
1`. *This is what shows fail-open reaches the pick: the pick being called is the assertion, since
a refused Run and an agent that failed both end without a Finished File. On those Fable overrides the
Manager's or the Implementer's Seat misread `unavailable` here refuses the Run under `RUN-22`.
Both sites drive these shapes in one order but not the same set: this one adds the families
outside the table, and leaves out the Run `CNF-26` compares against, `with a probe reporting
nothing exhausted`, which is that item's control rather than a fail-open shape.*
(`RUN-21`, `RUN-22`)

*Amended 2026-10-08 (`rl-4i7t`): the malformed, failed and timed-out reports keep both Seats on explicit Fable
overrides so an incorrectly accepted report would still refuse the Run.*

Two further Runs omit both `--implementer` and `--implementer-model`: one selects
`--manager codex` with session 90 before the pick; the other selects
`--manager-model claude-sonnet-5` with an exhausted Opus family. Each records
`manager:unknown` and `implementer:unknown` in byte-exact `probe-pick.md`, with both claude
Reviewers unavailable for the session report and only `opus` unavailable for the family report;
`astra`, `sol` and `grok` remain unknown. The pick is scripted to fail: exit 2, empty standard output,
no Finished File, exactly one Probe and one pick, no other calls and the spawn trace `pick`.
Missing records or spawns fail with an omitted-Implementer-preset label. *A runtime command
that defaults to codex while Probe processing still assigns the omitted preset to claude can
exit 2 too; the record and spawn assertions distinguish it.*

The pick's fail-open arms also include session 89, non-anchored, nonnumeric and NUL-split session
text, a failed session-100 Probe and a Probe scripted to print session 100 after its one-second
bound. Both claude Seats are explicitly on Fable; every Seat is unknown in the exact pick record,
the pick runs and the Run finishes. With codex Manager and Implementer presets and the same
claude-looking off-table model literal, session 100 at the pick-site, Panel-site and judge-site
checks leaves those Seats unknown, both claude Reviewers unavailable and both codex Reviewers and Grok
unknown. Assert the exact pick record and Panel copy, and the full spawn trace: pick,
Implementer, astra, grok and sol, judge. With a codex Manager and an
off-table claude Implementer, a Round's session 100 instead records the Implementer unavailable
but leaves that same spawn trace and successful completion. Finally, session 89 beside an
exhausted Fable family at the pick-site, Panel-site and judge-site checks leaves both off-table
claude Seats unknown, omits only fable and still finishes, with the exact pick record and Panel
copy and the complete spawn trace asserted: a low session reading cannot erase family exhaustion.

*Amended 2026-10-13 (`rl-9uu1`): claude fail-open and Round-verdict Runs explicitly select that
preset; omitted-preset Runs now assert the codex Implementer's Probe verdict and the pick spawn.
`F27` records the decision's evidence and verification.*

**CNF-32** The pick's prompt argument equals `PRM-1`'s fixture rendered as in `CNF-12`, with
`{{UNAVAILABLE}}` as the Probe before the pick leaves it, compared byte for byte in four Runs of
this item's own, each of which starts, calls the pick and ends 0. With the default models and that
Probe reporting `Fable` at 100%, `{{UNAVAILABLE}}` is the one line `fable`. With both Seats' models
off `RUN-21`'s table and `Opus` at 100%, it is the one line `opus`. With both Seats' models off
the table and `Fable` and `Opus` both at 100%, it is `fable`, a newline and `opus`, in that order
and nothing else. With the default models and a Probe reporting nothing exhausted, it is the empty
string: the prompt is the fixture with the placeholder replaced by nothing. *The empty form is
asserted here, and not left to `CNF-12`, because each form alone passes a wrong Implementation: one
that renders the list whatever the Probe said passes the populated Runs, and one that never renders
it passes the empty one. Each Seat has a Run of its own because no single Run can tell a working
render from one that hardcodes a Seat, the same argument `CNF-25` and `CNF-28` make of one row of
the table. The Seats are chosen so that no Run is refused (`RUN-22`): on the invocation's default
models an `Opus` report exhausts the Manager's Seat and refuses the Run before any pick prompt
exists, so the Runs that report it put both Seats off the table.*
(`PRM-1`, `PRM-6`, `RUN-21`, `RUN-20`, `RUN-22`)

*Amended 2026-10-08 (`rl-4i7t`): the default-model populated prompt now reports Fable; Opus reports use models
off the table so each prompt-rendering Run reaches the pick.*

*Amended 2026-10-13 (`rl-9uu1`): default-model prompt Runs now use the codex Implementer; the
Opus and both-family arms explicitly select claude on off-table models. Opus still refuses through
the default claude Manager. `F27` records the decision's evidence and verification.*

**CNF-33** With the default Manager preset a Run of two Rounds — Round 1 judges `rewrite`, Round 2
judges `done` — ends 0, and the recorded argument list of the judge call of each of those two
Rounds carries the `session` file's id, in a Run of this item's own: `RUN-16` says `every judge
call resumes it`, and a Run that ran one Round, or a reading that found no judge call, is a
failure here rather than a silent pass. *Why this is not left to `CNF-11`, which reads each Run's
Round 1 judge call alone, is `CNF-23`'s rationale, which holds of either preset.* (`RUN-16`,
`AGT-4`, `DIR-4`)

**CNF-36** A cut judge attempt waits sleep-first and retries with the same argument list and
rendered prompt, including the session id, as attempt 1. The original stdout and populated stderr
captures stay byte-identical, the retry's output has its own `-retry-1` name and is compared in
full, and exact capture listings assert every numbered check and attempt. With every re-check
failing open and every attempt cut, the requested-sleep budget alone bounds attempts and checks;
waits spent before the Panel reduce the remaining retries. A slow check spends no sleep budget.
Recovery at the final paid check still proceeds. A cut with no remaining budget makes no further
check and quotes its own output line on stderr.

The cut near-misses are exit zero; stderr only; no final newline; same-line text before the
prefix; text before the line; the supplied tetasm report; a NUL inside the prefix; a NUL after
the newline; hypothetical weekly-limit wording; a timed-out attempt that printed the line; and
a call that wrote a Finished File or rewrote the Task File before printing it. Each keeps the
ordinary failure outcome with no post-cut check or retry, and leaves any decision files in place.
A codex Manager is never retried. A cut pick exits 2 after its sole pick with no Round. Positive
controls carry an arbitrary suffix, ignore stderr and accept a nonzero status other than 1
(7, 124 and 137), including own exits 124 and 137 with a silent SIGTERM-ignoring child whose reap
outlasts the Manager timeout. Plain cuts also retry with an invalid inherited `LC_ALL=xx_YY.UTF-8` and an
exported `BASH_FUNC_foo-bar%%=() { :; }`. Each added control requires exit 0, two judge attempts,
both retry captures and the byte-identical first stdout capture; neither stderr's contents are
asserted in the caller-environment controls.

During a 25-second poll, SIGINT and SIGTERM sent to the executable's PID produce exit 2 and
`interrupted` within 3 seconds. A signal during a re-check terminates and reaps that check's group
before returning exit 2 with `interrupted`, also within 3 seconds. These add clock-measured claims
to the rows `CNF-35` names. (`RUN-24`, `AGT-4`, `PRM-2`, `PRM-6`, `DIR-4`, `RUN-11`, `AGT-15`)

*Amended 2026-10-24 (`rl-ypm7`): add the own-exit, straggler and caller-environment positive
controls above. `RUN-24` says `A timed-out attempt is never cut` and
`A cut MUST begin the sleep-first wait above using the Round's remaining budget`;
`AGT-15` says `The reaping leaves the call's exit status the spawned process's`.
The straggler controls separate process execution from the following reap.*

## Not testable black-box

These requirements have no item because no black-box observation decides them; each says why.

| requirement | why |
|---|---|
| `DIR-8` | a Run Directory deleted under the executable is an OS race the suite can only approximate; the executable's exit 2 on a missing snapshot is asserted inside `CNF-9`'s Run by deleting `task-1.md` between the Implementer and the Panel, which is as close as a fake gets |
| `DIR-9` | a threat model: a statement of what is out of scope, with nothing to observe |
