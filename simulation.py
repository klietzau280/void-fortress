"""Void Fortress - simulation engine driven by real Claude Code hook events."""

from __future__ import annotations

import random
import time
from agents import Agent, AgentRole, Mood, THOUGHTS, spawn_agent, AGENT_NAMES, PERSONALITY_TRAITS
from world import World
from events import (
    EventReader, HookEvent, tool_to_activity, tool_to_description,
    SUBAGENT_ROLE_MAP,
)

# -- Bootstrap --
BOOTSTRAP_EVENT_LIMIT = 100
BOOTSTRAP_REPLAY_COUNT = 20

# -- Agent spawning --
SESSION_SPAWN_X_RANGE = (5, 40)
SESSION_SPAWN_Y_RANGE = (4, 15)
SUBAGENT_OFFSET_X = 5
SUBAGENT_OFFSET_Y = 3

# -- Zone movement --
ZONE_OFFSET_X = 3
ZONE_OFFSET_Y = 2
ZONE_CLAMP_MARGIN_X = 10
ZONE_CLAMP_MARGIN_Y = 6

# -- Task completion --
TASK_COMPLETE_CHANCE = 0.15

# -- Error handling --
NECRON_PANIC_CHANCE = 0.5
ERROR_THOUGHT_TIMER = 5.0

# -- Prompt display --
PROMPT_TRUNCATE_LEN = 35
PROMPT_THOUGHT_TIMER = 5.0

# -- Idle behavior --
IDLE_ZONE_PROXIMITY_X = 5
IDLE_ZONE_PROXIMITY_Y = 4
IDLE_OFFSET_RANGE = 2
IDLE_CLAMP_MARGIN = 4

# -- Wandering --
WANDER_CHANCE = 0.02
WANDER_MAX_X = 65
WANDER_MAX_Y = 22

# -- Thought refresh --
THOUGHT_TIMER_MIN = 3.0
THOUGHT_TIMER_MAX = 7.0
MOVE_TICK_DIVISOR = 3

# -- Satisfaction --
SATISFACTION_SMOOTHING = 0.9
SATISFACTION_NEW_WEIGHT = 0.1

# -- Demo mode --
DEMO_TICK_CHANCE = 0.03
DEMO_SPAWN_CHANCE = 0.08
DEMO_MAX_AGENTS = 8
DEMO_DESPAWN_CHANCE = 0.05


# Map activity to mood tendencies
ACTIVITY_MOOD_WEIGHTS = {
    "coding": [Mood.FOCUSED, Mood.FOCUSED, Mood.HAPPY, Mood.THINKING],
    "reading": [Mood.THINKING, Mood.FOCUSED, Mood.HAPPY, Mood.BORED],
    "searching": [Mood.THINKING, Mood.CONFUSED, Mood.FOCUSED, Mood.FRUSTRATED],
    "testing": [Mood.FOCUSED, Mood.HAPPY, Mood.PANICKING, Mood.ECSTATIC],
    "fixing": [Mood.FRUSTRATED, Mood.FOCUSED, Mood.THINKING, Mood.PANICKING],
    "thinking": [Mood.THINKING, Mood.THINKING, Mood.FOCUSED, Mood.CONFUSED],
    "waiting": [Mood.BORED, Mood.BORED, Mood.FRUSTRATED, Mood.HAPPY],
    "celebrating": [Mood.ECSTATIC, Mood.HAPPY, Mood.ECSTATIC, Mood.HAPPY],
    "panicking": [Mood.PANICKING, Mood.FRUSTRATED, Mood.PANICKING, Mood.CONFUSED],
    "idle": [Mood.BORED, Mood.HAPPY, Mood.THINKING, Mood.BORED],
}


class Simulation:
    def __init__(self, demo_mode: bool = False):
        self.world = World()
        self.agents: list[Agent] = []
        self.next_agent_id = 0
        self.last_update = time.time()
        self.speed = 1.0
        self.paused = False
        self.total_tasks_completed = 0
        self.total_tool_calls = 0
        self.incidents = 0
        self.agent_satisfaction = 0.75
        self.selected_agent_id: int | None = None
        self.demo_mode = demo_mode

        # Event tracking
        self.event_reader = EventReader()
        self.active_sessions: dict[str, int] = {}  # session_id -> agent_id
        self.subagent_map: dict[str, int] = {}  # agent_id (hook) -> agent_id (sim)
        self.session_context_pct: dict[str, float] = {}  # session_id -> last known ctx %
        self.last_event_time: float = 0
        self.waiting_for_events = True

        # Bootstrap from recent events to show current state
        self._bootstrap_from_recent()

    def _next_id(self) -> int:
        aid = self.next_agent_id
        self.next_agent_id += 1
        return aid

    def _bootstrap_from_recent(self):
        """Read recent events to reconstruct current state."""
        events = self.event_reader.read_recent_events(BOOTSTRAP_EVENT_LIMIT)
        if not events:
            self.waiting_for_events = True
            return

        # Find active sessions from recent events
        active_sessions = set()
        ended_sessions = set()
        for e in events:
            if e.event_name == "SessionStart":
                active_sessions.add(e.session_id)
            elif e.event_name == "SessionEnd":
                ended_sessions.add(e.session_id)

        # Sessions that started but didn't end are probably still running
        still_active = active_sessions - ended_sessions

        # Create agents for active sessions
        for sid in still_active:
            self._ensure_session_agent(sid)

        # Replay recent tool uses to set current activity
        for e in events[-BOOTSTRAP_REPLAY_COUNT:]:
            if e.session_id in still_active:
                self._process_event(e, notify=False)

        if self.agents:
            self.waiting_for_events = False

        # Move file position to end so we only get new events going forward
        self.event_reader._init_position()

    def _ensure_session_agent(self, session_id: str) -> Agent:
        """Get or create the main agent for a session."""
        if session_id in self.active_sessions:
            agent_id = self.active_sessions[session_id]
            for a in self.agents:
                if a.id == agent_id:
                    return a

        # Create new main agent for this session
        agent = spawn_agent(self._next_id(), AgentRole.MAIN)
        # Keep the random name from spawn_agent
        agent.is_subagent = False
        agent.activity = "thinking"
        agent.thought = "Starting up..."
        agent.x = random.randint(*SESSION_SPAWN_X_RANGE)
        agent.y = random.randint(*SESSION_SPAWN_Y_RANGE)
        agent.target_x = agent.x
        agent.target_y = agent.y
        self.agents.append(agent)
        self.active_sessions[session_id] = agent.id
        self.waiting_for_events = False
        return agent

    def _spawn_subagent_for_event(self, event: HookEvent) -> Agent:
        """Spawn a subagent based on a SubagentStart or Agent tool event."""
        subagent_type = event.subagent_type or "general-purpose"
        role_name = SUBAGENT_ROLE_MAP.get(subagent_type, "coder")
        role = AgentRole(role_name) if role_name in [r.value for r in AgentRole] else AgentRole.CODER

        # Find parent
        parent_id = self.active_sessions.get(event.session_id)

        agent = spawn_agent(self._next_id(), role, parent_id=parent_id, is_subagent=True)

        # Spawn near parent
        parent = None
        if parent_id is not None:
            parent = next((a for a in self.agents if a.id == parent_id), None)
        if parent:
            agent.x = parent.x + random.randint(-SUBAGENT_OFFSET_X, SUBAGENT_OFFSET_X)
            agent.y = parent.y + random.randint(-SUBAGENT_OFFSET_Y, SUBAGENT_OFFSET_Y)
            agent.x = max(2, min(self.world.width - ZONE_CLAMP_MARGIN_X, agent.x))
            agent.y = max(2, min(self.world.height - ZONE_CLAMP_MARGIN_Y, agent.y))

        agent.activity = "thinking"
        agent.thought = f"Spawned as {subagent_type}..."

        # Use the hook's agent_id to track this subagent
        hook_agent_id = event.agent_id or f"sub-{self.next_agent_id}"
        self.subagent_map[hook_agent_id] = agent.id

        self.agents.append(agent)
        return agent

    def _find_agent_for_event(self, event: HookEvent) -> Agent | None:
        """Find which simulation agent corresponds to a hook event."""
        # If the event has an agent_id, check if it's a known subagent
        if event.agent_id and event.agent_id in self.subagent_map:
            sim_id = self.subagent_map[event.agent_id]
            for a in self.agents:
                if a.id == sim_id:
                    return a

        # Otherwise it's the main session agent
        if event.session_id in self.active_sessions:
            sim_id = self.active_sessions[event.session_id]
            for a in self.agents:
                if a.id == sim_id:
                    return a

        return None

    def get_worst_context_pct(self) -> float | None:
        """Return the highest context window usage across active sessions, or None."""
        if not self.session_context_pct:
            return None
        active_pcts = [self.session_context_pct[sid]
                       for sid in self.active_sessions
                       if sid in self.session_context_pct]
        return max(active_pcts) if active_pcts else None

    def get_session_context_bars(self) -> list[tuple[str, float]]:
        """Return list of (agent_name, used_pct) for active sessions with context data."""
        bars = []
        for sid, agent_id in self.active_sessions.items():
            if sid not in self.session_context_pct:
                continue
            pct = self.session_context_pct[sid]
            name = "???"
            for a in self.agents:
                if a.id == agent_id:
                    name = a.name
                    break
            bars.append((name, pct))
        # Sort by usage descending so hottest session is first
        bars.sort(key=lambda b: b[1], reverse=True)
        return bars

    def _process_event(self, event: HookEvent, notify: bool = True):
        """Process a single hook event and update simulation state."""
        self.last_event_time = event.timestamp

        # Track context window usage per session
        if event.context_window_pct is not None and event.session_id:
            self.session_context_pct[event.session_id] = event.context_window_pct

        if event.event_name == "SessionStart":
            agent = self._ensure_session_agent(event.session_id)
            agent.activity = "idle"
            agent.thought = "Session started!"
            agent.mood = Mood.HAPPY
            if notify:
                project = event.cwd or "unknown"
                project = project.split("/")[-1] if "/" in project else project
                self.world.add_notification(
                    f"Claude session started in {project}",
                    "🟢", "\033[92m",
                )

        elif event.event_name == "SessionEnd":
            agent = self._find_agent_for_event(event)
            if agent:
                if notify:
                    self.world.add_notification(
                        f"{agent.name} session ended",
                        "🔴", "\033[91m",
                    )
                self.agents.remove(agent)
                self.active_sessions.pop(event.session_id, None)
                self.session_context_pct.pop(event.session_id, None)

        elif event.event_name == "SubagentStart":
            agent = self._spawn_subagent_for_event(event)
            if notify:
                stype = event.subagent_type or "agent"
                self.world.add_notification(
                    f"{agent.name} spawned as {stype}!",
                    "👋", "\033[92m",
                )

        elif event.event_name == "SubagentStop":
            hook_id = event.agent_id
            if hook_id and hook_id in self.subagent_map:
                sim_id = self.subagent_map.pop(hook_id)
                agent = next((a for a in self.agents if a.id == sim_id), None)
                if agent:
                    if notify:
                        necron_kills = [
                            f"NECRON AMBUSH! {agent.name} destroyed!",
                            f"{agent.name} vaporized by gauss flayer!",
                            f"Tomb Wraith claimed {agent.name}!",
                            f"{agent.name} fell to Necron fire!",
                            f"Deathmark targeted {agent.name}. No survivors.",
                            f"Scarabs consumed {agent.name}'s mech!",
                            f"{agent.name} phased out — Necron translocation!",
                            f"Doomsday beam hit {agent.name}!",
                        ]
                        self.world.add_notification(
                            random.choice(necron_kills),
                            "💀", "\033[91m",
                        )
                    self.agents.remove(agent)

        elif event.event_name in ("PreToolUse", "PostToolUse"):
            agent = self._find_agent_for_event(event)
            if not agent:
                agent = self._ensure_session_agent(event.session_id)

            activity = tool_to_activity(event.tool_name)
            description = tool_to_description(event.tool_name, event.tool_input)

            agent.activity = activity
            if description:
                agent.thought = description
                agent.thought_timer = 4.0

            # Move toward appropriate zone (non-build activities only)
            # Build activities (coding, fixing, testing) are positioned by the GUI
            # which flies them to the station build site
            if activity not in ("coding", "fixing", "testing"):
                zone = self.world.get_zone_for_activity(activity)
                cx, cy = zone.center()
                agent.target_x = cx + random.randint(-ZONE_OFFSET_X, ZONE_OFFSET_X)
                agent.target_y = cy + random.randint(-ZONE_OFFSET_Y, ZONE_OFFSET_Y)
                agent.target_x = max(2, min(self.world.width - ZONE_CLAMP_MARGIN_X, agent.target_x))
                agent.target_y = max(2, min(self.world.height - ZONE_CLAMP_MARGIN_Y, agent.target_y))

            # Update mood based on activity
            mood_options = ACTIVITY_MOOD_WEIGHTS.get(activity, [Mood.THINKING])
            if random.random() > agent.mood_stability:
                agent.mood = random.choice(mood_options)

            if event.event_name == "PostToolUse":
                self.total_tool_calls += 1
                if random.random() < TASK_COMPLETE_CHANCE:
                    agent.tasks_completed += 1
                    self.total_tasks_completed += 1

            # Agent tool = subagent about to spawn
            if event.tool_name == "Agent" and event.event_name == "PreToolUse":
                desc = (event.tool_input or {}).get("description", "")
                if notify and desc:
                    self.world.add_notification(
                        f"Delegating: {desc}",
                        "🔀", "\033[96m",
                    )

        elif event.event_name == "PostToolUseFailure":
            agent = self._find_agent_for_event(event)
            if agent:
                # Necron incursion on errors
                if random.random() < NECRON_PANIC_CHANCE:
                    agent.activity = "panicking"
                    agent.mood = Mood.PANICKING
                    agent.thought = random.choice(THOUGHTS["panicking"])
                else:
                    agent.activity = "fixing"
                    agent.mood = Mood.FRUSTRATED
                    agent.thought = random.choice(THOUGHTS["fixing"])
                agent.thought_timer = ERROR_THOUGHT_TIMER
                self.incidents += 1
                necron_alerts = [
                    f"NECRON INCURSION! {agent.name} under attack!",
                    f"{agent.name}: Tomb World signature detected!",
                    f"Gauss flayer hit on {event.tool_name}!",
                    f"{agent.name}: Xenos corruption in {event.tool_name}!",
                    f"Scarab swarm consuming {event.tool_name}!",
                    f"Cryptek interference on {event.tool_name}!",
                ]
                if notify:
                    self.world.add_notification(
                        random.choice(necron_alerts),
                        "💥", "\033[91m",
                    )

        elif event.event_name == "UserPromptSubmit":
            agent = self._find_agent_for_event(event)
            if not agent:
                agent = self._ensure_session_agent(event.session_id)
            agent.activity = "thinking"
            agent.mood = Mood.FOCUSED
            prompt = event.prompt or ""
            if prompt:
                agent.thought = f'User: "{prompt[:PROMPT_TRUNCATE_LEN]}..."' if len(prompt) > PROMPT_TRUNCATE_LEN else f'User: "{prompt}"'
            else:
                agent.thought = "New instructions received!"
            agent.thought_timer = PROMPT_THOUGHT_TIMER
            if notify:
                self.world.add_notification(
                    "New user prompt received",
                    "💬", "\033[97m",
                )

        elif event.event_name == "Stop":
            agent = self._find_agent_for_event(event)
            if agent:
                agent.activity = "waiting"
                agent.thought = "Done! Waiting for feedback..."
                agent.mood = Mood.HAPPY
                agent.thought_timer = 8.0

        elif event.event_name == "Notification":
            if notify:
                self.world.add_notification(
                    "Claude needs attention",
                    "🔔", "\033[93m",
                )

        elif event.event_name == "PreCompact":
            agent = self._find_agent_for_event(event)
            if agent:
                agent.thought = "Memory getting full... compacting!"
                agent.mood = Mood.CONFUSED
                agent.activity = "thinking"
                if notify:
                    self.world.add_notification(
                        "Context compaction in progress",
                        "🗜️", "\033[95m",
                    )

        elif event.event_name == "PermissionRequest":
            agent = self._find_agent_for_event(event)
            if agent:
                agent.thought = "Asking for permission..."
                agent.mood = Mood.THINKING
                agent.activity = "waiting"

    def update(self):
        """Main simulation tick."""
        if self.paused:
            return

        now = time.time()
        dt = (now - self.last_update) * self.speed
        self.last_update = now
        self.world.tick += 1

        # Read new events from Claude Code
        new_events = self.event_reader.read_new_events()
        for event in new_events:
            self._process_event(event)

        # Update agent animations
        for agent in self.agents:
            if self.world.tick % MOVE_TICK_DIVISOR == 0:
                agent.move_toward_target()

            # Thought bubble decay
            agent.thought_timer -= dt
            if agent.thought_timer <= 0:
                agent.thought = random.choice(THOUGHTS.get(agent.activity, THOUGHTS["idle"]))
                agent.thought_timer = random.uniform(THOUGHT_TIMER_MIN, THOUGHT_TIMER_MAX)

            # Gradual mood drift
            agent.update_mood(dt)

            # Idle/waiting agents fly to the bottom-right corner and chill
            if agent.activity in ("idle", "waiting"):
                idle_zone = self.world.get_zone_for_activity("idle")
                zx, zy = idle_zone.center()
                if abs(agent.target_x - zx) > IDLE_ZONE_PROXIMITY_X or abs(agent.target_y - zy) > IDLE_ZONE_PROXIMITY_Y:
                    agent.target_x = zx + random.randint(-IDLE_OFFSET_RANGE, IDLE_OFFSET_RANGE)
                    agent.target_y = zy + random.randint(-1, 1)
                    agent.target_x = max(2, min(self.world.width - IDLE_CLAMP_MARGIN, agent.target_x))
                    agent.target_y = max(2, min(self.world.height - IDLE_CLAMP_MARGIN, agent.target_y))
            # Build activities stay put (GUI positions them at the station)
            elif agent.activity in ("coding", "fixing", "testing"):
                pass
            # Other active agents wander within their zone
            elif (agent.x == agent.target_x and agent.y == agent.target_y
                    and random.random() < WANDER_CHANCE):
                agent.set_new_wander_target(min(self.world.width, WANDER_MAX_X), min(self.world.height, WANDER_MAX_Y))

        # Update notifications
        self.world.update_notifications(now)

        # Update satisfaction
        if self.agents:
            moods = [a.mood for a in self.agents]
            happy = sum(1 for m in moods if m in (Mood.HAPPY, Mood.ECSTATIC, Mood.FOCUSED))
            self.agent_satisfaction = SATISFACTION_SMOOTHING * self.agent_satisfaction + SATISFACTION_NEW_WEIGHT * (happy / len(moods))

        # Demo mode fallback
        if self.demo_mode and not new_events and random.random() < DEMO_TICK_CHANCE:
            self._demo_tick()

    def _demo_tick(self):
        """Generate fake activity for demo mode."""
        if not self.agents:
            agent = spawn_agent(self._next_id(), AgentRole.MAIN)
            self.agents.append(agent)
            self.world.add_notification("Demo session started!", "🎮", "\033[92m")

        if random.random() < DEMO_SPAWN_CHANCE and len(self.agents) < DEMO_MAX_AGENTS:
            role = random.choice(list(AgentRole))
            agent = spawn_agent(self._next_id(), role, parent_id=self.agents[0].id, is_subagent=True)
            self.agents.append(agent)
            self.world.add_notification(f"{agent.name} ({role.value}) spawned!", "👋", "\033[92m")

        if random.random() < DEMO_DESPAWN_CHANCE:
            subs = [a for a in self.agents if a.is_subagent]
            if subs:
                gone = random.choice(subs)
                self.agents.remove(gone)
                self.world.add_notification(f"{gone.name} finished up!", "👋", "\033[93m")

        if self.agents:
            agent = random.choice(self.agents)
            activities = ["coding", "reading", "searching", "thinking", "testing", "fixing"]
            agent.activity = random.choice(activities)
            agent.thought_timer = 0
            zone = self.world.get_zone_for_activity(agent.activity)
            cx, cy = zone.center()
            agent.target_x = cx + random.randint(-ZONE_OFFSET_X, ZONE_OFFSET_X)
            agent.target_y = cy + random.randint(-ZONE_OFFSET_Y, ZONE_OFFSET_Y)
            agent.target_x = max(2, min(self.world.width - ZONE_CLAMP_MARGIN_X, agent.target_x))
            agent.target_y = max(2, min(self.world.height - ZONE_CLAMP_MARGIN_Y, agent.target_y))

    def get_selected_agent(self):
        if self.selected_agent_id is not None:
            for a in self.agents:
                if a.id == self.selected_agent_id:
                    return a
        return None

    def select_next_agent(self):
        if not self.agents:
            return
        if self.selected_agent_id is None:
            self.selected_agent_id = self.agents[0].id
        else:
            ids = [a.id for a in self.agents]
            try:
                idx = ids.index(self.selected_agent_id)
                self.selected_agent_id = ids[(idx + 1) % len(ids)]
            except ValueError:
                self.selected_agent_id = ids[0]

    def select_prev_agent(self):
        if not self.agents:
            return
        if self.selected_agent_id is None:
            self.selected_agent_id = self.agents[-1].id
        else:
            ids = [a.id for a in self.agents]
            try:
                idx = ids.index(self.selected_agent_id)
                self.selected_agent_id = ids[(idx - 1) % len(ids)]
            except ValueError:
                self.selected_agent_id = ids[0]
