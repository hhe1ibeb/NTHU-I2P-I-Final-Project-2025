import pygame as pg

from src.utils import GameSettings
from src.core import GameManager
from src.core.services import sound_manager
from src.interface.components import Text, Overlay, Button, Frame
from src.sprites import Sprite

def create_backpack_overlay(game_manager: GameManager):
    bag_dict = game_manager.bag.to_dict()
    monster_list, items_list = bag_dict["monsters"], bag_dict["items"]
    
    overlay_components = []

    px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
    backpack_text = Text(
        "BACKPACK",
        "Minecraft.ttf",
        50, px - 370, py - 190
    )
    overlay_components.append(backpack_text)

    monster_text = Text(
        "Monsters",
        "Minecraft.ttf",
        30, px - 370, py - 125,
        color=(60, 60, 60)
    )
    items_text = Text(
        "Items",
        "Minecraft.ttf",
        30, px + 100, py - 125,
        color=(60, 60, 60)
    )
    overlay_components.append(monster_text)
    overlay_components.append(items_text)

    dx, dy = 0, 0
    for monster in monster_list:
        container = Frame(
            "UI/raw/UI_Flat_Banner04a.png",
            px - 375 + dx, py - 90 + dy, 220, 60
        )
        monster_img = Frame(
            monster["sprite_path"],
            px - 360 + dx, py - 80 + dy, 40, 40
        )
        name_text = Text(
            monster["name"],
            "Minecraft.ttf",
            15,
            px - 315 + dx, py - 65 + dy
        )
        hp_text = Text(
            f"HP: {monster["hp"]}/{monster["max_hp"]}",
            "Minecraft.ttf",
            12,
            px - 235 + dx, py - 70 + dy,
            color=(255, 62, 23)
        )
        level_text = Text(
            f"Level: {monster["level"]}",
            "Minecraft.ttf",
            12,
            px - 235 + dx, py - 55 + dy,
            color=(16, 96, 201)
        )
        dy += 65
        if dy >= 260:
            dy = 0
            dx += 230
        overlay_components.extend([container, monster_img, name_text, hp_text, level_text])
        pass

    dy = 0
    for item in items_list:
        container = Frame(
            "UI/raw/UI_Flat_Banner04a.png",
            px + 100, py - 90 + dy, 300, 60
        )
        item_img = Frame(
            item["sprite_path"],
            px + 125, py - 75 + dy, 35, 35
        )
        item_text = Text(
            item["name"],
            "Minecraft.ttf",
            24,
            px + 170, py - 70 + dy
        )
        count_text = Text(
            f"x {item["count"]}",
            "Minecraft.ttf",
            24,
            px + 300, py - 70 + dy
        )
        dy += 65
        overlay_components.extend([container, item_img, item_text, count_text])

    exit_text = Text(
        "Press ESC to exit",
        "Minecraft.ttf",
        24, 
        px // 3 + 120, py // 3 + 435,
        color=(50, 50, 50)
    )
    overlay_components.append(exit_text)

    exit_button = Button(
        "UI/button_back.png", "UI/button_back_hover.png",
        px // 3 + 50, py // 3 + 420, 50, 50,
        lambda: backpack_overlay.display(False)
    )
    overlay_components.append(exit_button)
    
    backpack_overlay = Overlay(
        "UI/raw/UI_Flat_Frame03a.png", 
        px // 3, py // 3, 900, 500,
        160,
        default_display=False,
        components=overlay_components,
        exit_key=[pg.K_ESCAPE]
    )
    
    return backpack_overlay