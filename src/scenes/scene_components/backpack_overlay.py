import pygame as pg
from src.utils import GameSettings
from src.core.managers.game_manager import GameManager
from src.interface.components import Text, Overlay, Button, Frame

class BackpackOverlay(Overlay):
    def __init__(self, game_manager: GameManager):
        self.game_manager = game_manager
        self.px = GameSettings.SCREEN_WIDTH // 2
        self.py = GameSettings.SCREEN_HEIGHT // 2
        
        super().__init__(
            "UI/raw/UI_Flat_Frame03a.png", 
            self.px // 3, self.py // 3, 900, 500,
            160,
            default_display=False,
            components=[], 
            exit_key=[pg.K_ESCAPE]
        )
        
        self.static_components = self._create_static_ui()
        
        self.refresh_content()

    def display(self, show: bool):
        if show:
            self.refresh_content()
        super().display(show)

    def _create_static_ui(self):
        comps = []
        comps.append(Text("BACKPACK", "Minecraft.ttf", 50, self.px - 370, self.py - 190))
        comps.append(Text("Monsters", "Minecraft.ttf", 30, self.px - 370, self.py - 125, color=(60, 60, 60)))
        comps.append(Text("Items", "Minecraft.ttf", 30, self.px + 100, self.py - 125, color=(60, 60, 60)))
        comps.append(Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            self.px // 3 + 50, self.py // 3 + 420, 50, 50,
            lambda: self.display(False)
        ))
        return comps

    def refresh_content(self):
        self.components = self.static_components.copy()
        
        bag_dict = self.game_manager.bag.to_dict()
        monster_list = bag_dict["monsters"]
        items_list = bag_dict["items"]

        dx, dy = 0, 0
        for monster in monster_list:
            self.components.extend([
                Frame("UI/raw/UI_Flat_Banner04a.png", self.px - 375 + dx, self.py - 90 + dy, 220, 60),
                Frame(monster["sprite_path"], self.px - 360 + dx, self.py - 80 + dy, 40, 40),
                Text(monster["name"], "Minecraft.ttf", 15, self.px - 315 + dx, self.py - 65 + dy),
                Text(f"HP: {monster['hp']}/{monster['max_hp']}", "Minecraft.ttf", 12, self.px - 235 + dx, self.py - 70 + dy, color=(255, 62, 23)),
                Text(f"Level: {monster['level']}", "Minecraft.ttf", 12, self.px - 235 + dx, self.py - 55 + dy, color=(16, 96, 201))
            ])
            dy += 65
            if dy >= 260:
                dy = 0
                dx += 230

        dy = 0
        for item in items_list:
            if item["count"] <= 0:
                continue

            self.components.extend([
                Frame("UI/raw/UI_Flat_Banner04a.png", self.px + 100, self.py - 90 + dy, 300, 60),
                Frame(item["sprite_path"], self.px + 125, self.py - 75 + dy, 35, 35),
                Text(item["name"], "Minecraft.ttf", 24, self.px + 170, self.py - 70 + dy),
                Text(f"x {item['count']}", "Minecraft.ttf", 24, self.px + 300, self.py - 70 + dy)
            ])
            dy += 65