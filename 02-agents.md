# 02 — Agents

How rloop is invoked, how it invokes each agent, and what every agent process is given. The
command lines here are verbatim requirements: an Implementation reproduces them argument for
argument, and the Conformance Suite's fakes record what they received and compare (`ADR-0001`).

## rloop's own command line

**AGT-1** An Implementation MUST accept exactly this invocation:

```text
rloop [OPTIONS] [INSTRUCTION]

  --auto                       run a Sequence (05-sequence.md) instead of one Run
  --implementer claude|codex   which Implementer preset a Round uses          (default: claude)
  --manager-model MODEL        the Manager's model                             (default: claude-fable-5-1)
  --base REF                   the ref Reviewers diff against                  (default: HEAD at start)
  --run-dir PATH               the Run Directory, which must not exist yet     (default: DIR-2)
  --max-rounds N               Rounds per Run                                  (default: 10)
  --max-runs N                 Runs per Sequence                               (default: 20)
  --manager-timeout SECONDS    per Manager call                                (default: 3600)
  --implementer-timeout SECONDS  per Implementer call                          (default: 14400)
  --reviewer-timeout SECONDS   per Reviewer call                               (default: 1800)
  --kill-after SECONDS         SIGTERM-to-SIGKILL grace                        (default: 10)
  --version                    print the Implementation's version and exit 0
  --help                       print this usage and exit 0
```

`INSTRUCTION` is one argument, free text, rendered into the Manager's pick prompt (`PRM-1`);
absent, the Manager picks on its own. Long options MAY also be given as `--flag=value`. There are
no environment-variable equivalents and no configuration file.

**AGT-2** An unknown option, a missing or non-numeric value, a number below 1 for `--max-rounds`
or `--max-runs` or below 0 for a timeout, more than one `INSTRUCTION`, or a combination `SEQ-3`
forbids MUST exit 2 with a message on standard error and nothing spawned. *A usage error found
after the first agent call has already spent money.*

## The agent command lines

Each is written as an argument list; `<angle brackets>` are values rloop supplies and everything
else is literal, including the order. A prompt is one argument, however many lines it holds.

**AGT-3** The pick MUST be:

```text
claude -p <pick prompt> --session-id <session id> --model <manager model> --effort high --dangerously-skip-permissions
```

where `<session id>` is a UUID rloop generated for this Run and also wrote to the Run Directory's
`session` file (`DIR-4`), and `<manager model>` is `--manager-model`'s value.

**AGT-4** The judge call MUST be:

```text
claude -p <judge prompt> --resume <session id> --model <manager model> --effort high --dangerously-skip-permissions
```

with the pick's `<session id>`. *`--resume` is what makes the Manager one conversation: it judges
Round 3 remembering why it wrote Round 2's brief.*

**AGT-5** The Implementer, with `--implementer claude`, MUST be:

```text
claude -p <implementer prompt> --dangerously-skip-permissions
```

**AGT-6** The Implementer, with `--implementer codex`, MUST be:

```text
codex exec --dangerously-bypass-approvals-and-sandbox <implementer prompt>
```

*Both run with permissions bypassed: writing is the Implementer's job, and codex's workspace
sandbox blocks the network and `.git`, which breaks `nix`, `cargo fetch` and commits. Neither
carries a model flag: the CLI's configured default is the Implementer's model.*

**AGT-7** Reviewer `fable` MUST be:

```text
claude -p <review prompt> --model claude-fable-5-1 --effort high --dangerously-skip-permissions --disallowedTools Edit,Write,NotebookEdit,Bash(git checkout:*),Bash(git stash:*),Bash(git reset:*),Bash(git commit:*),Bash(git clean:*)
```

**AGT-8** Reviewer `opus` MUST be:

```text
claude -p <review prompt> --model claude-opus-5 --effort xhigh --dangerously-skip-permissions --disallowedTools Edit,Write,NotebookEdit,Bash(git checkout:*),Bash(git stash:*),Bash(git reset:*),Bash(git commit:*),Bash(git clean:*)
```

**AGT-9** The deny list in `AGT-7` and `AGT-8` is one argument. It holds because
`--disallowedTools` is honoured under `--dangerously-skip-permissions` — verified on Claude Code
2.1.274: a run under both flags asked to `Write` a file answered `DENIED` and wrote nothing, and one
asked to `git commit` was denied while `git status` ran. *The Reviewers keep a shell so they can
run the tests; what they lose is every way to edit the tree or move history. This is the
harness's enforcement, and rb-lite's no-shell-plus-diff-file is what it replaces.*

**AGT-10** Reviewer `astra` MUST be:

```text
codex exec -s read-only -m gpt-6-astra -c model_reasoning_effort=high <review prompt>
```

and Reviewer `sol` MUST be:

```text
codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=xhigh <review prompt>
```

*`codex review --base` cannot take a prompt (codex 0.153.4 refuses the combination), and the
Reviewer must read the brief; `exec` under the read-only sandbox lets it run git and the tests and
write nothing. The `-c` value is passed without quotes: codex parses it as TOML and, failing that,
takes the raw string, and `xhigh` was echoed back as `reasoning effort: xhigh` on 0.153.4.*

**AGT-11** The Panel MUST be exactly the four Reviewers `AGT-7`, `AGT-8` and `AGT-10` name, with
the Feedback File names `DIR-4` gives them. There is no flag, file or variable that changes the
Panel; changing it is a change to this document.

## What every agent process is given

**AGT-12** Every agent process MUST be started with standard input from the null device. *A CLI
that finds stdin open may wait on it until its timeout kills it; codex 0.153.4 did, for 25
minutes, during this Specification's own review.*

**AGT-13** Every agent process MUST be started with the git toplevel as its working directory,
its standard output to the file `DIR-4` names for it and its standard error to the matching
`.err` file, and the environment rloop itself received plus exactly these variables:

| variable | value |
|---|---|
| `RLOOP_ROLE` | `manager`, `implementer` or `reviewer` |
| `RLOOP_ROUND` | the Round number; `0` for the pick |
| `RLOOP_RUN` | the Run's number within its Sequence; `1` for a lone Run |
| `RLOOP_RUN_DIR` | the Run Directory's absolute path |
| `RLOOP_REVIEWER` | `fable`, `opus`, `astra` or `sol`; set for Reviewers only |

*Real agents ignore these — the prompt tells a model where things are. The Conformance Suite's
fakes read them to find their scripted part, which is what makes the suite independent of prompt
wording and CLI flags (`06-conformance.md`).*

**AGT-14** Every agent call MUST be bounded by its role's timeout (`AGT-1`). At the limit rloop
MUST send SIGTERM to the agent's process group, wait `--kill-after` seconds, then send SIGKILL to
the group, and treat the call as exited non-zero. A timeout is then whatever a failure of that
role is: judged by the Manager for an Implementer (`RUN-14`), a failure note for a Reviewer
(`RUN-15`), exit 2 for the Manager (`RUN-11`). *The group, not the PID: both CLIs fork tool
subprocesses, and a killed parent leaves them orphaned and still writing.*

**AGT-15** rloop MUST NOT exit while any agent process it started is running. On SIGINT or
SIGTERM it MUST send SIGTERM to every live agent group, wait for them (with `--kill-after`, then
SIGKILL), and exit 2 with `interrupted` on standard error. A second SIGINT during that wait MUST
send SIGKILL at once. The Run Directory is left as it is (`RUN-17`).

**AGT-16** Each agent process MUST be started in its own process group (its own session, as
`setsid` gives), so that `AGT-14` and `AGT-15` reach every descendant.

## Versions

**AGT-17** The command lines above were verified against Claude Code 2.1.274 and codex 0.153.4 on
2026-09-17/18. A fake agent accepts any flag, so the Conformance Suite cannot tell a wrong flag
from a right one; a flag that a newer CLI rejects is found only by a live Run, and `06-conformance.md`
carries the item that says so.
