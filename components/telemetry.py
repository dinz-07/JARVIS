import asyncio

from app.theme import rgba, PANEL, CYAN


class Telemetry:
    def __init__(self, app):
        self.app = app
        self.timer = 0.0

    async def refresh(self):
        self.app.monitor.read()
        data = self.app.monitor.read()
        self.app.hud.update(data, self.app.core.radius, self.app.cx, self.app.cy)
        if self.app.modules.system_rows:
            self.app.modules.update_system(data)

    async def loop(self):
        while True:
            await asyncio.sleep(1.4)
            try:
                data = self.app.monitor.read()
                self.app.hud.update(data, self.app.core.radius, self.app.cx, self.app.cy)
                if self.app.modules.system_rows:
                    self.app.modules.update_system(data)
            except Exception:
                pass
