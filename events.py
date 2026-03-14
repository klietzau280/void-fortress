"""Void Fortress - event reader, tails the JSONL events file from Claude Code hooks."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import List, Optional


EVENTS_FILE = os.path.expanduser("~/.agent-valley/events.jsonl")


@dataclass
class HookEvent:
    timestamp: float
    event_name: str
    session_id: str
    tool_name: Optional[str] = None
    tool_input: Optional[dict] = None
    tool_response: Optional[str] = None
    agent_id: Optional[str] = None
    agent_type: Optional[str] = None
    subagent_type: Optional[str] = None
    cwd: Optional[str] = None
    prompt: Optional[str] = None
    error: Optional[str] = None
    raw: Optional[dict] = None

    @classmethod
    def from_json(cls, data: dict) -> HookEvent:
        return cls(
            timestamp=data.get("_ts", time.time()),
            event_name=data.get("hook_event_name", "unknown"),
            session_id=data.get("session_id", ""),
            tool_name=data.get("tool_name"),
            tool_input=data.get("tool_input"),
            tool_response=data.get("tool_response"),
            agent_id=data.get("agent_id"),
            agent_type=data.get("agent_type"),
            subagent_type=data.get("subagent_type"),
            cwd=data.get("cwd"),
            prompt=data.get("prompt"),
            error=data.get("error"),
            raw=data,
        )


# Map Claude Code tool names to activity categories
TOOL_ACTIVITY_MAP = {
    "Bash": "coding",
    "Read": "reading",
    "Edit": "coding",
    "Write": "coding",
    "Grep": "searching",
    "Glob": "searching",
    "Agent": "thinking",
    "WebSearch": "searching",
    "WebFetch": "reading",
    "Skill": "coding",
    "NotebookEdit": "coding",
    "TaskCreate": "thinking",
    "TaskUpdate": "thinking",
}

# Map subagent types to roles
SUBAGENT_ROLE_MAP = {
    "Explore": "explorer",
    "Plan": "planner",
    "general-purpose": "coder",
    "claude-code-guide": "researcher",
    "statusline-setup": "fixer",
}


def tool_to_activity(tool_name: Optional[str]) -> str:
    """Convert a Claude Code tool name to an activity."""
    if not tool_name:
        return "thinking"
    # Handle MCP tools
    if tool_name.startswith("mcp__"):
        parts = tool_name.split("__")
        if "search" in tool_name.lower():
            return "searching"
        if "read" in tool_name.lower() or "get" in tool_name.lower():
            return "reading"
        if "create" in tool_name.lower() or "edit" in tool_name.lower() or "write" in tool_name.lower():
            return "coding"
        return "coding"
    return TOOL_ACTIVITY_MAP.get(tool_name, "thinking")


def tool_to_description(tool_name: Optional[str], tool_input: Optional[dict]) -> str:
    """Generate a human-readable description of what the tool is doing."""
    if not tool_name:
        return ""

    inp = tool_input or {}

    if tool_name == "Bash":
        cmd = inp.get("command", "")
        desc = inp.get("description", "")
        if desc:
            return desc
        # Truncate long commands
        return f"$ {cmd[:50]}..." if len(cmd) > 50 else f"$ {cmd}"

    if tool_name == "Read":
        path = inp.get("file_path", "???")
        return f"Reading {os.path.basename(path)}"

    if tool_name == "Edit":
        path = inp.get("file_path", "???")
        return f"Editing {os.path.basename(path)}"

    if tool_name == "Write":
        path = inp.get("file_path", "???")
        return f"Writing {os.path.basename(path)}"

    if tool_name == "Grep":
        pattern = inp.get("pattern", "???")
        return f'Searching for "{pattern[:30]}"'

    if tool_name == "Glob":
        pattern = inp.get("pattern", "???")
        return f"Finding files: {pattern[:30]}"

    if tool_name == "Agent":
        desc = inp.get("description", "")
        stype = inp.get("subagent_type", "")
        return f"Spawning {stype or 'agent'}: {desc}" if desc else f"Spawning {stype or 'agent'}"

    if tool_name == "WebSearch":
        query = inp.get("query", "???")
        return f'Searching web: "{query[:30]}"'

    if tool_name == "Skill":
        skill = inp.get("skill", "???")
        return f"Running /{skill}"

    if tool_name.startswith("mcp__"):
        parts = tool_name.split("__")
        server = parts[1] if len(parts) > 1 else "mcp"
        method = parts[2] if len(parts) > 2 else tool_name
        return f"{server}: {method}"

    return tool_name


class EventReader:
    """Tails the events JSONL file for new events."""

    def __init__(self):
        self.file_path = EVENTS_FILE
        self.file_pos = 0
        self._init_position()

    def _init_position(self):
        """Start reading from current end of file (only show new events)."""
        if os.path.exists(self.file_path):
            self.file_pos = os.path.getsize(self.file_path)

    def read_new_events(self) -> List[HookEvent]:
        """Read any new events since last check."""
        if not os.path.exists(self.file_path):
            return []

        events = []
        try:
            with open(self.file_path, "r") as f:
                f.seek(self.file_pos)
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        events.append(HookEvent.from_json(data))
                    except json.JSONDecodeError:
                        continue
                self.file_pos = f.tell()
        except IOError:
            pass

        return events

    def read_recent_events(self, max_events: int = 50) -> List[HookEvent]:
        """Read the most recent N events from the file (for startup context)."""
        if not os.path.exists(self.file_path):
            return []

        events = []
        try:
            with open(self.file_path, "r") as f:
                lines = f.readlines()
                for line in lines[-max_events:]:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        events.append(HookEvent.from_json(data))
                    except json.JSONDecodeError:
                        continue
        except IOError:
            pass

        return events
