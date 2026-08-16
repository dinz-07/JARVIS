import flet as ft

from app.theme import (
    CYAN, ICE, WHITE, DIM, PANEL, PANEL_2, BG_DEEP, GREEN, AMBER, VIOLET,
    GOLD, ROSE, MAGENTA, TEAL, rgba, label, FONT,
)
from components.module_cards import CARD_COLS

MODULE_ACCENTS = {
    "system": CYAN,
    "weather": CYAN,
    "calendar": GOLD,
    "tasks": GREEN,
    "music": ROSE,
    "browser": VIOLET,
    "email": TEAL,
    "security": GREEN,
}


class ModulesPanel:
    def __init__(self, app):
        self.app = app
        self.state = app.state
        self.current = None
        self.system_rows = {}
        self.music_bar = None
        self.music_title = None
        self.scan_status = None
        self.tasks_col = None
        self.browser_body = None

        self.title = ft.Text(
            "MODULE", size=20,
            style=ft.TextStyle(color=WHITE, font_family=FONT, letter_spacing=4.0, weight=ft.FontWeight.W_200),
        )
        self.uid = ft.Text(
            "", size=9, style=ft.TextStyle(color=rgba(DIM, 0.8), font_family=FONT, letter_spacing=2.0),
        )
        close_icon = getattr(ft.Icons, "CLOSE", None)
        self.close_btn = ft.IconButton(
            icon=close_icon,
            icon_color=ICE,
            icon_size=18,
            on_click=lambda e: self.app.close_module(),
        )
        self.content = ft.Container(expand=True, padding=ft.Padding.all(8))
        self.accent = CYAN
        self.underline = ft.Container(
            height=2,
            border_radius=ft.BorderRadius(1, 1, 1, 1),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1.0, 0.0),
                end=ft.Alignment(1.0, 0.0),
                colors=["#00000000", rgba(CYAN, 0.9), "#00000000"],
            ),
            shadow=[ft.BoxShadow(blur_radius=12, color=rgba(CYAN, 0.5))],
        )
        self.brackets = {
            "tl": self._bracket("tl", CYAN),
            "tr": self._bracket("tr", CYAN),
            "bl": self._bracket("bl", CYAN),
            "br": self._bracket("br", CYAN),
        }
        self.root = ft.Container(
            content=ft.Stack(
                [
                    ft.Container(
                        width=36,
                        height=3,
                        border_radius=ft.BorderRadius(2, 2, 0, 0),
                        bgcolor=rgba(CYAN, 0.9),
                        shadow=[ft.BoxShadow(blur_radius=10, color=rgba(CYAN, 0.8))],
                    ),
                    self.brackets["tl"],
                    self.brackets["tr"],
                    self.brackets["bl"],
                    self.brackets["br"],
                    ft.Container(
                        left=3,
                        top=0,
                        right=3,
                        height=1,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1.0, 0.0),
                            end=ft.Alignment(1.0, 0.0),
                            colors=["#00ffffff", rgba(WHITE, 0.14), "#00ffffff"],
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Column([self.title, self.uid], spacing=2),
                                    ft.Container(expand=True),
                                    self.close_btn,
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            self.underline,
                            self.content,
                        ],
                        spacing=12,
                    ),
                ]
            ),
            width=880,
            height=560,
            border_radius=8,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0.5, -1.0),
                end=ft.Alignment(0.5, 1.0),
                colors=[rgba("#020c1b", 0.97), rgba("#000000", 0.97)],
            ),
            border=ft.Border.all(1, rgba(CYAN, 0.4)),
            shadow=[
                ft.BoxShadow(blur_radius=70, spread_radius=6, color=rgba(CYAN, 0.3)),
                ft.BoxShadow(blur_radius=140, color=rgba(VIOLET, 0.14)),
            ],
            padding=ft.Padding.all(22),
            opacity=0.0,
            visible=False,
        )

    def _bracket(self, pos, accent):
        side = 1.6
        if pos == "tl":
            return ft.Container(
                left=10, top=10, width=16, height=16,
                border=ft.Border(
                    left=ft.BorderSide(side, rgba(accent, 0.8)),
                    top=ft.BorderSide(side, rgba(accent, 0.8)),
                ),
                shadow=[ft.BoxShadow(blur_radius=8, color=rgba(accent, 0.6))],
            )
        if pos == "tr":
            return ft.Container(
                right=10, top=10, width=16, height=16,
                border=ft.Border(
                    right=ft.BorderSide(side, rgba(accent, 0.8)),
                    top=ft.BorderSide(side, rgba(accent, 0.8)),
                ),
                shadow=[ft.BoxShadow(blur_radius=8, color=rgba(accent, 0.6))],
            )
        if pos == "bl":
            return ft.Container(
                left=10, bottom=10, width=16, height=16,
                border=ft.Border(
                    left=ft.BorderSide(side, rgba(accent, 0.8)),
                    bottom=ft.BorderSide(side, rgba(accent, 0.8)),
                ),
                shadow=[ft.BoxShadow(blur_radius=8, color=rgba(accent, 0.6))],
            )
        return ft.Container(
            right=10, bottom=10, width=16, height=16,
            border=ft.Border(
                right=ft.BorderSide(side, rgba(accent, 0.8)),
                bottom=ft.BorderSide(side, rgba(accent, 0.8)),
            ),
            shadow=[ft.BoxShadow(blur_radius=8, color=rgba(accent, 0.6))],
        )

    def _set_accent(self, name):
        accent = MODULE_ACCENTS.get(name, CYAN)
        self.accent = accent
        self.title.style = ft.TextStyle(
            color=accent, font_family=FONT, letter_spacing=4.0, weight=ft.FontWeight.W_200,
        )
        self.underline.gradient = ft.LinearGradient(
            begin=ft.Alignment(-1.0, 0.0),
            end=ft.Alignment(1.0, 0.0),
            colors=["#00000000", rgba(accent, 0.9), "#00000000"],
        )
        self.underline.shadow = [ft.BoxShadow(blur_radius=12, color=rgba(accent, 0.5))]
        self.root.border = ft.Border.all(1, rgba(accent, 0.45))
        self.root.shadow = [
            ft.BoxShadow(blur_radius=70, spread_radius=6, color=rgba(accent, 0.3)),
            ft.BoxShadow(blur_radius=140, color=rgba(accent, 0.12)),
        ]
        self.root.gradient = ft.LinearGradient(
            begin=ft.Alignment(0.5, -1.0),
            end=ft.Alignment(0.5, 1.0),
            colors=[rgba("#020c1b", 0.97), rgba("#000000", 0.97), rgba(accent, 0.05)],
        )
        for pos, b in self.brackets.items():
            b.border = {
                "tl": ft.Border(left=ft.BorderSide(1.6, rgba(accent, 0.85)), top=ft.BorderSide(1.6, rgba(accent, 0.85))),
                "tr": ft.Border(right=ft.BorderSide(1.6, rgba(accent, 0.85)), top=ft.BorderSide(1.6, rgba(accent, 0.85))),
                "bl": ft.Border(left=ft.BorderSide(1.6, rgba(accent, 0.85)), bottom=ft.BorderSide(1.6, rgba(accent, 0.85))),
                "br": ft.Border(right=ft.BorderSide(1.6, rgba(accent, 0.85)), bottom=ft.BorderSide(1.6, rgba(accent, 0.85))),
            }[pos]
            b.shadow = [ft.BoxShadow(blur_radius=8, color=rgba(accent, 0.6))]

    def _card(self, content, accent=CYAN):
        return ft.Container(
            content=ft.Stack(
                [
                    ft.Container(
                        content=content,
                        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                    ),
                    ft.Container(
                        left=2,
                        top=0,
                        right=2,
                        height=1,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1.0, 0.0),
                            end=ft.Alignment(1.0, 0.0),
                            colors=["#00ffffff", rgba(WHITE, 0.12), "#00ffffff"],
                        ),
                    ),
                    ft.Container(
                        left=1,
                        bottom=1,
                        right=1,
                        height=2,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1.0, 0.0),
                            end=ft.Alignment(1.0, 0.0),
                            colors=["#00ffffff", rgba(BG_DEEP, 0.5), "#00ffffff"],
                        ),
                    ),
                ]
            ),
            border_radius=4,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1.0, -1.0),
                end=ft.Alignment(1.0, 1.0),
                colors=[rgba(PANEL_2, 0.92), rgba(BG_DEEP, 0.92)],
            ),
            border=ft.Border.all(1, rgba(accent, 0.22)),
            shadow=[
                ft.BoxShadow(blur_radius=16, color=rgba(accent, 0.14)),
                ft.BoxShadow(blur_radius=40, color=rgba(accent, 0.06), offset=ft.Offset(0, 6)),
            ],
        )

    def layout(self, w, h):
        self.root.width = min(900, int(w * 0.56))
        self.root.height = min(580, int(h * 0.62))
        self.root.left = int(w / 2 - self.root.width / 2)
        self.root.top = int(h * 0.17)

    def open(self, name):
        self.current = name
        self._set_accent(name)
        self.title.value = name + " OVERVIEW"
        self.uid.value = f"NODE {CARD_COLS[name] + 1:02d} // {name} MODULE LINK"
        builder = getattr(self, "_build_" + name.lower(), None)
        if builder:
            builder()
        self.root.visible = True
        self.state.tween(self.root, "opacity", 1.0, duration=0.35)
        self.state.tween(self.root, "scale", 1.0, duration=0.45, curve="out_back", start=0.9)
        self.state.log("MODULE OPENED :: " + name)

    def close(self):
        if not self.root.visible:
            return
        self.state.tween(self.root, "opacity", 0.0, duration=0.3)
        self.state.tween(self.root, "scale", 0.9, duration=0.35, on_done=self._hidden)
        self.current = None

    def _hidden(self):
        self.root.visible = False

    def _bar(self, pct, color=CYAN):
        return ft.Container(
            width=150,
            height=5,
            border_radius=3,
            bgcolor=rgba(DIM, 0.15),
            content=ft.Container(
                width=int(150 * max(0.0, min(1.0, pct / 100.0))),
                height=5,
                border_radius=3,
                bgcolor=rgba(color, 0.9),
                shadow=[ft.BoxShadow(blur_radius=8, color=rgba(color, 0.6))],
            ),
        )

    def _row(self, k, v, color=ICE):
        inner = ft.Row(
            [
                ft.Container(
                    width=5,
                    height=5,
                    border_radius=3,
                    bgcolor=rgba(color, 0.9),
                    shadow=[ft.BoxShadow(blur_radius=6, color=rgba(color, 0.7))],
                ),
                label(k, 10, DIM, 2.5),
                ft.Container(expand=True),
                ft.Text(v, size=12, style=ft.TextStyle(color=color, font_family=FONT, letter_spacing=1.2)),
            ],
            spacing=8,
        )
        return self._card(inner, color)

    def _build_system(self):
        self.system_rows = {}
        col = ft.Column(spacing=9)
        for key, disp in [
            ("cpu", "CPU"), ("mem", "MEMORY"), ("gpu", "GPU"), ("disk", "STORAGE"),
            ("net", "NETWORK"), ("batt", "POWER"),
        ]:
            row = ft.Row([label(disp, 10, DIM, 2.5), ft.Container(expand=True)])
            v = ft.Text("--", size=12, style=ft.TextStyle(color=ICE, font_family=FONT, letter_spacing=1.2))
            row.controls.append(self._bar(0))
            row.controls.append(v)
            self.system_rows[key] = (row, v)
            col.controls.append(self._card(row))
        col.controls.append(ft.Divider(height=1, color=rgba(CYAN, 0.12)))
        col.controls.append(self._row("SECURITY", "VERIFIED", GREEN))
        col.controls.append(self._row("THREAT LEVEL", "LOW", GREEN))
        col.controls.append(self._row("UPLINK", "AES-256 SECURE", ICE))
        self.content.content = col

    def update_system(self, data):
        if not self.system_rows:
            return
        vals = {
            "cpu": f"{int(data['cpu'])}%",
            "mem": f"{int(data['mem'])}%",
            "gpu": f"{int(data['gpu'])}%",
            "disk": f"{int(data['disk'])}%",
            "net": f"{data['net_mbps']:.1f} MB/s",
            "batt": f"{int(data['battery'].percent)}%" if data["battery"] else "N/A",
        }
        for key, (row, v) in self.system_rows.items():
            pct = {
                "cpu": data["cpu"], "mem": data["mem"], "gpu": data["gpu"],
                "disk": data["disk"], "net": min(100.0, data["net_mbps"] * 12),
                "batt": data["battery"].percent if data["battery"] else 100.0,
            }[key]
            row.controls[1].width = int(150 * max(0.0, min(1.0, pct / 100.0)))
            v.value = vals[key]
        self.content.update()

    def _build_weather(self):
        d = self.app.weather_data
        temp_col = AMBER if d["temp"] >= 30 else (ICE if d["temp"] >= 18 else WHITE)
        rows = [
            self._row("LOCATION", d["location"], ICE),
            self._row("CONDITION", d["condition"], ICE),
            self._row("TEMPERATURE", f"{d['temp']}°C", temp_col),
            self._row("HUMIDITY", f"{d['humidity']}%", ICE),
            self._row("WIND", f"{d['wind']} km/h", ICE),
        ]
        fcast = ft.Row(
            [
                self._card(
                    ft.Column([label(h, 9, DIM, 2), label(f"{t}°", 13, WHITE, 1)], spacing=4,
                              horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    GOLD,
                )
                for h, t, _ in d["forecast"]
            ],
            spacing=8,
        )
        self.content.content = ft.Column(
            [*rows, ft.Divider(height=1, color=rgba(CYAN, 0.12)), label("FORECAST", 9, DIM, 2.5), fcast],
            spacing=10,
        )

    def _build_calendar(self):
        rows = [
            self._card(
                ft.Row(
                    [
                        ft.Container(
                            content=label(t, 10, GOLD, 1.5, weight=ft.FontWeight.W_600),
                            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            border_radius=3,
                            bgcolor=rgba(GOLD, 0.1),
                            border=ft.Border.all(1, rgba(GOLD, 0.35)),
                        ),
                        label(e, 12, WHITE, 1.2),
                    ],
                    spacing=14,
                ),
                GOLD,
            )
            for t, e in self.app.calendar_data
        ]
        self.content.content = ft.Column(rows, spacing=14)

    def _build_tasks(self):
        self.tasks_col = ft.Column(spacing=8)
        field = ft.TextField(
            hint_text="NEW TASK...",
            hint_style=ft.TextStyle(color=rgba(DIM, 0.8), font_family=FONT, letter_spacing=1.5, size=11),
            text_style=ft.TextStyle(color=WHITE, font_family=FONT, letter_spacing=1.0, size=12),
            border_radius=4,
            border_color=rgba(CYAN, 0.3),
            focused_border_color=CYAN,
            height=36,
            content_padding=ft.Padding.symmetric(horizontal=12),
            on_submit=self._add_task,
        )
        self.content.content = ft.Column([self.tasks_col, field], spacing=10)
        self._render_tasks()

    def _safe_update(self, control):
        try:
            control.update()
        except RuntimeError:
            pass

    def _render_tasks(self):
        if self.tasks_col is None:
            return
        self.tasks_col.controls = []
        for i, t in enumerate(self.app.tasks.tasks):
            chk = ft.Checkbox(
                value=t["done"],
                on_change=lambda e, idx=i: self._toggle_task(idx),
                check_color=CYAN,
            )
            style = ft.TextStyle(
                color=rgba(DIM, 0.6) if t["done"] else WHITE,
                font_family=FONT,
                letter_spacing=1.0,
                decoration=ft.TextDecoration.LINE_THROUGH if t["done"] else None,
            )
            txt = ft.Text(t["text"], size=12, style=style)
            self.tasks_col.controls.append(self._card(ft.Row([chk, txt], spacing=8), GREEN))
        self._safe_update(self.tasks_col)

    def _toggle_task(self, i):
        self.app.tasks.toggle(i)
        self._render_tasks()

    def _add_task(self, e):
        if e.control.value.strip():
            self.app.tasks.add(e.control.value.strip())
            e.control.value = ""
            e.control.update()
            self._render_tasks()
            self.state.log("TASK ADDED")

    def _build_music(self):
        self.music_title = ft.Text(
            "", size=16,
            style=ft.TextStyle(color=WHITE, font_family=FONT, letter_spacing=2.0, weight=ft.FontWeight.W_200),
        )
        self.music_bar = ft.ProgressBar(value=0.0, color=CYAN, bgcolor=rgba(DIM, 0.12), height=4, border_radius=2)
        self.music_eq = ft.Row(
            [ft.Container(width=3, height=6, border_radius=2, bgcolor=rgba(CYAN, 0.7)) for _ in range(9)],
            spacing=3,
            vertical_alignment=ft.CrossAxisAlignment.END,
        )
        play_icon = getattr(ft.Icons, "PLAY_ARROW", None)
        next_icon = getattr(ft.Icons, "SKIP_NEXT", None)
        self.play_btn = ft.IconButton(icon=play_icon, icon_color=ICE, on_click=lambda e: self._toggle_music())
        self.next_btn = ft.IconButton(icon=next_icon, icon_color=ICE, on_click=lambda e: self._next_music())
        self.controls_row = ft.Row([self.play_btn, self.next_btn])
        self.content.content = self._card(
            ft.Column(
                [
                    ft.Row([label("NOW PLAYING", 9, DIM, 2.5), ft.Container(expand=True), self.music_eq],
                           vertical_alignment=ft.CrossAxisAlignment.END),
                    self.music_title,
                    self.music_bar,
                    ft.Container(height=6),
                    self.controls_row,
                ],
                spacing=8,
            ),
            ROSE,
        )
        self._render_music()

    def _render_music(self):
        title, artist = self.app.music.track
        self.music_title.value = f"{title} — {artist}"
        self._safe_update(self.music_title)

    def _toggle_music(self):
        self.app.music.toggle()
        self.state.log("MUSIC " + ("PLAYING" if self.app.music.playing else "PAUSED"))
        self._render_music()

    def _next_music(self):
        self.app.music.next()
        self.state.log("TRACK ADVANCED")
        self._render_music()

    def _build_email(self):
        rows = [
            self._card(
                ft.Column(
                    [label(f"FROM {f}", 10, TEAL, 2), label(s, 12, WHITE, 1.0)],
                    spacing=3,
                ),
                TEAL,
            )
            for f, s in self.app.email_data
        ]
        self.content.content = ft.Column(rows, spacing=10)

    def _build_security(self):
        self.scan_status = ft.Text(
            "", size=12, style=ft.TextStyle(color=GREEN, font_family=FONT, letter_spacing=1.5),
        )
        scan_icon = getattr(ft.Icons, "SEARCH", None)
        btn = ft.FilledButton(
            "RUN THREAT SCAN",
            icon=scan_icon,
            on_click=lambda e: self.app.start_scan(),
            style=ft.ButtonStyle(
                color=WHITE,
                bgcolor=rgba(CYAN, 0.15),
                side=ft.BorderSide(1, rgba(CYAN, 0.5)),
            ),
        )
        threat_pill = ft.Container(
            content=label(self.app.security.threat, 10, GREEN, 2, weight=ft.FontWeight.W_600),
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            border_radius=12,
            bgcolor=rgba(GREEN, 0.08),
            border=ft.Border.all(1, rgba(GREEN, 0.35)),
        )
        self.content.content = ft.Column(
            [
                self._row("SECURITY PROTOCOL", "LEVEL 7", ICE),
                self._row("FIREWALL", "ACTIVE", GREEN),
                self._row("BREACH ATTEMPTS", f"{self.app.security.breaches} BLOCKED", GREEN),
                self._row("COMPLETED SCANS", str(self.app.security.scans), ICE),
                ft.Row(
                    [
                        ft.Container(
                            width=5, height=5, border_radius=3, bgcolor=rgba(GREEN, 0.9),
                            shadow=[ft.BoxShadow(blur_radius=6, color=rgba(GREEN, 0.7))],
                        ),
                        label("THREAT LEVEL", 10, DIM, 2.5),
                        ft.Container(expand=True),
                        threat_pill,
                    ],
                    spacing=8,
                ),
                ft.Divider(height=1, color=rgba(CYAN, 0.12)),
                btn,
                self.scan_status,
            ],
            spacing=11,
        )

    def set_scan_status(self, text, color=GREEN):
        if self.scan_status:
            self.scan_status.value = text
            self.scan_status.style = ft.TextStyle(color=color, font_family=FONT, letter_spacing=1.5)
            self.scan_status.update()

    def _build_browser(self):
        field = ft.TextField(
            hint_text="jarvis://core",
            hint_style=ft.TextStyle(color=rgba(DIM, 0.8), font_family=FONT, letter_spacing=1.0, size=11),
            text_style=ft.TextStyle(color=WHITE, font_family=FONT, letter_spacing=1.0, size=12),
            border_radius=4,
            border_color=rgba(CYAN, 0.3),
            focused_border_color=CYAN,
            height=36,
            content_padding=ft.Padding.symmetric(horizontal=12),
            on_submit=lambda e: self._browse(e.control),
        )
        go_icon = getattr(ft.Icons, "ARROW_FORWARD", None)
        go = ft.IconButton(icon=go_icon, icon_color=ICE, on_click=lambda e: self._browse(field))
        self.browser_body = ft.Text(
            "", size=12, style=ft.TextStyle(color=ICE, font_family=FONT, letter_spacing=1.2),
        )
        self.browser_detail = ft.Text(
            "", size=11, style=ft.TextStyle(color=DIM, font_family=FONT, letter_spacing=1.0),
        )
        self.content.content = ft.Column(
            [
                ft.Row([field, go], spacing=4),
                ft.Divider(height=1, color=rgba(CYAN, 0.12)),
                self._card(ft.Column([self.browser_body, self.browser_detail], spacing=6), VIOLET),
            ],
            spacing=10,
        )
        title, lines = self.app.browser.go("jarvis://core")
        self.browser_body.value = title
        self.browser_detail.value = "\n".join(lines)

    def _browse(self, field):
        url = field.value
        title, lines = self.app.browser.go(url)
        self.browser_body.value = title
        self.browser_detail.value = "\n".join(lines)
        self.browser_body.update()
        self.browser_detail.update()
        self.state.log("BROWSER :: " + (url or "jarvis://core"))

    def tick(self, dt):
        if self.current == "MUSIC" and self.music_bar:
            self.app.music.tick(dt)
            self.music_bar.value = self.app.music.pos
            import math
            base = 1.0 if self.app.music.playing else 0.4
            for i, bar in enumerate(self.music_eq.controls):
                h = base * (8 + 14 * abs(math.sin(self.app.music.t * 4.0 + i * 0.8)))
                bar.height = h
