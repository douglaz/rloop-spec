import Rloop.Loop
/-! The marked regions (`ADR-0002`): what a region between `<!-- formal: <decl> -->` and
`<!-- /formal -->` in a document must contain, computed from the declaration named. `lake exe
render` prints them and `tools/check_regions.py` holds each document to them, byte for byte
(every region here is a `render` region: pure computation). -/

namespace Rloop.Render

/-- A marked region: the declaration it renders, its kind, and its text. -/
structure Region where
  decl : String
  kind : String
  text : String

/-! ## `RUN-11`'s decision table -/

/-- The three states of the Task File the decision distinguishes after a call, relative to the
snapshot the Manager was given. -/
inductive TaskState | absent | unchanged | rewritten
  deriving DecidableEq, Repr

def TaskState.name : TaskState → String
  | .absent => "absent"
  | .unchanged => "unchanged"
  | .rewritten => "rewritten"

/-- The first line of the Finished File, as the table spells it. -/
def finishedName : Option Status → String
  | none => "none"
  | some .done => "`STATUS: done`"
  | some .blocked => "`STATUS: blocked`"
  | some .idle => "`STATUS: idle`"
  | some .other => "anything else"

def Phase.name : Phase → String
  | .pick => "pick"
  | .judge => "judge"

def Verdict.name : Verdict → String
  | .next => "next Round"
  | .exit .e0 => "exit 0"
  | .exit .e1 => "exit 1"
  | .exit .e2 => "exit 2"
  | .exit .e3 => "exit 3"

/-- One row: the inputs, and `decide`'s verdict on representative values — the snapshot is content
`1` (or absent at the pick), a rewrite is content `2`, and the cap is either reached (`round =
maxRounds`) or not (`round + 1 < maxRounds`). -/
def row (phase : Phase) (ok : Bool) (fin : Option Status) (task : TaskState) (atCap : Bool) :
    String :=
  let prev : Option Nat := match phase with | .pick => none | .judge => some 1
  let writesTask : Option Nat := match task with
    | .absent => none
    | .unchanged => none
    | .rewritten => some 2
  let cur : Option Nat := match phase, task with
    | .pick, _ => none
    | .judge, .absent => none
    | .judge, _ => some 1
  let (round, maxRounds) := match phase, atCap with
    | .pick, true => (0, 0)
    | .pick, false => (0, 10)
    | .judge, true => (10, 10)
    | .judge, false => (3, 10)
  let v := decide Guards.all phase prev cur round maxRounds none
    { ok := ok, writesFinished := fin, writesTask := writesTask }
  let taskName := match phase, task with
    | .pick, .rewritten => "written"
    | _, t => t.name
  s!"| {Phase.name phase} | {if ok then "0" else "non-zero"} | {finishedName fin} | {taskName} | {if atCap then "yes" else "no"} | **{Verdict.name v}** |"

/-- The rows the table shows: every combination that a reader could ask about, in the order the
decision reads them, with the combinations a prior column already settles collapsed to one row. -/
def rows : List String :=
  -- A failed call: nothing else is read.
  [ row .pick false none .absent false, row .judge false (some .done) .rewritten false ]
  -- A Finished File: its first line decides, whatever the Task File.
  ++ ([Phase.pick, Phase.judge].flatMap fun ph =>
      [Status.done, .blocked, .idle, .other].map fun s => row ph true (some s) .rewritten false)
  -- No Finished File: the Task File and the cap.
  ++ [ row .pick true none .absent false, row .pick true none .rewritten false,
       row .pick true none .rewritten true,
       row .judge true none .absent false, row .judge true none .unchanged false,
       row .judge true none .rewritten false, row .judge true none .rewritten true ]

@[req "RUN-11"]
def decisionTable : String :=
  String.intercalate "\n"
    ([ "| call | Manager exit | Finished File first line | Task File vs. snapshot | cap reached? | verdict |",
       "|---|---|---|---|---|---|" ] ++ rows)

def regions : List Region :=
  [ { decl := "Rloop.Render.decisionTable", kind := "render", text := decisionTable } ]

end Rloop.Render
