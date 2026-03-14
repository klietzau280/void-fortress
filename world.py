"""Void Fortress - world state (zones, notifications, tick counter).

Provides activity zones for agent movement and a notification system.
The visual station grid is handled by station.py; this module tracks
the logical world dimensions and notification queue.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List

# -- World defaults --
DEFAULT_WORLD_WIDTH = 80
DEFAULT_WORLD_HEIGHT = 24

# -- Notifications --
NOTIFICATION_MAX_BUFFER = 50
NOTIFICATION_TRIM_TO = 30
NOTIFICATION_EXPIRY_SEC = 30.0


@dataclass
class Zone:
    """A rectangular region of the world."""
    x: int
    y: int
    w: int
    h: int

    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)


@dataclass
class Notification:
    text: str
    icon: str
    color: str
    timestamp: float = field(default_factory=time.time)


class World:
    """Logical world state - zones and notifications."""

    def __init__(self, width: int = DEFAULT_WORLD_WIDTH, height: int = DEFAULT_WORLD_HEIGHT):
        self.width = width
        self.height = height
        self.tick = 0

        # Activity zones — working agents orbit the station center,
        # idle/waiting agents retreat to bottom-right corner
        cx, cy = width // 2, height // 2
        self.zones = {
            "coding":    Zone(cx - 8, cy - 4, 16, 8),
            "reading":   Zone(cx - 12, cy - 6, 10, 6),
            "searching": Zone(cx + 4, cy - 6, 10, 6),
            "testing":   Zone(cx - 6, cy + 2, 12, 6),
            "fixing":    Zone(cx - 4, cy - 2, 8, 4),
            "thinking":  Zone(cx + 6, cy + 1, 10, 5),
            "idle":      Zone(width - 16, height - 7, 12, 6),
            "waiting":   Zone(width - 16, height - 7, 12, 6),
        }

        self.notifications: List[Notification] = []

    def get_zone_for_activity(self, activity: str) -> Zone:
        return self.zones.get(activity, self.zones["idle"])

    def add_notification(self, text: str, icon: str = "", color: str = ""):
        self.notifications.append(Notification(text, icon, color))
        # Keep only recent notifications
        if len(self.notifications) > NOTIFICATION_MAX_BUFFER:
            self.notifications = self.notifications[-NOTIFICATION_TRIM_TO:]

    def update_notifications(self, now: float):
        # Expire old notifications (older than 30s)
        cutoff = now - NOTIFICATION_EXPIRY_SEC
        self.notifications = [n for n in self.notifications if n.timestamp > cutoff]
