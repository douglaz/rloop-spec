#!/usr/bin/env bash
# The formal layer's gate (ADR-0002): build every Lean module, then run `lake exe gate`,
# which refuses any @[req] declaration whose proof depends on an axiom outside
# propext / Classical.choice / Quot.sound -- so `sorry`, a project `axiom` and
# `native_decide` are all red -- and refuses an empty index. Then `lake exe render`
# writes the marked regions; the citations and regions gates read what this script
# writes, so check-all.sh runs it first. Each output is written beside itself and renamed into
# place: a Panel runs several check-all.sh in this tree at once, and a reader in one must never
# see a file another has just truncated.
#
# Also refuses a module under Rloop/ that Rloop.lean does not import:
# a proof file the build never reads is a green check that asserts nothing, with a .lean suffix.
#
# Needs `lake` and `lean` on PATH: run under `nix develop` (flake.nix). A missing
# toolchain is a failure, not a skip.
set -uo pipefail
cd "$(dirname "$0")/formal" || exit 2

if ! command -v lake >/dev/null 2>&1; then
  echo "FAIL: lake not on PATH -- run under 'nix develop' (see flake.nix)"
  exit 1
fi

for f in Rloop/*.lean; do
  m="Rloop.$(basename "$f" .lean)"
  if ! grep -q "^import $m\$" Rloop.lean; then
    echo "FAIL: $f exists but Rloop.lean does not import $m -- the build never reads it"
    exit 1
  fi
done

# emit OUT CMD...: CMD's stdout to OUT via a rename, its line count in $lines, CMD's status.
emit() { "${@:2}" > "$1.$$.tmp"; local rc=$?; lines=$(wc -l < "$1.$$.tmp"); mv -f "$1.$$.tmp" "$1"; return "$rc"; }

lake build || exit 1
emit .lake/index.jsonl lake exe gate
rc=$?
echo "index: $lines tagged declarations -> tools/formal/.lake/index.jsonl"
[ "$rc" -eq 0 ] || exit "$rc"
# The marked regions (check_regions.py reads these; a render that fails is a red gate).
emit .lake/regions.jsonl lake exe render || exit 1
echo "regions: $lines marked regions -> tools/formal/.lake/regions.jsonl"
# The replay file the Conformance Suite runs (ADR-0002); check_scenarios.py holds the committed
# copy to it.
emit .lake/scenarios.tsv lake exe scenarios || exit 1
echo "scenarios: $(( lines - 1 )) scripted runs -> tools/formal/.lake/scenarios.tsv"
# The negative control: every guard's absence changes at least one line.
lake exe scenarios --controls || exit 1
