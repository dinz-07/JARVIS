import flet as ft

from app.theme import CYAN, ICE, WHITE, DIM, rgba, FONT


class Hologram:
    def __init__(self, state):
        self.state = state
        self.user_text = ft.Text(
            "", size=11, style=ft.TextStyle(color=rgba(DIM, 0.9), font_family=FONT, letter_spacing=1.6, italic=True),
            text_align=ft.TextAlign.CENTER,
        )
        self.resp_text = ft.Text(
            "", size=14, style=ft.TextStyle(color=ICE, font_family=FONT, letter_spacing=0.8, weight=ft.FontWeight.W_200),
            text_align=ft.TextAlign.CENTER,
        )
        self.root = ft.Container(
            content=ft.Column(
                [self.user_text, self.resp_text],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=720,
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=34, vertical=20),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0.5, -1.0),
                end=ft.Alignment(0.5, 1.0),
                colors=[rgba("#0d1a26", 0.75), rgba("#060b12", 0.6)],
            ),
            border=ft.Border.all(1, rgba(CYAN, 0.22)),
            shadow=[ft.BoxShadow(blur_radius=40, color=rgba(CYAN, 0.16))],
            opacity=0.0,
            visible=False,
        )
        self.timer = 0.0

    def show(self, user, response, duration=7.0):
        self.user_text.value = user
        self.resp_text.value = response
        self.root.visible = True
        self.root.opacity = 0.0
        self.state.tween(self.root, "opacity", 1.0, duration=0.45)
        self.timer = duration

    def layout(self, w, h):
        self.root.width = min(760, int(w * 0.52))
        self.root.left = int(w / 2 - self.root.width / 2)
        self.root.top = int(h * 0.12)

    def tick(self, dt):
        if self.root.visible and self.root.opacity > 0.99:
            self.timer -= dt
            if self.timer <= 0:
                self.state.tween(self.root, "opacity", 0.0, duration=0.5)
                self.root.visible = False
