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
suite MUST expand every path it reads without splitting it on a space or a tab. A newline in it is
not supported; `07-open-findings.md` records why.
(`00-overview.md`)

**CNF-2** The suite puts fake `claude` and `codex` executables first on `PATH`. A fake reads
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
directory sits between the two. `cmp` and `find` are the suite's own and are not on the
executable's `PATH`. An executable that relies on anything more brings it itself; a wrapper that
puts its own inputs on `PATH`, as a nix `writeShellApplication` does, satisfies this. *Why the
host's `PATH` is withheld: rloop-bash `02c6206` compared `task.md` against `task-<r>.md` with
`cmp`, which its flake did not wrap, and read a missing `cmp` as "differs". The Run `RUN-12`
describes — `rloop MUST exit 2 rather than start another Round` — then burns every remaining
Round on the same brief instead of ending at the no-decision one, and every Round's Task File
goes where `DIR-6`'s `move task.md to rejected-<r>-task.md` sends it; on a host with diffutils on
`PATH`, the suite could not tell.* (`AGT-13`)

## The scenarios

**CNF-3** For every line of `conformance/scenarios.tsv` the suite MUST run the executable in a
fresh git repository with the line's script loaded into the fakes, `--max-rounds` set to the
line's cap, and `--manager-model` and `--implementer-model` set from the line's `seats` column,
and assert the exit status equals the line's and the recorded spawns equal the line's
trace — a Panel compared as the set of the Reviewers rloop called, the rest in order, and a Run
refused at the pick as no spawn at all. The file is
what `tools/formal/` enumerates (`ADR-0002`, `tools/check_scenarios.py`). A line whose `seats` is
`-` — every line the enumeration held before `RUN-22` — is replayed with both Seats on a model
`RUN-21`'s table does not name, `claude-sonnet-5`, and with a probe before the pick reporting
nothing exhausted; any other line names the Seats on the table's models and what that probe
prints. *Those older lines were written for Runs no Seat's verdict could stop, and a replay on the
default models would now refuse or cut short the ones whose probe reports `Fable`; the column is
where the file says so, rather than a replay that assumes it.* This item is the executable form
of the decision table and the Round: (`RUN-5`, `RUN-6`, `RUN-7`, `RUN-9`,
`RUN-10`, `RUN-11`, `RUN-12`, `RUN-13`, `RUN-14`, `RUN-15`, `RUN-21`, `RUN-22`, `DIR-5`, `DIR-6`,
`DIR-7`, `OVR-1`)

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
(`AGT-1`, `AGT-2`, `SEQ-3`, `SEQ-5`, `SEQ-6`)

**CNF-6** Outside a git working tree the executable exits 2 and spawns nothing. (`RUN-1`)

**CNF-7** With `--run-dir` naming an existing directory (empty or not) or a path whose parent does
not exist, the executable exits 2 and spawns nothing. With `--run-dir` naming a fresh path, the
directory exists afterwards and is the only one created. (`DIR-1`, `DIR-3`)

**CNF-8** Without `--run-dir`, in a repository whose path the suite gives a space and a tab
independently of `TMPDIR`, the Run Directory is created under `<toplevel>/.rloop/runs/`,
`<toplevel>/.rloop/.gitignore` holds exactly `*` and a newline — compared byte for byte — and
`git status --porcelain` prints nothing after a Run whose fakes changed no tracked file.
Separate Runs, also without `--run-dir` and with fakes that change no tracked file, use repository
paths chosen by `mktemp` without deliberately adding whitespace. A pre-existing `.gitignore` of
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
(`DIR-4`, `RUN-17`, `RUN-23`)

## What agents receive

**CNF-10** Every fake records the five variables with the values `AGT-13` gives its role and
Round, `RLOOP_REVIEWER` unset except for Reviewers, its working directory equal to the git
toplevel, and standard input at end of file on first read. (`AGT-12`, `AGT-13`)

**CNF-11** For each role the recorded argument list equals the fixture in
`conformance/fixtures/argv/` with the placeholders filled in: the pick's `<session id>` is the
`session` file's content and each Run's Round 1 judge call, the one read here, carries that same
id — the item that reads a Run's judge calls all is `CNF-23` under `--manager codex` and `CNF-33`
under the default preset; `<manager model>` is `--manager-model`'s value, or the preset's default;
`<implementer model>` is `--implementer-model`'s value, or the preset's default, asserted for the
claude default, the codex default and a non-default value given on the command line;
`--manager codex` produces `AGT-3`'s and `AGT-4`'s second lists and the default produces their
first; `--implementer codex` produces `AGT-6`'s list and the default `AGT-5`'s; the four
Reviewers' lists are `AGT-7`, `AGT-8` and `AGT-10`'s, one each, with their `RLOOP_REVIEWER` names.
One further Run has the repository's own path and its `--run-dir` path each hold a space and a tab,
and every role's list — the pick's, the Implementer's, the four Reviewers' and the judge's — equals
its fixture with those paths' bytes unchanged; the suite makes both paths itself rather than
reading either out of `TMPDIR`, so no verdict here moves with what the caller exported. (`AGT-3`,
`AGT-4`, `AGT-5`, `AGT-6`, `AGT-7`, `AGT-8`, `AGT-10`, `AGT-11`, `RUN-16`, `RUN-23`, `OVR-2`)

**CNF-12** For each role the recorded prompt argument equals the fixture in
`conformance/fixtures/prompts/` rendered by `PRM-6` with the values the suite knows: the Run
Directory's paths, the base hash, the Round, `--max-rounds`, the caller's instruction (given and
absent), the dirty-at-start list (a tree with one modified and one untracked path, and a clean
tree), the unavailable list, empty in each of these Runs since no Probe before the pick here
reports anything exhausted (`CNF-32` asserts it populated, and empty in a Run of its own), and the
four Feedback File paths in order. One further Run gives an instruction holding placeholder names
(`{{TASK_FILE}}`, `{{UNAVAILABLE}}`, `{{ROUND}}`) together with a backslash, `&` and `%s`, and a
`--run-dir` path holding `{{INSTRUCTION}}`; its pick, Implementer and judge prompts equal their
fixtures with each value's bytes unchanged, as `PRM-6` renders them. A further Run, the one
`CNF-11` reads the argument lists of, has the repository's own path and its `--run-dir` path each
hold a space and a tab; every role's prompt — the pick's, the Implementer's, the four Reviewers'
and the judge's — equals the fixture rendered with the paths the suite handed the executable, byte
for byte. Each rendered prompt ends with `PRM-5`'s sentence. (`PRM-1`, `PRM-2`, `PRM-3`, `PRM-4`,
`PRM-5`, `PRM-6`, `RUN-3`, `RUN-23`, `DIR-10`)

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
The same Round once more with `--kill-after 2`, every Reviewer fake spawning a child that ignores
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

## Concurrency, time and signals

**CNF-16** With every Reviewer fake sleeping 2 seconds, a Round's Panel completes in under 5
seconds, and every Reviewer's recorded start precedes every Reviewer's recorded end. (`RUN-8`)

**CNF-17** With `--reviewer-timeout 1 --kill-after 1`, one Reviewer fake sleeping 30 seconds and
spawning a child that ignores SIGTERM, and the other three answering: the Run exits 0, the slow
Reviewer's Feedback File carries `REVIEWER FAILED`, the other three hold the fakes' answer, the
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
a Task File, the Implementer and all four Reviewers succeed and the judge writes `STATUS: done` —
each Manager fake exiting 0 having spawned a child that ignores SIGTERM: the Run exits 0; no call of
the Run records any of those children among the children alive when it started, nor the pick's or
the Implementer's own process among the calls alive when it started; and once the executable has
returned, neither a fake that spawned one nor any of the children is running. The same Run with the
Implementer fake spawning that child instead of the Manager's. The same Run with every Reviewer fake
spawning it: the judge's record — the first call to start once every Reviewer has exited — carries
no Reviewer's child among the children alive when it started and no Reviewer's own process among the
calls alive when it started. The same Run with both of the Run's probes spawning it: the pick's
record carries neither the child nor the own process of the probe before the pick, and each of the
Panel's four records carries neither the child nor the own process of the Round's probe. Neither of
those two Runs can pass on absent evidence: a missing record, a missing snapshot line, a missing
recorded pid and a Panel of other than four records are each red. A further Run of the Implementer's
shape, the Implementer fake also appending to the Task File and its child polling for
`rejected-1-task.md` under the Run Directory rather than sleeping: the Run exits 0,
`rejected-1-task.md` is there, the child recorded that it was watching before its fake exited, and
it never found the file — so the Implementer's group was gone before the Checkpoint that follows its
call, and not only before the next call. Two Runs more of the probes' shape, one for each of
`RUN-21`'s call sites, every probe's child polling under the Run Directory rather than sleeping: for
the record the probe before the pick writes, `probe-pick.md`, and for the record the Round's probe
writes, `probe-1.md`. In each the Run exits 0, that record is there, the probe whose own record is
the watched one recorded that it was watching before its fake exited, and its child never found the
file — so that probe's group was gone before rloop wrote that record, and not only before the next
call. Neither Run passes on absent evidence either: a missing record, a missing readiness marker, a
fake that exited before its child published one and a child whose pid is unrecorded or still running
once the executable has returned are each red. A last Run of the probes' shape, for the read of a
probe's output rather than for the record: every probe's child writing to the standard output it
inherited rather than sleeping — one second after its own fake has exited, the line `Current week
(Fable): 100% used` — and `--kill-after 4`. The Run exits 2, the probe before the pick is the only
call it makes, that line is in `probe-pick.out`, `probe-pick.md` records the Manager's Seat, the
Implementer's and `fable` unavailable and the other three unknown, and the child's pid is recorded
and not running once the executable has returned — so rloop read that probe's output after reaping
its group and not before. Nor does that Run pass on absent evidence: a line that never reached the
capture leaves the read nothing to witness and is red.
*A call that exits 0 is what `AGT-14`'s `At the limit` never reaches, and leaving a check running is
a habit `07-open-findings.md`'s `F16` records: the child of a healthy Implementer writes into the
working tree through the whole Panel and the Manager's commit. `CNF-17` reads the same record for
the reaping after a timeout. The pick's and the Implementer's own processes are read from every
later record, each Reviewer's from the judge's record alone, and each probe's from the call that
follows it (`RUN-21`, `RUN-7`). What `RUN-8` forecloses is a *sibling* Reviewer's record, having the
Panel's Reviewers spawned so that `none waits for another to finish`: a Reviewer that finds a
sibling's process — or a sibling's child — alive has found that working, which is why the judge, the
call after the whole Panel, is where a Reviewer is read. The Checkpoint starts no call, so no record
of a later one speaks for that boundary and the straggler is the witness; the appended Task File is
what makes `DIR-6` `move task.md to rejected-<r>-task.md` there, and the child's recorded readiness
is what keeps its silence from passing for compliance. Each probe's record starts no call either,
and `AGT-15`'s `A call is complete only once its process group has been reaped that way` puts it
after the reaping, so the same straggler witnesses it; `RLOOP_FAKE_WATCH` carries one name, which is
why the two call sites take a Run each and each Run reads the watching probe's tag alone. What that
straggler establishes is the record and not the read: `AGT-15` has `rloop MUST read the call's
output, and do anything else that follows the call` come `only after that`, and a child that never
finds the record witnesses the second of those and not the first. Reading the output leaves no file
for a straggler to poll, so the last Run gives the read a straggler that writes where those poll:
into the capture `DIR-4` has the probe's standard output reach `entire and unmodified`, so that
an executable which reads before reaping reads bytes that line has not arrived in yet. The probe
before the pick is that Run's site because `RUN-22` ends the Run on its verdicts — `exit 2 without
spawning any agent` — which makes a verdict derived from the wrong bytes a Run that calls the pick
and goes on. Its window has margin at both ends: the child's first write is a second after its own
fake exits, which a read before the reaping is well inside, and `--kill-after 4` keeps that child
alive three seconds past that write, which a read after the reaping falls past, the line having
reached the capture three seconds before that read. `F17` names the boundaries this item still reads
at the next call alone.*
(`AGT-15`, `AGT-16`, `DIR-4`, `DIR-6`, `RUN-21`, `RUN-22`)

**CNF-35** With one Round, `--kill-after 1`, the `fable` Reviewer fake sleeping 10 seconds while the
other three answer at once, and every Reviewer fake spawning a child that ignores SIGTERM: the child
the `opus` fake left is gone within 6 seconds of `opus`'s own recorded exit, and at that moment the
Panel is four Reviewer records each carrying a child, `fable`'s own recorded process is running and
`fable` has not recorded its exit; the Run ends 0, and neither a fake that spawned a child nor any
child is running once the executable has returned. Then the same Round with `--kill-after 5` and no
Reviewer sleeping, so that the four exit within a moment of one another: each of the four children
is gone within 9 seconds of its own Reviewer's recorded exit. Neither row passes on absent
evidence: a Panel of other than four records, a Reviewer that recorded no child, and one whose fake
recorded no exit, are each red. (`AGT-15`, `RUN-8`)
*`AGT-15` has `Reviewers run concurrently` and `so each Reviewer's group is reaped as that Reviewer
exits`, and these are the two ways an Implementation reaps them in some other order anyway. The
first row is the roster: a Panel waited for in the fixed order `fable`, `opus`, `astra`, `sol` keeps
an early Reviewer's group until every Reviewer named before it has exited too — up to
`--reviewer-timeout` of an orphaned build or check writing into the working tree while the rest of
the Panel reviews it — and `opus` is the one read because `fable`, the Reviewer ahead of it, is the
one still running. That `fable` runs is read from `fable`'s own recorded process, and the Panel's
records are counted rather than assumed, because every other read of the row is about `opus` alone:
an Implementation that called one Reviewer would satisfy all of them, and the survival clause says
nothing about a record that was never written. `fable`'s missing end line is read as well and not
instead, a Reviewer the executable has not yet reaped being a zombie whose pid still answers. The
second row is the grace: a reap that blocks the wait loop leaves the Reviewer that exits next
unsignalled until the previous group's grace has ended, so the second child of four goes two graces
past its own Reviewer's exit and the fourth four. `CNF-34` sees neither, reading each Reviewer
against `the first call to start once every Reviewer has exited`, by which time every
delay above has ended. Each bound is its row's grace and a margin, five seconds and four, because
the claim is that a group goes with its own Reviewer and not that it goes in any particular tenth of
a second: these rows with `CNF-16` and `CNF-17` are the suite's only clock-measured claims, and a
tight bound is a flaky suite. `--kill-after 5` in the second row rather than 1 is what carries the
shape it separates from past nine seconds at all, and that margin is not wide at every child: the
second Reviewer's two graces are ten seconds and clear the bound by one. It is the third child and
the fourth, three graces and four — fifteen seconds and twenty — that the bound separates widely,
while the first, whose group waits on nothing, is not separated at all.*

**CNF-18** SIGINT sent to the executable while an Implementer fake sleeps, having spawned a child
that ignores SIGTERM: the fake records SIGTERM, the executable exits 2 with `interrupted` on
standard error, neither the fake nor its child survives, and the Run Directory is intact. The
same with SIGTERM. The same once more with a **Probe** (`AGT-18`) in the Implementer's place: SIGINT
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
once the call has returned is `CNF-34`'s to witness, at both call sites; registering it with the
handler is this item's, and the Probe is the role whose call an Implementation is likeliest to write
inline rather than through the machinery every agent call shares. The call site driven is `RUN-21`'s
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
the flags in `02` accepted by both CLIs; a Run on a task that turns on a deliberately ambiguous
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
  of them together, a choice settles, and the brief holds the record.
  Every adviser process observed ran its model's command line from `PRM-1`, including the model,
  effort and read-only flags as stated there.
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

**CNF-23** With `--manager codex` a Run that judges `done` ends 0 with that Finished File, the
`session` file holds the `thread_id` of the `thread.started` event the fake wrote as the pick's
first line of standard output, every judge call is given that same id, and `manager-pick.out`
still holds that output byte for byte. That Run has two Rounds — Round 1 sends the brief back,
Round 2 judges `done` — and the judge call of each is read, not the first alone. A pick that
exits 0 having written no `thread.started` event exits 2 with no Round run and the Run Directory
kept. *The ordinary Run is asserted here and not left to `CNF-11`, which reads the argument lists
and would stay green over a preset that spawns every call correctly and then exits 2.*
(`RUN-16`, `AGT-3`, `AGT-4`, `DIR-4`)

**CNF-24** The pick runs the probe exactly once, before the pick's Manager call, with
`RLOOP_ROUND` `0`, `RLOOP_ROLE` `probe`, standard input at end of file and the git toplevel as its
working directory; `probe-pick.out` holds the probe's bytes and `probe-pick.err` exists. Every
Round runs the probe exactly once, after that Round's Implementer and before any of its Reviewers
starts, keeps `probe-<r>.out` byte for byte as the probe wrote it, and leaves a `probe-<r>.err`. A
Run of two Rounds leaves `probe-pick.*`, `probe-1.*` and `probe-2.*` and no `probe-0.*`: the
pick's record is named for the pick, not for a Round. Each call's recorded argument list equals
`conformance/fixtures/argv/AGT-18.txt`. (`RUN-7`, `RUN-21`, `AGT-18`, `AGT-12`, `AGT-13`,
`DIR-4`, `OVR-2`)

**CNF-25** `probe-<r>.md` names every Seat exactly once, in the order `manager`, `implementer`,
`fable`, `opus`, `astra`, `sol`, each with `unavailable` or `unknown` and nothing else, every line
ending with a newline, the last included — compared byte for byte, since command substitution
sees neither a missing final newline nor an extra blank line. With both Seats' models off
`RUN-21`'s table and the probe scripted to report `Current week (Fable): 100% used`, `fable` reads
`unavailable` and the other five read `unknown` — `opus` because no line names its family,
`astra`, `sol` and the two Seats because no model of theirs is in `RUN-21`'s table. With
`Current week (Opus): 100% used` instead, the verdicts swap: `opus` alone reads `unavailable`.
*Both rows are asserted because one row cannot tell a working table from a rule that hardcodes
`fable`.* With `--implementer-model claude-fable-5-1`, the Manager's model off the table and the
`Fable` report, `implementer` reads `unavailable` and `manager` `unknown`, and the Run still
reaches its judge and ends 0. *The record is per Seat, read from each Seat's own model rather than
copied from a Reviewer's line, and a Round's verdict on the Implementer's Seat stops nothing.*
(`RUN-21`, `RUN-22`, `DIR-4`)

**CNF-26** With both Seats' models off `RUN-21`'s table, every Seat reads `unknown` — `probe-1.md`
compared byte for byte, as in `CNF-25` — and the Panel still runs in full, when the probe writes
nothing; when it writes output carrying no `Current week` line; when it reports only
`Current week (all models): 100% used`; when it reports a family at `99% used`; when it writes
`Current week (Fable): 100% used` other than at the start of a line; when a family line's
`100% used` is split by a NUL byte; when it reports a family at `100% used` but **exits non-zero**;
and when it does not finish within its bound, however complete the output it would have written. In
each case the Run reaches its judge and ends exactly as the same Run does with a probe reporting
nothing exhausted. *These are the fail-open paths, and they are the reason `RUN-21` reads one shape
and calls everything else `unknown`. The NUL-split line does not begin with `RUN-21`'s prefix,
however it reads once a byte is dropped. An item that only ever saw a well-formed probe would be a
green check over a rule nobody tested. `CNF-31` drives these shapes again at
`the probe before the pick`, and says how the two sets differ.* (`RUN-21`)

**CNF-27** With both Seats' models off `RUN-21`'s table and the probe scripted to report
`Current week (Fable): 100% used`, the Round runs no
`fable` Reviewer at all — no argument list is recorded for it — while `opus`, `astra` and `sol` all
run; `feedback-<r>-fable.md` holds exactly `REVIEWER NOT RUN (unavailable)`, carries no
`REVIEWER FAILED`, and `reviewer-<r>-fable.err` is empty; and the Round reaches its judge and the
Run ends 0. With both `Current week (Fable): 100% used` and `Current week (Opus): 100% used` on
separate lines, `probe-1.md` records `manager:unknown`, `implementer:unknown`,
`fable:unavailable`, `opus:unavailable`, `astra:unknown` and `sol:unknown`, in that order, each
line ending with a newline. Neither `fable` nor `opus` is called; `astra` and `sol` both run.
Each omitted Reviewer's Feedback File contains exactly the not-run line above, with its terminating
newline and no extra content, and its `.err` file exists and is empty. In both cases the judge
is called with every Panel Feedback File path, including those of the omitted Reviewers; with
the called Reviewers succeeding and the judge scripted to finish done, the Run produces its
Finished File and exits 0. With `fable` omitted and every called Reviewer failing, the Run
instead exits 2, calls no judge and produces no Finished File.
`CNF-15` owns the other literal. *An Implementation that reused one literal for both would pass
every other item, and the Manager reads the two as different things (`PRM-2`).* (`RUN-7`, `RUN-8`, `RUN-15`,
`RUN-21`, `PRM-2`, `DIR-4`)

**CNF-28** With the default models and the probe before the pick scripted to report
`Current week (Fable): 100% used · resets Sep 24, 3pm (UTC)`, the executable exits 2, and **no
Manager, Implementer or Reviewer argument list is recorded** — the probe's own is, exactly once;
standard output is empty; standard error names `claude-fable-5-1`, that line, reset and all, and
both `manager` and `implementer`, since both Seats are `unavailable` and `RUN-22`'s message names
`the Seat — both, when both are`; the Run Directory holds exactly `probe-pick.out`,
`probe-pick.err` and `probe-pick.md`; and `probe-pick.md` reads `manager:unavailable`, `implementer:unavailable`,
`fable:unavailable`, then `unknown` for `opus`, `astra` and `sol`. With `--manager-model
claude-opus-5`, the Implementer's model off the table and `Current week (Opus): 100% used`
instead, the Run is refused the same way and standard error names `claude-opus-5`. The pick is
scripted to fail. Here and in `CNF-29` and `CNF-30`, standard error names a Seat when the Seat's
word stands whole in what is left of standard error once every `manager-model` and
`implementer-model` is deleted together with any dashes before it. *The spawn record is the
assertion: a Run that spawned a Manager which then failed also exits 2, so the status alone passes
an Implementation that ignores the refusal. The second Run is there because one row cannot tell a
Seat read from its own model from a rule that hardcodes `fable`. The flag names go first because
`RUN-22`'s message `SHOULD name the flag that chooses another model` and each flag's name carries a
Seat's word, so a message naming the flag and no Seat would otherwise pass.* (`RUN-22`, `RUN-21`,
`DIR-4`, `RUN-10`)

**CNF-29** With the Manager's model off `RUN-21`'s table, the Implementer's at its default and the
probe before the pick reporting `Current week (Fable): 100% used`, the executable exits 2 with no
Manager, Implementer or Reviewer argument list recorded, standard output empty, the Run Directory
holding the three `probe-pick.*` files alone, `probe-pick.md` reading `manager:unknown` and
`implementer:unavailable`, and standard error naming `implementer`, `claude-fable-5-1` and the
probe's line. With `--implementer-model claude-opus-5` and `Current week (Opus): 100% used`
instead, the Run is refused the same way and standard error names `claude-opus-5`. Of standard
error the item asserts presence only. `RUN-22` states `a message naming the Seat — both, when both
are — its model, and the reset the probe reported`, and bounds the stream no further; `RUN-10`
states `Progress and diagnostics go to standard error and their wording is not specified`. The pick
is scripted to fail. *Again the spawn record, not the status, is what an Implementation that
refuses only for the Manager's Seat fails. The second Run is there because one row cannot tell a
Seat read from its own model from a rule that hardcodes `fable`, and a per-Seat or per-site lookup
can get one Seat's row right and another's wrong. A message naming both Seats unavailable when only
one is passes here, since no sentence in the set forbids it; the per-Seat reading stays asserted
where it is observable, in `probe-pick.md` above.* (`RUN-22`, `RUN-21`, `DIR-4`, `RUN-10`)

**CNF-30** With the Manager's model at its default and the Implementer's off `RUN-21`'s table, the
probes before the pick and in Round 1 reporting nothing exhausted, Round 2's reporting
`Current week (Fable): 100% used`, and Round 1 judged `rewrite`: the executable exits 2;
`manager-judge-1.out` exists and **`manager-judge-2.out` does not**, nor is a Round 2 judge argument
list recorded; Round 2's Implementer ran and its Panel ran without `fable` — `opus`, `astra` and
`sol` called, `feedback-2-fable.md` exactly the not-run line; `probe-2.md` reads
`manager:unavailable` and `fable:unavailable`, every other Seat `unknown`; there is no Finished File
and standard output is empty; and standard error names `manager`, `claude-fable-5-1` and the probe's
`Fable` line, reset and all, since `RUN-22` exits `with the message above for the Manager's Seat`,
which names the reset by `quoting the probe's matching line verbatim`. With Round 1's probe
reporting `Fable` instead, the Run exits 2 with no `manager-judge-1.out`, and standard error names
the same three. With `--manager-model claude-opus-5` and `Current week (Opus): 100% used` instead,
both Runs go the same way with `opus` in `fable`'s place, and standard error names `claude-opus-5`.
The withheld judge is scripted to fail. *The missing judge is the assertion: a Run whose judge was
called and failed also exits 2. The second pair of Runs is there because one row cannot tell a Seat
read from its own model from a rule that hardcodes `fable`, and a per-Seat or per-site lookup can
get one Seat's row right and another's wrong.* (`RUN-22`, `RUN-21`, `RUN-7`, `RUN-10`, `DIR-4`)

**CNF-31** With both Seats' models off `RUN-21`'s table and the probe before the pick reporting
`Current week (Fable): 100% used`, or `Fable` and `Opus` both at 100%, the Run starts — the pick
is called — and ends 0, and `probe-pick.md` reads `manager:unknown`, `implementer:unknown` and
the Reviewers' lines `CNF-25` and `CNF-27` give those reports. With the default models, the Run
starts and ends 0, every Seat `unknown` in `probe-pick.md`, when the probe before the pick writes
nothing; writes no usage line; reports only `Current week (all models): 100% used`; reports only
families outside the table; reports `99% used`; writes `Current week (Fable): 100% used` other
than at the start of a line; writes a family line whose `100% used` is split by a NUL byte;
reports a family at `100% used` but **exits non-zero**; or does not finish within `--probe-timeout
1`. *This is what shows fail-open reaches the pick: the pick being called is the assertion, since
a refused Run and an agent that failed both end without a Finished File. On the default models the
Manager's or the Implementer's Seat misread `unavailable` here refuses the Run under `RUN-22`.
Both sites drive these shapes in one order but not the same set: this one adds the families
outside the table, and leaves out the Run `CNF-26` compares against, `with a probe reporting
nothing exhausted`, which is that item's control rather than a fail-open shape.*
(`RUN-21`, `RUN-22`)

**CNF-32** The pick's prompt argument equals `PRM-1`'s fixture rendered as in `CNF-12`, with
`{{UNAVAILABLE}}` as the Probe before the pick leaves it, compared byte for byte in four Runs of
this item's own, each of which starts, calls the pick and ends 0. With the default models and that
Probe reporting `Opus` at 100%, `{{UNAVAILABLE}}` is the one line `opus`. With both Seats' models
off `RUN-21`'s table and `Fable` at 100%, it is the one line `fable`. With both Seats' models off
the table and `Fable` and `Opus` both at 100%, it is `fable`, a newline and `opus`, in that order
and nothing else. With the default models and a Probe reporting nothing exhausted, it is the empty
string: the prompt is the fixture with the placeholder replaced by nothing. *The empty form is
asserted here, and not left to `CNF-12`, because each form alone passes a wrong Implementation: one
that renders the list whatever the Probe said passes the populated Runs, and one that never renders
it passes the empty one. Each Seat has a Run of its own because no single Run can tell a working
render from one that hardcodes a Seat, the same argument `CNF-25` and `CNF-28` make of one row of
the table. The Seats are chosen so that no Run is refused (`RUN-22`): on the default models a
`Fable` report refuses the Run before any pick prompt exists, so the Runs that report it put both
Seats off the table.*
(`PRM-1`, `PRM-6`, `RUN-21`, `RUN-20`, `RUN-22`)

**CNF-33** With the default Manager preset a Run of two Rounds — Round 1 judges `rewrite`, Round 2
judges `done` — ends 0, and the recorded argument list of the judge call of each of those two
Rounds carries the `session` file's id, in a Run of this item's own: `RUN-16` says `every judge
call resumes it`, and a Run that ran one Round, or a reading that found no judge call, is a
failure here rather than a silent pass. *Why this is not left to `CNF-11`, which reads each Run's
Round 1 judge call alone, is `CNF-23`'s rationale, which holds of either preset.* (`RUN-16`,
`AGT-4`, `DIR-4`)

## Not testable black-box

These requirements have no item because no black-box observation decides them; each says why.

| requirement | why |
|---|---|
| `DIR-8` | a Run Directory deleted under the executable is an OS race the suite can only approximate; the executable's exit 2 on a missing snapshot is asserted inside `CNF-9`'s Run by deleting `task-1.md` between the Implementer and the Panel, which is as close as a fake gets |
| `DIR-9` | a threat model: a statement of what is out of scope, with nothing to observe |
