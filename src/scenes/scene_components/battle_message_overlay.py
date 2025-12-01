import pygame as pg

from src.interface.components import Overlay, Text

def create_battle_message_overlay(message):
    overlay_width = 1280
    overlay_height = 200
    overlay_x = 0
    overlay_y = 520

    message_text = Text(
        message,
        "Minecraft.ttf",
        30, overlay_x + 100, overlay_y + 60
    )

    overlay_components = [message_text]

    overlay = Overlay(
        "UI/raw/UI_Flat_Frame01a.png",
        overlay_x, overlay_y,
        overlay_width, overlay_height,
        0,
        default_display=False,
        components=overlay_components,
    )

    return overlay
