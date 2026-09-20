# 07 — Open findings

What was raised and not taken, deferred, or left open, so that it is not raised again from
scratch. Identifiers `F<n>` are append-only like every other.

## F1 — The rewrite gate (deferred 2026-09-17)

The idea this project began with: any change to the Specification or to an Implementation is
gated on whether rloop, run on a fresh Implementation repository holding only the pinned
Specification, rewrites rloop from the documents and the result passes `conformance/run` — a
bootstrapping chain like a self-hosting compiler's, with the previous release driving `--auto`
on a seed repository, passing meaning the suite is green and one real Run completes, and every
run of the gate recorded. Deferred by the owner as an interesting idea for later; the shape
sketched here is the one to start from. Until it exists, `CNF-22` is the only live check.

## F2 — Citation and obligation gates (deferred 2026-09-18)

provisiond-spec's `check_citations.py` (a quoted phrase attributed to a requirement whose body
does not contain it) and `check_obligations.py` (a duty assigned to another requirement's
subject) caught drift in a set of 700 requirements over months. This set has about eighty.
They are added the first time this set is found to have drifted in either way.

## F3 — Unaccepted commits behind a clean tree (open, stated)

`ADR-0004` and `SEQ-10`: an Implementer may commit during a Run that ends blocked or capped;
the next invocation's base takes those commits in unreviewed. Closing it needs rollback, which
rloop will not have. Open by decision; the Finished File's report is the mitigation.

## F4 — The scenario alphabet is a choice (open)

`Rloop.Scenarios` enumerates seven Manager outcomes, two Implementer outcomes, three Panel
classes, one interference point per script, and caps 1 and 2. Fable's review of `ADR-0002`
argued depth 2 suffices because the decision is memoryless apart from the Round counter; astra's
asked for cap 3 and the default of 10 as explicit lines. Cap 10 is `CNF-3`'s job only through
`--max-rounds`; a cap-3 enumeration was not added. Revisit if an Implementation passes the suite
and fails live on a Round-3 behaviour.

## F5 — The first Implementation's findings (closed 2026-09-18)

The first `rloop-bash` build from the documents alone, by an implementer with no knowledge of
how they were written, reached 18 of 20 executable items and stopped on one specification
defect rather than working around it: `AGT-7`'s deny list holds a space (`Bash(git checkout:*)`)
and `tools/check_fixtures.py` split it into six arguments, so `CNF-11` demanded an argv that
`AGT-9` forbids — and that would have handed the real CLI broken patterns. Closed by quoting
the argument in `02-agents.md` and teaching the gate the quotes. Three ambiguities from the same
report are closed in place: `SEQ-7` now defers to `RUN-10` for a Run that ended 2; `DIR-2` now
requires a timestamp fine enough to tell two Runs of one Sequence apart; `AGT-16` accepts a
process group without a session. *The set had been validated against a stub that read the same
split fixtures, which is why the defect survived: a check and its subject built from one
misreading agree with each other.*

## F6 — The first live check, `CNF-22` (closed 2026-09-19)

Against `rloop-bash` at `e8b215d` (spec `7a463bb`), on the real CLIs `AGT-17` names, with
`rloop-bash` as the target repository. **A lone Run** with an instruction (add a CI workflow):
one Round, four Reviewers with no findings, `STATUS: done`, exit 0, one commit by the
Implementer with no attribution (`b8fdf0b`), tree clean; the Manager rejected one Reviewer
suggestion as outside the brief and, the repository having no tracker, reported in the Finished
File a real defect it had noticed — an inherited `RLOOP_REVIEWER` leaking into Manager and
Implementer spawns, which broke rloop-inside-rloop. **A two-Run Sequence** with that defect as
the instruction: Run 1 fixed it in one Round (`a61e3f7`), ended `done`; Run 2 found it done and
ended `idle`; the Sequence exited 0 and printed both Finished Files under `== run n ==`. Every
prompt in `03` was read by a real model and did what it says. Two observations kept: the
Manager assumed the Specification repository public, so the workflow it accepted cannot clone
the submodule on a runner until that changes; and an interrupted pick (SIGINT during the live
Manager's first call) exited 2 `interrupted` with nothing left in the tree, which `CNF-18` had
only shown with fakes.

## F7 — `RUN-19` and `RUN-20` exercised live (closed 2026-09-19)

Two scratch projects, each run through `nix run github:douglaz/rloop-bash` at `580b112`. **A
contradictory specification** (`notes`: `NOTE-3` replaces the file with the new note, `NOTE-2`
lists every note ever added, `NOTE-1` allows no other store): the Run ended `blocked` at the pick
with nothing changed, the report naming the document, the commit, the three rules, both readings
with their observable difference, a recommended rewrite of `NOTE-3`, and three smaller gaps to
settle in the same edit. **An open implementation choice** (`tally`: `TAL-2` leaves storage to the
implementation): the Manager left storage to the Implementer, because the brief did not need to
settle it, and held a Consultation on the one choice the brief did need to settle — the collation
behind `TAL-3`'s "sorted by name", which changes the output and the tests; fable and astra agreed
on byte order, so no escalation, and the brief records the question, both answers and the choice.
The same Run then showed the loop working under disagreement of a different kind: three of four
Reviewers found a real defect in Round 1 (awk comparing numeric-looking names numerically, so
`tally 01` deleted the `1` counter), the Manager reproduced it, rewrote the brief with the exact
line and a reproduction, Round 2 fixed it, four Reviewers passed it, `done` after two Rounds, five
suggestions rejected as outside the brief and listed in the report.

## F8 — The first real-project Run (closed 2026-09-19)

rloop-bash#1: a lone Run on `provisiond-spec`, three Rounds, a 1068-line Lean module landed with
the repository's seven gates green, sixty-one minutes. Four observations: the PID `nix run`
hands back is the wrapper's (rloop-bash now prints its own; the README says how to keep a
detached Run's exit status); the codex Reviewers' read-only sandbox could not run the
repository's nix gates and only one of the two said so (`PRM-4` now has every Reviewer state up
front what it could not run, and `AGT-10` drops the sandbox); the tracker file the Manager claims
a task in is dirtied after `RUN-3`'s list is taken (now stated there as the Manager's to commit);
and commits carry no attribution, as `SEQ-8` says.

## F9 — A second Manager preset, because one vendor's quota stops the loop (closed 2026-09-20)

rloop-bash#3: the Round 2 judge call of a Run on `provisiond-spec` was killed at
`--manager-timeout` having written nothing on either stream, the signature of the account behind
`claude-fable-5-1` reaching its quota — the same call one Round earlier had answered in two
minutes. A direct probe confirmed it: `claude-fable-5-1` hung and was killed, `claude-opus-5`
answered at once. With the Manager pinned to one CLI by `AGT-3` and `AGT-4`, one vendor's quota
stopped every Run, and `--manager-model` could only pick another model of the same vendor.

`gpt-6-astra` was then evaluated in the Manager's seat by hand, on `PRM-1`'s prompt verbatim: it
read the repository's conventions, picked the lowest ready task off the frontier as
`docs/agents/issue-tracker.md` says, claimed it through the tracker, ran the repository's gates
unpiped, and ended `blocked` on a genuine specification ambiguity with the passages, both
readings and a recommended clarification — `RUN-19`'s rule, followed without rloop enforcing it.
A second call resuming that session named the task it had claimed, so a codex Manager is one
conversation as `RUN-16` requires.

Landed as `--manager claude|codex`: `AGT-1`, `AGT-2`, `AGT-3` and `AGT-4` amended, `RUN-16`
rewritten around an id rloop chose or the pick reported, `DIR-4`'s "entire and unparsed" narrowed
to the bytes it was protecting, `CNF-5` and `CNF-11` extended and `CNF-23` added. What this does
not do is let a Run outlive a quota it meets mid-Round: the Panel is still two claude Reviewers
and two codex ones (`AGT-7`, `AGT-8`, `AGT-10`), and a dead one costs `--reviewer-timeout` a
Round before `RUN-15` marks it failed and the Round goes on.

## F10 — What a Run that exits 2 leaves behind (closed 2026-09-20)

rloop-bash#3. A Run on `provisiond-spec` completed two Rounds and then died: the Round 2 judge
call was killed at `--manager-timeout` having written zero bytes on both streams — the signature
of an account reaching its quota, not a defect, and killing the call is `AGT-14` working. What the
operator was left with was the report's subject: five files of good work uncommitted, no Finished
File because the judge never wrote one, the tracker row still claimed, and a follow-up the Manager
had promised unfiled. The `README.md` bullet that should have helped covered "blocked or capped"
together and said to read the Finished File — which a capped Run does not have, since the cap is an
exit 2. It is now two bullets, and the exit-2 one names the Run Directory's files as the evidence
and the two things the Run does not tidy.

**Rejected, from the same report:** having rloop write a minimal `finished.md` of its own —
`STATUS: failed` and the phase it died in — so that "read the Finished File" is true of every
terminated Run. It would put rloop's words in the file `DIR-4` gives the Manager, add a fifth case
to `RUN-9`'s four and an exit to `RUN-10`'s table, and change the model and the suite with them;
the reporter judged the sentence enough, and so does this. `RUN-17` already guarantees the
evidence survives, which is what makes the reconstruction possible at all.

## F11 — The codex Manager preset, live (closed 2026-09-20)

`F9` added `--manager codex` and `rloop-bash` implemented it the same day, itself under rloop
(`3809ed8`, suite 21/21). What the fakes could not show, a Run then did: with `--manager codex`
the pick's standard output opened with
`{"type":"thread.started","thread_id":"01a0bfb9-a63a-7a82-a47f-3ff75b43906d"}` and the `session`
file held that id, so `AGT-3`'s `--json` contract and `RUN-16`'s rule hold against the real CLI;
`codex exec resume` carried the conversation into the judge call; the Run ended `STATUS: done`
with `gpt-6-astra` in the Manager's seat, having picked the task, written the brief, verified the
build and both suite invocations itself, declined two Reviewer suggestions with reasons — one of
them correctly, that prescribing this Implementation's exact diagnostic wording in the
Specification would change a contract `RUN-10` leaves open — and closed its GitHub issue.

Two observations kept rather than acted on. `claude-fable-5-1` was at 100% of its weekly limit
throughout, so the `AGT-7` Reviewer slot died at its timeout on every Round of both Runs
(`REVIEWER FAILED (exit 124)`, `RUN-15` working); that waste is rloop-spec#3. And the codex
Reviewers report `PRM-4`'s item 0 only when something blocked them, so their bare `No findings.`
does not say what it rests on; that is rloop-spec#4.
