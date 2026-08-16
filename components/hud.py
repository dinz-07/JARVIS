import math

import flet as ft
import flet.canvas as ftcanvas

from app.state import LISTENING, SPEAKING, THINKING, EXECUTING, IDLE
from app.theme import CYAN, ICE, WHITE, DIM, PANEL, VIOLET, rgba, label, value_text, FONT, panel_gradient

CHIP_POS = {
    "cpu": (0.085, 0.19),
    "neural": (0.925, 0.19),
    "voice": (0.085, 0.80),
    "latency": (0.925, 0.80),
    "load": (0.50, 0.125),
}


class Hud:
    def __init__(self, state):
        self.state = state
        self.t = 0.0
        self.chips = {}
        self.connector = ftcanvas.Canvas(shapes=[], width=1920, height=1080)
        self.connector_wrap = ft.Container(content=self.connector, width=1920, height=1080)
        for key, (px, py) in CHIP_POS.items():
            self.chips[key] = self._chip(key, px, py)

    def _chip(self, key, px, py):
        value = value_text("--", 24, ICE, 1)
        unit = ft.Text(
            "", size=9, style=ft.TextStyle(color=DIM, font_family=FONT, letter_spacing=1.5),
        )
        accent = ft.Container(
            width=3,
            height=22,
            border_radius=1.5,
            bgcolor=rgba(CYAN, 0.85),
            shadow=[ft.BoxShadow(blur_radius=6, color=rgba(CYAN, 0.7))],
        )
        body = ft.Container(
            content=ft.Stack(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Container(
                                            width=5,
                                            height=5,
                                            border_radius=3,
                                            bgcolor=rgba(CYAN, 0.9),
                                            shadow=[ft.BoxShadow(blur_radius=6, color=rgba(CYAN, 0.8))],
                                        ),
                                        label(key.upper().replace("_", " "), 9, ICE, 2.4),
                                    ],
                                    spacing=7,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Row([value, unit], spacing=5, vertical_alignment=ft.CrossAxisAlignment.END),
                            ],
                            spacing=6,
                        ),
                        padding=ft.Padding.only(left=14, right=12, top=12, bottom=12),
                    ),
                    ft.Container(left=0, top=0, width=3, height=22, border_radius=ft.BorderRadius(0, 2, 0, 0), bgcolor=rgba(CYAN, 0.85)),
                    ft.Container(
                        left=2, top=0, right=2, height=1,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1.0, 0.0),
                            end=ft.Alignment(1.0, 0.0),
                            colors=["#00ffffff", rgba(WHITE, 0.14), "#00ffffff"],
                        ),
                    ),
                ]
            ),
            width=132,
            border_radius=6,
            bgcolor=rgba("#020c1b", 0.72),
            border=ft.Border.all(1, rgba(CYAN, 0.2)),
            shadow=[ft.BoxShadow(blur_radius=20, color=rgba(CYAN, 0.12))],
        )
        return {
            "key": key,
            "px": px,
            "py": py,
            "value": value,
            "unit": unit,
            "body": body,
        }

    def layout(self, w, h):
        for key, c in self.chips.items():
            cw = c["body"].width if c["body"].width else 118
            ch = c["body"].height if c["body"].height else 54
            c["body"].left = int(w * c["px"] - cw / 2)
            c["body"].top = int(h * c["py"] - ch / 2)
        self.connector.width = w
        self.connector.height = h
        self.connector_wrap.width = w
        self.connector_wrap.height = h

    def update(self, telemetry, core_r, cx, cy):
        t = self.state.now
        neural_base = {
            IDLE: 38, LISTENING: 64, THINKING: 82, SPEAKING: 58, EXECUTING: 90,
        }.get(self.state.ai_state, 40)
        neural = max(0, min(100, int(neural_base + 6 * math.sin(t * 2.3) + 3 * math.sin(t * 7.7))))
        lat = int(8 + telemetry["cpu"] * 0.28 + 2 * math.sin(t * 5.1) + 3)
        voice = "ACTIVE" if self.state.voice_active else ("STANDBY" if self.state.ai_state == IDLE else "ENGAGED")
        self._set("cpu", f"{int(telemetry['cpu'])}%", "CPU")
        self._set("neural", f"{neural}%", "NEURAL")
        self._set("latency", f"{lat}ms", "NET")
        self._set("voice", voice, "VOICE")
        self._set("load", f"{int(telemetry['mem'])}%", "MEM")

        shapes = []
        for key, c in self.chips.items():
            bx = (c["body"].left or 0) + (c["body"].width or 118) / 2
            by = (c["body"].top or 0) + (c["body"].height or 54) / 2
            dx = cx - bx
            dy = cy - by
            dist = math.hypot(dx, dy)
            if dist < 5:
                continue
            ex = cx - dx / dist * (core_r + 10)
            ey = cy - dy / dist * (core_r + 10)
            col = VIOLET if dist > max(cx, cy) * 0.55 else CYAN
            glow_a = 0.14 + 0.10 * math.sin(t * 1.7 + bx * 0.01)
            shapes.append(
                ftcanvas.Line(
                    bx, by, ex, ey,
                    paint=ft.Paint(
                        color=rgba(col, glow_a),
                        stroke_width=1.0,
                        stroke_cap=ft.StrokeCap.ROUND,
                    ),
                )
            )
            shapes.append(ftcanvas.Circle(ex, ey, 2.2, paint=ft.Paint(color=rgba(col, 0.55))))
            shapes.append(ftcanvas.Circle(ex, ey, 1.1, paint=ft.Paint(color=rgba(ICE, 0.9))))
        self.connector.shapes = shapes

    def _set(self, key, value, unit):
        c = self.chips[key]
        c["value"].value = value
        c["unit"].value = unit
