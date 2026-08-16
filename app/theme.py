import flet as ft

BG = "#01060d"
BG_DEEP = "#000000"
PANEL = "#020c1b"
PANEL_2 = "#041226"
LINE = "#0a2a44"
LINE_2 = "#0f3a5e"
CYAN = "#00f0ff"
ICE = "#b8f4ff"
VIOLET = "#5ea9ff"
MAGENTA = "#7df9ff"
ROSE = "#4df5ff"
GOLD = "#ffe08a"
TEAL = "#2dd4bf"
WHITE = "#ffffff"
DIM = "#8fa8c4"
FAINT = "#0e2b42"
RED = "#ff4a6a"
GREEN = "#00ff88"
AMBER = "#ffc44d"

FONT = "Exo 2"
FONT_HEAD = "Orbitron"


def rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    a = format(round(max(0.0, min(1.0, alpha)) * 255), "02x")
    return f"#{a}{r}{g}{b}"


def panel_gradient(top: str = "#020c1b", alpha: float = 0.92, direction: str = "down") -> ft.LinearGradient:
    if direction == "up":
        colors = ["#00000000", rgba(top, alpha)]
        begin, end = ft.Alignment(0.5, 1.0), ft.Alignment(0.5, 0.0)
    elif direction == "diag":
        colors = [rgba(top, alpha), rgba(PANEL_2, 0.55), "#00000000"]
        begin, end = ft.Alignment(-1.0, -1.0), ft.Alignment(1.0, 1.0)
    else:
        colors = [rgba(top, alpha), rgba(PANEL, 0.85), rgba(BG_DEEP, 0.92)]
        begin, end = ft.Alignment(0.5, -1.0), ft.Alignment(0.5, 1.0)
    return ft.LinearGradient(begin=begin, end=end, colors=colors)


def glow(color: str, blur: float = 28.0, spread: float = 2.0, alpha: float = 0.55, x: float = 0.0, y: float = 0.0) -> ft.BoxShadow:
    return ft.BoxShadow(
        spread_radius=spread,
        blur_radius=blur,
        color=rgba(color, alpha),
        offset=ft.Offset(x, y),
    )


def anim(duration: int = 320, curve=ft.AnimationCurve.EASE_OUT) -> ft.Animation:
    return ft.Animation(duration, curve)


def _style(color: str = DIM, spacing: float = 0.0, weight=ft.FontWeight.W_400, italic: bool = False):
    return ft.TextStyle(
        color=color,
        font_family=FONT,
        letter_spacing=spacing,
        weight=weight,
        italic=italic,
    )


def label(text: str, size: float = 10.0, color: str = DIM, spacing: float = 3.0, weight=ft.FontWeight.W_400) -> ft.Text:
    return ft.Text(text, size=size, style=_style(color, spacing, weight))


def value_text(text: str, size: float = 26.0, color: str = WHITE, spacing: float = 1.0) -> ft.Text:
    return ft.Text(text, size=size, style=_style(color, spacing, ft.FontWeight.W_200))


def head(text: str, size: float = 16.0, color: str = WHITE, spacing: float = 3.0, weight=ft.FontWeight.W_700) -> ft.Text:
    return ft.Text(text, size=size, style=ft.TextStyle(color=color, font_family=FONT_HEAD, letter_spacing=spacing, weight=weight))
