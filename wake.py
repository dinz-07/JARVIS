import asyncio
import io
import math
import re
import subprocess
import sys
import time
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from services.headless_app import HeadlessApp

RATE = 16000
BLOCK = 1600
SPEECH_ON = 0.02
SPEECH_OFF = 0.008
START_BLOCKS = 4
END_BLOCKS = 12
MAX_SECONDS = 6.0
COOLDOWN = 2.5
LOG = ROOT / "wake_log.txt"
FLAG = ROOT / "wake_off.flag"


def _disabled():
    return FLAG.exists()


def _log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _rms(data):
    return math.sqrt(float(np.mean(np.square(data.astype(np.float64) / 32768.0))))


def capture_burst():
    blocks = []
    speaking = False
    on = 0
    off = 0
    t0 = time.time()
    with sd.InputStream(samplerate=RATE, channels=1, dtype="int16", blocksize=BLOCK) as stream:
        while True:
            data, _ = stream.read(BLOCK)
            rms = _rms(data)
            if not speaking:
                if rms > SPEECH_ON:
                    on += 1
                    blocks.append(data)
                    if on >= START_BLOCKS:
                        speaking = True
                        t0 = time.time()
                else:
                    on = 0
                    blocks = []
            else:
                blocks.append(data)
                if rms < SPEECH_OFF:
                    off += 1
                else:
                    off = 0
                if off >= END_BLOCKS or (time.time() - t0) > MAX_SECONDS:
                    break
    if not blocks:
        return None
    audio = np.concatenate(blocks)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(audio.tobytes())
    return buf.getvalue()


WAKE_WORDS = ["jarvis", "jarbis", "jarvi", "harvis", "jarwis", "jer vis", "ja rvis"]


def wake_command(low):
    low = re.sub(r"^(hey|ok|okay|hello|hi|yo|excuse me)\s+", "", low)
    for w in WAKE_WORDS:
        idx = low.find(w)
        if idx >= 0:
            return low[idx + len(w):].strip(" ,-:.")
    m = re.match(r"^(service|sir vis|survis)\b(.*)$", low)
    if m:
        return m.group(2).strip(" ,-:.")
    return None


def _ui_running():
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-Process flet -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like '*JARVIS*' }"],
            capture_output=True, text=True, timeout=15,
        )
        return bool(out.stdout and out.stdout.strip())
    except Exception:
        return False


def _launch_ui():
    try:
        subprocess.Popen([sys.executable, "main.py"], cwd=str(ROOT))
        return True
    except Exception as exc:
        _log("UI LAUNCH ERROR :: " + str(exc)[:100])
        return False


async def main():
    if _disabled():
        _log("wake listener DISABLED (wake_off.flag present) — delete the flag to re-enable")
        return
    app = HeadlessApp()
    _log("JARVIS wake listener online")
    _log("groq " + ("AVAILABLE" if app.groq.available else "UNAVAILABLE — voice fallback"))
    while True:
        if _disabled():
            _log("wake listener DISABLED via wake_off.flag")
            break
        try:
            _log("LISTENING for wake word...")
            burst = await asyncio.to_thread(capture_burst)
            if burst is None:
                continue
            text = ""
            if app.groq.available:
                try:
                    text = await app.groq.stt_bytes(burst)
                except Exception as exc:
                    _log("STT ERROR :: " + str(exc)[:80])
            low = text.lower()
            cmd = wake_command(low)
            if cmd is None:
                _log("ignored utterance :: " + (text or "(none)"))
                continue
            _log("WAKE WORD :: command = " + (cmd or "(empty)"))
            want_ui = not cmd or any(p in low for p in (
                "open jarvis", "launch jarvis", "open the interface", "start jarvis", "show the interface",
            ))
            if want_ui:
                if _ui_running():
                    response = "The interface is already open, sir."
                elif _launch_ui():
                    response = "Opening the interface, sir."
                else:
                    response = "Unable to launch the interface, sir."
            else:
                response = await app.engine.process(cmd, voice=True)
                if app.last_action == "module":
                    response = (
                        f"The {app.last_module} module runs inside the desktop interface, sir. "
                        "Open the application to view it."
                    )
                    app.last_action = None
                elif app.last_action == "scan":
                    response = "Threat scan executed. All sectors report clear, sir."
                    app.last_action = None
                elif app.last_action == "shutdown":
                    response = "Powering down is a desktop command, sir. Say open jarvis to launch the interface."
                    app.last_action = None
            _log("REPLY :: " + response.replace("\n", " ")[:100])
            if app.groq.available:
                try:
                    await app.groq.tts(response)
                except Exception as exc:
                    _log("TTS ERROR :: " + str(exc)[:80])
            await asyncio.sleep(COOLDOWN)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            _log("LOOP ERROR :: " + str(exc)[:120])
            await asyncio.sleep(1.0)


if __name__ == "__main__":
    asyncio.run(main())
