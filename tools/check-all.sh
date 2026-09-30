#!/usr/bin/env bash
# Run every gate that guards this specification set.
#
# Each gate runs to completion and its exit status is captured directly -- never
# through a pipe, which would report the status of the last command in the
# pipeline rather than the gate's own.
#
# Exit status 0 = every gate passed; advisory findings may still be reported.

set -uo pipefail

cd "$(dirname "$0")/.." || exit 2

declare -a NAMES=()
declare -a CODES=()
overall=0

run() {
  local name="$1"; shift
  echo
  echo "=============================================================="
  echo "  $name"
  echo "=============================================================="
  "$@"
  local rc=$?
  NAMES+=("$name")
  CODES+=("$rc")
  [ "$rc" -ne 0 ] && overall=1
  return 0
}

# The formal gate runs first: the regions and scenarios gates read what it writes.
run "formal       (Lean build, axiom policy, @[req] index, regions, scenarios)" bash tools/check_formal.sh
run "identifiers  (identifier integrity; restatements block or advise per F2)" python3 tools/check_ids.py
run "citations    (owner-body quotations; explicit failures block, inferred failures advise)" python3 tools/check_citations.py
run "line-cites   (a <path>:<line> citation's sentence still reads there; an impossible range blocks, an unanchored one advises)" python3 tools/check_line_citations.py
run "coverage     (every requirement cited by a CNF item or excused)" python3 tools/check_coverage.py
run "regions      (a marked region is what its declaration emits)" python3 tools/check_regions.py
run "fixtures     (the suite's fixtures are the documents' blocks)" python3 tools/check_fixtures.py
run "scenarios    (the committed scenarios are what the model enumerates)" python3 tools/check_scenarios.py
run "panel-trace  (the suite's comparator on hand-written traces, the fake past a script's last Round and probe shape, restrict_path's skip, its refusals and its relative-entry normalisation; the executable checks run in an Implementation's CI)" conformance/test-panel-trace

# The last gate runs this script: tools/test_citation_gates.py's aggregate control copies
# the set and runs check-all.sh in the copy, once for every mutation in the list its subTest
# loop iterates. Each of those runs is passed RLOOP_SPEC_CITATION_CONTROLS_NESTED holding
# aggregate-control: and the control's own process id, and that string, with this run's
# parent id in it, is the one value that skips this step -- announced, and taking no SUMMARY
# row -- so that neither entry point, this script or `python3 tools/test_citation_gates.py`
# run directly, recurses. Both halves are what make the value evidence that the control
# started this run rather than something an environment merely carries: the prefix is written
# nowhere but there, so nothing holds it by accident, and the id makes even that string stale
# for every run but the one child it was written for. A bare process id would not be
# evidence. A Nix build runs its builder as PID 1 in a PID namespace, so under checks.gates
# -- this repository's own entry point -- this script's $PPID is 1, and the legacy value 1,
# which the aggregate control itself wrote from `64252d7` until `a948618` replaced it with
# its own process id, would have been honoured by that build. A value built to match the
# token is forgery, not an accident, and is out of scope. Every other present value takes a
# FAIL row, the empty string included: a gate that a variable silences on presence alone is a
# gate any stray environment turns off, and failing makes every mismatch between the value
# the control writes and the value read here a red aggregate control rather than an unbounded
# recursion. A PASS for a gate that did not run is the false green this step exists to close,
# which is why the skip takes no row.
controls="controls     (the identifier and citation gates' own positive and negative controls, each in a disposable copy of the set)"
# The one value that skips this step, and the prefix every row below opens with: `%%"("*`
# cuts the gate's name at its first parenthesis, so that formatting has one home and renaming
# the gate moves the rows and the backstop's pattern with it. A pattern carrying the name as a
# literal would stop matching the row this step's own run takes, and an ordinary run would
# gain a spurious FAIL.
token="aggregate-control:$PPID"
controls_row="${controls%%"("*}("
# `+` and `-`, never the `:` forms: `${x:-}` reads a set-but-empty variable as unset, and an
# empty value is present -- it is no evidence of anything, and reading it as absence is how a
# writer side that produced one would reach this step again. Only an unset variable runs the
# step; `set -u` (:10) is why the expansion cannot be dropped. `present` answers that one
# question and nothing else: the backstop below reads the token instead, because presence is
# what a stray environment supplies and the token is what it cannot.
present="${RLOOP_SPEC_CITATION_CONTROLS_NESTED+set}"
guard="${RLOOP_SPEC_CITATION_CONTROLS_NESTED-}"
if [ "$guard" = "$token" ]; then
  echo
  echo "=============================================================="
  echo "  SKIPPED  controls (nested run: RLOOP_SPEC_CITATION_CONTROLS_NESTED is the aggregate control's token for this run's parent, PID $PPID)"
  echo "=============================================================="
elif [ -n "$present" ]; then
  NAMES+=("${controls_row}RLOOP_SPEC_CITATION_CONTROLS_NESTED='$guard' is not the aggregate control's token for this run's parent, $PPID: only the nested run it starts may skip this step -- see tools/check-all.sh)")
  CODES+=(1)
  overall=1
else
  run "$controls" python3 tools/test_citation_gates.py
fi

# Announcing the skip is not enough on its own: a run that does not carry the token is not
# the nested run the skip above is for, and a skip it takes anyway leaves every other row
# PASS and no trace of this gate at all. So the absence of the row is itself a failure here
# -- the same false green, seen from the other side, and the one a broken guard produces
# rather than a nested run. Keyed on the token and not on presence, because the only run
# this can catch is one whose guard is already broken, so the branches above cannot be
# relied on to have read the value the way they read it here. Matching any row that opens
# with the gate's name is what holds every case to exactly one row: each branch above adds
# at most one row, and this adds one only where they added none.
if [ "$guard" != "$token" ] && [[ " ${NAMES[*]} " != *" $controls_row"* ]]; then
  NAMES+=("${controls_row}skipped by the nested-run guard in a run that did not carry the aggregate control's token: see tools/check-all.sh)")
  CODES+=(1)
  overall=1
fi

echo
echo "=============================================================="
echo "  SUMMARY"
echo "=============================================================="
for i in "${!NAMES[@]}"; do
  if [ "${CODES[$i]}" -eq 0 ]; then status="PASS"; else status="FAIL"; fi
  printf '  %-4s  %s\n' "$status" "${NAMES[$i]}"
done
echo

if [ "$overall" -eq 0 ]; then
  echo "All gates passed (advisory findings, if any, remain for review)."
else
  echo "One or more gates FAILED."
fi
exit "$overall"
