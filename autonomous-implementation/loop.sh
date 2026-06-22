#!/bin/bash

set -euo pipefail

# ── Practitioner config ────────────────────────────────────────────────
# Keep this script agent-agnostic by supplying the command that starts one
# fresh coding-agent session. Prefer setting LOOP_AGENT_COMMAND in the shell;
# edit DEFAULT_AGENT_COMMAND only in a local copy.
#
# Contract for the command:
# - It runs unattended from this working directory.
# - It reads the prompt from $LOOP_PROMPT_FILE, either directly or through the
#   command string below.
# - It completes exactly one task from $LOOP_TASKS_FILE, updates the activity
#   log, commits changes, and exits.
# - It prints normal text, or JSON with a top-level "result" field.
#
# Example Claude Code adapter:
#   export LOOP_AGENT_COMMAND='claude -p "$(cat "$LOOP_PROMPT_FILE")" --output-format json --dangerously-skip-permissions'
#
# Generic stdin-style adapter:
#   export LOOP_AGENT_COMMAND='your-agent-cli --non-interactive < "$LOOP_PROMPT_FILE"'
DEFAULT_AGENT_COMMAND=""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

PROMPT_FILE="${LOOP_PROMPT_FILE:-PROMPT.md}"
TASKS_FILE="${LOOP_TASKS_FILE:-TASKS.md}"
ACTIVITY_FILE="${LOOP_ACTIVITY_FILE:-ACTIVITY.md}"
PATTERNS_FILE="${LOOP_PATTERNS_FILE:-PATTERNS.md}"
AGENTS_FILE="${LOOP_AGENTS_FILE:-AGENTS.md}"
SANDBOX_FILE="${LOOP_SANDBOX_FILE:-SANDBOX.md}"
LOCKFILE="${LOOP_LOCKFILE:-.loop.lock}"
DELAY_BETWEEN_ITERATIONS="${LOOP_DELAY:-3}"
COMPLETION_SENTINEL="<all-tasks-done/>"
COMMIT_PREFIX="${LOOP_COMMIT_PREFIX:-loop:}"
AGENT_COMMAND="${LOOP_AGENT_COMMAND:-$DEFAULT_AGENT_COMMAND}"

usage() {
  echo "Usage: $0 <iterations>"
  echo ""
  echo "Runs a coding agent autonomously to complete tasks defined in $TASKS_FILE."
  echo "Each iteration starts one fresh session and should complete one task."
  echo ""
  echo "Prerequisites:"
  echo "  - LOOP_AGENT_COMMAND exported, or DEFAULT_AGENT_COMMAND set in this script"
  echo "  - git installed and this directory inside a git repository"
  echo "  - $PROMPT_FILE with per-session prompt"
  echo "  - $AGENTS_FILE with canonical loop instructions"
  echo "  - $TASKS_FILE with task definitions generated from PLAN.md"
  echo "  - $ACTIVITY_FILE and $PATTERNS_FILE for loop continuity"
  echo "  - $SANDBOX_FILE reviewed before running"
  echo ""
  echo "Environment variables:"
  echo "  LOOP_AGENT_COMMAND   Command used to start one fresh agent session"
  echo "  LOOP_PROMPT_FILE     Path to prompt file (default: PROMPT.md)"
  echo "  LOOP_TASKS_FILE      Path to task registry (default: TASKS.md)"
  echo "  LOOP_ACTIVITY_FILE   Path to activity log (default: ACTIVITY.md)"
  echo "  LOOP_PATTERNS_FILE   Path to recurring-corrections file (default: PATTERNS.md)"
  echo "  LOOP_AGENTS_FILE     Path to canonical instructions (default: AGENTS.md)"
  echo "  LOOP_SANDBOX_FILE    Path to sandbox guidance (default: SANDBOX.md)"
  echo "  LOOP_DELAY           Seconds between iterations (default: 3)"
  echo ""
  echo "Examples:"
  echo '  export LOOP_AGENT_COMMAND='"'"'your-agent-cli --non-interactive < "$LOOP_PROMPT_FILE"'"'"''
  echo "  ./loop.sh 3"
  echo ""
  echo '  export LOOP_AGENT_COMMAND='"'"'claude -p "$(cat "$LOOP_PROMPT_FILE")" --output-format json --dangerously-skip-permissions'"'"''
  echo "  ./loop.sh 3"
  exit 1
}

format_duration() {
  local seconds=$1
  if [ "$seconds" -lt 60 ]; then
    echo "${seconds}s"
  elif [ "$seconds" -lt 3600 ]; then
    local minutes=$((seconds / 60))
    local remaining_seconds=$((seconds % 60))
    echo "${minutes}m ${remaining_seconds}s"
  else
    local hours=$((seconds / 3600))
    local minutes=$(((seconds % 3600) / 60))
    echo "${hours}h ${minutes}m"
  fi
}

timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

cleanup() {
  rm -f "$LOCKFILE"
}

count_incomplete_tasks() {
  local count
  count=$(grep -cE '^[[:space:]]*-[[:space:]]+\*\*Passes:\*\*[[:space:]]+false[[:space:]]*$' "$1" 2>/dev/null || true)
  echo "${count:-0}"
}

require_file() {
  local path=$1
  local description=$2
  if [ ! -f "$path" ]; then
    echo -e "${RED}Error: $path not found — $description${NC}"
    exit 1
  fi
}

if [ -z "${1:-}" ]; then
  usage
fi

if ! [[ "$1" =~ ^[0-9]+$ ]] || [ "$1" -lt 1 ]; then
  echo -e "${RED}Error: iterations must be a positive integer${NC}"
  exit 1
fi

ITERATIONS=$1

# Export the loop contract for the adapter command.
export LOOP_PROMPT_FILE="$PROMPT_FILE"
export LOOP_TASKS_FILE="$TASKS_FILE"
export LOOP_ACTIVITY_FILE="$ACTIVITY_FILE"
export LOOP_PATTERNS_FILE="$PATTERNS_FILE"
export LOOP_AGENTS_FILE="$AGENTS_FILE"
export LOOP_SANDBOX_FILE="$SANDBOX_FILE"
export LOOP_COMPLETION_SENTINEL="$COMPLETION_SENTINEL"
export LOOP_COMMIT_PREFIX="$COMMIT_PREFIX"

# ── Pre-flight checks ──────────────────────────────────────────────────

if [ -z "$AGENT_COMMAND" ]; then
  echo -e "${RED}Error: no agent command configured${NC}"
  echo "Set LOOP_AGENT_COMMAND or edit DEFAULT_AGENT_COMMAND near the top of this script."
  echo "Run '$0' with no arguments for examples."
  exit 1
fi

HAS_JQ=true
if ! command -v jq &> /dev/null; then
  echo -e "${YELLOW}Warning: jq not found — JSON result parsing and token display will be unavailable${NC}"
  echo ""
  HAS_JQ=false
fi

if ! command -v git &> /dev/null; then
  echo -e "${RED}Error: git not found in PATH${NC}"
  exit 1
fi

if ! git rev-parse --is-inside-work-tree &> /dev/null; then
  echo -e "${RED}Error: not inside a git repository${NC}"
  exit 1
fi

if [ -f "$LOCKFILE" ]; then
  LOCK_PID=$(cat "$LOCKFILE" 2>/dev/null || echo "")
  if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
    echo -e "${RED}Error: another loop instance is running (PID $LOCK_PID)${NC}"
    echo -e "${RED}If this is stale, remove $LOCKFILE manually.${NC}"
    exit 1
  else
    echo -e "${YELLOW}Warning: stale lockfile found — removing${NC}"
    rm -f "$LOCKFILE"
  fi
fi

trap cleanup EXIT INT TERM
echo $$ > "$LOCKFILE"

require_file "$PROMPT_FILE" "per-session prompt is required"
require_file "$AGENTS_FILE" "canonical loop instructions are required"
require_file "$TASKS_FILE" "generate task definitions first"
require_file "$ACTIVITY_FILE" "activity log is required"
require_file "$PATTERNS_FILE" "recurring-corrections file is required"

if [ ! -f "$SANDBOX_FILE" ]; then
  echo -e "${YELLOW}Warning: $SANDBOX_FILE not found${NC}"
  echo -e "${YELLOW}Review sandboxing and isolation before running autonomous sessions.${NC}"
  echo ""
  read -p "Continue anyway? [y/N] " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

INCOMPLETE_TASKS=$(count_incomplete_tasks "$TASKS_FILE")

if [ "$INCOMPLETE_TASKS" -eq 0 ]; then
  echo -e "${GREEN}All tasks in $TASKS_FILE are already complete. Nothing to do.${NC}"
  exit 0
fi

if [ "$ITERATIONS" -lt "$INCOMPLETE_TASKS" ]; then
  echo -e "${YELLOW}Warning: $INCOMPLETE_TASKS incomplete task(s) in $TASKS_FILE, but only $ITERATIONS iteration(s) requested${NC}"
  echo -e "${YELLOW}Not all tasks will be completed.${NC}"
  echo ""
  read -p "Continue anyway? [y/N] " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  echo -e "${YELLOW}Warning: uncommitted changes detected in the working tree${NC}"
  echo -e "${YELLOW}The loop prompt instructs the agent to commit with 'git add -A', which may include these changes.${NC}"
  echo -e "${YELLOW}Consider committing or stashing your work first.${NC}"
  echo ""
  read -p "Continue anyway? [y/N] " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# ── Start ───────────────────────────────────────────────────────────────

echo -e "${BOLD}Starting autonomous implementation loop${NC}"
echo "================================================================"
echo -e "  ${CYAN}Started:${NC}          $(timestamp)"
echo -e "  ${CYAN}Max iterations:${NC}   $ITERATIONS"
echo -e "  ${CYAN}Incomplete tasks:${NC} $INCOMPLETE_TASKS"
echo -e "  ${CYAN}Prompt file:${NC}      $PROMPT_FILE"
echo -e "  ${CYAN}Tasks file:${NC}       $TASKS_FILE"
echo -e "  ${CYAN}Activity file:${NC}    $ACTIVITY_FILE"
echo -e "  ${CYAN}Agent command:${NC}    configured"
echo "================================================================"
echo ""

TOTAL_START_TIME=$(date +%s)
COMPLETED_ITERATIONS=0
FAILED_ITERATIONS=0

for ((i=1; i<=ITERATIONS; i++)); do
  ITER_START_TIME=$(date +%s)
  export LOOP_ITERATION="$i"

  echo -e "${BOLD}${GREEN}>> Iteration $i of $ITERATIONS${NC}"
  echo -e "${DIM}----------------------------------------------------------------${NC}"
  echo -e "  ${BLUE}Started:${NC} $(timestamp)"

  CURRENT_INCOMPLETE=$(count_incomplete_tasks "$TASKS_FILE")
  echo -e "  ${BLUE}Remaining tasks:${NC} $CURRENT_INCOMPLETE"

  if [ "$CURRENT_INCOMPLETE" -eq 0 ]; then
    echo -e "${GREEN}  No incomplete tasks remain — stopping early.${NC}"
    break
  fi
  echo ""

  set +e
  raw_output=$(bash -lc "$AGENT_COMMAND" 2>&1)
  exit_code=$?
  set -e

  result="$raw_output"
  INPUT_TOKENS=0
  OUTPUT_TOKENS=0
  TOTAL_TOKENS=0

  if [ "$HAS_JQ" = true ] && echo "$raw_output" | jq -e . &> /dev/null 2>&1; then
    parsed_result=$(echo "$raw_output" | jq -r '.result // .message // .text // empty')
    if [ -n "$parsed_result" ]; then
      result="$parsed_result"
    fi
    INPUT_TOKENS=$(echo "$raw_output" | jq -r '.input_tokens // .usage.input_tokens // 0')
    OUTPUT_TOKENS=$(echo "$raw_output" | jq -r '.output_tokens // .usage.output_tokens // 0')
    TOTAL_TOKENS=$((INPUT_TOKENS + OUTPUT_TOKENS))
  fi

  ITER_END_TIME=$(date +%s)
  ITER_DURATION=$((ITER_END_TIME - ITER_START_TIME))

  RESPONSE_LINES=$(echo "$result" | wc -l | tr -d ' ')
  RESPONSE_CHARS=$(echo "$result" | wc -c | tr -d ' ')

  echo -e "${DIM}--- Agent Response ---${NC}"
  echo "$result"
  echo -e "${DIM}--- End Response ---${NC}"
  echo ""

  echo -e "  ${BLUE}Finished:${NC} $(timestamp)"
  echo -e "  ${BLUE}Duration:${NC} $(format_duration "$ITER_DURATION")"
  echo -e "  ${BLUE}Response:${NC} $RESPONSE_LINES lines, $RESPONSE_CHARS chars"
  echo -e "  ${BLUE}Exit code:${NC} $exit_code"

  if [ "$TOTAL_TOKENS" -gt 0 ]; then
    echo ""
    echo -e "  ${BOLD}Context Usage${NC}"

    CONTEXT_WINDOW="${LOOP_CONTEXT_WINDOW:-200000}"
    USAGE_PERCENT=$((TOTAL_TOKENS * 100 / CONTEXT_WINDOW))
    INPUT_PERCENT=$((INPUT_TOKENS * 100 / CONTEXT_WINDOW))
    OUTPUT_PERCENT=$((OUTPUT_TOKENS * 100 / CONTEXT_WINDOW))

    if [ "$INPUT_TOKENS" -ge 1000 ]; then
      INPUT_DISPLAY="$((INPUT_TOKENS / 1000)).$((INPUT_TOKENS % 1000 / 100))k"
    else
      INPUT_DISPLAY="$INPUT_TOKENS"
    fi
    if [ "$OUTPUT_TOKENS" -ge 1000 ]; then
      OUTPUT_DISPLAY="$((OUTPUT_TOKENS / 1000)).$((OUTPUT_TOKENS % 1000 / 100))k"
    else
      OUTPUT_DISPLAY="$OUTPUT_TOKENS"
    fi
    if [ "$TOTAL_TOKENS" -ge 1000 ]; then
      TOTAL_DISPLAY="$((TOTAL_TOKENS / 1000)).$((TOTAL_TOKENS % 1000 / 100))k"
    else
      TOTAL_DISPLAY="$TOTAL_TOKENS"
    fi

    FILLED_SEGMENTS=$((USAGE_PERCENT / 10))
    if [ "$FILLED_SEGMENTS" -gt 10 ]; then FILLED_SEGMENTS=10; fi
    EMPTY_SEGMENTS=$((10 - FILLED_SEGMENTS))

    BAR=""
    for ((s=0; s<FILLED_SEGMENTS; s++)); do BAR+="# "; done
    for ((s=0; s<EMPTY_SEGMENTS; s++)); do BAR+="- "; done

    echo -e "  [${BAR}]  ${TOTAL_DISPLAY}/${CONTEXT_WINDOW} tokens (${USAGE_PERCENT}%)"
    echo -e "  Input:  ${INPUT_DISPLAY} tokens (${INPUT_PERCENT}%)"
    echo -e "  Output: ${OUTPUT_DISPLAY} tokens (${OUTPUT_PERCENT}%)"
  fi

  if [[ "$result" == *"$COMPLETION_SENTINEL"* ]]; then
    COMPLETED_ITERATIONS=$i
    TOTAL_END_TIME=$(date +%s)
    TOTAL_DURATION=$((TOTAL_END_TIME - TOTAL_START_TIME))

    echo ""
    echo -e "${BOLD}${GREEN}================================================================${NC}"
    echo -e "${BOLD}${GREEN}ALL TASKS COMPLETE${NC}"
    echo -e "${GREEN}================================================================${NC}"
    echo -e "  ${CYAN}Finished:${NC}    $(timestamp)"
    echo -e "  ${CYAN}Iterations:${NC}  $i of $ITERATIONS"
    echo -e "  ${CYAN}Total time:${NC}  $(format_duration "$TOTAL_DURATION")"
    exit 0
  fi

  if [ $exit_code -ne 0 ]; then
    echo -e "  ${YELLOW}Warning: agent process exited with non-zero code ($exit_code)${NC}"
    FAILED_ITERATIONS=$((FAILED_ITERATIONS + 1))
  fi

  LATEST_COMMIT_MSG=$(git log -1 --pretty=format:"%s" 2>/dev/null || echo "")
  if [[ "$LATEST_COMMIT_MSG" == "$COMMIT_PREFIX"* ]]; then
    echo -e "  ${GREEN}Committed: $LATEST_COMMIT_MSG${NC}"
  else
    echo -e "  ${YELLOW}Warning: no '$COMMIT_PREFIX' commit detected for this iteration${NC}"
  fi

  COMPLETED_ITERATIONS=$i

  echo ""
  echo -e "${DIM}================================================================${NC}"
  echo ""

  if [ $i -lt "$ITERATIONS" ]; then
    echo -e "${DIM}Waiting ${DELAY_BETWEEN_ITERATIONS}s before next iteration...${NC}"
    sleep "$DELAY_BETWEEN_ITERATIONS"
    echo ""
  fi
done

TOTAL_END_TIME=$(date +%s)
TOTAL_DURATION=$((TOTAL_END_TIME - TOTAL_START_TIME))

FINAL_INCOMPLETE=$(count_incomplete_tasks "$TASKS_FILE")
TASKS_COMPLETED=$((INCOMPLETE_TASKS - FINAL_INCOMPLETE))

echo -e "${BOLD}${YELLOW}================================================================${NC}"
echo -e "${BOLD}${YELLOW}REACHED MAX ITERATIONS${NC}"
echo -e "${YELLOW}================================================================${NC}"
echo -e "  ${CYAN}Finished:${NC}           $(timestamp)"
echo -e "  ${CYAN}Iterations run:${NC}     $COMPLETED_ITERATIONS of $ITERATIONS"
echo -e "  ${CYAN}Failed iterations:${NC}  $FAILED_ITERATIONS"
echo -e "  ${CYAN}Total time:${NC}         $(format_duration "$TOTAL_DURATION")"
echo -e "  ${CYAN}Tasks completed:${NC}    $TASKS_COMPLETED"
echo -e "  ${CYAN}Tasks remaining:${NC}    $FINAL_INCOMPLETE"
echo ""
if [ "$FINAL_INCOMPLETE" -gt 0 ]; then
  echo -e "Run ${BOLD}./loop.sh $FINAL_INCOMPLETE${NC} to complete remaining tasks."
fi
exit 1
