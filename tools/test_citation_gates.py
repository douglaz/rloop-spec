#!/usr/bin/env python3
"""Positive/negative CLI controls in disposable copies, also run by gates.yml."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from spec_text import attributions, quotations, units

ROOT = Path(__file__).resolve().parent.parent
QUOTE = "The Manager MUST be one session for the whole Run"
FALSE_QUOTE = QUOTE.replace("one", "seventeen")


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

    def gate(self, script, status=0, *reasons):
        result = subprocess.run([sys.executable, str(self.root / "tools" / script)],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, status, result.stdout + result.stderr)
        for reason in reasons:
            self.assertIn(reason, result.stdout)
        return result.stdout

    def ids(self, status=0, *reasons):
        return self.gate("check_ids.py", status, *reasons)

    def citations(self, status=0, *reasons):
        return self.gate("check_citations.py", status, *reasons)

    def test_current_definitions_and_quotes(self):
        self.ids(0, "RESTATEMENTS: none")
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

    def test_punctuation_copy_quote_and_corruption_compose(self):
        for shape in ("{rule}; see `RUN-16`.",
                      "{rule}. The check is `RUN-16`.",
                      "The check is `RUN-16`. {rule}.",
                      "{rule}. *`RUN-16` is the check.*"):
            with self.subTest(shape=shape):
                path = self.root / "control.md"
                path.write_text(shape.format(rule=QUOTE))
                self.ids(1, "RESTATEMENT: control.md:", "RUN-16", QUOTE)
                path.write_text(shape.format(rule=f"`{QUOTE}`"))
                self.ids()
                self.citations()
                path.write_text(shape.format(rule=f"`{FALSE_QUOTE}`"))
                self.ids()
                self.citations(1, "CITATION: control.md:",
                               "RUN-16 (01-run-lifecycle.md)", FALSE_QUOTE)

    def test_sequence_copy_with_sentence_and_italic_pointers(self):
        copy = "A Run inside a Sequence MUST NOT start on a dirty tree"
        for text in (f"{copy}. The check is `SEQ-4`.",
                     f"The check is `SEQ-4`. {copy}.",
                     f"{copy}. *`SEQ-4` is the check.*"):
            with self.subTest(text=text):
                (self.root / "control.md").write_text(text)
                self.ids(1, "RESTATEMENT: control.md:", "SEQ-4", copy)

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

    def test_speaker_survives_intervening_prose_and_later_pointer(self):
        for gap in (" the rule is ", ", in short, "):
            with self.subTest(gap=gap):
                path = self.root / "control.md"
                path.write_text(f"`SEQ-4` says{gap}`{QUOTE}` (`RUN-16`).")
                self.ids()
                self.citations(1, "CITATION: control.md:1",
                               "SEQ-4 (05-sequence.md)", QUOTE)
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
        self.citations(1, "CITATION: control.md:1", "RUN-16", "fabricated words")

    def test_modal_with_negation_is_not_a_quoted_rule(self):
        self.append("The Manager `MUST NOT` use seventeen sessions (`RUN-16`).")
        self.ids(1, "RESTATEMENT:", "RUN-16", "seventeen sessions")

    def test_removed_ovr4_copy_is_not_pre_authorized(self):
        self.replace("00-overview.md",
                     "**OVR-4** `AGT-15` owns the process-lifetime rule and signal handling.",
                     "**OVR-4** rloop MUST NOT exit while an agent process it started "
                     "is still running (`AGT-15`).")
        self.ids(1, "RESTATEMENT: 00-overview.md:", "AGT-15", "OVR-4")

    def test_removed_run18_copy_is_not_pre_authorized(self):
        self.replace("01-run-lifecycle.md",
                     "**RUN-18** rloop MUST NOT tell an Implementer whether to commit:",
                     "**RUN-18** rloop MUST NOT commit, and MUST NOT tell an Implementer "
                     "whether to commit:")
        self.ids(1, "RESTATEMENT: 01-run-lifecycle.md:", "OVR-3", "MUST NOT commit")

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
                    owners = [owner for owner, _ in
                              attributions(list(units(path.read_text()))[-1])]
                    self.assertEqual(owners, ["RUN-16"] if "(`RUN-16`)" in after else [])
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
                self.ids(1, "RESTATEMENT: control.md:", "RUN-16", QUOTE)

    def test_newly_reviewed_clause_does_not_exempt_its_paragraph(self):
        self.replace("05-sequence.md", ". `.rloop/` is ignored",
                     ". The Manager MUST use seventeen sessions. `.rloop/` is ignored")
        self.ids(1, "RESTATEMENT: 05-sequence.md:", "MUST use seventeen sessions")

    def test_new_definition_line_is_not_an_ownership_exemption(self):
        self.append(f"**OVR-5** {QUOTE} (`RUN-16`).")
        self.ids(1, "RESTATEMENT:", "RUN-16")

    def test_reviewed_home_cannot_gain_a_new_duty(self):
        self.replace("01-run-lifecycle.md",
                     "A Reviewer that `RUN-21` recorded `unavailable` MUST NOT be called at all.",
                     "A Reviewer that `RUN-21` recorded `unavailable` MUST be called twice.")
        self.ids(1, "RESTATEMENT:", "RUN-21", "MUST be called twice")

    def test_bare_identifier_and_unrelated_code_are_not_quotes(self):
        for suffix in ("`RUN-16`", "`RUN-16` with `session`",
                       "`RUN-16` with `an unrelated code span`"):
            with self.subTest(suffix=suffix):
                path = self.root / "control.md"
                path.write_text(f"{QUOTE} according to {suffix}.\n")
                self.ids(1, "RESTATEMENT: control.md:", "RUN-16")

    def test_valid_quote_does_not_cover_an_unquoted_rule(self):
        self.append(f"`RUN-16`: `{QUOTE}` and the Manager MUST start again.")
        self.ids(1, "RESTATEMENT:", "MUST start again")

    def test_quoted_modal_is_not_a_quoted_rule(self):
        self.append("The Manager `MUST` use seventeen sessions (`RUN-16`).")
        self.ids(1, "RESTATEMENT:", "RUN-16", "seventeen sessions")

    def test_unrelated_normative_quote_cannot_cover_copy(self):
        self.append(f"`RUN-16`: `{QUOTE}` and a Sequence MUST start dirty (`SEQ-4`).")
        self.ids(1, "RESTATEMENT:", "SEQ-4")

    def test_wrapping_does_not_hide_copy_or_break_quote(self):
        self.append(f"{QUOTE}\n(`RUN-16`).")
        self.ids(1, "RESTATEMENT:", "RUN-16")
        self.replace("00-overview.md", f"{QUOTE}\n(`RUN-16`).",
                     "`RUN-16`: `The Manager MUST be one\nsession for the whole Run`.")
        self.ids()
        self.citations()

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
                self.citations(1, "CITATION: control.md:", "RUN-16", FALSE_QUOTE)

    def test_multiple_owners_and_quotes(self):
        self.append(f"`RUN-16`: `{QUOTE}`, and `SEQ-4`: `{FALSE_QUOTE}`.")
        self.ids()
        self.citations(1, "CITATION:", "SEQ-4 (05-sequence.md)", FALSE_QUOTE)

    def test_short_explicit_quote_is_verified(self):
        self.append("`RUN-16` says `seventeen sessions`.")
        self.citations(1, "CITATION:", "RUN-16", "seventeen sessions")

    def test_each_quote_in_a_direct_speech_list_is_verified(self):
        self.append(f"`RUN-16` says `{QUOTE}` and `this is fabricated wording`.")
        self.citations(1, "CITATION:", "RUN-16", "this is fabricated wording")

    def test_direct_speech_owner_is_not_intervening_input_id(self):
        self.append(f"`RUN-16` says `SEQ-4` `{QUOTE}`.")
        self.ids()
        self.citations()
        self.replace("00-overview.md", f"`RUN-16` says `SEQ-4` `{QUOTE}`",
                     f"`SEQ-4` says `RUN-16` `{QUOTE}`")
        self.citations(1, "CITATION:", "SEQ-4 (05-sequence.md)")

    def test_other_requirement_or_document_cannot_supply_quote(self):
        self.append(f"`SEQ-4`: `{QUOTE}` (see `01-run-lifecycle.md`).")
        self.append(QUOTE, "docs/adr/0006-rloop-reads-a-vendors-quota-report-and-fails-open.md")
        self.ids()
        self.citations(1, "CITATION:", "SEQ-4 (05-sequence.md)", QUOTE)

    def test_next_heading_ends_owner_body(self):
        self.append(f"## Unowned prose\n\n{FALSE_QUOTE}", "01-run-lifecycle.md")
        self.append(f"`RUN-18`: `{FALSE_QUOTE}`.")
        self.citations(1, "CITATION:", "RUN-18", FALSE_QUOTE)

    def test_next_definition_ends_owner_body(self):
        self.append(f"`RUN-15`: `{QUOTE}`.")
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
                self.citations(1, "CITATION: control.md:", "RUN-16", phrase)

    def test_existing_identifier_checks_remain_active(self):
        self.append("**RUN-9999** A citation to `DIR-9999` and `ADR-9999`.\n\n**RUN-1** Duplicate.")
        self.ids(1, "DUPES: [('RUN-1'", "DANGLING: ['DIR-9999']",
                 "OUTLIER IDS: {'RUN': [9999]}", "BAD ADR REFS: ['9999']")
        self.replace("00-overview.md", "**RUN-9999**", "**OVR-6**")
        self.ids(1, "NUMBER GAPS: {'OVR': [5]}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
