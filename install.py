#!/usr/bin/env python3
"""Void Fortress - cross-platform installer.

Registers Claude Code hooks and checks dependencies.
Works on Windows, macOS, and Linux.
"""

import io
import json
import os
import shutil
import subprocess
import sys

# Ensure Unicode output works on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")

# The hook command — use hook.py with python/python3
if sys.platform == "win32":
    HOOK_COMMAND = f'python "{os.path.join(SCRIPT_DIR, "hook.py")}"'
else:
    HOOK_COMMAND = f'python3 "{os.path.join(SCRIPT_DIR, "hook.py")}"'

EVENTS = [
    "SessionStart", "SessionEnd",
    "SubagentStart", "SubagentStop",
    "PreToolUse", "PostToolUse", "PostToolUseFailure",
    "UserPromptSubmit", "Stop",
    "Notification", "PermissionRequest", "PreCompact",
]

# ANSI colors (work in modern Windows terminals too)
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
CYAN = "\033[0;36m"
NC = "\033[0m"


def check_python():
    """Verify Python version."""
    v = sys.version_info
    if v < (3, 9):
        print(f"  {RED}ERROR: Python 3.9+ required (found {v.major}.{v.minor}){NC}")
        sys.exit(1)
    print(f"  {GREEN}\u2713{NC} python {v.major}.{v.minor}.{v.micro}")


def check_pygame():
    """Check for pygame, install if missing."""
    try:
        import pygame  # noqa: F401
        print(f"  {GREEN}\u2713{NC} pygame")
    except ImportError:
        print(f"  {YELLOW}Installing pygame...{NC}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"],
                              stdout=subprocess.DEVNULL)
        print(f"  {GREEN}\u2713{NC} pygame installed")


def check_claude():
    """Check if Claude Code CLI is available."""
    if shutil.which("claude"):
        print(f"  {GREEN}\u2713{NC} claude")
    else:
        print(f"  {YELLOW}\u26a0 Claude Code CLI not found (optional \u2014 needed for live mode){NC}")


def install_hooks():
    """Register hooks in Claude Code settings."""
    settings_dir = os.path.dirname(SETTINGS_FILE)
    os.makedirs(settings_dir, exist_ok=True)

    # Load existing settings
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
        except json.JSONDecodeError:
            backup = SETTINGS_FILE + ".bak"
            print(f"  {YELLOW}WARNING: existing settings.json was invalid, backing up to {backup}{NC}")
            shutil.copy2(SETTINGS_FILE, backup)

    hooks = settings.setdefault("hooks", {})

    installed = 0
    skipped = 0

    for event in EVENTS:
        hook_entry = {"type": "command", "command": HOOK_COMMAND}

        if event in hooks:
            # Check if our hook is already registered
            already = False
            for group in hooks[event]:
                for h in group.get("hooks", []):
                    if "hook.py" in h.get("command", ""):
                        already = True
                        break
                    # Also detect old hook.sh registrations
                    if "hook.sh" in h.get("command", ""):
                        # Replace the old hook.sh with hook.py
                        h["command"] = HOOK_COMMAND
                        already = True
                        break
            if already:
                skipped += 1
                continue

        # Add our hook
        hooks[event] = [{"hooks": [hook_entry]}]
        installed += 1

    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

    print(f"  Installed {installed} hooks, {skipped} already present")
    print(f"  {GREEN}\u2713{NC} Hooks registered in {SETTINGS_FILE}")


def main():
    print()
    print(f"{CYAN}  \u2554{'═' * 38}\u2557{NC}")
    print(f"{CYAN}  \u2551        V O I D   F O R T R E S S     \u2551{NC}")
    print(f"{CYAN}  \u2551  In the grim darkness there is code   \u2551{NC}")
    print(f"{CYAN}  \u255a{'═' * 38}\u255d{NC}")
    print()

    # Check dependencies
    print(f"{YELLOW}Checking dependencies...{NC}")
    check_python()
    check_pygame()
    check_claude()

    # Install hooks
    print()
    print(f"{YELLOW}Installing Claude Code hooks...{NC}")
    install_hooks()

    # Done
    py = "python" if sys.platform == "win32" else "python3"
    print()
    print(f"{GREEN}Installation complete!{NC}")
    print()
    print(f"  Launch the fortress:")
    print(f"    {CYAN}cd {SCRIPT_DIR} && {py} gui.py{NC}")
    print()
    print(f"  Demo mode (no Claude Code needed):")
    print(f"    {CYAN}{py} gui.py --demo{NC}")
    print()
    print(f"  Then use Claude Code in another terminal and watch the mechs build.")
    print()
    print(f"{CYAN}The Emperor protects.{NC}")
    print()


if __name__ == "__main__":
    main()
