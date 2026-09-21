import Rloop.Loop
/-! # The Conformance Suite's scenarios (`ADR-0002`)

Every scripted Behaviour over a small alphabet, run through the model with `Guards.all`, emitted
as one line each: the script the fakes replay, and the exit code and spawn trace the executable
must reproduce. The enumeration extends a script only while the model's Run continues, so each
line is a distinct executed trace and no line carries choices nothing reads.

Interference is added to the one-Round scripts only, at one point each (`ADR-0002`: at most one
point per script); under `Guards.all` it changes nothing, which is exactly what the suite then
checks of the executable.

The line format, tab-separated:

    id  max_rounds  pick  rounds  interference  exit  trace

`pick` is one of `ok:task ok:done ok:blocked ok:idle ok:other ok:nothing fail`; `rounds` is
`impl=<ok|fail>;panel=<all|some|none>;judge=<rewrite|same|done|blocked|idle|other|fail>` per
Round joined by `|` (`-` when no Round runs); `interference` is `-` or
`<round>:<afterImplementer|afterPanel>:<editTask|writeFinished|both>`; `trace` is the spawns
joined by `,`: `pick`, `impl<r>:<ok|fail>`, `panel<r>:<all|some|none>:<members>`, `judge<r>`.
`members` joins Reviewer names with `+` in canonical name order, including failed Reviewers. -/

namespace Rloop.Scenarios

/-- The Manager outcomes the alphabet offers, and their names. `task`/`rewrite` writes content
equal to the Round number plus one so that every rewrite is fresh; `same` writes nothing. -/
def managerChoices : List (String × (Nat → ManagerResult)) :=
  [ ("task", fun k => { ok := true, writesFinished := none, writesTask := some (k + 1) }),
    ("done", fun _ => { ok := true, writesFinished := some .done, writesTask := none }),
    ("blocked", fun _ => { ok := true, writesFinished := some .blocked, writesTask := none }),
    ("idle", fun _ => { ok := true, writesFinished := some .idle, writesTask := none }),
    ("other", fun _ => { ok := true, writesFinished := some .other, writesTask := none }),
    ("nothing", fun _ => { ok := true, writesFinished := none, writesTask := none }),
    ("fail", fun _ => { ok := false, writesFinished := none, writesTask := none }) ]

def pickName (n : String) : String := if n == "fail" then "fail" else s!"ok:{n}"
def judgeName (n : String) : String := if n == "task" then "rewrite" else if n == "nothing" then "same" else n

def implChoices : List (String × Bool) := [("ok", true), ("fail", false)]
def panelChoices : List (String × Panel) := [("all", .all), ("some", .some), ("none", .none)]
def panelName : Panel → String
  | .all => "all" | .some => "some" | .none => "none"

def interferenceChoices : List (String × Interference) :=
  [ ("editTask", .editTask 77), ("writeFinished", .writeFinished .done), ("both", .both 77 .done) ]
def pointName : Point → String
  | .afterImplementer => "afterImplementer" | .afterPanel => "afterPanel"

/-- One Round's scripted choices. -/
structure RoundChoice where
  impl : String × Bool
  panel : String × Panel
  judge : String × (Nat → ManagerResult)

def RoundChoice.name (c : RoundChoice) : String :=
  s!"impl={c.impl.1};panel={c.panel.1};judge={judgeName c.judge.1}"

/-- The Behaviour a script denotes: Round `k` reads the `k`-th choice; beyond the script (never
reached, since the enumeration stops where the Run stops) the agents fail. -/
def behaviour (pick : String × (Nat → ManagerResult)) (rounds : List RoundChoice)
    (interf : Option (Nat × Point × Interference)) : Behaviour :=
  { pick := pick.2 0
    implementer := fun k => rounds[k - 1]?.map (·.impl.2) |>.getD false
    panel := fun k => rounds[k - 1]?.map (·.panel.2) |>.getD .none
    judge := fun k => rounds[k - 1]?.map (fun c => c.judge.2 k)
      |>.getD { ok := false, writesFinished := none, writesTask := none }
    interference := fun k p => match interf with
      | some (r, q, i) => if r == k && q == p then i else .none
      | none => .none }

def Reviewer.name : Reviewer → String
  | .astra => "astra" | .fable => "fable" | .opus => "opus" | .sol => "sol"

/-- Encode membership as a set, regardless of list order or repetition. -/
def membershipName (members : List Reviewer) : String :=
  String.intercalate "+" ((Reviewer.all.filter members.contains).map Reviewer.name)

def Spawn.name : Spawn → String
  | .pick => "pick"
  | .implementer r ok => s!"impl{r}:{if ok then "ok" else "fail"}"
  | .panel r p members => s!"panel{r}:{panelName p}:{membershipName members}"
  | .judge r => s!"judge{r}"

structure Scenario where
  maxRounds : Nat
  pick : String
  rounds : List RoundChoice
  interference : String
  exit : Exit
  trace : List Spawn

def exitName : Exit → String
  | .e0 => "0" | .e1 => "1" | .e2 => "2" | .e3 => "3"

def Scenario.line (i : Nat) (s : Scenario) : String :=
  let rounds := if s.rounds.isEmpty then "-" else String.intercalate "|" (s.rounds.map (·.name))
  String.intercalate "\t"
    [ s!"S{i}", toString s.maxRounds, s.pick, rounds, s.interference, exitName s.exit,
      String.intercalate "," (s.trace.map Spawn.name) ]

/-- Does the Run with this script reach Round `n + 1`? It does exactly when its trace holds an
Implementer for that Round. -/
def reachesRound (tr : List Spawn) (r : Nat) : Bool :=
  tr.any fun s => match s with | .implementer k _ => k == r | _ => false

/-- The alphabet one enumeration draws from. -/
structure Alphabet where
  impls : List (String × Bool) := implChoices
  panels : List (String × Panel) := panelChoices
  judges : List (String × (Nat → ManagerResult)) := managerChoices

/-- Extend `rounds` by one scripted Round in every way; a script is a scenario when the Run
executes exactly its Rounds, and a prefix to extend when the Run goes on past them. A Round whose Panel loses every Reviewer never
reaches its judge, so only one judge choice is drawn for it: the others would repeat the line. -/
partial def extend (a : Alphabet) (maxRounds : Nat) (pick : String × (Nat → ManagerResult))
    (interf : Option (Nat × Point × Interference)) (interfName : String)
    (rounds : List RoundChoice) : List Scenario :=
  if rounds.length ≥ maxRounds then [] else
  (a.impls.flatMap fun impl => a.panels.flatMap fun panel =>
    (if panel.2 == .none then a.judges.take 1 else a.judges).flatMap fun judge =>
    let rs := rounds ++ [{ impl := impl, panel := panel, judge := judge }]
    let (e, tr) := run Guards.all (behaviour pick rs interf) maxRounds
    if !reachesRound tr rs.length then []
    -- The Run went on past the script's last Round: this script is a prefix, not a scenario, and
    -- the recursion supplies the next Round's choices.
    else if reachesRound tr (rs.length + 1) then extend a maxRounds pick interf interfName rs
    else [{ maxRounds := maxRounds, pick := pickName pick.1, rounds := rs, interference := interfName,
            exit := e, trace := tr }])

def scriptsFor (a : Alphabet) (maxRounds : Nat) (interf : Option (Nat × Point × Interference))
    (interfName : String) : List Scenario :=
  managerChoices.flatMap fun pick =>
    let (e, tr) := run Guards.all (behaviour pick [] interf) maxRounds
    if reachesRound tr 1 then extend a maxRounds pick interf interfName []
    else [{ maxRounds := maxRounds, pick := pickName pick.1, rounds := [], interference := interfName,
            exit := e, trace := tr }]

/-- The interference scripts draw from a narrower alphabet — a succeeding Implementer, a full
Panel, and the three judge outcomes that read the Task File or the Finished File — because the
other choices end the Round before the Checkpoint's work could show. -/
def narrow : Alphabet :=
  { impls := implChoices.take 1, panels := panelChoices.take 1,
    judges := managerChoices.filter fun (n, _) => n == "task" || n == "nothing" || n == "done" }

/-- The scenarios: caps 1 and 2 without interference, then cap 1 with each single interference. -/
def all : List Scenario :=
  scriptsFor {} 1 none "-" ++ scriptsFor {} 2 none "-"
  ++ ([Point.afterImplementer, Point.afterPanel].flatMap fun p =>
      interferenceChoices.flatMap fun (n, i) =>
        (scriptsFor narrow 1 (some (1, p, i)) s!"1:{pointName p}:{n}").filter (·.rounds.length > 0))

/-- The negative control (`ADR-0002`): for each guard, the number of scenario lines whose expected
exit or trace the model without that guard would get wrong. A guard nobody's line depends on is a
guard the suite cannot see missing. -/
def controls : List (String × Nat) :=
  let without : List (String × Guards) :=
    [ ("noDecision", { Guards.all with noDecision := false }),
      ("cap", { Guards.all with cap := false }),
      ("panelAbort", { Guards.all with panelAbort := false }),
      ("checkpoint", { Guards.all with checkpoint := false }) ]
  without.map fun (name, g) =>
    (name, (all.filter fun s =>
      let interf := parseInterference s.interference
      let pick := managerChoices.find? (fun (n, _) => pickName n == s.pick) |>.getD ("fail", fun _ => { ok := false, writesFinished := none, writesTask := none })
      run g (behaviour pick s.rounds interf) s.maxRounds != (s.exit, s.trace)).length)
where
  parseInterference (n : String) : Option (Nat × Point × Interference) :=
    if n == "-" then none else
    match n.splitOn ":" with
    | [r, p, k] =>
      let point := if p == "afterPanel" then Point.afterPanel else Point.afterImplementer
      (interferenceChoices.find? (·.1 == k)).map fun (_, i) => (r.toNat!, point, i)
    | _ => none

def tsv : List String :=
  "id\tmax_rounds\tpick\trounds\tinterference\texit\ttrace" ::
    (all.zipIdx.map fun (s, i) => s.line (i + 1))

end Rloop.Scenarios
