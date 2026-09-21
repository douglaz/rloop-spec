#!/usr/bin/env bash
# Shared scenario replay and comparison for run and test-panel-trace.
# Caller supplies work, fakes and exe, and owns scratch-directory cleanup.

# --- a fresh repository per run ----------------------------------------------------------------
new_repo() { # new_repo -> prints path; a git repo with one commit
  local r; r="$(mktemp -d "$work/repo.XXXXXX")"
  ( cd "$r" && git init -q -b master && echo hello > README && git add README \
    && git -c user.email=s@s -c user.name=suite commit -q -m init ) || return 1
  echo "$r"
}

# run_rloop <repo> <record dir> [rloop args...] ; environment for the fakes comes from the caller
run_rloop() {
  local repo="$1" rec="$2"; shift 2
  mkdir -p "$rec"
  ( cd "$repo" && PATH="$fakes:$PATH" RLOOP_FAKE_RECORD="$rec" "$exe" "$@" </dev/null \
      >"$rec/stdout" 2>"$rec/stderr" )
  echo $? > "$rec/exit"
  cat "$rec/exit"
}

# Observed trace: pick, impl<r>:<ok|fail>, panel<r>:<class>:<members>, judge<r>.
# Members are the recorded Reviewer names, sorted in C locale, unique and joined by +.
# A start or end records membership; without a successful end, that Reviewer failed.
# No expected roster is used to fill omissions.
observed_trace() { # observed_trace <record dir>
  local rec="$1" out=() line role round reviewer outcome pr=-1
  local -A outcomes=()
  [ -f "$rec/trace" ] || { echo ""; return; }
  flush_panel() {
    if [ "$pr" != -1 ]; then
      local cls membership outcome oks=0 fails=0
      for outcome in "${outcomes[@]}"; do
        if [ "$outcome" = ok ]; then oks=$((oks + 1)); else fails=$((fails + 1)); fi
      done
      if [ "$fails" = 0 ]; then cls=all; elif [ "$oks" = 0 ]; then cls=none; else cls=some; fi
      membership=$(printf '%s\n' "${!outcomes[@]}" | LC_ALL=C sort | paste -sd+)
      out+=("panel$pr:$cls:$membership"); pr=-1; outcomes=()
    fi
  }
  # Keep non-Panel completions and both Reviewer starts and ends, ordered by timestamp.
  # A start defaults to failure until its end arrives; each identity contributes once.
  while IFS= read -r line; do
    line="${line#*	}"
    role="${line%%:*}"; round="$(echo "$line" | cut -d: -f2)"; outcome="${line##*:}"
    case "$role" in
      manager) flush_panel; if [ "$round" = 0 ]; then out+=("pick"); else out+=("judge$round"); fi ;;
      implementer) flush_panel; out+=("impl$round:$outcome") ;;
      reviewer) if [ "$pr" != "$round" ]; then flush_panel; pr="$round"; fi
                reviewer="${line#*:*:}"; reviewer="${reviewer%%:*}"
                if [[ "$line" = *:end:* ]]; then outcomes[$reviewer]="$outcome"
                else outcomes[$reviewer]="${outcomes[$reviewer]:-fail}"; fi ;;
    esac
  done < <(awk -F: '{ for (i = 1; i <= NF; i++) if ($i == "end" || ($1 == "reviewer" && $i == "start")) { print $(i+1) "\t" $0; break } }' "$rec/trace" | sort -n)
  flush_panel
  local IFS=,; echo "${out[*]}"
}

# --- CNF-3: the scenarios ---------------------------------------------------------------------------
run_scenarios() { # run_scenarios <scenarios file> -> prints "<failures> <total>"
  local file="$1" total=0 bad=0 id max pick rounds interf exp_exit exp_trace repo rec got_exit got_trace
  while IFS=$'\t' read -r id max pick rounds interf exp_exit exp_trace; do
    [ "$id" = id ] && continue
    total=$((total + 1))
    repo="$(new_repo)"; rec="$work/rec-$id"
    got_exit=$(RLOOP_FAKE_PICK="$pick" RLOOP_FAKE_ROUNDS="${rounds/#-/}" RLOOP_FAKE_INTERFERENCE="$interf" \
      run_rloop "$repo" "$rec" --run-dir "$repo/run" --max-rounds "$max")
    got_trace="$(observed_trace "$rec")"
    if [ "$got_exit" != "$exp_exit" ] || [ "$got_trace" != "$exp_trace" ]; then
      bad=$((bad + 1))
      [ "$bad" -le 5 ] && printf '        %s: expected exit %s trace %s; got exit %s trace %s\n' "$id" "$exp_exit" "$exp_trace" "$got_exit" "$got_trace" >&2
    fi
    rm -rf "$repo" "$rec"
  done < "$file"
  echo "$bad $total"
}
