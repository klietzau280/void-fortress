#!/bin/bash
# Void Fortress - hook for Claude Code
# Logs events to JSONL + plays sci-fi trooper voice lines

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOUNDS_DIR="$SCRIPT_DIR/sounds"
EVENTS_DIR="$HOME/.agent-valley"
EVENTS_FILE="$EVENTS_DIR/events.jsonl"
LOCK_FILE="$EVENTS_DIR/.sound.lock"
PID_FILE="$EVENTS_DIR/.gui.pid"
VOLUME=0.5
COOLDOWN=3

mkdir -p "$EVENTS_DIR"

# Read stdin
INPUT=$(cat)

# --- Log event to JSONL (always, even without GUI) ---
TIMESTAMP=$(python3 -c "import time; print(time.time())")
echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
data['_ts'] = $TIMESTAMP
print(json.dumps(data))
" >> "$EVENTS_FILE" 2>/dev/null

# --- Only play sounds if GUI is running ---
if [ ! -f "$PID_FILE" ]; then
    exit 0
fi
GUI_PID=$(cat "$PID_FILE" 2>/dev/null)
if ! kill -0 "$GUI_PID" 2>/dev/null; then
    rm -f "$PID_FILE"
    exit 0
fi

# --- Play sound ---
EVENT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('hook_event_name',''))" 2>/dev/null)

pick_random() {
    local prefix="$1"
    local files=("$SOUNDS_DIR"/${prefix}_*.aiff)
    if [ ${#files[@]} -gt 0 ] && [ -f "${files[0]}" ]; then
        local idx=$((RANDOM % ${#files[@]}))
        echo "${files[$idx]}"
    fi
}

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

if [ -z "$SOUND" ] || [ ! -f "$SOUND" ]; then
    exit 0
fi

# Cooldown
NOW=$(python3 -c "import time; print(int(time.time()))")
if [ -f "$LOCK_FILE" ]; then
    LAST=$(cat "$LOCK_FILE" 2>/dev/null)
    DIFF=$((NOW - LAST))
    if [ "$DIFF" -lt "$COOLDOWN" ]; then
        exit 0
    fi
fi

echo "$NOW" > "$LOCK_FILE"
osascript -e "do shell script \"afplay -v $VOLUME '$SOUND' &\"" &

exit 0
