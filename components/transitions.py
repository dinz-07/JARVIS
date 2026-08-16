import flet as ft


def fade_in(control, duration=420, delay=0.0):
    control.opacity = 0.0
    return control


def pop_in(control, duration=420):
    control.opacity = 0.0
    control.scale = 0.86
    return control


def scene(core, cards, module, settings, overlay, active):
    core.root.opacity = 0.16 if active == "module" else (0.35 if active == "settings" else 1.0)
    core.root.scale = 0.62 if active == "module" else (0.9 if active == "settings" else 1.0)
    cards.container.opacity = 0.08 if active == "module" else 1.0
    cards.container.scale = 0.92 if active == "module" else 1.0
    module.opacity = 1.0 if active == "module" else 0.0
    module.scale = 1.0 if active == "module" else 0.9
    settings.opacity = 1.0 if active == "settings" else 0.0
    settings.scale = 1.0 if active == "settings" else 0.94
    overlay.opacity = 0.55 if active != "core" else 0.0
    overlay.visible = active != "core"
