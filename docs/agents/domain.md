# Domain docs

Single-context: one `CONTEXT.md` and one `docs/adr/`, both at the root.

## Before exploring, read these

- **`CONTEXT.md`**: the glossary, and the only one.
- **`docs/adr/`**: the ADRs that touch the area you are about to work in.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis or
a test name), use the term `CONTEXT.md` defines. Don't drift to the aliases it lists to avoid.

If the concept you need is not in the glossary, that is a signal. Either you are inventing
language the project does not use, so reconsider, or there is a real gap, so note it for
`/domain-modeling`.

## Flag ADR conflicts

If your output contradicts an existing ADR, say so explicitly rather than silently overriding it:

> _Contradicts ADR-0007 (a gate that cannot decide warns rather than blocks), but worth reopening because…_
