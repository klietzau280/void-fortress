"""Void Fortress - agent definitions with moods, personalities, and thought bubbles."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum

# -- Mood rendering --
ANSI_RESET = "\033[0m"

# -- Agent defaults --
DEFAULT_MOOD_STABILITY = 0.5
DEFAULT_ENERGY = 1.0

# -- Thought timing --
THOUGHT_TIMER_MIN = 2.0
THOUGHT_TIMER_MAX = 5.0

# -- Energy rates --
ENERGY_DRAIN_RATE = 0.02
ENERGY_RECOVER_RATE = 0.05

# -- Thought bubble (ASCII) --
THOUGHT_BUBBLE_MAX_WIDTH = 30

# -- Mood stability range --
MOOD_STABILITY_MIN = 0.3
MOOD_STABILITY_MAX = 0.9

# -- Spawn position ranges --
SPAWN_X_MIN = 5
SPAWN_X_MAX = 60
SPAWN_Y_MIN = 3
SPAWN_Y_MAX = 20

# -- Celebration --
CELEBRATION_THOUGHT_TIMER = 3.0


class Mood(Enum):
    ECSTATIC = ("GLORIOUS", "★", "\033[93m")       # victory
    HAPPY = ("RIGHTEOUS", "☺", "\033[92m")         # duty fulfilled
    FOCUSED = ("ZEALOUS", "◉", "\033[96m")         # combat focus
    THINKING = ("VIGILANT", "◎", "\033[94m")       # scanning
    CONFUSED = ("SUSPICIOUS", "?", "\033[95m")     # something's wrong
    FRUSTRATED = ("WRATHFUL", "!", "\033[91m")     # anger
    BORED = ("STOIC", "~", "\033[90m")             # standing watch
    PANICKING = ("BESIEGED", "‼", "\033[31m")      # under fire

    def __init__(self, label, icon, color):
        self.label = label
        self.icon = icon
        self.color = color

    @property
    def reset(self):
        return ANSI_RESET

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
        "Augur arrays at maximum sensitivity",
        "The grep-servitors found something...",
        "Sifting through the data-reliquary",
        "Signal detected. Origin: unknown tomb world",
        "Pattern-matching against known heresies",
        "The search-spirit stirs in the cogitator",
        "Cross-referencing the Forbidden Index",
    ],
    "reading": [
        "Studying the sacred texts of the codebase",
        "This ancient logic... it reeks of heresy",
        "Consulting the litanies of deployment",
        "The tech-priest who wrote this was mad",
        "Cross-referencing with the holy changelog",
        "These scrolls are older than the Imperium",
        "Decoding the machine spirit's memory",
        "The data-slate reveals troubling truths",
        "This was last touched by a heretek...",
        "Reading between the runes of the ancients",
        "The log files whisper of past battles",
        "Who wrote this?! Not a loyal servant.",
        "Interfacing with the knowledge-core",
        "The parchment is faded but the logic holds",
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
        "The weld holds. The Emperor protects.",
        "Laying adamantium logic into the hull",
        "Each line of code, a prayer to the Machine God",
        "This function shall be my monument",
        "Riveting new armor plating to the core",
        "The forge burns bright. The code takes shape.",
        "Tempering the logic in holy promethium",
        "Building ramparts against the darkness",
    ],
    "testing": [
        "Stress-testing the void shields...",
        "All wards holding. The Emperor protects.",
        "17 subsystems tainted. Initiating purge.",
        "The litany of verification begins",
        "Plasma containment nominal. For now.",
        "Running the Rites of Diagnostics",
        "If this fails, we all meet the Emperor",
        "Applying the Seven Seals of Verification",
        "The test-servitors report no anomalies",
        "Structural integrity at 97%. Acceptable.",
        "Simulation complete. Casualties: minimal.",
        "The warp drives test clean. Suspicious.",
        "All bulkheads sealed. Pressure holding.",
    ],
    "fixing": [
        "The corruption runs deeper than expected",
        "HULL BREACH ON DECK SEVEN",
        "Applying sacred unguents to the wound",
        "This bug is heresy of the highest order",
        "Sealing the breach with righteous fury",
        "The machine spirit cries out in pain",
        "git blame reveals... HERESY",
        "Necron tomb code awakening in prod...",
        "The Deceiver's hand is in this logic",
        "Gauss flayer errors stripping the hull",
        "We disturbed a Necron data-tomb. Fool.",
        "The code reassembles itself... NECRONS",
        "Living metal... the bug self-healed?!",
        "Cryptek sorcery in the stack trace",
        "The Nightbringer walks these pipelines",
        "Patching hull with ferrocrete and faith",
        "The wound festers. More sacred unguents.",
        "Rerouting power through backup conduits",
        "The taint must be excised. No mercy.",
        "Scarab traces in the memory banks...",
    ],
    "thinking": [
        "Consulting the strategic cogitators",
        "The Codex does not cover this scenario",
        "Weighing the Emperor's will...",
        "A thousand calculations, one truth",
        "The warp whispers solutions... I resist",
        "Planning the next crusade",
        "There must be a purer path forward",
        "Running probability matrices...",
        "The tactical display shows... options",
        "Calibrating the strategic auguries",
        "Communing with the machine spirit",
        "The answer lies buried in the data-vaults",
        "Weighing the cost in blood and logic",
        "The cogitator banks hum with purpose",
    ],
    "waiting": [
        "Standing vigil at my post",
        "Awaiting orders from command",
        "Even in stillness, I serve",
        "My blade is ready. My patience... less so.",
        "The silence between battles is the loudest",
        "Maintaining combat readiness",
        "Eternal vigilance is the price of purity",
        "The void is cold. My duty keeps me warm.",
        "Listening to the hum of the reactor",
        "Counting rivets. Checking seals. Again.",
        "The watch is long but the will endures",
        "Reciting the Litany of Patience...",
        "Nothing on the auspex. Good.",
    ],
    "celebrating": [
        "VICTORY FOR THE IMPERIUM!",
        "The fortress grows. The enemy trembles.",
        "Another heresy purged from the codebase",
        "The machine spirit sings with approval",
        "Glory to the chapter! Zero defects!",
        "The Emperor smiles upon this deploy",
        "We are steel. We are doom. We are DONE.",
        "Sound the warhorn! The task is complete!",
        "Mark this day in the Fortress Codex!",
        "The servitors cheer. Wait, servitors can't cheer.",
        "Deploy successful. The void trembles.",
        "The Imperium endures. So does my code.",
    ],
    "panicking": [
        "THE VOID SHIELDS ARE FAILING!",
        "WARP BREACH IN THE MAIN REACTOR!",
        "FALL BACK! FALL BACK!",
        "The corruption has spread to production!",
        "By the Throne... who pushed to main?!",
        "ALL HANDS TO BATTLE STATIONS!",
        "We are undone. The Codex has no answer.",
        "NECRON MONOLITH PHASING INTO THE REPO!",
        "THE TOMB WORLD HAS AWAKENED!",
        "Scarabs consuming the build artifacts!",
        "A Necron Lord commands this exception!",
        "GAUSS FLUX ARC HIT THE MAIN BRANCH!",
        "The C'tan shard hungers for our uptime",
        "Flayed Ones in the dependency tree!",
        "DESTROYER CULT IN THE CI PIPELINE!",
        "MULTIPLE HULL BREACHES! DECKS 3 THROUGH 9!",
        "The reactor is going critical! EVACUATE!",
        "Necron phase-shift detected in the kernel!",
        "THE TESSERACT VAULT IS OPEN!",
        "Wraith constructs in the memory allocator!",
        "The Void Dragon stirs beneath the code!",
    ],
    "idle": [
        "Standing watch over the void",
        "The stars hold no comfort, only duty",
        "Awaiting the next crusade...",
        "Sharpening my resolve",
        "The fortress is quiet. Too quiet.",
        "Meditating on the Litany of Deployment",
        "In the grim darkness there is only code",
        "Staring into the void. It stares back.",
        "The servitor brought recaf. Lukewarm.",
        "Polishing the hull. It calms the spirit.",
        "Running maintenance on my welding arm",
        "The void hums. Or is that the reactor?",
        "Another shift. Another empty auspex.",
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
    "Rhadamant", "Thorne", "Calgar", "Orion",
    "Solaria", "Myrmidon", "Zephon", "Baldur",
    "Ursarax", "Tyber", "Valeria", "Khorven",
    "Artemis", "Reclus", "Veridian", "Kasr",
    "Mortarion", "Aethon", "Seraphina", "Volkov",
    "Nemiel", "Targon", "Ixion", "Lyander",
    "Drusus", "Fenix", "Rhovan", "Imperius",
    "Sariel", "Haldor", "Nyx", "Cassius",
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
    mood_stability: float = DEFAULT_MOOD_STABILITY  # 0 = volatile, 1 = stable
    energy: float = DEFAULT_ENERGY  # 0 = exhausted, 1 = full
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

    def get_thought_bubble(self, max_width=THOUGHT_BUBBLE_MAX_WIDTH):
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
            self.thought_timer = random.uniform(THOUGHT_TIMER_MIN, THOUGHT_TIMER_MAX)

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
            self.energy = max(0.0, self.energy - dt * ENERGY_DRAIN_RATE)
        else:
            self.energy = min(DEFAULT_ENERGY, self.energy + dt * ENERGY_RECOVER_RATE)

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
        self.thought_timer = CELEBRATION_THOUGHT_TIMER


def spawn_agent(agent_id, role=None, parent_id=None, is_subagent=False, exclude_names=None):
    """Create a new agent with random traits."""
    available = [n for n in AGENT_NAMES if n not in (exclude_names or ())]
    name = random.choice(available) if available else random.choice(AGENT_NAMES)
    role = role or random.choice(list(AgentRole))
    personality = random.choice(PERSONALITY_TRAITS)
    mood_stability = random.uniform(MOOD_STABILITY_MIN, MOOD_STABILITY_MAX)

    return Agent(
        id=agent_id,
        name=name,
        role=role,
        personality=personality,
        mood_stability=mood_stability,
        parent_id=parent_id,
        is_subagent=is_subagent,
        x=random.randint(SPAWN_X_MIN, SPAWN_X_MAX),
        y=random.randint(SPAWN_Y_MIN, SPAWN_Y_MAX),
        target_x=random.randint(SPAWN_X_MIN, SPAWN_X_MAX),
        target_y=random.randint(SPAWN_Y_MIN, SPAWN_Y_MAX),
    )
