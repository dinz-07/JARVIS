import datetime
import random
import webbrowser

from app.state import LISTENING, SPEAKING, THINKING, IDLE

MODULES = ["SYSTEM", "WEATHER", "CALENDAR", "TASKS", "MUSIC", "EMAIL", "SECURITY", "BROWSER"]

MODULE_ALIASES = {
    "system": "SYSTEM",
    "sys": "SYSTEM",
    "weather": "WEATHER",
    "wheater": "WEATHER",
    "calendar": "CALENDAR",
    "cal": "CALENDAR",
    "tasks": "TASKS",
    "task": "TASKS",
    "todo": "TASKS",
    "music": "MUSIC",
    "song": "MUSIC",
    "email": "EMAIL",
    "mail": "EMAIL",
    "security": "SECURITY",
    "sec": "SECURITY",
    "browser": "BROWSER",
    "web": "BROWSER",
    "browse": "BROWSER",
}

SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "stackoverflow": "https://stackoverflow.com",
    "wikipedia": "https://www.wikipedia.org",
    "reddit": "https://www.reddit.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "instagram": "https://www.instagram.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
    "maps": "https://maps.google.com",
    "chatgpt": "https://chatgpt.com",
    "gpt": "https://chatgpt.com",
    "linkedin": "https://www.linkedin.com",
    "whatsapp": "https://web.whatsapp.com",
    "amazon": "https://www.amazon.com",
    "flipkart": "https://www.flipkart.com",
    "whatsapp": "https://web.whatsapp.com",
}

WIT_LINES = [
    "Running that would require an access level even I don't have, sir.",
    "That request exceeds my current neural allocation. Might I suggest the SYSTEMS module?",
    "I could attempt it, though I cannot guarantee the outcome won't be spectacular.",
    "Command recognized. Capability unresolved. Try one of the eight active modules.",
    "Intriguing. My protocols advise caution, sir.",
]


class JarvisEngine:
    def __init__(self, app):
        self.app = app

    async def process(self, text, voice=False):
        raw = text.strip()
        low = raw.lower()
        self.app.state.log("COMMAND :: " + raw.upper()[:64])
        if voice:
            self.app.state.set_state(THINKING)

        if not raw:
            return self._reply("Awaiting instruction, sir.")

        if any(k in low for k in ("status", "system status", "how is", "system check", "health")):
            return await self._status(voice)

        if any(k in low for k in ("time", "what time", "date", "what day")):
            now = datetime.datetime.now()
            return self._reply(
                f"The local time is {now.strftime('%H:%M:%S')} on {now.strftime('%A, %d %B %Y')}."
            )

        if any(k in low for k in ("weather", "temperature", "forecast")):
            self.app.open_module("WEATHER")
            return self._reply("Opening the weather module. Skies over the tower are clear, 26 degrees.")

        if "shutdown" in low or "power down" in low or "sleep" in low:
            self.app.start_shutdown()
            return self._reply("Shutdown sequence initiated. It has been a pleasure, sir.")

        if "fullscreen" in low:
            self.app.toggle_fullscreen()
            return self._reply("Display reconfigured to fullscreen.")

        if "scan" in low or "threat" in low:
            self.app.start_scan()
            return self._reply("Threat scan initiated. Analyzing all sectors for anomalies.")

        if low.startswith(("open ", "launch ", "go to ")):
            name = low.split(" ", 1)[1]
            for alias, mod in MODULE_ALIASES.items():
                if alias in name:
                    self.app.open_module(mod)
                    return self._reply(f"Opening the {mod} module, sir.")
            for site, url in SITES.items():
                if site == name or site in name:
                    webbrowser.open(url)
                    return self._reply(f"Opening {site.title()} in your browser, sir.")
            return self._reply(random.choice(WIT_LINES))

        for alias, mod in MODULE_ALIASES.items():
            if low == alias or low.startswith(alias + " "):
                self.app.open_module(mod)
                return self._reply(f"Accessing the {mod} module.")

        if low.startswith("add task"):
            task = raw[len("add task"):].strip(" :,-")
            if task:
                self.app.tasks.add(task)
                self.app.state.log("TASK ADDED :: " + task.upper())
                return self._reply(f"Task recorded: {task}. Now {len(self.app.tasks.tasks)} items active.")
            return self._reply("Task input empty, sir. State what you would like to add.")

        if low in ("clear", "clear log", "cls"):
            self.app.state.activity.clear()
            self.app.state.activity_version += 1
            return self._reply("Activity stream cleared.")

        if any(k in low for k in ("music", "play", "pause", "track")):
            self.app.open_module("MUSIC")
            return self._reply("Music module engaged. Select a track to begin.")

        if any(k in low for k in ("hello", "hey", "hi jarvis", "good morning")):
            return self._reply("Good day, sir. All systems are at your disposal.")

        if any(k in low for k in ("who are you", "what are you", "your name")):
            return self._reply(
                "I am JARVIS — Just A Rather Very Intelligent System. Your digital operations core, at your service."
            )

        if any(k in low for k in ("thank", "thanks")):
            return self._reply("Always a pleasure, sir.")

        if self.app.groq.available:
            try:
                now = datetime.datetime.now()
                system = (
                    "You are JARVIS, a concise and witty AI assistant running on the user's PC. "
                    "Keep replies to 2-4 short sentences. "
                    "The user can open modules SYSTEM, WEATHER, CALENDAR, TASKS, MUSIC, EMAIL, SECURITY, "
                    "BROWSER via the module cards or commands like 'open weather'. "
                    f"Local time is {now.strftime('%A %H:%M')}."
                )
                return await self.app.groq.chat(raw, system)
            except Exception as exc:
                self.app.state.log("GROQ ERROR :: " + str(exc)[:80])

        return self._reply(random.choice(WIT_LINES))

    async def _status(self, voice):
        await self.app.telemetry.refresh()
        data = self.app.monitor.read()
        batt = data["battery"]
        batt_txt = f"{int(batt.percent)}% remaining" if batt else "N/A (desktop)"
        return self._reply(
            "All primary systems are operational, sir.\n\n"
            f"CPU utilization is {int(data['cpu'])} percent.\n"
            f"Memory utilization is {int(data['mem'])} percent.\n"
            f"Storage is {int(data['disk'])} percent occupied.\n"
            f"Network throughput {data['net_mbps']:.1f} MB/s.\n"
            f"Power: {batt_txt}.\n\n"
            "No critical issues detected."
        )

    def _reply(self, text):
        return text
