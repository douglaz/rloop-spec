# The Manager commits accepted work, and rloop only checks the tree is clean

**Status:** accepted (2026-09-17, after reviews by Opus and gpt-6-astra, both "adopt with changes")

In a Sequence the second Run records `BASE = HEAD` over a tree still holding the first Run's
uncommitted work, so its Panel reviews both tasks, and a blocked Run mixes accepted and unaccepted
changes. Someone has to put accepted work into history between Runs. rloop does not: a tool that
commits knows nothing of a repository's conventions, signing or hooks, and its predecessor refused
to write history for that reason. The Manager does, because it has read the repository's
instructions, is the only agent that knows the work was accepted, and is already doing the tracker's
bookkeeping at that moment.

The rule is a post-condition, not an action: when the Manager writes `STATUS: done`, the accepted
work is in history and the tree is clean. Where the Implementer already committed, the Manager
commits only what remains; it never squashes, rewrites or makes an empty commit. A hook failure that
needs a code change is a finding like any other and goes back through a Round; the Manager never
edits code to get a commit through, never bypasses a hook or signing, and adds no tool or assistant
attribution. rloop's part is one check: before every Run of a Sequence, the first included, a tree
that is not clean is exit 2 and no Manager is spawned. `--auto` with `--base` is a usage error — one
asks for a task's diff per Run, the other for the accumulated branch.

## The hole this leaves, stated rather than closed

An Implementer may commit (the repository's instructions decide), so a blocked or capped Run can
leave unaccepted commits behind a clean tree, and the next invocation's `BASE = HEAD` swallows them
unreviewed. Closing it needs rollback, which rloop will not have. Every Finished File therefore
reports the HEAD the Run started from, the HEAD it ended on, the review base, and what is committed
versus in the tree; reconciling after an unsuccessful Run is the caller's.

## Considered options

- **rloop snapshots the tree as the base** (`git stash create`, `write-tree`). Git plumbing in every
  Implementation, the blocked-Run mixing remains, and nothing is ever committed.
- **rloop commits `run N`.** Rejected above.
- **Tell Reviewers to focus.** The noise compounds with every Run.
- **Per-Run branches, or Implementer commits and Manager squashes.** Both bring branch and rollback
  semantics into the tool. Branches, pushes and pull requests are the caller's, and there is no
  `--branch` flag: the caller checks out a branch before starting a Sequence.
- **Exit 2 when a lone Run ends done on a dirty tree** (astra). A warning instead (Opus): nothing
  downstream of a lone Run depends on it.
