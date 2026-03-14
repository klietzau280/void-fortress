# VOID FORTRESS

### *In the grim darkness of the far future, there is only code.*

Watch your Claude Code agents as construction mechs building a space fortress in real-time. Every tool call forges another bulkhead. Every subagent deploys another battle-brother. Every error awakens the Necrons.

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
- **Claw wrecker mechs** fly to build sites with thruster flames, weld with sparks — coding agents work directly on the station, idle agents retreat to the corner
- **Space radio comms** — all voice lines processed through a bandpass radio filter with static crackle and hiss, like transmissions from a distant void ship
- **Necron incursions** — errors awaken tomb world horrors: *"NECRON MONOLITH PHASING INTO THE REPO!"*, *"Scarab swarm consuming the build artifacts!"*, *"The Deceiver's hand is in this logic"*
- **Pilot dossiers** — click any mech to inspect its battle-brother with a Doom-style portrait
- **Session crews** — multiple Claude Code sessions get different hull colors
- **Battle moods** — ZEALOUS when coding, WRATHFUL when fixing bugs, GLORIOUS on completion, BESIEGED when the Necrons attack
- **War thoughts** — *"The Codex Astartes supports this refactor"*, *"git blame reveals... HERESY"*, *"Cryptek sorcery in the stack trace"*

## Quick Start

```bash
git clone https://github.com/klietzau280/void-fortress.git
cd void-fortress

# Install everything (pygame + Claude Code hooks)
./install.sh

# Launch the fortress
python3 gui.py
```

That's it. Open Claude Code in another terminal and watch the mechs build.

### Demo Mode

Don't have Claude Code? Watch the mechs anyway:

```bash
python3 gui.py --demo
```

### Uninstall

```bash
./uninstall.sh
```

Removes the hooks from Claude Code. Your other settings are untouched.

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

## Agent Behavior

- **Coding / Fixing / Testing** — mechs fly to the station and work on structures
- **Reading / Searching / Thinking** — mechs patrol their activity zones
- **Idle / Waiting** — mechs retreat to the bottom-right corner and hold position
- **Errors** — 50% chance of full Necron panic, tomb world signatures, gauss flayer hits

## Requirements

- **macOS**
- **Python 3.9+**
- **pygame**
- **Claude Code**

## Credits

- **Voice**: [Sci-Fi Trooper Voice Pack](https://opengameart.org/content/sci-fi-trooper-voice-pack-54-lines) by Angus Macnaughton (CC-BY 4.0), processed through space radio filter
- **Portraits**: Procedural, inspired by Doom's STFST status bar sprites
- **Engine**: [pygame](https://www.pygame.org/)

---

*The Emperor protects. The Codex Astartes supports this action. The Necrons do not care.*
