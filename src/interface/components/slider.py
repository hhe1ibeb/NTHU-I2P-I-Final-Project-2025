from __future__ import annotations
import pygame as pg

from src.sprites import Sprite
from src.core.services import input_manager
from src.utils import Logger, GameSettings
from typing import Callable, override
from .component import UIComponent

class Slider(UIComponent):
    max_value: float
    value: float
    img_bar: Sprite
    bar_rect: pg.Rect
    img_handle: Sprite
    handle_rect: pg.Rect
    is_dragging: bool
    on_change: Callable[[float], None]

    @staticmethod
    def pointInRectanlge(px, py, rw, rh, rx, ry):
        if px > rx and px < rx  + rw:
            if py > ry and py < ry + rh:
                return True
        return False
    
    def __init__(
            self,
            bar_img: str, handle_img: str,
            x, y, bar_width, bar_height, handle_width, handle_height,
            current_value: float, max_value: float,
            on_change: Callable[[float], None] = lambda v: None
        ):
        super().__init__()
        self.value = current_value
        self.max_value = max_value
        self.img_bar = Sprite(bar_img, (bar_width, bar_height))
        self.img_handle = Sprite(handle_img, (handle_width, handle_height))
        self.bar_rect = pg.Rect(x, y, bar_width, bar_height)
        handle_x = x + bar_width * (current_value / max_value) - handle_width / 2
        handle_y = y - handle_height / 3
        self.handle_rect = pg.Rect(handle_x, handle_y, handle_width, handle_height)
        self.is_dragging = False
        self.on_change = on_change

    def handle_input(self):
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]
        
        if mouse_pressed:
            if self.bar_rect.collidepoint(mouse_pos) or self.handle_rect.collidepoint(mouse_pos):
                self.is_dragging = True
        else:
            self.is_dragging = False

        if self.is_dragging:
            # 1. Move handle to mouse X
            self.handle_rect.centerx = mouse_pos[0]

            # 2. Clamp handle to bar boundaries
            if self.handle_rect.centerx < self.bar_rect.left:
                self.handle_rect.centerx = self.bar_rect.left
            elif self.handle_rect.centerx > self.bar_rect.right:
                self.handle_rect.centerx = self.bar_rect.right

            # 3. Calculate new value (Ratio: 0.0 to 1.0)
            # Distance from left edge / Total width
            relative_x = self.handle_rect.centerx - self.bar_rect.left
            ratio = relative_x / self.bar_rect.width
            
            new_value = ratio * self.max_value
            
            # 4. Only update if value actually changed (optimization)
            if self.value != new_value:
                self.value = new_value
                self.on_change(self.value)

    @override
    def update(self, dt):
        self.handle_input()
    
    @override
    def draw(self, screen):
        screen.blit(self.img_bar.image, self.bar_rect)
        screen.blit(self.img_handle.image, self.handle_rect)