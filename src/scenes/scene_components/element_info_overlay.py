import pygame as pg
from src.utils import GameSettings
from src.interface.components import Overlay, Text, Button, Frame

class ElementInfoOverlay(Overlay):
    def __init__(self):
        self.px = GameSettings.SCREEN_WIDTH // 2 - 200
        self.py = GameSettings.SCREEN_HEIGHT // 2 - 250
        
        super().__init__(
            "UI/raw/UI_Flat_Frame02a.png",
            self.px, self.py, 400, 500,
            180,
            default_display=False,
            components=[],
            exit_key=[pg.K_ESCAPE]
        )
        
        self.bg_components = [
            Text("Element Guide", "Minecraft.ttf", 30, self.px + 100, self.py + 30),
            
            # Water
            Frame("ingame_ui/element_water.png", self.px + 50, self.py + 80, 32, 32),
            Text("Water > Fire", "Minecraft.ttf", 24, self.px + 100, self.py + 85),
            
            # Fire
            Frame("ingame_ui/element_fire.png", self.px + 50, self.py + 130, 32, 32),
            Text("Fire > Grass", "Minecraft.ttf", 24, self.px + 100, self.py + 135),
            
            # Grass
            Frame("ingame_ui/element_grass.png", self.px + 50, self.py + 180, 32, 32),
            Text("Grass > Water", "Minecraft.ttf", 24, self.px + 100, self.py + 185),
            
            # Electric
            Frame("ingame_ui/element_electric.png", self.px + 50, self.py + 230, 32, 32),
            Text("Electric > Water", "Minecraft.ttf", 24, self.px + 100, self.py + 235),
            
            # Close Button
            Button(
                "UI/button_back.png", "UI/button_back_hover.png",
                self.px + 175, self.py + 440, 50, 50,
                lambda: self.display(False)
            )
        ]
        
    def display(self, show: bool):
        if show:
            self.components = list(self.bg_components)
        super().display(show)
