#!/usr/bin/env python3
"""Positive/negative CLI controls in disposable copies, run by check-all.sh and gates.yml."""

from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from spec_text import INTRODUCING_PHRASES, attributions, quotations, units

ROOT = Path(__file__).resolve().parent.parent
QUOTE = "The Manager MUST be one session for the whole Run"
FALSE_QUOTE = QUOTE.replace("one", "seventeen")
GUARD = "RLOOP_SPEC_CITATION_CONTROLS_NESTED"


class CitationControls(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="rloop-citation-controls-")
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        (self.root / "tools").mkdir()
        (self.root / "docs/adr").mkdir(parents=True)
        for pattern in ("*.md", "docs/adr/*.md", "tools/*.py", "tools/restatement-homes.json"):
            for source in ROOT.glob(pattern):
                shutil.copy2(source, self.root / source.relative_to(ROOT))

    def append(self, text, document="00-overview.md"):
        with (self.root / document).open("a") as f:
            f.write("\n\n" + text + "\n")

    def replace(self, document, old, new):
        path = self.root / document
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1))

    def corpus_line(self, document, needle):
        """The line `needle` is on in this copy of the corpus. A control that pins a
        corpus location derives it here rather than carrying a literal, which prose
        above the line silently stales -- `47c3b48` moved RUN-16's history by 14.
        A second occurrence would silently decide which line the caller pins, so
        uniqueness is asserted rather than left to hold by coincidence."""
        text = (self.root / document).read_text()
        self.assertEqual(text.count(needle), 1, needle)
        return text.count("\n", 0, text.index(needle)) + 1

    def controls_rows(self, output):
        """The SUMMARY rows the controls gate took in a nested check-all.sh run. Counted by
        the callers rather than searched for with `in`: only a count catches one condition
        taking two rows -- which is what `a948618` did to an empty value, by expanding the
        variable separately in the two checks -- and only a count catches one row twice."""
        return re.findall(r"^  (?:PASS|FAIL)  controls .*", output, re.M)

    def nested_guard(self, value, status, row, skipped, others=0):
        """One case of the nested-run guard's table: check-all.sh over this copy of the set
        with the guard variable holding `value`, or filtered out of the environment when that
        is None -- filtered, and not left to os.environ, because a shell, a CI step or a stray
        export that carries the name would make an unset case witness a present-value row.
        `row` is the status of the one row this gate takes, or None for the cases that take
        none, `skipped` whether the run announced the skip, and `others` how many rows other
        than this gate's are FAIL -- none for any case of the guard's own table, one for a
        caller whose control.md mutation fails a gate."""
        env = {k: v for k, v in os.environ.items() if k != GUARD}
        if value is not None:
            env[GUARD] = value
        result = subprocess.run(["bash", "tools/check-all.sh"], cwd=self.root,
                                capture_output=True, text=True, timeout=600, env=env)
        output = result.stdout + result.stderr
        rows = self.controls_rows(output)
        self.assertEqual(len(rows), 0 if row is None else 1, output)
        if row is not None:
            self.assertTrue(rows[0].startswith(f"  {row}  controls "), output)
            # A FAIL row in a run that did not announce a skip is the invalid-value branch's,
            # the one row that names the value it refused; the backstop's row is reached only
            # through a skip and names none. Asserting the value on that row is what makes the
            # naming a witnessed behaviour rather than a claim README.md makes for it.
            if row == "FAIL" and not skipped:
                self.assertIn(f"{GUARD}='{value}'", rows[0], output)
        self.assertEqual(result.returncode, status, output)
        self.assertEqual(len([r for r in re.findall(r"^  FAIL  (.*)$", output, re.M)
                              if not r.startswith("controls")]), others, output)
        # The announced skip is what tells the row a present non-token value takes from the
        # backstop's row: without it, a guard that skipped a stray value would leave the
        # backstop to supply the one FAIL row and every assertion above would still hold.
        if skipped:
            self.assertIn("SKIPPED  controls", output)
        else:
            self.assertNotIn("SKIPPED  controls", output)
        return output

    def gate(self, script, status=0, *reasons):
        result = subprocess.run([sys.executable, str(self.root / "tools" / script)],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, status, result.stdout + result.stderr)
        for reason in reasons:
            self.assertIn(reason, result.stdout)
        if any("CITATION:" in r or "RESTATEMENT:" in r for r in reasons):
            # Tier, location, owner and words must describe the same finding;
            # the restored corpus's advisories cannot satisfy a mutant's check.
            findings = re.findall(r"^(?:BLOCKING|ADVISORY) (?:CITATION|RESTATEMENT):[^\n]*"
                                  r"(?:\n  [^\n]*)*", result.stdout, re.M)
            self.assertTrue(any(all(r in finding for r in reasons) for finding in findings),
                            result.stdout)
        return result.stdout

    def ids(self, status=0, *reasons, tier="BLOCKING"):
        reasons = [r.replace("RESTATEMENT:", f"{tier} RESTATEMENT:") for r in reasons]
        return self.gate("check_ids.py", status, *reasons)

    def summary(self, output):
        """`tools/check_citations.py`'s own counts, as (blocking, advisory), for the delta in
        `citations`. The (0, 0) is the reading of `Quoted attributions verified: clean`, the line
        a run with no findings prints in place of the counted one. No other output reaches it:
        every call is on output whose tally in `citations` has already required it to carry
        exactly the one summary line its printed blocks imply."""
        line = re.search(r"^Quoted attributions: (\d+) blocking, (\d+) advisory\.$", output, re.M)
        return (int(line[1]), int(line[2])) if line else (0, 0)

    def citations(self, status=0, *reasons, tier="BLOCKING", since=None):
        """The citation gate over this copy, with two readings of the run's own output. Neither
        is redundant, and between them they witness what one pinned corpus-wide total did.

        The tally: `tools/check_citations.py` prints one block per finding and then exactly one
        summary line, `Quoted attributions: {blocking} blocking, {len(bad) - blocking}
        advisory.` or `Quoted attributions verified: clean`. Every run here re-derives that line
        from the blocks printed beside it, which is what witnesses the summary's arithmetic --
        and it sees what no reading of those numbers alone can, a run that prints one finding
        twice while counting it once.

        The delta: `since` is a summary read off this copy before the caller's first mutation,
        and the run must exceed it by exactly one finding of `tier` and none of the other. That
        is the half the tally cannot supply, because a spurious second finding tallies
        consistently with its own summary. Read as a difference and never pinned to a literal,
        an advisory that arrives anywhere else in the set raises both readings together and
        reddens only `test_current_definitions_and_quotes`, the one control that is about the
        corpus being clean. One baseline per test method and never inside a `subTest`: a loop
        that rewrites the same copy would otherwise read its baseline off a mutated one."""
        reasons = [r.replace("CITATION:", f"{tier} CITATION:") for r in reasons]
        output = self.gate("check_citations.py", status, *reasons)
        blocks = re.findall(r"^(BLOCKING|ADVISORY) CITATION:", output, re.M)
        self.assertEqual(re.findall(r"^Quoted attributions.*$", output, re.M),
                         [f"Quoted attributions: {blocks.count('BLOCKING')} blocking, "
                          f"{blocks.count('ADVISORY')} advisory." if blocks else
                          "Quoted attributions verified: clean"], output)
        if since is not None:
            self.assertEqual(tuple(now - was for now, was in zip(self.summary(output), since)),
                             (1, 0) if tier == "BLOCKING" else (0, 1), output)
        return output

    def test_current_definitions_and_quotes(self):
        history = self.corpus_line("01-run-lifecycle.md", "pick MUST start")
        self.ids(0, f"RESTATEMENT: 01-run-lifecycle.md:{history}", "pick MUST start",
                 tier="ADVISORY")
        self.citations(0, "Quoted attributions verified: clean")

    def test_copy_quote_and_one_word_mutation_compose(self):
        copy = f"{QUOTE} (`RUN-16`)."
        self.append(copy)
        self.ids(1, "RESTATEMENT: 00-overview.md:", "RUN-16", QUOTE)
        quoted = f"`RUN-16`: `{QUOTE}`."
        self.replace("00-overview.md", copy, quoted)
        self.ids()
        self.citations()
        self.replace("00-overview.md", quoted, f"`RUN-16`: `{FALSE_QUOTE}`.")
        self.ids()  # Same syntactic route; the composed gate must now reject it.
        self.citations(1, "CITATION: 00-overview.md:", "RUN-16 (01-run-lifecycle.md)", FALSE_QUOTE)

    def test_original_run3_defect_inside_a_definition_body(self):
        self.replace("01-run-lifecycle.md",
                     "`SEQ-4` owns the clean-tree check for a Run inside a Sequence.",
                     "a Run inside a Sequence MUST NOT (`SEQ-4`).")
        self.ids(1, "RESTATEMENT: 01-run-lifecycle.md:", "SEQ-4", "MUST NOT")
        self.citations()

    def test_punctuation_copy_quote_and_corruption_compose(self):
        for shape in ("{rule}; see `RUN-16`.",
                      "{rule}. The check is `RUN-16`.",
                      "The check is `RUN-16`. {rule}.",
                      "{rule}. *`RUN-16` is the check.*"):
            with self.subTest(shape=shape):
                path = self.root / "control.md"
                path.write_text(shape.format(rule=QUOTE))
                self.ids(0, "RESTATEMENT: control.md:", "RUN-16", QUOTE, tier="ADVISORY")
                path.write_text(shape.format(rule=f"`{QUOTE}`"))
                self.ids()
                self.citations()
                path.write_text(shape.format(rule=f"`{FALSE_QUOTE}`"))
                self.ids()
                self.citations(0, "CITATION: control.md:",
                               "RUN-16 (01-run-lifecycle.md)", FALSE_QUOTE, tier="ADVISORY")

    def test_sequence_copy_with_sentence_and_italic_pointers(self):
        copy = "A Run inside a Sequence MUST NOT start on a dirty tree"
        for text in (f"{copy}. The check is `SEQ-4`.",
                     f"The check is `SEQ-4`. {copy}.",
                     f"{copy}. *`SEQ-4` is the check.*"):
            with self.subTest(text=text):
                (self.root / "control.md").write_text(text)
                self.ids(0, "RESTATEMENT: control.md:", "SEQ-4", copy, tier="ADVISORY")
                self.citations()

    def test_explicit_owner_survives_later_parenthetical(self):
        for intro in (" says", ":", "'s", "'s wording that"):
            with self.subTest(intro=intro):
                path = self.root / "control.md"
                path.write_text(f"`SEQ-4`{intro} `{QUOTE}` (`RUN-16`).")
                self.ids()
                self.citations(1, "CITATION: control.md:",
                               "SEQ-4 (05-sequence.md)", QUOTE)
        # Verify the second claimed relationship too, rather than just reversing
        # which one shadows the other.
        path.write_text(f"`RUN-16` says `{QUOTE}` (`SEQ-4`).")
        self.citations(1, "CITATION: control.md:", "SEQ-4 (05-sequence.md)", QUOTE)
        path.write_text(f"`RUN-16` says `{QUOTE}` (`RUN-16`).")
        self.ids()
        self.citations()

    def test_short_normative_quote_and_corruption(self):
        self.append("`SEQ-5`: `MUST exit 2`.")
        self.ids()
        self.citations()
        self.replace("00-overview.md", "`SEQ-5`: `MUST exit 2`.",
                     "`SEQ-5`: `MUST exit 7`.")
        self.ids()
        self.citations(1, "CITATION:", "SEQ-5 (05-sequence.md)", "MUST exit 7")

    def test_short_explicit_quote_checks_attached_owners(self):
        path = self.root / "control.md"
        baseline = self.summary(self.citations())
        for intro in (" says", ":", "'s"):
            for owners in ("`SEQ-4`", "`RUN-16`, `SEQ-4`"):
                with self.subTest(intro=intro, owners=owners):
                    path.write_text(f"`RUN-16`{intro} `one session` ({owners}).")
                    self.ids()
                    self.citations(1, "CITATION: control.md:1",
                                   "SEQ-4 (05-sequence.md)", "one session", since=baseline)
            with self.subTest(intro=intro, owners="valid only"):
                path.write_text(f"`RUN-16`{intro} `one session` (`RUN-16`).")
                self.ids()
                self.citations()

    def test_parenthetical_explanatory_reference_is_not_an_owner(self):
        path = self.root / "control.md"
        baseline = self.summary(self.citations())
        path.write_text(f"`{QUOTE}` (`RUN-16`; but see `SEQ-4` for the Sequence rule).")
        self.ids()
        self.citations()
        path.write_text(f"`{QUOTE}` (`SEQ-4`; but see `RUN-16` for the session rule).")
        self.ids()
        self.citations(1, "CITATION: control.md:1", "SEQ-4 (05-sequence.md)", QUOTE,
                       since=baseline)

    def test_explanatory_reference_preserves_preceding_owner_list(self):
        path = self.root / "control.md"
        baseline = self.summary(self.citations())
        for suffix in ("", "; but see `RUN-16` for the session rule"):
            with self.subTest(suffix=suffix):
                path.write_text(f"`{QUOTE}` (`RUN-16`, `SEQ-4`{suffix}).")
                self.ids()
                self.citations(1, "CITATION: control.md:1", "SEQ-4 (05-sequence.md)",
                               QUOTE, since=baseline)
        path.write_text("`MUST exit 2` (`SEQ-5`, `RUN-1`; but see `RUN-16` for sessions).")
        self.ids()
        self.citations()

    def test_speaker_survives_intervening_prose_and_later_pointer(self):
        for gap in (" the rule is ", ", in short, "):
            with self.subTest(gap=gap):
                path = self.root / "control.md"
                path.write_text(f"`SEQ-4` says{gap}`{QUOTE}` (`RUN-16`).")
                self.ids()
                self.citations(0, "CITATION: control.md:1",
                               "SEQ-4 (05-sequence.md)", QUOTE, tier="ADVISORY")
                path.write_text(f"`RUN-16` says{gap}`{QUOTE}` (`RUN-16`).")
                self.ids()
                self.citations()
                path.write_text(f"`RUN-16` says{gap}`{QUOTE}` (`SEQ-4`).")
                self.citations(1, "CITATION: control.md:1",
                               "SEQ-4 (05-sequence.md)", QUOTE)

    def test_every_attached_parenthetical_owner_is_verified(self):
        path = self.root / "control.md"
        for intro in ("", "`RUN-16` says the rule is "):
            with self.subTest(intro=intro):
                path.write_text(f"{intro}`{QUOTE}` (`RUN-16`, `SEQ-4`).")
                self.ids()
                self.citations(1, "CITATION: control.md:1",
                               "SEQ-4 (05-sequence.md)", QUOTE)
        # Both definitions contain this short normative phrase.
        path.write_text("`MUST exit 2` (`SEQ-5`, `RUN-1`).")
        self.ids()
        self.citations()
        path.write_text("`RUN-16` says `MUST exit 2` (`SEQ-5`, `RUN-1`).")
        self.citations(1, "CITATION: control.md:1", "RUN-16", "MUST exit 2")
        path.write_text(f"`{QUOTE}` (`RUN-16`). Also see `SEQ-4`.")
        self.ids()
        self.citations()

    def test_speech_gap_stops_at_punctuation_and_new_introducers(self):
        path = self.root / "control.md"
        for separator in (".", "!", "?", ";"):
            with self.subTest(separator=separator):
                path.write_text(f"`SEQ-4` says something{separator} `{QUOTE}` (`RUN-16`).")
                self.ids()
                self.citations()
        for intro in (" says the rule is", ":", "'s"):
            with self.subTest(intro=intro):
                path.write_text(f"`SEQ-4` says to consult `RUN-16`{intro} `{QUOTE}`.")
                self.ids()
                self.citations()
        path.write_text(f"`RUN-16` says, in short, `{QUOTE}` and `fabricated words`.")
        self.ids()
        self.citations(0, "CITATION: control.md:1", "RUN-16", "fabricated words", tier="ADVISORY")

    def test_modal_with_negation_is_not_a_quoted_rule(self):
        self.append("The Manager `MUST NOT` use seventeen sessions (`RUN-16`).")
        self.ids(1, "RESTATEMENT:", "RUN-16", "seventeen sessions")
        self.citations()

    def test_removed_ovr4_copy_is_not_pre_authorized(self):
        self.replace("00-overview.md",
                     "**OVR-4** `AGT-15` owns the process-lifetime rule and signal handling.",
                     "**OVR-4** rloop MUST NOT exit while an agent process it started "
                     "is still running (`AGT-15`).")
        self.ids(1, "RESTATEMENT: 00-overview.md:", "AGT-15", "OVR-4")
        self.citations()

    def test_removed_run18_copy_is_not_pre_authorized(self):
        self.replace("01-run-lifecycle.md",
                     "**RUN-18** rloop MUST NOT tell an Implementer whether to commit:",
                     "**RUN-18** rloop MUST NOT commit, and MUST NOT tell an Implementer "
                     "whether to commit:")
        self.ids(0, "RESTATEMENT: 01-run-lifecycle.md:", "OVR-3", "MUST NOT commit", tier="ADVISORY")
        self.citations()

    def test_unmatched_backtick_cannot_absorb_later_block(self):
        for separator, first, second in (("\n\n", "", ""),
                                          ("\n", "- ", "- "),
                                          ("\n", "* ", "* "),
                                          ("\n", "+ ", "+ "),
                                          ("\n", "1. ", "2. "),
                                          ("\n", "| ", "| "),
                                          ("\n", "**OVR-5** ", "**OVR-6** ")):
            with self.subTest(first=first):
                prefix = first + "`" + separator + second
                line = separator.count("\n") + 1
                path = self.root / "control.md"
                path.write_text(f"{prefix}`RUN-16`: `{QUOTE}`.")
                self.ids()
                self.citations()
                copy = "A Run inside a Sequence MUST NOT start on a dirty tree"
                path.write_text(f"{prefix}{copy} (`SEQ-4`).")
                self.ids(1, f"RESTATEMENT: control.md:{line}", "SEQ-4", copy)
                self.citations()  # No phantom quotation from the stray delimiter.
                path.write_text(f"{prefix}`RUN-16`: `{FALSE_QUOTE}`.")
                self.citations(1, f"CITATION: control.md:{line}", "RUN-16", FALSE_QUOTE)

    def test_unrelated_blocks_cannot_supply_attribution(self):
        # A quote without a citation in its own block cannot borrow the previous
        # block's owner; malformed spans cannot bridge it either.
        for before, after in (("`RUN-16`: words.", f"`{QUOTE}`."),
                              ("`SEQ-4` says the rule is", f"`{QUOTE}` (`RUN-16`)."),
                              ("`RUN-16`: `", f"{QUOTE}.")):
            for separator, first, second in (("\n\n", "", ""),
                                              ("\n", "- ", "- "),
                                              ("\n", "* ", "* "),
                                              ("\n", "+ ", "+ "),
                                              ("\n", "1. ", "2. "),
                                              ("\n", "| ", "| "),
                                              ("\n", "**OVR-5** ", "**OVR-6** ")):
                with self.subTest(separator=separator, first=first, before=before):
                    path = self.root / "control.md"
                    path.write_text(first + before + separator + second + after)
                    owners = [owner for owner, _, _ in
                              attributions(list(units(path.read_text()))[-1])]
                    self.assertEqual(owners, ["RUN-16"] if "(`RUN-16`)" in after else [])
                    self.ids()
                    self.citations()

    def test_unrelated_quote_cannot_cover_rule_in_another_block(self):
        for separator, first, second in (("\n\n", "", ""),
                                          ("\n", "- ", "- "),
                                          ("\n", "* ", "* "),
                                          ("\n", "+ ", "+ "),
                                          ("\n", "**OVR-5** ", "**OVR-6** ")):
            with self.subTest(first=first):
                (self.root / "control.md").write_text(
                    f"{first}`RUN-16`: `{QUOTE}`.{separator}"
                    f"{second}{QUOTE}; see `RUN-16`.")
                self.ids(0, "RESTATEMENT: control.md:", "RUN-16", QUOTE, tier="ADVISORY")
                self.citations()

    def test_newly_reviewed_clause_does_not_exempt_its_paragraph(self):
        self.replace("05-sequence.md", ". `.rloop/` is ignored",
                     ". The Manager MUST use seventeen sessions. `.rloop/` is ignored")
        self.ids(0, "RESTATEMENT: 05-sequence.md:", "MUST use seventeen sessions", tier="ADVISORY")
        self.citations()

    def test_new_definition_line_is_not_an_ownership_exemption(self):
        self.append(f"**OVR-5** {QUOTE} (`RUN-16`).")
        self.ids(1, "RESTATEMENT:", "RUN-16")
        self.citations()

    def test_reviewed_home_cannot_gain_a_new_duty(self):
        self.replace("01-run-lifecycle.md",
                     "A Reviewer that `RUN-21` recorded `unavailable` MUST NOT be called at all.",
                     "A Reviewer that `RUN-21` recorded `unavailable` MUST be called twice.")
        self.ids(0, "RESTATEMENT:", "RUN-21", "MUST be called twice", tier="ADVISORY")
        self.citations()

    def test_bare_identifier_and_unrelated_code_are_not_quotes(self):
        for suffix in ("`RUN-16`", "`RUN-16` with `session`",
                       "`RUN-16` with `an unrelated code span`"):
            with self.subTest(suffix=suffix):
                path = self.root / "control.md"
                path.write_text(f"{QUOTE} according to {suffix}.\n")
                self.ids(0, "RESTATEMENT: control.md:", "RUN-16", tier="ADVISORY")
                self.citations()

    def test_valid_quote_does_not_cover_an_unquoted_rule(self):
        self.append(f"`RUN-16`: `{QUOTE}` and the Manager MUST start again.")
        self.ids(0, "RESTATEMENT:", "MUST start again", tier="ADVISORY")
        self.citations()

    def test_quoted_modal_is_not_a_quoted_rule(self):
        self.append("The Manager `MUST` use seventeen sessions (`RUN-16`).")
        self.ids(1, "RESTATEMENT:", "RUN-16", "seventeen sessions")
        self.citations()

    def test_unrelated_normative_quote_cannot_cover_copy(self):
        self.append(f"`RUN-16`: `{QUOTE}` and a Sequence MUST start dirty (`SEQ-4`).")
        self.ids(1, "RESTATEMENT:", "SEQ-4")
        self.citations()

    def test_wrapping_does_not_hide_copy_or_break_quote(self):
        self.append(f"{QUOTE}\n(`RUN-16`).")
        self.ids(1, "RESTATEMENT:", "RUN-16")
        self.replace("00-overview.md", f"{QUOTE}\n(`RUN-16`).",
                     "`RUN-16`: `The Manager MUST be one\nsession for the whole Run`.")
        self.ids()
        self.citations()

    CLAUSE = "A Reviewer that `RUN-21` recorded `unavailable` MUST NOT be called at all"

    def test_strikethrough_never_changes_a_digest_or_a_quotation(self):
        # F2: tildes are removed wherever they occur, so ~~...~~ keeps the reviewed
        # digest and the quotation, and cannot hide a changed word inside either.
        self.replace("01-run-lifecycle.md", f"{self.CLAUSE}.", f"~~{self.CLAUSE}~~.")
        self.append(f"`RUN-16`: `~~{QUOTE}~~`.")
        self.assertNotIn("MUST NOT be called at all", self.ids())
        self.citations()
        self.replace("01-run-lifecycle.md", f"~~{self.CLAUSE}~~.",
                     f"~~{self.CLAUSE.replace('at all', 'twice')}~~.")
        self.replace("00-overview.md", f"`~~{QUOTE}~~`", f"`~~{FALSE_QUOTE}~~`")
        self.ids(0, "RESTATEMENT: 01-run-lifecycle.md:", "RUN-21", "MUST NOT be called twice",
                 tier="ADVISORY")
        self.citations(1, "CITATION: 00-overview.md:", "RUN-16 (01-run-lifecycle.md)", FALSE_QUOTE)

    def test_underscore_emphasis_is_a_changed_word(self):
        # F2: underscores are kept wherever they occur. One in the owner's body
        # verifies; _..._ around a reviewed clause or a quotation is a new clause.
        self.replace("01-run-lifecycle.md", f"{self.CLAUSE}.", f"_{self.CLAUSE}_.")
        self.append("`RUN-16`: `it is the thread_id of the first`.")
        self.ids(0, "RESTATEMENT: 01-run-lifecycle.md:", "RUN-21",
                 "_A Reviewer that RUN-21 recorded unavailable MUST NOT be called at all_.",
                 tier="ADVISORY")
        self.citations()
        self.replace("00-overview.md", "`it is the thread_id of the first`", f"`_{QUOTE}_`")
        self.citations(1, "CITATION: 00-overview.md:", "RUN-16 (01-run-lifecycle.md)",
                       f"_{QUOTE}_")

    def test_literal_code_characters_follow_the_same_rule(self):
        # F2: an underscore inside an identifier is significant; a tilde in a path
        # or an asterisk in a glob is lost on both sides, so those compare equal.
        self.append("**OVR-5** rloop MUST read `check_ids.py` under `/x` for every `.md` file.")
        path = self.root / "control.md"  # outside OVR-5's own body
        path.write_text("`OVR-5`: `check_ids.py`, `OVR-5`: `~/x`, `OVR-5`: `*.md`.")
        self.ids()
        self.citations()
        path.write_text("`OVR-5`: `checkids.py`, `OVR-5`: `~~under /y~~`, "
                        "`OVR-5`: `**every .txt file**`.")
        self.ids()
        for absent in ("checkids.py", "under /y", "every .txt file"):
            self.citations(1, "CITATION: control.md:", "OVR-5 (00-overview.md)", absent)

    def test_parenthetical_existing_quote_is_verified(self):
        self.replace("01-run-lifecycle.md", f"`RUN-16`: `{QUOTE}`",
                     f"`RUN-16`: `{FALSE_QUOTE}`")
        self.ids()
        self.citations(1, "CITATION: 01-run-lifecycle.md:", "RUN-16", FALSE_QUOTE)

    def test_prm5_wrapped_span_and_owner(self):
        text = (self.root / "03-prompts.md").read_text()
        spans = [q for q in quotations(text) if q.text.startswith("Do not create,")]
        self.assertEqual(len(spans), 1)
        phrase = spans[0].text
        self.assertIn("\n", phrase)
        self.assertIn("this prompt tells you to write.", phrase)
        self.append(f"`PRM-5` says `{phrase}`.")
        self.ids()
        self.citations()
        self.replace("00-overview.md", phrase, phrase.replace("delete", "duplicate"))
        self.citations(1, "CITATION:", "PRM-5", "duplicate")

    def test_explicit_attribution_shapes(self):
        for shape in (f"`RUN-16` says `{QUOTE}`.", f"`RUN-16`'s wording that `{QUOTE}`.",
                      f"`RUN-16`'s `{QUOTE}`.", f"`{QUOTE}` (`RUN-16`).",
                      f"`{QUOTE}` — see `RUN-16`.",
                      f'`RUN-16` reads “{QUOTE}”.', f'`RUN-16` states "{QUOTE}".'):
            with self.subTest(shape=shape):
                path = self.root / "control.md"
                path.write_text(shape)
                self.citations()
                path.write_text(shape.replace(QUOTE, FALSE_QUOTE))
                if "“" in shape or '"' in shape:
                    self.ids(1, "RESTATEMENT: control.md:", "RUN-16", FALSE_QUOTE)
                else:
                    self.ids()
                tier = "ADVISORY" if "— see" in shape else "BLOCKING"
                self.citations(int(tier == "BLOCKING"), "CITATION: control.md:",
                               "RUN-16", FALSE_QUOTE, tier=tier)

    def test_multiple_owners_and_quotes(self):
        self.append(f"`RUN-16`: `{QUOTE}`, and `SEQ-4`: `{FALSE_QUOTE}`.")
        self.ids()
        self.citations(1, "CITATION:", "SEQ-4 (05-sequence.md)", FALSE_QUOTE)

    def test_short_explicit_quote_is_verified(self):
        self.append("`RUN-16` says `seventeen sessions`.")
        self.ids()
        self.citations(1, "CITATION:", "RUN-16", "seventeen sessions")

    def test_each_quote_in_a_direct_speech_list_is_verified(self):
        self.append(f"`RUN-16` says `{QUOTE}` and `this is fabricated wording`.")
        self.ids()
        self.citations(0, "CITATION:", "RUN-16", "this is fabricated wording", tier="ADVISORY")

    def test_direct_speech_owner_is_not_intervening_input_id(self):
        self.append(f"`RUN-16` says `SEQ-4` `{QUOTE}`.")
        self.ids()
        self.citations()
        self.replace("00-overview.md", f"`RUN-16` says `SEQ-4` `{QUOTE}`",
                     f"`SEQ-4` says `RUN-16` `{QUOTE}`")
        self.ids()
        self.citations(0, "CITATION:", "SEQ-4 (05-sequence.md)", tier="ADVISORY")

    def test_other_requirement_or_document_cannot_supply_quote(self):
        self.append(f"`SEQ-4`: `{QUOTE}` (see `01-run-lifecycle.md`).")
        self.append(QUOTE, "docs/adr/0006-rloop-reads-a-vendors-quota-report-and-fails-open.md")
        self.ids()
        self.citations(1, "CITATION:", "SEQ-4 (05-sequence.md)", QUOTE)

    def test_next_heading_ends_owner_body(self):
        self.append(f"## Unowned prose\n\n{FALSE_QUOTE}", "01-run-lifecycle.md")
        self.append(f"`RUN-18`: `{FALSE_QUOTE}`.")
        self.ids()
        self.citations(1, "CITATION:", "RUN-18", FALSE_QUOTE)

    def test_next_definition_ends_owner_body(self):
        self.append(f"`RUN-15`: `{QUOTE}`.")
        self.ids()
        self.citations(1, "CITATION:", "RUN-15", QUOTE)

    def test_historical_and_teaching_words_do_not_excuse_false_quote(self):
        for prefix in ("Previously amended, ", "For example, ", "The original wording: "):
            with self.subTest(prefix=prefix):
                (self.root / "control.md").write_text(f"{prefix}`RUN-16`: `{FALSE_QUOTE}`.")
                self.ids()
                self.citations(1, "CITATION: control.md:", "RUN-16", FALSE_QUOTE)

    def test_adr_is_checked(self):
        self.append(f"`RUN-16`: `{FALSE_QUOTE}`.", "docs/adr/control.md")
        self.ids()
        self.citations(1, "CITATION: docs/adr/control.md:", "RUN-16", FALSE_QUOTE)

    def test_no_ellipsis_splicing_or_word_substrings(self):
        for phrase in ("The Manager MUST … for the whole Run", QUOTE.replace("Run", "Ru")):
            with self.subTest(phrase=phrase):
                (self.root / "control.md").write_text(f"`RUN-16`: `{phrase}`.")
                self.ids()
                self.citations(1, "CITATION: control.md:", "RUN-16", phrase)

    def test_existing_identifier_checks_remain_active(self):
        self.append("**RUN-9999** A citation to `DIR-9999` and `ADR-9999`.\n\n**RUN-1** Duplicate.")
        self.ids(1, "DUPES: [('RUN-1'", "DANGLING: ['DIR-9999']",
                 "OUTLIER IDS: {'RUN': [9999]}", "BAD ADR REFS: ['9999']")
        self.citations()
        self.replace("00-overview.md", "**RUN-9999**", "**OVR-6**")
        self.ids(1, "NUMBER GAPS: {'OVR': [5]}")
        self.citations()

    def test_all_blocking_forms_pair_true_and_false_attributions(self):
        shapes = ["`RUN-16`: `{quote}`.", "`RUN-16`'s `{quote}`.",
                  "`RUN-16`’s `{quote}`.", "`{quote}` (`RUN-16`)."]
        for intro in ("says", "said", "states", "stated", "reads", "read",
                      "gives the term meaning as"):
            shapes.append("`RUN-16` " + intro + "\n `{quote}`.")
        for shape in shapes:
            with self.subTest(shape=shape):
                path = self.root / "control.md"
                path.write_text(shape.format(quote=QUOTE))
                self.ids()
                self.citations()
                path.write_text(shape.format(quote=FALSE_QUOTE))
                self.ids()
                self.citations(1, "CITATION: control.md:", "RUN-16", FALSE_QUOTE)

    def test_unquoted_explicit_restatements_and_quoted_repairs(self):
        for shape in ("`RUN-16`: {quote}.", "`RUN-16`'s {quote}.",
                      "{quote} (`RUN-16`)."):
            with self.subTest(shape=shape):
                path = self.root / "control.md"
                path.write_text(shape.format(quote=QUOTE))
                self.ids(1, "RESTATEMENT: control.md:", "RUN-16", QUOTE)
                self.citations()
                path.write_text(shape.format(quote=f"`{QUOTE}`"))
                self.ids()
                self.citations()

    def test_empty_phrase_list_keeps_intervening_prose_advisory(self):
        self.assertEqual(INTRODUCING_PHRASES, ())
        for intro in ("says that", "states the rule is", "reads, in short,",
                      "says — in short —", "says `SEQ-5`", "says:",
                      "gives this meaning as the rule"):
            with self.subTest(intro=intro):
                path = self.root / "control.md"
                path.write_text(f"`RUN-16` {intro} `{QUOTE}` (`RUN-16`).")
                self.ids()
                self.citations()
                path.write_text(f"`SEQ-4` {intro} `{QUOTE}` (`RUN-16`).")
                self.ids()
                self.citations(0, "CITATION: control.md:", "SEQ-4", QUOTE, tier="ADVISORY")

    def test_denial_and_claim_have_the_same_advisory_tier(self):
        for speech, quote in (("says the rule is", QUOTE), ("says nothing about", "one session")):
            with self.subTest(speech=speech):
                path = self.root / "control.md"
                path.write_text(f"`SEQ-4` {speech} `{quote}` (`RUN-16`).")
                self.ids()
                self.citations(0, "CITATION: control.md:", "SEQ-4", quote, tier="ADVISORY")
                path.write_text(f"`RUN-16` {speech} `{quote}` (`RUN-16`).")
                self.ids()
                self.citations()

    def test_parenthetical_prose_prefix_is_advisory(self):
        for prefix in ("{owner} for the session rule", "{owner}, with `RUN-16` as context"):
            with self.subTest(prefix=prefix):
                path = self.root / "control.md"
                path.write_text(f"`{QUOTE}` ({prefix.format(owner='`RUN-16`')}).")
                self.ids()
                self.citations()
                path.write_text(f"`{QUOTE}` ({prefix.format(owner='`SEQ-4`')}).")
                self.ids()
                self.citations(0, "CITATION: control.md:", "SEQ-4", QUOTE, tier="ADVISORY")
                path.write_text(f"{QUOTE} ({prefix.format(owner='`SEQ-4`')}).")
                self.ids(0, "RESTATEMENT: control.md:", "SEQ-4", QUOTE, tier="ADVISORY")
                self.citations()

    def test_explanatory_marker_whitespace_and_case(self):
        for marker in ("; but see", ";but   see", ";\n but\tsee"):
            with self.subTest(marker=marker):
                path = self.root / "control.md"
                path.write_text(f"`{QUOTE}` (`RUN-16`{marker} `SEQ-4` for another rule).")
                self.ids()
                self.citations()
                path.write_text(f"`{QUOTE}` (`SEQ-4`{marker} `RUN-16` for the session rule).")
                self.ids()
                self.citations(1, "CITATION: control.md:", "SEQ-4", QUOTE)
        path.write_text(f"`{QUOTE}` (`SEQ-4`; But see `RUN-16` for the session rule).")
        self.ids()
        self.citations(0, "CITATION: control.md:", "SEQ-4", QUOTE, tier="ADVISORY")

    def test_nearest_citation_fallback_declined_parenthetical(self):
        # '(see ID)' is declined by parenthetical recognition; the normative
        # backtick quotation still binds to the nearest citation in the unit.
        path = self.root / "control.md"
        path.write_text(f"`{QUOTE}` (see `RUN-16`).")
        self.ids()
        self.citations()
        path.write_text(f"`{FALSE_QUOTE}` (see `RUN-16`).")
        self.ids()
        self.citations(0, "CITATION: control.md:", "RUN-16", FALSE_QUOTE, tier="ADVISORY")
        # Double quotes do not use the normative backtick fallback. With no
        # attributed owner they leave the modal uncovered in check_ids.py.
        path.write_text(f'"{FALSE_QUOTE}" (see `RUN-16`).')
        self.ids(0, "RESTATEMENT: control.md:", "RUN-16", FALSE_QUOTE, tier="ADVISORY")
        self.assertNotIn("CITATION: control.md:", self.citations())
        path.write_text(f'"{QUOTE}" (see `RUN-16`).')
        self.ids(0, "RESTATEMENT: control.md:", "RUN-16", QUOTE, tier="ADVISORY")
        self.assertNotIn("CITATION: control.md:", self.citations())

    def test_continued_quotes_do_not_inherit_blocking_tier(self):
        for join in (" ", ", ", " and ", " or ", " also "):
            with self.subTest(join=join):
                path = self.root / "control.md"
                path.write_text(f"`RUN-16` says `{QUOTE}`{join}`one session`.")
                self.ids()
                self.citations()
                path.write_text(f"`RUN-16` says `{QUOTE}`{join}`fabricated wording`.")
                self.ids()
                self.citations(0, "CITATION: control.md:", "RUN-16", "fabricated wording",
                               tier="ADVISORY")
                path.write_text(f"`RUN-16` says `{QUOTE}`{join}`one session` (`SEQ-4`).")
                self.ids()
                self.citations(1, "CITATION: control.md:", "SEQ-4", "one session")

    def test_advisory_does_not_hide_explicit_owner_or_borrow_its_tier(self):
        path = self.root / "control.md"
        path.write_text(f"`RUN-16` says the rule is `{QUOTE}` (`SEQ-4`).")
        self.ids()
        self.citations(1, "CITATION: control.md:", "SEQ-4", QUOTE)
        path.write_text(f"`SEQ-4` says the rule is `{QUOTE}` (`SEQ-4`).")
        self.ids()
        self.citations(1, "CITATION: control.md:", "SEQ-4", QUOTE)
        path.write_text(f"`RUN-16`: `{FALSE_QUOTE}` and `fabricated wording`.")
        self.ids()
        self.citations(1, "CITATION: control.md:", "RUN-16", FALSE_QUOTE)
        self.citations(1, "CITATION: control.md:", "RUN-16", "fabricated wording", tier="ADVISORY")

    def test_restatement_tiers_do_not_leak_between_clauses(self):
        path = self.root / "control.md"
        path.write_text(f"`RUN-16`: `{QUOTE}` and the Manager MUST start again.")
        self.ids(0, "RESTATEMENT: control.md:", "MUST start again", tier="ADVISORY")
        self.citations()
        path.write_text("`RUN-16`: The Manager MUST use seventeen sessions. "
                        "The Manager SHOULD start again.")
        must_column = path.read_text().index("MUST") + 1
        should_column = path.read_text().index("SHOULD") + 1
        self.ids(1, f"RESTATEMENT: control.md:1:{must_column} ", "MUST use seventeen sessions")
        self.ids(1, f"RESTATEMENT: control.md:1:{should_column} ", "SHOULD start again", tier="ADVISORY")
        self.citations()

    def check_owner_pair(self, shape, words, tier):
        # A separate block and wrapped inputs exercise diagnostic offsets too.
        for owner in ("RUN-16", "SEQ-4"):
            with self.subTest(owner=owner):
                text = "Control\n\n" + shape.format(owner=owner, quote=words)
                (self.root / "control.md").write_text(text)
                self.assertNotIn("RESTATEMENT: control.md:", self.ids())
                if owner == "RUN-16":
                    self.assertNotIn("CITATION: control.md:", self.citations())
                else:
                    line = text.count("\n", 0, text.index(f"`{words}`")) + 1
                    self.citations(int(tier == "BLOCKING"),
                                   f"CITATION: control.md:{line} attributes",
                                   "SEQ-4 (05-sequence.md)", words, tier=tier)

    def check_restatement(self, text, words, owners, tier):
        text = "Control\n\n" + text
        (self.root / "control.md").write_text(text)
        position = text.index("MUST")
        line = text.count("\n", 0, position) + 1
        column = position - text.rfind("\n", 0, position)
        self.ids(int(tier == "BLOCKING"),
                 f"RESTATEMENT: control.md:{line}:{column} cites {owners} outside",
                 words, tier=tier)
        self.assertNotIn("CITATION: control.md:", self.citations())

    def test_quote_adjacency_required_examples(self):
        for apostrophe in ("'", "’"):
            for gap in (" ", "\n\t"):
                shapes = (
                    ("`{owner}`" + apostrophe + "s claim that nothing is said about"
                     + gap + "`{quote}` is wrong.", "one session", "ADVISORY"),
                    ("`{owner}`" + apostrophe + "s rule that, as the Panel found, the Manager may ignore"
                     + gap + "`{quote}` entirely.", "one session", "ADVISORY"),
                    ("`{owner}`: the rule is" + gap + "`{quote}`.", QUOTE, "ADVISORY"),
                    ("`{owner}`" + apostrophe + "s requirement is"
                     + gap + "`{quote}`.", QUOTE, "ADVISORY"),
                    ("`{owner}`:" + gap + "`{quote}`.", QUOTE, "BLOCKING"),
                    ("`{owner}`" + apostrophe + "s" + gap + "`{quote}`.", QUOTE, "BLOCKING"),
                    ("`{owner}`" + apostrophe + "s wording that"
                     + gap + "`{quote}`.", QUOTE, "BLOCKING"),
                    ("`{owner}` says" + gap + "`{quote}`.", QUOTE, "BLOCKING"),
                )
                for shape, words, tier in shapes:
                    with self.subTest(shape=shape):
                        self.check_owner_pair(shape, words, tier)

    def test_all_recognized_introducers_require_adjacent_quotes(self):
        intros = [" " + verb for verb in ("says", "said", "states", "stated", "reads", "read")]
        intros.append(" gives the term meaning as")
        intros.extend(apostrophe + "s " + own + noun + " that"
                      for apostrophe in ("'", "’") for own in ("", "own ")
                      for noun in ("rule", "claim", "wording", "statement", "sentence", "words", "text"))
        for intro in intros:
            for gap, tier in (("\n\t", "BLOCKING"), (", as the Panel found, ", "ADVISORY")):
                with self.subTest(intro=intro, gap=gap):
                    self.check_owner_pair("`{owner}`" + intro + gap + "`{quote}`.", QUOTE, tier)

    def test_restatement_sentence_boundaries_beside_parentheticals(self):
        words = "The Manager MUST start again"
        for punctuation in (".", "!", "?", ";"):
            for whitespace in (" ", "\n\t"):
                boundary = punctuation + whitespace
                shapes = (
                    ("`RUN-16`: sessions are one" + boundary + words + ".", "RUN-16"),
                    ("`RUN-16`: sessions are one" + boundary + "(see `SEQ-4`) " + words + ".",
                     "RUN-16, SEQ-4"),
                    ("`RUN-16`'s wording" + boundary + "(see `SEQ-4`) " + words + ".",
                     "RUN-16, SEQ-4"),
                    ("`RUN-16`’s wording" + boundary + "(see `SEQ-4`) " + words + ".",
                     "RUN-16, SEQ-4"),
                    (words + boundary + "(`SEQ-4`) Sessions are one, see `RUN-16`.",
                     "RUN-16, SEQ-4"),
                )
                for text, owners in shapes:
                    with self.subTest(text=text):
                        self.check_restatement(text, words, owners, "ADVISORY")

    def test_same_clause_restatements_and_parenthetical_punctuation(self):
        shapes = ["`RUN-16`: {quote}.", "`RUN-16`'s {quote}.",
                  "`RUN-16`’s\n {quote}.", "{quote}\n (`RUN-16`)."]
        for punctuation in (".", "!", "?", ";"):
            aside = "(as noted" + punctuation + "\n by the Panel) "
            shapes.extend(("`RUN-16`: " + aside + "{quote}.",
                           "`RUN-16`'s " + aside + "{quote}.",
                           "{quote} " + aside + "(`RUN-16`)."))
        for shape in shapes:
            with self.subTest(shape=shape):
                self.check_restatement(shape.format(quote=QUOTE), QUOTE, "RUN-16", "BLOCKING")
                (self.root / "control.md").write_text(shape.format(quote=f"`{QUOTE}`"))
                self.assertNotIn("RESTATEMENT: control.md:", self.ids())
                self.assertNotIn("CITATION: control.md:", self.citations())

    def test_parenthetical_ownership_prefix_separators(self):
        for separator in (" ", "\n\t", ", ", "; ", " / ", " & "):
            for suffix in ("", ";\n but\tsee `SEQ-4` for context"):
                with self.subTest(separator=separator, suffix=suffix):
                    shape = "`{quote}` (`RUN-16`" + separator + "`{owner}`" + suffix + ")."
                    self.check_owner_pair(shape, QUOTE, "BLOCKING")

    def test_restored_adr0006_full_sentence_is_advisory(self):
        document = "docs/adr/0006-rloop-reads-a-vendors-quota-report-and-fails-open.md"
        sentence = ("So rloop runs the probe `AGT-18` states before each Panel, and `RUN-21` "
                    "reads out of it a line\nbeginning `Current week (<family>): 100% used`.")
        text = (self.root / document).read_text()
        self.assertIn(sentence, text)
        # The corruption below rewrites the first occurrence and the gate is read back for
        # that one finding, so a second occurrence would decide which one is read. corpus_line
        # asserts that uniqueness on the way to the line the citation gate prints for this
        # quotation, which is the line the quotation opens on and not the sentence's first.
        quotation = self.corpus_line(document, "Current week (<family>): 100% used")
        # No restatement is excluded here. check_ids reaches its restatement rule only
        # through an association unit that holds an RFC keyword, and this ADR holds
        # none, so no behaviour of that gate can report one in this file; an exclusion
        # would be true whatever the gate did. Its exit status is still asserted.
        self.ids()
        # 3ca7e1d: the quote verifies, so this line carries no finding. Keyed on the line
        # rather than read off the corpus's summary, which says nothing about this sentence.
        # The exact string the corrupted run below is required to print, the word after the
        # line number included: that is what pairs the absence with a witness that the gate
        # prints it at all, and what keeps this line's digits from matching a finding on a
        # longer line number that begins with them.
        restored = self.citations()
        self.assertNotIn(f"CITATION: {document}:{quotation} attributes", restored)
        # The shape is still recognised, still attributed and still advisory; only the
        # quote came true. Corrupt it in this copy alone -- the corpus keeps RUN-21's words.
        self.replace(document, "Current week (<family>): 100% used",
                     "Current week (<family>): 17% used")
        self.citations(0, f"CITATION: {document}:{quotation} attributes",
                       "RUN-21 (01-run-lifecycle.md)",
                       "Current week (<family>): 17% used", tier="ADVISORY",
                       since=self.summary(restored))

    def test_restored_run16_history_has_no_quote_owner(self):
        document = "01-run-lifecycle.md"
        self.assertIn('this read "the\npick MUST start', (self.root / document).read_text())
        clause = self.corpus_line(document, "pick MUST start")
        self.ids(0, f"RESTATEMENT: {document}:{clause}", "pick MUST start", tier="ADVISORY")
        # The two gates report this one sentence on two different lines: the identifier
        # gate at the modal it leaves uncovered, the citation gate where the quotation
        # opens, and the quotation opens a line earlier. Keying the exclusion on the
        # clause's line excludes a string the citation gate cannot print for this quote.
        quotation = self.corpus_line(document, 'this read "the')
        self.assertNotIn(f"CITATION: {document}:{quotation}", self.citations())

    def test_aggregate_advisories_and_blockers(self):
        # Copy the actual runner, formal model and generated assets, including
        # any existing build cache; never mutate or symlink the source tree.
        for directory in ("tools", "conformance"):
            result = subprocess.run(["cp", "-a", "--reflink=auto", str(ROOT / directory),
                                     str(self.root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        path = self.root / "control.md"
        token = f"aggregate-control:{os.getpid()}"
        # Every step that mutates the copy runs at this level and never inside a subTest: a
        # failed assertion inside one is recorded and the method carries on, which would run a
        # later witness against a script that was not mutated as intended.
        #
        # The controls step is stubbed before the first witness rather than after the loop
        # below, so that no witness in this method can reach it: a run that reaches it runs
        # this file again, which copies the set again, without bound, and subprocess's timeout
        # bounds the direct child only. The token witnesses below skip the step while the
        # token is honoured, so only a double fault -- a guard that stopped honouring it and a
        # lost invalid-value branch -- takes them there, and the stub is what bounds that. The
        # stub costs them nothing: a guard that stopped skipping a valid token still fails
        # them, on the stub's PASS row and the missing announcement, in seconds rather than a
        # full tmpfs.
        #
        # The whole line, never the bare command, which the comment above the step also
        # carries and carries first, where replace() -- first occurrence only -- would stub
        # the comment and leave the step running the file. Unique before it is replaced:
        # replace() asserts presence, not uniqueness.
        script = "tools/check-all.sh"
        text = (self.root / script).read_text()
        step = 'run "$controls" python3 tools/test_citation_gates.py'
        self.assertEqual(text.count(step), 1, step)
        # `true` keeps the step's own PASS row, through the same `run` the real step uses, so
        # the unset case below still witnesses the backstop staying quiet where a row exists;
        # what it stops is the recursion. The half it cannot witness -- that the file really
        # ran -- stays with a top-level check-all.sh run.
        self.replace(script, step, 'run "$controls" true')
        # A stub that cannot be seen is a recursion that cannot be seen.
        for line in (self.root / script).read_text().splitlines():
            if "test_citation_gates.py" in line:
                self.assertTrue(line.lstrip().startswith("#"), line)
        warning = f"`SEQ-4` says the rule is `{QUOTE}` (`RUN-16`)."
        for mutation, status, diagnostic in (
                (warning, 0, "ADVISORY CITATION: control.md:"),
                (warning + f"\n\n`SEQ-4`: `{QUOTE}`.", 1, "BLOCKING CITATION: control.md:"),
                (warning + "\n\nSee `RUN-9999`.", 1, "DANGLING: ['RUN-9999']")):
            with self.subTest(diagnostic=diagnostic):
                path.write_text(mutation)
                self.ids(1 if "RUN-9999" in mutation else 0)
                self.citations(status if "BLOCKING" in diagnostic else 0,
                               "CITATION: control.md:", "SEQ-4", QUOTE, tier="ADVISORY")
                # check-all.sh runs this file as its last gate. The guard is set here, not
                # merely inherited, so that the standalone invocation gates.yml uses -- which
                # has no guard in its environment -- witnesses the skip too. Its value is
                # the token that script honours for the nested run's parent, this process: a
                # prefix written nowhere else, so no environment carries it by accident, and
                # this id, so the token is stale for every other run. check-all.sh fails a
                # run carrying any other value, so a value this side stopped writing is a red
                # control here and never a recursion.
                # Skipped, and taking no row: without those two, two of these three cases
                # witness only the exit status of 1 their own control.md mutation produces,
                # whatever the guard did.
                output = self.nested_guard(token, status, None, skipped=True,
                                           others=1 if status else 0)
                self.assertIn(diagnostic, output)
                self.assertIn("ADVISORY CITATION: control.md:", output)
                self.assertIn("PASS  formal", output)
                self.assertIn("PASS  scenarios", output)
                self.assertIn("All gates passed" if status == 0 else "One or more gates FAILED", output)

        # The rest of the guard's table, in the copy already made rather than a second one.
        # The loop above leaves control.md holding a dangling identifier, which fails a gate
        # in every run below whatever the guard did, which is why it is removed here and not
        # beside the stub above.
        path.unlink()
        # `1` is the value a Nix build's PID-namespaced builder holds, and the value earlier
        # revisions of this mechanism honoured; this process id is the nested run's own
        # parent, the one bare integer a guard keyed on an id alone would still have
        # honoured; `aggregate-control:0` is the prefix with an id behind it that this process
        # cannot hold, a value a guard keyed on the prefix alone would still have skipped. None
        # of them is the token, which is both halves at once.
        #
        # `0`, and not the `1` an earlier revision sampled here, because the token every
        # witness in this method is compared against is built above from this process's own
        # `os.getpid()` -- which nested_guard makes the nested run's `$PPID`, by spawning
        # check-all.sh directly -- and `os.getpid()` is never `0`. So this literal cannot be
        # the token in any process this file runs in, where `aggregate-control:1` is the token
        # whenever the control is itself PID 1 -- a container entrypoint, or a builder that
        # `exec`s this file -- and asserting a row for it reddens an unmutated tree there. The
        # argument has to be about `os.getpid()` and not about `$PPID`: a process whose parent
        # lives outside its PID namespace reads `getppid()` as `0`, so there is no general
        # claim that `$PPID` is never `0` to lean on.
        for value, row in ((None, "PASS"), ("", "FAIL"), ("1", "FAIL"), (str(os.getpid()), "FAIL"),
                           ("aggregate-control:0", "FAIL")):
            with self.subTest(guard=value):
                self.nested_guard(value, 0 if row == "PASS" else 1, row, skipped=False)
        # The guard line forced to always skip: the one mutation that reaches the backstop,
        # and safe by construction, since a script that always skips never runs this file.
        # Asserted unique so that it cannot also match the backstop's own comparison, and
        # applied through replace(), so that a reworded guard line fails this control rather
        # than leaving an unmutated script for the cases below to run.
        always = 'if [ "$guard" = "$token" ]; then'
        self.assertEqual((self.root / script).read_text().count(always), 1, always)
        self.replace(script, always, "if true; then")
        # This process id again, and `aggregate-control:0` again -- its safety is argued above,
        # where it first appears -- because the backstop is the side a guard reading half the
        # token leaves quiet, and each half needs a witness carrying the other: a backstop
        # reading the parent id alone takes no row for this process id, and one reading the
        # prefix alone takes none for a prefixed non-token value such as `aggregate-control:0`.
        for value, row in ((None, "FAIL"), ("", "FAIL"), ("1", "FAIL"),
                           (str(os.getpid()), "FAIL"), ("aggregate-control:0", "FAIL"),
                           (token, None)):
            with self.subTest(guard=value, always_skips=True):
                self.nested_guard(value, 1 if row else 0, row, skipped=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
