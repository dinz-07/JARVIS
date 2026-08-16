import math
import random

import flet as ft
import flet.canvas as ftcanvas

from app.state import EXECUTING, IDLE, LISTENING, SPEAKING, THINKING
from app.theme import CYAN, ICE, VIOLET, MAGENTA, ROSE, GOLD, TEAL, GREEN, WHITE, rgba

ROT_SPEED = {
    IDLE: 0.13,
    LISTENING: 0.45,
    THINKING: 1.05,
    SPEAKING: 0.55,
    EXECUTING: 0.9,
}

STATE_COLOR = {
    IDLE: CYAN,
    LISTENING: CYAN,
    THINKING: MAGENTA,
    SPEAKING: ROSE,
    EXECUTING: GREEN,
}

STATE_LABEL = {
    IDLE: "STANDBY",
    LISTENING: "LISTENING...",
    THINKING: "ANALYZING...",
    SPEAKING: "SPEAKING...",
    EXECUTING: "EXECUTING...",
}

STATE_TEXT_COLOR = {
    IDLE: CYAN,
    LISTENING: ICE,
    THINKING: MAGENTA,
    SPEAKING: ROSE,
    EXECUTING: GREEN,
}


class AICore:
    def __init__(self, state, radius=170):
        self.state = state
        self.radius = radius
        self.t = 0.0
        self.form = 0.0
        self.power = 1.0
        self.parallax_x = 0.0
        self.parallax_y = 0.0
        self.rot1 = 0.0
        self.rot2 = 0.0
        self.rot_fast = 0.0
        self.wf = [0.0] * 30
        self.wf_target = 0.0
        self.orbiters = []
        random.seed(11)
        for i in range(26):
            self.orbiters.append(
                {
                    "ang": random.uniform(0, 6.28),
                    "sp": random.uniform(0.2, 0.9) * (1 if i % 2 else -1),
                    "rad": random.uniform(0.95, 1.75),
                    "r": random.uniform(1.0, 2.4),
                    "ph": random.uniform(0, 6.28),
                    "sp2": random.uniform(0.4, 1.4),
                    "col": [CYAN, ICE, TEAL, "#5ea9ff", MAGENTA][i % 5],
                }
            )
        self.hex_verts, self.hex_edges = self._build_lattice()
        self.cs = int(self.radius * 2 + 170)
        self.canvas = ftcanvas.Canvas(shapes=[], width=self.cs, height=self.cs)

        self.status = ft.Text(
            "STANDBY",
            size=24,
            style=ft.TextStyle(color=CYAN, font_family="Orbitron", letter_spacing=8, weight=ft.FontWeight.W_400),
            text_align=ft.TextAlign.CENTER,
        )
        self.sub = ft.Text(
            "JARVIS // NEURAL CORE // NODE 01",
            size=9,
            style=ft.TextStyle(color="#5a7089", font_family="Orbitron", letter_spacing=2.4),
            text_align=ft.TextAlign.CENTER,
        )
        self.pct = ft.Text(
            "0%",
            size=20,
            style=ft.TextStyle(color=WHITE, font_family="Orbitron", letter_spacing=2, weight=ft.FontWeight.W_300),
            text_align=ft.TextAlign.CENTER,
            opacity=0,
        )
        self.lock = ft.Text(
            "SECURE UPLINK // SYSTEM LINK: ACTIVE",
            size=8,
            style=ft.TextStyle(color="#43627c", font_family="Exo 2", letter_spacing=2.0),
            text_align=ft.TextAlign.CENTER,
            opacity=0.7,
        )

        self.glow_outer = ft.Container(
            width=int(self.radius * 3.1),
            height=int(self.radius * 3.1),
            border_radius=int(self.radius * 1.55),
            bgcolor=rgba(CYAN, 0.02),
            shadow=[
                ft.BoxShadow(
                    spread_radius=6,
                    blur_radius=90,
                    color=rgba(CYAN, 0.10),
                )
            ],
        )
        self.ghost_ring = ft.Container(
            width=int(self.radius * 2.35),
            height=int(self.radius * 2.35),
            border_radius=int(self.radius * 1.18),
            bgcolor="#00000000",
            border=ft.Border.all(1, rgba(CYAN, 0.10)),
        )

        self.info_col = ft.Column(
            [
                self.sub,
                self.status,
                self.pct,
                self.lock,
            ],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.root = ft.Stack(
            [
                self.glow_outer,
                self.ghost_ring,
                self.canvas,
                ft.Container(
                    content=self.info_col,
                    alignment=ft.Alignment.CENTER,
                    width=self.cs,
                    height=int(self.cs * 0.42),
                    bottom=0,
                ),
            ],
            width=self.cs,
            height=self.cs,
        )
        self.holder = ft.Container(
            content=self.root,
            width=self.cs,
            height=self.cs,
        )
        self.canvas_left = (self.cs - self.radius * 2) / 2
        self.canvas_top = (self.cs - self.radius * 2) / 2

    @staticmethod
    def _build_lattice():
        PHI = (1 + math.sqrt(5)) / 2
        ico = [
            (-1, PHI, 0), (1, PHI, 0), (-1, -PHI, 0), (1, -PHI, 0),
            (0, -1, PHI), (0, 1, PHI), (0, -1, -PHI), (0, 1, -PHI),
            (PHI, 0, -1), (PHI, 0, 1), (-PHI, 0, -1), (-PHI, 0, 1),
        ]
        faces = [
            (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
            (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
            (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
            (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
        ]
        hverts = []
        edge_keys = {}
        for fa in faces:
            for k in range(3):
                a, b = fa[k], fa[(k + 1) % 3]
                key = (a, b) if a < b else (b, a)
                if key not in edge_keys:
                    ax, ay, az = ico[key[0]]
                    bx, by, bz = ico[key[1]]
                    for t in (1 / 3, 2 / 3):
                        x = ax + (bx - ax) * t
                        y = ay + (by - ay) * t
                        z = az + (bz - az) * t
                        n = math.sqrt(x * x + y * y + z * z)
                        hverts.append((x / n, y / n, z / n))
                    edge_keys[key] = (len(hverts) - 2, len(hverts) - 1)
        hedges = list(edge_keys.values())

        def near_pt(v, nb):
            key = (v, nb) if v < nb else (nb, v)
            i1, i2 = edge_keys[key]
            return i1 if v == key[0] else i2

        for v in range(12):
            nbrs = []
            for fa in faces:
                if v in fa:
                    for nb in fa:
                        if nb != v and nb not in nbrs:
                            nbrs.append(nb)
            ring = [near_pt(v, nb) for nb in nbrs]
            for k in range(len(ring)):
                hedges.append((ring[k], ring[(k + 1) % len(ring)]))
        return hverts, hedges

    def resize(self, radius):
        self.radius = radius
        self.cs = int(radius * 2 + 170)
        self.canvas.width = self.cs
        self.canvas.height = self.cs
        self.root.width = self.cs
        self.root.height = self.cs
        self.holder.width = self.cs
        self.holder.height = self.cs
        self.glow_outer.width = int(radius * 3.1)
        self.glow_outer.height = int(radius * 3.1)
        self.glow_outer.border_radius = int(radius * 1.55)
        self.ghost_ring.width = int(radius * 2.35)
        self.ghost_ring.height = int(radius * 2.35)
        self.ghost_ring.border_radius = int(radius * 1.18)
        self.info_col.width = self.cs
        self.canvas_left = (self.cs - radius * 2) / 2
        self.canvas_top = (self.cs - radius * 2) / 2

    def set_state_visual(self):
        st = self.state.ai_state
        label = STATE_LABEL.get(st, "STANDBY")
        if self.status.value != label:
            self.status.value = label
        self.status.style = ft.TextStyle(
            color=STATE_TEXT_COLOR.get(st, CYAN),
            font_family="Orbitron",
            letter_spacing=6,
            weight=ft.FontWeight.W_400,
        )
        self.pct.opacity = 1.0 if st == EXECUTING else 0.0
        if st == EXECUTING:
            self.pct.value = f"{int(self.state.progress * 100)}%"

    def tick(self, dt):
        self.t += dt
        st = self.state.ai_state
        reduced = self.state.settings["reduced_motion"]
        anim_on = self.state.settings["animations"]
        if not anim_on:
            dt = 0.0
        spd = ROT_SPEED.get(st, 0.13)
        if reduced:
            spd *= 0.4
        self.rot1 += spd * dt
        self.rot2 -= spd * 0.55 * dt
        self.rot_fast += spd * 3.2 * dt

        if st == LISTENING:
            self.wf_target = 1.0
        elif st == SPEAKING:
            self.wf_target = 0.8
        else:
            self.wf_target = 0.0
        if st in (LISTENING, SPEAKING):
            self.wf_target += 0.12 * math.sin(self.t * 7.0)
        self.wf_target = max(0.0, min(1.0, self.wf_target))
        self.wf = [
            v + (self.wf_target - v) * min(1.0, dt * 6.0) + (random.uniform(-1, 1) * 0.06 if self.wf_target > 0.05 else 0)
            for v in self.wf
        ]
        self.wf = [max(0.05, min(1.0, v)) for v in self.wf]

        if self.state.phase == "boot":
            self.form = min(1.0, self.form + dt / 2.6)
        elif self.state.phase == "ready":
            self.form = min(1.0, self.form + dt * 2)
        if self.state.shutdown:
            self.power = max(0.0, self.power - dt / 2.8)

        breath = 0.5 + 0.5 * math.sin(self.t * 1.6)
        pulse = 1.0 + 0.05 * breath + (0.06 * math.sin(self.t * 9.0) if st == LISTENING else 0)
        R = self.radius
        C = self.cs / 2
        cx = self.parallax_x * 0.4
        cy = self.parallax_y * 0.4
        shapes = []
        f = self.form
        p = self.power
        accent = STATE_COLOR.get(st, CYAN)

        def A(col, a):
            return rgba(col, a * f * p)

        # ambient halo
        shapes.append(ftcanvas.Circle(C + cx, C + cy, R * 1.9, paint=ft.Paint(color=A(accent, 0.035))))
        for off in (-7, 9):
            shapes.append(
                ftcanvas.Circle(
                    C + cx + off, C + cy + (6 if off < 0 else -5), R * 1.45,
                    paint=ft.Paint(color=A(accent, 0.03), style=ft.PaintingStyle.STROKE, stroke_width=1.2),
                )
            )

        # ---- hexagon lattice sphere (truncated icosahedron wireframe) ----
        r3 = R * 1.5
        L = R * 1.04
        persp = 3.2
        sa, ca = math.sin(self.rot1 + self.parallax_y * 0.015), math.cos(self.rot1 + self.parallax_y * 0.015)
        sb, cb = math.sin(self.rot2 + self.parallax_x * 0.02), math.cos(self.rot2 + self.parallax_x * 0.02)
        proj = []
        for (x, y, z) in self.hex_verts:
            x1 = x * ca + z * sa
            z1 = -x * sa + z * ca
            y2 = y * cb - z1 * sb
            z2 = y * sb + z1 * cb
            if z2 < -persp * 0.97:
                z2 = -persp * 0.97
            s = persp / (persp + z2)
            proj.append((C + cx + x1 * s * L, C + cy + y2 * s * L, s, z2))
        for (i, j) in self.hex_edges:
            px1, py1, _, z1e = proj[i]
            px2, py2, _, z2e = proj[j]
            depth = 0.5 + (z1e + z2e) / (2 * persp)
            depth = max(0.0, min(1.0, depth))
            if depth < 0.03:
                continue
            shapes.append(
                ftcanvas.Line(
                    px1, py1, px2, py2,
                    paint=ft.Paint(
                        color=A(accent if depth > 0.5 else VIOLET, 0.06 + 0.5 * depth),
                        stroke_width=0.5 + 1.5 * depth,
                    ),
                )
            )
        for (x, y, _, z2) in proj:
            if z2 > 0.4:
                depth = 0.5 + z2 / persp
                shapes.append(
                    ftcanvas.Circle(
                        x, y, 1.0 + 0.9 * depth,
                        paint=ft.Paint(color=A(ICE, 0.2 + 0.5 * depth)),
                    )
                )

        # ---- state animations ----
        if st == IDLE:
            # graceful standby: slow gold sweep + counter cyan arc
            shapes.append(
                ftcanvas.Arc(
                    C + cx - r3, C + cy - r3, r3 * 2, r3 * 2,
                    self.rot1, 0.85, use_center=False,
                    paint=ft.Paint(color=A(CYAN, 0.4), style=ft.PaintingStyle.STROKE, stroke_width=1.8),
                )
            )
            shapes.append(
                ftcanvas.Arc(
                    C + cx - R * 1.62, C + cy - R * 1.62, R * 3.24, R * 3.24,
                    -self.rot2, 0.5, use_center=False,
                    paint=ft.Paint(color=A(CYAN, 0.25), style=ft.PaintingStyle.STROKE, stroke_width=1.1),
                )
            )
            shapes.append(
                ftcanvas.Circle(
                    C + cx + math.cos(self.rot1) * r3, C + cy + math.sin(self.rot1) * r3,
                    3.0, paint=ft.Paint(color=A(ICE, 0.95)),
                )
            )

        elif st == LISTENING:
            # radar: expanding echo rings + fast mic ring
            for k in range(3):
                ph = (self.t * 0.7 + k / 3.0) % 1.0
                rr = R * (0.45 + 0.6 * ph)
                al = 0.45 * (1.0 - ph)
                shapes.append(
                    ftcanvas.Circle(
                        C + cx, C + cy, rr,
                        paint=ft.Paint(color=A(CYAN, al), style=ft.PaintingStyle.STROKE, stroke_width=1.2),
                    )
                )
            n = len(self.wf)
            for i in range(n):
                a = i * math.tau / n + self.rot_fast * 0.15
                rr = R * 0.68 + self.wf[i] * R * 0.26
                mx = C + cx + math.cos(a) * rr
                my = C + cy + math.sin(a) * rr
                col = CYAN if i % 3 else ICE
                shapes.append(ftcanvas.Circle(mx, my, 2.2, paint=ft.Paint(color=A(col, 0.85))))

        elif st == THINKING:
            # analysis: 3 chasing color arcs + rotating scan beam + spark ring
            for i, (col, r, off) in enumerate(
                [(CYAN, R * 1.52, 0.0), (MAGENTA, R * 1.42, 2.1), (ICE, R * 1.32, 4.2)]
            ):
                a = self.rot_fast + off
                shapes.append(
                    ftcanvas.Arc(
                        C + cx - r, C + cy - r, r * 2, r * 2,
                        a, 0.9, use_center=False,
                        paint=ft.Paint(color=A(col, 0.5), style=ft.PaintingStyle.STROKE, stroke_width=1.8),
                    )
                )
                shapes.append(
                    ftcanvas.Circle(
                        C + cx + math.cos(a) * r, C + cy + math.sin(a) * r, 3.4,
                        paint=ft.Paint(color=A(col, 1.0)),
                    )
                )
            a = self.rot_fast
            shapes.append(
                ftcanvas.Arc(
                    C + cx - R * 1.05, C + cy - R * 1.05, R * 2.1, R * 2.1,
                    a, 0.55, use_center=True,
                    paint=ft.Paint(color=A(WHITE, 0.35), style=ft.PaintingStyle.STROKE, stroke_width=2.2),
                )
            )
            shapes.append(
                ftcanvas.Line(
                    C + cx, C + cy,
                    C + cx + math.cos(a) * R * 1.15, C + cy + math.sin(a) * R * 1.15,
                    paint=ft.Paint(color=A(MAGENTA, 0.6), stroke_width=1.4),
                )
            )
            for i in range(12):
                a2 = self.rot_fast * 1.7 + i * math.tau / 12
                rr = R * (0.9 + 0.12 * math.sin(self.t * 6.0 + i * 0.7))
                mx = C + cx + math.cos(a2) * rr
                my = C + cy + math.sin(a2) * rr
                col = [MAGENTA, ICE, CYAN][i % 3]
                shapes.append(
                    ftcanvas.Circle(mx, my, 1.4 + 0.4 * math.sin(self.t * 8 + i),
                                    paint=ft.Paint(color=A(col, 0.8)))
                )

        elif st == SPEAKING:
            # voice-reactive: waveform ring + energy echoes + flaring core
            energy = sum(self.wf) / len(self.wf)
            for k in range(3):
                ph = (self.t * 1.4 + k / 3.0 + energy * 0.4) % 1.0
                rr = R * (0.5 + 0.55 * ph)
                al = 0.4 * (1.0 - ph) * (0.6 + 0.4 * energy)
                shapes.append(
                    ftcanvas.Circle(
                        C + cx, C + cy, rr,
                        paint=ft.Paint(color=A(ROSE if k % 2 else CYAN, al), style=ft.PaintingStyle.STROKE, stroke_width=1.4),
                    )
                )
            n = len(self.wf)
            for i in range(n):
                a = i * math.tau / n + self.rot1 * 0.5
                rr = R * 0.62 + self.wf[i] * R * 0.28
                mx = C + cx + math.cos(a) * rr
                my = C + cy + math.sin(a) * rr
                col = ROSE if i % 2 == 0 else ICE
                shapes.append(
                    ftcanvas.Circle(mx, my, 2.6, paint=ft.Paint(color=A(col, 0.9)))
                )
            for i in range(6):
                a = self.rot_fast * 0.8 + i * math.tau / 6
                rr = R * 0.55 + energy * R * 0.2
                shapes.append(
                    ftcanvas.Circle(
                        C + cx + math.cos(a) * rr, C + cy + math.sin(a) * rr,
                        1.8 + energy * 2.2, paint=ft.Paint(color=A(ICE, 0.6 + 0.4 * energy)),
                    )
                )

        elif st == EXECUTING:
            prog = max(0.0, min(1.0, self.state.progress))
            a0 = -math.pi / 2
            sweep = prog * math.tau
            shapes.append(
                ftcanvas.Arc(
                    C + cx - R * 0.9, C + cy - R * 0.9, R * 1.8, R * 1.8,
                    a0, sweep, use_center=False,
                    paint=ft.Paint(color=A(GREEN, 0.95), style=ft.PaintingStyle.STROKE, stroke_width=3.0),
                )
            )
            ea = a0 + sweep
            shapes.append(
                ftcanvas.Circle(
                    C + cx + math.cos(ea) * R * 0.9, C + cy + math.sin(ea) * R * 0.9, 4.0,
                    paint=ft.Paint(color=A(WHITE, 1.0)),
                )
            )

        # ---- shared layers ----
        tech_r = R * 1.18
        shapes.append(
            ftcanvas.Circle(
                C + cx, C + cy, tech_r,
                paint=ft.Paint(color=A(accent, 0.2), style=ft.PaintingStyle.STROKE, stroke_width=0.9),
            )
        )
        for i in range(32):
            a = i * math.tau / 32
            mx = C + cx + math.cos(a) * tech_r
            my = C + cy + math.sin(a) * tech_r
            shapes.append(ftcanvas.Circle(mx, my, 1.1, paint=ft.Paint(color=A(accent, 0.10))))
        for i in range(4):
            a = self.rot2 + i * math.tau / 4
            mx = C + cx + math.cos(a) * tech_r
            my = C + cy + math.sin(a) * tech_r
            shapes.append(ftcanvas.Circle(mx, my, 1.9, paint=ft.Paint(color=A(accent, 0.55))))

        n_orb = max(8, int(24 * self.state.settings["particles"]))
        for i in range(n_orb):
            o = self.orbiters[i % len(self.orbiters)]
            a = o["ang"] + self.rot1 * o["sp"]
            rr = R * o["rad"] + 4 * math.sin(self.t * o["sp2"] + o["ph"])
            depth = 0.5 + 0.5 * math.sin(a)
            mx = C + cx + math.cos(a) * rr
            my = C + cy + math.sin(a) * rr
            al = 0.2 + 0.45 * (0.5 + 0.5 * math.sin(self.t * o["sp2"] * 2 + o["ph"]))
            shapes.append(ftcanvas.Circle(mx, my, o["r"] * (0.5 + 0.5 * depth), paint=ft.Paint(color=A(o["col"], al))))

        # core center — arc reactor style, state-colored
        sr = R * (0.74 + 0.05 * breath) * pulse
        core_col = accent if st not in (IDLE,) else CYAN
        try:
            grad = ft.Paint(
                gradient=ft.PaintRadialGradient(
                    center=ft.Offset(0.45, 0.42),
                    radius=1.0,
                    colors=["#00ffffff", A(core_col, 0.5), A(core_col, 0.16), A(core_col, 0.0)],
                )
            )
            shapes.append(ftcanvas.Circle(C + cx, C + cy, sr, paint=grad))
        except Exception:
            shapes.append(ftcanvas.Circle(C + cx, C + cy, sr, paint=ft.Paint(color=A(core_col, 0.06))))
        shapes.append(
            ftcanvas.Circle(
                C + cx, C + cy, sr,
                paint=ft.Paint(color=A(WHITE if st in (THINKING, SPEAKING) else core_col, 0.3),
                               style=ft.PaintingStyle.STROKE, stroke_width=1.2),
            )
        )
        shapes.append(
            ftcanvas.Circle(C + cx, C + cy, sr * 0.55, paint=ft.Paint(color=A(WHITE, 0.10 + 0.09 * breath)))
        )
        if st == SPEAKING:
            energy = sum(self.wf) / len(self.wf)
            shapes.append(
                ftcanvas.Circle(C + cx, C + cy, sr * 0.7 + energy * R * 0.1, paint=ft.Paint(color=A(WHITE, 0.9)))
            )

        if st in (THINKING, EXECUTING):
            for i in range(2):
                a = self.rot_fast * (1 if i == 0 else -0.7) + i * math.pi
                paint = ft.Paint(
                    color=A(WHITE, 0.5 if st == THINKING else 0.3),
                    style=ft.PaintingStyle.STROKE,
                    stroke_width=2.2,
                )
                shapes.append(
                    ftcanvas.Arc(
                        C + cx - R * 0.92, C + cy - R * 0.92, R * 1.84, R * 1.84,
                        a, 0.7, use_center=False, paint=paint,
                    )
                )

        if st != IDLE:
            sy = (self.t * 22) % self.cs
            shapes.append(
                ftcanvas.Line(
                    0, sy, self.cs, sy,
                    paint=ft.Paint(color=A(accent, 0.05), stroke_width=0.8),
                )
            )

        halo = 10 + 4 * breath
        shapes.append(ftcanvas.Circle(C + cx, C + cy, halo, paint=ft.Paint(color=A(accent, 0.30))))
        shapes.append(ftcanvas.Circle(C + cx, C + cy, 4.5 + 1.5 * breath, paint=ft.Paint(color=A(WHITE, 0.95))))
        if st in (THINKING, EXECUTING):
            dhalf = R * 0.46
            for k in range(4):
                ang = self.rot_fast * 0.6 + k * math.pi / 2
                dx = math.cos(ang) * dhalf
                dy = math.sin(ang) * dhalf
                shapes.append(
                    ftcanvas.Line(
                        C + cx - dx * 0.75, C + cy - dy * 0.75, C + cx + dx * 0.75, C + cy + dy * 0.75,
                        paint=ft.Paint(color=A(accent, 0.22), stroke_width=0.9),
                    )
                )

        self.canvas.shapes = shapes
        self.set_state_visual()
        self.holder.opacity = min(1.0, max(0.0, self.power))
        gx = self.parallax_x
        gy = self.parallax_y
        self.glow_outer.left = int(self.canvas_left - self.radius * 0.55) + int(gx * 0.6)
        self.glow_outer.top = int(self.canvas_top - self.radius * 0.55) + int(gy * 0.6)
        self.ghost_ring.left = int(self.canvas_left - self.radius * 0.18) - int(gx * 1.4)
        self.ghost_ring.top = int(self.canvas_top - self.radius * 0.18) - int(gy * 1.4)

    def update(self):
        self.canvas.update()
        self.holder.update()
        self.glow_outer.update()
        self.ghost_ring.update()
        self.status.update()
        self.pct.update()
