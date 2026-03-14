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

# -- Explosion --
EXPLOSION_PARTICLE_COUNT = 45
EXPLOSION_LIFETIME = 1.8
EXPLOSION_SPEED_MIN = 40
EXPLOSION_SPEED_MAX = 200
EXPLOSION_SIZE_MIN = 2
EXPLOSION_SIZE_MAX = 6
EXPLOSION_DRAG_MIN = 0.92
EXPLOSION_DRAG_MAX = 0.97
EXPLOSION_FLASH_DURATION = 0.1
EXPLOSION_FLASH_ALPHA = 120
EXPLOSION_FLASH_COLOR = (80, 255, 80)

# -- Info popup --
POPUP_SHADOW_OFFSET = 3
POPUP_SHADOW_ALPHA = 80
POPUP_PORTRAIT_SIZE = 62
POPUP_MARGIN = 12
POPUP_TOP_PADDING = 10
POPUP_CLOSE_SIZE = 14
POPUP_CLOSE_COLOR = (140, 35, 35)
POPUP_CLOSE_X_COLOR = (200, 200, 200)
POPUP_BG_COLOR = (14, 18, 32)
POPUP_BORDER_COLOR = (45, 55, 85)
POPUP_ACCENT_COLOR = (80, 200, 255)
POPUP_THOUGHT_MAX_LEN = 45
POPUP_BADGE_HEIGHT = 16
POPUP_BADGE_PADDING = 8
POPUP_HEADER_HEIGHT = 28
POPUP_HEADER_BG = (8, 10, 22)
POPUP_NAME_COLOR = (230, 235, 245)
POPUP_RANK_TEXT_COLOR = (15, 18, 30)
POPUP_MOOD_BAR_BG = (25, 30, 48)
POPUP_MOOD_BAR_HEIGHT = 20
POPUP_MOOD_GLOW_ALPHA = 30
POPUP_MOOD_BORDER_WIDTH = 3
POPUP_MOOD_GLOW_MARGIN = 4
POPUP_STAT_LABEL_COLOR = (70, 78, 105)
POPUP_STAT_VALUE_COLOR = (190, 195, 215)
POPUP_STAT_LABEL_OFFSET_X = 10
POPUP_STAT_VALUE_OFFSET_X = 100
POPUP_STAT_ROW_HEIGHT = 20
POPUP_STAT_BULLET_RADIUS = 2
POPUP_THOUGHT_QUOTE_COLOR = (100, 150, 130)
POPUP_CORNER_LENGTH = 10

# -- Agent visual --
MECH_MOVE_SPEED = 150.0
MECH_WALK_FRAME_INTERVAL = 0.15
MECH_BOB_FREQUENCY = 1.2
MECH_BOB_AMPLITUDE = 3
MECH_ARRIVAL_THRESHOLD = 3
THOUGHT_BUBBLE_MAX_WIDTH = 180
THOUGHT_BUBBLE_DURATION = 5.0
PORTRAIT_SEED_PRIME = 7919
PORTRAIT_SEED_MOD = 10000

# -- Agent position mapping (grid to pixel) --
# Base values for 960x530 world area; scaled dynamically by _agent_grid_params()
AGENT_BASE_WORLD_W = 960
AGENT_BASE_WORLD_H = 530  # 640 - UI_H
AGENT_PX_SCALE = 8
AGENT_PX_OFFSET_X = 80
AGENT_PY_SCALE = 12
AGENT_PY_OFFSET_Y = 60
AGENT_GRID_W = 80   # world.width
AGENT_GRID_H = 24   # world.height
AGENT_FILL_RATIO = 0.85  # agents fill 85% of visible area

# -- Engine glow --
ENGINE_GLOW_HEIGHT = 6
ENGINE_GLOW_BASE_ALPHA = 80
ENGINE_GLOW_FLICKER_AMPLITUDE = 40
ENGINE_GLOW_FLICKER_SPEED = 12.0

# -- Selection --
SELECTION_BORDER_COLOR = (255, 255, 100)
CLICK_SELECT_RADIUS_SQ = 2500

# -- Name tag --
NAME_TAG_FONT_SIZE = 16
NAME_TAG_BG_ALPHA = 140
SUBAGENT_TAG_FONT_SIZE = 13

# -- Notifications --
NOTIFICATION_MAX_TEXT_LEN = 50
NOTIFICATION_LIFETIME_SEC = 4.0
NOTIFICATION_MAX_DISPLAY = 3
NOTIFICATION_FADE_START = 3.5
NOTIFICATION_FADE_DURATION = 1.5
NOTIFICATION_BG_ALPHA = 200

# -- Save --
AUTO_SAVE_INTERVAL_SEC = 30

# -- Demo --
DEMO_BUILD_CHANCE = 0.012

# -- Fuel / Void Shields --
FUEL_MAX_TOOL_CALLS = 200
FUEL_WARN_THRESHOLD = 0.5
FUEL_CRITICAL_THRESHOLD = 0.2
SHIELD_PANEL_WIDTH = 260
SHIELD_BAR_HEIGHT = 10
SHIELD_ROW_HEIGHT = 26  # label + bar combined
SHIELD_BAR_BORDER_RADIUS = 4
SHIELD_MAX_BARS = 3
SHIELD_BAR_BG = (20, 24, 38)
SHIELD_BAR_BORDER = (45, 52, 72)
SHIELD_BAR_NAME_COLOR = (160, 170, 195)
SHIELD_BAR_PCT_COLOR = (220, 225, 240)
SHIELD_BAR_NAME_MAX_LEN = 12
SHIELD_EDGE_GLOW_WIDTH = 6
SHIELD_EDGE_GLOW_ALPHA = 70
SHIELD_OFFLINE_COLOR = (60, 65, 80)

# -- UI panel --
UI_PANEL_BG = (12, 14, 28)
UI_PANEL_BG_DARK = (8, 10, 22)
UI_PANEL_BORDER = (40, 50, 80)
UI_PANEL_DIVIDER = (40, 50, 70)
UI_PANEL_GLOW_ALPHA = 25
UI_PANEL_CORNER_LENGTH = 14
UI_HINT_COLOR = (55, 60, 80)
UI_MOOD_TEXT_COLOR = (160, 165, 185)
UI_CONTROLS_COLOR = (55, 60, 80)
UI_DEMO_COLOR = (80, 80, 100)
UI_SALVAGE_COLOR = (180, 200, 140)
UI_SUBAGENT_TAG_COLOR = (100, 100, 140)

# -- Waiting overlay --
WAITING_OVERLAY_ALPHA = 100
WAITING_DOTS_SPEED = 2
WAITING_DOTS_MAX = 4
WAITING_SUBTITLE_COLOR = (180, 190, 210)
WAITING_HINT_COLOR = (100, 100, 130)
WAITING_PULSE_BASE_ALPHA = 100
WAITING_PULSE_AMPLITUDE = 50
WAITING_PULSE_SPEED = 3
WAITING_FRAME_WIDTH = 360
WAITING_FRAME_HEIGHT = 100

# -- Paused overlay --
PAUSED_TEXT_COLOR = (255, 255, 100)
PAUSED_BANNER_HEIGHT = 50
PAUSED_BG_ALPHA = 220
PAUSED_GLOW_ALPHA = 50
PAUSED_CORNER_LENGTH = 16
PAUSED_SCAN_ALPHA = 20

# -- Notification polish --
NOTIFICATION_SLIDE_DURATION = 0.3
NOTIFICATION_SLIDE_DISTANCE = 20
NOTIFICATION_BORDER_ALPHA = 60
NOTIFICATION_ACCENT_ALPHA = 180
NOTIFICATION_ACCENT_WIDTH = 3
NOTIFICATION_CORNER_LENGTH = 6

# -- Shared inline colors --
ENGINE_GLOW_COLOR = (255, 140, 30)
SUBAGENT_ROLE_TAG_COLOR = (180, 180, 255)

# -- Role colors (popup + UI) --
ROLE_COLORS = {
    "main": POPUP_ACCENT_COLOR,
    "explorer": POPUP_ACCENT_COLOR,
    "coder": (80, 220, 100),
    "tester": (200, 120, 255),
    "researcher": (120, 140, 255),
    "reviewer": (200, 200, 220),
    "fixer": (255, 100, 80),
    "planner": POPUP_ACCENT_COLOR,
}

# -- Mood colors --
MOOD_COLORS = {
    "RIGHTEOUS": (60, 200, 60),
    "GLORIOUS": (255, 220, 40),
    "ZEALOUS": (60, 170, 255),
    "VIGILANT": (90, 110, 230),
    "SUSPICIOUS": (190, 90, 230),
    "WRATHFUL": (230, 50, 40),
    "STOIC": (110, 110, 125),
    "BESIEGED": (255, 30, 30),
}
MOOD_COLOR_DEFAULT = (120, 120, 140)

# Explosion colors — Necron gauss green + fire
EXPLOSION_COLORS = [
    (80, 255, 80),    # necron green
    (50, 220, 50),    # dark green
    (160, 255, 80),   # yellow-green
    (255, 200, 50),   # fire yellow
    (255, 140, 30),   # fire orange
    (255, 60, 20),    # fire red
    (200, 255, 200),  # bright green flash
]


# ---------------------------------------------------------------------------
# Visual polish helpers
# ---------------------------------------------------------------------------

def draw_tech_corners(surface, rect, color, length=12, thickness=2):
    """L-shaped corner brackets on all 4 corners of *rect*."""
    x1, y1, x2, y2 = rect.left, rect.top, rect.right - 1, rect.bottom - 1
    # Top-left
    pygame.draw.line(surface, color, (x1, y1), (x1 + length, y1), thickness)
    pygame.draw.line(surface, color, (x1, y1), (x1, y1 + length), thickness)
    # Top-right
    pygame.draw.line(surface, color, (x2 - length, y1), (x2, y1), thickness)
    pygame.draw.line(surface, color, (x2, y1), (x2, y1 + length), thickness)
    # Bottom-left
    pygame.draw.line(surface, color, (x1, y2 - length), (x1, y2), thickness)
    pygame.draw.line(surface, color, (x1, y2), (x1 + length, y2), thickness)
    # Bottom-right
    pygame.draw.line(surface, color, (x2, y2 - length), (x2, y2), thickness)
    pygame.draw.line(surface, color, (x2 - length, y2), (x2, y2), thickness)


def draw_glow_text(surface, font, text, color, x, y, glow_color=None, glow_alpha=40):
    """Render *text* with an 8-offset glow halo behind it. Returns the text surface."""
    if glow_color is None:
        glow_color = color
    gr, gg, gb = glow_color
    glow_surf = font.render(text, True, (gr, gg, gb))
    glow_surf.set_alpha(glow_alpha)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            surface.blit(glow_surf, (x + dx * 2, y + dy * 2))
    txt_surf = font.render(text, True, color)
    surface.blit(txt_surf, (x, y))
    return txt_surf


def draw_scan_lines(surface, rect, alpha=18, spacing=3):
    """Horizontal CRT scan lines overlay on *rect*."""
    scan = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for sy in range(0, rect.height, spacing):
        pygame.draw.line(scan, (0, 0, 0, alpha), (0, sy), (rect.width, sy))
    surface.blit(scan, (rect.x, rect.y))


def draw_accent_divider(surface, x1, y1, x2, y2, color, glow=False):
    """Colored divider line with optional wider glow line behind it."""
    if glow:
        r, g, b = color
        glow_surf = pygame.Surface((abs(x2 - x1) + 4, 5), pygame.SRCALPHA)
        glow_surf.fill((r, g, b, 25))
        surface.blit(glow_surf, (min(x1, x2) - 2, min(y1, y2) - 2))
    pygame.draw.line(surface, color, (x1, y1), (x2, y2), 1)


def _render_glow_logo(font, text, color, glow_color=None, glow_alpha=40):
    """Pre-render text with glow halo onto a transparent surface."""
    if glow_color is None:
        glow_color = color
    pad = 6  # extra space for glow offsets
    txt_surf = font.render(text, True, color)
    w, h = txt_surf.get_width() + pad * 2, txt_surf.get_height() + pad * 2
    result = pygame.Surface((w, h), pygame.SRCALPHA)
    gr, gg, gb = glow_color
    glow_surf = font.render(text, True, (gr, gg, gb))
    glow_surf.set_alpha(glow_alpha)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            result.blit(glow_surf, (pad + dx * 2, pad + dy * 2))
    result.blit(txt_surf, (pad, pad))
    return result


class Explosion:
    """Necron gauss explosion particle effect."""

    def __init__(self, px: float, py: float):
        self.px = px
        self.py = py
        self.age = 0.0
        self.lifetime = EXPLOSION_LIFETIME
        self.particles: list[dict] = []

        # Spawn particles
        for _ in range(EXPLOSION_PARTICLE_COUNT):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(EXPLOSION_SPEED_MIN, EXPLOSION_SPEED_MAX)
            self.particles.append({
                "x": 0.0, "y": 0.0,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": random.randint(EXPLOSION_SIZE_MIN, EXPLOSION_SIZE_MAX),
                "color": random.choice(EXPLOSION_COLORS),
                "drag": random.uniform(EXPLOSION_DRAG_MIN, EXPLOSION_DRAG_MAX),
            })

    @property
    def done(self):
        return self.age >= self.lifetime

    def update(self, dt: float):
        self.age += dt
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vx"] *= p["drag"]
            p["vy"] *= p["drag"]

    def draw(self, screen: pygame.Surface, cam_x: float, cam_y: float):
        fade = max(0.0, 1.0 - self.age / self.lifetime)
        # Flash on first frames
        if self.age < EXPLOSION_FLASH_DURATION:
            flash_r = int(30 * (1.0 - self.age / EXPLOSION_FLASH_DURATION))
            flash = pygame.Surface((flash_r * 2, flash_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash, (*EXPLOSION_FLASH_COLOR, int(EXPLOSION_FLASH_ALPHA * fade)),
                               (flash_r, flash_r), flash_r)
            screen.blit(flash, (int(self.px - cam_x - flash_r),
                                int(self.py - cam_y - flash_r)))

        for p in self.particles:
            alpha = int(255 * fade)
            sx = int(self.px + p["x"] - cam_x)
            sy = int(self.py + p["y"] - cam_y)
            size = max(1, int(p["size"] * fade))
            r, g, b = p["color"]
            dot = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot, (r, g, b, alpha), (size, size), size)
            screen.blit(dot, (sx - size, sy - size))


class InfoPopup:
    """Pilot dossier popup when you click a mech."""

    WIDTH = 270
    HEIGHT = 230

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

        bg = POPUP_BG_COLOR
        border = POPUP_BORDER_COLOR
        accent = POPUP_ACCENT_COLOR

        popup_rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
        shadow = pygame.Surface((self.WIDTH + 4, self.HEIGHT + 4), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, POPUP_SHADOW_ALPHA))
        screen.blit(shadow, (self.x + POPUP_SHADOW_OFFSET, self.y + POPUP_SHADOW_OFFSET))

        pygame.draw.rect(screen, bg, popup_rect)
        pygame.draw.rect(screen, border, popup_rect, 2)

        # Tech corner brackets
        draw_tech_corners(screen, popup_rect, accent, length=POPUP_CORNER_LENGTH, thickness=2)

        # Header bar — dark band at top with name + rank
        header_rect = pygame.Rect(self.x + 2, self.y + 2, self.WIDTH - 4, POPUP_HEADER_HEIGHT)
        pygame.draw.rect(screen, POPUP_HEADER_BG, header_rect)

        role_color = ROLE_COLORS.get(agent.role.value, accent)
        rank = "CAPTAIN" if not agent.is_subagent else agent.role.value[:3].upper()

        name_surf = font_large.render(agent.name, True, POPUP_NAME_COLOR)
        screen.blit(name_surf, (self.x + POPUP_MARGIN, self.y + 5))
        rank_surf = font_small.render(rank, True, POPUP_RANK_TEXT_COLOR)
        badge_w = rank_surf.get_width() + POPUP_BADGE_PADDING
        badge_x = self.x + POPUP_MARGIN + name_surf.get_width() + 8
        badge_rect = pygame.Rect(badge_x, self.y + 8, badge_w, POPUP_BADGE_HEIGHT)
        pygame.draw.rect(screen, role_color, badge_rect, border_radius=3)
        screen.blit(rank_surf, (badge_rect.x + 4, badge_rect.y + 2))

        # Close button
        self.close_rect = pygame.Rect(self.x + self.WIDTH - 20, self.y + 7, POPUP_CLOSE_SIZE, POPUP_CLOSE_SIZE)
        pygame.draw.rect(screen, POPUP_CLOSE_COLOR, self.close_rect, border_radius=2)
        x_surf = font_small.render("x", True, POPUP_CLOSE_X_COLOR)
        screen.blit(x_surf, (self.close_rect.x + 3, self.close_rect.y + 1))

        left = self.x + POPUP_MARGIN
        cy = self.y + POPUP_HEADER_HEIGHT + 6

        # Portrait (left side) with mood-glow frame
        portrait_size = POPUP_PORTRAIT_SIZE
        portrait_seed = agent.id * PORTRAIT_SEED_PRIME
        if agent_visuals and agent.id in agent_visuals:
            portrait_seed = agent_visuals[agent.id].portrait_seed
        portrait = create_pilot_portrait(portrait_seed, agent.mood.label, portrait_size)

        mood_color = MOOD_COLORS.get(agent.mood.label, MOOD_COLOR_DEFAULT)

        px = left
        py = cy
        # Mood glow behind portrait
        gm = POPUP_MOOD_GLOW_MARGIN
        glow_rect = pygame.Rect(px - gm, py - gm, portrait_size + gm * 2, portrait_size + gm * 2)
        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        mr, mg, mb = mood_color
        glow_surf.fill((mr, mg, mb, POPUP_MOOD_GLOW_ALPHA))
        screen.blit(glow_surf, (glow_rect.x, glow_rect.y))
        # Mood-colored border
        border_rect = pygame.Rect(px - 2, py - 2, portrait_size + 4, portrait_size + 4)
        pygame.draw.rect(screen, mood_color, border_rect, POPUP_MOOD_BORDER_WIDTH)
        screen.blit(portrait, (px, py))

        cy = py + portrait_size + 8

        # Mood bar - colored strip
        bar_rect = pygame.Rect(left, cy, self.WIDTH - 24, POPUP_MOOD_BAR_HEIGHT)
        pygame.draw.rect(screen, POPUP_MOOD_BAR_BG, bar_rect, border_radius=3)
        pygame.draw.rect(screen, mood_color, bar_rect, border_radius=3)
        mood_txt = font.render(f"  {agent.mood.label.upper()}  ·  {agent.activity}", True, POPUP_RANK_TEXT_COLOR)
        screen.blit(mood_txt, (left + 6, cy + 2))
        cy += 28

        # Accent divider (mood-colored)
        draw_accent_divider(screen, left, cy, self.x + self.WIDTH - 12, cy, mood_color, glow=True)
        cy += 8

        # Stats grid with bullet dots
        stats = [
            ("Personality", agent.personality),
            ("Energy", f"{agent.energy:.0%}"),
            ("Operations", str(agent.tasks_completed)),
        ]
        if agent.is_subagent:
            stats.insert(0, ("Type", "Subagent"))

        for label, value in stats:
            pygame.draw.circle(screen, accent, (left + 3, cy + 6), POPUP_STAT_BULLET_RADIUS)
            label_surf = font_small.render(label, True, POPUP_STAT_LABEL_COLOR)
            value_surf = font.render(value, True, POPUP_STAT_VALUE_COLOR)
            screen.blit(label_surf, (left + POPUP_STAT_LABEL_OFFSET_X, cy))
            screen.blit(value_surf, (left + POPUP_STAT_VALUE_OFFSET_X, cy - 1))
            cy += POPUP_STAT_ROW_HEIGHT

        # Thought at bottom
        cy += 2
        draw_accent_divider(screen, left, cy, self.x + self.WIDTH - 12, cy, mood_color, glow=True)
        cy += 6
        if agent.thought:
            thought = agent.thought[:POPUP_THOUGHT_MAX_LEN] + "..." if len(agent.thought) > POPUP_THOUGHT_MAX_LEN else agent.thought
            chevron_surf = font_small.render(">", True, accent)
            screen.blit(chevron_surf, (left, cy))
            thought_surf = font_small.render(f'"{thought}"', True, POPUP_THOUGHT_QUOTE_COLOR)
            screen.blit(thought_surf, (left + 12, cy))


# Session colors - each session gets one hull color
SESSION_COLORS = [
    "hull_acc_blue", "hull_acc_red", "hull_acc_green", "hull_acc_purple",
    "hull_acc_orange", "hull_acc_cyan", "hull_acc_yellow", "hull_acc_dark",
]


# Current screen-dependent grid→pixel mapping (updated each frame by GUI)
_grid_scale_x = AGENT_PX_SCALE
_grid_scale_y = AGENT_PY_SCALE
_grid_offset_x = AGENT_PX_OFFSET_X
_grid_offset_y = AGENT_PY_OFFSET_Y


def _update_grid_params(screen_w: int, world_h: int):
    """Recompute grid→pixel scale so agents fill the visible world area."""
    global _grid_scale_x, _grid_scale_y, _grid_offset_x, _grid_offset_y
    usable_w = screen_w * AGENT_FILL_RATIO
    usable_h = world_h * AGENT_FILL_RATIO
    _grid_scale_x = usable_w / AGENT_GRID_W
    _grid_scale_y = usable_h / AGENT_GRID_H
    _grid_offset_x = (screen_w - usable_w) / 2
    _grid_offset_y = (world_h - usable_h) / 2


def grid_to_px(gx: float, gy: float) -> tuple[float, float]:
    """Convert grid coordinates to pixel coordinates."""
    return (gx * _grid_scale_x + _grid_offset_x,
            gy * _grid_scale_y + _grid_offset_y)


class AgentVisual:
    """Visual state for an agent."""

    def __init__(self, agent: Agent, session_color: str = ""):
        self.agent_id = agent.id
        hull_color = session_color or random.choice(HULL_COLORS)
        self.session_color = hull_color
        self.sprites = create_agent_sprites("", hull_color, scale=3)
        self.portrait_seed = agent.id * PORTRAIT_SEED_PRIME + hash(agent.name) % PORTRAIT_SEED_MOD
        px, py = grid_to_px(agent.x, agent.y)
        self.px = px
        self.py = py
        self.target_px = self.px
        self.target_py = self.py
        self.walk_frame = 0
        self.walk_timer = 0.0
        self.bubble_surface = None
        self.bubble_text = ""
        self.bubble_timer = 0.0
        self.bounce = 0.0
        self.float_phase = random.uniform(0, math.tau)  # unique float offset
        self.sitting = False
        self.bench_pos = None
        self.moving = False
        self._override_target = False  # when True, don't follow sim coords

    def update(self, agent: Agent, dt: float, font: pygame.font.Font):
        if not self.sitting and not self._override_target:
            tx, ty = grid_to_px(agent.x, agent.y)
            self.target_px = tx
            self.target_py = ty

        # Clear override once we've arrived
        if self._override_target:
            dx = self.target_px - self.px
            dy = self.target_py - self.py
            if math.sqrt(dx * dx + dy * dy) < MECH_ARRIVAL_THRESHOLD:
                self._override_target = False

        speed = MECH_MOVE_SPEED  # mechs move fast
        dx = self.target_px - self.px
        dy = self.target_py - self.py
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 1:
            move = min(speed * dt, dist)
            self.px += dx / dist * move
            self.py += dy / dist * move
            self.walk_timer += dt
            if self.walk_timer > MECH_WALK_FRAME_INTERVAL:
                self.walk_frame = (self.walk_frame + 1) % 2
                self.walk_timer = 0
            self.moving = True
        else:
            self.px = self.target_px
            self.py = self.target_py
            self.moving = False

        # Mechs always bob gently in zero-g
        self.bounce = math.sin(time.time() * MECH_BOB_FREQUENCY + self.float_phase) * MECH_BOB_AMPLITUDE

        if agent.thought != self.bubble_text:
            self.bubble_text = agent.thought
            if agent.thought:
                self.bubble_surface = create_thought_bubble(agent.thought, font, max_width=THOUGHT_BUBBLE_MAX_WIDTH)
            else:
                self.bubble_surface = None
            self.bubble_timer = THOUGHT_BUBBLE_DURATION
        self.bubble_timer -= dt

    def get_sprite(self, agent: Agent):
        if self.sitting:
            return self.sprites["sit"]
        if agent.mood == Mood.ECSTATIC or agent.mood == Mood.PANICKING:
            return self.sprites["celebrate"]  # boost/afterburner
        if self.moving:
            return self.sprites["walk1"] if self.walk_frame == 0 else self.sprites["walk2"]
        return self.sprites["stand"]

    def draw(self, screen, agent, mood_icons, selected, cam_x, cam_y,
             name_font=None, tag_font=None):
        sx = int(self.px - cam_x)
        sy = int(self.py - cam_y + self.bounce)
        sprite = self.get_sprite(agent)
        # Use idle sprite height for consistent name placement
        idle_h = self.sprites["stand"].get_height()
        mech_w = sprite.get_width()

        # Engine glow beneath mech when moving
        if self.moving:
            glow_w = mech_w // 2
            glow_h = ENGINE_GLOW_HEIGHT
            glow = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
            glow_alpha = int(ENGINE_GLOW_BASE_ALPHA + ENGINE_GLOW_FLICKER_AMPLITUDE * math.sin(time.time() * ENGINE_GLOW_FLICKER_SPEED))
            glow.fill((*ENGINE_GLOW_COLOR, glow_alpha))
            screen.blit(glow, (sx + mech_w // 2 - glow_w // 2,
                               sy + idle_h))

        screen.blit(sprite, (sx, sy))

        if selected:
            rect = pygame.Rect(sx - 2, sy - 2, mech_w + 4, idle_h + 4)
            pygame.draw.rect(screen, SELECTION_BORDER_COLOR, rect, 2, border_radius=3)

        # Name tag to the RIGHT of the mech
        name_surf = name_font.render(agent.name, True, PALETTE["white"])
        name_bg = pygame.Surface((name_surf.get_width() + 6, name_surf.get_height() + 2), pygame.SRCALPHA)
        name_bg.fill((0, 0, 0, NAME_TAG_BG_ALPHA))
        nx = sx + mech_w + 4
        ny = sy + idle_h // 2 - name_bg.get_height() // 2
        screen.blit(name_bg, (nx, ny))
        screen.blit(name_surf, (nx + 3, ny + 1))

        if agent.is_subagent:
            tag = tag_font.render(agent.role.value, True, SUBAGENT_ROLE_TAG_COLOR)
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
        # Use a mech sprite as the window icon
        icon_sprites = create_agent_sprites("", "hull_acc_blue", scale=2)
        icon = icon_sprites["stand"]
        pygame.display.set_icon(icon)
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 18)
        self.font_large = pygame.font.SysFont(None, 28)
        self.font_title = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 14)
        self.font_name_tag = pygame.font.SysFont(None, NAME_TAG_FONT_SIZE)
        self.font_subagent_tag = pygame.font.SysFont(None, SUBAGENT_TAG_FONT_SIZE)

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
        self.explosions: list[Explosion] = []

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
        for mood_name in ["RIGHTEOUS", "GLORIOUS", "ZEALOUS", "VIGILANT",
                          "SUSPICIOUS", "WRATHFUL", "STOIC", "BESIEGED"]:
            self.mood_icons[mood_name] = create_mood_icon(mood_name, 16)

        # Pre-rendered title logo with cyan glow
        self._title_logo = _render_glow_logo(
            self.font_title, "VOID FORTRESS", PALETTE["energy_cyan"],
            glow_alpha=45)

        # Waiting screen logo — larger, more dramatic
        self._font_waiting = pygame.font.SysFont(None, 48)
        self._waiting_title = _render_glow_logo(
            self._font_waiting, "VOID FORTRESS", PALETTE["energy_cyan"],
            glow_alpha=60)

        # Scan line overlay for UI panel (regenerated on resize)
        self._ui_scanlines = None
        self._scanline_cache_w = 0

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
            vis = self.agent_visuals[k]
            # Spawn explosion at the dead agent's position
            self.explosions.append(Explosion(vis.px, vis.py))
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

            # Update grid scaling for current window size before moving agents
            sw, sh = self.screen.get_size()
            _update_grid_params(sw, sh - UI_H)

            # Update visuals
            for agent in self.sim.agents:
                vis = self._ensure_visual(agent)
                vis.update(agent, dt, self.font)

            self._cleanup_visuals()

            # Update explosions
            for exp in self.explosions:
                exp.update(dt)
            self.explosions = [e for e in self.explosions if not e.done]

            # Notifications - only process NEW ones by index
            all_notifs = self.sim.world.notifications
            # If the world expired old notifications, the list shrank — re-sync
            if len(all_notifs) < self._seen_notif_count:
                self._seen_notif_count = len(all_notifs)
            if len(all_notifs) > self._seen_notif_count:
                for notif in all_notifs[self._seen_notif_count:]:
                    txt = notif.text
                    if len(txt) > NOTIFICATION_MAX_TEXT_LEN:
                        txt = txt[:NOTIFICATION_MAX_TEXT_LEN - 3] + "..."
                    surf = self.font.render(txt, True, PALETTE["white"])
                    self.notification_surfs.append((surf, now))
                self._seen_notif_count = len(all_notifs)
            # Expire after lifetime, keep max display count
            self.notification_surfs = [(s, t) for s, t in self.notification_surfs if now - t < NOTIFICATION_LIFETIME_SEC][-NOTIFICATION_MAX_DISPLAY:]

            # Auto-save
            if now - self._last_save > AUTO_SAVE_INTERVAL_SEC:
                self.station.save()
                self._last_save = now

            # Demo mode: build stuff every ~3 seconds, only when agents are working
            if self.sim.demo_mode and random.random() < DEMO_BUILD_CHANCE and self.sim.agents:
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
        best_dist = float('inf')
        best_id = None
        for agent in self.sim.agents:
            vis = self.agent_visuals.get(agent.id)
            if not vis:
                continue
            ax = vis.px - self.cam_x
            ay = vis.py - self.cam_y
            dist = (mx - ax) ** 2 + (my - ay) ** 2
            if dist < best_dist and dist < CLICK_SELECT_RADIUS_SQ:
                best_dist = dist
                best_id = agent.id
        if best_id is not None:
            self.sim.selected_agent_id = best_id
        return best_id

    def _render(self, dt):
        w, h = self.screen.get_size()
        world_h = h - UI_H

        # Station draws starfield background (1920x1200, covers full screen)
        self.station.draw(self.screen, self.cam_x, self.cam_y, w, world_h)

        # Agents (sorted by y for depth)
        sorted_agents = sorted(self.sim.agents, key=lambda a: a.y)
        selected_id = self.sim.selected_agent_id
        for agent in sorted_agents:
            vis = self.agent_visuals.get(agent.id)
            if vis:
                vis.draw(self.screen, agent, self.mood_icons,
                         agent.id == selected_id, self.cam_x, self.cam_y,
                         name_font=self.font_name_tag, tag_font=self.font_subagent_tag)

        # Explosions (drawn on top of agents)
        for exp in self.explosions:
            exp.draw(self.screen, self.cam_x, self.cam_y)

        # Waiting overlay
        if not self.sim.agents and self.sim.waiting_for_events:
            overlay = pygame.Surface((w, world_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, WAITING_OVERLAY_ALPHA))
            self.screen.blit(overlay, (0, 0))

            cyan = PALETTE["energy_cyan"]

            # Big pre-rendered logo
            logo = self._waiting_title
            lx = w // 2 - logo.get_width() // 2
            ly = world_h // 2 - 50
            self.screen.blit(logo, (lx, ly))

            # Pulsing border frame
            t = time.time()
            pulse_alpha = int(WAITING_PULSE_BASE_ALPHA + WAITING_PULSE_AMPLITUDE * math.sin(t * WAITING_PULSE_SPEED))
            frame_rect = pygame.Rect(w // 2 - WAITING_FRAME_WIDTH // 2, ly - 10, WAITING_FRAME_WIDTH, WAITING_FRAME_HEIGHT)
            frame_surf = pygame.Surface((frame_rect.width, frame_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(frame_surf, (*cyan, pulse_alpha), frame_surf.get_rect(), 2, border_radius=4)
            self.screen.blit(frame_surf, (frame_rect.x, frame_rect.y))

            # Subtitle
            dots = "." * (int(t * WAITING_DOTS_SPEED) % WAITING_DOTS_MAX)
            msg1 = self.font_large.render(f"Awaiting deployment orders{dots}", True, cyan)
            msg2 = self.font.render("Start a Claude Code session to begin the crusade!", True, WAITING_SUBTITLE_COLOR)
            msg3 = self.font_small.render("--demo for demo mode  |  R to purge and rebuild", True, WAITING_HINT_COLOR)
            self.screen.blit(msg1, (w // 2 - msg1.get_width() // 2, world_h // 2 + 10))
            self.screen.blit(msg2, (w // 2 - msg2.get_width() // 2, world_h // 2 + 40))
            self.screen.blit(msg3, (w // 2 - msg3.get_width() // 2, world_h // 2 + 60))

            # Scan lines over waiting overlay
            draw_scan_lines(self.screen, pygame.Rect(0, 0, w, world_h), alpha=12, spacing=3)

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

        # Paused overlay — full-width banner
        if self.sim.paused:
            banner_y = (world_h - PAUSED_BANNER_HEIGHT) // 2
            banner_bg = pygame.Surface((w, PAUSED_BANNER_HEIGHT), pygame.SRCALPHA)
            banner_bg.fill((0, 0, 0, PAUSED_BG_ALPHA))
            self.screen.blit(banner_bg, (0, banner_y))

            cyan = PALETTE["energy_cyan"]
            pygame.draw.line(self.screen, cyan, (0, banner_y), (w, banner_y), 1)
            pygame.draw.line(self.screen, cyan, (0, banner_y + PAUSED_BANNER_HEIGHT), (w, banner_y + PAUSED_BANNER_HEIGHT), 1)

            draw_glow_text(self.screen, self.font_title, "PAUSED", PAUSED_TEXT_COLOR,
                           w // 2 - self.font_title.size("PAUSED")[0] // 2,
                           banner_y + (PAUSED_BANNER_HEIGHT - self.font_title.get_height()) // 2,
                           glow_color=cyan, glow_alpha=PAUSED_GLOW_ALPHA)

            banner_rect = pygame.Rect(0, banner_y, w, PAUSED_BANNER_HEIGHT)
            draw_tech_corners(self.screen, banner_rect, cyan, length=PAUSED_CORNER_LENGTH, thickness=2)
            draw_scan_lines(self.screen, banner_rect, alpha=PAUSED_SCAN_ALPHA, spacing=3)

        pygame.display.flip()

    def _render_ui(self, w, h, world_h):
        panel = pygame.Rect(0, world_h, w, UI_H)

        # Two-tone background: darker bottom half for depth
        top_half = pygame.Rect(0, world_h, w, UI_H // 2)
        bot_half = pygame.Rect(0, world_h + UI_H // 2, w, UI_H - UI_H // 2)
        pygame.draw.rect(self.screen, UI_PANEL_BG, top_half)
        pygame.draw.rect(self.screen, UI_PANEL_BG_DARK, bot_half)

        # Glow border — faint cyan line above solid border
        cyan = PALETTE["energy_cyan"]
        glow_line = pygame.Surface((w, 3), pygame.SRCALPHA)
        glow_line.fill((*cyan, UI_PANEL_GLOW_ALPHA))
        self.screen.blit(glow_line, (0, world_h - 2))
        pygame.draw.line(self.screen, UI_PANEL_BORDER, (0, world_h), (w, world_h), 2)

        # Tech corner brackets on panel
        draw_tech_corners(self.screen, panel, cyan, length=UI_PANEL_CORNER_LENGTH, thickness=2)

        # Row 1: Pre-rendered title logo + stats
        x = 10
        y = world_h + 4

        # Blit pre-rendered glow logo (offset by padding baked in)
        self.screen.blit(self._title_logo, (x - 6, y - 6))
        x += self._title_logo.get_width() - 6

        if self.sim.demo_mode:
            demo = self.font_small.render("[DEMO]", True, UI_DEMO_COLOR)
            self.screen.blit(demo, (x, y + 12))
            x += demo.get_width() + 10

        # Vertical divider between title and stats
        pygame.draw.line(self.screen, UI_PANEL_DIVIDER, (x, world_h + 6), (x, world_h + 28), 1)
        x += 10

        # Crew count
        crew_txt = self.font.render(f"Crew: {len(self.sim.agents)}", True, PALETTE["mood_ZEALOUS"])
        self.screen.blit(crew_txt, (x, y + 8))
        x += crew_txt.get_width() + 20

        # Salvage count (total built)
        salvage_txt = self.font.render(f"Fortified: {self.station.total_placed}", True, UI_SALVAGE_COLOR)
        self.screen.blit(salvage_txt, (x, y + 8))
        x += salvage_txt.get_width() + 20

        # ── Void Shields: right-anchored panel ──
        shield_x = w - SHIELD_PANEL_WIDTH - 10
        shield_y = world_h + 6

        # Vertical divider separating shields from stats
        pygame.draw.line(self.screen, UI_PANEL_DIVIDER,
                         (shield_x - 10, world_h + 4), (shield_x - 10, world_h + UI_H - 18), 1)

        bars = self.sim.get_session_context_bars()  # [(name, used_pct, agent_id), ...]
        bar_x = shield_x
        bar_w = SHIELD_PANEL_WIDTH
        by = shield_y

        if bars:
            for i in range(min(len(bars), SHIELD_MAX_BARS)):
                name, used_pct, agent_id = bars[i]
                fuel_pct = max(0.0, min(1.0, 1.0 - used_pct / 100.0))
                remaining = int(100 - used_pct)

                # Use session hull color for the bar, tinted by health
                vis = self.agent_visuals.get(agent_id)
                session_color = PALETTE.get(vis.session_color, PALETTE["energy_cyan"]) if vis else PALETTE["energy_cyan"]

                # Desaturate toward yellow/red when low
                if fuel_pct > FUEL_WARN_THRESHOLD:
                    bar_color = session_color
                elif fuel_pct > FUEL_CRITICAL_THRESHOLD:
                    bar_color = PALETTE["flame_yellow"]
                else:
                    bar_color = PALETTE["mood_WRATHFUL"]

                # Label row: colored dot + name left, percentage right
                pygame.draw.circle(self.screen, session_color, (bar_x + 4, by + 7), 3)
                name_surf = self.font.render(name[:SHIELD_BAR_NAME_MAX_LEN], True, SHIELD_BAR_NAME_COLOR)
                pct_surf = self.font.render(f"{remaining}%", True, bar_color)
                self.screen.blit(name_surf, (bar_x + 12, by))
                self.screen.blit(pct_surf, (bar_x + bar_w - pct_surf.get_width(), by))

                # Bar track (tight: 2px gap between label and bar)
                bar_y = by + name_surf.get_height() + 1
                pygame.draw.rect(self.screen, SHIELD_BAR_BG,
                                 (bar_x, bar_y, bar_w, SHIELD_BAR_HEIGHT), border_radius=SHIELD_BAR_BORDER_RADIUS)

                # Filled portion in session color
                fill_w = max(1, int(fuel_pct * bar_w))
                pygame.draw.rect(self.screen, bar_color,
                                 (bar_x, bar_y, fill_w, SHIELD_BAR_HEIGHT), border_radius=SHIELD_BAR_BORDER_RADIUS)

                # Glow on the fill edge
                if fill_w > SHIELD_EDGE_GLOW_WIDTH:
                    r, g, b = bar_color
                    edge_glow = pygame.Surface((SHIELD_EDGE_GLOW_WIDTH, SHIELD_BAR_HEIGHT), pygame.SRCALPHA)
                    edge_glow.fill((r, g, b, SHIELD_EDGE_GLOW_ALPHA))
                    self.screen.blit(edge_glow, (bar_x + fill_w - SHIELD_EDGE_GLOW_WIDTH, bar_y))

                # Border
                pygame.draw.rect(self.screen, SHIELD_BAR_BORDER,
                                 (bar_x, bar_y, bar_w, SHIELD_BAR_HEIGHT), 1, border_radius=SHIELD_BAR_BORDER_RADIUS)

                by = bar_y + SHIELD_BAR_HEIGHT + 4
        else:
            # No sessions — show "VOID SHIELDS" header + offline bar
            header_surf = self.font.render("VOID SHIELDS", True, cyan)
            self.screen.blit(header_surf, (bar_x, by))
            by += 16
            pygame.draw.rect(self.screen, SHIELD_BAR_BG,
                             (bar_x, by, bar_w, SHIELD_BAR_HEIGHT), border_radius=SHIELD_BAR_BORDER_RADIUS)
            pygame.draw.rect(self.screen, SHIELD_BAR_BORDER,
                             (bar_x, by, bar_w, SHIELD_BAR_HEIGHT), 1, border_radius=SHIELD_BAR_BORDER_RADIUS)
            offline_surf = self.font_small.render("OFFLINE", True, SHIELD_OFFLINE_COLOR)
            self.screen.blit(offline_surf, (bar_x + bar_w // 2 - offline_surf.get_width() // 2, by))

        # Horizontal accent divider between row 1 and row 2 (stop before shield panel)
        div_y = world_h + 34
        draw_accent_divider(self.screen, 8, div_y, shield_x - 18, div_y, cyan, glow=True)

        # Row 2: Selected agent detail (or hint to click)
        selected = self.sim.get_selected_agent()
        y2 = world_h + 40
        if selected:
            name_txt = self.font_large.render(selected.name, True, PALETTE["white"])
            self.screen.blit(name_txt, (10, y2))

            role_color = {
                "main": PALETTE["mood_GLORIOUS"], "explorer": PALETTE["mood_ZEALOUS"],
                "coder": PALETTE["mood_RIGHTEOUS"], "tester": PALETTE["mood_SUSPICIOUS"],
                "researcher": PALETTE["mood_VIGILANT"], "reviewer": PALETTE["white"],
                "fixer": PALETTE["mood_WRATHFUL"], "planner": PALETTE["mood_ZEALOUS"],
            }.get(selected.role.value, PALETTE["white"])
            role_txt = self.font.render(selected.role.value, True, role_color)
            self.screen.blit(role_txt, (10 + name_txt.get_width() + 8, y2 + 4))

            if selected.is_subagent:
                sub_txt = self.font_small.render("(subagent)", True, UI_SUBAGENT_TAG_COLOR)
                self.screen.blit(sub_txt, (10 + name_txt.get_width() + role_txt.get_width() + 16, y2 + 6))

            mood_txt = self.font.render(
                f"{selected.mood.label}  ·  {selected.activity}",
                True, UI_MOOD_TEXT_COLOR)
            self.screen.blit(mood_txt, (10, y2 + 24))

            if selected.thought:
                thought_str = selected.thought[:NOTIFICATION_MAX_TEXT_LEN] + "..." if len(selected.thought) > NOTIFICATION_MAX_TEXT_LEN else selected.thought
                thought = self.font.render(f'"{thought_str}"', True, (140, 180, 160))
                self.screen.blit(thought, (10, y2 + 44))
        elif self.sim.agents:
            hint = self.font.render("Click a mech to inspect it", True, UI_HINT_COLOR)
            self.screen.blit(hint, (10, y2 + 10))

        # Bottom row: controls + event time
        controls = self.font_small.render(
            "[Tab] Select  [Space] Pause  [Click] Inspect  [R] Reset  [Q] Quit",
            True, UI_CONTROLS_COLOR)
        self.screen.blit(controls, (10, h - 16))

        if self.sim.last_event_time:
            ago = int(time.time() - self.sim.last_event_time)
            evt_txt = f"Last event: {ago}s ago" if ago < 60 else f"Last event: {ago // 60}m ago"
            evt_surf = self.font_small.render(evt_txt, True, UI_CONTROLS_COLOR)
            self.screen.blit(evt_surf, (w - evt_surf.get_width() - 10, h - 16))

        # Scan lines overlay on panel (regenerate on resize)
        if w != self._scanline_cache_w:
            self._ui_scanlines = pygame.Surface((w, UI_H), pygame.SRCALPHA)
            for sy in range(0, UI_H, 3):
                pygame.draw.line(self._ui_scanlines, (0, 0, 0, 18), (0, sy), (w, sy))
            self._scanline_cache_w = w
        self.screen.blit(self._ui_scanlines, (0, world_h))

    def _render_notifications(self, w):
        now = time.time()
        cyan = PALETTE["energy_cyan"]
        y = 10
        for surf, t in reversed(self.notification_surfs[-5:]):
            age = now - t
            alpha = 255 if age < NOTIFICATION_FADE_START else int((NOTIFICATION_FADE_START + NOTIFICATION_FADE_DURATION - age) / NOTIFICATION_FADE_DURATION * 255)
            alpha = max(0, min(255, alpha))

            slide_offset = int((1.0 - min(age / NOTIFICATION_SLIDE_DURATION, 1.0)) * NOTIFICATION_SLIDE_DISTANCE)

            bg_w = surf.get_width() + 20
            bg_h = surf.get_height() + 8
            bg = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
            bg.fill((20, 20, 35, min(alpha, NOTIFICATION_BG_ALPHA)))
            cr, cg, cb = cyan
            pygame.draw.rect(bg, (cr, cg, cb, min(alpha, NOTIFICATION_BORDER_ALPHA)), bg.get_rect(), 1, border_radius=5)
            pygame.draw.rect(bg, (cr, cg, cb, min(alpha, NOTIFICATION_ACCENT_ALPHA)),
                             pygame.Rect(0, 2, NOTIFICATION_ACCENT_WIDTH, bg_h - 4))
            surf.set_alpha(alpha)

            x = max(0, w - bg_w - 10 + slide_offset)
            self.screen.blit(bg, (x, y))
            self.screen.blit(surf, (x + 12, y + 4))

            notif_rect = pygame.Rect(x, y, bg_w, bg_h)
            draw_tech_corners(self.screen, notif_rect, (cr, cg, cb), length=NOTIFICATION_CORNER_LENGTH, thickness=1)

            y += bg_h + 4


def main():
    args = sys.argv[1:]
    demo = "--demo" in args

    gui = GUI(demo_mode=demo)
    gui.run()


if __name__ == "__main__":
    main()
