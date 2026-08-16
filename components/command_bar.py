import flet as ft

from app.theme import CYAN, ICE, WHITE, DIM, PANEL, VIOLET, rgba, FONT


class CommandBar:
    def __init__(self, app):
        self.app = app
        self.field = ft.TextField(
            hint_text="ASK JARVIS ANYTHING...",
            hint_style=ft.TextStyle(
                color=rgba(ICE, 0.45),
                font_family=FONT,
                letter_spacing=2.0,
                size=12,
            ),
            text_style=ft.TextStyle(color=WHITE, font_family=FONT, letter_spacing=1.0, size=13),
            cursor_color=CYAN,
            border=ft.InputBorder.NONE,
            content_padding=ft.Padding.symmetric(vertical=12, horizontal=16),
            bgcolor="#00000000",
            on_submit=self._submit,
            on_focus=self._focus,
            on_blur=self._blur,
        )
        self.mic = ft.IconButton(
            icon=ft.Icons.MIC,
            icon_color=ICE,
            icon_size=20,
            on_click=lambda e: self.app.voice_toggle(),
            tooltip="Voice input",
        )
        power_icon = getattr(ft.Icons, "POWER_SETTINGS_NEW", ft.Icons.POWER)
        self.shut = ft.IconButton(
            icon=power_icon,
            icon_color=rgba(DIM, 0.8),
            icon_size=18,
            on_click=lambda e: self.app.start_shutdown(),
            tooltip="Shut down JARVIS",
        )
        self.wrap = ft.Container(
            content=ft.Stack(
                [
                    ft.Row(
                        [
                            self.field,
                            self.mic,
                            self.shut,
                        ],
                        spacing=2,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(
                        left=2, top=0, right=2, height=1,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1.0, 0.0),
                            end=ft.Alignment(1.0, 0.0),
                            colors=["#00000000", rgba(CYAN, 0.55), "#00000000"],
                        ),
                    ),
                ]
            ),
            width=620,
            height=48,
            border_radius=6,
            bgcolor=rgba("#020c1b", 0.85),
            border=ft.Border.all(1, rgba(CYAN, 0.35)),
            shadow=[
                ft.BoxShadow(blur_radius=28, color=rgba(CYAN, 0.16)),
                ft.BoxShadow(blur_radius=70, color=rgba(CYAN, 0.05), offset=ft.Offset(0, 8)),
            ],
            padding=ft.Padding.only(left=6, right=6),
        )
        self.hint = ft.Text(
            "ENTER // SUBMIT      ESC // CLEAR      CTRL+M // VOICE      CTRL+Q // SHUTDOWN      F11 // FULLSCREEN      1-8 // MODULES",
            size=8,
            style=ft.TextStyle(color=rgba(DIM, 0.7), font_family=FONT, letter_spacing=1.6),
        )
        self.root = ft.Container(
            content=ft.Column(
                [self.wrap, self.hint],
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    def _submit(self, e):
        text = self.field.value
        self.field.value = ""
        self.field.update()
        if text and text.strip():
            self.app.run_command(text)

    def _focus(self, e):
        self.wrap.border = ft.Border.all(1, rgba(CYAN, 0.8))
        self.wrap.shadow = [ft.BoxShadow(blur_radius=36, spread_radius=2, color=rgba(CYAN, 0.3))]

    def _blur(self, e):
        self.wrap.border = ft.Border.all(1, rgba(CYAN, 0.25))
        self.wrap.shadow = [ft.BoxShadow(blur_radius=24, color=rgba(CYAN, 0.12))]

    def layout(self, w, h):
        self.wrap.width = min(620, int(w * 0.52))
        self.root.left = int(w / 2 - self.wrap.width / 2)
        self.root.top = int(h * 0.915)
