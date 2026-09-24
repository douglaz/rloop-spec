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

## F2 — Citation and obligation gates (citations delivered 2026-09-22; obligations still deferred)

provisiond-spec's citation and obligation gates supplied the precedent. A probe here then found
candidate restatements, triggering the accepted citation work. Delivered: the restatement check
in `tools/check_ids.py` and the quoted-attribution part of provisiond-spec's
`check_citations.py`, ported to `tools/check_citations.py`. Amended `RUN-3` to point at `SEQ-4`
for the Sequence check while retaining its own lone Run permission and dirty-at-start recording.
Amended `OVR-4` into a pointer to `AGT-15`, removing its duplicate process-lifetime prohibition
and the corresponding home exemption; its identifier and conformance coverage remain.
Amended `RUN-18` to point to `OVR-3` for git mutations while retaining its own rule about the
Implementer's commit choice. Amended F2 to deliver the blocking/advisory boundary decided in
[ADR-0007](docs/adr/0007-a-gate-that-cannot-decide-warns-rather-than-blocks.md).
Restored `ADR-0006`'s original probe reference and `RUN-16`'s historical quotation, which the
scanner work had reworded. They now report advisory findings without exemptions; the duplicate
normative rules remain removed.

A line citing another requirement and carrying an uppercase RFC-2119 keyword is a restatement
candidate unless it defines its own rule or carries the cited owner's words in backticks. Exact normative phrases have no
minimum word count; backticking only a modal (including its negation) does not quote the rule.
Both gates retain associations across sentences, semicolons and wrapped lines within a
paragraph. Blank lines, list items (`-`, `*`, `+` and numbered items), table rows, headings and
requirement definitions end that association. Backtick spans can wrap within a unit but cannot
absorb another one, even after an unmatched delimiter. Being inside a requirement body does not
excuse a second rule.
`tools/restatement-homes.json` records the reviewed defining clauses by enclosing owner and
exact normalized-text digest, with the reason each citation names
an input, command, subject or related operation. A changed clause requires renewed ownership
review; a new definition line is not automatically exempt. Fingerprints cover individual clauses,
not entire association units, so an adjacent new rule still needs review. The digest is taken
over normalized text, and the normalization is a character rule, not a Markdown parser: every
asterisk, backtick and tilde is removed wherever it occurs, including inside literal code and
identifiers, so `~~strikethrough~~` and `*emphasis*` never change a digest or a quotation, and a
tilde or asterisk that is part of a path or a glob is lost too; every underscore is kept wherever
it occurs, so `_emphasis_` changes a digest and a quotation and an underscore inside an identifier
is significant; runs of whitespace, including wrapping, collapse to one space, and case,
punctuation and words are preserved. A reviewed clause rewrapped in `_…_` therefore reads as a
new clause and needs its digest in `tools/restatement-homes.json` refreshed, while one rewrapped
in `~~…~~` or `**…**` does not. Self-citations remain at their own home.

Both checks report each finding as `BLOCKING` or `ADVISORY`. Blocking findings fail the
individual check and the aggregate gate, even alongside advisories. Advisories remain visible
and do not change the exit status. Identifier integrity failures still block.

For quoted attributions, the blocking forms are:

- An identifier followed by a colon and then the quotation, separated only by whitespace.
- A bare possessive followed by the quotation, separated only by whitespace, including straight
  and curly apostrophes.
- A quotation immediately after its recognized introducer, separated only by whitespace.
- An attached parenthetical whose ownership prefix consists of identifiers and separators
  (whitespace, commas, semicolons, slashes or ampersands). The prefix is the content before
  the literal lowercase `; but see`, with flexible whitespace, or the whole content when the
  marker is absent. Every owner in that prefix is checked; identifiers after the marker
  claim nothing. Thus a correct owner cannot rescue an incorrect owner in the same list.

The enumerated introducing-phrase list is empty. Recognizing a speech introducer does not
make unrestricted prose after it blocking. The recognized introducers are `says`, `states`,
`reads` and their past tenses, possessive `(own) rule/claim/wording/statement/sentence/words/text
that`, and `gives … meaning as`. Every introducer form requires whitespace-only attachment to
its quotation. Inferred speech through ordinary prose, comma- or dash-delimited asides or input
identifiers is advisory. Speech association stops at sentence punctuation
(`.`, `!`, `?`, `;`) or another quote; the latest introducer supplies the speaker.
Continued quotations joined by a comma, whitespace, `and`, `or` or `also` inherit the owner,
not its tier: they are advisory unless they have their own blocking form.

An attached non-nested parenthetical beginning with an identifier still claims owners before
the explanatory marker when the prefix contains prose; those inferred claims are advisory.
Parenthetical recognition does not collect citations beyond the closing parenthesis. A later
parenthetical cannot replace a speech attribution: each relationship is checked with its own
tier. A correct advisory attribution cannot hide an incorrect explicit owner, and a separate
blocking relationship cannot promote an inferred one.

The nearest-citation fallback also remains advisory: a normative backtick quote without a
recognized speaker or parenthetical owner binds to the nearest citation in its paragraph,
even when explicit recognition declines the form. Restatement association across intervening
prose or sentence punctuation is advisory too. For an uncovered modal, the explicit colon,
possessive or attached ownership prefix must belong to its own clause; a separate quotation's
syntax cannot make it blocking. Sentence boundaries beside parentheticals still end that clause;
punctuation inside quotations or parentheticals does not split the outer clause. A quotation
with no recognized owner does not cover a modal for the restatement check, so a declined
attribution can still report an advisory restatement.

The citation check compares a contiguous phrase against that owner's body only, ending at the
next definition or section heading. Both sides are normalized by the character rule stated above
for the digest, and by nothing else. A parenthetical attribution without an RFC-2119 keyword or an
explicit introducer retains the source's four-word prose heuristic, so short code labels citing
their definitions are not mistaken for prose quotations. Normative phrases and explicit
introducers have no such minimum. Both tiers use the same phrase eligibility and verification;
no other document, historical word, teaching marker or baseline supplies missing words.
The lexical scan does not parse relative clauses or distinguish a speech claim from its denial;
these inferred findings remain for a reader to judge.

The source's unquoted-attribution ratchet, baseline, Lean-name machinery and historical self-test
were not ported. Unquoted summaries, implicit attribution across independent blocks, fenced
examples and internal contradictions without a lexical signal still need review. An exact quote establishes
wording, not the correctness of the argument using it. The controls in
`tools/test_citation_gates.py` exercise both checks together, including changed words, misleading
code spans and owner-boundary failures; README's Gates table and CI carry the invocations.

`check_obligations.py` stays deferred: the observed obligation finding was a paraphrase, not a
duty assigned to another requirement's subject, and no instance of that gate's shape appeared.

Two of the four shapes recorded against this needed no gate at all. The copy in an Implementation's
`README.md` was deleted for a pointer, and the Specification's own operator section now cites its
owners (`ADR-0005`). `CONTEXT.md`'s example dialogue now uses no value this Specification owns —
no identifier, no filename, no exit status — which every other example dialogue surveyed already
did without a rule to make it.

## F3 — Unaccepted commits behind a clean tree (open, stated)

`ADR-0004` and `SEQ-10`: an Implementer may commit during a Run that ends blocked or capped;
the next invocation's base takes those commits in unreviewed. Closing it needs rollback, which
rloop will not have. Open by decision; the Finished File's report is the mitigation.

## F4 — The scenario alphabet is a choice (open)

`Rloop.Scenarios` enumerates seven Manager outcomes, two Implementer outcomes, three Panel
classes, one interference point per script, a block of probe scripts, a block of Seat scripts,
and caps 1 and 2. Fable's
review of `ADR-0002` argued depth 2 suffices because the decision is memoryless apart from the
Round counter; astra's asked for cap 3 and the default of 10 as explicit lines. Cap 10 is
`CNF-3`'s job only through `--max-rounds`; a cap-3 enumeration was not added. Revisit if an
Implementation passes the suite and fails live on a Round-3 behaviour.

The probe scripts (`F13`) took the count from 206 to 227. They are a block of their own, not an
axis crossed with the rest: the Panel's class and its membership are independent in the model, so
a cross product would add lines that differ only in one trace token's members while taking the
same decision path, which is the growth `ADR-0002` reduced the Panel to classes to avoid. The cost
is stated: the 206 lines leave the probe unscripted, so an Implementation whose availability
reading leaks into a Round the block does not script is caught only by the block.

The Seat scripts (`RUN-22`) took it from 227 to 237, and the growth is additive: every one of the
227 lines kept its exit and trace byte for byte and gained only the `seats` column, as `-`. The
ten are chosen one by one rather than drawn from an alphabet — each Seat refused at the pick, and
the Manager's on the table's other row as well; the Manager's Seat left alone by the other family;
the judge withheld in Round 1 and in Round 2; the Implementer's Seat read `unavailable` by a Round
and the Run finishing; both Seats on the table under two probes that fail open and one clear one —
because crossing Seats with the rest would repeat every line that no verdict of theirs can stop.
The cost has the same shape: the 227 lines seat no model on the table, so an Implementation whose
Seat reading leaks into a Run they script is caught only by the block and by `CNF-25` to `CNF-31`.

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

## F12 — The Consultation needs two models that answered (open 2026-09-20)

rloop-spec#5: its second comment, "Settled, 2026-09-20 — the Consultation quorum", records the
accepted design from a three-adviser consultation. An adviser that hangs or exhausts its quota
has not disagreed, and sending the operator to clarify a specification diagnoses the wrong
failure. Retrying that adviser each Round also spends the Manager's turn on a known non-answer.

Amended `RUN-20`, which now owns the whole policy and is where it is read: what an answer is, how
a model that did not answer is replaced and why it is not called again, the bounds, the
single-vendor case and what a blocked report must say. Two of its rules are the ones this finding
exists to explain. `RUN-20`: `The Manager MUST record every model called and what each did` is
what makes selective disclosure visible — without it the quorum is satisfiable by re-rolling
advisers until two agree. And the blocked report states two independent facts rather than choosing a cause,
because an adviser that hangs has not disagreed and no one can say whether its answer would have
settled the question. Amended `PRM-1` and `PRM-2` to carry the policy at pick and judge,
regenerated their fixtures, and replaced the Consultation glossary entry with a citation to its
owner. The adviser command lines are unchanged.

2026-09-23: amended `RUN-20` so that an adviser whose model the Probe found out of quota counts as
one that did not answer without being called, `PRM-1` to list the Probe's `unavailable` Reviewer
Seats in a new `{{UNAVAILABLE}}` render (`PRM-6`, asserted by `CNF-32`), and `PRM-2` to read the
same fact off the Round's `REVIEWER NOT RUN` Feedback Files. On 2026-09-22 a Consultation at the
pick called `fable` while `claude-fable-5-1` was at 100% of its weekly limit and lost 600 seconds
to a call that wrote nothing: the waste `F11` calls rloop-spec#3, moved from the Panel to the
Consultation. The verdict was in the vendor's report, and on disk in the same Run seventeen minutes
later as `probe-1.md`'s `fable:unavailable`, but nothing carried it to the Manager at the pick: no
Probe ran before the pick then. `RUN-21` now runs one there and it writes `probe-pick.md`, which
nothing in the prompt read until this amendment. rloop still runs no Consultation; it states the
fact in the prompt, as `{{DIRTY_AT_START}}` states the caller's paths. Amended the record sentence
of `PRM-1` and of `PRM-2` so that a skipped adviser is recorded with its Probe verdict as the reason.

**Still open:** under `--manager codex` the shell-tool bound is unverified. The codex Manager's
hanging-adviser case remains open even with a per-call bound written into the prompts: a live
`CNF-22` observation nobody has made. It must show the Manager bounding hanging calls, using
counterparts without retrying a non-answering model in the Run, recording all calls and any
single-vendor Consultation, and leaving time to write the file the outcome needs — naming the
silent models and saying whether those that answered agreed. This amendment adds no duty to rloop.

## F13 — The model cannot yet express a partial Panel (closed 2026-09-22)

`RUN-15` has three arms — a Reviewer that failed, one that was never called, and the
zero-survivor abort that counts both — but `Rloop.panel_none_aborts` and
`Rloop.panel_abort_off_judges`, which `RUN-15` cited as its pair, modelled only `panel := .none`
(`Properties.lean`). The model had no input for availability, so `Loop.lean`'s single construction
site passed `Reviewer.all` and no enumerated scenario omitted a Reviewer: the behaviour was
specified and covered by `CNF-27`, and proved for the failure arm only.

Closed by `rl-availability-scenario-axis-rnp`. `Behaviour` gained `available`, keyed by Round and
Reviewer; a Panel's spawn names the Reviewers called, not `Reviewer.all`; and the zero-survivor
abort counts a Reviewer not run as down, a guard of its own, `notRunDown`, so that its absence has
a witness. `RUN-15` now cites `Rloop.not_run_and_failed_aborts`, `Rloop.not_run_down_off_judges`
and `Rloop.none_called_aborts` beside the first pair. `conformance/scenarios.tsv` gained a `probe`
column and a block of probe scripts (`F4` has the count): each family at 100% and both; both with
the codex Reviewers failing, the reachable form of all four down, since `RUN-21` gives no codex
model a family; `fable` unavailable in Round 1 and back in Round 2; and three probes read as
`unknown` — the matching line with a non-zero exit, the words not at the start of a line, and
families outside the table. The lines where not-run and failed Reviewers make the Panel all down
are the ones `lake exe scenarios --controls` counts for `notRunDown`.
`conformance/test-panel-trace` shows each case red against a mutant of `rloop-bash`: a table
without Opus or without Fable, a not-run Reviewer not counted down, verdicts remembered across
Rounds, the probe's exit status ignored, an unanchored match, and families given to the codex
Reviewers or matched by any name.

## F14 — The probe, live (closed 2026-09-21)

The first Run with `RUN-21` implemented, against the real CLIs, on this repository, while
`claude-fable-5-1` was genuinely at 100% of its weekly limit. rloop-bash `616bf4e`, spec
`9c28a85`, `--manager codex --implementer codex` and **no** `--reviewer-timeout` cap.

The probe answered in **three seconds** and `probe-1.md` read `fable:unavailable`, `opus:unknown`,
`astra:unknown`, `sol:unknown`. One real `/usage` exercised four clauses of `RUN-21` at once,
which no scripted shape does: the anchored match fired on `Current week (Fable): 100% used`; the
aggregate line was present at 69% and correctly not read; **no Opus line existed at all**, so
absence read `unknown` as the rule says; and both codex Reviewers read `unknown` for want of a
family. `probe-1.err` was empty.

`RUN-15` then held: three Reviewer processes were spawned, not four — one `claude` at
`--model claude-opus-5 --effort xhigh` and two `codex` — `feedback-1-fable.md` was byte-identical
to `REVIEWER NOT RUN (unavailable)`, and `reviewer-1-fable.err` was zero bytes.

**What it cost, and what it saved.** The Panel finished in 6m45s, bounded by a live Reviewer. On
the default `--reviewer-timeout` the dead `AGT-7` seat would have held that Panel open for thirty
minutes, every Round, since a Panel cannot finish before its slowest seat and a seat that will
never answer always runs to its cap. Three seconds replaced it. This is what rloop-spec#3 was
filed for and it is now measured rather than argued.

**What it did not fix.** `astra` and `sol` each wrote a bare thirteen-byte `No findings.` — the
`PRM-4` shortcut of rloop-spec#4, now observed in four codex reports across two Runs without
exception. The Panel was therefore one substantive reviewer, `opus`, exactly as it was before the
probe existed. A silent seat is worse than a dead one: a dead seat is visibly absent in
`RUN-15`'s accounting, while thirteen bytes read as a review that found nothing. Fixing the seat
that hangs did not fix the Panel.

## F15 — `PRM-4`'s amended closing line, live (closed 2026-09-22)

`PRM-4` ended `If there is nothing to report, write exactly: No findings.`, the last and most
specific instruction in the report block, and it swallowed item 0 on the clean path. The codex
Reviewers were obeying it. rloop-spec#4 diagnosed that; `3da20a8` replaced the sentence with
`If you have nothing for items 1 and 2, write item 0 and then exactly: No findings.` and
rloop-bash `d37b128` adopted it.

**Before**, across three Runs on the unamended prompt: six codex reports, every one of them the
bare thirteen-byte literal, none carrying item 0.

**After**, the four-Round Run that built the restatement gates, on rloop-bash `d37b128` — the
executing store path was checked for the amended bytes first, because `nix run` had silently
served a cached older build on an earlier attempt:

| Round | `astra` | `sol` |
|---|---|---|
| 1 | 1551 | 3126 |
| 2 | 1760 | 1411 |
| 3 | 1297 | 1191 |
| 4 | 146 | 1121 |

Eight reports, eight carrying item 0. The Round 4 `astra` report is the one that matters, because
it is **clean** and still 146 bytes rather than thirteen: `0. I ran everything I needed. Both
unpiped aggregate gate runs exited 0; all 41 regression tests and six independent probes passed.`
followed by the literal. Provenance restored, and the literal kept, so a clean report is still
machine-recognisable. `sol`'s Round 2 report carried the other half of item 0's purpose — a
control it could not run, which the Manager would otherwise never have learnt.

*What it bought, in the same Run.* Reviewers that had been silent for six consecutive reports
drove Rounds 2, 3 and 4, each on a real defect in the gates being built: a restatement escaping
past a semicolon, a quotation misattributed across intervening prose, a short quotation with a
false owner, and the normalizer disagreeing with this finding's own description of it. Round 1's
work passed every gate and would have merged. The prompt fix is why it did not.

*What it does not settle.* Two models, one repository, one task shape. `00-overview.md` says the
prompts are `checked for equality, never for quality`; this is one observation, not a property.

## F16 — Headless agents end their turn on a background check (open 2026-09-23)

Three times a claude Seat started a long check in its shell tool's background and ended its turn
to await it. Headless, nothing resumes it.

- Run `20260923T022252.771492072Z-505649`, Round 1, the Implementer: its whole output was
  ``Still running `u2`. I'll be re-invoked when it finishes.`` Its work was left uncommitted and
  unreported, and a regression it would have caught went to the Panel instead.
- The same Run, Round 2, the `fable` Reviewer: its whole Feedback File was
  `Waiting on the background runs. There is nothing else independent to fetch;
  every remaining item depends on those results.` A Seat spent, no review.
- Run `20260923T042304.628017728Z-505649`, Round 1, the Implementer: `Both suite runs are still
  going; I'll pick up when they report.`, its work complete and uncommitted, although its brief
  carried the milder `Do not end your turn while a check is still running in the background; wait
  for it and report its result.` The Round 2 brief said `Run every command in the foreground and
  wait for it.` and forbade the background outright, with the reason; the Implementer complied.

Amended `PRM-3` and `PRM-4` with one identical sentence before the closing one, and regenerated
`PRM-3.txt` and `PRM-4.txt` by the fixtures tool (rl-agents-end-turn-on-background-check-twn).
`PRM-3`: `Run every command in the foreground and wait for it to finish; do not use your shell
tool's background facility, because nothing resumes you if your turn ends while a command is
still running.` A Consultation chose the prohibition over the milder sentence and over leaving it
to each brief: the failure is the harness's, not any task's.

*What does not follow.* One observation of the prohibition complying, in a brief, under
`--implementer claude`; nothing yet shows the sentence working as prompt text, nor anything under
`--implementer codex` or from a codex Reviewer. `00-overview.md` says the prompts are `checked for
equality, never for quality`. **Open** until a Run on an Implementation carrying the amended
prompts shows an Implementer and a claude Reviewer running a long check to completion.
