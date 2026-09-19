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
