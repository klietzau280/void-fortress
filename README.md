# VOID FORTRESS

> *In the grim darkness of the far future, there is only code.*

Watch your Claude Code agents as construction mechs building a space fortress in real-time. Every tool call, every subagent spawn, every error -- rendered as mechs welding hull plating onto a growing orbital fortress.

## Features

- **Construction Mechs with Welding Sparks** -- Your agents manifest as armored mechs, flying to build sites and bolting modules onto the station as they work.
- **Doom-Style Pilot Portraits** -- Each mech has a procedurally generated pilot portrait. Click to inspect their dossier.
- **Procedural Fortress That Grows As You Code** -- Every tool call adds structure. Edits weld hull plating. Grep searches deploy scanner arrays. Errors leave damage craters.
- **Grimdark Voice Lines** -- "Yes my lord", "Victory is ours", "The machine spirit is willing". Sci-fi trooper barks play on session events.
- **Session Color-Coding** -- Multiple Claude instances get different hull accent colors so you can tell your mechs apart.
- **Click-to-Inspect Pilot Dossiers** -- Name, rank, mood, personality, current thought, energy level. Everything a field commander needs.

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/klietzau280/void-fortress.git
cd void-fortress

# 2. Install dependencies
pip install pygame

# 3. Install Claude Code hooks
python3 gui.py --install

# 4. Demo mode (no Claude Code needed)
python3 gui.py --demo

# 5. Real mode (start Claude Code in another terminal first)
python3 gui.py
```

The `--install` command writes hook entries to `~/.claude/settings.json` so that every Claude Code event (tool use, session start, errors, etc.) gets logged for the GUI to consume.

## Controls

| Key | Action |
|-----|--------|
| **Tab** | Cycle through mechs |
| **Space** | Pause / Resume |
| **Click** | Inspect a mech's pilot dossier |
| **R** | Purge the fortress and rebuild from nothing |
| **Q / Esc** | Disengage |
| **Right-drag** | Pan the camera |
| **+/-** | Adjust simulation speed |

## How It Works

1. Claude Code fires hook events (tool use, session start/end, errors, subagent spawns)
2. `hook.sh` logs each event as JSONL to `~/.agent-valley/events.jsonl`
3. The GUI tails the event file and translates events into mech activities
4. Mechs move to work zones, build station modules, and react with mood changes
5. Sounds play through pygame.mixer when events fire (session start, task complete, errors, etc.)

## Credits

- **Voice**: Sci-Fi Trooper Voice Pack by Angus Macnaughton ([CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/))
- **Portraits**: Inspired by Doom's STFST sprites
- **Built with**: [pygame](https://www.pygame.org/)

---

*The Emperor protects. But having a visual dashboard helps too.*
