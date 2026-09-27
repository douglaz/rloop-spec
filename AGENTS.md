# AGENTS.md

Specifications only. `tools/` holds the gates that check them, `conformance/` the black-box suite
an Implementation is held to, and `.github/workflows/` runs the gates. Nothing that implements
rloop belongs here (`ADR-0001`): Implementations live in their own repositories and pin this one
as a submodule.

## Gates

`nix develop --command bash tools/check-all.sh`, before you start and again every time you change
something. Run it unpiped — a pipe reports the pipeline's status, not the gate's, which is why
`check-all.sh` captures each exit code directly. The shell is required: the formal gate needs
Lean, and a missing toolchain is a red gate, not a skipped one.

`nix flake check -L`, also unpiped, before you report done. It builds `flake.nix`'s `checks.gates`,
which runs that same `tools/check-all.sh` inside the Nix build sandbox, where `PATH` holds nothing
but the derivation's inputs and there is no `/usr/bin/env`. The dev shell has names the derivation
does not, so a breakage that is the sandbox's alone is green there and red here.
`conformance/scenario-lib.sh` calls `executable_path_needs` "the names the fakes and the git shim
run under the executable's PATH", and `restrict_path` exits 2 before any item without one of them;
besides what stdenv supplies, `checks.gates`'s `nativeBuildInputs` is what puts them on `PATH` in
the sandbox. Those are the lists this command catches drifting apart — `cd376d3` added `git` to
the first and left the derivation red until `d0e25a2` added it to the second — and every other
sandbox-only breakage with them. Caveat: the sandbox gets the repository's *tracked* files, so
`git add` a new gate, fixture or scenario file before running it, or the sandbox is green on a tree
the next commit reds; and on a tree whose output is already in the store it is a cache hit —
`running 0 flake checks...` in under a second, no gate output to quote — and
`nix build --rebuild --no-link -L .#checks.x86_64-linux.gates` builds the check anyway. The sandbox
run is the slower one — it gets no incremental `lake` cache — which is why the dev-shell run stays
the loop you iterate in.

Neither command runs `.github/workflows/gates.yml`, whose negative controls (`README.md`, *Gates*)
require the message each mutation makes the gate print, so a reworded message leaves every quoting
control's `grep -qF` literal stale and CI red on a tree both commands call green — `6dc3326`
reworded one message and `37f8fce` brought the control back into line. Whoever rewords a message a
gate or the suite prints greps the workflow for the old text first and updates every control that
quotes it, in the same commit; that is a manual check and not a closed door, because whether a
mutant still reaches the new wording only the CI run witnesses.

A formalized clause's home is its Lean declaration in `tools/formal/`, tagged `@[req "RUN-13"]`
(`ADR-0002`). Change the declaration and the Markdown together; a theorem that stops proving is
the gate telling you the amendment contradicts a property the set claims — read the theorem before
weakening it. Every guard has a witness theorem for its absence; a guard without one is
decoration. Never put a `CNF` identifier in `tools/formal/`. After changing the model, run
`python3 tools/check_regions.py --write` and `python3 tools/check_scenarios.py --write` and commit
what they wrote: the decision table in `01` and `conformance/scenarios.tsv` are rendered, not
hand-kept.

A prompt or an agent command line is changed in `03-prompts.md` or `02-agents.md` and nowhere
else; then `python3 tools/check_fixtures.py --write` regenerates the suite's fixtures. Never edit
`conformance/fixtures/` by hand.

## Writing a requirement

**Quote the sentence.** A claim about what another requirement says carries that requirement's own
words in backticks; "`RUN-12` forbids …" is an assertion.

**Cite the owner.** One rule, one home; everywhere else points at it. An argument has an owner too —
re-explaining a rule in a second document is how a second normative copy gets written.

**Cite the list; let it hold the number.** A count written into prose is wrong the first time
either end moves.

**A decision gets its identifier when it is accepted, not when it is written.** Phrase every
accepted change against an identifier — "amend `DIR-6`", "add SEQ-11" — so that checking it
landed is a `grep`.

## Vocabulary

`CONTEXT.md` is the glossary and the only glossary. Use its terms — Manager, Implementer,
Reviewer, Panel, Run, Round, Sequence, Task File, Finished File, Run Directory, Checkpoint,
Interference, Idle — and not their avoided aliases. "Tampering" is on the avoid list because
`DIR-9` rules the adversary out.

## Agent skills

### Issue tracker

Beads (`br`), local-first in `.beads/`, committed with the specs. Issue prefix `rl`. Never
hand-edit `issues.jsonl`; `br sync --flush-only` before committing.

### Domain docs

Single-context: `CONTEXT.md` and `docs/adr/` at the root.

## Conventions with a home already

- Identifiers, retention, withdrawn ids → `README.md`, *Requirement conventions*.
- Vocabulary → `CONTEXT.md`.
- Decisions and what was rejected to reach them → `docs/adr/`.
- What an Implementation must demonstrate → `06-conformance.md`.
- What was deferred or left open → `07-open-findings.md`.
