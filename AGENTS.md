# AGENTS.md

Specifications only. `tools/` holds the gates that check them, `conformance/` the black-box suite
an Implementation is held to, and `.github/workflows/` runs the gates. Nothing that implements
rloop belongs here (`ADR-0001`): Implementations live in their own repositories and pin this one
as a submodule.

## Gates

`nix develop --command bash tools/check-all.sh`, before you start and again before you report
done. Run it unpiped — a pipe reports the pipeline's status, not the gate's, which is why
`check-all.sh` captures each exit code directly. The shell is required: the formal gate needs
Lean, and a missing toolchain is a red gate, not a skipped one.

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
