import Rloop.Loop
/-! # Requested sleeps and process attempts (`RUN-24`)

A Round has `ceil(b/p)` paid sleeps: each requests `min p remaining`, including the last,
possibly shorter sleep. Checks, calls and wakeup delays spend none. `credits` is that ledger's
remaining sleep count, not wall time. The script supplies every reading and attempt outcome;
weekly means exhaustion of the Manager's own Seat, and clear includes unknown. Byte recognition
and process reaping are suite obligations. A cut is already the guarded, within-bound outcome.

The projection into `Behaviour` keeps one logical judge spawn if attempt 1 was admitted, the
terminal attempt's `ManagerResult`, and the final Panel reading for Reviewer availability.
Expiry before any attempt projects to an unavailable Manager; expiry after a cut projects to a
failed terminal attempt. Thus existing Run theorems and `decide` need no changed statements.
-/
namespace Rloop.Wait

inductive Event | clear | session | weekly | cut | done
  deriving DecidableEq, Repr
inductive Site | panel | judge | attempt
  deriving DecidableEq, Repr
structure Outcome where
  attempts : Nat := 0
  done : Bool := false
  deriving DecidableEq, Repr

/-- Number of nonzero requested sleeps, for poll `p ≥ 1`. -/
def sleeps (b p : Nat) : Nat := (b + p - 1) / p

/-- The shared-ledger guard. Turning it off refills the ledger on every cut. A session check
and a cut both pay before the next check; a weekly check never pays or retries. A script ending
without a terminal result fails. Malformed event/site combinations fail closed too. -/
def play (shared : Bool) (initial : Nat) : List Event → Site → Nat → Outcome
  | [], _, _ => {}
  | e :: es, site, credits =>
    match site, e with
    | .attempt, .done => { attempts := 1, done := true }
    | .attempt, .cut =>
      let left := if shared then credits else initial
      match left with
      | 0 => { attempts := 1 }
      | n + 1 => let r := play shared initial es .judge n
                 { r with attempts := r.attempts + 1 }
    | .panel, .clear => play shared initial es .judge credits
    | .judge, .clear => play shared initial es .attempt credits
    | .panel, .session | .judge, .session =>
      match credits with
      | 0 => {}
      | n + 1 => play shared initial es site n
    | _, _ => {}

/-- Every script of readings and cuts, including fail-open checks followed by repeated cuts,
is bounded by the shared ledger. -/
theorem play_bound (initial : Nat) (script : List Event) :
    ∀ (site : Site) (credits : Nat),
      (play true initial script site credits).attempts ≤ credits + 1 := by
  induction script with
  | nil => intro site credits; simp [play]
  | cons e es ih =>
    intro site credits
    cases site <;> cases e <;> cases credits <;>
      simp_all [play] <;> try omega
    all_goals exact Nat.le_trans (ih _ _) (by omega)

@[req "RUN-24"]
theorem attempt_bound (b p : Nat) (_hp : p ≥ 1) (script : List Event) :
    (play true (sleeps b p) script .panel (sleeps b p)).attempts ≤
      1 + (b + p - 1) / p := by
  have h := play_bound (sleeps b p) script .panel (sleeps b p)
  simpa [sleeps, Nat.add_comm] using h

/-- Two cuts, two clear re-checks, then done: refilling per cut both overruns the bound and
changes the terminal result. The appended scenario block replays this witness. -/
@[req "RUN-24"]
theorem fresh_budget_overruns :
    let script := [Event.clear, .clear, .cut, .clear, .cut, .clear, .done]
    (play true 1 script .panel 1 = { attempts := 2, done := false }) ∧
    (play false 1 script .panel 1 = { attempts := 3, done := true }) := by decide

end Rloop.Wait
