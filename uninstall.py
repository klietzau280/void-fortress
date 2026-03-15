#!/usr/bin/env python3
"""Void Fortress - cross-platform uninstaller.

Removes Claude Code hooks without affecting other settings.
Works on Windows, macOS, and Linux.
"""

import json
import os
import sys

SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")


def main():
    print()
    print("Removing Void Fortress hooks from Claude Code...")

    if not os.path.exists(SETTINGS_FILE):
        print("No settings file found. Nothing to remove.")
        return

    with open(SETTINGS_FILE, "r") as f:
        settings = json.load(f)

    hooks = settings.get("hooks", {})
    removed = 0
    to_delete = []

    for event, groups in hooks.items():
        new_groups = []
        for group in groups:
            # Remove hooks that reference hook.py or hook.sh
            new_hooks = [
                h for h in group.get("hooks", [])
                if "hook.py" not in h.get("command", "")
                and "hook.sh" not in h.get("command", "")
            ]
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

    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

    print(f"Removed {removed} hooks. Your other settings are untouched.")
    print()
    print("Done. The fortress sleeps.")
    print()


if __name__ == "__main__":
    main()
