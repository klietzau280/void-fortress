#!/usr/bin/env python3
"""Void Fortress - cross-platform hook for Claude Code.

Logs events to JSONL and plays sci-fi trooper voice lines.
Replaces hook.sh for Windows/macOS/Linux compatibility.
"""

import glob
import json
import os
import random
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(SCRIPT_DIR, "sounds")
EVENTS_DIR = os.path.expanduser("~/.agent-valley")
EVENTS_FILE = os.path.join(EVENTS_DIR, "events.jsonl")
LOCK_FILE = os.path.join(EVENTS_DIR, ".sound.lock")
PID_FILE = os.path.join(EVENTS_DIR, ".gui.pid")
VOLUME = 0.5
COOLDOWN = 3


def pick_random(prefix: str) -> str | None:
    """Pick a random sound file matching the prefix."""
    pattern = os.path.join(SOUNDS_DIR, f"{prefix}_*.*")
    files = glob.glob(pattern)
    if files:
        return random.choice(files)
    return None


EVENT_SOUND_MAP = {
    "SessionStart": "session_start",
    "UserPromptSubmit": "task_ack",
    "Stop": "task_done",
    "PostToolUseFailure": "error",
    "PermissionRequest": "input",
    "SubagentStart": "spawn",
    "SubagentStop": "explosion",
    "PreCompact": "compact",
}


def play_sound(sound_path: str) -> None:
    """Play a sound file cross-platform, non-blocking."""
    if sys.platform == "darwin":
        subprocess.Popen(
            ["afplay", "-v", str(VOLUME), sound_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    elif sys.platform == "win32":
        # Use pygame.mixer if available (already a dependency), else PowerShell
        try:
            import pygame.mixer
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(VOLUME)
            sound.play()
        except Exception:
            # Fallback: PowerShell media player (supports .wav/.aiff)
            ps_cmd = (
                f"(New-Object Media.SoundPlayer '{sound_path}').Play()"
            )
            subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
    else:
        # Linux — try aplay for wav, paplay for pulse, or ffplay
        for player in [["aplay", "-q"], ["paplay"], ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]]:
            try:
                subprocess.Popen(
                    player + [sound_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                break
            except FileNotFoundError:
                continue


def gui_is_running() -> bool:
    """Check if the GUI process is alive."""
    if not os.path.exists(PID_FILE):
        return False
    try:
        pid = int(open(PID_FILE).read().strip())
    except (ValueError, OSError):
        return False

    if sys.platform == "win32":
        # On Windows, use tasklist to check PID
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return str(pid) in result.stdout
        except Exception:
            return False
    else:
        # Unix — signal 0 checks if process exists
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def main():
    os.makedirs(EVENTS_DIR, exist_ok=True)

    # Read event from stdin
    raw = sys.stdin.read()
    if not raw.strip():
        return

    # Parse and log event
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return

    data["_ts"] = time.time()
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

    # Only play sounds if GUI is running
    if not gui_is_running():
        return

    event_name = data.get("hook_event_name", "")
    prefix = EVENT_SOUND_MAP.get(event_name)
    if not prefix:
        return

    sound = pick_random(prefix)
    if not sound or not os.path.isfile(sound):
        return

    # Cooldown check
    now = int(time.time())
    if os.path.exists(LOCK_FILE):
        try:
            last = int(open(LOCK_FILE).read().strip())
            if now - last < COOLDOWN:
                return
        except (ValueError, OSError):
            pass

    with open(LOCK_FILE, "w") as f:
        f.write(str(now))

    play_sound(sound)


if __name__ == "__main__":
    main()
