import math
import random

import flet as ft
import flet.canvas as ftcanvas

from app.theme import CYAN, ICE, VIOLET, rgba
from app import theme


def _radial(center, radius, stops):
    try:
        return ft.RadialGradient(center=center, radius=radius, colors=stops)
    except Exception:
        return None


class Background:
    def __init__(self, state, width=1600, height=900):
        self.state = state
        self.width = width
        self.height = height
        self.t = 0.0
        self.particles = []
        self.links = []
        self.rebuild()
        self.canvas = ftcanvas.Canvas(shapes=[], width=self.width, height=self.height)
        self.static_canvas = ftcanvas.Canvas(
            shapes=list(self.static_shapes), width=self.width, height=self.height
        )
        self.stack = ft.Stack(
            [
                ft.Container(
                    width=self.width,
                    height=self.height,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(0.5, -1.0),
                        end=ft.Alignment(0.5, 1.0),
                        colors=["#000000", theme.BG, theme.BG_DEEP],
                    ),
                ),
                ft.Container(
                    width=int(self.width * 0.7),
                    height=int(self.height * 0.75),
                    left=int(-self.width * 0.22),
                    top=int(-self.height * 0.28),
                    gradient=_radial(
                        ft.Alignment(0.4, 0.5),
                        self.height * 0.9,
                        ["#00000000", rgba(CYAN, 0.05), "#00000000"],
                    ),
                ),
                ft.Container(
                    width=int(self.width * 0.8),
                    height=int(self.height * 0.8),
                    right=int(-self.width * 0.25),
                    bottom=int(-self.height * 0.3),
                    gradient=_radial(
                        ft.Alignment(0.5, 0.5),
                        self.height,
                        ["#00000000", rgba(CYAN, 0.06), "#00000000"],
                    ),
                ),
                self.static_canvas,
                self.canvas,
                ft.Container(
                    width=self.width,
                    height=self.height,
                    gradient=_radial(
                        ft.Alignment(0.5, 0.45),
                        self.height * 1.15,
                        [rgba("#02040a", 0.55), rgba("#02040a", 0.12), "#00000000"],
                    ),
                ),
            ],
            width=self.width,
            height=self.height,
        )

    def _bottom_glow(self):
        try:
            return ft.RadialGradient(
                center=ft.Alignment(0.0, 1.0),
                radius=self.height * 0.9,
                colors=["#00000000", rgba(CYAN, 0.05), "#00000000"],
            )
        except Exception:
            return None

    def rebuild(self):
        random.seed(7)
        n = int(44 * self.state.settings["particles"])
        self.particles = []
        for _ in range(n):
            self.particles.append(
                {
                    "x": random.uniform(0, self.width),
                    "y": random.uniform(0, self.height),
                    "vx": random.uniform(-8, 8),
                    "vy": random.uniform(-6, 6),
                    "r": random.uniform(0.8, 2.0),
                    "ph": random.uniform(0, 6.28),
                    "sp": random.uniform(0.4, 1.4),
                }
            )
        self.links = []
        for _ in range(12):
            a, b = random.sample(range(len(self.particles)), 2)
            self.links.append((a, b))
        self.static_shapes = self._static_shapes()

    def _static_shapes(self):
        shapes = []
        gx = 56
        gy = 56
        dot = rgba(CYAN, 0.055)
        for x in range(0, self.width + 1, gx):
            for y in range(0, self.height + 1, gy):
                shapes.append(ftcanvas.Circle(x, y, 0.8, paint=ft.Paint(color=dot)))
        scan = rgba(CYAN, 0.022)
        for y in range(0, self.height + 1, 5):
            shapes.append(
                ftcanvas.Line(0, y, self.width, y, paint=ft.Paint(color=scan, stroke_width=0.5))
            )
        self._brackets(shapes)
        return shapes

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.canvas.width = width
        self.canvas.height = height
        self.static_canvas.width = width
        self.static_canvas.height = height
        self.stack.width = width
        self.stack.height = height
        for c in self.stack.controls:
            if isinstance(c, ft.Container):
                c.width = width
                c.height = height
        self.rebuild()
        self.static_canvas.shapes = list(self.static_shapes)

    def tick(self, dt, reduced=False, cursor=None):
        self.t += dt
        speed = 0.35 if reduced else 1.0
        shapes = []
        mx = my = strength = None
        if cursor:
            mx, my, strength = cursor
        for p in self.particles:
            if strength and mx is not None:
                dx = p["x"] - mx
                dy = p["y"] - my
                d2 = dx * dx + dy * dy
                if d2 < 14400:
                    d = math.sqrt(d2) or 1.0
                    f = (1.0 - d / 120.0) * 160.0 * strength
                    p["x"] += dx / d * f * dt * speed
                    p["y"] += dy / d * f * dt * speed
            p["x"] += p["vx"] * speed * dt
            p["y"] += p["vy"] * speed * dt
            if p["x"] < -8:
                p["x"] = self.width + 8
            if p["x"] > self.width + 8:
                p["x"] = -8
            if p["y"] < -8:
                p["y"] = self.height + 8
            if p["y"] > self.height + 8:
                p["y"] = -8
            a = 0.16 + 0.22 * (0.5 + 0.5 * math.sin(self.t * p["sp"] + p["ph"]))
            shapes.append(
                ftcanvas.Circle(
                    p["x"], p["y"], p["r"],
                    paint=ft.Paint(color=rgba(ICE, a)),
                )
            )
        for a, b in self.links:
            pa = self.particles[a]
            pb = self.particles[b]
            alpha = 0.05 + 0.05 * math.sin(self.t * 0.8 + a)
            shapes.append(
                ftcanvas.Line(
                    pa["x"], pa["y"], pb["x"], pb["y"],
                    paint=ft.Paint(color=rgba(CYAN, alpha), stroke_width=0.7),
                )
            )
        if strength and mx is not None:
            breath = 0.5 + 0.5 * math.sin(self.t * 2.6)
            rr = (24 + breath * 12) * (0.4 + 0.6 * strength)
            shapes.append(
                ftcanvas.Circle(
                    mx, my, rr,
                    paint=ft.Paint(
                        color=rgba(CYAN, (0.10 + 0.07 * breath) * strength),
                        style=ft.PaintingStyle.STROKE,
                        stroke_width=1.0,
                    ),
                )
            )
            shapes.append(
                ftcanvas.Circle(
                    mx, my, 1.6,
                    paint=ft.Paint(color=rgba(ICE, (0.75 + 0.2 * breath) * strength)),
                )
            )
        self.canvas.shapes = shapes

    def update(self):
        self.canvas.update()

    def _brackets(self, shapes):
        m = 16
        s = 34
        col = rgba(CYAN, 0.5)
        pts = [
            (m, m, m + s, m),
            (m, m, m, m + s),
            (self.width - m - s, m, self.width - m, m),
            (self.width - m, m, self.width - m, m + s),
            (m, self.height - m, m + s, self.height - m),
            (m, self.height - m - s, m, self.height - m),
            (self.width - m - s, self.height - m, self.width - m, self.height - m),
            (self.width - m, self.height - m - s, self.width - m, self.height - m),
        ]
        for x1, y1, x2, y2 in pts:
            shapes.append(
                ftcanvas.Line(x1, y1, x2, y2, paint=ft.Paint(color=col, stroke_width=1.2))
            )
        tick = rgba(CYAN, 0.35)
        tx = [(m, m, m + 6, m), (m, m, m, m + 6),
              (self.width - m - 6, m, self.width - m, m), (self.width - m, m, self.width - m, m + 6),
              (m, self.height - m - 6, m, self.height - m), (m, self.height - m, m + 6, self.height - m),
              (self.width - m - 6, self.height - m, self.width - m, self.height - m),
              (self.width - m, self.height - m - 6, self.width - m, self.height - m)]
        for x1, y1, x2, y2 in tx:
            shapes.append(
                ftcanvas.Line(x1, y1, x2, y2, paint=ft.Paint(color=tick, stroke_width=1.0))
            )
