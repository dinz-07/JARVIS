from app.state import AppState
from services.system_monitor import SystemMonitor
from services.groq_engine import GroqEngine
from services.jarvis_engine import JarvisEngine
from services.actions import (
    TasksStore, MusicPlayer, SecurityState, WeatherData, CalendarData, EmailData, BrowserState,
)


class _Telemetry:
    async def refresh(self):
        pass


class HeadlessApp:
    def __init__(self):
        self.page = None
        self.state = AppState()
        self.state.phase = "ready"
        self.monitor = SystemMonitor()
        self.groq = GroqEngine()
        self.telemetry = _Telemetry()
        self.tasks = TasksStore()
        self.music = MusicPlayer()
        self.security = SecurityState()
        self.weather = WeatherData()
        self.calendar = CalendarData()
        self.email = EmailData()
        self.browser = BrowserState()
        self.engine = JarvisEngine(self)
        self.last_action = None
        self.last_module = None

    def open_module(self, name):
        self.last_action = "module"
        self.last_module = name

    def start_scan(self):
        self.last_action = "scan"

    def start_shutdown(self):
        self.last_action = "shutdown"

    def toggle_fullscreen(self):
        self.last_action = "fullscreen"

    def voice_wave(self, active):
        pass
