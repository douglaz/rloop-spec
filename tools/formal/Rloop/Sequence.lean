import Rloop.Loop
/-! # The Sequence

`--auto` (`05-sequence.md`, `ADR-0004`): Runs one after another until the Manager finds nothing
left. Each Run is `Rloop.run`'s business; here a Run is abstracted to two facts the Sequence reads —
whether the tree was clean when it was about to start, and how it exited — and the model carries
only the rules between Runs. Git itself is not modelled: `clean` is a Bool the script supplies. -/

namespace Rloop

/-- What the Sequence learns of Run `n`: the tree's state before it, and its exit. -/
structure RunFacts where
  clean : Bool
  exit : Exit
  deriving DecidableEq, Repr

/-- The one guard between Runs: refuse to start on a tree that is not clean (`SEQ-4`). -/
structure SeqGuards where
  cleanCheck : Bool := true
  deriving DecidableEq, Repr

def SeqGuards.all : SeqGuards := {}

/-- What the Sequence did, in order: started Run `n`, or refused to. -/
inductive Step
  | started (n : Nat)
  | refused (n : Nat)
  deriving DecidableEq, Repr

/-- The Sequence's exit (`SEQ-6`): `idle` ends it with 0, `blocked` with 1, any failure or the
cap with 2. -/
def sequence (g : SeqGuards) (facts : Nat → RunFacts) (maxRuns : Nat) : Exit × List Step :=
  go maxRuns 1 []
where
  go : Nat → Nat → List Step → Exit × List Step
    | 0, _, trace => (.e2, trace.reverse)
    | fuel + 1, n, trace =>
      let f := facts n
      if g.cleanCheck && !f.clean then (.e2, (Step.refused n :: trace).reverse)
      else
        let trace := Step.started n :: trace
        match f.exit with
        | .e3 => (.e0, trace.reverse)
        | .e0 => go fuel (n + 1) trace
        | .e1 => (.e1, trace.reverse)
        | .e2 => (.e2, trace.reverse)

def Step.isStart : Step → Bool
  | .started _ => true
  | _ => false

def starts (t : List Step) : Nat := (t.filter Step.isStart).length

theorem starts_reverse (t : List Step) : starts t.reverse = starts t := by
  simp [starts, List.filter_reverse, List.length_reverse]

theorem starts_append (t u : List Step) : starts (t ++ u) = starts t + starts u := by
  simp [starts, List.filter_append, List.length_append]

theorem starts_cons_started (n : Nat) (t : List Step) : starts (.started n :: t) = starts t + 1 := by
  simp [starts, List.filter, Step.isStart]

theorem starts_one_started (n : Nat) : starts [.started n] = 1 := rfl
theorem starts_one_refused (n : Nat) : starts [.refused n] = 0 := rfl

/-! ## `SEQ-5` — the cap bounds the Runs -/

theorem go_starts_le (g : SeqGuards) (facts : Nat → RunFacts) :
    ∀ (fuel n : Nat) (tr : List Step),
      starts (sequence.go g facts fuel n tr).2 ≤ starts tr + fuel := by
  intro fuel
  induction fuel with
  | zero => intro _ _; simp [sequence.go, starts_reverse]
  | succ fuel ih =>
    intro n tr
    simp only [sequence.go]
    split
    · simp only [List.reverse_cons, starts_append, starts_reverse, starts_one_refused]; omega
    · split
      · simp only [List.reverse_cons, starts_append, starts_reverse, starts_one_started]; omega
      · have := ih (n + 1) (.started n :: tr)
        simp only [starts_cons_started] at this
        omega
      · simp only [List.reverse_cons, starts_append, starts_reverse, starts_one_started]; omega
      · simp only [List.reverse_cons, starts_append, starts_reverse, starts_one_started]; omega

@[req "SEQ-5"]
theorem starts_le_maxRuns (facts : Nat → RunFacts) (maxRuns : Nat) :
    starts (sequence SeqGuards.all facts maxRuns).2 ≤ maxRuns := by
  have := go_starts_le SeqGuards.all facts maxRuns 1 []
  simpa [sequence, starts] using this

/-! ## `SEQ-4` — no Run starts on a tree that is not clean -/

theorem go_started_clean (g : SeqGuards) (hg : g.cleanCheck = true) (facts : Nat → RunFacts) :
    ∀ (fuel n : Nat) (tr : List Step),
      (∀ k, Step.started k ∈ tr → (facts k).clean = true) →
      ∀ k, Step.started k ∈ (sequence.go g facts fuel n tr).2 → (facts k).clean = true := by
  intro fuel
  induction fuel with
  | zero => intro n tr h k hk; simp only [sequence.go, List.mem_reverse] at hk; exact h k hk
  | succ fuel ih =>
    intro n tr h k hk
    simp only [sequence.go] at hk
    split at hk
    · simp only [List.mem_reverse, List.mem_cons] at hk
      rcases hk with hk | hk
      · cases hk
      · exact h k hk
    · rename_i hc
      have hcn : (facts n).clean = true := by simpa [hg] using hc
      have h' : ∀ j, Step.started j ∈ (Step.started n :: tr) → (facts j).clean = true := by
        intro j hj
        simp only [List.mem_cons] at hj
        rcases hj with hj | hj
        · cases hj; exact hcn
        · exact h j hj
      split at hk
      · simp only [List.mem_reverse] at hk; exact h' k hk
      · exact ih (n + 1) _ h' k hk
      · simp only [List.mem_reverse] at hk; exact h' k hk
      · simp only [List.mem_reverse] at hk; exact h' k hk

@[req "SEQ-4"]
theorem started_means_clean (facts : Nat → RunFacts) (maxRuns k : Nat) :
    Step.started k ∈ (sequence SeqGuards.all facts maxRuns).2 → (facts k).clean = true :=
  go_started_clean SeqGuards.all rfl facts maxRuns 1 [] (by intro _ h; simp at h) k

/-- A first Run that ends `done` but leaves the tree dirty for the second. -/
def sloppy : Nat → RunFacts
  | 1 => { clean := true, exit := .e0 }
  | _ => { clean := false, exit := .e3 }

@[req "SEQ-4"]
theorem dirty_refused :
    sequence SeqGuards.all sloppy 5 = (.e2, [.started 1, .refused 2]) := by decide

/-- With the check off, Run 2 starts over Run 1's leftovers and the Sequence ends 0 anyway. -/
@[req "SEQ-4"]
theorem clean_check_off_starts_dirty :
    sequence { cleanCheck := false } sloppy 5 = (.e0, [.started 1, .started 2]) := by decide

/-! ## `SEQ-6` — exit 0 means every Run was done and the last was idle; nothing follows blocked -/

/-- The Runs started, in order, with their exits. -/
def exits (facts : Nat → RunFacts) (t : List Step) : List Exit :=
  t.filterMap fun s => match s with
    | .started n => some (facts n).exit
    | .refused _ => none

theorem exits_reverse_cons (facts : Nat → RunFacts) (s : Step) (tr : List Step) :
    exits facts (s :: tr).reverse = exits facts tr.reverse ++ exits facts [s] := by
  simp [exits, List.reverse_cons, List.filterMap_append]

theorem mem_exits_reverse (facts : Nat → RunFacts) (tr : List Step) (e : Exit) :
    e ∈ exits facts tr.reverse ↔ e ∈ exits facts tr := by
  simp [exits, List.filterMap_reverse, List.mem_reverse]

theorem go_exit0 (g : SeqGuards) (facts : Nat → RunFacts) :
    ∀ (fuel n : Nat) (tr : List Step),
      (∀ e, e ∈ exits facts tr → e = .e0) →
      (sequence.go g facts fuel n tr).1 = .e0 →
      ∃ pre, exits facts (sequence.go g facts fuel n tr).2 = pre ++ [.e3] ∧
        ∀ e, e ∈ pre → e = .e0 := by
  intro fuel
  induction fuel with
  | zero => intro _ _ _ h; simp [sequence.go] at h
  | succ fuel ih =>
    intro n tr hall he
    simp only [sequence.go] at he ⊢
    split at he
    · simp at he
    · rename_i hc
      simp only [hc, Bool.false_eq_true, ↓reduceIte]
      split at he
      · rename_i hx
        refine ⟨exits facts tr.reverse, ?_, ?_⟩
        · rw [exits_reverse_cons]; simp [exits, hx]
        · intro e hee; exact hall e ((mem_exits_reverse facts tr e).1 hee)
      · rename_i hx
        have hall' : ∀ e, e ∈ exits facts (.started n :: tr) → e = .e0 := by
          intro e hee
          simp only [exits, List.filterMap_cons, hx] at hee
          simp only [List.mem_cons] at hee
          rcases hee with hee | hee
          · exact hee
          · exact hall e (by simpa [exits] using hee)
        exact ih (n + 1) _ hall' he
      · simp at he
      · simp at he

@[req "SEQ-6"]
theorem exit0_means_all_done_then_idle (facts : Nat → RunFacts) (maxRuns : Nat) :
    (sequence SeqGuards.all facts maxRuns).1 = .e0 →
      ∃ pre, exits facts (sequence SeqGuards.all facts maxRuns).2 = pre ++ [.e3] ∧
        ∀ e, e ∈ pre → e = .e0 :=
  go_exit0 SeqGuards.all facts maxRuns 1 [] (by intro _ h; simp [exits] at h)

/-- A Sequence whose second Run blocks and whose third would be idle: it never starts. -/
def stuck : Nat → RunFacts
  | 2 => { clean := true, exit := .e1 }
  | _ => { clean := true, exit := .e0 }

@[req "SEQ-6"]
theorem blocked_stops :
    sequence SeqGuards.all stuck 5 = (.e1, [.started 1, .started 2]) := by decide

end Rloop
