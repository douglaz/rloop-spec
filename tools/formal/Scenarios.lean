import Rloop
/-! `lake exe scenarios` — prints `Rloop.Scenarios.tsv`, the Conformance Suite's replay file
(`ADR-0002`). With `--controls`, prints instead how many lines each guard's absence would change
and exits 1 if any guard changes none: a guard no scenario depends on is one the suite cannot see
missing. -/

def main (args : List String) : IO UInt32 := do
  if args == ["--controls"] then
    let mut bad := 0
    for (name, n) in Rloop.Scenarios.controls do
      IO.println s!"{name}: {n} scenario(s) would fail without it"
      if n == 0 then bad := bad + 1
    return (if bad == 0 then 0 else 1)
  for line in Rloop.Scenarios.tsv do
    IO.println line
  return 0
