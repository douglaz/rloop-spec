# The formal model generates the Conformance Suite's scenarios

**Status:** accepted (2026-09-17, after two independent reviews — Fable and gpt-6-astra — both
"adopt with changes"; the changes are below)

rloop's control flow is one small total decision function, so the Lean model that owns the decision
table also enumerates every scripted agent behaviour up to a small round cap and emits, per script,
the expected exit code and spawn trace. The Conformance Suite replays each script through fake
agents against a real executable. Hand-written scenarios were the alternative; they are a second
copy of the table and they miss the combinations nobody thinks of (A→B→A task rewrites, a done file
beside a failed Manager, partial Panels at the cap).

A theorem is still never conformance: scenarios are evaluations of definitions, conformance is the
executable passing them, N scenarios are N points of evidence, and no `CNF` identifier appears under
`tools/formal/`.

## What the reviews changed

- The Task File is modelled as content identities, not "changed?", or A→B→A is inexpressible.
- `STATUS` is three-valued (`done | blocked | other`); the phase (pick or judge) and an absent Task
  File are inputs. A Finished File present before the pick is not: `ADR-0003` makes it unreachable.
- Interference by a non-Manager is an input — at most one point per script, to hold the count — and
  the property is non-interference: exit code and spawn trace are the same whatever it is.
- Behaviour is a total function of the round, not a finite list — termination over a list is
  vacuous. The cap is a bound on Implementer spawns; a hung agent is a hypothesis.
- Between Runs the model carries only whether the tree is `clean` (`ADR-0004`); git is not
  modelled, and "rloop never writes history" is the suite's `CNF-19`, not a theorem.
- The Panel is reduced to classes (all, some, none succeeded) to keep the enumeration in the low
  hundreds; the gate prints the count. Reviewers in a Round are compared as a set, never a sequence.
- Every guard is shown load-bearing for the suite, not only for the model: `lake exe scenarios
  --controls` counts, per guard, the scenario lines the model without it would get wrong and
  refuses zero; and `conformance/run --self-check` flips one expected line and requires red. A suite
  that cannot go red is a green check that asserts nothing. An Implementation repository may add
  mutants of its own executable on top.
- The emitted file is line-oriented and committed under `conformance/`, with a gate that regenerates
  and compares it, so an Implementation repository runs the suite with no Lean and no JSON parser.
- A few hand-written scenarios stay even for modelled behaviour: generation removes the independent
  chance to notice the rule itself is wrong. Everything byte-level or OS-level (argv and prompt
  equality, STATUS spelling variants, partial writes, signals, timeouts) is hand-written and the
  README says it is outside the model.

## Escape hatch

If the enumerator outgrows roughly fifty lines of Lean, fall back to the rendered table plus ten
hand-written scenarios.
