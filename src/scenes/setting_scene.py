from __future__ import annotations
import pygame as pg

from src.utils import GameSettings
from src.sprites import BackgroundSprite
from src.core.services import scene_manager, sound_manager, input_manager
from src.interface.components import Button

class SettingScene:
    exit_button: Button
    def __init__(self) -> None:
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background2.png")

        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 3 // 4
        self.exit_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px, py, 100, 100,
            lambda: scene_manager.change_scene("menu")
        )

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def update(self, dt: float) -> None:
        self.exit_button.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        self.exit_button.draw(screen)