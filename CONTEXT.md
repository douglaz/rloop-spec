# rloop

A loop that lets one long-lived judging agent drive disposable working agents through a single task in a git repository. This repository is its **Specification**; it holds no **Implementation**.

## Language

### The specification set

**Specification**:
This repository: the language-neutral requirements for rloop, the **Conformance Suite** that tests them, and the formal model that checks them.
_Avoid_: Docs, design

**Implementation**:
A program that satisfies the **Specification**, living in its own repository that pins the Specification at one revision. Many may exist, one per language.
_Avoid_: Port, reference implementation

**Conformance Suite**:
The executable, black-box tests the **Specification** ships, run against any **Implementation** regardless of its language.
_Avoid_: Test suite, smoke test, checklist

**Scenario**:
One scripted behaviour of every agent for one **Run**, with the exit code and spawn order the **Specification**'s model gives it; the **Conformance Suite** replays it with fake agents.
_Avoid_: Test case, vector

### The loop

**Manager**:
The one agent whose conversation survives the whole **Run**; it picks the task, judges each **Round**, and decides when the Run is over.
_Avoid_: Orchestrator, planner, supervisor

**Implementer**:
A disposable agent that changes the repository to satisfy the **Task File**. A fresh one is used every **Round**.
_Avoid_: Worker, coder

**Reviewer**:
A disposable agent that judges the repository's changes against the **Task File** and must not modify anything. Reviewers never talk to the **Implementer**; only the **Manager** reads them.
_Avoid_: Critic, checker

**Panel**:
The set of **Reviewers**, each a different model, run side by side in one **Round**.

**Feedback File**:
One **Reviewer**'s findings for one **Round**, written for the **Manager**.
_Avoid_: Review, findings file

**Clarification**:
A change to the repository's specifications or instructions that only their owner can make. A task that needs one ends its **Run** blocked; the **Manager** never chooses a reading.
_Avoid_: Assumption, interpretation

**Consultation**:
The **Manager** putting an implementation decision the specifications leave open to advisers before settling it in the **Task File**, and recording what each one said. How many must answer, who they are, and what happens when they do not, is `RUN-20`'s. Not a **Panel**: the Manager runs it, rloop does not.
_Avoid_: Design review, second opinion

**Task File**:
The **Manager**'s written brief for the current **Round**: what to implement, precise enough for an independent **Implementer** to build and independent reviewers to judge against. The Manager rewrites it to start another Round.
_Avoid_: Spec, prompt, plan

**Finished File**:
The **Manager**'s closing report, whose existence ends the **Run**. It declares the Run done, blocked or **Idle** and carries notes and questions for whoever started the Run.
_Avoid_: Report, result, summary

**Run Directory**:
The directory holding everything one **Run** wrote: the **Task File**, each **Round**'s brief, the **Feedback Files**, agent logs and the **Finished File**. One per Run, never reused.
_Avoid_: Workdir, state dir, temp dir

**Checkpoint**:
The point, after the **Implementer** and again after the **Panel**, where rloop puts the **Manager**'s files back as the Manager left them and sets aside whatever a non-Manager wrote over them.
_Avoid_: Guard, validation, integrity check

**Interference**:
A non-**Manager** agent writing to the **Task File** or **Finished File**. Assumed to be a mistake, never an attack.
_Avoid_: Tampering, attack

**Run**:
One task, from the **Manager** picking it to the Manager declaring it finished.

**Sequence**:
**Runs** made one after another by a single invocation until the **Manager** finds nothing left to pick. Each Run in it is independent: its own Manager, its own **Run Directory**, its own **Finished File**.
_Avoid_: Drain, batch, session, auto mode

**Idle**:
The outcome of a **Run** whose **Manager** found no task to pick and changed nothing. Distinct from done, and only possible before the first **Round**.
_Avoid_: Empty, nothing-to-do, no-op

**Round**:
One pass of **Implementer** → **Panel** → **Manager** judgment within a **Run**.
_Avoid_: Iteration, cycle

**Base**:
The commit a **Run**'s **Reviewers** diff against, fixed once when the Run starts.
_Avoid_: Baseline (that word is the **Task File** snapshot's), origin

## Example dialogue

**Dev:** So when the reviewers find a problem, rloop sends it back to the implementer?

**Expert:** No. rloop never reads a Reviewer. The Panel's Feedback Files go to the Manager, and only the Manager decides whether another Round is needed. If it is, it rewrites the Task File and rloop starts a fresh Implementer on it.

**Dev:** Fresh — the same one, resumed?

**Expert:** Fresh. Implementers and Reviewers are disposable; the Manager is the one conversation that lasts the whole Run.

**Dev:** And the implementer ticked the checkboxes in the brief, so the reviewers reviewed against a changed brief.

**Expert:** That is Interference, and the Checkpoint undid it before the Panel ran: the brief Round 2 ran against is `task-2.md`, and what the Implementer wrote over it is `rejected-2-task.md`. Nobody calls that tampering here; the threat model is a mistake, not an attack.

**Dev:** The spec says "the file is written" but not whether it's overwritten or appended. Can't the Manager just pick one?

**Expert:** No. Two readings, two behaviours: that is a Clarification, and the Run ends blocked with the passage and the recommendation in the report. Had the spec said nothing at all about it — a matter of how, not what — the Manager would hold a Consultation with two advisers and record the choice in the brief.

**Dev:** Then the Run ended with exit 3 — is that a failure?

**Expert:** Idle. The Manager found nothing to pick and changed nothing. A Sequence treats it as "drained", exit 0; a lone Run reports it as 3 so a caller's loop can stop.
