"""Void Fortress - agent definitions with moods, personalities, and thought bubbles."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum


class Mood(Enum):
    ECSTATIC = ("ecstatic", "★", "\033[93m")      # bright yellow
    HAPPY = ("happy", "☺", "\033[92m")             # green
    FOCUSED = ("focused", "◉", "\033[96m")         # cyan
    THINKING = ("thinking", "◎", "\033[94m")       # blue
    CONFUSED = ("confused", "?", "\033[95m")        # magenta
    FRUSTRATED = ("frustrated", "!", "\033[91m")    # red
    BORED = ("bored", "~", "\033[90m")             # gray
    PANICKING = ("panicking", "‼", "\033[31m")     # dark red

    def __init__(self, label, icon, color):
        self.label = label
        self.icon = icon
        self.color = color

    @property
    def reset(self):
        return "\033[0m"

    def render(self):
        return f"{self.color}{self.icon}{self.reset}"


class AgentRole(Enum):
    MAIN = "main"
    EXPLORER = "explorer"
    PLANNER = "planner"
    CODER = "coder"
    TESTER = "tester"
    RESEARCHER = "researcher"
    REVIEWER = "reviewer"
    FIXER = "fixer"


# Thought templates per activity - GRIMDARK
THOUGHTS = {
    "searching": [
        "Scanning for heretical code signatures",
        "The omnissiah guides my search",
        "Purging the index for forbidden knowledge",
        "I sense corruption in this sector",
        "By the Throne, where is that file",
        "The machine spirit resists my queries",
        "Sweeping for xenos artifacts...",
    ],
    "reading": [
        "Studying the sacred texts of the codebase",
        "This ancient logic... it reeks of heresy",
        "Consulting the litanies of deployment",
        "The tech-priest who wrote this was mad",
        "Cross-referencing with the holy changelog",
        "These scrolls are older than the Imperium",
        "Decoding the machine spirit's memory",
    ],
    "coding": [
        "Forging new bulkheads for the fortress",
        "Inscribing the sacred runes of logic",
        "The machine spirit accepts my offering",
        "Reinforcing the walls against corruption",
        "Another module welded to the bastion",
        "My duty is my shield. My code is my sword.",
        "The Codex Astartes supports this refactor",
        "Purging weakness from the architecture",
    ],
    "testing": [
        "Stress-testing the void shields...",
        "All wards holding. The Emperor protects.",
        "17 subsystems tainted. Initiating purge.",
        "The litany of verification begins",
        "Plasma containment nominal. For now.",
        "Running the Rites of Diagnostics",
        "If this fails, we all meet the Emperor",
    ],
    "fixing": [
        "The corruption runs deeper than expected",
        "HULL BREACH ON DECK SEVEN",
        "Applying sacred unguents to the wound",
        "This bug is heresy of the highest order",
        "Sealing the breach with righteous fury",
        "The machine spirit cries out in pain",
        "git blame reveals... HERESY",
    ],
    "thinking": [
        "Consulting the strategic cogitators",
        "The Codex does not cover this scenario",
        "Weighing the Emperor's will...",
        "A thousand calculations, one truth",
        "The warp whispers solutions... I resist",
        "Planning the next crusade",
        "There must be a purer path forward",
    ],
    "waiting": [
        "Standing vigil at my post",
        "Awaiting orders from command",
        "Even in stillness, I serve",
        "My blade is ready. My patience... less so.",
        "The silence between battles is the loudest",
        "Maintaining combat readiness",
        "Eternal vigilance is the price of purity",
    ],
    "celebrating": [
        "VICTORY FOR THE IMPERIUM!",
        "The fortress grows. The enemy trembles.",
        "Another heresy purged from the codebase",
        "The machine spirit sings with approval",
        "Glory to the chapter! Zero defects!",
        "The Emperor smiles upon this deploy",
        "We are steel. We are doom. We are DONE.",
    ],
    "panicking": [
        "THE VOID SHIELDS ARE FAILING!",
        "WARP BREACH IN THE MAIN REACTOR!",
        "FALL BACK! FALL BACK!",
        "The corruption has spread to production!",
        "By the Throne... who pushed to main?!",
        "ALL HANDS TO BATTLE STATIONS!",
        "We are undone. The Codex has no answer.",
    ],
    "idle": [
        "Standing watch over the void",
        "The stars hold no comfort, only duty",
        "Awaiting the next crusade...",
        "Sharpening my resolve",
        "The fortress is quiet. Too quiet.",
        "Meditating on the Litany of Deployment",
        "In the grim darkness there is only code",
    ],
}

# Names pool - Battle-Brothers and Sisters
AGENT_NAMES = [
    "Titus", "Castus", "Severus", "Mordecai",
    "Theron", "Grimnar", "Vael", "Korrath",
    "Decimus", "Ferrus", "Sigrid", "Ashara",
    "Malakai", "Draven", "Kael", "Voss",
    "Praxis", "Thanatos", "Helion", "Corvin",
    "Vex", "Kragg", "Steele", "Arcturus",
]

# Personality traits - grimdark edition
PERSONALITY_TRAITS = [
    "zealous", "grim", "wrathful", "stoic",
    "fanatical", "ruthless", "disciplined", "relentless",
]


@dataclass
class Agent:
    id: int
    name: str
    role: AgentRole
    personality: str
    mood: Mood = Mood.HAPPY
    x: int = 0
    y: int = 0
    target_x: int = 0
    target_y: int = 0
    activity: str = "idle"
    thought: str = ""
    thought_timer: float = 0
    mood_stability: float = 0.5  # 0 = volatile, 1 = stable
    energy: float = 1.0  # 0 = exhausted, 1 = full
    tasks_completed: int = 0
    parent_id: int | None = None
    spawn_time: float = field(default_factory=time.time)
    is_subagent: bool = False
    walk_frame: int = 0

    # Sprite parts (ASCII art building blocks)
    BODY_FRAMES = [
        # Frame 0 - standing
        [" o ", "/|\\", "/ \\"],
        # Frame 1 - walk left
        [" o ", "/|\\", "/ >"],
        # Frame 2 - walk right
        [" o ", "/|\\", "< \\"],
        # Frame 3 - celebrating
        [" o ", "\\|/", "/ \\"],
        # Frame 4 - panicking
        [" o ", " |>", "< \\"],
    ]

    def get_sprite(self):
        """Get the current sprite frame based on mood and movement."""
        if self.mood == Mood.ECSTATIC:
            frame = self.BODY_FRAMES[3]
        elif self.mood == Mood.PANICKING:
            frame = self.BODY_FRAMES[4]
        elif self.x != self.target_x or self.y != self.target_y:
            frame = self.BODY_FRAMES[1 + (self.walk_frame % 2)]
        else:
            frame = self.BODY_FRAMES[0]
        return frame

    def get_thought_bubble(self, max_width=30):
        """Render a thought bubble above the agent."""
        if not self.thought:
            return []

        # Truncate thought to fit
        text = self.thought[:max_width - 4]
        width = len(text) + 2
        top = "." + "-" * width + "."
        mid = f"| {text} |"
        bot = "'" + "-" * width + "'"
        tail = "  o"
        return [top, mid, bot, tail]

    def update_thought(self, dt):
        """Update thought bubble timer and pick new thoughts."""
        self.thought_timer -= dt
        if self.thought_timer <= 0:
            self.thought = random.choice(THOUGHTS.get(self.activity, THOUGHTS["idle"]))
            self.thought_timer = random.uniform(2.0, 5.0)

    def update_mood(self, dt):
        """Update mood based on activity. Stable - no random flickering."""
        # Activity directly determines mood
        activity_mood = {
            "coding": Mood.FOCUSED,
            "reading": Mood.THINKING,
            "searching": Mood.THINKING,
            "testing": Mood.FOCUSED,
            "fixing": Mood.FRUSTRATED,
            "thinking": Mood.THINKING,
            "waiting": Mood.BORED,
            "celebrating": Mood.ECSTATIC,
            "panicking": Mood.PANICKING,
            "idle": Mood.BORED,
        }
        target_mood = activity_mood.get(self.activity)
        if target_mood:
            self.mood = target_mood

        # Energy drain
        if self.activity not in ("idle", "waiting"):
            self.energy = max(0.0, self.energy - dt * 0.02)
        else:
            self.energy = min(1.0, self.energy + dt * 0.05)

    def move_toward_target(self):
        """Move one step toward target position."""
        if self.x < self.target_x:
            self.x += 1
        elif self.x > self.target_x:
            self.x -= 1
        if self.y < self.target_y:
            self.y += 1
        elif self.y > self.target_y:
            self.y -= 1
        self.walk_frame += 1

    def set_new_wander_target(self, max_x, max_y):
        """Pick a new random position to wander to."""
        self.target_x = random.randint(2, max_x - 10)
        self.target_y = random.randint(2, max_y - 6)

    def complete_task(self):
        """Mark current task as done."""
        self.tasks_completed += 1
        self.mood = Mood.ECSTATIC
        self.activity = "celebrating"
        self.thought = random.choice(THOUGHTS["celebrating"])
        self.thought_timer = 3.0


def spawn_agent(agent_id, role=None, parent_id=None, is_subagent=False):
    """Create a new agent with random traits."""
    name = random.choice(AGENT_NAMES)
    role = role or random.choice(list(AgentRole))
    personality = random.choice(PERSONALITY_TRAITS)
    mood_stability = random.uniform(0.3, 0.9)

    return Agent(
        id=agent_id,
        name=name,
        role=role,
        personality=personality,
        mood_stability=mood_stability,
        parent_id=parent_id,
        is_subagent=is_subagent,
        x=random.randint(5, 60),
        y=random.randint(3, 20),
        target_x=random.randint(5, 60),
        target_y=random.randint(3, 20),
    )
