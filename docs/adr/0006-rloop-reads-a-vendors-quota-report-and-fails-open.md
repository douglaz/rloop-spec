# rloop reads a vendor's quota report and fails open

**Status:** accepted (2026-09-21)

An exhausted model does not fail fast. It hangs, writes zero bytes on both streams, and is killed
at its seat's timeout. A Reviewer seat therefore pays `--reviewer-timeout` every Round for a model
that was never going to answer, and rloop learns this by spending the timeout and forgets it before
the next Round. Measured on the Run that produced `9bd4166`: `fable` was killed at exit 124 in both
Rounds, roughly thirty of the Run's forty-six minutes.

So rloop runs the probe `AGT-18` states before each Panel and reads the `Current week (<family>):
<n>% used` line out of it (`RUN-21`). That is a vendor's human-facing report, with no contract
behind it, parsed by a Specification that is otherwise language-neutral. All three advisers
consulted on rloop-spec#3 objected to exactly that, in some form of "this encodes vendor billing
behaviour in an orchestration Specification".

The objection is answered by what this set already is. `ADR-0001` makes it language-neutral about
the **Implementation**; everywhere else it is deliberately harness-specific, hardcoding
`claude-fable-5-1`, `gpt-6-astra`, `gpt-5.6-sol`, `claude-opus-5`, the `--effort` values and
`AGT-7`'s deny list byte for byte, with `AGT-17` pinning the CLI versions. `AGT-17` also already
concedes this exact risk class — *"a flag that a newer CLI rejects is found only by a live Run"* —
so a `/usage` format that drifts is the same accepted exposure as a flag that drifts, not a new
one. The format did drift once during this work: between 2026-09-20 and 2026-09-21 the reset time
in that line moved from `2:59pm` to `3pm`. `RUN-21` reads the family and the percentage and nothing
else, so it did not care.

**Fail open is what makes the objection survivable.** Only a positive, unambiguous reading counts.
A probe that exits non-zero, hits its bound, writes nothing, writes something unparseable, reports
under 100%, or names no family for a Reviewer's model leaves that Reviewer `unknown`, and an
`unknown` Reviewer is spawned. A drifted format degrades to doing nothing, never to a silently
smaller Panel. This is also what keeps a mistyped model name loud rather than quiet: a wrong name
exits 1 in seconds with `[claude-code:unrecognized_model]`, while exhaustion hangs with zero bytes,
and the two signatures are not confusable.

## Consequences

- **The probe is not an agent.** No prompt is rendered into it, it produces no Feedback File, and
  it takes no part in the spawn trace the model enumerates — so the formal model and every
  scenario `conformance/scenarios.tsv` holds are untouched by it. It is nonetheless bounded,
  recorded and argv-checked like everything else rloop spawns.
- **No codex probe.** That vendor publishes no quota at all: `codex exec "/status"` reports the
  sandbox and `codex doctor` reports auth and reachability. The only probe available would be a
  real inference call every Round, and fail-open means not probing costs nothing but the status
  quo. Both codex Reviewers read `unknown`, always. If codex ever exposes quota, `RUN-21`'s table
  is where it lands.
- **`OVR-1` is narrowed**, for the second time in two days and by the same reasoning as `F9`: the
  sentence was banning a reading it was never written to ban. It protects rloop from acting on an
  agent's judgment; a quota report is not one.
- **The verdict is a record first.** `RUN-21` writes `probe-<r>.md` and says nothing about the
  Panel, which is what made this shippable and falsifiable on its own: `CNF-24`, `CNF-25` and
  `CNF-26` read the record, not the Panel. `RUN-15` is what acts on it, and landed next.
- **The Specification now leads `rloop-bash`.** `CNF-9`, `CNF-24`, `CNF-25` and `CNF-26` are red
  against it until it implements the probe. That is `ADR-0001`'s designed path — an amended
  requirement, a pin bump, a code change there — not a regression here.
