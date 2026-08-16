import flet as ft

from app.theme import CYAN, ICE, WHITE, DIM, rgba, FONT


class ActivityStream:
    def __init__(self, state):
        self.state = state
        self.title = ft.Text(
            "ACTIVITY STREAM",
            size=9,
            style=ft.TextStyle(color=rgba(ICE, 0.6), font_family=FONT, letter_spacing=3.0),
        )
        self.rows = ft.Column(spacing=5)
        self.root = ft.Container(
            content=ft.Column(
                [self.title, self.rows],
                spacing=8,
            ),
            width=190,
            padding=ft.Padding.all(10),
            border_radius=4,
            bgcolor=rgba("#0a1118", 0.35),
            border=ft.Border.all(1, rgba(CYAN, 0.10)),
        )
        self.last_version = -1

    def layout(self, w, h):
        self.root.left = int(w * 0.742)
        self.root.top = int(h * 0.315)

    def tick(self):
        if self.state.activity_version == self.last_version:
            return
        self.last_version = self.state.activity_version
        self.rows.controls = []
        for ts, text in list(self.state.activity)[:7]:
            row = ft.Row(
                [
                    ft.Text(ts, size=8, style=ft.TextStyle(color=rgba(DIM, 0.8), font_family=FONT, letter_spacing=1.0)),
                    ft.Container(width=4, height=4, border_radius=2, bgcolor=rgba(CYAN, 0.5)),
                    ft.Text(text, size=8.5, style=ft.TextStyle(color=rgba(ICE, 0.85), font_family=FONT, letter_spacing=1.2)),
                ],
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            self.rows.controls.append(row)
        self.rows.update()
