#!/usr/bin/env python3
"""
VOID FORTRESS - Pygame graphical UI.
Construction mechs build a space fortress as your AI agents work.
"""

from __future__ import annotations

import os
import sys
import random
import time
import math
import pygame

from simulation import Simulation
from agents import Agent, Mood, AgentRole
from sprites import (
    PALETTE, HULL_COLORS,
    create_agent_sprites, create_mood_icon,
    create_thought_bubble, create_pilot_portrait,
)
from station import Station

# Screen
WINDOW_W = 960
WINDOW_H = 640
FPS = 30
UI_H = 110


class InfoPopup:
    """Pilot dossier popup when you click a mech."""

    WIDTH = 270
    HEIGHT = 210

    def __init__(self):
        self.visible = False
        self.agent_id = None
        self.x = 0
        self.y = 0
        self.close_rect = pygame.Rect(0, 0, 0, 0)

    def show(self, agent_id, sx, sy, sw, sh):
        self.visible = True
        self.agent_id = agent_id
        self.x = min(sx + 20, sw - self.WIDTH - 10)
        self.y = min(sy - 40, sh - self.HEIGHT - 10)
        self.x = max(10, self.x)
        self.y = max(10, self.y)

    def hide(self):
        self.visible = False
        self.agent_id = None

    def hit_test(self, mx, my):
        if not self.visible:
            return False
        return (self.x <= mx <= self.x + self.WIDTH and
                self.y <= my <= self.y + self.HEIGHT)

    def hit_close(self, mx, my):
        return self.close_rect.collidepoint(mx, my)

    def draw(self, screen, agent, mood_icons, font, font_large, font_small,
             agent_visuals=None):
        if not self.visible or not agent:
            return

        bg = (14, 18, 32)
        border = (45, 55, 85)
        accent = (80, 200, 255)

        popup_rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
        shadow = pygame.Surface((self.WIDTH + 4, self.HEIGHT + 4), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 80))
        screen.blit(shadow, (self.x + 3, self.y + 3))

        pygame.draw.rect(screen, bg, popup_rect)
        pygame.draw.rect(screen, border, popup_rect, 2)

        # Close button
        self.close_rect = pygame.Rect(self.x + self.WIDTH - 20, self.y + 4, 14, 14)
        pygame.draw.rect(screen, (140, 35, 35), self.close_rect, border_radius=2)
        x_surf = font_small.render("x", True, (200, 200, 200))
        screen.blit(x_surf, (self.close_rect.x + 3, self.close_rect.y + 1))

        left = self.x + 12
        cy = self.y + 10

        # Portrait (left side)
        portrait_size = 62
        portrait_seed = agent.id * 7919
        if agent_visuals and agent.id in agent_visuals:
            portrait_seed = agent_visuals[agent.id].portrait_seed
        portrait = create_pilot_portrait(portrait_seed, agent.mood.label, portrait_size)
        px = left
        py = cy
        border_rect = pygame.Rect(px - 2, py - 2, portrait_size + 4, portrait_size + 4)
        pygame.draw.rect(screen, border, border_rect)
        screen.blit(portrait, (px, py))

        # Name + rank (right of portrait)
        info_x = left + portrait_size + 10

        name_surf = font_large.render(agent.name, True, (230, 235, 245))
        screen.blit(name_surf, (info_x, cy))

        role_color = {
            "main": accent, "explorer": (80, 200, 255),
            "coder": (80, 220, 100), "tester": (200, 120, 255),
            "researcher": (120, 140, 255), "reviewer": (200, 200, 220),
            "fixer": (255, 100, 80), "planner": (80, 200, 255),
        }.get(agent.role.value, accent)
        rank = "CAPTAIN" if not agent.is_subagent else agent.role.value[:3].upper()
        rank_surf = font_small.render(rank, True, (15, 18, 30))
        badge_w = rank_surf.get_width() + 8
        badge_rect = pygame.Rect(info_x, cy + 22, badge_w, 16)
        pygame.draw.rect(screen, role_color, badge_rect, border_radius=3)
        screen.blit(rank_surf, (badge_rect.x + 4, badge_rect.y + 2))

        cy = py + portrait_size + 8

        # Mood bar - colored strip
        mood_color = {
            "happy": (60, 200, 60), "ecstatic": (255, 220, 40),
            "focused": (60, 170, 255), "thinking": (90, 110, 230),
            "confused": (190, 90, 230), "frustrated": (230, 50, 40),
            "bored": (110, 110, 125), "panicking": (255, 30, 30),
        }.get(agent.mood.label, (120, 120, 140))
        bar_rect = pygame.Rect(left, cy, self.WIDTH - 24, 20)
        pygame.draw.rect(screen, (25, 30, 48), bar_rect, border_radius=3)
        pygame.draw.rect(screen, mood_color, bar_rect, border_radius=3)
        mood_txt = font.render(f"  {agent.mood.label.upper()}  ·  {agent.activity}", True, (15, 18, 30))
        screen.blit(mood_txt, (left + 6, cy + 2))
        cy += 28

        # Divider
        pygame.draw.line(screen, border, (left, cy), (self.x + self.WIDTH - 12, cy), 1)
        cy += 8

        # Stats grid - clean two-column layout
        stats = [
            ("Personality", agent.personality),
            ("Energy", f"{agent.energy:.0%}"),
            ("Operations", str(agent.tasks_completed)),
        ]
        if agent.is_subagent:
            stats.insert(0, ("Type", "Subagent"))

        for label, value in stats:
            label_surf = font_small.render(label, True, (70, 78, 105))
            value_surf = font.render(value, True, (190, 195, 215))
            screen.blit(label_surf, (left, cy))
            screen.blit(value_surf, (left + 90, cy - 1))
            cy += 20

        # Thought at bottom
        cy += 2
        pygame.draw.line(screen, border, (left, cy), (self.x + self.WIDTH - 12, cy), 1)
        cy += 6
        if agent.thought:
            thought = agent.thought[:45] + "..." if len(agent.thought) > 45 else agent.thought
            thought_surf = font_small.render(f'"{thought}"', True, (100, 150, 130))
            screen.blit(thought_surf, (left, cy))


# Session colors - each session gets one hull color
SESSION_COLORS = [
    "hull_acc_blue", "hull_acc_red", "hull_acc_green", "hull_acc_purple",
    "hull_acc_orange", "hull_acc_cyan", "hull_acc_yellow", "hull_acc_dark",
]


class AgentVisual:
    """Visual state for an agent."""

    def __init__(self, agent: Agent, session_color: str = ""):
        self.agent_id = agent.id
        hull_color = session_color or random.choice(HULL_COLORS)
        self.session_color = hull_color
        self.sprites = create_agent_sprites("", hull_color, scale=3)
        self.portrait_seed = agent.id * 7919 + hash(agent.name) % 10000  # unique per agent
        self.px = float(agent.x * 8 + 80)
        self.py = float(agent.y * 12 + 60)
        self.target_px = self.px
        self.target_py = self.py
        self.walk_frame = 0
        self.walk_timer = 0.0
        self.bubble_surface = None
        self.bubble_text = ""
        self.bubble_timer = 0.0
        self.bounce = 0.0
        self.float_phase = random.uniform(0, 6.28)  # unique float offset
        self.sitting = False
        self.bench_pos = None
        self.moving = False
        self._override_target = False  # when True, don't follow sim coords

    def update(self, agent: Agent, dt: float, font: pygame.font.Font):
        if not self.sitting and not self._override_target:
            self.target_px = float(agent.x * 8 + 80)
            self.target_py = float(agent.y * 12 + 60)

        # Clear override once we've arrived
        if self._override_target:
            dx = self.target_px - self.px
            dy = self.target_py - self.py
            if math.sqrt(dx * dx + dy * dy) < 3:
                self._override_target = False

        speed = 150.0  # mechs move fast
        dx = self.target_px - self.px
        dy = self.target_py - self.py
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 1:
            move = min(speed * dt, dist)
            self.px += dx / dist * move
            self.py += dy / dist * move
            self.walk_timer += dt
            if self.walk_timer > 0.15:
                self.walk_frame = (self.walk_frame + 1) % 2
                self.walk_timer = 0
            self.moving = True
        else:
            self.px = self.target_px
            self.py = self.target_py
            self.moving = False

        # Mechs always bob gently in zero-g
        self.bounce = math.sin(time.time() * 1.2 + self.float_phase) * 3

        if agent.thought != self.bubble_text:
            self.bubble_text = agent.thought
            if agent.thought:
                self.bubble_surface = create_thought_bubble(agent.thought, font, max_width=180)
            else:
                self.bubble_surface = None
            self.bubble_timer = 5.0
        self.bubble_timer -= dt

    def get_sprite(self, agent: Agent):
        if self.sitting:
            return self.sprites["sit"]
        if agent.mood == Mood.ECSTATIC or agent.mood == Mood.PANICKING:
            return self.sprites["celebrate"]  # boost/afterburner
        if self.moving:
            return self.sprites["walk1"] if self.walk_frame == 0 else self.sprites["walk2"]
        return self.sprites["stand"]

    def draw(self, screen, agent, mood_icons, selected, cam_x, cam_y):
        sx = int(self.px - cam_x)
        sy = int(self.py - cam_y + self.bounce)
        sprite = self.get_sprite(agent)
        # Use idle sprite height for consistent name placement
        idle_h = self.sprites["stand"].get_height()
        mech_w = sprite.get_width()

        # Engine glow beneath mech when moving
        if self.moving:
            glow_w = mech_w // 2
            glow_h = 6
            glow = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
            glow_alpha = int(80 + 40 * math.sin(time.time() * 12))
            glow.fill((255, 140, 30, glow_alpha))
            screen.blit(glow, (sx + mech_w // 2 - glow_w // 2,
                               sy + idle_h))

        screen.blit(sprite, (sx, sy))

        if selected:
            rect = pygame.Rect(sx - 2, sy - 2, mech_w + 4, idle_h + 4)
            pygame.draw.rect(screen, (255, 255, 100), rect, 2, border_radius=3)

        # Name tag to the RIGHT of the mech
        name_font = pygame.font.SysFont(None, 16)
        name_surf = name_font.render(agent.name, True, PALETTE["white"])
        name_bg = pygame.Surface((name_surf.get_width() + 6, name_surf.get_height() + 2), pygame.SRCALPHA)
        name_bg.fill((0, 0, 0, 140))
        nx = sx + mech_w + 4
        ny = sy + idle_h // 2 - name_bg.get_height() // 2
        screen.blit(name_bg, (nx, ny))
        screen.blit(name_surf, (nx + 3, ny + 1))

        if agent.is_subagent:
            tag_font = pygame.font.SysFont(None, 13)
            tag = tag_font.render(agent.role.value, True, (180, 180, 255))
            screen.blit(tag, (nx, ny + name_bg.get_height() + 1))

        # Mood icon to the right of the name
        mood_icon = mood_icons.get(agent.mood.label)
        if mood_icon:
            screen.blit(mood_icon, (nx + name_bg.get_width() + 2, ny))

        # Thought bubble above mech
        if self.bubble_surface and self.bubble_timer > 0:
            bx = sx + mech_w // 2 - self.bubble_surface.get_width() // 2
            by = sy - self.bubble_surface.get_height() - 6
            if self.bubble_timer < 1.0:
                self.bubble_surface.set_alpha(int(self.bubble_timer * 255))
            else:
                self.bubble_surface.set_alpha(255)
            screen.blit(self.bubble_surface, (bx, by))


class GUI:
    def __init__(self, demo_mode: bool = False):
        pygame.init()
        pygame.display.set_caption("Void Fortress")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 18)
        self.font_large = pygame.font.SysFont(None, 28)
        self.font_title = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 14)

        # Clear stale events so we don't replay old session data
        self._data_dir = os.path.expanduser("~/.agent-valley")
        os.makedirs(self._data_dir, exist_ok=True)
        events_file = os.path.join(self._data_dir, "events.jsonl")
        if os.path.exists(events_file):
            open(events_file, "w").close()

        # Write PID file so hook.sh knows we're running (enables sounds)
        self._pid_file = os.path.join(self._data_dir, ".gui.pid")
        with open(self._pid_file, "w") as f:
            f.write(str(os.getpid()))

        self.sim = Simulation(demo_mode=demo_mode)
        self.agent_visuals: dict[int, AgentVisual] = {}
        self.mood_icons: dict[str, pygame.Surface] = {}
        self._session_colors: dict[int, str] = {}  # session_key -> hull color
        self._pending_core = None  # queued core build waiting for mech arrival

        # The station - grows as agents work
        self.station = Station()
        self.station.reset()

        # Camera
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.dragging = False
        self.drag_start = (0, 0)
        self.cam_drag_start = (0.0, 0.0)

        # Info popup
        self.info_popup = InfoPopup()

        # Notification display
        self.notification_surfs: list[tuple[pygame.Surface, float]] = []
        self._seen_notif_count = 0  # track how many notifications we've processed

        # Track last processed tool call count to know when to build
        self._last_tool_calls = 0
        self._last_incidents = 0
        self._last_agent_count = 0

        # Save timer
        self._last_save = time.time()

        self._init_assets()

    def _init_assets(self):
        for mood_name in ["happy", "ecstatic", "focused", "thinking",
                          "confused", "frustrated", "bored", "panicking"]:
            self.mood_icons[mood_name] = create_mood_icon(mood_name, 16)

    def _build_from_tool(self, tool_name: str, agent_name: str, agent_px: float, agent_py: float):
        """Agent flies to build site, then builds a station piece."""
        if not self.station.has_core:
            # First build: queue agent to fly to center, then place core on arrival
            self._queue_core_build(agent_name, tool_name)
            return True

        ok = self.station.build(tool_name=tool_name, agent_name=agent_name,
                                near_px=agent_px, near_py=agent_py)
        if ok:
            self._fly_agent_to_last_build(agent_name)
        return ok

    def _build_from_event(self, event_key: str, agent_name: str, agent_px: float, agent_py: float):
        """Build a station piece from a non-tool event."""
        if not self.station.has_core:
            self._queue_core_build(agent_name, event_key)
            return True

        ok = self.station.build_event(event_key, agent_name=agent_name,
                                      near_px=agent_px, near_py=agent_py)
        if ok:
            self._fly_agent_to_last_build(agent_name)
        return ok

    def _queue_core_build(self, agent_name: str, tool_name: str):
        """Send a mech to the center and build core on arrival."""
        center_px = float(self.station.GRID_W // 2 * self.station.CELL_PX)
        center_py = float(self.station.GRID_H // 2 * self.station.CELL_PX)
        self._pending_core = {"agent": agent_name, "tool": tool_name}

        for agent in self.sim.agents:
            if agent.name == agent_name:
                vis = self.agent_visuals.get(agent.id)
                if vis:
                    vis.target_px = center_px
                    vis.target_py = center_py
                    vis._override_target = True
                break

    def _check_pending_core(self):
        """Check if the mech has arrived at center to build the core."""
        if not hasattr(self, '_pending_core') or not self._pending_core:
            return
        if self.station.has_core:
            self._pending_core = None
            return

        agent_name = self._pending_core["agent"]
        for agent in self.sim.agents:
            if agent.name == agent_name:
                vis = self.agent_visuals.get(agent.id)
                if vis and not vis._override_target:
                    # Mech has arrived - build the core!
                    self.station._place_core(agent_name, self._pending_core["tool"])
                    self._pending_core = None
                break

    def _fly_agent_to_last_build(self, agent_name: str):
        """Send the agent's mech to the last placed structure."""
        if not self.station.placed_structures:
            return
        last = self.station.placed_structures[-1]
        target_px = float(last["x"] * self.station.CELL_PX + 16)
        target_py = float(last["y"] * self.station.CELL_PX + 16)

        for agent in self.sim.agents:
            if agent.name == agent_name:
                vis = self.agent_visuals.get(agent.id)
                if vis:
                    vis.target_px = target_px
                    vis.target_py = target_py
                    vis._override_target = True
                break

    def _ensure_visual(self, agent: Agent) -> AgentVisual:
        if agent.id not in self.agent_visuals:
            # Assign hull color based on session (parent_id or own id for main agents)
            session_key = agent.parent_id if agent.is_subagent and agent.parent_id is not None else agent.id
            if session_key not in self._session_colors:
                color_idx = len(self._session_colors) % len(SESSION_COLORS)
                self._session_colors[session_key] = SESSION_COLORS[color_idx]
            color = self._session_colors[session_key]
            self.agent_visuals[agent.id] = AgentVisual(agent, session_color=color)
        return self.agent_visuals[agent.id]

    def _cleanup_visuals(self):
        alive_ids = {a.id for a in self.sim.agents}
        dead = [k for k in self.agent_visuals if k not in alive_ids]
        for k in dead:
            del self.agent_visuals[k]
        if self.info_popup.visible and self.info_popup.agent_id not in alive_ids:
            self.info_popup.hide()

    def run(self):
        running = True
        last_time = time.time()

        while running:
            now = time.time()
            dt = now - last_time
            last_time = now

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        running = False
                    elif event.key == pygame.K_TAB:
                        if event.mod & pygame.KMOD_SHIFT:
                            self.sim.select_prev_agent()
                        else:
                            self.sim.select_next_agent()
                    elif event.key == pygame.K_SPACE:
                        self.sim.paused = not self.sim.paused
                        self.sim.last_update = time.time()
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.sim.speed = min(5.0, self.sim.speed + 0.5)
                    elif event.key == pygame.K_MINUS:
                        self.sim.speed = max(0.5, self.sim.speed - 0.5)
                    elif event.key == pygame.K_r:
                        # Reset world
                        self.station.reset()
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        idx = event.key - pygame.K_1
                        if idx < len(self.sim.agents):
                            self.sim.selected_agent_id = self.sim.agents[idx].id
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mx, my = event.pos
                        w, h = self.screen.get_size()
                        world_h = h - UI_H
                        if self.info_popup.visible and self.info_popup.hit_close(mx, my):
                            self.info_popup.hide()
                            self.sim.selected_agent_id = None
                        elif self.info_popup.visible and self.info_popup.hit_test(mx, my):
                            pass
                        elif my < world_h:
                            clicked_id = self._click_select(mx, my, world_h)
                            if clicked_id is not None:
                                self.info_popup.show(clicked_id, mx, my, w, h)
                            else:
                                self.info_popup.hide()
                                self.sim.selected_agent_id = None
                        else:
                            self.info_popup.hide()
                            self.sim.selected_agent_id = None
                    if event.button in (1, 3):
                        self.dragging = True
                        self.drag_start = event.pos
                        self.cam_drag_start = (self.cam_x, self.cam_y)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging and event.buttons[2]:
                        dx = event.pos[0] - self.drag_start[0]
                        dy = event.pos[1] - self.drag_start[1]
                        self.cam_x = self.cam_drag_start[0] - dx
                        self.cam_y = self.cam_drag_start[1] - dy

            # Update simulation
            self.sim.update()

            # Check if mech arrived to build core
            self._check_pending_core()

            # Check for new tool calls -> trigger builds (1 piece per call)
            if self.sim.total_tool_calls > self._last_tool_calls:
                self._last_tool_calls = self.sim.total_tool_calls
                for agent in self.sim.agents:
                    if agent.activity not in ("idle", "waiting"):
                        vis = self.agent_visuals.get(agent.id)
                        px = vis.px if vis else 200
                        py = vis.py if vis else 200
                        tool = {"coding": "Edit", "reading": "Read", "searching": "Grep",
                                "fixing": "Bash", "thinking": "Agent"}.get(agent.activity, "Edit")
                        self._build_from_tool(tool, agent.name, px, py)
                        break

            # Check for new incidents -> puddles
            if self.sim.incidents > self._last_incidents:
                self._last_incidents = self.sim.incidents
                for agent in self.sim.agents:
                    if agent.mood == Mood.FRUSTRATED or agent.mood == Mood.PANICKING:
                        vis = self.agent_visuals.get(agent.id)
                        px = vis.px if vis else 200
                        py = vis.py if vis else 200
                        self._build_from_event("PostToolUseFailure", agent.name, px, py)
                        break

            # Check for new agents -> benches/flags
            if len(self.sim.agents) > self._last_agent_count:
                diff = len(self.sim.agents) - self._last_agent_count
                for agent in self.sim.agents[-diff:]:
                    vis = self._ensure_visual(agent)
                    event_key = "SessionStart" if not agent.is_subagent else "SubagentStart"
                    self._build_from_event(event_key, agent.name, vis.px, vis.py)
            self._last_agent_count = len(self.sim.agents)

            # Update visuals
            for agent in self.sim.agents:
                vis = self._ensure_visual(agent)
                vis.update(agent, dt, self.font)

            self._cleanup_visuals()

            # Notifications - only process NEW ones by index
            all_notifs = self.sim.world.notifications
            if len(all_notifs) > self._seen_notif_count:
                for notif in all_notifs[self._seen_notif_count:]:
                    txt = f"{notif.icon} {notif.text}"
                    if len(txt) > 50:
                        txt = txt[:47] + "..."
                    surf = self.font.render(txt, True, PALETTE["white"])
                    self.notification_surfs.append((surf, now))
                self._seen_notif_count = len(all_notifs)
            # Expire after 4s, keep max 3
            self.notification_surfs = [(s, t) for s, t in self.notification_surfs if now - t < 4.0][-3:]

            # Auto-save every 30s
            if now - self._last_save > 30:
                self.station.save()
                self._last_save = now

            # Demo mode: build stuff every ~3 seconds, only when agents are working
            if self.sim.demo_mode and random.random() < 0.012 and self.sim.agents:
                working = [a for a in self.sim.agents if a.activity not in ("idle", "waiting")]
                if working:
                    agent = random.choice(working)
                    vis = self.agent_visuals.get(agent.id)
                    if vis:
                        tools = ["Edit", "Read", "Grep", "Bash", "Write"]
                        self._build_from_tool(random.choice(tools), agent.name, vis.px, vis.py)

            self._render(dt)
            self.clock.tick(FPS)

        # Save on exit and remove PID file (disables sounds)
        self.station.save()
        if os.path.exists(self._pid_file):
            os.remove(self._pid_file)
        pygame.quit()

    def _click_select(self, mx, my, world_h):
        best_dist = 999999
        best_id = None
        for agent in self.sim.agents:
            vis = self.agent_visuals.get(agent.id)
            if not vis:
                continue
            ax = vis.px - self.cam_x
            ay = vis.py - self.cam_y
            dist = (mx - ax) ** 2 + (my - ay) ** 2
            if dist < best_dist and dist < 2500:
                best_dist = dist
                best_id = agent.id
        if best_id is not None:
            self.sim.selected_agent_id = best_id
        return best_id

    def _render(self, dt):
        w, h = self.screen.get_size()
        # Fill EVERYTHING with pure black - no white, no lighter patches
        self.screen.fill((8, 8, 18))
        world_h = h - UI_H

        # Station draws its own starfield background + structures
        self.station.draw(self.screen, self.cam_x, self.cam_y, w, world_h)

        # Agents (sorted by y for depth)
        sorted_agents = sorted(self.sim.agents, key=lambda a: a.y)
        selected_id = self.sim.selected_agent_id
        for agent in sorted_agents:
            vis = self.agent_visuals.get(agent.id)
            if vis:
                vis.draw(self.screen, agent, self.mood_icons,
                         agent.id == selected_id, self.cam_x, self.cam_y)

        # Waiting overlay
        if not self.sim.agents and self.sim.waiting_for_events:
            overlay = pygame.Surface((w, world_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))

            dots = "." * (int(time.time() * 2) % 4)
            msg1 = self.font_large.render(f"Awaiting deployment orders{dots}", True, PALETTE["energy_cyan"])
            msg2 = self.font.render("Start a Claude Code session to begin the crusade!", True, (180, 190, 210))
            msg3 = self.font_small.render("--demo for demo mode  |  R to purge and rebuild", True, (100, 100, 130))
            self.screen.blit(msg1, (w // 2 - msg1.get_width() // 2, world_h // 2 - 30))
            self.screen.blit(msg2, (w // 2 - msg2.get_width() // 2, world_h // 2 + 10))
            self.screen.blit(msg3, (w // 2 - msg3.get_width() // 2, world_h // 2 + 35))

        # UI Panel
        self._render_ui(w, h, world_h)

        # Notifications
        self._render_notifications(w)

        # Info popup
        if self.info_popup.visible:
            popup_agent = next((a for a in self.sim.agents if a.id == self.info_popup.agent_id), None)
            if popup_agent:
                self.info_popup.draw(self.screen, popup_agent, self.mood_icons,
                                     self.font, self.font_large, self.font_small,
                                     self.agent_visuals)
            else:
                self.info_popup.hide()

        # Paused overlay
        if self.sim.paused:
            pause_txt = self.font_title.render("PAUSED", True, (255, 255, 100))
            px = w // 2 - pause_txt.get_width() // 2
            bg = pygame.Surface((pause_txt.get_width() + 20, pause_txt.get_height() + 10), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 180))
            self.screen.blit(bg, (px - 10, 10))
            self.screen.blit(pause_txt, (px, 15))

        pygame.display.flip()

    def _render_ui(self, w, h, world_h):
        panel = pygame.Rect(0, world_h, w, UI_H)
        pygame.draw.rect(self.screen, (12, 14, 28), panel)
        pygame.draw.line(self.screen, (40, 50, 80), (0, world_h), (w, world_h), 2)

        # Row 1: Title + stats
        x = 10
        y = world_h + 8

        title = self.font_large.render("Void Fortress", True, PALETTE["energy_cyan"])
        self.screen.blit(title, (x, y))
        x += title.get_width() + 15

        if self.sim.demo_mode:
            demo = self.font_small.render("[DEMO]", True, (80, 80, 100))
            self.screen.blit(demo, (x, y + 8))
            x += demo.get_width() + 15

        # Crew count
        crew_txt = self.font.render(f"Crew: {len(self.sim.agents)}", True, PALETTE["mood_focused"])
        self.screen.blit(crew_txt, (x, y + 4))
        x += crew_txt.get_width() + 20

        # Salvage count (total built)
        salvage_txt = self.font.render(f"Fortified: {self.station.total_placed}", True, (180, 200, 140))
        self.screen.blit(salvage_txt, (x, y + 4))
        x += salvage_txt.get_width() + 20

        # Fuel gauge - based on context usage (tool calls as proxy)
        # More tool calls = more fuel burned. Resets per session.
        fuel_label = self.font_small.render("Void Shields", True, (120, 130, 160))
        self.screen.blit(fuel_label, (x, y - 1))
        bar_x = x
        bar_y = y + 12
        bar_w = 80
        bar_h = 10
        # Fuel drains as tool calls increase (roughly 200 calls = empty)
        fuel_pct = max(0.0, 1.0 - self.sim.total_tool_calls / 200.0)
        pygame.draw.rect(self.screen, (30, 35, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        if fuel_pct > 0:
            if fuel_pct > 0.5:
                bar_color = PALETTE["energy_cyan"]
            elif fuel_pct > 0.2:
                bar_color = PALETTE["flame_yellow"]
            else:
                bar_color = PALETTE["mood_frustrated"]
            fill_w = int(fuel_pct * bar_w)
            pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, fill_w, bar_h), border_radius=3)
        pygame.draw.rect(self.screen, (50, 55, 75), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)

        # Row 2: Selected agent detail (or hint to click)
        selected = self.sim.get_selected_agent()
        y2 = world_h + 38
        if selected:
            # Name + role
            name_txt = self.font_large.render(selected.name, True, PALETTE["white"])
            self.screen.blit(name_txt, (10, y2))

            role_color = {
                "main": PALETTE["mood_ecstatic"], "explorer": PALETTE["mood_focused"],
                "coder": PALETTE["mood_happy"], "tester": PALETTE["mood_confused"],
                "researcher": PALETTE["mood_thinking"], "reviewer": PALETTE["white"],
                "fixer": PALETTE["mood_frustrated"], "planner": PALETTE["mood_focused"],
            }.get(selected.role.value, PALETTE["white"])
            role_txt = self.font.render(selected.role.value, True, role_color)
            self.screen.blit(role_txt, (10 + name_txt.get_width() + 8, y2 + 4))

            if selected.is_subagent:
                sub_txt = self.font_small.render("(subagent)", True, (100, 100, 140))
                self.screen.blit(sub_txt, (10 + name_txt.get_width() + role_txt.get_width() + 16, y2 + 6))

            # Mood + activity on one line
            mood_txt = self.font.render(
                f"{selected.mood.label}  ·  {selected.activity}",
                True, (160, 165, 185))
            self.screen.blit(mood_txt, (10, y2 + 26))

            # Thought
            if selected.thought:
                thought_str = selected.thought[:50] + "..." if len(selected.thought) > 50 else selected.thought
                thought = self.font.render(f'"{thought_str}"', True, (140, 180, 160))
                self.screen.blit(thought, (10, y2 + 46))
        elif self.sim.agents:
            hint = self.font.render("Click a mech to inspect it", True, (60, 65, 90))
            self.screen.blit(hint, (10, y2 + 10))

        # Bottom row: controls + event time
        controls = self.font_small.render(
            "[Tab] Select  [Space] Pause  [Click] Inspect  [R] Reset  [Q] Quit",
            True, (55, 60, 80))
        self.screen.blit(controls, (10, h - 16))

        if self.sim.last_event_time:
            ago = int(time.time() - self.sim.last_event_time)
            evt_txt = f"Last event: {ago}s ago" if ago < 60 else f"Last event: {ago // 60}m ago"
            evt_surf = self.font_small.render(evt_txt, True, (55, 60, 80))
            self.screen.blit(evt_surf, (w - evt_surf.get_width() - 10, h - 16))

    def _render_notifications(self, w):
        now = time.time()
        y = 10
        for surf, t in reversed(self.notification_surfs[-5:]):
            age = now - t
            alpha = 255 if age < 3.5 else int((5.0 - age) / 1.5 * 255)
            alpha = max(0, min(255, alpha))

            bg = pygame.Surface((surf.get_width() + 16, surf.get_height() + 8), pygame.SRCALPHA)
            bg.fill((20, 20, 35, min(alpha, 200)))
            pygame.draw.rect(bg, (80, 80, 120, min(alpha, 200)), bg.get_rect(), 1, border_radius=4)
            surf.set_alpha(alpha)

            x = w - bg.get_width() - 10
            self.screen.blit(bg, (x, y))
            self.screen.blit(surf, (x + 8, y + 4))
            y += bg.get_height() + 4


def main():
    args = sys.argv[1:]
    demo = "--demo" in args

    gui = GUI(demo_mode=demo)
    gui.run()


if __name__ == "__main__":
    main()
