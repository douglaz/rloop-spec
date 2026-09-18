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
