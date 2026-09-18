import Lean
/-! `@[req "RUN-7"]` — the one link between a Lean declaration and the requirement it formalizes
(`ADR-0002`). The gate enumerates tagged declarations to enforce the axiom policy and to emit the
index the documents are checked against. There is no other manifest. -/

open Lean

namespace Rloop

syntax (name := req) "req " str : attr

/-- The requirement identifier a declaration formalizes. One declaration, one identifier. -/
initialize reqAttr : ParametricAttribute String ←
  registerParametricAttribute {
    name := `req
    descr := "the requirement identifier (e.g. \"RUN-7\") this declaration formalizes"
    getParam := fun _ stx =>
      match stx with
      | `(attr| req $s:str) => pure s.getString
      | _ => throwError "expected @[req \"XXX-n\"]"
  }

end Rloop
