<p align="center">
  <img src="screenshots/mech_weld.png" width="120" />
</p>

<h1 align="center">VOID FORTRESS</h1>

<p align="center">
  <strong>In the grim darkness of the far future, there is only code.</strong>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &nbsp;&bull;&nbsp;
  <a href="#features">Features</a> &nbsp;&bull;&nbsp;
  <a href="#controls">Controls</a> &nbsp;&bull;&nbsp;
  <a href="#credits">Credits</a>
</p>

---

Your Claude Code agents are construction mechs building a space fortress in real-time. Every tool call forges another bulkhead. Every subagent deploys another battle-brother. Every error awakens the Necrons.

**Your fortress is unique. Your fortress is yours.**

---

## The Crew

<table>
  <tr>
    <td align="center"><img src="screenshots/face_zealous.png" width="96" /><br /><sub><b>ZEALOUS</b></sub></td>
    <td align="center"><img src="screenshots/face_wrathful.png" width="96" /><br /><sub><b>WRATHFUL</b></sub></td>
    <td align="center"><img src="screenshots/face_glorious.png" width="96" /><br /><sub><b>GLORIOUS</b></sub></td>
    <td align="center"><img src="screenshots/face_besieged.png" width="96" /><br /><sub><b>BESIEGED</b></sub></td>
  </tr>
</table>

Doom-style pilot portraits. Each battle-brother gets a unique face. Visors glow with their current mood.

## The Mechs

<table>
  <tr>
    <td align="center"><img src="screenshots/mech_idle.png" width="120" /><br /><sub>Standing watch</sub></td>
    <td align="center"><img src="screenshots/mech_red.png" width="120" /><br /><sub>Moving to target</sub></td>
    <td align="center"><img src="screenshots/mech_weld.png" width="120" /><br /><sub>Welding bulkheads</sub></td>
  </tr>
</table>

Claw wreckers with grabber arms and welding sparks. Session color-coded — you always know which crew belongs to which Claude Code instance.

---

## Features

| | |
|---|---|
| **Procedural fortress** | Grows as you code — Edit/Write builds armory walls, Read deploys augur arrays, Bash lays plasma conduits, Grep raises sensor spires |
| **Claw wrecker mechs** | Fly to build sites with thruster flames, weld with sparks — coding agents work the station, idle agents retreat to the corner |
| **Space radio comms** | All voice lines through a bandpass radio filter with static crackle and hiss, like transmissions from a distant void ship |
| **Necron incursions** | Errors awaken tomb world horrors: *"NECRON MONOLITH PHASING INTO THE REPO!"* ... *"The Deceiver's hand is in this logic"* |
| **Pilot dossiers** | Click any mech to inspect its battle-brother with a Doom-style portrait |
| **Session crews** | Multiple Claude Code sessions get different hull colors |
| **Battle moods** | ZEALOUS when coding, WRATHFUL fixing bugs, GLORIOUS on completion, BESIEGED when the Necrons attack |
| **War thoughts** | *"The Codex Astartes supports this refactor"* ... *"git blame reveals... HERESY"* |

---

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

---

## Controls

| Key | Action |
|:---:|--------|
| **Click** | Inspect pilot dossier |
| **Tab** | Cycle mechs |
| **Space** | Pause / resume |
| **R** | Purge and rebuild |
| **Q** | Disengage |

---

## What You Build Depends on How You Code

```
Claude Code Tool          Fortress Structure
─────────────────         ──────────────────────────────────────────
Edit / Write        -->   Armory, Barracks, War Chapel, Shield Generator
Read                -->   Lance Battery, Augur Array
Grep / Glob         -->   Sensor Spire, Lance Battery
Bash                -->   Plasma Conduit, Reactor
Agent spawn         -->   Armory, Shield Generator, Barracks
```

## Agent Behavior

| State | Behavior |
|-------|----------|
| Coding / Fixing / Testing | Mechs fly to the station and work on structures |
| Reading / Searching / Thinking | Mechs patrol their activity zones |
| Idle / Waiting | Mechs retreat to the bottom-right corner and hold position |
| Errors | 50% chance of full Necron panic, tomb world signatures, gauss flayer hits |

---

## Requirements

- **macOS**
- **Python 3.9+**
- **pygame**
- **Claude Code**

## Credits

- **Voice** — [Sci-Fi Trooper Voice Pack](https://opengameart.org/content/sci-fi-trooper-voice-pack-54-lines) by Angus Macnaughton (CC-BY 4.0), processed through space radio filter
- **Portraits** — Procedural, inspired by Doom's STFST status bar sprites
- **Engine** — [pygame](https://www.pygame.org/)

---

<p align="center">
  <em>The Emperor protects. The Codex Astartes supports this action. The Necrons do not care.</em>
</p>
