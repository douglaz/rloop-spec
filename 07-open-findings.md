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
individual check and the aggregate gate, `tools/check-all.sh`, even alongside advisories.
Advisories remain visible and do not change the exit status. Identifier integrity failures still
block.

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
Seat reading leaks into a Run they script is caught only by the block and by `CNF-25` to `CNF-32`.

Giving the probe block the `some` Panel class took it from 237 to 256, and that growth is
additive too: every one of the 237 kept its exit and trace byte for byte. The class had been left
out of all seven scripts for one reason — `conformance/fakes/agent` scripted `some` as `fable`
alone succeeding, so where a probe took `fable` out of the calls the Round was a Panel of failures
rather than the class the line named. The reason covered three scripts of the seven, `fable`,
`both` and Round 1 of `fable|clear`, and cost the block the one combination none of the rest
reaches: a Round with an uncalled Reviewer, mixed outcomes among the called ones, and a judge that
still runs. The fake now scripts `astra` succeeding beside `fable`, and `astra` holds a model
`RUN-21`'s table does not name, so no probe shape takes it out and every script realises the
class — the old reason is obsolete, not narrowed. The cost of the block keeps its shape: those
lines are where an Implementation that drops a Panel's survivors once the probe has taken a
Reviewer out is caught, and `conformance/test-panel-trace` shows one of them red against a mutant
that reads a Reviewer not run beside a called one that failed as an all-down Panel.

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

2026-10-02 (rloop-spec#9): re-derived `CNF-22`'s Consultation observations from `RUN-20`, obligation
by obligation, with the mapping written into `CNF-22`: each obligation quoted beside the
observation that witnesses it, and the ones no observation reaches listed there with their
reasons. The observations had grown one per review finding, each against the defect it patched,
and two gaps came of it. The single-vendor observation asked only for the marker, so a Run in
which no adviser answered satisfied it; it now asks for the other vendor's two answers, their
agreement and the settled choice as well. And the Probe-verdict skip of 2026-09-23 had no
observation; it has one now, conditional like the blocked one, because a Probe record reads
`unavailable` against the real CLIs only when a model's quota is really exhausted, which a release
cannot produce at will. A release that lacks either conditional observation says so in a statement
kept with the record.

2026-10-02 (`rl-run20-open-points-m56t`): replaced the pair-and-counterpart policy in `RUN-20`,
which supersedes what the paragraphs above say of it. A Consultation now calls every adviser its
relevant Probe record does not read `unavailable`, all of them together; it carries nothing over
from an earlier Consultation of the Run; and it settles on the unique leading position held by at
least two answers, a tie or fewer than two answers ending the Run `blocked`. The two pairs,
replacement by counterpart, the rule that a model that did not answer is not called again in the
Run, the second question put to the remaining advisers on a disagreement and the total
Consultation budget are gone; `ADR-0009` records why, and what was rejected. `PRM-1` and `PRM-2`
carry the new policy and their fixtures were regenerated. `CNF-22`'s Consultation observations are
five short items again: the mapping the entry above describes, and its list of what no observation
reaches, are deleted.

**Still open:** under `--manager codex` the shell-tool bound is unverified. The codex Manager's
hanging-adviser case remains open even with a per-call bound written into the prompts: a live
`CNF-22` observation nobody has made. It must show the Manager bounding hanging calls, letting
the remaining answers decide, recording all calls and any
single-vendor Consultation, and leaving time to write the file the outcome needs — naming the
silent models and saying whether those that answered agreed. This amendment adds no duty to rloop.

2026-10-03 (`rl-adviser-floor-vjqt`): the owner supplied these observations. In Run
`20261003T041125.632310657Z-3550034`, the pick for `rl-lineciteg-no-antecedent-and-control-8k2`,
the codex Manager chose 240 seconds for every adviser. `opus` (`claude-opus-5`, effort `xhigh`)
exited 124 with empty stdout and stderr after 240.5 seconds; fable, astra and sol answered in
55–128 seconds. An xhigh Reviewer of the same model routinely takes 15–25 minutes here, so an
arbitrarily short chosen bound can remove it from a Consultation.

The owner also verified on 2026-10-03 that Claude Code's Bash ceiling is controlled by
`BASH_MAX_TIMEOUT_MS`, default 600000 ms, including under `claude -p`. With both
`BASH_DEFAULT_TIMEOUT_MS=5000` and `BASH_MAX_TIMEOUT_MS=5000`, a request to run
`sleep 15; echo FINISHED` returned `Exit code 143 / Command timed out after 5s` after about
10 seconds wall time. The timeout killed the command. A 600-second adviser bound plus
termination grace therefore does not fit under that default ceiling. These are supplied
observations, not experiments repeated in this Round.

Amended `RUN-20`: `Each call's chosen maximum duration MUST be at least 600 seconds`;
`This is a floor on the bound: a call that answers sooner ends sooner`. Amended the duration
sentences in `PRM-1` and `PRM-2` and regenerated their fixtures.

Amended `AGT-13`: ``For every Manager call (pick and every judge) under
`--manager claude`, rloop MUST set this to `--manager-timeout` in milliseconds (seconds multiplied
by 1000), overriding any inherited value, regardless of the selected model``.

Amended `CNF-10` and its executable checks for the recorded ceiling, and `CNF-22`'s Settled
observation for the recorded duration floor; `ADR-0009` points to the bound's owner. Fake environment recordings do
not establish live shell survival.

**Still open:** whether `codex exec`'s shell tool keeps a foreground command alive past
610 seconds. The cited Run establishes only 240.5 seconds. The first live Consultation under
the floor settles this question; this amendment does not claim it has already done so.

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

Each observation below is a claude Seat that started a long check in its shell tool's background
and ended its turn to await it. Headless, nothing resumes it.

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
- Run `20260925T024030.524416029Z-367594`, Round 1, the **judge** (the Manager under `PRM-2`, a
  `claude` Seat): its whole output, `manager-judge-1.out`, was one line, `The suite is halfway;
  the rest of my work needs its final verdict list, so I'll wait for its completion notice.`
  Neither `task.md` rewritten nor a Finished File: `RUN-12`'s `no decision`, so rloop exited
  2, the Round's accepted work was left uncommitted, the bead claimed, and the Sequence stopped.
  `PRM-2` carried no such sentence: the amendment below had reached `PRM-3` and `PRM-4` only.

Amended `PRM-3` and `PRM-4` with one identical sentence before the closing one, and regenerated
`PRM-3.txt` and `PRM-4.txt` by the fixtures tool (rl-agents-end-turn-on-background-check-twn).
`PRM-3`: `Run every command in the foreground and wait for it to finish; do not use your shell
tool's background facility, because nothing resumes you if your turn ends while a command is
still running.` A Consultation chose the prohibition over the milder sentence and over leaving it
to each brief: the failure is the harness's, not any task's.

Amended `PRM-1` and `PRM-2` on 2026-09-25 with the same sentence in the same place, the block's
last line before the closing one, and regenerated `PRM-1.txt` and `PRM-2.txt` by the fixtures tool
(rl-prm2-foreground-judge-88k). `PRM-2`: `Run every command in the foreground and wait for it to
finish; do not use your shell tool's background facility, because nothing resumes you if your
turn ends while a command is still running.` The judge is the call whose lost turn costs the most:
the Round's accepted work stays uncommitted and the Sequence stops.

*What does not follow.* One observation of the prohibition complying, in a brief, under
`--implementer claude`; nothing yet shows the sentence working as prompt text, nor anything under
`--implementer codex` or from a codex Reviewer. `00-overview.md` says the prompts are `checked for
equality, never for quality`. **Open** until a Run on an Implementation carrying the amended
prompts shows an Implementer, a claude Reviewer and the judge running a long check to completion.

## F17 — A claim about `CNF-24` withdrawn, cleanup witnesses and their limits (open 2026-09-26)

Residuals of `rl-cnf34-step-not-call-nfy`, the change that gave `CNF-34` a witness of the
Checkpoint boundary, and the claim that change carried and this one withdraws. They had lived only
in commit messages until now.

*`CNF-34`'s own-process assertion at a call boundary is separable from `CNF-24`, and a mutant
separates it.* `CNF-24` orders a Run's calls by the `NNN-` prefix each fake writes as it
**starts** — it has every Round run the probe `after that Round's Implementer and before any of
its Reviewers starts` — so it cannot see whether an earlier call's process had **exited**, and an
Implementer still alive when the probe starts leaves it green. The own-process assertion of
`CNF-34` carries that boundary alone. The mutant was built and measured this Round, by the `opus`
Reviewer and reproduced by `astra`: the reaping scratch copy of rloop-bash with the Checkpoint and
the probe's spawn moved ahead of the Implementer's reap — the plain `AGT-15` violation at a call
boundary — gives a red `CNF-34` naming `implementer-1` alive when a later call started, `CNF-24`
green beside it and every other verdict line as in the unmutated run. `3e334bb`'s commit message
argued that no such mutant exists and `eb4936f` carried the claim into this finding; it was
reasoning rather than measurement, and it is **withdrawn as unsound**. It is recorded here rather
than edited out of history so that it is not argued a third time. The Checkpoint arm was never
inside that argument — its boundary is a step and no call, and the Checkpoint-before-reap mutant
reddens `CNF-34` alone.

*At opening, the `manager-0` arm of the own-process loop had no mutant behind it.* The investigation below
supersedes this paragraph's own-process and Interference limitations.
Of the mutants built for this earlier work, the one that reddens the own-process loop's `implementer-1` arm is the probe started
before the Implementer's group is reaped; the Checkpoint run before that reap reddens the new
Checkpoint witness alone, since it still waits for the Implementer's own process and leaves
`CALLS_ALIVE` clean. The `manager-0` arm is the same predicate over a pid that later records do
carry, so it is live code and not dead, and it is exercised green on every run — but nothing
demonstrates it red, which is the standard `AGENTS.md` sets when it says *a guard without one is
decoration*. Those historical demonstrations left the arm's interference knob unexercised besides:
rloop-bash `02c6206`'s Checkpoint compares with `cmp -s` (`bin/rloop:286`), and of `cmp` and `find` `CNF-2`
says they `are the suite's own and are not on the executable's PATH`, so that executable sets
`task.md` aside whether or not the Implementer ticked it — the arm re-run with
`RLOOP_FAKE_INTERFERENCE` removed gave the same green and the same red, so the flip is the reap
boundary's alone, but neither `RLOOP_FAKE_INTERFERENCE=1:afterImplementer:editTask` nor the guard
against a missing `rejected-1-task.md` is demonstrated by that executable.

*Which of `CNF-34`'s own-process reads a mutant reddens.* The Reviewer and Probe rows the item
gained after this finding opened (`rl-cnf34-reviewer-probe-rows-2mv`) have mutants of their own,
built against the same reaping scratch copy of rloop-bash `02c6206`, each mutation gated on
`RLOOP_FAKE_GRANDCHILD_IGNORE_TERM` so that exactly one `CNF-34` Run is mutated and every other
verdict line of the suite stays byte-identical. A Reviewer's own-process read is demonstrated only
beside group brackets: no mutant reddened a Reviewer's own-process bracket with that Reviewer's
group bracket green. The probe's read separates. The mutant that neither waits for nor reaps the
probe until the next call has started, at both of `RUN-21`'s call sites, gives two brackets and no
others: `[probe-0: 001-probe-0.env GRANDCHILD … alive when 002-manager-0.env started]`, the group
half of the read at the pick's boundary, and `[probe-1: 004-probe-1.env PID … alive when
004-reviewer-1-fable.env started]`, the own-process half against one of the Panel's four records.
`probe-0`'s own-process half stays green under it — the probe's own process is gone before rloop
reaches the pick, which was the row's own gap as the suite then stood, filed as
`rl-cnf34-probe0-read-fast-fake-8et` and ended by the probe sleep landed below —
so at that boundary it is the group half that catches the deferral. What the `probe-0` own-process
read needs is one further defect, and it then reddens that read alone: the deferral narrowed to the
probe before the pick, with that one probe call's standard input left open — against `AGT-12`'s
`started with standard input from the null device`, so that the call outlasts the record — gives
`[probe-0: 001-probe-0.env PID … alive when 002-manager-0.env started]` beside a green group half,
as the item's whole detail and with no other item's verdict moved. `manager-0`, the arm above, is
then the only own-process read at a call boundary that no mutant reddens. The `survived the Run`
read is an own-process read of the item as well — `nothing_survived` (`conformance/run:66-78`)
reads `PID` beside `GRANDCHILD` — and no mutant of either Round reddens that half either, for the
reason its own comment gives: `Every ancestor is gone by then, so neither can be a zombie`
(`conformance/run:67-68`). Both own-process brackets come with a green group half for one reason:
the fake writes `GRANDCHILDREN_ALIVE` (`conformance/fakes/agent:121`) before it spawns the child
that ignores SIGTERM (`:178`), so a call that starts while the probe is still running finds no
`GRANDCHILD=` line in the probe's record and has nothing to report. The group half can be green with
the group alive, and it is the two halves together that caught these mutants.

*The remaining step boundaries before the 2026-10-03 investigation below.* The Checkpoint after
the Implementer and each probe's availability record are the step boundaries the item now observes, and each is a boundary
whose files a straggler races (`DIR-6`, `RUN-21`). The boundaries observed only at the call that
follows are the pick's, where the next step is `RUN-6`'s `copy the Task File to` `task-1.md`; the
Panel's, where `RUN-7` has `the Checkpoint again` and the judge's record is what the Reviewer row
reads in its place; and the judge's, where `RUN-7` has `the decision` — and in a Run of one Round no
later call exists at all, so the judge's own snapshot is read only to keep an unwritten one from
passing. A watching straggler was a candidate for each boundary the list names; none was witnessed
then. That list is of *steps*. `AGT-15`'s clause has another half — the read of the call's own
output — and the paragraph below settles it at one call site and leaves it unobserved at every
other.

*The Probe's two boundaries, settled 2026-09-29 (`rl-agt15-probe-record-step-taf`).* They were read
at the call that follows each, and by then that probe's verdicts are recorded: `RUN-21` has `After
each call it MUST record for every Seat exactly one verdict`, `before the pick` for the probe before
the pick and in Round `r` for the Round's. A straggler of the probe's group that raced that record
was therefore unwitnessed, and the `sol` Reviewer of this finding's Round measured the gap — a
mutant that writes the availability record while the probe's child is still alive and reaps the
group before the next call starts left `CNF-34` green. The specification owner settled the reading
in its general form, and `AGT-15`'s `A call is complete only once its process group has been reaped
that way` replaced the wording that put the reaping before the step that follows the call: rloop
reads the call's output only after the reaping, so each probe's record is on the far side of it at
both of `RUN-21`'s call sites, and `CNF-34` gained a watching straggler at each. The gap is closed
and the mutant is red. Rebuilt against rloop-bash `18c8807`, gated on `RLOOP_FAKE_WATCH`'s value
beginning `probe:` — what confines it to the two new Runs, where a gate on the variable merely being
set would mutate the Checkpoint arm too, whose value is `implementer:rejected-1-task.md`
(`conformance/run:798`) — and with the wait loop of that executable's `reap` inlined rather than
reordered so the verdicts still see the status the reaping sets, it gives `[probe-0 watch: the
probe's child saw probe-pick.md, so its group outlived the call and ran through the record]` and the
same bracket for `probe-1` and `probe-1.md` as the item's whole detail, with every other verdict
line of the suite byte-identical. Gated that way the mutant says nothing about the item as it stood
at `48d5f2c`: no row of that suite sets `RLOOP_FAKE_WATCH` to a `probe:` value, so the gate never
fires and the mutation is inert by construction. Ungated instead — applied at both of `RUN-21`'s
call sites with nothing to confine it — against that tree extracted with `git archive`, every
verdict line of the suite is byte-identical to the unmutated executable's, the item's own included,
so `CNF-34` stayed green there. That is the gap these two Runs close.

*The read of a call's output, witnessed 2026-09-29 (`rl-agt15-output-read-no-witness-a9h`).*
The straggler those two Runs gave each probe witnesses the record and not the read: it *polls*, and
reading a call's output leaves it no file to find, so a read taken before the reaping and one taken
after look the same to it. The witness for the read is a straggler that *writes* into the capture
`DIR-4` has the probe's standard output reach `entire and unmodified` — a line the reader acts on,
since an inert one changes no verdict — and `CNF-34` gained one Run of it, at the probe before the
pick (`conformance/run:738-779`). `RUN-22` is what makes the read observable there: it has rloop
`exit 2 without spawning any agent` on that probe's verdicts, so an executable that derives them
from bytes the straggler's line has not reached yet calls the pick and runs on. The knob is
`RLOOP_FAKE_WRITE_STDOUT`, which had only a role and a fixed line and now takes a first-write delay
and the line with it (`conformance/fakes/agent:67-86`, `:141`, `:172-175`); the row asks for one
second and `--kill-after 4`, so an early read is a second short of the line and a reaping one has
three seconds of the child's writing behind it before it reads.

The mutant is a scratch copy of rloop-bash `19f532a`, run behind a stand-in for that repository's
flake wrapper, which appends `diffutils` to `PATH`: `bin/rloop` calls `cmp`, which `CNF-2`'s PATH
does not carry, so run bare it is red on `CNF-3` and `CNF-9` whatever the mutation.
Its probe call sites snapshot the capture between the wait and the reaping and derive the verdicts
from that snapshot, leaving the record — and the refusal, and every other step — after the reaping,
so that it violates the read half alone and the two watching Runs above stay green. Ungated, at both
of `RUN-21`'s call sites: against the suite as it stood at `9d85f6f` every verdict line is
byte-identical to the unmutated executable's, `CNF-34`'s included, which is the blindness this Run
ends; against the amended suite its whole detail is `[probe read: exit 0, not RUN-22's refusal]
[probe read: 9 calls recorded, not the probe before the pick alone] [probe read: probe-pick.md is
not unavailable unavailable unavailable unknown unknown unknown: 'manager:unknown
implementer:unknown fable:unknown opus:unknown astra:unknown sol:unknown ']`, with every other
verdict line byte-identical. No gate confines it because none is needed: exactly one item's
verdict moves. A mutant that moves the *whole* verdict step ahead of the reaping instead — the
record with the read — is a different defect and the two watching Runs already red it (`[probe-0
watch: the probe's child saw probe-pick.md, so its group outlived the call and ran through the
record]` and the same for `probe-1`), which is why it witnesses nothing about this half.

Still unobserved: every other call's output read — the pick's, the Implementer's, each Reviewer's,
the judge's and the Round's probe's. `RUN-22` gives the probe before the pick an observable no other
call has. The ordinary `probe-0` own-process read was a separate gap, investigated below and ended
by the probe sleep that investigation's candidate became.

*The ordinary Probe's sleep candidate, declined 2026-10-03
(`rl-cnf34-probe0-read-fast-fake-8et`) and landed by owner decision the same day
(`rl-cnf34-probe-sleep-land-cuvo`).* The `02c6206` measurements above remain historical.
At Specification `46248df0f618bcda8646f01424feb1a8fab2e5b9`, the candidate was
`RLOOP_FAKE_SLEEP_PROBE=1` on the ordinary `rec-reap-probe` invocation alone, with the fake,
the watching and output-writing arms, and `--kill-after 1` unchanged. The correctly reaping
executable was a byte-identical scratch copy of
`/nix/store/mydjhwg0771w726kcp1gpx71v485kc4s-rloop/bin/rloop`, resolved from
`/home/master/p/rloop-bash/result/bin/rloop`, SHA-256
`4759d2779b719e8513fba386d2879e9290807ab7ec53383e604bde85cfbcaabd`;
the neighboring source repository was clean at `a110ec2a3e9c4eefa67ced14976e24263d83249f`.
The scratch mutant retained that executable's wrapper, including its appended `diffutils` PATH,
and the spawn's `</dev/null`. No Implementation repository or store file was edited.

The mutation initializes `deferred_probe=''`. At both Probe call sites it replaces
`reap "$pid"`, only when `[ "${RLOOP_FAKE_RECORD##*/}" = rec-reap-probe ]`, with
`deferred_probe=$pid; st=0`; otherwise it retains the original reap. At the end of `spawn`, after
`live+=("$pid")`, a nonempty `deferred_probe` is saved in `local deferred="$deferred_probe"`,
cleared, and waited for and reaped by `reap "$deferred"`. Thus the pick is spawned before the first
Probe's wait/reap, and `fable` before the Round's Probe's wait/reap; the latter finishes before the
remaining Reviewers are spawned. The early verdict read uses status zero for these successful
fakes. The activation condition does not use the candidate sleep. `mutation.log` in each ordinary
Run records both deferrals and the subsequent spawns; no other arm recorded an activation.

The full comparison, with complete ordered verdicts retained, was:

| Suite | Executable | Exit | Passed / failed | Seconds |
|---|---|---|---|---|
| Unchanged | Correctly reaping | 0 | 33 / 0 | 118.69 |
| Candidate | Correctly reaping | 0 | 33 / 0 | 120.73 |
| Unchanged | Deferral-only mutant | 1 | 32 / 1 | 118.51 |
| Candidate | Same mutant | 1 | 32 / 1 | 120.33 |

Only `CNF-34` failed for the mutant. Its unchanged detail was the `probe-0` `GRANDCHILD` bracket
against the pick and the `probe-1` `PID` bracket against `fable`; the candidate added only the
`probe-0` `PID` bracket in that full comparison. Every other item's verdict was byte-identical
across all four runs, and no other arm of `CNF-34` reported a bracket. This includes the watching
and output-writing arms. These totals retain the suite's printed qualifications: `CNF-4` was not
run with `--self-check`, and `CNF-22` is live, by hand.

That apparent isolation was judged on 2026-10-03 not to survive repetition. The ordinary arm was extracted with its
unchanged helpers and evidence guards, and run twenty times per suite against the same mutant,
alternating which suite ran first. Counts below are failures of each individual read:

| Earlier Probe / later call / read | Unchanged | Candidate |
|---|---|---|
| `probe-0` / pick / `PID` | 0 / 20 | 20 / 20 |
| `probe-0` / pick / `GRANDCHILD` | 18 / 20 | 18 / 20 |
| `probe-1` / `fable` / `PID` | 20 / 20 | 20 / 20 |
| `probe-1` / `fable` / `GRANDCHILD` | 0 / 20 | 2 / 20 |

Both reads against each of `opus`, `astra` and `sol` stayed green throughout. Candidate repetitions
09 and 11 added `[probe-1: 004-probe-1.env GRANDCHILD … alive when 005-reviewer-1-fable.env started]`;
their unchanged partners did not. The missing `probe-0` group brackets occurred in unchanged
repetitions 13 and 14, but candidate repetitions 01 and 14: equal totals conceal different reads.
For example, candidate 01's pick recorded an empty `GRANDCHILDREN_ALIVE` but the Probe's PID in
`CALLS_ALIVE`; both Probe pids were present in its completed record. These are guarded reads,
not missing-evidence passes. The fake's snapshots precede its child creation and sleep, so these
observations do not establish that the sleep deterministically changes a group read; they do
refute a claim of reliable isolation. Five targeted repetitions per suite against the correctly
reaping executable were all green. Every measured ordinary Run exited 0, every fake recorded
`STDIN=eof`, and neither variant reported a survivor or a missing record. The one-second sleep
left the sixty-second Probe timeout unchanged; this was not a timeout experiment. Targeted mean
runtime rose from 2.55 to 4.55 seconds for the mutant and from 2.57 to 4.57 for the correctly
reaping executable, consistent with sleeping once at each Probe.

Evidence was retained outside the Run Directory at
`/tmp/rloop-cnf34-probe0-20261003-mt6i_ig6`, a tmpfs path that records where it was and is not one
a reader can rely on: `provenance.json`, `mutation.diff`, `candidate.diff`,
the executable and suite copies, `analysis.json`, and `reads.csv` (each Probe's PID and child
against each relevant later call). `results/<label>/` holds the command, environment, direct exit
status and timing in `measurement.json`, complete stdout/stderr and ordered `verdicts`, and
`work.path` locates the retained fake records. Both suite copies differ from the repository only
by replacing the final cleanup trap with retention, plus the candidate's local setting.
To reproduce the full matrix from that evidence directory, give each invocation a fresh label:

```sh
python3 measure.py run unchanged reference rerun-u-ref
python3 measure.py run candidate reference rerun-c-ref
python3 measure.py run unchanged mutant rerun-u-mut
python3 measure.py run candidate mutant rerun-c-mut
```

`measure.py` runs the named suite in the foreground with null stdin and records its actual status;
`target` in place of `run` selects the extracted ordinary arm. `repeat.py` records the repetition
order; `analyze.py` checks the records and produces the read counts. `trial-u` and `trial-c` are
excluded setup failures from an unset variable in diagnostic logging, corrected before any full
or repeated measurement; `trial2-*` are preliminary measurements, also excluded from the tables.
The candidate was declined on 2026-10-03 under the bead's isolation rule: it exposed the target in
this sample, but other reads varied, including an added Round Probe group failure — `probe-1` /
`fable` / `GRANDCHILD`, 0 / 20 unchanged against 2 / 20 candidate. `conformance/run`, the fake and
`CNF-34` were left unchanged by that decision, and the suite was left with no demonstrated ordinary
`probe-0` own-process witness for the deferral alone.

*The decline reversed and the sleep landed, by owner decision 2026-10-03
(`rl-cnf34-probe-sleep-land-cuvo`).* The ground of the decline did not hold. The `opus` Reviewer of
Run `20261002T235249.000350681Z-3550034` re-ran the same target against the same mutant 90 more
times; its evidence was at `/tmp/reviewer-cnf34-probe1-check`, a tmpfs path that records where it
was and is not one a reader can rely on. Counts are failures of each read, the twenty repetitions
per suite above pooled with the Reviewer's:

| Earlier Probe / later call / read | Unchanged | Candidate |
|---|---|---|
| `probe-0` / pick / `PID` (the target) | 0 / 80 | 50 / 50 |
| `probe-1` / `fable` / `GRANDCHILD` (the read called added) | 2 / 80 | 4 / 50 |

On the read called added, Fisher's exact test, two-sided, gives p = 0.20 pooled and p = 0.60 on the
Reviewer's runs alone, and the bracket appears without the sleep, in the Reviewer's unchanged runs
`u07` and `u34`. The mechanism agrees with the counts: the fake writes `GRANDCHILD=` when it spawns
the child and sleeps only afterwards (`conformance/fakes/agent`), so the sleep comes after both
that write and the next call's read of it, and has no way to add the bracket. `CNF-34` was red in
every one of the 130 mutant runs. The technique is the one `rl-cnf34-remaining-boundaries-4lq`
accepted for the pick, below: a one-second delay that took the own-process read from 0 / 20 to
20 / 20.

What landed is the measured candidate and nothing else: `conformance/run` sets
`RLOOP_FAKE_SLEEP_PROBE=1` on the ordinary `rec-reap-probe` Run and on no other, the fake is
unchanged, and `CNF-34` states the sleep. The ordinary `probe-0` own-process read now has its
witness for the deferral alone: `[probe-0: 001-probe-0.env PID … alive when 002-manager-0.env
started]`. Against the landed suite, the same mutation rebuilt on the executable of rloop-bash
`297238b` (SHA-256 `d5c3284d443d7620c2708b009cc3b489decdfdb6ba55991bd7d1c06759d6989e`, wrapper
retained) fails `CNF-34` and no other item, 32 passed and 1 failed, its whole detail that bracket,
the `probe-0` `GRANDCHILD` bracket against the same record and the `probe-1` `PID` bracket against
`005-reviewer-1-fable.env`; the unmutated executable gives 33 passed, 0 failed.

The group half remains a limit at that boundary and is recorded, not redesigned: the `probe-0` /
pick / `GRANDCHILD` read is intermittent in both variants — 18 / 20 in each suite above and
57 / 60 in the Reviewer's unchanged runs — as is `probe-1` / `fable` / `GRANDCHILD` in the table
above. That intermittent silence never turned the item green on the mutant.

*Remaining boundaries investigated 2026-10-03 (`rl-cnf34-remaining-boundaries-4lq`).*
This amends `CNF-34` with the watching Runs it lists and a delay in its ordinary Manager Run;
it left the ordinary Probe sleep candidate above declined, as it stood when this investigation
closed; the candidate landed afterwards, as that paragraph records. The starting Specification was
`1370638210061870b37a0c07ab86a1abb149d6f2`. The reference resolved from
`/home/master/p/rloop-bash/result/bin/rloop` to
`/nix/store/mydjhwg0771w726kcp1gpx71v485kc4s-rloop/bin/rloop`, SHA-256
`4759d2779b719e8513fba386d2879e9290807ab7ec53383e604bde85cfbcaabd`.
The neighboring repository was clean at `a110ec2a3e9c4eefa67ced14976e24263d83249f`;
the packaged body differs from its `bin/rloop` only by a trailing blank line
(`source-provenance.diff`).
Every executable below is a scratch copy of that packaged executable, retaining its Bash
interpreter and wrapper PATH additions for git, coreutils, diffutils and util-linux, including
`cmp`. Nothing in the Implementation repository or Nix store was edited.

The retained witnesses and scratch mutations are:

- **Pick snapshot (`pick-snapshot.diff`).** Wait for the pick's process and preserve its status,
  but copy its Task File to `task-1.md` before group cleanup; suppress that copy at its former
  location. The remaining decision and output read stay after cleanup, and cleanup completes
  before the Implementer starts. This is ungated and activates in both suite versions. The new
  Manager watcher reads only `manager-0`; a later Manager's child finding the already existing
  snapshot is legitimate evidence outside that tag.
- **Panel Checkpoint (`panel-step.diff`).** Keep each Reviewer's wait and asynchronous group
  sweep, but move the second Checkpoint immediately before the final group-cleanup barrier,
  suppressing its original call. Activation requires the Reviewer-child knob, no Reviewer
  sleep and `--kill-after 1`, conditions met by the ordinary Reviewer arm in both suites and
  by the new Panel arm. Only `fable` edits the Task File, at `afterPanel`: the first Checkpoint
  has no Interference to reject. Every Reviewer's watcher is checked against that second
  Checkpoint's file, which must contain the Reviewer's edit. No sibling's live PID is treated
  as failure; the later-call check still reads only the judge's record.
- **Judge decision (`judge.diff`).** Wait for the judge's process, preserving its status, then
  execute the decision before group cleanup. On *next Round*, cleanup follows the snapshot;
  on a terminal path it precedes report output and return. Activation is ungated. The new
  two-Round Run has its first judge rewrite the Task File; only `manager-1` watches `task-2.md`,
  and the next Implementer's record must exist with both Manager pids absent. It witnesses the
  decision's next-Round snapshot effect, not the judge's own writing of a Finished File.
- **Pick's own process (`own.diff`).** In `rec-reap-manager` only, defer the pick's wait and
  cleanup until immediately after spawning the Implementer. Poll for the real Task File at
  0.01-second intervals, bounded by 1000 attempts, to avoid advancing on a file the fake has
  not yet written; use status zero for this successful fake until the real wait. Log the
  deferral and subsequent spawn in both suite versions. Standard input remains `/dev/null`.
  The unchanged fake exits too quickly to expose its own PID reliably. The retained
  `RLOOP_FAKE_PICK_EXIT_DELAY=1`, confined to the ordinary Manager arm, sleeps after writing
  the pick's files and output, before its exit. It changes no descendant or stdin behavior.
  The existing own-process assertion then fails beside the child assertion; it is not a
  child-only failure being counted as evidence about the pick's PID.

The early trials also tried moving the pick's whole decision (`pick.diff`) and withholding the
Panel's per-Reviewer sweeps (`panel.diff`). Their targeted repetitions were red, but they move
more work than the retained isolated mutations above, so neither is the basis of the full
comparison. The ordinary pick deferral without the exit delay was tried first, then compared
against the delayed fake in alternating order.

Targeted measurements extracted the relevant arms with their actual helpers and evidence guards.
In the repeated step, own-process and Checkpoint controls every executable Run exited 0;
a red result below is the assertion, not a failed fake. Each new watching arm was green
against the reference in 10/10 repetitions. The isolated pick
snapshot, Panel Checkpoint and judge mutations were red in 10/10 each. Whole-arm mean seconds
were 1.514 / 0.500 for reference / pick mutant, 1.437 / 0.494 for reference / Panel mutant and
2.780 / 1.769 for reference / judge mutant. A watcher exits when it sees the forbidden file,
which explains the shorter failing Runs. The ordinary Manager arm, over 20 alternating
repetitions per suite with the same deferral mutant, gave:

| Read | Unchanged fake | Delayed fake |
|---|---|---|
| Pick's child alive at a later call | 20 / 20 | 20 / 20 |
| `manager-0` own PID alive at a later call | 0 / 20 | 20 / 20 |
| Missing evidence or survivor after return | 0 / 20 | 0 / 20 |

Mean runtime was 2.513 seconds unchanged and 3.506 with the delay. The delayed reference was green
in 5/5 repetitions, mean 3.525 seconds. These observations demonstrate the own-process guard for
an isolated deferred wait with null stdin, alongside descendant evidence; they do not demonstrate
an own-process-only failure, and they did not change the separate ordinary Probe limitation above,
which the probe sleep landed afterwards ended.

With the current wrapper, the existing Implementer Checkpoint arm was green in 5/5 repetitions.
Replacing only `RLOOP_FAKE_INTERFERENCE=1:afterImplementer:editTask` with `-` made it red in 5/5:
`[checkpoint: no rejected-1-task.md, so the Checkpoint had nothing to witness]`.
A separate control first required the rejected file after the normal Run, then removed just that
file before `watched_nothing`; it produced the same sole bracket in 5/5. Whole-arm means were
1.436, 1.429 and 1.437 seconds respectively. Thus the old missing-`cmp` limitation is historical:
the edit now causes rejection, and the missing-file guard is demonstrated. This verifies existing
coverage and adds no suite arm.

The intended new step diagnostics are
`[pick watch: the Manager's child saw task-1.md, so its group outlived the call and ran through the snapshot]`,
`[panel fable watch: the Reviewer's child saw rejected-1-task.md, so its group outlived the call and ran through the second Checkpoint]`
(and the same bracket for `opus`, `astra` and `sol`), and
`[judge watch: the Manager's child saw task-2.md, so its group outlived the call and ran through the snapshot]`.
Every Panel bracket names that Reviewer's own watcher; none is a concurrency finding against a
sibling. The own-process diagnostics contain the recorded PIDs; the full comparison below records
the actual lines and their distinct meanings.

The full-suite comparisons were:

| Suite | Executable | Exit | Passed / failed | Seconds |
|---|---|---|---|---|
| Unchanged | `reference` | 0 | 33 / 0 | 116.61 |
| Candidate | `reference` | 0 | 33 / 0 | 123.02 |
| Unchanged | `pick-snapshot` | 0 | 33 / 0 | 116.92 |
| Candidate | `pick-snapshot` | 1 | 32 / 1 | 122.34 |
| Unchanged | `panel-step` | 0 | 33 / 0 | 118.57 |
| Candidate | `panel-step` | 1 | 32 / 1 | 122.88 |
| Unchanged | `judge` | 0 | 33 / 0 | 117.06 |
| Candidate | `judge` | 1 | 32 / 1 | 122.66 |
| Unchanged | `own` | 1 | 32 / 1 | 117.10 |
| Candidate | `own` | 1 | 32 / 1 | 123.77 |

Every other item's complete ordered verdict was byte-identical across the matrix. These totals
retain the suite's printed qualifications: `CNF-4` was not run with `--self-check`, and `CNF-22`
is live, by hand. Mutation logs prove activation in both versions, including the ordinary
Reviewer arm for `panel-step` and `rec-reap-manager` for `own`; no pre-change pass depended on an
inert condition. The snapshot, Panel and judge defects were green in the unchanged suite and red
only at their new watchers in the amended one. The own-process mutant was already red unchanged:
`[manager: child 1544636 alive when a later call started]`. Amended, its entire detail was
`[manager: child 1694367 alive when a later call started] [manager: manager-0 1694351 alive when a later call started]`.
The first bracket remains descendant evidence; only the added second bracket demonstrates the
existing own-process assertion. No missing evidence, survivor or unrelated bracket appeared.
The records audited for these arms all carry `STDIN=eof`. In the Panel arm each standard-error
trace records exactly one rejection, between the Panel and judge, with none at the first
Checkpoint; the retained rejected file carries the Reviewer's edit.

The reference full pair's observed increase was 6.41 seconds; the targeted means above separate
the new arms and the pick delay. A direct run of the shipped suite with a `TMPDIR` containing a
space, tab and newline also reported 33 passed, 0 failed, exit 0, in 125.25 seconds;
`final-newline/measurement.json` records its command and exact path. This checks the new path
reads under the same qualifications; it does not amend `RUN-23`.

A further candidate, `judge-late-effect.diff`, moves the group cleanup immediately *before* the
snapshot inside the early decision instead of after it. The next-Round predicates are still
evaluated early, but their observable effect is delayed. The new judge arm remains green in
10/10 repetitions, mean 2.779 seconds. That is a measured residual, not exhaustive decision
coverage: a snapshot watcher cannot see pure computation, and terminal decisions are not witnessed
by this arm. Detecting an early internal read whose effects wait would need a timed change to
decision inputs or an Implementation hook; neither is established by these experiments. The
next-Round effect is retained without adding such machinery. Polling likewise establishes the
measured reorderings, which leave a grace interval for observation, not detection of every
arbitrarily brief inversion. The other output-read limitations already recorded above remain.

Evidence lives outside the Run Directory in
`/tmp/rloop-cnf34-boundaries-20261003-lw2y_vro`. `provenance.json` identifies the reference;
`*.diff` records the mutations; the executable copies preserve their wrappers. `unchanged/`
and `candidate/` hold suite copies whose only harness change replaces the cleanup trap with a
record of the retained work path. `results/<label>/` contains the command, exit and elapsed time
in `measurement.json`, complete stdout/stderr, complete ordered `verdicts`, and `work.path`
pointing to the retained fake records, readiness and observation files and mutation activation logs.
The original work paths are also recorded in `original-work.path`; the evidence directory keeps
a copy of each work tree so the records are available together.
`analysis.json` and `reads.tsv` summarize the individual reads; `manifest.json` hashes the inputs.
The `trial-*` Runs are preliminary; `rep-*` and `refined-*` are the repetitions above. No trial was
silently counted as a repeat. `repeat.py`, `repeat-refined.py` and `full.py` record invocation order.
From that directory, use a fresh result label for each rerun:

```sh
python3 measure.py unchanged reference rerun-u-ref
python3 measure.py candidate reference rerun-c-ref
python3 measure.py unchanged pick-snapshot rerun-u-pick
python3 measure.py candidate pick-snapshot rerun-c-pick
python3 measure.py candidate panel-step rerun-c-panel
python3 measure.py candidate judge rerun-c-judge
python3 measure.py candidate own rerun-c-own
python3 measure.py candidate own rerun-own-arm own
python3 measure.py no-interference reference rerun-without-edit checkpoint
python3 measure.py missing-rejected reference rerun-missing-file checkpoint
```

Omitting the final arm name runs the full suite; `pick`, `panel`, `judge`, `own` and `checkpoint`
select extracted arms. All invocations run in the foreground with null stdin. To reconstruct
without the scratch files, start from the Specification revision and packaged hash above, apply
this amendment for the candidate, and use the mutation recipes above; the controls differ only
by removing the Interference setting or deleting the asserted rejected file before its read.

## F18 — Newline-containing scratch paths (deferred 2026-09-27; resolved 2026-10-03)

The original defect was in line-delimited path reads. At `3744925`, selecting an environment
record with `ls` into `head -1` truncated its path at the newline. The surviving prefix was
non-empty, so the missing-record guard did not fire: the downstream reads reported unwritten
records instead. Under `TMPDIR=$'/tmp/rv-nl\ndir'`, one such detail was
`[probe-0: rv-nl recorded no PID]`. Counting `ls` output with `wc -l` counted one file as two.
That measurement ended at `14 passed, 18 failed`, versus `19 passed, 13 failed` under normal,
space and tab paths. Its newly red items were `CNF-21`, `CNF-24`, `CNF-27`, `CNF-28`, `CNF-29`.
The deferral avoided risking a red item turning green, or a green item turning red, for a scratch
path shape no user was known to need. The conversion was left for demonstration in its own bead, `rl-suite-newline-paths-deferred-mzc`; two advisers agreed in that Consultation.
`3744925`'s commit message described the symptom incorrectly as a missing-record diagnostic;
the non-empty truncated prefix explains why that diagnostic was never printed.

The picked conversion amends `CNF-1`: the suite `MUST expand every path it reads without splitting
it on whitespace`.

`RUN-23` still says `A newline is out of scope`; demonstrating the suite with
one executable that handles newlines does not extend that obligation to other Implementations.
The suite now collects quoted globs into arrays, filters unmatched patterns, counts files, and
selects whole paths in glob order. `spawn_count` (`conformance/run:46`) uses that count;
`record_of` (`conformance/run:612-618`) retains its missing-record guard. Environment checks also
reject both absent and duplicate records. Sequence directory selection uses the same arrays;
the fresh-directory comparison keeps full paths as NUL-separated records. PID and timestamp
reads, fixed-filename listings and existence-only checks are not full-path selections.

Before editing, the suite at `dff4bafabfea61d308a385a0268582f853f650ef` measured `33 passed, 0 failed`
under a normal path (exit 0) and `24 passed, 9 failed` under a newline path (exit 1). Its failed
items, in suite order, were `CNF-5`, `CNF-17`, `CNF-34`, `CNF-20`, `CNF-21`, `CNF-24`, `CNF-27`,
`CNF-28`, `CNF-29`. This reproduces the historical targets against today's executable; the old
failing baseline is not the current acceptance total.

The changed suite measured `33 passed, 0 failed`, exit 0, under each of normal, space, tab and
newline paths. All ordered identifier/verdict pairs matched the unchanged normal-path run,
including the historically affected items listed above. The newline run no longer produced the
truncated-record diagnostics in `CNF-34`, or the doubled counts in usage, Sequence and Probe
checks. One example from the unchanged newline stdout was:

```text
[probe-0: before-newline recorded no PID]
```

No assertion was relaxed to obtain those totals. These were default invocations, without
`--self-check`; the suite's live item and optional self-check retain their printed qualifications.

The read-only executable for every comparison was
`/nix/store/mydjhwg0771w726kcp1gpx71v485kc4s-rloop/bin/rloop`, resolved from
`/home/master/p/rloop-bash/result/bin/rloop`, SHA-256
`4759d2779b719e8513fba386d2879e9290807ab7ec53383e604bde85cfbcaabd`.
The sibling checkout was clean at `a110ec2a3e9c4eefa67ced14976e24263d83249f`, with Specification
pin `a34df16df464d7f2fe813debe0f9c4067457ae16`. Its `bin/rloop` matches the executable after removing
the six Nix wrapper lines and one appended newline; the retained derivation is
`/nix/store/d08zk6x3dlb0p0gd5wgvgmv1w8z41p90-rloop.drv`. The changed suite's SHA-256 is
`47fc43712168d5a0f26f9b09ef23cea90005f0723b474c94be7c2f29fbf8456c`.
The host used Bash 5.3.15 and `LC_ALL=C.UTF-8`.

Evidence remains under `/tmp/rloop-newline-20261003-3550034-evidence` (call it `E` below).
Each label has `.stdout`, `.stderr`, `.json` (argv, actual TMPDIR, executable hash, direct status,
elapsed time), and `.verdicts` (ordered identifier/verdict pairs). `comparison.json` records their
comparison. Actual scratch paths, expressed with Bash escaping, were:

| Label | TMPDIR below E | Exit | Passed / failed |
|---|---|---|---|
| before-normal | `before-normal-tmp` | 0 | 33 / 0 |
| before-newline | `$'before-newline\ndir'` | 1 | 24 / 9 |
| after-normal | `after-normal-tmp` | 0 | 33 / 0 |
| after-space | `after-space space dir` | 0 | 33 / 0 |
| after-tab | `$'after-tab\ttab dir'` | 0 | 33 / 0 |
| after-newline | `$'after-newline\ndir'` | 0 | 33 / 0 |

To reconstruct the comparisons after those scratch files disappear, create a fresh evidence
directory, extract the unchanged Specification with
`git archive dff4bafabfea61d308a385a0268582f853f650ef -o "$E/before.tar"`, and unpack it into
`$E/before`. Set `exe` to the store executable above and verify it with `sha256sum "$exe"`.
For each table row set `label` and the actual `scratch` path (use `$'\n'` or `$'\t'`, never a
command substitution that strips a trailing newline). Use `$E/before/conformance/run` for the
before rows and the changed `conformance/run` for the after rows:

```bash
mkdir -p "$scratch"
printf '%q\n' "$scratch" > "$E/$label.path"
status=0
TMPDIR="$scratch" bash "$suite" "$exe" </dev/null \
  > "$E/$label.stdout" 2> "$E/$label.stderr" || status=$?
printf '%s\n' "$status" > "$E/$label.exit"
awk '/^  (PASS|FAIL)  CNF-/ { print $1, $2 }' "$E/$label.stdout" > "$E/$label.verdicts"
```

Compare each after `.verdicts` file to `before-normal.verdicts` with `cmp`, and compare the direct
statuses. Record sequence numbers and the incidental order of diagnostic brackets are not verdicts.
The retained `measure.py` performs those invocations in the foreground; `before.tar`,
`after-conformance/`, `provenance.json`, `derivation.json` and `executable-source.diff` identify the
inputs independently of either checkout's later state.

Focused disposable controls extracted the actual `matching_paths`, `path_count`, `spawn_count`,
`record_of`, `seq_of`, `present`, `check_env` and `check_probe_env` definitions into `functions.sh`
and sourced them under `set -u`. Their parent directories contain a literal newline. With no
matches, the array, loop and count are empty/zero; `record_of` clears a stale selection and sets
`ok=0` with its missing-record detail, `seq_of` returns -1 and `present` rejects it, and both
environment readers set `ok=0`. With `010-probe-0.argv` alone the count is 1; after adding
`002-probe-0.argv` it is 2 and the selected prefix is 002. The corresponding environment paths
compare byte for byte, one valid environment passes, and duplicate Manager environments fail.
Directories named `010/` and `002/` likewise count as two and select `002/` before `010/`,
with a missing second directory yielding an empty selection. `controls.py` and `checks.sh` retain
the recipe and each control's stdout, stderr and direct status.

The clean controls exited 0. Restoring the old `ls`/`wc -l` count exited 1 at `one-count`
(expected 1, got 2); restoring `record_of`'s `ls`/`head -1` exited 1 at `whole-path` (the prefix
alone survived). Removing the unmatched-pattern filter exited 1 at `empty-array` (expected 0,
got 1); removing the missing-record guard exited 1 at `missing-record-ok` (expected 0, got 1).
`site-controls.py` also extracts the actual judge-timeout, judge-snapshot, Probe argv, judge argv,
Sequence count and refusal count selections with their guards: absent evidence sets `ok=0` at
each site, and replacing each selection/guard block with a no-op makes its control exit 1.
These controls check that missing evidence stays red, which the full green runs alone cannot show.

The workflow's line-citation control now uses the current `spawn_count` anchor above; its
impossible-range and unanchored stages still target lines 99999 and 31. Exercised from the actual
workflow block in a disposable tracked-file copy, it exited 0, with gate statuses 0 / 1 / 0:
anchored clean, `BLOCKING LINE CITATION` for the impossible range, `ADVISORY LINE CITATION` for
the unanchored line. `workflow-control.py`, `workflow-control.sh`, `workflow.stdout`,
`workflow.stderr` and `workflow.statuses` retain that execution. The workflow inspection found
no other affected message or source-literal controls.

## F19 — A Reviewer's cleanup by pattern outside the repository (open 2026-10-02)

Run `20261002T032914.259585815Z-773560`, the `opus` Reviewer: it made scratch copies with
`mktemp -d` to test a `gates.yml` step by hand, then cleaned up with
`rm -rf /tmp/rv-B /tmp/rv-C /tmp/tmp.*`. The glob matches every `mktemp -d` directory on the
machine, and `/tmp` ended about 0.7G below where it started: at least one directory that was not
the Reviewer's went with its own. The prompts said nothing about the filesystem outside the
repository and the Run Directory, which is where scratch copies go.

Amended `PRM-3` and `PRM-4` with one identical sentence before the closing one, and regenerated
`PRM-3.txt` and `PRM-4.txt` by the fixtures tool (rl-agent-cleanup-own-paths-only-aofo). `PRM-3`:
`Outside the repository, delete only what you created, naming each path exactly and never by a
pattern that could match something you did not create.`

A per-agent `TMPDIR` was considered and not chosen: it changes how every agent process is started,
adds a directory rloop must own and reap, and needs its own Conformance coverage. Revisit it only
if a later Run shows the sentence being ignored.

*What does not follow.* Nothing yet shows the sentence working as prompt text; `00-overview.md`
says the prompts are `checked for equality, never for quality`. **Open** until a Run on an
Implementation carrying the amended prompts shows an Implementer or a Reviewer removing its own
scratch paths by name.


## F20 — A force-tracked `.rloop/.gitignore` can stop the next Run (open 2026-10-02)

A repository can force-track `.rloop/.gitignore` with `git add -f` while its bytes differ from
exactly `*` and a newline. During its first Run using the default Run Directory, `DIR-2`'s
`rewriting a file whose bytes differ` changes that tracked file. Ignore rules do not hide tracked
files, so `git status --porcelain` reports the change.

If the rewrite remains uncommitted when the next Run of a Sequence would start, `SEQ-4`'s
`when it prints anything, exit 2 without starting the Run` stops the Sequence before that Run.
This is the consequence of leaving the change dirty, not a claim that the Manager must leave it
dirty. `DIR-2`'s `no tracked file changes` and `SEQ-4`'s statement that `.rloop/` `is ignored`
and `and so never counts` do not hold for this tracked-file case.

Committing the rewritten file resolves this case permanently: subsequent Runs already find the
required bytes. The owner chose to document this boundary on 2026-10-02, changing no requirement
for it.

## F21 — The suite's verdicts moved with `TMPDIR`'s whitespace (resolved 2026-10-04)

Bead `rl-suite-verdict-count-tmpdir-mc5`. Every repository, record directory, Run Directory, the
fakes directory and the private directory of `CNF-2` live under the suite's scratch root, which
`mktemp` named `rloop-conformance.XXXXXX` under `TMPDIR`. Only the dedicated whitespace arms of
`CNF-8`, `CNF-9`, `CNF-11` and `CNF-12` used a path the suite itself gave whitespace, so every
other arm's path held whitespace only when the caller's `TMPDIR` did, which `CNF-9` already calls
a defect: `an item that sees whitespace only when the caller exports it gives a verdict that moves
with` `TMPDIR`. Resolved by giving the scratch root's own name a space and a tab, in
`conformance/run` and in `conformance/test-panel-trace`; `CNF-1`, `CNF-2` and `CNF-8` say so. No
arm was converted and no dedicated whitespace arm was removed: those arms are still the ones that
put whitespace in the repository's and the Run Directory's own names. Four advisers were consulted
on the shape and all chose this one over converting each arm.

A newline in `TMPDIR` can still move an arbitrary Implementation's verdicts. `RUN-23` says
`A newline is out of scope`, so an executable that mishandles one is not held to anything by it,
and the suite adds no newline to the root's name.

Measured on 2026-10-04 with the suite before the change at `6beea3d` and after it
(`conformance/run` SHA-256 `8b579e60e75d75fc6ef63ac942417d8e5a718c60a9c33d57f079fcc44725b2fe`),
Bash 5.3.15. The reference executable is
`/nix/store/sib4qscsjgyzanwrq512rr1j3c2wpgl0-rloop/bin/rloop`, SHA-256
`d5c3284d443d7620c2708b009cc3b489decdfdb6ba55991bd7d1c06759d6989e`, built from rloop-bash
`297238b4610b171f978bf403b8c24ff3c3516c64`, whose Specification pin is `5246aed`. The mutant is a
copy of that file, SHA-256 `4fe46371a2c716ad45d69294104a3266585ac6e23d46623b057877a5e8393ed2`, with
its line 293 (`bin/rloop` line 287 behind the six wrapper lines) changed from
`TASK_FILE) out+="$run_dir/task.md" ;;` to `TASK_FILE) out+="$(printf "%s" $run_dir/task.md)" ;;`,
so it word-splits the Task File's path into its prompts. `TMPDIR` shapes are directories below one
scratch directory `S`, itself free of whitespace.

| Label | `TMPDIR` | Exit | Passed / failed | Red items |
|---|---|---|---|---|
| ref-before-plain | `$S/t-plain` | 0 | 33 / 0 | |
| ref-before-space | `$S/t sp` | 0 | 33 / 0 | |
| ref-before-tab | `$S/t`, a tab, `tab` | 0 | 33 / 0 | |
| mut-before-plain | `$S/t-plain` | 1 | 31 / 2 | `CNF-11`, `CNF-12` |
| mut-before-space | `$S/t sp` | 1 | 30 / 3 | `CNF-11`, `CNF-12`, `CNF-32` |
| mut-before-tab | `$S/t`, a tab, `tab` | 1 | 30 / 3 | `CNF-11`, `CNF-12`, `CNF-32` |
| ref-after-plain | `$S/t-plain` | 0 | 33 / 0 | |
| ref-after-space | `$S/t sp` | 0 | 33 / 0 | |
| ref-after-tab | `$S/t`, a tab, `tab` | 0 | 33 / 0 | |
| ref-after-newline | `$S/t`, a newline, `nl` | 0 | 33 / 0 | |
| mut-after-plain | `$S/t-plain` | 1 | 30 / 3 | `CNF-11`, `CNF-12`, `CNF-32` |
| mut-after-space | `$S/t sp` | 1 | 30 / 3 | `CNF-11`, `CNF-12`, `CNF-32` |
| mut-after-tab | `$S/t`, a tab, `tab` | 1 | 30 / 3 | `CNF-11`, `CNF-12`, `CNF-32` |

Before, the mutant under the plain `TMPDIR` was red only in the whitespace Run's arms of `CNF-11`
and `CNF-12`; under a space or a tab every arm of both went red and `CNF-32` joined. After, the
ordered identifier/verdict pairs are byte-identical across the three shapes for the mutant, and
equal mutant-before's under the space `TMPDIR`; for the reference they are byte-identical across
the four shapes and equal reference-before's. The pin lag reddened nothing on either side.
`conformance/test-panel-trace`, with no argument and with the reference, exited 0 before and after
under the plain and the space `TMPDIR`, with the same count of `PASS` lines.

To reconstruct, for each row set `label`, `exe` and `scratch` (use `$'\t'` or `$'\n'`, never a
command substitution), verify `exe` with `sha256sum`, and run from the Specification checkout at
the commit before this finding for the before rows and at it for the after rows:

```bash
mkdir -p "$scratch"
status=0; TMPDIR="$scratch" bash conformance/run "$exe" </dev/null >"$E/$label.stdout" 2>"$E/$label.stderr" || status=$?
awk '/^  (PASS|FAIL)  CNF-/ { print $1, $2 }' "$E/$label.stdout" > "$E/$label.verdicts"
```

Compare `.verdicts` files with `cmp` and the statuses directly.
