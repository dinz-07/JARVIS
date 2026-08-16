import asyncio
import os
import time

import flet as ft

from app.state import EXECUTING, IDLE, AppState
from app.theme import BG, BG_DEEP, CYAN, ICE, WHITE, DIM, GREEN, rgba, label, FONT, FONT_HEAD

from components.ai_core import AICore
from components.particles import Background
from components.hud import Hud
from components.module_cards import ModuleCards
from components.activity_stream import ActivityStream
from components.hologram import Hologram
from components.command_bar import CommandBar
from components.modules import ModulesPanel
from components.telemetry import Telemetry

from services.system_monitor import SystemMonitor
from services.jarvis_engine import JarvisEngine
from services.groq_engine import GroqEngine
from services.voice import VoiceManager
from services.actions import (
    TasksStore, MusicPlayer, SecurityState, WeatherData, CalendarData, EmailData, BrowserState,
)

BOOT_LINES = [
    "NEURAL CORE ........ ONLINE",
    "VOICE SYSTEM ........ ONLINE",
    "VISION SYSTEM ....... ONLINE",
    "SYSTEM CONTROL ...... ONLINE",
    "SECURITY ............ VERIFIED",
]

SHUT_LINES = [
    "VOICE SYSTEM ........ OFFLINE",
    "NEURAL CORE .......... STANDBY",
    "SYSTEM CONTROL ....... OFFLINE",
    "SECURITY ............. LOCKED",
]

NAV = ["CORE", "SYSTEM", "TASKS", "SECURITY", "COMMAND", "SETTINGS"]


def txt(text, size=10, color=DIM, spacing=2.0, weight=ft.FontWeight.W_400):
    return ft.Text(
        text,
        size=size,
        style=ft.TextStyle(color=color, font_family=FONT, letter_spacing=spacing, weight=weight),
    )


class JarvisApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.state = AppState()
        self.monitor = SystemMonitor()
        self.groq = GroqEngine()
        self.engine = JarvisEngine(self)
        self.voice = VoiceManager(self)
        self.tasks = TasksStore()
        self.music = MusicPlayer()
        self.security = SecurityState()
        self.weather_data = WeatherData.get()
        self.calendar_data = CalendarData.get()
        self.email_data = EmailData.get()
        self.browser = BrowserState()
        self.w = 1600
        self.h = 900
        self.cx = 800
        self.cy = 396
        self.R = 110
        self.field_focused = False
        self.boot_stage = -1
        self.boot_t = 0.0
        self.shut_stage = -1
        self.shut_t = 0.0
        self.mouse_x = 0.5
        self.mouse_y = 0.45
        self.mouse_seen = False
        self.last_mouse = 0.0
        self.frame = 0

        self.bg = Background(self.state)
        self.core = AICore(self.state)
        self.hud = Hud(self.state)
        self.cards = ModuleCards(self.state, self.open_module)
        self.stream = ActivityStream(self.state)
        self.hologram = Hologram(self.state)
        self.command = CommandBar(self)
        self.modules = ModulesPanel(self)
        self.telemetry = Telemetry(self)
        self.settings_panel = self._build_settings()
        self.nav = self._build_nav()
        self.corner_labels = self._build_corners()
        self.interface_row = self._build_interface_row()
        self.dim = ft.Container(
            width=1600, height=900, bgcolor=rgba(BG_DEEP, 0.62), opacity=0.0, visible=False,
        )
        self.boot = self._build_boot()
        self.shutdown = self._build_shutdown()
        self.root = ft.Stack(expand=True)

    def _nav_pill(self, name):
        txt_c = txt(name, 10, rgba(DIM, 0.9), 2.6, ft.FontWeight.W_400)
        c = ft.Container(
            content=txt_c,
            padding=ft.Padding.symmetric(horizontal=16, vertical=7),
            border_radius=3,
        )

        def enter(e):
            txt_c.style = ft.TextStyle(color=CYAN, font_family=FONT, letter_spacing=2.6)
            c.bgcolor = rgba(CYAN, 0.08)
            c.border = ft.Border.all(1, rgba(CYAN, 0.3))

        def exit(e):
            txt_c.style = ft.TextStyle(color=rgba(DIM, 0.9), font_family=FONT, letter_spacing=2.6)
            c.bgcolor = "#00000000"
            c.border = ft.Border.all(1, rgba(CYAN, 0.0))

        gd = ft.GestureDetector(
            content=c,
            on_enter=enter,
            on_exit=exit,
            on_tap=lambda e, n=name: self._nav_click(n),
        )
        return gd

    def _build_nav(self):
        logo = ft.Row(
            [
                ft.Text(
                    "JARVIS",
                    size=17,
                    style=ft.TextStyle(color=CYAN, font_family=FONT_HEAD, letter_spacing=5, weight=ft.FontWeight.W_700),
                ),
                ft.Container(
                    content=ft.Text(
                        "v2.0",
                        size=8,
                        style=ft.TextStyle(color=rgba(DIM, 0.9), font_family=FONT_HEAD, letter_spacing=1.5),
                    ),
                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                    border_radius=3,
                    border=ft.Border.all(1, rgba(CYAN, 0.35)),
                    bgcolor=rgba(CYAN, 0.06),
                ),
            ],
            spacing=9,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.online_dot = ft.Container(
            width=8,
            height=8,
            border_radius=4,
            bgcolor=GREEN,
            shadow=[ft.BoxShadow(blur_radius=10, color=rgba(GREEN, 0.9))],
        )
        self.sfx_btn = ft.IconButton(
            icon=getattr(ft.Icons, "VOLUME_UP", ft.Icons.MUSIC_NOTE),
            icon_color=rgba(ICE, 0.85),
            icon_size=16,
            tooltip="Sound on/off",
            on_click=lambda e: self._toggle_sfx(),
        )
        online = ft.Row(
            [
                self.sfx_btn,
                self.online_dot,
                ft.Text(
                    "ONLINE",
                    size=10,
                    style=ft.TextStyle(color=GREEN, font_family=FONT_HEAD, letter_spacing=3, weight=ft.FontWeight.W_700),
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        pills = ft.Row([self._nav_pill(n) for n in NAV], spacing=4)
        self.nav = ft.Container(
            content=ft.Stack(
                [
                    ft.Container(content=logo, left=40, top=9),
                    ft.Container(content=pills, left=220, top=9),
                    ft.Container(content=online, right=40, top=10),
                ],
                height=44,
            ),
            top=10,
        )
        return self.nav

    def _nav_click(self, name):
        self.state.log("NAVIGATION :: " + name)
        if name == "CORE":
            self.close_module()
        elif name == "COMMAND":
            self.command.field.focus()
        elif name == "SETTINGS":
            self.toggle_settings()
        else:
            self.open_module(name)

    def _build_corners(self):
        wm = txt("JARVIS // ARTIFICIAL INTELLIGENCE SYSTEM", 8.5, rgba(CYAN, 0.5), 2.6)
        ver = txt("CORE v2.0 // NEXT-GENERATION AI AGENT", 8.5, rgba(DIM, 0.55), 2.2)
        return {
            "wm": ft.Container(content=wm, left=26, bottom=14),
            "ver": ft.Container(content=ver, left=26, top=14),
        }

    def _build_interface_row(self):
        def chip(icon, text):
            ic = getattr(ft.Icons, icon, None)
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ic, size=13, color=CYAN),
                            width=24,
                            height=24,
                            border_radius=12,
                            bgcolor=rgba(CYAN, 0.08),
                            border=ft.Border.all(1, rgba(CYAN, 0.3)),
                            alignment=ft.Alignment.CENTER,
                        ),
                        txt(text, 9.5, rgba(ICE, 0.9), 2.0),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                border_radius=20,
                bgcolor=rgba("#020c1b", 0.65),
                border=ft.Border.all(1, rgba(CYAN, 0.25)),
                shadow=[ft.BoxShadow(blur_radius=16, color=rgba(CYAN, 0.12))],
            )

        self.interface_row = ft.Row(
            [
                chip("MIC", "VOICE AGENT READY"),
                chip("BOLT", "SYSTEM POWERED"),
                chip("SHIELD", "SECURE INTERFACE"),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        return self.interface_row

    def _build_boot(self):
        texts = [txt("CHAPTER 01 — INITIALIZATION", 9.5, rgba(CYAN, 0.6), 6.0)]
        texts += [txt(l, 11, rgba(ICE, 0.85), 2.5) for l in BOOT_LINES]
        self.boot_big = ft.Text(
            "JARVIS", size=72,
            style=ft.TextStyle(color=CYAN, font_family=FONT_HEAD, letter_spacing=18, weight=ft.FontWeight.W_900),
        )
        self.boot_bar = ft.Container(
            width=240, height=2,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1.0, 0.0),
                end=ft.Alignment(1.0, 0.0),
                colors=["#0000ffff", rgba(CYAN, 1.0), "#0000ffff"],
            ),
            shadow=[ft.BoxShadow(blur_radius=14, color=rgba(CYAN, 0.7))],
        )
        self.boot_sub = txt("ARTIFICIAL INTELLIGENCE SYSTEM", 11, rgba(CYAN, 0.75), 6.0)
        self.boot_ready = txt("SYSTEM READY", 12, rgba(GREEN, 0.95), 5.0)
        col = ft.Column(
            texts + [self.boot_big, self.boot_bar, self.boot_sub, self.boot_ready],
            spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        return ft.Container(
            content=col,
            width=1600, height=900,
            bgcolor=BG,
            alignment=ft.Alignment.TOP_CENTER,
            padding=ft.Padding.only(top=120),
            opacity=1.0,
        )

    def _build_shutdown(self):
        texts = [txt("JARVIS SHUTDOWN INITIATED", 13, ICE, 4.0)]
        texts += [txt(l, 11, rgba(ICE, 0.8), 2.5) for l in SHUT_LINES]
        self.shut_end = txt("GOODBYE.", 30, rgba(CYAN, 0.95), 10.0)
        col = ft.Column(texts + [self.shut_end], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        return ft.Container(
            content=col,
            width=1600, height=900,
            bgcolor=BG,
            alignment=ft.Alignment.CENTER,
            opacity=0.0,
            visible=False,
        )

    def _settings_row(self, title, control):
        return ft.Container(
            content=ft.Row(
                [label(title, 10.5, WHITE, 2.5), ft.Container(expand=True), control],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(vertical=9),
            border=ft.Border(bottom=ft.BorderSide(1, rgba(CYAN, 0.08))),
        )

    def _toggle_sfx(self):
        st = self.state.settings
        st.update(sfx=not st["sfx"])
        self.sfx_btn.icon = getattr(ft.Icons, "VOLUME_UP", ft.Icons.MUSIC_NOTE) if st["sfx"] else getattr(ft.Icons, "VOLUME_OFF", ft.Icons.MUSIC_NOTE)
        self.sfx_btn.icon_color = rgba(CYAN, 1.0) if st["sfx"] else rgba(DIM, 0.6)
        self.page.update()

    def _build_settings(self):
        st = self.state.settings
        sw_voice = ft.Switch(value=st["voice"], active_color=CYAN, on_change=self._set_voice)
        sw_sfx = ft.Switch(value=st["sfx"], active_color=CYAN, on_change=lambda e: st.update(sfx=e.control.value))
        sw_anim = ft.Switch(value=st["animations"], active_color=CYAN, on_change=lambda e: st.update(animations=e.control.value))
        sw_motion = ft.Switch(value=st["reduced_motion"], active_color=CYAN, on_change=self._set_motion)
        sl_particles = ft.Slider(min=0, max=100, value=50, width=170, label="DENSITY",
                                 on_change=self._set_particles, active_color=CYAN, inactive_color=rgba(DIM, 0.3))
        sl_hud = ft.Slider(min=20, max=100, value=100, width=170, label="INTENSITY",
                           on_change=self._set_hud, active_color=CYAN, inactive_color=rgba(DIM, 0.3))
        title = txt("SETTINGS", 18, WHITE, 4.0, ft.FontWeight.W_200)
        close_icon = getattr(ft.Icons, "CLOSE", None)
        close_btn = ft.IconButton(icon=close_icon, icon_color=ICE, on_click=lambda e: self.toggle_settings())
        col = ft.Column(
            [
                ft.Row([title, ft.Container(expand=True), close_btn]),
                self._settings_row("VOICE", sw_voice),
                self._settings_row("SOUND EFFECTS", sw_sfx),
                self._settings_row("PARTICLE DENSITY", sl_particles),
                self._settings_row("HUD INTENSITY", sl_hud),
                self._settings_row("ANIMATIONS", sw_anim),
                self._settings_row("REDUCED MOTION", sw_motion),
                ft.Container(
                    content=txt(
                        "ENTER // SUBMIT    ESC // BACK    CTRL+M // VOICE    CTRL+Q // SHUTDOWN    F11 // FULLSCREEN    1-8 // MODULES",
                        8.5, rgba(DIM, 0.7), 1.4,
                    ),
                    padding=ft.Padding.only(top=12),
                ),
            ],
            spacing=2,
        )
        return ft.Container(
            content=col,
            width=480,
            border_radius=8,
            bgcolor=rgba("#020c1b", 0.97),
            border=ft.Border.all(1, rgba(CYAN, 0.35)),
            shadow=[ft.BoxShadow(blur_radius=60, spread_radius=3, color=rgba(CYAN, 0.22))],
            padding=ft.Padding.all(26),
            opacity=0.0,
            visible=False,
            scale=0.94,
        )

    def _set_voice(self, e):
        self.state.settings["voice"] = e.control.value
        self.state.log("VOICE " + ("ENABLED" if e.control.value else "DISABLED"))

    def _set_motion(self, e):
        self.state.settings["reduced_motion"] = e.control.value
        self.state.log("REDUCED MOTION " + ("ON" if e.control.value else "OFF"))

    def _set_particles(self, e):
        self.state.settings["particles"] = e.control.value / 50.0
        self.bg.rebuild()
        self.state.log("PARTICLE DENSITY ADJUSTED")

    def _set_hud(self, e):
        self.state.settings["hud"] = e.control.value / 100.0
        for c in self.hud.chips.values():
            c["body"].opacity = 0.35 + 0.65 * self.state.settings["hud"]

    def run(self):
        page = self.page
        page.title = "JARVIS — AI COMMAND EXPERIENCE"
        page.bgcolor = BG
        page.padding = 0
        page.spacing = 0
        try:
            w = int(os.environ.get("JARVIS_W", "1600"))
            h = int(os.environ.get("JARVIS_H", "900"))
            page.window.width = w
            page.window.height = h
        except Exception:
            pass
        try:
            page.run_task(page.window.center)
        except Exception:
            pass
        try:
            page.window.min_width = 1180
            page.window.min_height = 700
        except Exception:
            pass
        page.on_resize = self._on_resize
        page.on_keyboard_event = self._on_key
        try:
            page.on_mouse_event = self._on_mouse
        except Exception:
            pass
        self.command.field.on_focus = lambda e: self._set_focus(True)
        self.command.field.on_blur = lambda e: self._set_focus(False)
        self.build()
        page.add(self.root)
        page.run_task(self._loop)

    def _set_focus(self, focused):
        self.field_focused = focused

    def _on_resize(self, e):
        if getattr(self, "nav", None) is None or getattr(self, "interface_row", None) is None:
            return
        self.layout()
        self.page.update()

    def _on_mouse(self, e):
        w = max(1, self.page.width)
        h = max(1, self.page.height)
        x = getattr(e, "x", None)
        y = getattr(e, "y", None)
        if x is None:
            x = getattr(e, "local_x", w / 2)
        if y is None:
            y = getattr(e, "local_y", h / 2)
        self.mouse_x = max(0.0, min(1.0, x / w))
        self.mouse_y = max(0.0, min(1.0, y / h))
        self.mouse_seen = True
        self.last_mouse = time.time()

    def _on_key(self, e):
        key = (e.key or "").upper()
        ctrl = bool(getattr(e, "ctrl", False))
        if ctrl and key == "M":
            self.voice_toggle()
            return
        if ctrl and key in ("Q", "C"):
            self.start_shutdown()
            return
        if key in ("F11", "F11_KEY") or (ctrl and key == "F"):
            self.toggle_fullscreen()
            return
        if key in ("ESCAPE", "ESC"):
            if self.state.module:
                self.close_module()
            elif self.settings_panel.visible:
                self.toggle_settings()
            else:
                self.command.field.value = ""
                self.page.update()
            return
        if self.field_focused:
            return
        names = list(self.cards.cards.keys())
        if key.isdigit() and 1 <= int(key) <= 8:
            self.open_module(names[int(key) - 1])
        elif key == "S":
            self.toggle_settings()

    def layout(self):
        w = self.page.width or 1600
        h = self.page.height or 900
        self.w = w
        self.h = h
        self.R = max(84, min(175, min(w, h) * 0.115))
        self.cx = w / 2
        self.cy = h * 0.44
        self.bg.resize(int(w), int(h))
        self.core.resize(self.R)
        cs = self.core.cs
        self.core.holder.left = int(self.cx - cs / 2)
        self.core.holder.top = int(self.cy - cs / 2)
        self.hud.layout(w, h)
        self.cards.layout(w, h)
        self.stream.layout(w, h)
        self.hologram.layout(w, h)
        self.command.layout(w, h)
        self.modules.layout(w, h)
        self.nav.width = int(w)
        self.nav.left = 0
        cs = self.core.cs
        self.interface_row.top = int(self.cy + cs / 2 + 18)
        self.interface_row.left = int(w / 2 - 300)
        self.settings_panel.left = int(w / 2 - 240)
        self.settings_panel.top = int(h * 0.16)
        self.dim.width = int(w)
        self.dim.height = int(h)
        self.boot.width = int(w)
        self.boot.height = int(h)
        self.boot.padding = ft.Padding.only(top=int(h * 0.15))
        self.shutdown.width = int(w)
        self.shutdown.height = int(h)

    def _cursor(self):
        if not self.mouse_seen:
            return (0, 0, 0.0)
        w = self.w or 1600
        h = self.h or 900
        strength = max(0.0, 1.0 - (time.time() - self.last_mouse) / 1.5)
        return (self.mouse_x * w, self.mouse_y * h, strength)

    def tick(self, dt):
        st = self.state
        st.tick(dt)
        self.frame += 1
        if os.environ.get("JARVIS_DEBUG") and self.frame % 60 == 0:
            print(
                f"[DBG] t={self.frame / 30:.1f}s phase={st.phase} scene={st.scene} "
                f"module={st.module} ai_state={st.ai_state} boot_stage={self.boot_stage} "
                f"progress={st.progress:.2f}"
            )
        if st.phase == "boot":
            self._boot_tick(dt)
            self.bg.tick(dt, False, self._cursor())
            self.core.tick(dt)
            self.page.update()
            return
        if st.shutdown:
            self._shut_tick(dt)
            self.bg.tick(dt, True, self._cursor())
            self.core.tick(dt)
            self.page.update()
            return
        if st.ai_state == EXECUTING:
            st.progress = min(1.0, st.progress + dt / 3.2)
            if st.progress >= 1.0:
                st.set_state(IDLE)
                st.progress = 0.0
                if st.exec_done:
                    fn = st.exec_done
                    st.exec_done = None
                    fn()
        self.bg.tick(dt, st.settings["reduced_motion"], self._cursor())
        self.core.parallax_x += ((self.mouse_x - 0.5) * 26 - self.core.parallax_x) * min(1.0, dt * 6)
        self.core.parallax_y += ((self.mouse_y - 0.45) * 20 - self.core.parallax_y) * min(1.0, dt * 6)
        cs = self.core.cs
        self.core.holder.left = int(self.cx - cs / 2 + self.core.parallax_x * 0.5)
        self.core.holder.top = int(self.cy - cs / 2 + self.core.parallax_y * 0.5)
        self.core.tick(dt)
        data = self.monitor.read()
        self.hud.update(data, self.R, self.cx, self.cy)
        self.hologram.tick(dt)
        self.modules.tick(dt)
        self.stream.tick()
        if st.tweens:
            self.page.update()
        else:
            self.bg.update()
            self.core.update()
            self.hud.connector.update()
            for c in self.hud.chips.values():
                c["value"].update()
                c["unit"].update()
            if self.hologram.root.visible:
                self.hologram.root.update()

    def _boot_tick(self, dt):
        self.boot_t += dt
        if self.boot_stage == -1 and self.boot_t > 0.1:
            self.boot_stage = 0
            self.state.tween(self.boot.content.controls[0], "opacity", 1.0, duration=0.4)
        if self.boot_stage == 0 and self.boot_t > 1.0:
            self.boot_stage = 1
            for i in range(1, 6):
                self.state.tween(self.boot.content.controls[i], "opacity", 1.0, duration=0.3)
        if self.boot_stage == 1 and self.boot_t > 3.1:
            self.boot_stage = 2
            self.state.tween(self.boot_big, "opacity", 1.0, duration=0.8, curve="in_out_cubic")
        if self.boot_stage == 2 and self.boot_t > 3.9:
            self.boot_stage = 3
            self.state.tween(self.boot_sub, "opacity", 1.0, duration=0.6)
        if self.boot_stage == 3 and self.boot_t > 5.6:
            self.boot_stage = 4
            self.state.tween(self.boot_ready, "opacity", 1.0, duration=0.5)
            self.state.log("SYSTEM READY")
        if self.boot_stage == 4 and self.boot_t > 6.8:
            self.boot_stage = 5
            self.state.tween(self.boot, "opacity", 0.0, duration=1.6)
        if self.boot_stage == 5 and self.boot_t > 8.6:
            self.state.phase = "ready"
            self.boot.visible = False
            self.state.log("JARVIS ONLINE")

    def _shut_tick(self, dt):
        self.shut_t += dt
        cols = self.shutdown.content.controls
        stage = self.shut_stage
        if stage == 0 and self.shut_t > 0.15:
            self.shut_stage = 1
            self.state.tween(self.shutdown, "opacity", 0.92, duration=0.7)
            self.state.tween(cols[0], "opacity", 1.0, duration=0.4)
        if stage == 1 and self.shut_t > 1.6:
            self.shut_stage = 2
            for i in range(1, 5):
                self.state.tween(cols[i], "opacity", 1.0, duration=0.3)
        if stage == 2 and self.shut_t > 4.4:
            self.shut_stage = 3
            self.state.tween(self.shut_end, "opacity", 1.0, duration=0.7)
        if stage == 3 and self.shut_t > 5.6:
            self.shut_stage = 4
            self.state.tween(self.shutdown, "opacity", 1.0, duration=1.2)
        if stage == 4 and self.shut_t > 7.0:
            self.state.shutdown = False
            try:
                self.page.window.close()
            except Exception:
                try:
                    self.page.window_close()
                except Exception:
                    pass
            try:
                self.page.window.destroy()
            except Exception:
                pass

    async def _loop(self):
        last = time.time()
        while True:
            now = time.time()
            dt = min(0.05, now - last)
            last = now
            fps = 24 if self.state.settings["reduced_motion"] else 30
            try:
                self.tick(dt)
            except Exception as exc:
                print("TICK ERROR:", exc)
            await asyncio.sleep(max(0.001, 1.0 / fps - (time.time() - now)))

    def run_command(self, text):
        self.page.run_task(self._run_command, text)

    async def _run_command(self, text):
        response = await self.engine.process(text)
        self.hologram.show("> " + text.upper(), response)
        self.page.update()

    def voice_wave(self, active):
        ring = self.core.ghost_ring
        ring.opacity = 0.45 if active else 1.0
        ring.update()

    def voice_toggle(self):
        if not self.state.settings["voice"]:
            self.hologram.show("> VOICE", "The voice channel is disabled in settings, sir.")
            return
        if not self.state.voice_active:
            self.page.run_task(self.voice.cycle)

    def open_module(self, name):
        if self.state.shutdown or self.state.phase != "ready":
            return
        if self.state.module == name:
            return
        self.state.module = name
        self.state.scene = "module"
        self.modules.open(name)
        self._focus_module()

    def close_module(self):
        if self.state.module is None:
            return
        self.modules.close()
        self.state.module = None
        self.state.scene = "core"
        self._focus_core()

    def _focus_module(self):
        self.state.tween(self.core.holder, "opacity", 0.15, duration=0.4)
        self.state.tween(self.core.holder, "scale", 0.62, duration=0.5, curve="out_cubic")
        self.state.tween(self.cards.container, "opacity", 0.08, duration=0.4)
        self.state.tween(self.cards.container, "scale", 0.94, duration=0.4)
        self.state.tween(self.hud.connector_wrap, "opacity", 0.15, duration=0.4)
        self.state.tween(self.command.root, "opacity", 0.35, duration=0.4)
        self.state.tween(self.stream.root, "opacity", 0.3, duration=0.4)
        self.dim.visible = True
        self.state.tween(self.dim, "opacity", 1.0, duration=0.4)

    def _focus_core(self):
        self.state.tween(self.core.holder, "opacity", 1.0, duration=0.45)
        self.state.tween(self.core.holder, "scale", 1.0, duration=0.55, curve="out_back", start=0.62)
        self.state.tween(self.cards.container, "opacity", 1.0, duration=0.4)
        self.state.tween(self.cards.container, "scale", 1.0, duration=0.4)
        self.state.tween(self.hud.connector_wrap, "opacity", 1.0, duration=0.4)
        self.state.tween(self.command.root, "opacity", 1.0, duration=0.4)
        self.state.tween(self.stream.root, "opacity", 1.0, duration=0.4)
        self.state.tween(self.dim, "opacity", 0.0, duration=0.5, curve="in_out_cubic", on_done=self._dim_hidden)

    def _dim_hidden(self):
        self.dim.visible = False

    def toggle_settings(self):
        if self.state.module:
            self.close_module()
        visible = not self.settings_panel.visible
        self.settings_panel.visible = True
        if visible:
            self.state.tween(self.settings_panel, "opacity", 1.0, duration=0.35)
            self.state.tween(self.settings_panel, "scale", 1.0, duration=0.45, curve="out_back", start=0.94)
            self.dim.visible = True
            self.state.tween(self.dim, "opacity", 1.0, duration=0.4)
            self.state.log("SETTINGS OPENED")
        else:
            self.state.tween(self.settings_panel, "opacity", 0.0, duration=0.3)
            self.state.tween(self.settings_panel, "scale", 0.94, duration=0.35, on_done=self._settings_hidden)
            self.state.tween(self.dim, "opacity", 0.0, duration=0.4, curve="in_out_cubic", on_done=self._dim_hidden)

    def _settings_hidden(self):
        self.settings_panel.visible = False

    def start_scan(self):
        if self.state.shutdown or self.state.ai_state == EXECUTING:
            return
        self.state.progress = 0.0
        self.state.set_state(EXECUTING)
        self.state.log("THREAT SCAN STARTED")

        def done():
            self.security.scan()
            threat = self.security.threat
            self.modules.set_scan_status(
                f"SCAN {self.security.scans} COMPLETE — THREAT LEVEL {threat}",
                GREEN if threat == "LOW" else "#ffc44d",
            )
            self.hologram.show("> THREAT SCAN", f"Analysis complete. Threat level: {threat}. All sectors nominal, sir.")
            self.state.log("THREAT SCAN COMPLETE")

        self.state.exec_done = done

    def toggle_fullscreen(self):
        try:
            self.page.window.fullscreen = not self.page.window.fullscreen
            self.state.log("FULLSCREEN TOGGLED")
        except Exception:
            pass

    def start_shutdown(self):
        if self.state.shutdown or self.state.phase != "ready":
            return
        self.state.shutdown = True
        self.state.shut_t = 0.0
        self.shut_stage = 0
        self.shutdown.visible = True
        self.state.set_state(IDLE)
        self.state.log("SHUTDOWN INITIATED")
        self.page.update()

    def build(self):
        root = self.root
        root.controls.append(self.bg.stack)
        root.controls.append(self.hud.connector_wrap)
        root.controls.append(self.cards.container)
        for c in self.hud.chips.values():
            root.controls.append(c["body"])
        root.controls.append(self.core.holder)
        root.controls.append(self.interface_row)
        root.controls.append(self.hologram.root)
        root.controls.append(self.modules.root)
        root.controls.append(self.settings_panel)
        root.controls.append(self.nav)
        root.controls.append(self.corner_labels["wm"])
        root.controls.append(self.corner_labels["ver"])
        root.controls.append(self.command.root)
        root.controls.append(self.stream.root)
        root.controls.append(self.dim)
        root.controls.append(self.shutdown)
        root.controls.append(self.boot)
        self.cards.add_all()
        self.layout()
        self.state.phase = "boot"
        self.boot.visible = True
        self.boot_t = 0.0
        self.core.holder.opacity = 0.0
