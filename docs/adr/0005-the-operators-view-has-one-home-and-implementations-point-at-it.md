# The operator's view has one home and Implementations point at it

**Status:** accepted (2026-09-21)

`README.md`'s *Using rloop* tells whoever runs an Implementation what a Run does, what each exit
status means and what a Run that blocked or failed leaves behind. `rloop-bash` grew its own copy of
that section — six bullets, thirty-nine of forty-two lines identical — and within two days the copy
had diverged four ways: three citations dropped and the Consultation sentence rewritten into a
third, narrower paraphrase of `RUN-20`. Its own `AGENTS.md` had forbidden this from the first
commit, and forbidding it stopped nothing.

Two alternatives were rejected. Narrowing each Implementation's `AGENTS.md` to permit
operator-observable description keeps a hand-kept fork per Implementation, and the argument for it —
that an operator should not have to read eleven documents — is answered by a section that already
exists and is already written for that reader. Moving the section out of the Specification and
making it each Implementation's own was rejected for the same reason in reverse: what it describes
is behaviour every conforming Implementation must have, so it belongs where that behaviour is
specified.

So this Specification's `README.md` owns the operator's view, and an Implementation's `README.md`
covers only what it alone owns — how to build it, how to invoke it, what it needs on `PATH` — and
links here for the rest.

## Consequences

- That section may state a rule it does not own, in observational terms, but every bullet cites at
  least one requirement, so a reader and a gate can both reach the owner. `RUN-10`, `RUN-19` and
  `SEQ-6` were added for the three bullets that cited nothing.
- An Implementation links the absolute URL, not the submodule path: GitHub does not serve files
  inside a submodule, so `spec/README.md` renders as a dead link on the repository page.
- A future Implementation in another language copies the pointer, not the prose.
