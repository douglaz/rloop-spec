import Rloop.Loop
/-! # The Conformance Suite's scenarios (`ADR-0002`)

Every scripted Behaviour over a small alphabet, run through the model with `Guards.all`, emitted
as one line each: the script the fakes replay, and the exit code and spawn trace the executable
must reproduce. The enumeration extends a script only while the model's Run continues, so no line
scripts a Round the Run does not reach. Among the lines with neither interference nor a probe
script, each is a distinct executed trace and none carries choices nothing reads.

Two blocks are appended, each from a narrower alphabet, and in each a choice may deliberately
change nothing. Interference is added to the one-Round scripts only, at one point each
(`ADR-0002`: at most one point per script); under `Guards.all` it changes nothing, which is
exactly what the suite then checks of the executable. A probe script says what the availability
probe prints in each Round (`RUN-21`): a family at 100% takes that Reviewer out of the Panel's
calls, and every other shape — the fail-open paths — takes out nobody, so those lines repeat the
exit and trace of a line with no probe script, which is what the suite then checks: that the
executable's Panel stays whole.

The line format, tab-separated:

    id  max_rounds  pick  rounds  interference  probe  exit  trace

`pick` is one of `ok:task ok:done ok:blocked ok:idle ok:other ok:nothing fail`; `rounds` is
`impl=<ok|fail>;panel=<all|some|none>;judge=<rewrite|same|done|blocked|idle|other|fail>` per
Round joined by `|` (`-` when no Round runs); `interference` is `-` or
`<round>:<afterImplementer|afterPanel>:<editTask|writeFinished|both>`; `probe` is `-` (the fakes'
default, a probe reporting nothing exhausted) or the fakes' probe shape per Round joined by `|`;
`trace` is the spawns joined by `,`: `pick`, `impl<r>:<ok|fail>`,
`panel<r>:<all|some|none>:<members>`, `judge<r>`. `members` joins the names of the Reviewers
called with `+` in canonical name order, including failed Reviewers; a Reviewer `RUN-21` recorded
`unavailable` is not called and is not a member. -/

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

/-- Which Reviewers `RUN-21` leaves to be called after the probe prints the fakes' shape `n`
(`conformance/fakes/agent` says what each prints). Only a line beginning with a family at 100%,
from a probe that exited zero, takes a Reviewer out, and only `Fable` and `Opus` are in the
table; every other shape — `clear`, `fail`, `loose`, `unlisted` among them — reads `unknown`
for all four and takes out nobody. -/
def probeReads : String → Reviewer → Bool
  | "fable" => (· != .fable)
  | "opus" => (· != .opus)
  | "both" => fun r => r != .fable && r != .opus
  | _ => fun _ => true

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
    (interf : Option (Nat × Point × Interference)) (probes : List String) : Behaviour :=
  { pick := pick.2 0
    implementer := fun k => rounds[k - 1]?.map (·.impl.2) |>.getD false
    panel := fun k => rounds[k - 1]?.map (·.panel.2) |>.getD .none
    judge := fun k => rounds[k - 1]?.map (fun c => c.judge.2 k)
      |>.getD { ok := false, writesFinished := none, writesTask := none }
    interference := fun k p => match interf with
      | some (r, q, i) => if r == k && q == p then i else .none
      | none => .none
    available := fun k => probeReads (probes[k - 1]?.getD "-") }

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
  probes : List String
  exit : Exit
  trace : List Spawn

def exitName : Exit → String
  | .e0 => "0" | .e1 => "1" | .e2 => "2" | .e3 => "3"

def Scenario.line (i : Nat) (s : Scenario) : String :=
  let rounds := if s.rounds.isEmpty then "-" else String.intercalate "|" (s.rounds.map (·.name))
  String.intercalate "\t"
    [ s!"S{i}", toString s.maxRounds, s.pick, rounds, s.interference,
      if s.probes.isEmpty then "-" else String.intercalate "|" s.probes, exitName s.exit,
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
    (interf : Option (Nat × Point × Interference)) (interfName : String) (probes : List String)
    (rounds : List RoundChoice) : List Scenario :=
  if rounds.length ≥ maxRounds then [] else
  (a.impls.flatMap fun impl => a.panels.flatMap fun panel =>
    (if panel.2 == .none then a.judges.take 1 else a.judges).flatMap fun judge =>
    let rs := rounds ++ [{ impl := impl, panel := panel, judge := judge }]
    let (e, tr) := run Guards.all (behaviour pick rs interf probes) maxRounds
    if !reachesRound tr rs.length then []
    -- The Run went on past the script's last Round: this script is a prefix, not a scenario, and
    -- the recursion supplies the next Round's choices.
    else if reachesRound tr (rs.length + 1) then extend a maxRounds pick interf interfName probes rs
    else [{ maxRounds := maxRounds, pick := pickName pick.1, rounds := rs, interference := interfName,
            probes := probes, exit := e, trace := tr }])

def scriptsFor (a : Alphabet) (maxRounds : Nat) (interf : Option (Nat × Point × Interference))
    (interfName : String) (probes : List String := []) : List Scenario :=
  managerChoices.flatMap fun pick =>
    let (e, tr) := run Guards.all (behaviour pick [] interf probes) maxRounds
    if reachesRound tr 1 then extend a maxRounds pick interf interfName probes []
    else [{ maxRounds := maxRounds, pick := pickName pick.1, rounds := [], interference := interfName,
            probes := probes, exit := e, trace := tr }]

/-- The interference scripts draw from a narrower alphabet — a succeeding Implementer, a full
Panel, and the three judge outcomes that read the Task File or the Finished File — because the
other choices end the Round before the Checkpoint's work could show. -/
def narrow : Alphabet :=
  { impls := implChoices.take 1, panels := panelChoices.take 1,
    judges := managerChoices.filter fun (n, _) => n == "task" || n == "nothing" || n == "done" }

/-- The probe scripts draw from their own narrow alphabet: a succeeding Implementer, a Panel whose
called Reviewers all succeed or all fail, and a judge that ends the Run or rewrites the brief —
what the probe changes is who is called and whether the Panel is all down, and nothing after.
`some` is left out because the fakes script it as `fable` alone succeeding, so with `fable` not
called it is a Panel of failures, not the class the line would name. -/
def narrowProbe : Alphabet :=
  { impls := implChoices.take 1, panels := panelChoices.filter (·.2 != .some),
    judges := managerChoices.filter fun (n, _) => n == "task" || n == "done" }

/-- Each probe script with its cap: either family at 100% and both (`RUN-21`'s table, both rows),
the matching line from a probe that exits non-zero, the matching words not at the start of a line,
and families outside the table; then a Round that reads `fable` `unavailable` followed by one that
reads nobody so, which only a Run that probes again each Round gets right. -/
def probeScripts : List (Nat × List String) :=
  [ (1, ["fable"]), (1, ["opus"]), (1, ["both"]), (1, ["fail"]), (1, ["loose"]), (1, ["unlisted"]),
    (2, ["fable", "clear"]) ]

/-- The scenarios: caps 1 and 2 without interference, then cap 1 with each single interference,
then each probe script, kept to the lines that reach every Round it scripts a probe for. -/
def all : List Scenario :=
  scriptsFor {} 1 none "-" ++ scriptsFor {} 2 none "-"
  ++ ([Point.afterImplementer, Point.afterPanel].flatMap fun p =>
      interferenceChoices.flatMap fun (n, i) =>
        (scriptsFor narrow 1 (some (1, p, i)) s!"1:{pointName p}:{n}").filter (·.rounds.length > 0))
  ++ (probeScripts.flatMap fun (cap, probes) =>
      (scriptsFor narrowProbe cap none "-" probes).filter (·.rounds.length ≥ probes.length))

/-- The negative control (`ADR-0002`): for each guard, the number of scenario lines whose expected
exit or trace the model without that guard would get wrong. A guard nobody's line depends on is a
guard the suite cannot see missing. -/
def controls : List (String × Nat) :=
  let without : List (String × Guards) :=
    [ ("noDecision", { Guards.all with noDecision := false }),
      ("cap", { Guards.all with cap := false }),
      ("panelAbort", { Guards.all with panelAbort := false }),
      ("notRunDown", { Guards.all with notRunDown := false }),
      ("checkpoint", { Guards.all with checkpoint := false }) ]
  without.map fun (name, g) =>
    (name, (all.filter fun s =>
      let interf := parseInterference s.interference
      let pick := managerChoices.find? (fun (n, _) => pickName n == s.pick) |>.getD ("fail", fun _ => { ok := false, writesFinished := none, writesTask := none })
      run g (behaviour pick s.rounds interf s.probes) s.maxRounds != (s.exit, s.trace)).length)
where
  parseInterference (n : String) : Option (Nat × Point × Interference) :=
    if n == "-" then none else
    match n.splitOn ":" with
    | [r, p, k] =>
      let point := if p == "afterPanel" then Point.afterPanel else Point.afterImplementer
      (interferenceChoices.find? (·.1 == k)).map fun (_, i) => (r.toNat!, point, i)
    | _ => none

def tsv : List String :=
  "id\tmax_rounds\tpick\trounds\tinterference\tprobe\texit\ttrace" ::
    (all.zipIdx.map fun (s, i) => s.line (i + 1))

end Rloop.Scenarios
