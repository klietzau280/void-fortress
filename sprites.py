"""Void Fortress - pixel art sprite generator.

Mech sprites (claw wreckers), pilot portraits (Doom-style faces),
and space junk / station decoration sprites for the fortress builder.
"""

from __future__ import annotations
import pygame
import math
import random


# Space junkyard palette
PALETTE = {
    "skin": (200, 220, 240),        # pale blue-white (space suit visor glow)
    "skin_shadow": (160, 180, 210),
    "hair_brown": (101, 67, 33),
    "hair_red": (180, 60, 30),
    "hair_blond": (230, 200, 100),
    "hair_black": (40, 30, 30),
    # Hull accent colors for mech variants
    "hull_acc_blue": (50, 100, 180),
    "hull_acc_red": (180, 50, 50),
    "hull_acc_green": (50, 160, 80),
    "hull_acc_purple": (120, 60, 170),
    "hull_acc_orange": (200, 120, 30),
    "hull_acc_cyan": (50, 180, 190),
    "hull_acc_yellow": (200, 190, 50),
    "hull_acc_dark": (70, 70, 90),
    "pants": (50, 50, 70),
    "pants_dark": (35, 35, 55),
    "shoes": (80, 80, 100),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "outline": (20, 20, 35),
    "shadow": (0, 0, 0, 60),
    # Mood colors
    "mood_happy": (100, 220, 80),
    "mood_ecstatic": (255, 220, 50),
    "mood_focused": (80, 180, 220),
    "mood_thinking": (100, 120, 220),
    "mood_confused": (200, 100, 220),
    "mood_frustrated": (220, 70, 70),
    "mood_bored": (150, 150, 150),
    "mood_panicking": (255, 40, 40),
    # Space
    "space_bg": (8, 8, 18),
    "space_bg2": (12, 10, 25),
    "star_dim": (80, 80, 100),
    "star_bright": (220, 220, 255),
    "star_warm": (255, 200, 140),
    "nebula_purple": (40, 15, 60),
    "nebula_blue": (15, 25, 55),
    "metal_light": (160, 165, 175),
    "metal": (120, 125, 135),
    "metal_dark": (80, 85, 95),
    "metal_rust": (140, 90, 60),
    "hull_blue": (60, 80, 120),
    "hull_green": (50, 90, 70),
    "glass": (140, 200, 230),
    "glass_dark": (80, 140, 170),
    "wire_red": (200, 50, 40),
    "wire_green": (40, 200, 80),
    "wire_yellow": (220, 200, 50),
    "energy_blue": (80, 160, 255),
    "energy_cyan": (100, 240, 255),
    "flame_orange": (255, 140, 30),
    "flame_yellow": (255, 220, 80),
    "crystal_purple": (160, 80, 220),
    "crystal_pink": (220, 100, 180),
    "toxic_green": (80, 255, 80),
    # ground
    "path": (60, 65, 80),
    "path_dark": (45, 48, 62),
}

HULL_COLORS = [
    "hull_acc_blue", "hull_acc_red", "hull_acc_green", "hull_acc_purple",
    "hull_acc_orange", "hull_acc_cyan", "hull_acc_yellow", "hull_acc_dark",
]


# --- Claw Wrecker sprites ---
# Industrial construction mechs with grabber arms.
# Power loader meets 40K servitor. They BUILD the fortress.
#
# h/H/d = hull highlight/mid/dark
# C/c   = claw/arm bright/dark
# G/g   = cockpit glass bright/dim
# M/m   = metal joint light/dark
# E/e   = exhaust/thruster
# F/f   = welding spark bright/dim
# Y     = spark core
# .     = transparent

MECH_IDLE = [
    "....hGGGd.......",
    "....hHGHHd......",
    "....hHHHHd......",
    "...hHHHHHHd.....",
    "C..hHHMMHHd..c..",
    "Cc.hHHMMHHd.cc..",
    "CcchHHHHHHdccc..",
    ".ccHHHHHHHHcc...",
    "...hHHHHHHd.....",
    "...hHHHHHHd.....",
    "..hHeH..eHHd....",
    "..eeee..eeee....",
]

MECH_WORK1 = [
    "....hGGGd.......",
    "....hHGHHd......",
    "....hHHHHd......",
    "C..hHHHHHHd.....",
    "Cc.hHHMMHHd.....",
    "CcchHHMMHHd..c..",
    ".cchHHHHHHdccc..",
    "...HHHHHHHHcc...",
    "...hHHHHHHd.....",
    "...hHHHHHHd.....",
    "..hHeH..eHHd....",
    "..eeee..eeee....",
    "..fFFf..........",
    "...ff...........",
]

MECH_WORK2 = [
    "....hGGGd.......",
    "....hHGHHd......",
    "....hHHHHd......",
    "...hHHHHHHd..C..",
    "...hHHMMHHd.cC..",
    "..chHHMMHHdccC..",
    ".cchHHHHHHdcc...",
    "..cHHHHHHHHc....",
    "...hHHHHHHd.....",
    "...hHHHHHHd.....",
    "..hHeH..eHHd....",
    "..eeee..eeee....",
    "..........fFFf..",
    "...........ff...",
]

MECH_WELD = [
    "....hGGGd.......",
    "....hHGHHd......",
    "....hHHHHd......",
    "C..hHHHHHHd..C..",
    "Cc.hHHMMHHd.cC..",
    "CcchHHMMHHdccC..",
    ".ccHHHHHHHHcc...",
    "...HHHHHHHHc....",
    "...hHHHHHHd.....",
    "...hHHHHHHd.....",
    "..hHeH..eHHd....",
    "..eeee..eeee....",
    "..fFFf..fFFf....",
    "..fYYf..fYYf....",
    "...ff....ff.....",
]

MECH_DOCKED = [
    "....hGGGd.......",
    "....hHGHHd......",
    "....hHHHHd......",
    "...hHHHHHHd.....",
    "...hHHMMHHd.....",
    "c..hHHMMHHd..c..",
    ".c.hHHHHHHd.c...",
    "...HHHHHHHHc....",
    "...hHHHHHHd.....",
    "...hHHHHHHd.....",
]


def _render_mech(template, hull_color_name, scale=3):
    """Render a mech with proper 3-shade hull + claw coloring."""
    rows = len(template)
    cols = max(len(r) for r in template)
    w = cols * scale
    h = rows * scale
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    hull = PALETTE[hull_color_name]
    hull_hi = tuple(min(255, c + 40) for c in hull)
    hull_dk = tuple(max(0, c - 35) for c in hull)

    # Claws are always steel/iron regardless of hull color
    claw_hi = (180, 180, 195)
    claw_dk = (110, 112, 125)

    color_map = {
        "h": hull_hi,
        "H": hull,
        "d": hull_dk,
        "C": claw_hi,
        "c": claw_dk,
        "G": PALETTE["glass"],
        "g": PALETTE["glass_dark"],
        "M": PALETTE["metal_light"],
        "m": PALETTE["metal"],
        "E": PALETTE["metal"],
        "e": PALETTE["metal_dark"],
        "F": PALETTE["flame_orange"],
        "f": (200, 100, 20),
        "Y": PALETTE["flame_yellow"],
        ".": None,
    }

    for ri, row in enumerate(template):
        for ci, ch in enumerate(row):
            color = color_map.get(ch)
            if color:
                pygame.draw.rect(surf, color, (ci * scale, ri * scale, scale, scale))

    return surf


def create_agent_sprites(hair_color: str, hull_color: str, scale: int = 3):
    """Create claw wrecker mech sprites."""
    return {
        "stand": _render_mech(MECH_IDLE, hull_color, scale),
        "walk1": _render_mech(MECH_WORK1, hull_color, scale),
        "walk2": _render_mech(MECH_WORK2, hull_color, scale),
        "celebrate": _render_mech(MECH_WELD, hull_color, scale),
        "panic": _render_mech(MECH_WELD, hull_color, scale),
        "sit": _render_mech(MECH_DOCKED, hull_color, scale),
    }


# --- Mood icons ---

def create_mood_icon(mood_name: str, size: int = 16):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    color_key = f"mood_{mood_name}"
    color = PALETTE.get(color_key, PALETTE["white"])

    pygame.draw.circle(surf, color, (size // 2, size // 2), size // 2 - 1)
    pygame.draw.circle(surf, PALETTE["outline"], (size // 2, size // 2), size // 2 - 1, 1)

    cx, cy = size // 2, size // 2
    if mood_name == "happy":
        pygame.draw.circle(surf, PALETTE["black"], (cx - 2, cy - 2), 1)
        pygame.draw.circle(surf, PALETTE["black"], (cx + 2, cy - 2), 1)
        pygame.draw.arc(surf, PALETTE["black"], (cx - 3, cy - 1, 6, 5), 3.14, 6.28, 1)
    elif mood_name == "ecstatic":
        _draw_star(surf, cx, cy, 4, PALETTE["black"])
    elif mood_name == "focused":
        pygame.draw.circle(surf, PALETTE["black"], (cx, cy), 3, 1)
        pygame.draw.circle(surf, PALETTE["black"], (cx, cy), 1)
    elif mood_name == "thinking":
        for i in range(3):
            pygame.draw.circle(surf, PALETTE["black"], (cx - 3 + i * 3, cy), 1)
    elif mood_name == "confused":
        font = pygame.font.SysFont(None, size - 2)
        txt = font.render("?", True, PALETTE["black"])
        surf.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))
    elif mood_name == "frustrated":
        pygame.draw.line(surf, PALETTE["black"], (cx - 3, cy - 3), (cx - 1, cy - 1), 1)
        pygame.draw.line(surf, PALETTE["black"], (cx + 3, cy - 3), (cx + 1, cy - 1), 1)
        pygame.draw.line(surf, PALETTE["black"], (cx - 2, cy + 2), (cx + 2, cy + 2), 1)
    elif mood_name == "bored":
        font = pygame.font.SysFont(None, size - 4)
        txt = font.render("z", True, PALETTE["black"])
        surf.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))
    elif mood_name == "panicking":
        font = pygame.font.SysFont(None, size - 2)
        txt = font.render("!", True, PALETTE["black"])
        surf.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))
    return surf


def _draw_star(surf, cx, cy, r, color):
    points = []
    for i in range(5):
        angle = math.radians(i * 72 - 90)
        points.append((cx + int(r * math.cos(angle)), cy + int(r * math.sin(angle))))
        angle2 = math.radians(i * 72 + 36 - 90)
        points.append((cx + int(r * 0.4 * math.cos(angle2)), cy + int(r * 0.4 * math.sin(angle2))))
    if len(points) >= 3:
        pygame.draw.polygon(surf, color, points)


# --- SPACE JUNK SPRITES ---

def _make_from_template(template, color_map, scale=3):
    w = len(template[0]) * scale
    h = len(template) * scale
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for ri, row in enumerate(template):
        for ci, ch in enumerate(row):
            c = color_map.get(ch)
            if c:
                pygame.draw.rect(surf, c, (ci * scale, ri * scale, scale, scale))
    return surf


def create_satellite_sprite(variant: int = 0, scale: int = 3):
    """Wrecked satellite / solar panel array."""
    if variant == 0:
        template = [
            "...MM...",
            "PPPMMPP.",
            "PPPMMPP.",
            "...MM...",
        ]
        cmap = {"M": PALETTE["metal"], "P": PALETTE["hull_blue"], ".": None}
    elif variant == 1:
        # Dish antenna
        template = [
            ".MMMM.",
            "MMMMMM",
            ".MMMM.",
            "..MM..",
            "..MM..",
            "..MM..",
        ]
        cmap = {"M": PALETTE["metal_light"], ".": None}
    else:
        # Small probe
        template = [
            "..AA..",
            ".MMMM.",
            ".MGGM.",
            ".MMMM.",
            "..RR..",
        ]
        cmap = {"M": PALETTE["metal"], "G": PALETTE["glass"], "A": PALETTE["metal_light"],
                "R": PALETTE["wire_red"], ".": None}
    return _make_from_template(template, cmap, scale)


def create_hull_chunk_sprite(variant: int = 0, scale: int = 3):
    """Torn hull plating - what code creates."""
    if variant == 0:
        template = [
            ".HHHH.",
            "HHHHHH",
            "HHHHH.",
            ".HHH..",
        ]
        cmap = {"H": PALETTE["hull_blue"], ".": None}
    elif variant == 1:
        template = [
            "..HHH.",
            ".HHHHH",
            "HHHHHH",
            "HHHHH.",
            ".HH...",
        ]
        cmap = {"H": PALETTE["hull_green"], ".": None}
    else:
        template = [
            "HHHH",
            "HWWH",
            "HWWH",
            "HHHH",
        ]
        cmap = {"H": PALETTE["metal"], "W": PALETTE["glass"], ".": None}
    return _make_from_template(template, cmap, scale)


def create_data_core_sprite(variant: int = 0, scale: int = 3):
    """Glowing data core - what reading/searching creates."""
    if variant == 0:
        template = [
            "..CC..",
            ".CCCC.",
            ".CEEC.",
            ".CCCC.",
            "..CC..",
        ]
        cmap = {"C": PALETTE["crystal_purple"], "E": PALETTE["energy_cyan"], ".": None}
    elif variant == 1:
        template = [
            ".CCC.",
            "CCECC",
            ".CCC.",
        ]
        cmap = {"C": PALETTE["crystal_pink"], "E": PALETTE["energy_blue"], ".": None}
    else:
        template = [
            ".CC.",
            "CEEC",
            "CEEC",
            ".CC.",
        ]
        cmap = {"C": PALETTE["energy_blue"], "E": PALETTE["white"], ".": None}
    return _make_from_template(template, cmap, scale)


def create_wire_tangle_sprite(variant: int = 0, scale: int = 3):
    """Loose wires and cables - what searching/grep creates."""
    if variant == 0:
        template = [
            "R..G..",
            ".RG..Y",
            "..RG..",
            ".R..GY",
            "R..G.Y",
        ]
        cmap = {"R": PALETTE["wire_red"], "G": PALETTE["wire_green"],
                "Y": PALETTE["wire_yellow"], ".": None}
    else:
        template = [
            ".RR...",
            "..RR..",
            "...RR.",
            "..RR..",
            ".RR...",
        ]
        cmap = {"R": PALETTE["wire_red"], ".": None}
    return _make_from_template(template, cmap, scale)


def create_thruster_sprite(scale: int = 3):
    """Detached thruster - what Bash/terminal creates."""
    template = [
        "..MMM..",
        ".MMMMM.",
        ".MMMMM.",
        "..MMM..",
        "..FFF..",
        "..FYF..",
        "...F...",
    ]
    cmap = {"M": PALETTE["metal_dark"], "F": PALETTE["flame_orange"],
            "Y": PALETTE["flame_yellow"], ".": None}
    return _make_from_template(template, cmap, scale)


def create_catwalk_sprite(scale: int = 3):
    """Metal catwalk / path tile."""
    template = [
        "MMMMMMMM",
        "M.M..M.M",
        "MMMMMMMM",
    ]
    cmap = {"M": PALETTE["metal_dark"], ".": PALETTE["metal"], "X": None}
    return _make_from_template(template, cmap, scale)


def create_crate_sprite(variant: int = 0, scale: int = 3):
    """Cargo crate - bench equivalent (agents sit on crates)."""
    if variant == 0:
        template = [
            "CCCCCC",
            "CDDDDC",
            "CDDDDC",
            "CCCCCC",
        ]
        cmap = {"C": PALETTE["metal_rust"], "D": PALETTE["metal_dark"], ".": None}
    else:
        template = [
            "CCCCCC",
            "CXCCXC",
            "CCCCCC",
        ]
        cmap = {"C": PALETTE["hull_blue"], "X": PALETTE["energy_cyan"], ".": None}
    return _make_from_template(template, cmap, scale)


def create_beacon_sprite(variant: int = 0, scale: int = 3):
    """Signal beacon / antenna - flag equivalent."""
    colors = [PALETTE["wire_red"], PALETTE["wire_green"], PALETTE["energy_blue"]]
    light = colors[variant % 3]
    template = [
        "..L..",
        "..L..",
        ".LLL.",
        "..M..",
        "..M..",
        "..M..",
        ".MMM.",
    ]
    cmap = {"L": light, "M": PALETTE["metal"], ".": None}
    return _make_from_template(template, cmap, scale)


def create_leak_sprite(scale: int = 3):
    """Toxic leak / puddle - error indicator."""
    template = [
        "..GG...",
        ".GGGG..",
        ".GGGGG.",
        "..GGGG.",
        "...GG..",
    ]
    cmap = {"G": PALETTE["toxic_green"], ".": None}
    return _make_from_template(template, cmap, scale)


def create_asteroid_sprite(variant: int = 0, scale: int = 3):
    """Small asteroid / space rock."""
    if variant == 0:
        template = [
            "..RR..",
            ".RRRR.",
            "RRRRRR",
            ".RRRR.",
            "..RR..",
        ]
    else:
        template = [
            ".RRR.",
            "RRRRR",
            "RRRRR",
            ".RRR.",
        ]
    cmap = {"R": (90, 80, 70), ".": None}
    return _make_from_template(template, cmap, scale)


def create_scrap_sprite(variant: int = 0, scale: int = 3):
    """Misc scrap metal."""
    if variant == 0:
        template = [
            "M..M",
            ".MM.",
            "MMMM",
            ".MM.",
        ]
    else:
        template = [
            ".MM.",
            "MM.M",
            ".MMM",
        ]
    cmap = {"M": PALETTE["metal_rust"], ".": None}
    return _make_from_template(template, cmap, scale)


def create_engine_sprite(scale: int = 3):
    """Big salvaged engine block."""
    template = [
        ".MMMMM.",
        "MMMMMMM",
        "MMGGGMM",
        "MMGGGMM",
        "MMMMMMM",
        ".MFFFM.",
        "..FYF..",
    ]
    cmap = {"M": PALETTE["metal"], "G": PALETTE["glass_dark"],
            "F": PALETTE["flame_orange"], "Y": PALETTE["flame_yellow"], ".": None}
    return _make_from_template(template, cmap, scale)


# --- Thought bubble (unchanged) ---

def create_thought_bubble(text: str, font: pygame.font.Font, max_width: int = 200):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if font.size(test)[0] <= max_width - 16:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if not lines:
        lines = ["..."]

    line_height = font.get_linesize()
    text_h = line_height * len(lines)
    bubble_w = max(font.size(line)[0] for line in lines) + 16
    bubble_h = text_h + 12

    surf = pygame.Surface((bubble_w, bubble_h + 10), pygame.SRCALPHA)
    bubble_rect = pygame.Rect(0, 0, bubble_w, bubble_h)
    pygame.draw.rect(surf, (20, 20, 40, 220), bubble_rect, border_radius=6)
    pygame.draw.rect(surf, (80, 80, 120), bubble_rect, 1, border_radius=6)

    pygame.draw.circle(surf, (20, 20, 40, 220), (bubble_w // 2, bubble_h + 3), 3)
    pygame.draw.circle(surf, (80, 80, 120), (bubble_w // 2, bubble_h + 3), 3, 1)
    pygame.draw.circle(surf, (20, 20, 40, 220), (bubble_w // 2 + 2, bubble_h + 7), 2)
    pygame.draw.circle(surf, (80, 80, 120), (bubble_w // 2 + 2, bubble_h + 7), 2, 1)

    for i, line in enumerate(lines):
        txt = font.render(line, True, (200, 210, 230))
        surf.blit(txt, (8, 6 + i * line_height))

    return surf


# --- Space background ---

def draw_space_background(width: int, height: int):
    """Create a starfield background."""
    surf = pygame.Surface((width, height))
    surf.fill(PALETTE["space_bg"])

    # Nebula patches
    for _ in range(8):
        nx = random.randint(0, width)
        ny = random.randint(0, height)
        nr = random.randint(40, 120)
        nebula_surf = pygame.Surface((nr * 2, nr * 2), pygame.SRCALPHA)
        color = random.choice([PALETTE["nebula_purple"], PALETTE["nebula_blue"]])
        for r in range(nr, 0, -2):
            alpha = int(15 * (r / nr))
            pygame.draw.circle(nebula_surf, (*color, alpha), (nr, nr), r)
        surf.blit(nebula_surf, (nx - nr, ny - nr))

    # Stars
    for _ in range(200):
        sx = random.randint(0, width)
        sy = random.randint(0, height)
        brightness = random.random()
        if brightness > 0.95:
            color = PALETTE["star_bright"]
            size = 2
        elif brightness > 0.8:
            color = PALETTE["star_warm"]
            size = 1
        else:
            color = PALETTE["star_dim"]
            size = 1
        pygame.draw.rect(surf, color, (sx, sy, size, size))

    return surf


def draw_path_tile(surf, x, y, tile_w, tile_h):
    """Draw a catwalk/grating path tile."""
    px = x * tile_w
    py = y * tile_h
    pygame.draw.rect(surf, PALETTE["path"], (px, py, tile_w, tile_h))
    # Grating lines
    for gx in range(0, tile_w, 6):
        pygame.draw.line(surf, PALETTE["path_dark"], (px + gx, py), (px + gx, py + tile_h), 1)
    for gy in range(0, tile_h, 6):
        pygame.draw.line(surf, PALETTE["path_dark"], (px, py + gy), (px + tile_w, py + gy), 1)



# --- PILOT PORTRAITS ---
# Doom-style faces at 31x33 pixels. Photographically-informed value mapping.
# Key insights from the original STFST sprites:
# - Eyes are HIGHEST CONTRAST: 2-3 dark pixels against lightest pixels on face
# - Nose implied by SHADOW not outline
# - Hue-shifted skin ramp: dark red-brown → orange → yellow-white
# - Top-left lighting: forehead bright, eye sockets dark, cheeks mid
# - Helmet/hair creates dark silhouette framing the face
# - 6-8 skin tones in a warm ramp

_portrait_cache = {}

# Skin ramp: dark shadow → shadow → mid-shadow → mid → mid-light → light → highlight
_SKIN = [
    (62, 35, 28),    # 0: deep shadow (under brow, jaw edge)
    (95, 55, 38),    # 1: shadow (eye socket, side of nose)
    (130, 82, 55),   # 2: mid-shadow (cheeks shadow side)
    (168, 115, 78),  # 3: midtone (most of face)
    (195, 145, 100),  # 4: mid-light (forehead, cheek highlight)
    (218, 178, 132),  # 5: light (nose bridge, brow bone)
    (235, 205, 165),  # 6: highlight (forehead peak, nose tip)
]

# Feature colors
_EYE_WHITE = (210, 210, 215)
_PUPIL = (18, 15, 12)
_MOUTH_DARK = (45, 25, 22)
_TEETH = (200, 195, 185)
_BLOOD = (160, 30, 25)

# Each portrait is a 31-wide array of rows. Values map to:
#  0-6 = skin ramp
#  H/h/d = helmet highlight/mid/dark
#  W = eye white, P = pupil, M = mouth dark, T = teeth, B = blood
#  . = transparent (background)

# Instead of text templates, we'll paint programmatically using zone maps

def _make_face(helmet_h, helmet_m, helmet_d, visor_color=None):
    """Paint a 31x33 Doom-style face onto a surface."""
    W, H = 31, 33
    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # Helper to draw a pixel
    def px(x, y, color):
        if 0 <= x < W and 0 <= y < H:
            surf.set_at((x, y), color)

    def rect(x, y, w, h, color):
        for dy in range(h):
            for dx in range(w):
                px(x + dx, y + dy, color)

    def skin(x, y, level):
        px(x, y, _SKIN[min(6, max(0, level))])

    # --- HELMET (rows 0-9) ---
    # Rounded top silhouette
    for row, (x_start, width) in enumerate([
        (11, 9), (9, 13), (7, 17), (6, 19), (5, 21),
        (4, 23), (4, 23), (3, 25), (3, 25), (3, 25),
    ]):
        for dx in range(width):
            x = x_start + dx
            # Gradient: highlight on left, shadow on right
            if dx < width // 3:
                px(x, row, helmet_h)
            elif dx < 2 * width // 3:
                px(x, row, helmet_m)
            else:
                px(x, row, helmet_d)

    # --- BROW RIDGE (rows 10-11) ---
    for dx in range(25):
        x = 3 + dx
        skin(x, 10, 0 if dx < 3 or dx > 21 else 1)
        skin(x, 11, 0 if dx < 2 or dx > 22 else 1)

    # --- EYE AREA (rows 12-15) ---
    # Skin around eyes - socket shadow
    for row in range(12, 16):
        for dx in range(25):
            x = 3 + dx
            skin(x, row, 1)  # dark socket base

    # Lighten cheek areas between and beside eyes
    for row in range(12, 16):
        for dx in range(3):
            skin(3 + dx, row, 2)      # left cheek
            skin(25 + dx, row, 0)     # right edge shadow
        skin(14, row, 2)              # nose bridge
        skin(15, row, 3)
        skin(16, row, 2)

    # LEFT EYE (centered around x=9, rows 12-14)
    # White
    for ey in range(13, 15):
        for ex in range(8, 13):
            px(ex, ey, _EYE_WHITE)
    # Pupil - 2 dark pixels
    px(10, 13, _PUPIL)
    px(11, 13, _PUPIL)
    px(10, 14, _PUPIL)
    px(11, 14, _PUPIL)
    # Eyelid shadow above
    for ex in range(8, 13):
        skin(ex, 12, 0)

    # RIGHT EYE (centered around x=21, rows 12-14)
    for ey in range(13, 15):
        for ex in range(18, 23):
            px(ex, ey, _EYE_WHITE)
    px(19, 13, _PUPIL)
    px(20, 13, _PUPIL)
    px(19, 14, _PUPIL)
    px(20, 14, _PUPIL)
    for ex in range(18, 23):
        skin(ex, 12, 0)

    # --- NOSE AREA (rows 16-19) ---
    for row in range(16, 20):
        for dx in range(25):
            x = 3 + dx
            # Light on left, shadow on right of nose
            if 13 <= x <= 17:
                if x == 15:
                    skin(x, row, 5)  # nose bridge highlight
                elif x < 15:
                    skin(x, row, 4)  # left of nose
                else:
                    skin(x, row, 2)  # right shadow
            elif x < 13:
                skin(x, row, 4 if x > 6 else 3)  # left cheek lit
            else:
                skin(x, row, 3 if x < 24 else 2)  # right cheek

    # Nostril shadows
    skin(13, 19, 1)
    skin(14, 19, 0)
    skin(16, 19, 0)
    skin(17, 19, 1)

    # --- MOUTH AREA (rows 20-24) ---
    for row in range(20, 25):
        for dx in range(23):
            x = 4 + dx
            skin(x, row, 3)

    # Mouth line
    for ex in range(10, 21):
        px(ex, 22, _MOUTH_DARK)
    # Upper lip shadow
    for ex in range(11, 20):
        skin(ex, 21, 2)
    # Lower lip highlight
    for ex in range(11, 20):
        skin(ex, 23, 4)

    # --- CHIN (rows 25-29) ---
    for row in range(25, 30):
        width = 23 - (row - 25) * 3
        x_start = 4 + (row - 25) * 1
        for dx in range(max(0, width)):
            x = x_start + dx
            if x < W:
                skin(x, row, 4 if dx < width // 2 else 2)

    # --- FOREHEAD HIGHLIGHT (rows 4-6, center) ---
    for row in range(4, 7):
        for dx in range(7):
            x = 12 + dx
            skin(x, row, 6)

    # Add visor overlay if helmeted
    if visor_color:
        for row in range(12, 16):
            for dx in range(23):
                x = 4 + dx
                px(x, row, visor_color)
        # Visor highlight
        bright = tuple(min(255, c + 60) for c in visor_color)
        for dx in range(5):
            px(8 + dx, 13, bright)

    return surf


# Pre-built face variants with different helmet colors
_FACE_VARIANTS = [
    # (helmet_h, helmet_m, helmet_d, visor_color_or_None)
    ((110, 120, 140), (70, 80, 100), (40, 48, 65), None),          # exposed face, blue helmet
    ((120, 100, 75), (85, 65, 48), (52, 38, 28), None),            # brown helmet
    ((90, 115, 85), (55, 80, 50), (32, 52, 30), None),             # green helmet
    ((130, 65, 55), (95, 40, 35), (60, 25, 22), None),             # red helmet
    ((100, 100, 110), (70, 70, 80), (42, 42, 52), None),           # dark steel
]

_VISOR_VARIANTS = [
    ((90, 95, 110), (60, 65, 80), (35, 40, 55), (50, 180, 255)),   # blue visor
    ((85, 90, 100), (58, 62, 75), (35, 38, 50), (50, 220, 70)),    # green visor
    ((100, 80, 70), (70, 55, 45), (42, 32, 28), (255, 140, 30)),   # orange visor
    ((80, 80, 95), (52, 52, 68), (30, 30, 42), (200, 50, 50)),     # red visor
    ((95, 90, 85), (65, 62, 58), (40, 38, 35), (180, 80, 220)),    # purple visor
]

MOOD_TINTS = {
    "happy": (20, 40, 10, 18),
    "ecstatic": (40, 35, 0, 22),
    "focused": (0, 20, 40, 12),
    "thinking": (10, 10, 30, 12),
    "confused": (30, 8, 35, 18),
    "frustrated": (50, 5, 0, 28),
    "bored": (0, 0, 0, 8),
    "panicking": (70, 0, 0, 38),
}


def create_pilot_portrait(seed: int, mood: str = "focused", size: int = 72):
    """Create a Doom-style face portrait."""
    cache_key = (seed, mood, size)
    if cache_key in _portrait_cache:
        return _portrait_cache[cache_key]

    all_variants = _FACE_VARIANTS + _VISOR_VARIANTS
    v = all_variants[seed % len(all_variants)]
    h_h, h_m, h_d, visor = v[0], v[1], v[2], v[3] if len(v) > 3 else None

    # Override visor color with mood for helmeted variants
    if visor:
        mood_visors = {
            "happy": (50, 220, 60),
            "ecstatic": (255, 230, 40),
            "focused": (50, 180, 255),
            "thinking": (80, 100, 240),
            "confused": (190, 80, 240),
            "frustrated": (240, 45, 30),
            "bored": (100, 100, 120),
            "panicking": (255, 20, 20),
        }
        visor = mood_visors.get(mood, visor)

    face = _make_face(h_h, h_m, h_d, visor)

    # Apply mood tint
    tint = MOOD_TINTS.get(mood)
    if tint:
        overlay = pygame.Surface(face.get_size(), pygame.SRCALPHA)
        overlay.fill(tint)
        face.blit(overlay, (0, 0))

    # Scale up - nearest neighbor for crispy pixels
    result = pygame.transform.scale(face, (size, size))

    _portrait_cache[cache_key] = result
    return result
