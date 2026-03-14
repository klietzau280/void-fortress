"""Void Fortress - world state (zones, notifications, tick counter).

Provides activity zones for agent movement and a notification system.
The visual station grid is handled by station.py; this module tracks
the logical world dimensions and notification queue.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List


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

    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.tick = 0

        # Activity zones - rough areas where agents cluster by activity
        self.zones = {
            "coding":    Zone(10, 3, 20, 8),
            "reading":   Zone(35, 3, 15, 8),
            "searching": Zone(52, 3, 15, 8),
            "testing":   Zone(10, 12, 20, 8),
            "fixing":    Zone(35, 12, 15, 8),
            "thinking":  Zone(52, 12, 15, 8),
            "idle":      Zone(20, 8, 30, 6),
            "waiting":   Zone(20, 8, 30, 6),
        }

        self.notifications: List[Notification] = []

    def get_zone_for_activity(self, activity: str) -> Zone:
        return self.zones.get(activity, self.zones["idle"])

    def add_notification(self, text: str, icon: str = "", color: str = ""):
        self.notifications.append(Notification(text, icon, color))
        # Keep only recent notifications
        if len(self.notifications) > 50:
            self.notifications = self.notifications[-30:]

    def update_notifications(self, now: float):
        # Expire old notifications (older than 30s)
        cutoff = now - 30.0
        self.notifications = [n for n in self.notifications if n.timestamp > cutoff]
