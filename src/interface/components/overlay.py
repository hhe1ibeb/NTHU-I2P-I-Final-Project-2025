from __future__ import annotations
import pygame as pg

from src.sprites import Sprite
from src.core.services import input_manager, resource_manager
from src.utils import Logger, GameSettings, Key
from typing import Callable, override, List
from .component import UIComponent
from src.interface.components import Button

class Overlay(UIComponent):
    overlay_screen: pg.Surface
    overlay_img: pg.Surface
    overlay_img_rect: pg.Rect
    is_display = False
    components: List[UIComponent]
    exit_key: List[Key]

    def __init__(
            self,
            img_path: str,
            x: int, y: int, width: int, height: int,
            alpha_value: int, 
            default_display: bool,
            components: List[UIComponent] = None,
            exit_key: List[Key] = None
        ):
        super().__init__()
        self.overlay_screen = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        self.overlay_screen.fill((0, 0, 0))
        self.overlay_screen.set_alpha(alpha_value)

        self.overlay_img = resource_manager.get_image(img_path)
        self.overlay_img = pg.transform.scale(self.overlay_img, (width, height))
        self.overlay_img_rect = pg.Rect(x, y, width, height)

        self.components = components

        self.is_display = default_display
        self.exit_key = exit_key
        
    @override
    def update(self, dt):
        if self.is_display:
            if self.exit_key:
                for possible_key in self.exit_key:
                    if input_manager.key_down(possible_key):
                        self.display(False)
            if self.components:
                for component in self.components:
                    component.update(dt)
        return super().update(dt)
    
    @override
    def draw(self, screen):
        if self.is_display:
            screen.blit(self.overlay_screen, (0, 0))
            screen.blit(self.overlay_img, self.overlay_img_rect)
            if self.components:
                for component in self.components:
                    component.draw(screen)


    def display(self, state: bool):
        self.is_display = state