import datetime
import random


class TasksStore:
    def __init__(self):
        self.tasks = [
            {"text": "Review neural core logs", "done": False},
            {"text": "Deploy morning brief", "done": False},
            {"text": "Calibrate voice channel", "done": True},
        ]

    def add(self, text):
        self.tasks.insert(0, {"text": text, "done": False})

    def toggle(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index]["done"] = not self.tasks[index]["done"]


class MusicPlayer:
    def __init__(self):
        self.tracks = [
            ("Ion Storm", "Neural Drift"),
            ("Zero Point", "Cyber Tide"),
            ("Glass Horizon", "Pulse Theory"),
            ("Low Orbit", "System Echo"),
        ]
        self.index = 0
        self.playing = False
        self.pos = 0.0

    @property
    def track(self):
        return self.tracks[self.index]

    def toggle(self):
        self.playing = not self.playing
        return self.playing

    def next(self):
        self.index = (self.index + 1) % len(self.tracks)
        self.pos = 0.0

    def prev(self):
        self.index = (self.index - 1) % len(self.tracks)
        self.pos = 0.0

    def tick(self, dt):
        if self.playing:
            self.pos += dt / 3.2
            if self.pos >= 1.0:
                self.next()
                self.pos = 0.0


class SecurityState:
    def __init__(self):
        self.threat = "LOW"
        self.scans = 12
        self.breaches = 0

    def scan(self):
        self.scans += 1
        self.threat = "LOW" if random.random() < 0.92 else "MEDIUM"


class WeatherData:
    @staticmethod
    def get():
        return {
            "location": "STARK TOWER",
            "temp": 26,
            "humidity": 41,
            "wind": 12,
            "condition": "CLEAR SKIES",
            "forecast": [
                ("NOW", 26, "CLEAR"),
                ("+6H", 24, "PARTLY"),
                ("+12H", 22, "CLEAR"),
                ("+24H", 25, "CLEAR"),
            ],
        }


class CalendarData:
    @staticmethod
    def get():
        return [
            ("09:00", "CORE INTEGRITY REVIEW"),
            ("12:30", "SECTOR BRIEFING"),
            ("16:00", "SYSTEM UPGRADE WINDOW"),
        ]


class EmailData:
    @staticmethod
    def get():
        return [
            ("N.STARK", "Arc Reactor calibration report"),
            ("P.POTTS", "Q3 deployment schedule"),
            ("SYS.ALERTS", "Firewall policy update applied"),
        ]


class BrowserState:
    def __init__(self):
        self.url = "jarvis://core"
        self.page = {
            "jarvis://core": ("JARVIS INTERNAL NETWORK", [
                "Neural core: online",
                "Uplink: secure (AES-256)",
                "Sector access: level 7",
            ]),
        }
        self.visited = []

    def go(self, url):
        self.url = url.strip() or "jarvis://core"
        if url not in self.visited:
            self.visited.append(url)
        if url not in self.page:
            self.page[url] = (
                "PAGE NOT FOUND — " + url.upper(),
                ["No data retrieved from this address.", "Request logged in activity stream."],
            )
        return self.page[url]
