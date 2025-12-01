import pygame as pg

from src.utils import GameSettings
from src.core import GameManager, BattleManager
from src.core.services import sound_manager
from src.interface.components import Text, Overlay, Button, Frame
from src.sprites import Sprite

def create_selection_overlay(game_manager: GameManager, on_select_monster):
    monster_list = game_manager.bag.to_dict()["monsters"]

    overlay_components = []

    px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
    title_text = Text(
        "SELECT YOUR CHARACTER",
        "Minecraft.ttf",
        50, px - 350, py - 240
    )
    overlay_components.append(title_text)

    dx, dy = 0, 0
    for monster in monster_list:
        container = Button(
            "UI/raw/UI_Flat_Button01a_2.png","UI/raw/UI_Flat_Button01a_1.png",
            px - 450 + dx, py - 200 + dy, 200, 200,
            lambda m=monster: on_select_monster(m)
        )
        monster_img = Frame(
            monster["sprite_path"],
            px - 410 + dx, py - 190 + dy, 100, 100
        )
        level_text = Text(
            f"Level: {monster["level"]}",
            "Minecraft.ttf",
            20,
            px - 400 + dx, py - 80 + dy,
            color=(16, 96, 201)
        )
        hp_text = Text(
            f"HP: {monster["hp"]}/{monster["max_hp"]}",
            "Minecraft.ttf",
            20,
            px - 410 + dx, py - 50 + dy,
            color=(255, 62, 23)
        )
        dx += 230
        if dx >= 920:
            dx = 0
            dy += 220
        overlay_components.extend([container, monster_img, level_text, hp_text])

    selection_overlay = Overlay(
        "UI/raw/UI_Flat_Frame02a.png", 
        100, 50, 1100, 600,
        160,
        default_display=True,
        components=overlay_components,
    )
    
    return selection_overlay