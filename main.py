import os
import flet as ft

from app.app import JarvisApp


def main(page: ft.Page) -> None:
    fonts = {}
    for name, path in (
        ("Orbitron", os.path.join("assets", "fonts", "Orbitron.ttf")),
        ("Exo 2", os.path.join("assets", "fonts", "Exo2.ttf")),
    ):
        if os.path.exists(path):
            fonts[name] = path
    if fonts:
        try:
            page.fonts = fonts
        except Exception:
            pass
    JarvisApp(page).run()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
