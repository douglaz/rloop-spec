# The Specification hands an Implementation nothing to read

**Status:** accepted (2026-09-17)

Prompts and agent command lines are normative byte for byte, and the first design shipped them as
template files an Implementation would load and render. That was rejected: it turns every
Implementation into an interpreter for the Specification's data and moves the program into the
spec, when the point of this set is to test whether an implementer can turn a requirement into
code and do it again when the requirement changes. So they are stated verbatim in the Markdown
requirements, an Implementation hardcodes them however it likes, and the Conformance Suite compares
what its fake agents received against its own fixtures. A document gate keeps the Markdown blocks
and those fixtures identical; the Markdown is the home.

## Consequences

- A harness upgrade (a new flag, a new model on the Panel) is an amended requirement, a pin bump in
  each Implementation repository and a code change there — deliberately, since that path is what
  the rewrite gate exercises.
- Implementations live in their own repositories (`rloop-bash`, `rloop-rust`, …) and pin this one
  as a submodule. Nothing here is addressed to a build system.
