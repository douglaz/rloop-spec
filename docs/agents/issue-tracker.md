# Issue tracker: beads (`br`), with GitHub Issues as intake

Work is tracked in beads: local-first under `.beads/`, committed with the specifications, issue
prefix `rl`. An rloop Run's Manager picks from it, so an open bead is a ready task unless its body
says otherwise.

GitHub Issues on `douglaz/rloop-spec` are the intake: a raw report, written before anyone has
decided what to do about it. `/triage` reads them and ends each one in beads, in a pointer to
where it was already done, or in a recorded rejection. Nothing else works from them.

## Beads

- **Create**: `br create --title "..." --type task --priority N --description-file <path>`, plus
  `--external-ref gh-<N>` when it came from GitHub issue N.
- **Read**: `br show <id>` (`--json` for fields).
- **List**: `br list --status open --json`. What a Run would pick: `br ready --json`.
- **Comment**: `br comments add <id> --file <path>`.
- **Labels**: `br label add <id> --label <label>` / `br label remove <id> --label <label>`.
- **Close**: `br close <id> --reason "..."`.
- Never hand-edit `.beads/issues.jsonl`. Run `br sync --flush-only`, then commit `.beads/` with the
  change it belongs to.

## GitHub intake

- **List**: `gh issue list --state open --json number,title,body,labels,comments`.
- **Read**: `gh issue view <N> --json title,body,comments`. `--comments` alone prints the comments
  and not the body.
- **Comment**: `gh issue comment <N> --body-file <path>`.
- **Close**: `gh issue close <N> --reason completed|"not planned" --comment "..."`. That is one
  event, so watchers get one notification.
- **Close at conversion.** Once an issue's work is in beads, close it `completed` with a comment
  naming the bead ids. From then on the bead is the only home.

**PRs as a request surface: no.**

## When a skill says "publish to the issue tracker"

Create a bead.

## When a skill says "fetch the relevant ticket"

For an `rl-…` id, run `br show <id>`. For a `#N`, run `gh issue view <N> --json title,body,comments`.
