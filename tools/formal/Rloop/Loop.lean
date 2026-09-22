import Rloop.Req
/-! # The Run

The model of one Run (`01-run-lifecycle.md`), as `ADR-0002` decided: one total decision function
over what a Manager call left behind, and a Run as the fold of that function over a scripted
behaviour of the agents. Everything an Implementation must do between two agent calls is here;
nothing an agent does is — an agent's behaviour is an input, `Behaviour`, and every theorem below
holds for all of them.

The model carries no bytes, processes or git. A Task File is a content identity (`Nat`); a
Finished File is the `Status` its first line parses to; a Panel is which Reviewers rloop called
and the class of how many of them succeeded; interference by a non-Manager (`ADR-0003`) is an
input at two points of a Round. What the model omits is written on the theorem that depends on
it. -/

namespace Rloop

/-- The first line of a Finished File, parsed. `other` is any line that is not exactly one of the
three (`RUN-9`). -/
inductive Status | done | blocked | idle | other
  deriving DecidableEq, Repr

/-- rloop's exit codes (`RUN-10`). -/
inductive Exit | e0 | e1 | e2 | e3
  deriving DecidableEq, Repr

/-- Which Manager call is being judged: the pick, or a judge call after a Round. -/
inductive Phase | pick | judge
  deriving DecidableEq, Repr

/-- What one Manager call left behind: whether the process exited 0 in time, what it wrote as the
Finished File, and what it wrote as the Task File. `none` in either means it did not write that
file. The identities are of content: two writes of equal bytes are equal `Nat`s. -/
structure ManagerResult where
  ok : Bool
  writesFinished : Option Status
  writesTask : Option Nat
  deriving DecidableEq, Repr

/-- How many Reviewers of the Panel succeeded, reduced to the classes the decision reads
(`RUN-15`). -/
inductive Panel | all | some | none
  deriving DecidableEq, Repr

/-- Reviewer identities (`AGT-11`). -/
inductive Reviewer | astra | fable | opus | sol
  deriving DecidableEq, Repr

/-- The complete Panel. `AGT-11`: `The Panel MUST be exactly the four Reviewers AGT-7, AGT-8 and
AGT-10 name, with the Feedback File names DIR-4 gives them.` The alphabetical order used here is
not that requirement's — it is this model's trace encoding, which `conformance/scenario-lib.sh`
reproduces with `LC_ALL=C sort`. -/
def Reviewer.all : List Reviewer := [.astra, .fable, .opus, .sol]

/-- What a non-Manager may have done to the Manager's files (`ADR-0003`). -/
inductive Interference
  | none
  | editTask (content : Nat)
  | writeFinished (s : Status)
  | both (content : Nat) (s : Status)
  deriving DecidableEq, Repr

/-- The two points of a Round where the Checkpoint runs (`DIR-6`). -/
inductive Point | afterImplementer | afterPanel
  deriving DecidableEq, Repr

/-- The guards a dated decision added, each a parameter so its absence has a witness
(`ADR-0002`): the no-decision comparison (`RUN-12`), the round cap (`RUN-13`), the zero-survivor
abort (`RUN-15`), that abort counting a Reviewer never called as down (`RUN-15`), and the
Checkpoint (`DIR-6`). A theorem takes `Guards.all`; a witness turns one off. -/
structure Guards where
  noDecision : Bool := true
  cap : Bool := true
  panelAbort : Bool := true
  notRunDown : Bool := true
  checkpoint : Bool := true
  deriving DecidableEq, Repr

def Guards.all : Guards := {}

/-- The decision after a Manager call (`RUN-11`): the phase, the Task File content the Manager was
given (the snapshot, `none` at the pick), the content on disk when the call started (equal to the
snapshot under `Guards.all`), the Round just judged (`0` at the pick), the cap, and
what the call left behind — including a Finished File a non-Manager left that the Checkpoint did
not remove (`leftover`, always `none` under `Guards.all`). -/
inductive Verdict | next | exit (code : Exit)
  deriving DecidableEq, Repr

def decide (g : Guards) (phase : Phase) (prev current : Option Nat) (round maxRounds : Nat)
    (leftover : Option Status) (r : ManagerResult) : Verdict :=
  if !r.ok then .exit .e2
  else match r.writesFinished.or leftover with
    | some .done => .exit .e0
    | some .blocked => .exit .e1
    | some .idle => match phase with
      | .pick => .exit .e3
      | .judge => .exit .e2
    | some .other => .exit .e2
    | none =>
      match r.writesTask.or current with
      | none => .exit .e2
      | some t =>
        if g.noDecision && prev == some t then .exit .e2
        else if g.cap && round + 1 > maxRounds then .exit .e2
        else .next

/-- One agent process rloop started, in the order it started them. A `panel` entry is the whole
Panel: the class of how many of the Reviewers rloop called succeeded, and those Reviewers, which
run at once and which the Conformance Suite compares as a set (`ADR-0002`). A Reviewer `RUN-21`
recorded `unavailable` stays a Reviewer of the Panel (`RUN-15`) but is not a process rloop
started, so it is not a member here. -/
inductive Spawn
  | pick
  | implementer (round : Nat) (ok : Bool)
  | panel (round : Nat) (p : Panel) (members : List Reviewer)
  | judge (round : Nat)
  deriving DecidableEq, Repr

/-- The agents' behaviour, as a total function of the Round so that no Round is ever "off the end
of the script". `available k r` is false exactly when `RUN-21` recorded `r` `unavailable` before
Round `k`'s Panel; `unknown` means call it, so it is `true`, and so is every Reviewer by default.
`panel k` is the class of the Reviewers that were called. -/
structure Behaviour where
  pick : ManagerResult
  implementer : Nat → Bool
  panel : Nat → Panel
  judge : Nat → ManagerResult
  interference : Nat → Point → Interference
  available : Nat → Reviewer → Bool := fun _ _ => true

/-- A Behaviour with the interference removed: what the Checkpoint is supposed to make every Run
equivalent to. -/
def Behaviour.quiet (b : Behaviour) : Behaviour :=
  { b with interference := fun _ _ => .none }

/-- What is on disk between calls: the Task File content, the snapshot the Manager last left
(`task-<round>.md`), and a Finished File no Manager wrote. -/
structure Disk where
  task : Option Nat
  snapshot : Option Nat
  leftover : Option Status
  deriving DecidableEq, Repr

/-- Interference lands on the disk; the Checkpoint, when guarded, undoes it entirely, so under
`Guards.all` this is the identity (`DIR-6`, `DIR-7`). -/
def applyInterference (g : Guards) (d : Disk) : Interference → Disk
  | .none => d
  | .editTask c => if g.checkpoint then d else { d with task := some c }
  | .writeFinished s => if g.checkpoint then d else { d with leftover := some s }
  | .both c s => if g.checkpoint then d else { d with task := some c, leftover := some s }

/-- The Manager's write lands on the disk; when the Run continues, its Task File is the next
snapshot. -/
def afterManager (d : Disk) (r : ManagerResult) : Disk :=
  let t := r.writesTask.or d.task
  { task := t, snapshot := t, leftover := d.leftover }

/-- Every Reviewer of the Panel is down (`RUN-15`), given the class `p` of the Reviewers `called`.
A called Reviewer is down when it failed; one never called is down too under `notRunDown`, so the
Panel is all down when none was called or none of the called succeeded. Without it only a failure
counts, and the Panel is all down only when all four were called and failed. -/
def allDown (g : Guards) (p : Panel) (called : List Reviewer) : Bool :=
  if g.notRunDown then called.isEmpty || p == .none
  else called == Reviewer.all && p == .none

/-- The Rounds, with `fuel` the Rounds the cap still allows; `round` is the one about to run. -/
def rounds (g : Guards) (b : Behaviour) (maxRounds : Nat) :
    (fuel round : Nat) → Disk → List Spawn → Exit × List Spawn
  | 0, _, _, trace => (.e2, trace.reverse)
  | fuel + 1, round, d, trace =>
    let ok := b.implementer round
    let d := applyInterference g d (b.interference round .afterImplementer)
    let p := b.panel round
    let called := Reviewer.all.filter (b.available round)
    let trace := .panel round p called :: .implementer round ok :: trace
    if g.panelAbort && allDown g p called then (.e2, trace.reverse)
    else
      let d := applyInterference g d (b.interference round .afterPanel)
      let r := b.judge round
      let trace := .judge round :: trace
      match decide g .judge d.snapshot d.task round maxRounds d.leftover r with
      | .exit e => (e, trace.reverse)
      | .next => rounds g b maxRounds fuel (round + 1) (afterManager d r) trace

/-- One Run: the pick, then the Rounds. The fuel is one more than the cap so that a Run with the cap
guard off is distinguishable from one that hit it: `RUN-13`'s witness runs `maxRounds + 1`
Implementers. -/
def run (g : Guards) (b : Behaviour) (maxRounds : Nat) : Exit × List Spawn :=
  let d0 : Disk := { task := none, snapshot := none, leftover := none }
  match decide g .pick none none 0 maxRounds none b.pick with
  | .exit e => (e, [.pick])
  | .next => rounds g b maxRounds (maxRounds + 1) 1 (afterManager d0 b.pick) [.pick]

/-! ## Counting -/

def Spawn.isImplementer : Spawn → Bool
  | .implementer _ _ => true
  | _ => false

def Spawn.isManager : Spawn → Bool
  | .pick => true
  | .judge _ => true
  | _ => false

def Spawn.isJudge : Spawn → Bool
  | .judge _ => true
  | _ => false

def implementers (t : List Spawn) : Nat := (t.filter Spawn.isImplementer).length
def managers (t : List Spawn) : Nat := (t.filter Spawn.isManager).length
def judges (t : List Spawn) : Nat := (t.filter Spawn.isJudge).length

end Rloop
