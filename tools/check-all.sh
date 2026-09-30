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
# the set and runs check-all.sh in the copy, three times. That control sets
# RLOOP_SPEC_CITATION_CONTROLS_NESTED in the environment it passes to each of those runs,
# and a run that sees it skips this one step, so neither entry point -- this script, or
# `python3 tools/test_citation_gates.py` run directly -- recurses. The skip is announced
# and takes no SUMMARY row: a PASS for a gate that did not run is the false green this
# step exists to close. Nothing else sets this variable; anything that did would hide the
# step from a top-level run.
controls="controls     (the identifier and citation gates' own positive and negative controls, each in a disposable copy of the set)"
if [ -n "${RLOOP_SPEC_CITATION_CONTROLS_NESTED:-}" ]; then
  echo
  echo "=============================================================="
  echo "  SKIPPED  controls (nested run: RLOOP_SPEC_CITATION_CONTROLS_NESTED is set)"
  echo "=============================================================="
else
  run "$controls" python3 tools/test_citation_gates.py
fi

# Announcing the skip is not enough on its own: a run whose environment carries no guard
# is the top-level one, the skip above is not for it, and a skip it takes anyway leaves a
# summary of nine PASS rows and no trace of the tenth gate. So the absence of the row is
# itself a failure here -- the same false green, seen from the other side, and the one a
# broken guard produces rather than a nested run.
if [ -z "${RLOOP_SPEC_CITATION_CONTROLS_NESTED:-}" ] && [[ " ${NAMES[*]} " != *"$controls"* ]]; then
  NAMES+=("controls     (skipped by the nested-run guard in a run that set nothing: see tools/check-all.sh)")
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
