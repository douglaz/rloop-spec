# rloop — specification set

A language-neutral specification for **rloop**: a loop that lets one long-lived judging agent (the
Manager) drive disposable working agents (an Implementer, a four-model review Panel) through one
task in a git repository, and drain a backlog by repeating that. `CONTEXT.md` holds the
vocabulary; `00-overview.md` holds what it is for.

This repository contains **specifications only**, with two carve-outs: `tools/` holds the gates
that check the specifications, and `conformance/` holds the black-box suite an Implementation is
held to. Nothing that implements rloop belongs here. Implementations — `rloop-bash`, `rloop-rust`,
… — live in their own repositories, pin this one as a git submodule at one revision, build an
executable, and run `spec/conformance/run ./result/bin/rloop`.

## Gates

`nix develop --command bash tools/check-all.sh` runs every gate below, and CI runs the same script
on every push:

| Gate | What it refuses |
|---|---|
| `tools/check_formal.sh` | A formalized clause whose proof does not hold. `tools/formal/` carries the decision after every Manager call, the Round, the Sequence, and the properties `01` and `05` state, as Lean definitions tagged `@[req]` with the identifier each formalizes; every guard has a witness theorem for its absence (`ADR-0002`). `lake build` refuses a theorem that no longer proves; `lake exe gate` refuses a proof resting on any axiom beyond `propext`, `Classical.choice` and `Quot.sound` — a `sorry`, a project `axiom` and `native_decide` are each red — and an empty index; `lake exe render` writes the marked regions; `lake exe scenarios` writes the suite's replay file and, with `--controls`, refuses a guard that no scenario would miss |
| `tools/check_ids.py` | A duplicate identifier, a citation to an id nothing defines, a gap in a namespace's sequence, an id far above its neighbours, a reference to an ADR that does not exist |
| `tools/check_coverage.py` | A requirement that no `CNF` item cites and that `06-conformance.md` does not excuse with a reason |
| `tools/check_regions.py` | A marked region — the decision table in `01-run-lifecycle.md` — that is not what its Lean declaration emits |
| `tools/check_fixtures.py` | A prompt or command-line fixture in `conformance/fixtures/` that differs from its block in `02-agents.md` or `03-prompts.md`; the Markdown is the home (`ADR-0001`) |
| `tools/check_scenarios.py` | A committed `conformance/scenarios.tsv` that is not what the model enumerates; it prints the count so growth shows in review |

The workflow also breaks a document deliberately on every run and asserts each gate that has a
negative control rejects it, so that green is evidence.

## How to read this

| Document | Contents |
|---|---|
| `00-overview.md` | What rloop is, where it came from, design goals, non-goals, and **how much to trust this** |
| `01-run-lifecycle.md` | The Run: pick, Round, the Finished File, exit codes, the decision table (rendered from Lean), the round cap |
| `02-agents.md` | rloop's command line; every agent command line verbatim; the environment contract; spawning, timeouts, signals |
| `03-prompts.md` | The five prompts verbatim, and the rendering rule |
| `04-run-directory.md` | Where a Run's files go, who owns which, the Checkpoint, the threat model |
| `05-sequence.md` | `--auto`: Runs in sequence, the clean-tree check, who commits |
| `06-conformance.md` | What `conformance/run` proves of an Implementation, item by item, and what only a live Run can |
| `07-open-findings.md` | What was deferred or left open, so it is not re-raised from scratch |
| `CONTEXT.md` | Glossary: which word means what, and which words are avoided |
| `docs/adr/` | The decisions, and what was rejected to reach them |
| `conformance/` | The suite: `run`, the fakes, the fixtures, `scenarios.tsv` |

Read `00`, `01` and `04` first. `01` is the heart: rloop is the decision table and the Round
around it, and everything else is what the agents are told and given.

## The decisions this specification is built on

| ADR | Decision |
|---|---|
| `0001` | The Specification hands an Implementation nothing to read: prompts and command lines are verbatim requirements the Implementation hardcodes, and the suite's fixtures are kept identical to them by a gate |
| `0002` | The formal model generates the Conformance Suite's scenarios; a theorem is never conformance |
| `0003` | The Checkpoint repairs a cooperative model's accidents and does not resist an adversary; the Run Directory is used once and lives in-repo, self-ignored |
| `0004` | The Manager commits accepted work; rloop only checks the tree is clean between Runs; the hole this leaves is stated |

## Requirement conventions

Requirements use RFC 2119 keywords — **MUST**, **MUST NOT**, **SHOULD**, **MAY** — and each carries
a stable identifier:

| Prefix | Document |
|---|---|
| `OVR-n` | `00-overview.md` |
| `RUN-n` | `01-run-lifecycle.md` |
| `AGT-n` | `02-agents.md` |
| `PRM-n` | `03-prompts.md` |
| `DIR-n` | `04-run-directory.md` |
| `SEQ-n` | `05-sequence.md` |
| `CNF-n` | `06-conformance.md` |
| `Fn` | `07-open-findings.md` |

**Identifiers are append-only.** An identifier is never reused and never renumbered. Text may be
deleted; the gap in the sequence is the tombstone, and a deleted identifier goes in the table
below so an old citation still resolves — `tools/check_ids.py` reads it.

### Withdrawn identifiers

| id | withdrawn | why |
|---|---|---|

## Using rloop

For whoever runs an Implementation:

- **A lone Run:** `rloop` picks the next task from the repository's tracker; `rloop "fix the
  flaky retry test"` steers the pick. Exit 0 is done, 1 is blocked, 3 is idle (nothing to pick),
  2 is a failure; the Finished File — the Manager's report — is on standard output.
- **Blocked (exit 1) is a question for you.** The Manager blocks when the task turns on a point
  the repository's specifications leave ambiguous — it never picks a reading — and the report
  names the passage and recommends a clarification. Clarify the specification, then run again.
  Implementation choices the specifications leave open it settles after consulting two advisers,
  and the brief records the question and the answers.
- **A Sequence:** check out the branch the work should land on, then `rloop --auto`. It runs
  until the Manager finds nothing left (exit 0), a task blocks (1), or something fails (2). The
  Manager commits each accepted task before the next starts; rloop never commits, branches or
  pushes, and opening the pull request is yours.
- **After a Run that ended blocked or capped:** the work is in the tree, uncommitted, on top of
  clean history — unless the Implementer committed during the Round, in which case unaccepted
  commits sit behind a clean tree and the next invocation's base would take them in unreviewed
  (`ADR-0004`, `F3`). Read the Finished File: it says what is committed and what is in the tree.
  Reconcile before starting again.
- **The Run Directory** — `.rloop/runs/<timestamp>-<pid>/` by default — holds every brief, every
  Reviewer's feedback, every agent's output and the Manager's report. It is never deleted.

## How much to trust this

`00-overview.md`'s last section, in one line: the control flow is proved and executed against
fakes; the prompts are checked for equality and never for quality; the command lines were
verified by hand once; and no Implementation has yet run live.
