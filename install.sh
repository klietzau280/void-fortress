#!/bin/bash
# Void Fortress installer
# Registers Claude Code hooks and checks dependencies.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/hook.sh"
SETTINGS_FILE="$HOME/.claude/settings.json"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}  ╔══════════════════════════════════════╗${NC}"
echo -e "${CYAN}  ║        V O I D   F O R T R E S S     ║${NC}"
echo -e "${CYAN}  ║  In the grim darkness there is code   ║${NC}"
echo -e "${CYAN}  ╚══════════════════════════════════════╝${NC}"
echo ""

# --- Check dependencies ---
echo -e "${YELLOW}Checking dependencies...${NC}"

if ! command -v python3 &>/dev/null; then
    echo -e "${RED}ERROR: python3 not found. Install Python 3.9+${NC}"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} python3"

if ! python3 -c "import pygame" 2>/dev/null; then
    echo -e "  ${YELLOW}Installing pygame...${NC}"
    pip3 install pygame
    echo -e "  ${GREEN}✓${NC} pygame installed"
else
    echo -e "  ${GREEN}✓${NC} pygame"
fi

if ! command -v claude &>/dev/null; then
    echo -e "  ${YELLOW}⚠ Claude Code CLI not found (optional — needed for live mode)${NC}"
else
    echo -e "  ${GREEN}✓${NC} claude"
fi

# --- Make hook executable ---
chmod +x "$HOOK_SCRIPT"
echo -e "  ${GREEN}✓${NC} hook.sh executable"

# --- Install Claude Code hooks ---
echo ""
echo -e "${YELLOW}Installing Claude Code hooks...${NC}"

EVENTS=(
    "SessionStart" "SessionEnd"
    "SubagentStart" "SubagentStop"
    "PreToolUse" "PostToolUse" "PostToolUseFailure"
    "UserPromptSubmit" "Stop"
    "Notification" "PermissionRequest" "PreCompact"
)

mkdir -p "$(dirname "$SETTINGS_FILE")"

# Use python to safely merge hooks into existing settings
python3 << PYEOF
import json, os, sys

settings_file = "$SETTINGS_FILE"
hook_script = "$HOOK_SCRIPT"
events = $(python3 -c "import json; print(json.dumps('${EVENTS[*]}'.split()))")

# Load existing settings or start fresh
settings = {}
if os.path.exists(settings_file):
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    except json.JSONDecodeError:
        print("  WARNING: existing settings.json was invalid, backing up", file=sys.stderr)
        os.rename(settings_file, settings_file + ".bak")

hooks = settings.setdefault("hooks", {})

installed = 0
skipped = 0
for event in events:
    hook_entry = {"type": "command", "command": hook_script}

    if event in hooks:
        # Check if our hook is already registered
        already = False
        for group in hooks[event]:
            for h in group.get("hooks", []):
                if h.get("command") == hook_script:
                    already = True
                    break
        if already:
            skipped += 1
            continue

    # Add our hook
    hooks[event] = [{"hooks": [hook_entry]}]
    installed += 1

with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2)

print(f"  Installed {installed} hooks, {skipped} already present")
PYEOF

echo -e "  ${GREEN}✓${NC} Hooks registered in $SETTINGS_FILE"

# --- Done ---
echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo -e "  Launch the fortress:"
echo -e "    ${CYAN}cd $SCRIPT_DIR && python3 gui.py${NC}"
echo ""
echo -e "  Demo mode (no Claude Code needed):"
echo -e "    ${CYAN}python3 gui.py --demo${NC}"
echo ""
echo -e "  Then use Claude Code in another terminal and watch the mechs build."
echo ""
echo -e "${CYAN}The Emperor protects.${NC}"
echo ""
