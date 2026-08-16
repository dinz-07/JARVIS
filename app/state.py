import math
import time
from collections import deque

IDLE = "idle"
LISTENING = "listening"
THINKING = "thinking"
SPEAKING = "speaking"
EXECUTING = "executing"

STATE_LABEL = {
    IDLE: "STANDBY",
    LISTENING: "LISTENING...",
    THINKING: "ANALYZING...",
    SPEAKING: "SPEAKING...",
    EXECUTING: "EXECUTING...",
}


def _linear(k):
    return k


def _out_cubic(k):
    return 1 - (1 - k) ** 3


def _in_out_cubic(k):
    return 4 * k * k * k if k < 0.5 else 1 - (-2 * k + 2) ** 3 / 2


def _out_back(k):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (k - 1) ** 3 + c1 * (k - 1) ** 2


EASE = {
    "linear": _linear,
    "out_cubic": _out_cubic,
    "in_out_cubic": _in_out_cubic,
    "out_back": _out_back,
}


class Tween:
    def __init__(self, obj, attr, end, duration=0.4, curve="out_cubic", start=None, on_done=None):
        self.obj = obj
        self.attr = attr
        self.start = start if start is not None else getattr(obj, attr, 0.0)
        self.end = end
        self.duration = duration
        self.curve = curve
        self.on_done = on_done
        self.t = 0.0

    def tick(self, dt):
        self.t += dt
        k = min(1.0, self.t / self.duration)
        v = EASE.get(self.curve, _linear)(k)
        try:
            setattr(self.obj, self.attr, self.start + (self.end - self.start) * v)
        except Exception:
            pass
        return k >= 1.0


class AppState:
    def __init__(self):
        self.t0 = time.time()
        self.ai_state = IDLE
        self.settings = {
            "voice": True,
            "sfx": True,
            "particles": 1.0,
            "hud": 1.0,
            "animations": True,
            "reduced_motion": False,
        }
        self.activity = deque(maxlen=9)
        self.activity_version = 0
        self.tweens = []
        self.phase = "boot"
        self.scene = "core"
        self.module = None
        self.progress = 0.0
        self.exec_done = None
        self.exec_label = "TASK"
        self.shutdown = False
        self.fullscreen = False
        self.voice_active = False

    @property
    def now(self):
        return time.time() - self.t0

    def log(self, text):
        self.activity.appendleft((time.strftime("%H:%M:%S"), text))
        self.activity_version += 1

    def set_state(self, s):
        if s != self.ai_state:
            self.ai_state = s
            self.log("STATE :: " + STATE_LABEL[s])

    def tween(self, obj, attr, end, **kw):
        self.tweens.append(Tween(obj, attr, end, **kw))

    def tick(self, dt):
        remaining = []
        for t in self.tweens:
            finished = t.tick(dt)
            if finished and t.on_done:
                try:
                    t.on_done()
                except Exception:
                    pass
            if not finished:
                remaining.append(t)
        self.tweens = remaining
