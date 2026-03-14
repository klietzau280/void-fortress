#!/bin/bash
# Void Fortress - hook for Claude Code
# Logs events to JSONL + plays sci-fi trooper voice lines

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOUNDS_DIR="$SCRIPT_DIR/sounds"
EVENTS_DIR="$HOME/.agent-valley"
EVENTS_FILE="$EVENTS_DIR/events.jsonl"
LOCK_FILE="$EVENTS_DIR/.sound.lock"
VOLUME=0.5
COOLDOWN=3  # minimum seconds between sounds

mkdir -p "$EVENTS_DIR"

# Read stdin
INPUT=$(cat)

# --- Log event to JSONL (always) ---
TIMESTAMP=$(python3 -c "import time; print(time.time())")
echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
data['_ts'] = $TIMESTAMP
print(json.dumps(data))
" >> "$EVENTS_FILE" 2>/dev/null

# --- Play sound (with cooldown) ---
EVENT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('hook_event_name',''))" 2>/dev/null)

pick_random() {
    local prefix="$1"
    local files=("$SOUNDS_DIR"/${prefix}_*.aiff)
    if [ ${#files[@]} -gt 0 ] && [ -f "${files[0]}" ]; then
        local idx=$((RANDOM % ${#files[@]}))
        echo "${files[$idx]}"
    fi
}

# Only these events trigger sounds
SOUND=""
case "$EVENT" in
    SessionStart)       SOUND=$(pick_random "session_start") ;;
    UserPromptSubmit)   SOUND=$(pick_random "task_ack") ;;
    Stop)               SOUND=$(pick_random "task_done") ;;
    PostToolUseFailure) SOUND=$(pick_random "error") ;;
    PermissionRequest)  SOUND=$(pick_random "input") ;;
    SubagentStart)      SOUND=$(pick_random "spawn") ;;
    PreCompact)         SOUND=$(pick_random "compact") ;;
esac

# No sound for this event type? Just exit.
if [ -z "$SOUND" ] || [ ! -f "$SOUND" ]; then
    exit 0
fi

# Cooldown check - don't play if another sound played recently
NOW=$(python3 -c "import time; print(int(time.time()))")
if [ -f "$LOCK_FILE" ]; then
    LAST=$(cat "$LOCK_FILE" 2>/dev/null)
    DIFF=$((NOW - LAST))
    if [ "$DIFF" -lt "$COOLDOWN" ]; then
        exit 0
    fi
fi

# Write lock and play - osascript spawns through macOS, fully outside Claude's process tree
echo "$NOW" > "$LOCK_FILE"
osascript -e "do shell script \"afplay -v $VOLUME '$SOUND' &\"" &

exit 0
