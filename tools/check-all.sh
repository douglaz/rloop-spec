#!/usr/bin/env bash
# Run every gate that guards this specification set: the document gates tools/check-gates.sh
# holds, then the controls as that runner's last step. exec, so the exit status is the runner's.
exec bash "$(dirname "$0")/check-gates.sh" \
  "controls     (the identifier and citation gates' own positive and negative controls, each in a disposable copy of the set)" \
  python3 tools/test_citation_gates.py
