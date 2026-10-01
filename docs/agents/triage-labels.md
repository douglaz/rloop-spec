# Triage roles

`/triage` speaks in five state roles and two category roles. In this repository they are places,
not labels. A triaged issue ends up either closed or with its work in a bead.

| Role | Here |
|---|---|
| `needs-triage` | An open GitHub issue with no triage comment. |
| `needs-info` | An open GitHub issue whose latest comment is triage notes. The reporter is the owner, so this means "waiting on the owner's decision". |
| `ready-for-agent` | An open bead whose body does not withhold it: what `br ready` lists and an rloop Run picks. The agent brief is the bead's body. |
| `ready-for-human` | An open bead labelled `deferred` whose body opens **Owner-picked only. Not ready**, followed by what the owner must supply. `br ready` still lists it. The body line is what keeps a Manager from picking it. |
| `wontfix` | The GitHub issue closed `not planned`. A rejected or deferred idea goes in `07-open-findings.md`, which is this repository's out-of-scope record, so there is no `.out-of-scope/`. Work that was already done is closed `completed`, with a pointer to where it lives. |

| Category | Bead type |
|---|---|
| `bug` | `bug` |
| `enhancement` | `task`, the repository's default |
