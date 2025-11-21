from __future__ import annotations
import pygame as pg

from src.sprites import Sprite
from src.core.services import input_manager
from typing import Callable, override
from .component import UIComponent

class Frame(UIComponent):
    img: Sprite
    rect: pg.Rect
    
    def __init__(
            self,
            img_path: str, 
            x: int, y: int, width: int, height: int
        ):
        super().__init__()

        self.hitbox = pg.Rect(x, y, width, height)
        self.img = Sprite(img_path, (width, height))

    @override
    def update(self, dt):
        return super().update(dt)
    
    @override
    def draw(self, screen):
        screen.blit(self.img.image, self.hitbox)