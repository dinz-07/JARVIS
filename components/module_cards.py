import flet as ft

from app.theme import CYAN, ICE, WHITE, DIM, PANEL, VIOLET, rgba, label, FONT

MODULE_ICONS = {
    "SYSTEM": "MONITOR",
    "WEATHER": "CLOUD",
    "CALENDAR": "EVENT",
    "TASKS": "LIST_ALT",
    "MUSIC": "MUSIC_NOTE",
    "EMAIL": "MAIL",
    "SECURITY": "SECURITY",
    "BROWSER": "LANGUAGE",
}

CARD_COLS = {
    "SYSTEM": 0, "WEATHER": 1, "CALENDAR": 2, "TASKS": 3,
    "MUSIC": 4, "EMAIL": 5, "SECURITY": 6, "BROWSER": 7,
}

LEFT_XS = [0.155, 0.095, 0.095, 0.155]
RIGHT_XS = [0.845, 0.905, 0.905, 0.845]
YS = [0.325, 0.44, 0.555, 0.67]


def _icon(name):
    glyph = getattr(ft.Icons, name, None)
    if glyph is None:
        return None
    return ft.Icon(glyph, size=14, color=rgba(ICE, 0.55))


class ModuleCards:
    def __init__(self, state, on_open):
        self.state = state
        self.on_open = on_open
        self.cards = {}
        self.stack = ft.Stack(width=1600, height=900)
        self.container = ft.Container(content=self.stack, width=1600, height=900)
        for name in MODULE_ICONS:
            self.cards[name] = self._card(name)

    def _card(self, name):
        idx = CARD_COLS[name]
        num = ft.Container(
            content=ft.Text(
                f"{idx + 1:02d}", size=8,
                style=ft.TextStyle(color=rgba(CYAN, 0.9), font_family=FONT, letter_spacing=2),
            ),
            border_radius=3,
            padding=ft.Padding.symmetric(horizontal=5, vertical=2),
            bgcolor=rgba(CYAN, 0.08),
            border=ft.Border.all(1, rgba(CYAN, 0.25)),
        )
        title = ft.Text(
            name, size=15,
            style=ft.TextStyle(color=WHITE, font_family=FONT, letter_spacing=3.5, weight=ft.FontWeight.W_200),
        )
        icon = _icon(MODULE_ICONS[name])
        icon_tile = ft.Container(
            content=icon,
            width=30,
            height=30,
            border_radius=6,
            alignment=ft.Alignment.CENTER,
            bgcolor=rgba(CYAN, 0.09),
            border=ft.Border.all(1, rgba(CYAN, 0.22)),
            shadow=[ft.BoxShadow(blur_radius=10, color=rgba(CYAN, 0.25))],
        )
        body = ft.Container(
            content=ft.Stack(
                [
                    ft.Column(
                        [
                            ft.Row([num, ft.Container(expand=True), icon_tile], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.Container(expand=True),
                            title,
                        ],
                        spacing=2,
                    ),
                    ft.Container(
                        left=2, top=0, right=2, height=1,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1.0, 0.0),
                            end=ft.Alignment(1.0, 0.0),
                            colors=["#00ffffff", rgba(WHITE, 0.12), "#00ffffff"],
                        ),
                    ),
                ]
            ),
            width=150,
            height=88,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            border_radius=8,
            bgcolor=rgba("#020c1b", 0.72),
            border=ft.Border.all(1, rgba(CYAN, 0.22)),
            shadow=[
                ft.BoxShadow(blur_radius=18, color=rgba(CYAN, 0.10)),
                ft.BoxShadow(blur_radius=60, color=rgba(CYAN, 0.04), offset=ft.Offset(0, 8)),
            ],
        )
        gd = ft.GestureDetector(
            content=body,
            on_enter=lambda e, n=name: self._hover(n, True),
            on_exit=lambda e, n=name: self._hover(n, False),
            on_tap=lambda e, n=name: self.on_open(n),
        )
        return {
            "name": name,
            "body": body,
            "gd": gd,
            "hovered": False,
        }

    def _hover(self, name, on):
        c = self.cards[name]
        c["hovered"] = on
        body = c["body"]
        if on:
            body.scale = 1.08
            body.rotate = -0.05
            body.border = ft.Border.all(1, rgba(CYAN, 0.65))
            body.shadow = [
                ft.BoxShadow(blur_radius=36, spread_radius=4, color=rgba(CYAN, 0.35)),
                ft.BoxShadow(blur_radius=80, color=rgba(CYAN, 0.1), offset=ft.Offset(0, 10)),
            ]
        else:
            body.scale = 1.0
            body.rotate = 0.0
            body.border = ft.Border.all(1, rgba(CYAN, 0.22))
            body.shadow = [
                ft.BoxShadow(blur_radius=18, color=rgba(CYAN, 0.10)),
                ft.BoxShadow(blur_radius=60, color=rgba(CYAN, 0.04), offset=ft.Offset(0, 8)),
            ]

    def layout(self, w, h):
        compact = w < 1300
        for name, c in self.cards.items():
            body = c["body"]
            i = CARD_COLS[name]
            if compact:
                cw = 108
                ch = 60
                total = 8 * cw + 7 * 10
                x = w / 2 - total / 2 + i * (cw + 10)
                y = h * 0.84
            else:
                cw = 150
                ch = 88
                if i < 4:
                    x = w * LEFT_XS[i]
                    y = h * YS[i]
                else:
                    x = w * RIGHT_XS[i - 4]
                    y = h * YS[i - 4]
            body.width = cw
            body.height = ch
            c["gd"].left = int(x - cw / 2)
            c["gd"].top = int(y - ch / 2)
        self.container.width = w
        self.container.height = h
        self.stack.width = w
        self.stack.height = h

    def add_all(self):
        for c in self.cards.values():
            self.stack.controls.append(c["gd"])
