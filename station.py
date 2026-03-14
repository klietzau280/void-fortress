"""Void Fortress - space station builder, grows a station structure cell by cell.

The station is a grid where each cell is a pixel-level piece of the fortress.
Hull, windows, corridors, rooms - they tile together to form one solid structure.
Think Death Star cross-section, not scattered junk.
"""

from __future__ import annotations

import json
import math
import os
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple, List

import pygame
from sprites import PALETTE, draw_space_background


# Cell types - what each grid cell IS
class Cell(Enum):
    EMPTY = 0
    HULL = 1          # solid hull plating
    HULL_ACCENT = 2   # hull with accent stripe
    WINDOW = 3        # porthole window
    CORRIDOR = 4      # interior walkway
    FLOOR = 5         # room interior
    DOOR = 6          # door between sections
    ENGINE = 7        # engine/thruster
    SOLAR = 8         # solar panel
    ANTENNA_BASE = 9  # antenna mount
    ANTENNA_TIP = 10  # blinking antenna tip
    LIGHT = 11        # small light
    DISH = 12         # satellite dish


# Colors for each cell type - main color, plus highlight/shadow for edges
CELL_COLORS = {
    Cell.HULL:         (110, 115, 130),
    Cell.HULL_ACCENT:  (75, 85, 115),
    Cell.WINDOW:       (100, 175, 220),
    Cell.CORRIDOR:     (52, 56, 72),
    Cell.FLOOR:        (42, 45, 58),
    Cell.DOOR:         (35, 40, 55),
    Cell.ENGINE:       (65, 70, 85),
    Cell.SOLAR:        (35, 50, 105),
    Cell.ANTENNA_BASE: (85, 90, 105),
    Cell.ANTENNA_TIP:  (255, 50, 50),
    Cell.LIGHT:        (200, 220, 255),
    Cell.DISH:         (145, 150, 165),
}

# Edge highlight/shadow for hull cells to give 3D panel look
CELL_HIGHLIGHT = {
    Cell.HULL:         (135, 140, 158),
    Cell.HULL_ACCENT:  (95, 108, 140),
    Cell.DISH:         (170, 175, 190),
    Cell.ENGINE:       (85, 90, 108),
    Cell.SOLAR:        (48, 65, 130),
}
CELL_SHADOW = {
    Cell.HULL:         (82, 88, 102),
    Cell.HULL_ACCENT:  (55, 62, 88),
    Cell.DISH:         (115, 120, 135),
    Cell.ENGINE:       (45, 50, 62),
    Cell.SOLAR:        (22, 35, 78),
}

# Glow colors for animated cells
GLOW_CELLS = {
    Cell.WINDOW: (100, 180, 255, 40),
    Cell.LIGHT: (180, 210, 255, 60),
    Cell.ENGINE: (255, 140, 40, 50),
    Cell.ANTENNA_TIP: (255, 40, 40, 80),
}

SAVE_DIR = os.path.expanduser("~/.agent-valley")
SAVE_FILE = os.path.join(SAVE_DIR, "station.json")

# Room templates - these stamp onto the grid as coherent structures
# Each is a list of strings where chars map to cell types

# Character mapping for templates.
# O = door, D = dish (to avoid ambiguity).
CHAR_TO_CELL = {
    "H": Cell.HULL, "A": Cell.HULL_ACCENT, "W": Cell.WINDOW,
    "C": Cell.CORRIDOR, "F": Cell.FLOOR, "O": Cell.DOOR,
    "E": Cell.ENGINE, "S": Cell.SOLAR, "T": Cell.ANTENNA_TIP,
    "L": Cell.LIGHT, "D": Cell.DISH, ".": None,
}

ROOM_CORE = [
    "..HHHHHH..",
    ".HHWHHWHH.",
    "HHCCCCCCHHH",
    "HCCCCCCCCH",
    "HWCCCCCCWH",
    "HCCCCCCCCH",
    "HHCCCCCCHHH",
    ".HHWHHWHH.",
    "..HHHHHH..",
]

ROOM_LAB = [
    "HHHWHHWHH",
    "HFFFFFFFH",
    "WFFFFFFFH",
    "HFFFFFFFH",
    "HHHWHHWHH",
]

ROOM_QUARTERS = [
    "HHHWHH",
    "HFFFFH",
    "HFFFFH",
    "HHHWHH",
]

ROOM_HANGAR = [
    "HHHHHHHHHH",
    "HOOOOOOOOH",
    "HFFFFFFFFH",
    "HFFFFFFFFH",
    "HFFFFFFFFH",
    "HOOOOOOOOH",
    "HHHHHHHHHH",
]

ROOM_COMMAND = [
    "..HHHHHH..",
    ".HWWWWWWH.",
    "HWWFFFFWWH",
    "HWWFFFFWWH",
    ".HWWWWWWH.",
    "..HHHHHH..",
]

CORRIDOR_H = [
    "HHH",
    "CCC",
    "HHH",
]

CORRIDOR_V = [
    "HCH",
    "HCH",
    "HCH",
]

SOLAR_WING_H = [
    "SSSSSSSS",
    "SSHSHSHSHS",
    "SSSSSSSS",
]

SOLAR_WING_V = [
    "SSS",
    "SHS",
    "SSS",
    "SHS",
    "SSS",
    "SHS",
    "SSS",
]

ENGINE_POD = [
    ".HH.",
    "HEEH",
    "HEEH",
    ".HH.",
    ".EE.",
]

ANTENNA_TOWER = [
    ".T.",
    ".A.",
    ".A.",
    ".A.",
    "HAH",
]

DISH_ARRAY = [
    ".DDD.",
    "DDDDD",
    ".DDD.",
    "..A..",
    "..H..",
]


# Fortress structures - renamed for the grimdark theme
STRUCTURES = {
    "command_bastion": {
        "template": ROOM_CORE,
        "connect_dirs": [(1, 0), (-1, 0), (0, 1), (0, -1)],
        "priority": 0,
    },
    "armory": {
        "template": ROOM_LAB,
        "connect_dirs": [(1, 0), (-1, 0), (0, 1), (0, -1)],
        "priority": 2,
    },
    "barracks": {
        "template": ROOM_QUARTERS,
        "connect_dirs": [(1, 0), (-1, 0), (0, 1), (0, -1)],
        "priority": 2,
    },
    "war_chapel": {
        "template": ROOM_HANGAR,
        "connect_dirs": [(1, 0), (-1, 0), (0, 1), (0, -1)],
        "priority": 2,
    },
    "shield_gen": {
        "template": ROOM_COMMAND,
        "connect_dirs": [(1, 0), (-1, 0), (0, 1), (0, -1)],
        "priority": 2,
    },
    "conduit_h": {
        "template": CORRIDOR_H,
        "connect_dirs": [(1, 0), (-1, 0)],
        "priority": 1,
    },
    "conduit_v": {
        "template": CORRIDOR_V,
        "connect_dirs": [(0, 1), (0, -1)],
        "priority": 1,
    },
    "lance_h": {
        "template": SOLAR_WING_H,
        "connect_dirs": [(1, 0), (-1, 0)],
        "priority": 3,
    },
    "lance_v": {
        "template": SOLAR_WING_V,
        "connect_dirs": [(0, 1), (0, -1)],
        "priority": 3,
    },
    "reactor": {
        "template": ENGINE_POD,
        "connect_dirs": [(0, -1)],
        "priority": 3,
    },
    "sensor_spire": {
        "template": ANTENNA_TOWER,
        "connect_dirs": [(0, 1)],
        "priority": 3,
    },
    "augur_array": {
        "template": DISH_ARRAY,
        "connect_dirs": [(0, 1)],
        "priority": 3,
    },
}

# Map tools to fortress structures
TOOL_STRUCTURE_MAP = {
    "Edit": ["armory", "barracks", "conduit_h", "conduit_v"],
    "Write": ["war_chapel", "shield_gen", "conduit_h", "conduit_v"],
    "Read": ["lance_h", "lance_v", "augur_array"],
    "Grep": ["sensor_spire", "augur_array", "lance_h"],
    "Glob": ["sensor_spire", "lance_v"],
    "Bash": ["conduit_h", "conduit_v", "reactor"],
    "Agent": ["armory", "shield_gen", "barracks"],
    "WebSearch": ["augur_array", "sensor_spire"],
    "WebFetch": ["lance_h", "lance_v"],
    "Skill": ["war_chapel", "shield_gen", "reactor"],
}


class Station:
    """A space station rendered as a pixel grid."""

    CELL_PX = 5       # pixels per cell
    GRID_W = 160      # cells wide
    GRID_H = 110      # cells tall

    def __init__(self):
        self.grid = [[Cell.EMPTY for _ in range(self.GRID_W)] for _ in range(self.GRID_H)]
        self.placed_structures: list[dict] = []
        self.total_placed = 0
        self.has_core = False
        self._dirty = True  # need to re-render

        # Pre-render surface
        pw = self.GRID_W * self.CELL_PX
        ph = self.GRID_H * self.CELL_PX
        self.background = draw_space_background(pw, ph)
        self.station_surface = pygame.Surface((pw, ph), pygame.SRCALPHA)

    def _stamp_template(self, template: list, cx: int, cy: int) -> bool:
        """Stamp a structure template onto the grid at (cx, cy). Returns False if blocked."""
        rows = len(template)
        cols = max(len(r) for r in template)

        # Check if space is available (allow overlap with EMPTY only)
        for ry, row in enumerate(template):
            for rx, ch in enumerate(row):
                cell = CHAR_TO_CELL.get(ch)
                if cell is None:
                    continue
                gx = cx + rx
                gy = cy + ry
                if gx < 0 or gx >= self.GRID_W or gy < 0 or gy >= self.GRID_H:
                    return False
                if self.grid[gy][gx] != Cell.EMPTY:
                    return False

        # Stamp it
        for ry, row in enumerate(template):
            for rx, ch in enumerate(row):
                cell = CHAR_TO_CELL.get(ch)
                if cell is None:
                    continue
                self.grid[cy + ry][cx + rx] = cell

        self._dirty = True
        return True

    def _find_attach_point(self, template: list, near_px: float = -1, near_py: float = -1) -> Optional[Tuple[int, int]]:
        """Find a position where a template can attach to the existing station."""
        rows = len(template)
        cols = max(len(r) for r in template)

        # Find all cells that are station edge (adjacent to empty)
        edge_cells = set()
        for y in range(self.GRID_H):
            for x in range(self.GRID_W):
                if self.grid[y][x] != Cell.EMPTY:
                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.GRID_W and 0 <= ny < self.GRID_H:
                            if self.grid[ny][nx] == Cell.EMPTY:
                                edge_cells.add((nx, ny))

        if not edge_cells:
            return None

        # Try positions where the template would start near edge cells
        candidates = []
        for ex, ey in edge_cells:
            # Try placing template so various parts touch this edge cell
            for offset_y in range(rows):
                for offset_x in range(cols):
                    px = ex - offset_x
                    py = ey - offset_y
                    if self._can_stamp(template, px, py):
                        # Must actually touch existing station
                        if self._touches_station(template, px, py):
                            candidates.append((px, py))

        if not candidates:
            return None

        # Remove dupes
        candidates = list(set(candidates))

        # Prefer positions near agent
        if near_px >= 0 and near_py >= 0:
            agent_gx = near_px / self.CELL_PX
            agent_gy = near_py / self.CELL_PX
            candidates.sort(key=lambda p: (p[0] + cols // 2 - agent_gx) ** 2 + (p[1] + rows // 2 - agent_gy) ** 2)
            return candidates[0]

        # Otherwise pick randomly from best options (closer to center)
        center_x = self.GRID_W // 2
        center_y = self.GRID_H // 2
        candidates.sort(key=lambda p: (p[0] + cols // 2 - center_x) ** 2 + (p[1] + rows // 2 - center_y) ** 2)
        pick_from = max(1, len(candidates) // 3)
        return random.choice(candidates[:pick_from])

    def _can_stamp(self, template, cx, cy) -> bool:
        for ry, row in enumerate(template):
            for rx, ch in enumerate(row):
                cell = CHAR_TO_CELL.get(ch)
                if cell is None:
                    continue
                gx = cx + rx
                gy = cy + ry
                if gx < 0 or gx >= self.GRID_W or gy < 0 or gy >= self.GRID_H:
                    return False
                if self.grid[gy][gx] != Cell.EMPTY:
                    return False
        return True

    def _touches_station(self, template, cx, cy) -> bool:
        """Check if template placement would be adjacent to existing station."""
        for ry, row in enumerate(template):
            for rx, ch in enumerate(row):
                cell = CHAR_TO_CELL.get(ch)
                if cell is None:
                    continue
                gx = cx + rx
                gy = cy + ry
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < self.GRID_W and 0 <= ny < self.GRID_H:
                        if self.grid[ny][nx] != Cell.EMPTY:
                            # Make sure it's not part of our own template
                            lx, ly = nx - cx, ny - cy
                            if 0 <= ly < len(template) and 0 <= lx < len(template[ly]):
                                if CHAR_TO_CELL.get(template[ly][lx]) is not None:
                                    continue
                            return True
        return False

    def build(self, tool_name: str = "", agent_name: str = "",
              near_px: float = -1, near_py: float = -1) -> bool:
        """Build a structure. Returns True if successful."""
        if not self.has_core:
            return self._place_core()

        # Pick structure type based on tool
        options = TOOL_STRUCTURE_MAP.get(tool_name, ["conduit_h", "conduit_v"])

        # Try to connect a corridor first if we haven't built many yet
        corridor_count = sum(1 for s in self.placed_structures if s["name"].startswith("corridor"))
        room_count = sum(1 for s in self.placed_structures if s["name"] not in ("conduit_h", "conduit_v", "command_bastion"))

        # Balance: need corridors to connect rooms
        if room_count > corridor_count and random.random() < 0.6:
            options = ["conduit_h", "conduit_v"]

        random.shuffle(options)

        for struct_name in options:
            struct = STRUCTURES.get(struct_name)
            if not struct:
                continue

            template = struct["template"]
            pos = self._find_attach_point(template, near_px, near_py)
            if pos:
                if self._stamp_template(template, pos[0], pos[1]):
                    self.placed_structures.append({
                        "name": struct_name, "x": pos[0], "y": pos[1],
                        "placed_at": time.time(), "placed_by": agent_name,
                        "tool": tool_name,
                    })
                    self.total_placed += 1
                    return True

        # Fallback: try a corridor in any direction
        for fallback in ["conduit_h", "conduit_v"]:
            template = STRUCTURES[fallback]["template"]
            pos = self._find_attach_point(template, near_px, near_py)
            if pos and self._stamp_template(template, pos[0], pos[1]):
                self.placed_structures.append({
                    "name": fallback, "x": pos[0], "y": pos[1],
                    "placed_at": time.time(), "placed_by": agent_name,
                })
                self.total_placed += 1
                return True

        return False

    def build_event(self, event_key: str, agent_name: str = "",
                    near_px: float = -1, near_py: float = -1) -> bool:
        if not self.has_core:
            return self._place_core()

        event_tools = {
            "SessionStart": "Bash",
            "SubagentStart": "Agent",
            "PostToolUseFailure": "Grep",
        }
        return self.build(tool_name=event_tools.get(event_key, "Edit"),
                          agent_name=agent_name, near_px=near_px, near_py=near_py)

    def _place_core(self, agent_name: str = "system", tool_name: str = "") -> bool:
        cx = self.GRID_W // 2 - 5
        cy = self.GRID_H // 2 - 4
        if self._stamp_template(ROOM_CORE, cx, cy):
            self.has_core = True
            self.placed_structures.append({
                "name": "command_bastion", "x": cx, "y": cy,
                "placed_at": time.time(), "placed_by": agent_name,
                "tool": tool_name,
            })
            self.total_placed += 1
            return True
        return False

    def _render_station_surface(self):
        """Re-render the station to its surface."""
        self.station_surface.fill((0, 0, 0, 0))
        px = self.CELL_PX

        for y in range(self.GRID_H):
            for x in range(self.GRID_W):
                cell = self.grid[y][x]
                if cell == Cell.EMPTY:
                    continue
                color = CELL_COLORS.get(cell, (100, 100, 100))
                pygame.draw.rect(self.station_surface, color, (x * px, y * px, px, px))

        self._dirty = False

    def draw(self, screen: pygame.Surface, cam_x: float, cam_y: float,
             viewport_w: int = 0, viewport_h: int = 0):
        # Ensure background covers the full viewport by tiling if needed
        bg_w, bg_h = self.background.get_size()
        if viewport_w > 0 and viewport_h > 0:
            # Tile the background to cover any exposed area
            start_x = int(-cam_x) % bg_w - bg_w
            start_y = int(-cam_y) % bg_h - bg_h
            for ty in range(start_y, viewport_h, bg_h):
                for tx in range(start_x, viewport_w, bg_w):
                    screen.blit(self.background, (tx, ty))
        else:
            screen.blit(self.background, (-cam_x, -cam_y))

        if self._dirty:
            self._render_station_surface()

        screen.blit(self.station_surface, (-cam_x, -cam_y))

        # Animated effects
        now = time.time()
        px = self.CELL_PX

        for y in range(self.GRID_H):
            for x in range(self.GRID_W):
                cell = self.grid[y][x]
                if cell not in GLOW_CELLS:
                    continue

                sx = x * px - cam_x
                sy = y * px - cam_y

                r, g, b, base_a = GLOW_CELLS[cell]

                if cell == Cell.WINDOW:
                    # Gentle window glow
                    a = int(base_a + 15 * math.sin(now * 1.5 + x * 0.3 + y * 0.7))
                    glow = pygame.Surface((px + 2, px + 2), pygame.SRCALPHA)
                    glow.fill((r, g, b, max(0, min(255, a))))
                    screen.blit(glow, (sx - 1, sy - 1))

                elif cell == Cell.ANTENNA_TIP:
                    # Blink
                    if int(now * 2 + x) % 2:
                        glow = pygame.Surface((px + 4, px + 4), pygame.SRCALPHA)
                        pygame.draw.circle(glow, (r, g, b, base_a), (px // 2 + 2, px // 2 + 2), px)
                        screen.blit(glow, (sx - 2, sy - 2))

                elif cell == Cell.ENGINE:
                    # Thruster flicker
                    flicker = int(30 * math.sin(now * 8 + x * 3))
                    a = base_a + flicker
                    glow = pygame.Surface((px + 2, px + 4), pygame.SRCALPHA)
                    glow.fill((r, g, b, max(0, min(255, a))))
                    screen.blit(glow, (sx - 1, sy))

                elif cell == Cell.LIGHT:
                    a = int(base_a + 30 * math.sin(now * 3 + x + y))
                    glow = pygame.Surface((px + 2, px + 2), pygame.SRCALPHA)
                    glow.fill((r, g, b, max(0, min(255, a))))
                    screen.blit(glow, (sx - 1, sy - 1))

    def get_pixel_size(self):
        return (self.GRID_W * self.CELL_PX, self.GRID_H * self.CELL_PX)

    def save(self):
        os.makedirs(SAVE_DIR, exist_ok=True)
        # Save just the structure list, grid rebuilds from it
        data = {
            "version": 4, "type": "station_v2",
            "total_placed": self.total_placed,
            "structures": self.placed_structures,
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)

    def load(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            if data.get("type") != "station_v2":
                return
            for sd in data.get("structures", []):
                name = sd.get("name")
                struct = STRUCTURES.get(name)
                if not struct:
                    continue
                template = struct["template"]
                x, y = sd.get("x", 0), sd.get("y", 0)
                self._stamp_template(template, x, y)
                self.placed_structures.append(sd)
                if name == "command_bastion":
                    self.has_core = True
            self.total_placed = data.get("total_placed", len(self.placed_structures))
        except (json.JSONDecodeError, KeyError):
            pass

    def reset(self):
        self.grid = [[Cell.EMPTY for _ in range(self.GRID_W)] for _ in range(self.GRID_H)]
        self.placed_structures.clear()
        self.total_placed = 0
        self.has_core = False
        self._dirty = True
        pw, ph = self.get_pixel_size()
        self.background = draw_space_background(pw, ph)
        self.station_surface = pygame.Surface((pw, ph), pygame.SRCALPHA)
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)

    def get_stats(self):
        counts = {}
        for s in self.placed_structures:
            name = s["name"]
            counts[name] = counts.get(name, 0) + 1
        return counts
