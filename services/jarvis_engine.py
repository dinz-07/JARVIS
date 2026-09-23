import datetime
import random
import re
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


def _site_url(alias, query):
    q = re.sub(r"[^a-zA-Z0-9._\-\s]", "", query).strip()
    if alias in ("instagram",):
        q = q.replace(" ", "")
        if q:
            return f"https://www.instagram.com/{q}/"
    if alias in ("twitter", "x"):
        q = q.replace(" ", "")
        if q:
            return f"https://x.com/{q}"
    if alias == "github":
        q = q.replace(" ", "")
        if q:
            return f"https://github.com/{q}"
    if alias == "youtube":
        if q:
            return f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}"
    if alias in ("linkedin",):
        if q:
            return f"https://www.google.com/search?q=site:linkedin.com+{q.replace(' ', '+')}"
        return "https://www.linkedin.com/search/results/?keywords="
    if alias == "maps":
        if q:
            return f"https://www.google.com/maps/search/{q.replace(' ', '+')}"
    if alias == "google":
        if q:
            return f"https://www.google.com/search?q={q.replace(' ', '+')}"
    return None


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

        if low.startswith(("search for ", "search ")):
            q = low
            for prefix in ("search for ", "search "):
                if q.startswith(prefix):
                    q = q[len(prefix):]
                    break
            q = re.sub(r"^the web (for |about )?", "", q).strip(" ,:.")
            if not q:
                return self._reply("Search query empty, sir.")
            if self.app.groq.available:
                try:
                    self.app.state.log("WEB SEARCH :: " + q.upper()[:48])
                    return await self.app.groq.chat(
                        f"Search the web for: {q}. Summarize the key findings, sir.",
                        self._system_prompt(),
                        force_search=True,
                    )
                except Exception as exc:
                    self.app.state.log("SEARCH ERROR :: " + str(exc)[:80])
            webbrowser.open(f"https://www.google.com/search?q={q.replace(' ', '+')}")
            return self._reply(f"Searching the web for {q}, sir.")

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
            name = re.sub(r"\s+on\s+linkedin$", " linkedin", name)
            m = re.match(r"^([a-zA-Z0-9._\-@\s]+)\s+(instagram|x|twitter|github|linkedin)(?:\s+(?:id|profile|page))?$", name)
            if m:
                alias = m.group(2)
                q = m.group(1).strip(" @:-")
                url = _site_url(alias, q) if q else SITES.get(alias)
                if url:
                    webbrowser.open(url)
                    return self._reply(f"Opening {alias.title()} for {q}, sir.")
            for alias in SITES:
                if name == alias or name.startswith(alias + " ") or name.startswith(alias + "@"):
                    q = name[len(alias):].strip(" @:-")
                    q = re.sub(r"^(id|profile|page)\s+", "", q)
                    url = _site_url(alias, q) if q else SITES[alias]
                    if url:
                        webbrowser.open(url)
                        if q:
                            return self._reply(f"Opening {alias.title()} for {q}, sir.")
                        return self._reply(f"Opening {alias.title()} in your browser, sir.")
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
                return await self.app.groq.chat(raw, self._system_prompt())
            except Exception as exc:
                self.app.state.log("GROQ ERROR :: " + str(exc)[:80])

        return self._reply(random.choice(WIT_LINES))

    def _system_prompt(self):
        now = datetime.datetime.now()
        return (
            "You are JARVIS, a concise and witty AI assistant running on the user's PC. "
            "Keep replies to 2-4 short sentences. "
            "The user can open modules SYSTEM, WEATHER, CALENDAR, TASKS, MUSIC, EMAIL, SECURITY, "
            "BROWSER via the module cards or commands like 'open weather'. "
            "Commands starting with 'search' trigger a live web search whose results are given to you."
            f"Local time is {now.strftime('%A %H:%M')}."
        )

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
