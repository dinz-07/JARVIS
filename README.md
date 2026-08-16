# JARVIS — AI Command Experience

A desktop AI command center built with [Flet](https://flet.dev), styled like an Iron Man / Ultron interface — pure black + neon cyan, Orbitron typography, a rotating hexagon-lattice neural core, and state-driven animations for every AI phase.

## Features

- **Full voice agent** — Groq-powered pipeline: speech-to-text (whisper), LLM reasoning (gpt-oss), text-to-speech (orpheus)
- **Barge-in conversation** — speak anytime while JARVIS is talking
- **Wake word mode** — runs headless (no window), listens in the background, opens the desktop UI on trigger
- **State-driven core animations** — standby, listening (radar + mic waveform), thinking (chasing arcs + scan beam), speaking (voice-reactive waveform), executing (progress sweep) — each with its own color
- **8 modules** — system, weather, calendar, tasks, music, email, security, browser (open with `1`–`8` or voice)
- **Live HUD** — CPU / GPU / RAM / network / battery telemetry with connector lines
- **Ambient background** — particle field with links, grid scanlines, corner brackets; particles repel from your cursor with a pulsing cursor aura
- **Settings panel** — voice on/off, sound effects, particle density, HUD intensity, animations, reduced motion
- **Boot & shutdown sequences** — cinematic intro and exit screens

## Requirements

- Python 3.10+
- A [Groq](https://console.groq.com) API key (for STT / LLM / TTS)
- Microphone + speakers

## Setup

```bash
git clone https://github.com/dinz-07/JARVIS.git
cd JARVIS
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
pip install groq numpy sounddevice python-dotenv
```

Create a `.env` file in the project root (copy from `.env.example`):

```
GROQ_API_KEY=your_key_here
```

## Run

```bash
python main.py
```

Or double-click `jarvis.bat` (Windows).

## Controls

| Key | Action |
| --- | --- |
| `Enter` | Submit command |
| `Esc` | Back / clear / close panel |
| `Ctrl+M` | Toggle voice mode |
| `Ctrl+Q` / `Ctrl+C` | Shutdown |
| `F11` / `Ctrl+F` | Fullscreen |
| `1` – `8` | Open module |
| `S` | Settings panel |

## Wake mode (headless)

```bash
python wake.py
```

Listens for the wake word without the UI. `wake_on.bat` enables auto-start at login, `wake_off.bat` disables it.

## Structure

```
app/            main UI, state machine, theme
components/     core animation, HUD, modules, particles, command bar
services/       voice pipeline, Groq engine, actions, system monitor
assets/fonts/   Orbitron + Exo 2
main.py         entry point
wake.py         headless wake-word listener
```

## Notes

- `.env` is git-ignored — never commit API keys.
- Voice pipeline degrades gracefully to text-only if Groq is unreachable.