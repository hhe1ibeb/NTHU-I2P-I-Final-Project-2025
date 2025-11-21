from __future__ import annotations
import pygame as pg

from src.sprites import Sprite
from src.core.services import input_manager
from src.utils import Logger
from typing import Callable, override
from .component import UIComponent

class Toggle(UIComponent):
    value: bool
    variable: Callable[[], None] | None
    img_toggle: Sprite
    img_toggle_on: Sprite
    img_toggle_off: Sprite
    hitbox: pg.Rect
    toggled_on: Callable[[], None] | None
    toggled_off: Callable[[], None] | None
    
    def __init__(
            self,
            img_off: str, img_on:str,
            x: int, y: int, width: int, height: int,
            variable: Callable[[], None], # on is true, off is false
            toggled_on: Callable[[], None],
            toggled_off: Callable[[], None]
        ):
        super().__init__()

        self.variable = variable
        self.value = variable
        self.hitbox = pg.Rect(x, y, width, height)
        self.img_toggle_off = Sprite(img_off, (width, height))
        self.img_toggle_on = Sprite(img_on, (width, height))
        self.img_toggle = self.img_toggle_on if self.value else self.img_toggle_off
        self.toggled_on = toggled_on
        self.toggled_off = toggled_off


    @override
    def update(self, dt):
        if self.hitbox.collidepoint(input_manager.mouse_pos):
            if input_manager.mouse_pressed(1) and self.toggled_on is not None and self.toggled_off is not None:
                self.value = not self.value
                self.toggled_on() if self.value else self.toggled_off()
        self.value = self.variable()
        self.img_toggle = self.img_toggle_on if self.value else self.img_toggle_off
    
    @override
    def draw(self, screen):
        _ = screen.blit(self.img_toggle.image, self.hitbox)