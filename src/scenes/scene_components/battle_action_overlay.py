import pygame as pg

from src.interface.components import Button, Overlay, Text

def create_battle_action_overlay(on_attack, on_run):
    button_width = 200
    button_height = 60
    overlay_width = 1280
    overlay_height = 200
    overlay_x = 0
    overlay_y = 520

    # Button positions
    attack_x = overlay_x + 500
    attack_y = overlay_y + 60

    run_x = overlay_x + 760
    run_y = overlay_y + 60

    message_text = Text(
        "Pick your move",
        "Minecraft.ttf",
        30, overlay_x + 100, overlay_y + 60
    )

    attack_button = Button(
        "UI/raw/UI_Flat_Button01a_2.png",
        "UI/raw/UI_Flat_Button01a_1.png",
        attack_x,
        attack_y,
        button_width,
        button_height,
        on_attack
    )
    attack_text = Text(
        "Attack",
        "Minecraft.ttf",
        30, 
        attack_x + 50, 
        attack_y + 25
    )

    run_button = Button(
        "UI/raw/UI_Flat_Button01a_2.png",
        "UI/raw/UI_Flat_Button01a_1.png",
        run_x,
        run_y,
        button_width,
        button_height,
        on_run
    )
    run_text = Text(
        "Run",
        "Minecraft.ttf",
        30, 
        run_x + 60, 
        run_y + 25
    )

    overlay_components = [message_text, attack_button, attack_text, run_button, run_text]

    overlay = Overlay(
        "UI/raw/UI_Flat_Frame01a.png",
        overlay_x, overlay_y,
        overlay_width, overlay_height,
        0,
        default_display=False,
        components=overlay_components
    )

    return overlay
