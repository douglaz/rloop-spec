import Lean
import Rloop
/-! `lake exe gate` — the formal layer's own gate (`ADR-0002`).

For every declaration tagged `@[req "..."]` it collects the axioms the proof depends on and
refuses anything outside `propext`, `Classical.choice`, `Quot.sound`: that refuses `sorryAx`
transitively, any project `axiom`, and the per-declaration axiom `native_decide` mints in
Lean 4.30.0. It also refuses an empty index, because a gate over nothing is `DEF-16`'s green
check. It prints the index — one JSON object per tagged declaration — for the documents' gates.

Exit 0 = every tagged declaration is within policy. -/

open Lean

def allowed : List Name := [``propext, ``Classical.choice, ``Quot.sound]

def axiomsOf (env : Environment) (n : Name) : IO (Array Name) := do
  let ctx : Core.Context := { fileName := "<gate>", fileMap := default }
  let (axioms, _) ← (collectAxioms n : CoreM (Array Name)).toIO ctx { env := env }
  pure axioms

/-- Lean 4.30.0 names the axiom it mints for `native_decide` `<decl>._native.native_decide.ax_…`. -/
def usesNativeDecide (a : Name) : Bool :=
  (a.toString.splitOn "native_decide").length > 1

unsafe def main : IO UInt32 := do
  enableInitializersExecution
  -- `lake exe` sets no LEAN_PATH for the program it runs; run from `tools/formal`.
  initSearchPath (← findSysroot) [".lake/build/lib/lean"]
  withImportModules #[{ module := `Rloop }] {} (trustLevel := 0) fun env => do
    let mut found : Array (Name × String) := #[]
    let mut nativeOutsideExplore : Array Name := #[]
    for (n, _) in env.constants.toList do
      if let some req := Rloop.reqAttr.getParam? env n then
        found := found.push (n, req)
      -- `native_decide` is refused everywhere under `Rloop.*` except `Rloop.Explore`,
      -- tagged or not. Its axiom is minted per declaration with `native_decide` in its name.
      if (`Rloop).isPrefixOf n && !((`Rloop.Explore).isPrefixOf n) then
        let ax ← axiomsOf env n
        if ax.any usesNativeDecide then
          nativeOutsideExplore := nativeOutsideExplore.push n
    for n in nativeOutsideExplore do
      IO.eprintln s!"FAIL  {n} uses native_decide outside Rloop.Explore"
    let tagged := found.qsort (fun a b => a.1.toString < b.1.toString)
    if tagged.isEmpty then
      IO.eprintln "FAIL: no @[req] declarations found; a gate over nothing is not a gate"
      return 1
    let mut failures := 0
    for (n, req) in tagged do
      let axioms ← axiomsOf env n
      let bad := axioms.filter (fun a => !(allowed.contains a))
      let kind := if (env.find? n).any (·.isTheorem) then "theorem" else "def"
      let row := Json.mkObj [
        ("req", req), ("decl", n.toString), ("kind", kind),
        ("axioms", Json.arr (axioms.map (Json.str ·.toString))) ]
      IO.println row.compress
      if !bad.isEmpty then
        failures := failures + 1
        IO.eprintln s!"FAIL  {n} ({req}) depends on {bad.toList}"
    failures := failures + nativeOutsideExplore.size
    IO.eprintln s!"{tagged.size} tagged declarations, {failures} outside the axiom policy"
    return (if failures == 0 then 0 else 1)
