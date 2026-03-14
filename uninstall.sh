#!/bin/bash
# Void Fortress uninstaller — removes Claude Code hooks only.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/hook.sh"
SETTINGS_FILE="$HOME/.claude/settings.json"

echo ""
echo "Removing Void Fortress hooks from Claude Code..."

if [ ! -f "$SETTINGS_FILE" ]; then
    echo "No settings file found. Nothing to remove."
    exit 0
fi

python3 << PYEOF
import json, os

settings_file = "$SETTINGS_FILE"
hook_script = "$HOOK_SCRIPT"

with open(settings_file, 'r') as f:
    settings = json.load(f)

hooks = settings.get("hooks", {})
removed = 0
to_delete = []

for event, groups in hooks.items():
    new_groups = []
    for group in groups:
        new_hooks = [h for h in group.get("hooks", []) if h.get("command") != hook_script]
        if new_hooks:
            group["hooks"] = new_hooks
            new_groups.append(group)
        else:
            removed += 1
    if new_groups:
        hooks[event] = new_groups
    else:
        to_delete.append(event)

for event in to_delete:
    del hooks[event]

with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2)

print(f"Removed {removed} hooks. Your other settings are untouched.")
PYEOF

echo ""
echo "Done. The fortress sleeps."
echo ""
