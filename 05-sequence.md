# 05 — The Sequence

`--auto` runs Runs one after another until the Manager finds nothing left to pick. A Run in a
Sequence is exactly `01-run-lifecycle.md`'s Run; this document is only the rules between Runs.
`ADR-0004` is the decision on who commits between them.

## Shape

**SEQ-1** With `--auto`, rloop MUST perform Runs in order, `1, 2, 3, …`, each a complete Run with
its own Manager session (a fresh id, never a resume of an earlier Run's), its own Run Directory
(`DIR-2`), and its own Finished File. *A Manager carried across tasks judges its eighth task with
seven tasks of logs in its context; the repository and the tracker are what carry over, and the
Manager was always meant to read those.*

**SEQ-2** The caller's instruction, if any, MUST be rendered into every Run's pick prompt
unchanged. *An instruction naming one task — "implement br-42" — ends the Sequence cleanly: the
second Run finds it done and goes idle. No special case.*

**SEQ-3** `--auto` MUST be a usage error (exit 2, nothing spawned) together with `--base` or with
`--run-dir`. *`--base` asks for a review of the accumulated branch; a Sequence asks for one task's
diff per Run; the two contradict. `--run-dir` names one directory and a Sequence needs one per
Run.*

## Between Runs

**SEQ-4** Before every Run of a Sequence, the first included, rloop MUST run `git status
--porcelain` and, when it prints anything, exit 2 without starting the Run. `.rloop/` is ignored
(`DIR-2`) and so never counts. *This is the one mechanical check that replaces a promise: the
Manager's `SEQ-8` obligation to leave the tree clean at `done` is enforced by the next Run refusing
to start otherwise, and a Run that ended blocked, hit its cap or failed stops the Sequence through
this rule rather than three special cases.* `Rloop.started_means_clean` proves no Run starts on a
tree the check found dirty; `Rloop.clean_check_off_starts_dirty` is the Sequence that starts Run 2
over Run 1's leftovers without it.

**SEQ-5** `--max-runs N` (default 20) MUST bound the Runs of a Sequence; reaching it MUST exit 2.
`Rloop.starts_le_maxRuns` proves the bound. *Without a cap "the Sequence ends" is not a theorem,
and a Manager that always finds one more thing to polish never goes idle.*

**SEQ-6** A Sequence's exit status MUST be decided by its Runs' outcomes in order, stopping at the
first that ends it:

| Run `n` ended | Sequence |
|---|---|
| idle (exit 3) | **ends, exit 0** — everything was drained |
| done (exit 0) | Run `n + 1` starts (subject to `SEQ-4`, `SEQ-5`) |
| blocked (exit 1) | **ends, exit 1** — a human is needed; the Sequence does not skip ahead |
| exit 2 | **ends, exit 2** |

`Rloop.exit0_means_all_done_then_idle` proves exit 0 means every Run ended done and the last ended
idle; `Rloop.blocked_stops` shows nothing follows a blocked Run.

**SEQ-7** Standard output of a Sequence MUST be, for every Run that ended 0, 1 or 3, a line
`== run <n> ==` followed by that Run's Finished File, in order, and nothing else. A Run that ended
2 prints nothing, as `RUN-10` says of a lone one. Standard error carries progress.

## Committing

**SEQ-8** The judge prompt (`PRM-2`) MUST state, and the Manager is held to, this post-condition:
*when it writes `STATUS: done`, the accepted work is in history and the tree is clean.* Where the
Implementer already committed, the Manager commits what remains, the tracker's files included; it
never squashes, rewrites or makes an empty commit. A hook failure that needs a code change is a
finding like any other and goes back through a Round; the Manager never edits code to get a
commit through, never bypasses a hook or signing, follows the repository's commit conventions, and
adds no tool or assistant attribution. On `blocked` it commits nothing it did not accept and says
in the report what is committed and what is in the tree. rloop enforces none of this directly —
`SEQ-4` is the check — and a lone Run that ends done on a dirty tree SHOULD get a warning on
standard error and nothing more.

**SEQ-9** rloop MUST NOT create, switch or push branches. The caller checks out the branch a
Sequence should commit to before starting it; the `README.md` says so. *`ADR-0004` rejected
per-Run branches and a `--branch` flag: branches, pushes and pull requests belong to whoever calls
rloop.*

**SEQ-10** The hole `ADR-0004` leaves open MUST be stated in the `README.md`: an Implementer may
commit during a Run that then ends blocked or capped, leaving unaccepted commits behind a clean
tree, and the next invocation's base (`RUN-2`) takes them in unreviewed. Every Finished File
therefore reports the base, the `HEAD` the Run ended on, and what is committed versus in the tree
(`PRM-2`), and reconciling after an unsuccessful Run is the caller's.
