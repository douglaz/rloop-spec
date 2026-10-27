# Grok joins the fixed Reviewer Panel

**Status:** accepted (2026-10-27, `rl-8gel`)

Add `AGT-19`; amend `AGT-11`, `AGT-13`, `AGT-17`, `RUN-7`, `RUN-21`, `PRM-2`, `PRM-4`,
`PRM-6` and `DIR-4`, with their model and Conformance Suite. The owner accepted Grok as a
mandatory fifth Reviewer. `AGT-11` keeps the fixed Panel; `AGT-19` owns the exact official
Grok Build CLI invocation and `RUN-21` its permanently unknown verdict.

## Choices and rationale

- **A mandatory seat over optional selection.** Every Round receives the additional independent
  assessment; a flag or configurable roster would make a Panel's identity depend on the caller.
  `AGT-11` states `There is no flag, file or variable that changes the Panel`.
- **A third provider without changing Consultation.** The value sought is independent review of
  the Task File and changes. Extending the advisers would reopen quorum and settlement choices.
  `RUN-20` and the four adviser commands in `PRM-1` and `PRM-2` stay unchanged. Grok is no
  Manager or Implementer preset. Findings remain advice for the Manager, never votes.
- **The official CLI over a direct API client or Claude Code plugin.** The operator's existing
  CLI authentication is used, without rloop acquiring authentication, billing or API machinery.
  Setup has its home in `README.md`, *Using rloop*. Environment inheritance remains `AGT-13`'s;
  inherited API-key variables are not stripped to force subscription billing, and no billing
  guarantee follows from login.
- **Unknown quota over unsupported scraping.** No supported non-inference Grok quota report is
  part of this integration. `RUN-21` states `Grok's verdict MUST be unknown in every record`.
  Unknown means an attempted call; a missing binary, rejected model, authentication failure or
  timeout remains visible under `AGT-19` and `RUN-15`. No extra Probe, fallback or retry is added.
- **Sandbox off with explicit restrictions over a build-breaking read-only sandbox.** Reviewers
  need generated build outputs and Nix daemon sockets. The native tool removal and command denies
  reduce accidental edits while the shared prompt forbids repository changes. A shell remains
  capable of writing by another route under `DIR-9`'s cooperative threat model; these switches
  establish neither adversarial containment nor removal of all configured extensions and hooks.

## Dated evidence and limits

`AGT-17` owns the **PARTIAL**, supplied 2026-10-27 observations on
`grok 1.0.62 (1474f9cbdd91)`. They include corrected bounded reviews, literal command refusals,
native-tool withholding, raw progress stdout and a successful corrected offline Nix-store-context
build. The original `Edit,Write` value did not withhold the native tools and allowed an actual
write; only that literal was superseded by the accepted `search_replace,write` spelling. The first
malformed Nix fixture remains failed evidence. Bad-model and wrapper-timeout observations used
the original value. These are observations of specific attempts and CLI metadata, not universal
enforcement, billing or provider-side attestations.

This Specification Run did not repeat those live experiments or run an integrated five-Reviewer
Round. The Conformance Suite's fakes require no real Grok or network and cannot validate vendor
flag acceptance. Implementation integration, its failure and timeout behavior and the real
five-Reviewer Round remain the dependent `rl-ytgu` Run's work before the catch-up push. The
Specification leading the Implementation is the amendment path of `ADR-0001`.
