import Rloop.Loop
/-! # What every Run satisfies

Theorems over every `Behaviour` with `Guards.all`, and for each guard a witness — a concrete
Behaviour on which the Run with that guard off does what the theorem forbids (`ADR-0002`: "a
successful proof without the second theorem is decoration"). A witness closes by `decide` on a
closed term, under the standard axioms.

What the model does not carry, and so what no theorem here says: that an agent process ends
(timeouts are `AGT-14`, an assumption here), that bytes on disk are what a write meant, that two
Reviewers of one Panel saw one tree (`ADR-0003`'s threat model). -/

namespace Rloop

/-! ## Lemmas on the pieces -/

theorem applyInterference_all (d : Disk) (i : Interference) :
    applyInterference Guards.all d i = d := by
  cases i <;> rfl

/-- A judge call never yields `idle`'s exit: `idle` is a pick-only outcome (`RUN-9`). -/
theorem decide_judge_ne_e3 (g : Guards) (prev cur : Option Nat) (round m : Nat)
    (left : Option Status) (r : ManagerResult) :
    decide g .judge prev cur round m left r ≠ .exit .e3 := by
  unfold decide
  repeat' split
  all_goals (first | decide | contradiction | (simp; done) | (simp_all; done))

theorem applyInterference_leftover (g : Guards) (hg : g.checkpoint = true) (d : Disk)
    (i : Interference) : (applyInterference g d i).leftover = d.leftover := by
  cases i <;> simp [applyInterference, hg]

theorem implementers_reverse (t : List Spawn) : implementers t.reverse = implementers t := by
  simp [implementers, List.filter_reverse, List.length_reverse]

theorem judges_reverse (t : List Spawn) : judges t.reverse = judges t := by
  simp [judges, List.filter_reverse, List.length_reverse]

theorem managers_reverse (t : List Spawn) : managers t.reverse = managers t := by
  simp [managers, List.filter_reverse, List.length_reverse]

theorem implementers_append (t u : List Spawn) :
    implementers (t ++ u) = implementers t + implementers u := by
  simp [implementers, List.filter_append, List.length_append]

theorem implementers_pick : implementers [.pick] = 0 := rfl
theorem implementers_one_implementer (k : Nat) (ok : Bool) :
    implementers [.implementer k ok] = 1 := rfl

theorem implementers_cons_panel (k : Nat) (p : Panel) (members : List Reviewer) (t : List Spawn) :
    implementers (.panel k p members :: t) = implementers t := by
  simp [implementers, List.filter, Spawn.isImplementer]

theorem implementers_cons_implementer (k : Nat) (ok : Bool) (t : List Spawn) :
    implementers (.implementer k ok :: t) = implementers t + 1 := by
  simp [implementers, List.filter, Spawn.isImplementer]

theorem implementers_cons_judge (k : Nat) (t : List Spawn) :
    implementers (.judge k :: t) = implementers t := by
  simp [implementers, List.filter, Spawn.isImplementer]

/-- A Seat's verdict reads the probe and the Seat's model, not what the agents did. -/
theorem seatAvailable_interference (b : Behaviour) (i : Nat → Point → Interference) :
    ({ b with interference := i } : Behaviour).seatAvailable = b.seatAvailable := rfl

theorem seatAvailable_implementer (b : Behaviour) (f : Nat → Bool) :
    ({ b with implementer := f } : Behaviour).seatAvailable = b.seatAvailable := rfl

/-! ## `RUN-13` — the cap bounds the Implementers -/

/-- Entering Round `round` with the cap guard on needs `round ≤ m`, and from there at most
`m - round + 1` more Implementers run. -/
theorem rounds_implementers_le (g : Guards) (hg : g.cap = true) (b : Behaviour) (m : Nat) :
    ∀ (fuel round : Nat) (d : Disk) (tr : List Spawn), round ≤ m →
      implementers (rounds g b m fuel round d tr).2 ≤ implementers tr + (m - round + 1) := by
  intro fuel
  induction fuel with
  | zero =>
    intro round d tr _
    simp [rounds, implementers_reverse]
  | succ fuel ih =>
    intro round d tr hr
    simp only [rounds]
    split
    · simp only [implementers_reverse, implementers_cons_panel, implementers_cons_implementer]
      omega
    · split
      · simp only [implementers_reverse, implementers_cons_panel, implementers_cons_implementer]
        omega
      · split
        · simp only [implementers_reverse, implementers_cons_judge, implementers_cons_panel,
            implementers_cons_implementer]
          omega
        · rename_i h
          -- The verdict was `next`, so the cap check `round + 1 > m` was false.
          have hle : round + 1 ≤ m := by
            unfold decide at h
            repeat' split at h
            all_goals simp_all
            all_goals omega
          have := ih (round + 1)
            (afterManager (applyInterference g (applyInterference g d
              (b.interference round .afterImplementer)) (b.interference round .afterPanel))
              (b.judge round))
            (.judge round :: .panel round (b.panel round) (Reviewer.all.filter (b.available round)) ::
              .implementer round (b.implementer round) :: tr) hle
          simp only [implementers_cons_judge, implementers_cons_panel,
            implementers_cons_implementer] at this
          omega

/-- The cap is a bound on Implementer spawns, whatever the agents do. -/
@[req "RUN-13"]
theorem implementers_le_maxRounds (b : Behaviour) (m : Nat) :
    implementers (run Guards.all b m).2 ≤ m := by
  unfold run
  split
  · simp [implementers]
  · split
    · simp [implementers, List.filter, Spawn.isImplementer]
    · rename_i h
      have hle : 1 ≤ m := by
        unfold decide at h
        repeat' split at h
        all_goals (simp_all [Guards.all]; try omega)
      have := rounds_implementers_le Guards.all rfl b m (m + 1) 1
        (afterManager { task := none, snapshot := none, leftover := none } b.pick) [.pick] hle
      simp only [implementers_pick] at this
      dsimp only
      omega

/-- A Manager that rewrites a fresh brief every Round, on an Implementer that never fails and a
Panel that always succeeds: the Run that never converges. -/
def restless : Behaviour :=
  { pick := { ok := true, writesFinished := none, writesTask := some 0 }
    implementer := fun _ => true
    panel := fun _ => .all
    judge := fun k => { ok := true, writesFinished := none, writesTask := some k }
    interference := fun _ _ => .none }

/-- With the cap guard off, `restless` at `maxRounds = 1` runs a second Implementer. -/
@[req "RUN-13"]
theorem cap_off_overruns :
    implementers (run { Guards.all with cap := false } restless 1).2 = 2 := by decide

/-! ## `RUN-9`, `RUN-10` — `idle` is pick-only, and `e3` means no Implementer ran -/

theorem rounds_ne_e3 (g : Guards) (b : Behaviour) (m : Nat) :
    ∀ (fuel round : Nat) (d : Disk) (tr : List Spawn),
      (rounds g b m fuel round d tr).1 ≠ .e3 := by
  intro fuel
  induction fuel with
  | zero => intro _ _ _; simp [rounds]
  | succ fuel ih =>
    intro round d tr
    simp only [rounds]
    split
    · simp
    · split
      · simp
      · split
        · rename_i h
          intro he
          simp at he
          subst he
          exact decide_judge_ne_e3 _ _ _ _ _ _ _ h
        · exact ih _ _ _

/-- Exit 3 happens only at the pick: the trace is the pick alone. -/
@[req "RUN-10"]
theorem idle_spawns_nothing (b : Behaviour) (m : Nat) :
    (run Guards.all b m).1 = .e3 → (run Guards.all b m).2 = [.pick] := by
  unfold run
  split
  · intro h; simp at h
  · split
    · intro _; rfl
    · intro h
      exact absurd h (rounds_ne_e3 _ _ _ _ _ _ _)

/-! ## `RUN-15` — a Panel with no survivor aborts before the judge -/

def Spawn.isJudgeOf (k : Nat) : Spawn → Bool
  | .judge j => j == k
  | _ => false

/-- The Behaviour whose first Panel loses every Reviewer. -/
def orphaned : Behaviour :=
  { restless with panel := fun _ => .none }

@[req "RUN-15"]
theorem panel_none_aborts :
    run Guards.all orphaned 3 = (.e2, [.pick, .implementer 1 true, .panel 1 .none Reviewer.all]) := by decide

/-- With the abort off, the judge is called over a Panel that produced nothing. -/
@[req "RUN-15"]
theorem panel_abort_off_judges :
    ((run { Guards.all with panelAbort := false } orphaned 3).2.any (Spawn.isJudgeOf 1)) = true := by
  decide

/-- The first Panel reads both claude Reviewers `unavailable` and loses the two it calls: two
Reviewers not run and two failed. -/
def halfRun : Behaviour :=
  { orphaned with available := fun _ r => r != .fable && r != .opus }

/-- Not run and failed are both down, so that Panel is all down: exit 2 before the judge, with only
the Reviewers called in the trace. -/
@[req "RUN-15"]
theorem not_run_and_failed_aborts :
    run Guards.all halfRun 3 = (.e2, [.pick, .implementer 1 true, .panel 1 .none [.astra, .sol]]) := by
  decide

/-- With a Reviewer never called no longer counted as down, two failures of four read as a degraded
Panel and the judge is called. -/
@[req "RUN-15"]
theorem not_run_down_off_judges :
    ((run { Guards.all with notRunDown := false } halfRun 3).2.any (Spawn.isJudgeOf 1)) = true := by
  decide

/-- A Panel that called no Reviewer at all is all down, whatever class the script gives it. -/
@[req "RUN-15"]
theorem none_called_aborts (p : Panel) :
    run Guards.all { restless with panel := fun _ => p, available := fun _ _ => false } 3 =
      (.e2, [.pick, .implementer 1 true, .panel 1 p []]) := by
  cases p <;> decide

/-! ## `RUN-22` — a Seat that cannot answer refuses the Run, or the judge call -/

/-- A Run whose probe before the pick records the Manager's or the Implementer's Seat
`unavailable` exits 2 having spawned nothing: no pick, and nothing after it. -/
@[req "RUN-22"]
theorem seat_out_refused (b : Behaviour) (m : Nat)
    (h : b.seatAvailable 0 .manager = false ∨ b.seatAvailable 0 .implementer = false) :
    run Guards.all b m = (.e2, []) := by
  unfold run
  rcases h with h | h <;> simp [Guards.all, h]

/-- `restless` with the Manager's Seat on `fable`'s model and the Implementer's on `opus`'s, and a
probe before the pick that reads `out`'s family at 100%: `fable` takes out the Manager's Seat,
`opus` the Implementer's. -/
def seated (out : Reviewer) : Behaviour :=
  { restless with
    seat := fun s => match s with | .manager => some .fable | .implementer => some .opus
    available := fun k r => !(k == 0 && r == out) }

/-- With the refusal off, each Seat's arm spawns the pick it was to refuse. -/
@[req "RUN-22"]
theorem pick_refusal_off_picks :
    (run { Guards.all with pickRefusal := false } (seated .fable) 1).2.head? = some .pick ∧
    (run { Guards.all with pickRefusal := false } (seated .opus) 1).2.head? = some .pick := by
  decide

theorem rounds_judged_answers (b : Behaviour) (m k : Nat) :
    ∀ (fuel round : Nat) (d : Disk) (tr : List Spawn),
      (tr.any (Spawn.isJudgeOf k) = true → b.seatAvailable k .manager = true) →
      (rounds Guards.all b m fuel round d tr).2.any (Spawn.isJudgeOf k) = true →
        b.seatAvailable k .manager = true := by
  intro fuel
  induction fuel with
  | zero => intro _ _ tr htr h; simp [rounds, List.any_reverse, -List.any_eq_true] at h; exact htr h
  | succ fuel ih =>
    intro round d tr htr
    simp only [rounds]
    split
    · intro h; simp [List.any_reverse, Spawn.isJudgeOf, -List.any_eq_true] at h; exact htr h
    · split
      · intro h; simp [List.any_reverse, Spawn.isJudgeOf, -List.any_eq_true] at h; exact htr h
      · rename_i hj
        have htr' : (Spawn.judge round :: Spawn.panel round (b.panel round)
            (Reviewer.all.filter (b.available round)) ::
            Spawn.implementer round (b.implementer round) :: tr).any (Spawn.isJudgeOf k) = true →
            b.seatAvailable k .manager = true := by
          intro h
          simp [Spawn.isJudgeOf, -List.any_eq_true] at h
          rcases h with h | h
          · subst h; simpa [Guards.all] using hj
          · exact htr h
        split
        · intro h; simp only [List.any_reverse] at h; exact htr' h
        · exact ih _ _ _ htr'

/-- Every judge call a Run makes is for a Round whose probe recorded the Manager's Seat
`unknown`. -/
@[req "RUN-22"]
theorem judged_only_when_manager_answers (b : Behaviour) (m k : Nat) :
    (run Guards.all b m).2.any (Spawn.isJudgeOf k) = true → b.seatAvailable k .manager = true := by
  unfold run
  split
  · intro h; simp at h
  · split
    · intro h; simp [Spawn.isJudgeOf] at h
    · exact rounds_judged_answers b m k _ _ _ _ (by intro h; simp [Spawn.isJudgeOf] at h)

/-- `restless` with the Manager's Seat on `fable`'s model, and the probe before Round 2 reading that
family at 100%: a Manager that runs out mid-Run. -/
def runsOut : Behaviour :=
  { restless with
    seat := fun s => match s with | .manager => some .fable | .implementer => none
    available := fun k r => !(k == 2 && r == .fable) }

/-- Round 2's Panel runs, without `fable`, and the exit takes its judge's place. -/
@[req "RUN-22"]
theorem manager_out_skips_judge :
    run Guards.all runsOut 3 =
      (.e2, [.pick, .implementer 1 true, .panel 1 .all Reviewer.all, .judge 1,
             .implementer 2 true, .panel 2 .all [.astra, .opus, .sol]]) := by decide

/-- With the guard off, Round 2's judge is called on a Manager's Seat recorded `unavailable`. -/
@[req "RUN-22"]
theorem judge_refusal_off_judges :
    ((run { Guards.all with judgeRefusal := false } runsOut 3).2.any (Spawn.isJudgeOf 2)) = true := by
  decide

/-! ## `RUN-12` — no decision -/

/-- A Manager that picks a brief and then never writes again. -/
def silent : Behaviour :=
  { restless with judge := fun _ => { ok := true, writesFinished := none, writesTask := none } }

@[req "RUN-12"]
theorem no_decision_ends :
    run Guards.all silent 5 = (.e2, [.pick, .implementer 1 true, .panel 1 .all Reviewer.all, .judge 1]) := by
  decide

/-- With the comparison off, the same Manager burns every Round on the same brief. -/
@[req "RUN-12"]
theorem no_decision_off_burns :
    implementers (run { Guards.all with noDecision := false } silent 5).2 = 5 := by decide

/-! ## `RUN-11` — the Finished File decides, and beats a rewritten brief -/

/-- A Manager that, at Round 2, both rewrites the brief and declares the task done. -/
def doneAndRewrite : Behaviour :=
  { restless with judge := fun k =>
      if k == 2 then { ok := true, writesFinished := some .done, writesTask := some 99 }
      else { ok := true, writesFinished := none, writesTask := some k } }

@[req "RUN-11"]
theorem finished_beats_rewrite :
    run Guards.all doneAndRewrite 5 =
      (.e0, [.pick, .implementer 1 true, .panel 1 .all Reviewer.all, .judge 1,
             .implementer 2 true, .panel 2 .all Reviewer.all, .judge 2]) := by decide

/-- A Manager that writes `done` but exits non-zero: the tool failed, the file is not believed. -/
def doneButFailed : Behaviour :=
  { restless with judge := fun _ => { ok := false, writesFinished := some .done, writesTask := none } }

@[req "RUN-11"]
theorem failed_manager_is_e2 :
    (run Guards.all doneButFailed 5).1 = .e2 := by decide

/-- Exit 0 comes only from a Manager call that exited 0 and wrote `done`: the pick, or some judge
call the trace holds. -/
theorem rounds_e0_from_done (g : Guards) (hg : g.checkpoint = true) (b : Behaviour) (m : Nat) :
    ∀ (fuel round : Nat) (d : Disk) (tr : List Spawn), d.leftover = none →
      (rounds g b m fuel round d tr).1 = .e0 →
      ∃ k, (rounds g b m fuel round d tr).2.any (Spawn.isJudgeOf k) = true ∧
        (b.judge k).ok = true ∧ (b.judge k).writesFinished = some .done := by
  intro fuel
  induction fuel with
  | zero => intro _ _ _ _ h; simp [rounds] at h
  | succ fuel ih =>
    intro round d tr hl
    simp only [rounds]
    split
    · simp
    · have hl2 : (applyInterference g (applyInterference g d (b.interference round .afterImplementer))
          (b.interference round .afterPanel)).leftover = none := by
        simp [applyInterference_leftover g hg, hl]
      split
      · simp
      · split
        · rename_i e h
          intro he
          simp at he
          subst he
          refine ⟨round, ?_, ?_⟩
          · simp [List.any_reverse, Spawn.isJudgeOf]
          · unfold decide at h
            simp only [hl2] at h
            repeat' split at h
            all_goals simp_all
        · intro he
          have hl3 : (afterManager (applyInterference g (applyInterference g d
              (b.interference round .afterImplementer)) (b.interference round .afterPanel))
              (b.judge round)).leftover = none := by
            simp [afterManager, hl2]
          exact ih _ _ _ hl3 he

/-- Exit 0 is earned by a `done` some Manager call wrote after exiting 0 — the pick's, or one of a
judge call in the trace. -/
@[req "RUN-11"]
theorem exit0_from_done (b : Behaviour) (m : Nat) :
    (run Guards.all b m).1 = .e0 →
      (b.pick.ok = true ∧ b.pick.writesFinished = some .done) ∨
      ∃ k, (run Guards.all b m).2.any (Spawn.isJudgeOf k) = true ∧
        (b.judge k).ok = true ∧ (b.judge k).writesFinished = some .done := by
  unfold run
  split
  · intro he; simp at he
  · split
    · rename_i e h
      intro he
      simp at he
      subst he
      left
      unfold decide at h
      repeat' split at h
      all_goals simp_all
    · intro he
      right
      exact rounds_e0_from_done Guards.all rfl b m _ _ _ _ rfl he

/-! ## `DIR-6`, `DIR-7` — the Checkpoint makes interference invisible -/

theorem rounds_quiet (b : Behaviour) (m : Nat) :
    ∀ (fuel round : Nat) (d : Disk) (tr : List Spawn),
      rounds Guards.all b m fuel round d tr = rounds Guards.all b.quiet m fuel round d tr := by
  intro fuel
  induction fuel with
  | zero => intro _ _ _; rfl
  | succ fuel ih =>
    intro round d tr
    simp only [rounds, applyInterference_all, Behaviour.quiet, seatAvailable_interference]
    split
    · rfl
    · split
      · rfl
      · split
        · rfl
        · exact ih _ _ _

/-- Whatever a non-Manager writes over the Manager's files, the Run's exit code and every spawn
are those of the Run with no interference at all. -/
@[req "DIR-6"]
theorem checkpoint_non_interference (b : Behaviour) (m : Nat) :
    run Guards.all b m = run Guards.all b.quiet m := by
  unfold run
  simp only [Behaviour.quiet, seatAvailable_interference]
  split
  · rfl
  · split
    · rfl
    · exact rounds_quiet b m _ _ _ _

/-- An Implementer that writes `STATUS: done` where the Manager's report goes, under a Manager that
never declares anything. -/
def forged : Behaviour :=
  { silent with interference := fun k p =>
      if k == 1 && p == .afterImplementer then .writeFinished .done else .none }

/-- With the Checkpoint off, the forged file ends the Run with exit 0 although no Manager call wrote
`done`. -/
@[req "DIR-6"]
theorem checkpoint_off_believes_forgery :
    (run { Guards.all with checkpoint := false } forged 5).1 = .e0 := by decide

/-- An Implementer that edits its brief (content `0` becomes `7`), under a Manager that then writes
nothing. -/
def ticked : Behaviour :=
  { silent with interference := fun k p =>
      if k == 1 && p == .afterImplementer then .editTask 7 else .none }

/-- With the Checkpoint on, the untouched brief plus a silent Manager is "no decision". -/
@[req "DIR-7"]
theorem ticked_is_no_decision :
    run Guards.all ticked 5 = (.e2, [.pick, .implementer 1 true, .panel 1 .all Reviewer.all, .judge 1]) := by
  decide

/-- With it off, the Implementer's edit reads as a Manager rewrite and a second Round runs. -/
@[req "RUN-12"]
theorem checkpoint_off_reads_edit_as_rewrite :
    implementers (run { Guards.all with checkpoint := false } ticked 5).2 = 2 := by decide

/-! ## `RUN-14` — an Implementer's failure alone ends nothing -/

theorem rounds_implementer_blind (g : Guards) (b : Behaviour) (f : Nat → Bool) (m : Nat) :
    ∀ (fuel round : Nat) (d : Disk) (tr tr' : List Spawn), implementers tr = implementers tr' →
      (rounds g b m fuel round d tr).1 = (rounds g { b with implementer := f } m fuel round d tr').1 ∧
      implementers (rounds g b m fuel round d tr).2 =
        implementers (rounds g { b with implementer := f } m fuel round d tr').2 := by
  intro fuel
  induction fuel with
  | zero => intro _ _ _ _ h; exact ⟨rfl, by simp [rounds, implementers_reverse, h]⟩
  | succ fuel ih =>
    intro round d tr tr' h
    simp only [rounds, seatAvailable_implementer]
    split
    · refine ⟨rfl, ?_⟩
      simp only [List.reverse_cons, implementers_append, implementers_reverse, h,
        implementers_one_implementer]
    · split
      · refine ⟨rfl, ?_⟩
        simp only [List.reverse_cons, implementers_append, implementers_reverse, h,
          implementers_one_implementer]
      · split
        · refine ⟨rfl, ?_⟩
          simp only [List.reverse_cons, implementers_append, implementers_reverse, h,
            implementers_one_implementer]
        · exact ih _ _ _ _ (by simp [implementers_cons_judge, implementers_cons_panel,
            implementers_cons_implementer, h])

/-- Replacing every Implementer outcome changes neither the exit code nor how many Implementers
ran: only the Manager ends a Run (`RUN-14`). -/
@[req "RUN-14"]
theorem implementer_failure_ends_nothing (b : Behaviour) (f : Nat → Bool) (m : Nat) :
    (run Guards.all b m).1 = (run Guards.all { b with implementer := f } m).1 ∧
    implementers (run Guards.all b m).2 = implementers (run Guards.all { b with implementer := f } m).2 := by
  unfold run
  simp only [seatAvailable_implementer]
  split
  · exact ⟨rfl, rfl⟩
  · split
    · exact ⟨rfl, rfl⟩
    · exact rounds_implementer_blind Guards.all b f m _ _ _ _ _ rfl

end Rloop
