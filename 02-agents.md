# 02 — Agents

How rloop is invoked, how it invokes each agent, and what every agent process is given. The
command lines here are verbatim requirements: an Implementation reproduces them argument for
argument, and the Conformance Suite's fakes record what they received and compare (`ADR-0001`).

## rloop's own command line

**AGT-1** An Implementation MUST accept exactly this invocation:

```text
rloop [OPTIONS] [INSTRUCTION]

  --auto                       run a Sequence (05-sequence.md) instead of one Run
  --manager claude|codex       which Manager preset the pick and judges use   (default: claude)
  --implementer claude|codex   which Implementer preset a Round uses          (default: claude)
  --manager-model MODEL        the Manager's model                       (default: the preset's, AGT-3)
  --implementer-model MODEL    the Implementer's model                   (default: the preset's, AGT-5)
  --base REF                   the ref Reviewers diff against                  (default: HEAD at start)
  --run-dir PATH               the Run Directory, which must not exist yet     (default: DIR-2)
  --max-rounds N               Rounds per Run                                  (default: 10)
  --max-runs N                 Runs per Sequence                               (default: 20)
  --manager-timeout SECONDS    per Manager call                                (default: 3600)
  --implementer-timeout SECONDS  per Implementer call                          (default: 14400)
  --reviewer-timeout SECONDS   per Reviewer call                               (default: 1800)
  --probe-timeout SECONDS      the availability probe's bound (RUN-21)         (default: 60)
  --kill-after SECONDS         SIGTERM-to-SIGKILL grace                        (default: 10)
  --version                    print the Implementation's version and exit 0
  --help                       print this usage and exit 0
```

`INSTRUCTION` is one argument, free text, rendered into the Manager's pick prompt (`PRM-1`);
absent, the Manager picks on its own. Long options MAY also be given as `--flag=value`. There are
no environment-variable equivalents and no configuration file.

**AGT-2** An unknown option, a missing or non-numeric value, a value outside the set a preset
flag names — `--manager` and `--implementer` each take `claude` or `codex` and nothing else — a
number below 1 for `--max-rounds` or `--max-runs` or below 0 for a timeout, more than one
`INSTRUCTION`, or a combination `SEQ-3` forbids MUST exit 2 with a message on standard error and
nothing spawned. *A usage error found after the first agent call has already spent money.*
*The preset clause is stated here from 2026-09-20 with `--manager`; it was always true of
`--implementer`, which named its two values in `AGT-1` and nowhere said what a third does.*

## The agent command lines

Each is written as an argument list; `<angle brackets>` are values rloop supplies and everything
else is literal, including the order. A prompt is one argument, however many lines it holds, and
a `"double-quoted"` span is one argument however many spaces it holds — the quotes mark the
argument's extent and are not part of it.

**AGT-3** The pick MUST be, with `--manager claude`:

```text
claude -p <pick prompt> --session-id <session id> --model <manager model> --effort high --dangerously-skip-permissions
```

and with `--manager codex`:

```text
codex exec --json --dangerously-bypass-approvals-and-sandbox -m <manager model> -c model_reasoning_effort=high <pick prompt>
```

`<manager model>` is `--manager-model`'s value, which defaults to `claude-fable-5-1` under
`--manager claude` and to `gpt-6-astra` under `--manager codex`. The two presets reach their
`<session id>` differently and `RUN-16` owns that rule: under `claude` it is a UUID rloop
generated for this Run before the call, under `codex` it is the id the call reports. Either way
rloop writes it to the Run Directory's `session` file (`DIR-4`).

*The codex Manager was added 2026-09-20, after the claude account behind `claude-fable-5-1` hit
its quota mid-Run and a Manager-seat evaluation of `gpt-6-astra` on the `PRM-1` prompt picked a
task off the frontier, claimed it, ran the repository's gates and blocked on a genuine
specification ambiguity rather than choosing a reading (`F9`). Nothing ever required the Manager
to be one vendor's CLI; `AGT-3` and `AGT-4` simply named one.*

*Why `--json` on the pick and not elsewhere: codex has no flag that sets a session id, so the id
can only be learnt from the call that mints it. `--json` makes the first line of standard output
`{"type":"thread.started","thread_id":"<uuid>"}`, a structured contract rloop can read and the
suite can fix; the human-readable banner carries the same id on standard error, but a banner is
cosmetic and a specification that matched one would break on a cosmetic change. The cost is that
`manager-pick.out` holds JSONL under this preset, with the Manager's own words inside the
`agent_message` items. The judge call needs no id back, so it stays prose.*

**AGT-4** The judge call MUST be, with `--manager claude`:

```text
claude -p <judge prompt> --resume <session id> --model <manager model> --effort high --dangerously-skip-permissions
```

and with `--manager codex`:

```text
codex exec resume --dangerously-bypass-approvals-and-sandbox -m <manager model> -c model_reasoning_effort=high <session id> <judge prompt>
```

with the pick's `<session id>` either way. *Resuming is what makes the Manager one conversation:
it judges Round 3 remembering why it wrote Round 2's brief.*

**AGT-5** The Implementer, with `--implementer claude`, MUST be:

```text
claude -p <implementer prompt> --model <implementer model> --dangerously-skip-permissions
```

`<implementer model>` is `--implementer-model`'s value, which defaults to `claude-fable-5-1` under
`--implementer claude` and to `gpt-6-astra` under `--implementer codex`, the same defaults `AGT-3`
gives the Manager.

**AGT-6** The Implementer, with `--implementer codex`, MUST be:

```text
codex exec --dangerously-bypass-approvals-and-sandbox -m <implementer model> <implementer prompt>
```

with `<implementer model>` as `AGT-5` gives it.

*Both run with permissions bypassed: writing is the Implementer's job, and codex's workspace
sandbox blocks the network and `.git`, which breaks `nix`, `cargo fetch` and commits. Until
2026-09-22 neither line carried a model flag and the CLI's configured default was the
Implementer's model; that day `ADR-0008` needed every Seat to have a model rloop can name, and a
Seat filled by a CLI's configured default is one rloop cannot Probe. The cost is live: an operator
whose `claude` default is not `claude-fable-5-1`, or whose `codex` default is not `gpt-6-astra`,
now gets that model unless they pass `--implementer-model`.*

**AGT-7** Reviewer `fable` MUST be:

```text
claude -p <review prompt> --model claude-fable-5-1 --effort high --dangerously-skip-permissions --disallowedTools "Edit,Write,NotebookEdit,Bash(git checkout:*),Bash(git stash:*),Bash(git reset:*),Bash(git commit:*),Bash(git clean:*)"
```

**AGT-8** Reviewer `opus` MUST be:

```text
claude -p <review prompt> --model claude-opus-5 --effort xhigh --dangerously-skip-permissions --disallowedTools "Edit,Write,NotebookEdit,Bash(git checkout:*),Bash(git stash:*),Bash(git reset:*),Bash(git commit:*),Bash(git clean:*)"
```

**AGT-9** The deny list in `AGT-7` and `AGT-8` is one argument — the quotes above mark it, and
`Bash(git checkout:*)` holds a space that must not split it. It holds because
`--disallowedTools` is honoured under `--dangerously-skip-permissions` — verified on Claude Code
2.1.274: a run under both flags asked to `Write` a file answered `DENIED` and wrote nothing, and one
asked to `git commit` was denied while `git status` ran. *The Reviewers keep a shell so they can
run the tests; what they lose is every way to edit the tree or move history. This is the
harness's enforcement, and rb-lite's no-shell-plus-diff-file is what it replaces.*

**AGT-10** Reviewer `astra` MUST be:

```text
codex exec --dangerously-bypass-approvals-and-sandbox -m gpt-6-astra -c model_reasoning_effort=high <review prompt>
```

and Reviewer `sol` MUST be:

```text
codex exec --dangerously-bypass-approvals-and-sandbox -m gpt-5.6-sol -c model_reasoning_effort=xhigh <review prompt>
```

*`codex review --base` cannot take a prompt (codex 0.153.4 refuses the combination), and the
Reviewer must read the brief. Until 2026-09-19 these ran under `-s read-only`; that sandbox cannot
reach the nix daemon socket or create a temporary file outside the workspace (reproduced: `nix
develop` fails with `cannot connect to socket … Operation not permitted`), so on a nix-based
repository a codex Reviewer could inspect but never run a gate or the Conformance Suite, and its
"verified" meant less than a claude Reviewer's (rloop-bash#1). The sandbox is now bypassed, as
for the claude Reviewers; what keeps a codex Reviewer from writing is `PRM-4`'s instruction alone,
since codex has no deny list, which is within `DIR-9`'s threat model. The `-c` value is passed
without quotes: codex parses it as TOML and, failing that,
takes the raw string, and `xhigh` was echoed back as `reasoning effort: xhigh` on 0.153.4.*

**AGT-11** The Panel MUST be exactly the four Reviewers `AGT-7`, `AGT-8` and `AGT-10` name, with
the Feedback File names `DIR-4` gives them. There is no flag, file or variable that changes the
Panel; changing it is a change to this document.

## What every agent process is given

**AGT-12** Every agent process, and the **Probe** (`AGT-18`), MUST be started with standard input
from the null device. *A CLI
that finds stdin open may wait on it until its timeout kills it; codex 0.153.4 did, for 25
minutes, during this Specification's own review.*

**AGT-13** Every agent process, and the **Probe** (`AGT-18`), MUST be started with the git toplevel as its working directory,
its standard output to the file `DIR-4` names for it and its standard error to the matching
`.err` file, and the environment rloop itself received plus exactly these variables:

| variable | value |
|---|---|
| `RLOOP_ROLE` | `manager`, `implementer`, `reviewer` or `probe` |
| `RLOOP_ROUND` | the Round number; `0` for the pick |
| `RLOOP_RUN` | the Run's number within its Sequence; `1` for a lone Run |
| `RLOOP_RUN_DIR` | the Run Directory's absolute path |
| `RLOOP_REVIEWER` | `fable`, `opus`, `astra` or `sol`; set for Reviewers only |

*Real agents ignore these — the prompt tells a model where things are. The Conformance Suite's
fakes read them to find their scripted part, which is what makes the suite independent of prompt
wording and CLI flags (`06-conformance.md`).*

**AGT-14** Every agent call MUST be bounded by its role's timeout, and the **Probe**'s (`AGT-18`)
by `--probe-timeout` (`AGT-1`). At the limit rloop
MUST send SIGTERM to that process group, wait `--kill-after` seconds, then send SIGKILL to
the group, and treat the call as exited non-zero. A timeout is then whatever a failure of that
role is: judged by the Manager for an Implementer (`RUN-14`), a failure note for a Reviewer
(`RUN-15`), exit 2 for the Manager (`RUN-11`). *The group, not the PID: both CLIs fork tool
subprocesses, and a killed parent leaves them orphaned and still writing.*

**AGT-15** rloop MUST NOT exit while any agent process it started, or the **Probe** (`AGT-18`), is
running. On SIGINT or SIGTERM it MUST send SIGTERM to every live group, wait for them (with `--kill-after`, then
SIGKILL), and exit 2 with `interrupted` on standard error. A second SIGINT during that wait MUST
send SIGKILL at once. The Run Directory is left as it is (`RUN-17`).

**AGT-16** Each agent process, and the **Probe** (`AGT-18`), MUST be started in its own process group, so that `AGT-14` and
`AGT-15` reach every descendant. A new session (`setsid`) satisfies this; so does what
`timeout` does for the command it runs.

## The availability probe

**AGT-18** The availability probe (`RUN-21`) MUST be:

```text
claude -p "/usage"
```

It is a **Probe** (`CONTEXT.md`), not an agent: no prompt is rendered into it, no Feedback File
comes out of it, and it takes no part in the spawn trace the Conformance Suite compares (`CNF-3`).
One invocation covers both claude Reviewers, because it reports every claude family at once and
answers even through a model that is itself exhausted. There is no codex command line here;
`RUN-21` says what follows from that.

`AGT-12` through `AGT-16` each name the **Probe** beside every agent process, so it is started,
bounded and killed by those rules rather than by anything stated here. *Everything they exist to
prevent, a Probe can do too: the 25-minute stdin hang `AGT-12` records was a CLI, not a role.*

## Versions

**AGT-17** The command lines above were verified against Claude Code 2.1.274 and codex 0.153.4 on
2026-09-17/18, and `AGT-18` together with the `Current week (<family>): <n>% used` line `RUN-21`
reads against Claude Code 2.1.278 on 2026-09-21. A fake agent accepts any flag, so the Conformance
Suite cannot tell a wrong flag from a right one; a flag that a newer CLI rejects is found only by a
live Run, and `06-conformance.md` carries the item that says so. The probe's output format is the
same class of exposure and is not a new one: between 2026-09-20 and 2026-09-21 the reset time in
that line moved from `2:59pm` to `3pm` without the percentage changing, which is why `RUN-21` reads
the family and the percentage and nothing else — and why a format that drifts past it degrades to
`unknown`, not to a smaller Panel.
