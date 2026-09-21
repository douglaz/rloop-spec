# 00 — Overview

## What rloop is

rloop drives one task through a git repository with three kinds of agent: a **Manager** that picks
the task, briefs the others and judges the result; disposable **Implementers** that build what the
brief says; and a **Panel** of four disposable **Reviewers**, each a different model, that read the
result against the brief. The Manager is the only agent whose conversation survives the whole
**Run**, and the only one whose judgment rloop acts on: rloop never reads what a Reviewer wrote,
and never decides anything an agent could decide. `CONTEXT.md` holds the vocabulary; this document
holds what rloop is for and what it is not.

This repository is the **Specification**. It holds no Implementation. Implementations
(`rloop-bash`, `rloop-rust`, …) live in their own repositories, pin this one as a git submodule at
one revision, and are held to it by the **Conformance Suite** in `conformance/`, which runs against
any executable that answers to the command line in `02-agents.md` — the suite does not care what
language wrote it.

## Where it comes from

rloop replaces `rb-lite`, a 1,451-line Bash loop that repeated an implementer until the git diff
stopped changing, ran a reviewer panel, parsed the reviewers' output for severity tags, applied a
severity floor, counted surviving reviewers, detected no-op rounds and exited through five
distinct failure codes. Every one of those mechanisms was the tool doing a judgment a model does
better. rloop keeps the shape — implement, review, repeat — and hands the judging to the Manager.
What survives of rb-lite is written here as a requirement; what was learned from it the hard way
is written beside the requirement it produced:

- A Reviewer holding a shell can `git stash` while three others read the tree, so rb-lite gave its
  Reviewers no shell and wrote the diff to a file for them. rloop gives Reviewers a shell (they can
  run the tests) and denies the history-changing verbs instead (`AGT-9`), which is the harness
  doing the work the file did.
- `codex review --base` cannot take a prompt — it refuses one, verified on codex 0.153.4 — so the
  codex Reviewers run `codex exec` with the review prompt (`AGT-10`).
- An agent CLI with stdin left open waits on it forever; this cost one 25-minute reviewer timeout
  during this specification's own review. Every agent is spawned with stdin from the null device
  (`AGT-12`).

## Design goals

**OVR-1** rloop MUST act only on what the Manager wrote — the **Task File** and the **Finished
File** (`01-run-lifecycle.md`) — and on the availability probe's output, which is no agent's work
and which `RUN-21` alone says how to read. It MUST NOT parse a Reviewer's output, an
Implementer's output, or any part of the Finished File beyond its first line. *This rule read
"act only on what the Manager wrote" until 2026-09-21. A quota report is not a judgment an agent
made, and reading one lets rloop stop paying a Reviewer's timeout for a model that cannot answer;
`F9` narrowed `DIR-4` the same way, and for the same reason — the sentence was banning a reading
it was never written to ban.*

**OVR-2** Everything model-facing — every prompt, every agent command line, and the availability
probe's (`AGT-18`) — is stated in this Specification verbatim (`02-agents.md`, `03-prompts.md`),
and an Implementation MUST reproduce it byte for byte. `ADR-0001` explains why the
Specification nevertheless hands an Implementation no file to read.

**OVR-3** rloop MUST NOT run any git command that changes history or the working tree: no commit,
no checkout, no stash, no reset, no clean, no branch. It reads git — `rev-parse`, `status` — and
nothing else. The Manager commits accepted work (`SEQ-8`, `ADR-0004`).

**OVR-4** rloop MUST NOT exit while an agent process it started is still running (`AGT-15`).

## Non-goals

- **No rollback, checkpoint commits, worktree recovery, daemon, PR automation or run database.**
  rb-lite's `AGENTS.md` banned these and the ban stands.
- **No resume.** A Run Directory is used once (`DIR-3`). A Run that failed is inspected, not resumed.
- **No branch management.** The caller checks out the branch a Sequence should commit to
  (`SEQ-9`).
- **No defence against a hostile agent.** The Checkpoint repairs a cooperative model's mistake and
  the threat model says so (`DIR-8`, `ADR-0003`).
- **No configurability of the Panel or the prompts at run time.** The Panel is the four Reviewers
  `02-agents.md` names; changing it is a change to this Specification.

## How much to trust this

Every requirement wears the same costume — a MUST, an identifier, a conformance item — and the
confidence behind them is not uniform:

- **The control flow is proved and executed.** `tools/formal/` models the decision after every
  Manager call and the Sequence between Runs, proves the properties `01` and `05` state, and
  generates the scenarios the Conformance Suite replays (`ADR-0002`). A theorem is about the model;
  conformance is an executable passing the scenarios; the two are kept apart on purpose.
- **The prompts are checked for equality, never for quality.** The suite proves an Implementation
  sends the prompt this Specification states. Whether that prompt makes a Manager judge well is
  learned only from live Runs, and nothing here has yet been validated against one: **no
  Implementation exists at the time of writing.**
- **Agent command lines were verified once, by hand,** against the CLI versions `02-agents.md`
  names. A fake agent accepts any flag, so the suite cannot tell a wrong flag from a right one.
- **What the model omits is listed, not hidden:** bytes, signals, timeouts, git, and every agent's
  behaviour. `Properties.lean`'s header names them; `06-conformance.md` says which of them a
  hand-written item covers.
