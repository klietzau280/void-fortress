# VOID FORTRESS

### *In the grim darkness of the far future, there is only code.*

Watch your Claude Code agents as construction mechs building a space fortress in real-time. Every tool call forges another bulkhead. Every subagent deploys another battle-brother. Every error breaches the hull.

Your fortress is unique. Your fortress is yours.

---

## The Crew

| | | | |
|:---:|:---:|:---:|:---:|
| ![zealous](screenshots/face_zealous.png) | ![wrathful](screenshots/face_wrathful.png) | ![glorious](screenshots/face_glorious.png) | ![besieged](screenshots/face_besieged.png) |
| ZEALOUS | WRATHFUL | GLORIOUS | BESIEGED |

Doom-style pilot portraits. Each battle-brother gets a unique face. Visors glow with their current mood.

## The Mechs

| | | |
|:---:|:---:|:---:|
| ![idle](screenshots/mech_idle.png) | ![red](screenshots/mech_red.png) | ![weld](screenshots/mech_weld.png) |
| Standing watch | Moving to target | Welding bulkheads |

Claw wreckers with grabber arms and welding sparks. Session color-coded — you always know which crew belongs to which Claude Code instance.

---

## Features

- **Procedural fortress** grows as you code — Edit/Write builds armory walls, Read deploys augur arrays, Bash lays plasma conduits, Grep raises sensor spires
- **Claw wrecker mechs** fly to build sites with thruster flames, weld with sparks
- **Grimdark voice lines** — *"Yes my lord"*, *"Victory is ours"*, *"Requesting reinforcements"*
- **Pilot dossiers** — click any mech to inspect its battle-brother with a Doom-style portrait
- **Session crews** — multiple Claude Code sessions get different hull colors
- **Battle moods** — ZEALOUS when coding, WRATHFUL when fixing bugs, GLORIOUS on completion, BESIEGED when prod breaks
- **War thoughts** — *"The Codex Astartes supports this refactor"*, *"git blame reveals... HERESY"*

## Quick Start

```bash
git clone https://github.com/klietzau280/void-fortress.git
cd void-fortress
pip install pygame
```

### Demo Mode
```bash
python3 gui.py --demo
```

### Live Mode
```bash
# Install hooks into Claude Code
python3 gui.py --install

# Launch the fortress
python3 gui.py

# Use Claude Code in another terminal — watch the mechs build
```

## Controls

| Key | Action |
|-----|--------|
| **Click** | Inspect pilot dossier |
| **Tab** | Cycle mechs |
| **Space** | Pause / resume |
| **R** | Purge and rebuild |
| **Q** | Disengage |

## What You Build Depends on How You Code

| Claude Code Tool | Fortress Structure |
|-----------------|-------------------|
| Edit / Write | Armory, Barracks, War Chapel, Shield Generator |
| Read | Lance Battery, Augur Array |
| Grep / Glob | Sensor Spire, Lance Battery |
| Bash | Plasma Conduit, Reactor |
| Agent spawn | Armory, Shield Generator, Barracks |

## Requirements

- **macOS**
- **Python 3.9+**
- **pygame**
- **Claude Code**

## Credits

- **Voice**: [Sci-Fi Trooper Voice Pack](https://opengameart.org/content/sci-fi-trooper-voice-pack-54-lines) by Angus Macnaughton (CC-BY 4.0)
- **Portraits**: Procedural, inspired by Doom's STFST status bar sprites
- **Engine**: [pygame](https://www.pygame.org/)

---

*The Emperor protects. The Codex Astartes supports this action.*
