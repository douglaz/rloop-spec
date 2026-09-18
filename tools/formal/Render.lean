import Lean
import Rloop
/-! `lake exe render` — prints `Rloop.Render.regions`, one JSON object per marked region, for
`tools/check_regions.py` (`ADR-0002`). -/

open Lean

def main : IO UInt32 := do
  for r in Rloop.Render.regions do
    IO.println (Json.mkObj [("decl", r.decl), ("kind", r.kind), ("text", r.text)]).compress
  return 0
