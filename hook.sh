#!/bin/bash
# Void Fortress - hook for Claude Code
# Logs events to JSONL for the GUI to consume

EVENTS_DIR="$HOME/.agent-valley"
EVENTS_FILE="$EVENTS_DIR/events.jsonl"

mkdir -p "$EVENTS_DIR"

# Read stdin
INPUT=$(cat)

# --- Log event to JSONL ---
TIMESTAMP=$(python3 -c "import time; print(time.time())")
echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
data['_ts'] = $TIMESTAMP
print(json.dumps(data))
" >> "$EVENTS_FILE" 2>/dev/null

exit 0
