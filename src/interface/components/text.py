from __future__ import annotations
import pygame as pg

from src.sprites import Sprite
from src.core.services import input_manager, resource_manager
from src.utils import Logger
from typing import Callable, override
from .component import UIComponent

class Text(UIComponent):
    content: str
    font: pg.font.Font
    position: tuple[int, int]
    color: tuple[int, int, int]
    is_dynamic: bool=False
    variable: Callable | None
    text: pg.Surface
    
    def __init__(
            self,
            content: str, 
            font: str, size: int,
            x: int, y: int,
            variable: Callable=None,
            color: tuple[int, int, int]=(0, 0, 0),
        ):
        super().__init__()

        self.font = resource_manager.get_font(font, size)
        self.content = content
        self.position = (x, y)
        self.color = color

        if variable is not None:
            self.is_dynamic = True
            self.variable = variable
        
        self.text = self.font.render(self.content, True, self.color)

    def update(self, dt):
        if self.is_dynamic:
            self.content = self.variable()
            self.text = self.font.render(self.content, True, self.color)
        return super().update(dt)
    
    @override
    def draw(self, screen):
        screen.blit(self.text, self.position)