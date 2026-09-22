# 06 — Conformance

What an Implementation must demonstrate, and how: every item below is executed by
`conformance/run`, the Conformance Suite this repository ships. Each item names the requirements
it proves. Nothing here is ticked by hand — the suite's output is the tick — and an item that
cannot be executed is in the last section, with the reason.

## The suite's contract

**CNF-1** `conformance/run <path to an rloop executable>` MUST run every item below against that
executable and exit 0 only if every one passed, printing each item's identifier and verdict. It
needs `bash`, `git`, GNU coreutils, `grep`, `sed` and `awk` on `PATH` and nothing else — no Lean, no
Python, no network —
so that an Implementation repository in any language runs it from the submodule.
(`00-overview.md`)

**CNF-2** The suite puts fake `claude` and `codex` executables first on `PATH`. A fake reads
`RLOOP_ROLE`, `RLOOP_ROUND`, `RLOOP_RUN`, `RLOOP_REVIEWER` and `RLOOP_RUN_DIR` (`AGT-13`) to find
its scripted part, records what it received — argument list, environment, working directory,
whether standard input was at end of file — and acts: writes a Task File or Finished File, exits
non-zero, sleeps, ignores a signal, spawns a grandchild, or interferes with the Manager's files,
as the scenario says. The fake never reads a prompt and never parses a flag, which is what keeps
the suite's control flow independent of `02` and `03`. (`AGT-13`)

## The scenarios

**CNF-3** For every line of `conformance/scenarios.tsv` the suite MUST run the executable in a
fresh git repository with the line's script loaded into the fakes and `--max-rounds` set to the
line's cap, and assert the exit status equals the line's and the recorded spawns equal the line's
trace — a Panel compared as the set of the Reviewers rloop called, the rest in order. The file is
what `tools/formal/` enumerates (`ADR-0002`, `tools/check_scenarios.py`). This item is the
executable form of the decision table and the Round: (`RUN-5`, `RUN-6`, `RUN-7`, `RUN-9`,
`RUN-10`, `RUN-11`, `RUN-12`, `RUN-13`, `RUN-14`, `RUN-15`, `RUN-21`, `DIR-5`, `DIR-6`, `DIR-7`,
`OVR-1`)

**CNF-4** The suite MUST be able to fail: run with `--self-check` it flips one expected exit in
a copy of the scenario file, replays it, and requires a red result. The scenario file is shown
sensitive to each guard by `lake exe scenarios --controls` in `tools/check_formal.sh`, which
counts the lines each guard's absence would change and refuses zero. *A suite that cannot go red
is a green check that asserts nothing.* (`RUN-11`)

## Starting and stopping

**CNF-5** Each of these invocations exits 2, spawns nothing, and writes to standard error: an
unknown option; `--max-rounds 0`; `--max-rounds x`; `--reviewer-timeout -1`; two `INSTRUCTION`
arguments; `--auto --base HEAD`; `--auto --run-dir d`; `--manager gpt-6-astra`, a value outside
the preset's set and the mistake a caller makes who means `--manager codex --manager-model
gpt-6-astra`. `--version` and `--help` exit 0 and spawn nothing. (`AGT-1`, `AGT-2`, `SEQ-3`)

**CNF-6** Outside a git working tree the executable exits 2 and spawns nothing. (`RUN-1`)

**CNF-7** With `--run-dir` naming an existing directory (empty or not) or a path whose parent does
not exist, the executable exits 2 and spawns nothing. With `--run-dir` naming a fresh path, the
directory exists afterwards and is the only one created. (`DIR-1`, `DIR-3`)

**CNF-8** Without `--run-dir`, the Run Directory is created under `<toplevel>/.rloop/runs/`,
`<toplevel>/.rloop/.gitignore` exists holding the line `*`, and `git status --porcelain` prints
nothing after a Run whose fakes changed no tracked file. (`DIR-2`, `RUN-4`)

**CNF-9** After a two-Round Run the Run Directory holds exactly the names `DIR-4` lists for two
Rounds and nothing else; each agent's `.out` and `.err` hold that fake's standard output and
standard error entire; `session` holds the Manager's session id as a UUID, whichever preset
established it (`RUN-16`); and the directory is intact after a Run that ended 2. (`DIR-4`,
`RUN-17`)

## What agents receive

**CNF-10** Every fake records the five variables with the values `AGT-13` gives its role and
Round, `RLOOP_REVIEWER` unset except for Reviewers, its working directory equal to the git
toplevel, and standard input at end of file on first read. (`AGT-12`, `AGT-13`)

**CNF-11** For each role the recorded argument list equals the fixture in
`conformance/fixtures/argv/` with the placeholders filled in: the pick's `<session id>` is the
`session` file's content and every judge call carries that same id; `<manager model>` is
`--manager-model`'s value, or the preset's default; `--manager codex` produces `AGT-3`'s and
`AGT-4`'s second lists and the default produces their first;
`--implementer codex` produces
`AGT-6`'s list and the default `AGT-5`'s; the four Reviewers' lists are `AGT-7`, `AGT-8` and
`AGT-10`'s, one each, with their `RLOOP_REVIEWER` names. (`AGT-3`, `AGT-4`, `AGT-5`, `AGT-6`,
`AGT-7`, `AGT-8`, `AGT-10`, `AGT-11`, `RUN-16`, `OVR-2`)

**CNF-12** For each role the recorded prompt argument equals the fixture in
`conformance/fixtures/prompts/` rendered by `PRM-6` with the values the suite knows: the Run
Directory's paths, the base hash, the Round, `--max-rounds`, the caller's instruction (given and
absent), the dirty-at-start list (a tree with one modified and one untracked path, and a clean
tree), and the four Feedback File paths in order. Each rendered prompt ends with `PRM-5`'s
sentence. (`PRM-1`, `PRM-2`, `PRM-3`, `PRM-4`, `PRM-5`, `PRM-6`, `RUN-3`, `DIR-10`)

**CNF-13** `{{BASE}}` is the full hash of `HEAD` at start, and with `--base <ref>` the full hash of
that ref; a commit the fake Implementer makes during Round 1 does not change the base rendered
into Round 2's prompts. (`RUN-2`)

## Output

**CNF-14** For a Run ending 0, 1 or 3, standard output is byte-identical to `finished.md` and
nothing else; for a Run ending 2, standard output is empty and standard error is not. (`RUN-10`)

**CNF-15** A Reviewer fake that exits 7 after writing a line leaves its Feedback File holding that
line followed by `REVIEWER FAILED (exit 7)`; a Round with one such Reviewer proceeds to the judge.
(`RUN-15`)

## Concurrency, time and signals

**CNF-16** With every Reviewer fake sleeping 2 seconds, a Round's Panel completes in under 5
seconds, and every Reviewer's recorded start precedes every Reviewer's recorded end. (`RUN-8`)

**CNF-17** With `--reviewer-timeout 1` and one Reviewer fake sleeping 30 seconds, that Reviewer's
Feedback File carries `REVIEWER FAILED`, the Round proceeds, and the fake's process and the
grandchild it spawned are gone before the judge starts. With `--implementer-timeout 1
--kill-after 1` and an Implementer fake that ignores SIGTERM, the Implementer is gone within 5
seconds and the Run proceeds to the Panel. With `--manager-timeout 1` and a sleeping pick, the
Run exits 2. (`AGT-14`, `AGT-16`, `RUN-14`)

**CNF-18** SIGINT sent to the executable while an Implementer fake sleeps: the fake records
SIGTERM, the executable exits 2 with `interrupted` on standard error, no process of the fake's
group survives, and the Run Directory is intact. The same with SIGTERM. A second SIGINT while a
fake ignores SIGTERM ends it at once. (`AGT-15`, `OVR-4`, `RUN-17`)

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
pick that fails: exit 2, and standard output holds exactly two `== run` blocks. (`SEQ-1`, `SEQ-2`,
`SEQ-5`, `SEQ-6`, `SEQ-7`)

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
clarification in the report; and a Run whose brief settles an open implementation choice, with
the Consultation's question, every model it called and what each one did, the answers and the
choice recorded in the brief. Under each `--manager` preset, a Run holding **two** Consultations
MUST also be observed, the first of them meeting an adviser that **hangs** rather than one that
fails fast: the call bounded and terminated, the chosen durations, the bounds and each call's
elapsed time in the record, the counterpart called in its place, and the second Consultation
starting from the eligible models rather than the one that did not answer. One observation MUST
be of a Consultation in which neither model of one vendor answers, carrying the single-vendor
marker in the brief or the Finished File; and one, where it can be induced, of a Run ending
`blocked` with the report naming the silent models and saying whether those that answered
agreed. The Run
Directories and the commits are kept as the record. (`AGT-9`, `AGT-17`, `SEQ-8`, `SEQ-10`,
`RUN-19`, `RUN-20`)

**CNF-23** With `--manager codex` a Run that judges `done` ends 0 with that Finished File, the
`session` file holds the `thread_id` of the `thread.started` event the fake wrote as the pick's
first line of standard output, every judge call is given that same id, and `manager-pick.out`
still holds that output byte for byte. A pick that exits 0 having written no `thread.started`
event exits 2 with no Round run and the Run Directory kept. *The ordinary Run is asserted here and
not left to `CNF-11`, which reads the argument lists and would stay green over a preset that
spawns every call correctly and then exits 2.* (`RUN-16`, `AGT-3`, `AGT-4`, `DIR-4`)

**CNF-24** Every Round runs the probe exactly once, after that Round's Implementer and before any
of its Reviewers starts, keeps `probe-<r>.out` byte for byte as the probe wrote it, and leaves a
`probe-<r>.err`. A Run of two Rounds leaves `probe-1.*` and `probe-2.*` and no
`probe-0.*`: the pick has no Panel. Its recorded argument list equals
`conformance/fixtures/argv/AGT-18.txt`. (`RUN-7`, `RUN-21`, `AGT-18`, `AGT-13`, `DIR-4`, `OVR-2`)

**CNF-25** `probe-<r>.md` names every Reviewer of the Panel exactly once, in the order `fable`,
`opus`, `astra`, `sol`, each with `unavailable` or `unknown` and nothing else. With the probe
scripted to report `Current week (Fable): 100% used`, `fable` reads `unavailable` and the other
three read `unknown` — `opus` because no line names its family, `astra` and `sol` because no
model of theirs is in `RUN-21`'s table. With `Current week (Opus): 100% used` instead, the
verdicts swap: `opus` alone reads `unavailable`. *Both rows are asserted because one row cannot
tell a working table from a rule that hardcodes `fable`.* (`RUN-21`, `DIR-4`)

**CNF-26** Every Reviewer reads `unknown`, and the Panel still runs in full, when the probe writes
nothing; when it writes output carrying no `Current week` line; when it reports a family at
`99% used`; when it reports only `Current week (all models): 100% used`; when it reports a family
at `100% used` but **exits non-zero**; when those words appear
somewhere other than the start of a line; and when it does not finish within its bound, however
complete the output it would have written. In each case the
Run reaches its judge and ends exactly as the same Run does with a probe reporting nothing
exhausted. *These are the fail-open paths, and they are the reason `RUN-21` reads one shape and
calls everything else `unknown`. An item that only ever saw a well-formed probe would be a
green check over a rule nobody tested.* (`RUN-21`)

**CNF-27** With the probe scripted to report `Current week (Fable): 100% used`, the Round runs no
`fable` Reviewer at all — no argument list is recorded for it — while `opus`, `astra` and `sol` all
run; `feedback-<r>-fable.md` holds exactly `REVIEWER NOT RUN (unavailable)`, carries no
`REVIEWER FAILED`, and `reviewer-<r>-fable.err` is empty; and the Round reaches its judge and the
Run ends 0. With both `Current week (Fable): 100% used` and `Current week (Opus): 100% used` on
separate lines, `probe-1.md` records `fable:unavailable`, `opus:unavailable`, `astra:unknown` and
`sol:unknown`, in that order. Neither `fable` nor `opus` is called; `astra` and `sol` both run.
Each omitted Reviewer's Feedback File contains exactly the not-run line above, with its terminating
newline and no extra content, and its `.err` file exists and is empty. In both cases the judge
is called with every Panel Feedback File path, including those of the omitted Reviewers; with
the called Reviewers succeeding and the judge scripted to finish done, the Run produces its
Finished File and exits 0. With `fable` omitted and every called Reviewer failing, the Run
instead exits 2, calls no judge and produces no Finished File.
`CNF-15` owns the other literal. *An Implementation that reused one literal for both would pass
every other item, and the Manager reads the two as different things (`PRM-2`).* (`RUN-7`, `RUN-8`, `RUN-15`,
`RUN-21`, `PRM-2`, `DIR-4`)

## Not testable black-box

These requirements have no item because no black-box observation decides them; each says why.

| requirement | why |
|---|---|
| `DIR-8` | a Run Directory deleted under the executable is an OS race the suite can only approximate; the executable's exit 2 on a missing snapshot is asserted inside `CNF-9`'s Run by deleting `task-1.md` between the Implementer and the Panel, which is as close as a fake gets |
| `DIR-9` | a threat model: a statement of what is out of scope, with nothing to observe |
