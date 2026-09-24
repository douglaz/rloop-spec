#!/usr/bin/env bash
# Shared scenario replay and comparison for run and test-panel-trace.
# Caller supplies work, fakes and exe, calls restrict_path once, and owns scratch-directory cleanup.

# --- a fresh repository per run ----------------------------------------------------------------
new_repo() { # new_repo -> prints path; a git repo with one commit
  local r; r="$(mktemp -d "$work/repo.XXXXXX")"
  ( cd "$r" && git init -q -b master && echo hello > README && git add README \
    && git -c user.email=s@s -c user.name=suite commit -q -m init ) || return 1
  echo "$r"
}

# --- CNF-2: the executable's PATH -------------------------------------------------------------------
# What GNU coreutils ships, by its own program list: not what this host installs (a host may lack
# some) and not what any Implementation happens to call.
coreutils_programs='[ arch b2sum base32 base64 basename basenc cat chcon chgrp chmod chown chroot cksum comm
coreutils cp csplit cut date dd df dir dircolors dirname du echo env expand expr factor false
fmt fold groups head hostid hostname id install join kill link ln logname ls md5sum mkdir
mkfifo mknod mktemp mv nice nl nohup nproc numfmt od paste pathchk pinky pr printenv printf
ptx pwd readlink realpath rm rmdir runcon seq sha1sum sha224sum sha256sum sha384sum sha512sum
shred shuf sleep sort split stat stdbuf stty sum sync tac tail tee test timeout touch tr true
truncate tsort tty uname unexpand uniq unlink uptime users vdir wc who whoami yes'
# The names the fakes and the git shim run under the executable's PATH: a host without one would
# turn a suite defect into a red item, so the suite refuses to start instead.
executable_path_needs='bash git grep sed tr timeout head date sleep basename ls'
# restrict_path: builds $private, the only directory after $fakes on the executable's PATH: the
# tools CNF-1 names for an Implementation, each a symlink to the file bash finds. `type -P`, not
# `command -v`, which names the builtin for printf, kill, test, [, echo, pwd and true, so the
# link would dangle for the names a script calls most. A name the host lacks is skipped and
# named once on standard error; one the suite itself needs, here or on its own PATH (cmp and
# find, which stay the suite's), is exit 2 before any item.
restrict_path() {
  local name file skipped=""
  private="$work/private"; mkdir -p "$private"
  for name in cmp find; do
    type -P "$name" >/dev/null || { echo "conformance: $name is not on PATH and the suite needs it" >&2; exit 2; }
  done
  for name in bash git grep sed awk $coreutils_programs; do
    if file="$(type -P "$name")"; then
      case "$file" in /*) ;; *) file="$PWD/$file" ;; esac # a relative PATH entry prints a relative path
      ln -s "$file" "$private/$name"
    else skipped="$skipped $name"; fi
  done
  for name in $executable_path_needs; do
    [ -e "$private/$name" ] || { echo "conformance: $name could not be linked into the executable's PATH and the fakes need it" >&2; exit 2; }
  done
  [ -z "$skipped" ] || echo "conformance: not on this host, so not on the executable's PATH:$skipped" >&2
}

# run_rloop <repo> <record dir> [rloop args...] ; environment for the fakes comes from the caller
run_rloop() {
  local repo="$1" rec="$2"; shift 2
  mkdir -p "$rec"
  ( cd "$repo" && PATH="$fakes:$private" RLOOP_FAKE_RECORD="$rec" "$exe" "$@" </dev/null \
      >"$rec/stdout" 2>"$rec/stderr" )
  echo $? > "$rec/exit"
  cat "$rec/exit"
}

# Observed trace: pick, impl<r>:<ok|fail>, panel<r>:<class>:<members>, judge<r>.
# Members are the recorded Reviewer names, sorted in C locale, unique and joined by +.
# A start or end records membership; without a successful end, that Reviewer failed.
# No expected roster is used to fill omissions.
observed_trace() { # observed_trace <record dir>
  local rec="$1" out=() line role round reviewer outcome pr=-1 i idx
  # Two parallel indexed arrays rather than one associative array: `CNF-1` promises the suite
  # needs only `bash`, and macOS still ships 3.2, which has no `declare -A`. A Panel is four
  # entries, so the linear lookup costs nothing.
  local rvs=() outs=()
  [ -f "$rec/trace" ] || { echo ""; return; }
  flush_panel() {
    if [ "$pr" != -1 ]; then
      local cls membership outcome oks=0 fails=0
      for outcome in ${outs[@]+"${outs[@]}"}; do
        if [ "$outcome" = ok ]; then oks=$((oks + 1)); else fails=$((fails + 1)); fi
      done
      if [ "$fails" = 0 ]; then cls=all; elif [ "$oks" = 0 ]; then cls=none; else cls=some; fi
      membership=$(printf '%s\n' ${rvs[@]+"${rvs[@]}"} | LC_ALL=C sort | paste -sd+)
      out+=("panel$pr:$cls:$membership"); pr=-1; rvs=(); outs=()
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
                idx=-1; i=0
                while [ "$i" -lt "${#rvs[@]}" ]; do
                  if [ "${rvs[$i]}" = "$reviewer" ]; then idx=$i; break; fi
                  i=$((i + 1))
                done
                if [ "$idx" = -1 ]; then
                  rvs+=("$reviewer"); outs+=(fail); idx=$(( ${#rvs[@]} - 1 ))
                fi
                if [[ "$line" = *:end:* ]]; then outs[$idx]="$outcome"; fi ;;
    esac
  done < <(awk -F: '{ for (i = 1; i <= NF; i++) if ($i == "end" || ($1 == "reviewer" && $i == "start")) { print $(i+1) "\t" $0; break } }' "$rec/trace" | sort -n)
  flush_panel
  local IFS=,; echo "${out[*]}"
}

# --- the Seats (RUN-21, RUN-22) ---------------------------------------------------------------------
# A model RUN-21's table does not name: a Seat holding it reads `unknown` whatever the probe says,
# so a Run can be refused, or its judge withheld, only where a script seats a model on the table.
off_table_model=claude-sonnet-5
seat_model() { # seat_model <fable|opus|anything else> -> that Reviewer's model (AGT-7, AGT-8), or the off-table one
  case $1 in fable) echo claude-fable-5-1 ;; opus) echo claude-opus-5 ;; *) echo "$off_table_model" ;; esac
}

# --- CNF-3: the scenarios ---------------------------------------------------------------------------
run_scenarios() { # run_scenarios <scenarios file> -> prints "<failures> <total>"
  local file="$1" total=0 bad=0 id max pick rounds interf probe seats exp_exit exp_trace repo rec got_exit got_trace
  local kv manager_seat implementer_seat pick_probe
  while IFS=$'\t' read -r id max pick rounds interf probe seats exp_exit exp_trace; do
    [ "$id" = id ] && continue
    total=$((total + 1))
    manager_seat=''; implementer_seat=''; pick_probe=clear
    for kv in ${seats//;/ }; do
      case $kv in
        manager=*) manager_seat=${kv#*=} ;; implementer=*) implementer_seat=${kv#*=} ;; pick=*) pick_probe=${kv#*=} ;;
      esac
    done
    repo="$(new_repo)"; rec="$work/rec-$id"
    got_exit=$(RLOOP_FAKE_PICK="$pick" RLOOP_FAKE_ROUNDS="${rounds/#-/}" RLOOP_FAKE_INTERFERENCE="$interf" \
      RLOOP_FAKE_PROBE="${probe/#-/}" RLOOP_FAKE_PROBE_PICK="$pick_probe" run_rloop "$repo" "$rec" \
      --run-dir "$repo/run" --max-rounds "$max" \
      --manager-model "$(seat_model "$manager_seat")" --implementer-model "$(seat_model "$implementer_seat")")
    got_trace="$(observed_trace "$rec")"
    if [ "$got_exit" != "$exp_exit" ] || [ "$got_trace" != "$exp_trace" ]; then
      bad=$((bad + 1))
      [ "$bad" -le 5 ] && printf '        %s: expected exit %s trace %s; got exit %s trace %s\n' "$id" "$exp_exit" "$exp_trace" "$got_exit" "$got_trace" >&2
    fi
    rm -rf "$repo" "$rec"
  done < "$file"
  echo "$bad $total"
}
