from __future__ import annotations
import pygame as pg
from .entity import Entity
from src.core.services import input_manager
from src.utils import Position, PositionCamera, GameSettings, Logger
from src.core import GameManager
import math
from typing import override

class Player(Entity):
    speed: float = 400.0
    game_manager: GameManager

    def __init__(self, x: float, y: float, game_manager: GameManager) -> None:
        super().__init__(x, y, game_manager)
        self.is_teleporting = False

    @override
    def update(self, dt: float) -> None:
        dis = Position(0, 0)
        '''
        [TODO HACKATHON 2]
        Calculate the distance change, and then normalize the distance

        [TODO HACKATHON 4]
        Check if there is collision, if so try to make the movement smooth
        Hint #1 : use entity.py _snap_to_grid function or create a similar function
        Hint #2 : Beware of glitchy teleportation, you must do
                    1. Update X
                    2. If collide, snap to grid
                    3. Update Y
                    4. If collide, snap to grid
                  instead of update both x, y, then snap to grid
        
        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= ...
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += ...
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= ...
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += ...
        
        self.position = ...
        '''

        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= 1
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += 1
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= 1
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += 1

        if dis.x != 0 or dis.y != 0:
            dis_mag = (dis.x ** 2 + dis.y ** 2) ** 0.5 

            move_x = (dis.x * self.speed * dt) / dis_mag
            move_y = (dis.y * self.speed * dt) / dis_mag

            self.position.x += move_x
            player_rect = pg.Rect(int(self.position.x), int(self.position.y), GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)

            if self.game_manager.check_collision(player_rect):
                if move_x > 0:
                    self.position.x = (player_rect.x // GameSettings.TILE_SIZE) * GameSettings.TILE_SIZE
                if move_x < 0:
                    self.position.x = (player_rect.x // GameSettings.TILE_SIZE + 1) * GameSettings.TILE_SIZE

                player_rect.x = self.position.x

            self.position.y += move_y
            player_rect.y = int(self.position.y)
            if self.game_manager.check_collision(player_rect):
                if move_y > 0:
                    self.position.y = (player_rect.y // GameSettings.TILE_SIZE) * GameSettings.TILE_SIZE
                if move_y < 0:
                    self.position.y = (player_rect.y // GameSettings.TILE_SIZE + 1) * GameSettings.TILE_SIZE

        # Check teleportation
        tp = self.game_manager.current_map.check_teleport(self.position)
        if tp:
            pos_now = None
            if self.game_manager.current_map_key == "map.tmx":
                pos_now = self.position
            if not self.is_teleporting:
                self.is_teleporting = True
                dest = tp.destination
                self.game_manager.switch_map(dest, pos_now)
                return
        else:
            self.is_teleporting = False
                
        super().update(dt)

    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        
    @override
    def to_dict(self) -> dict[str, object]:
        return super().to_dict()
    
    @property
    @override
    def camera(self) -> PositionCamera:
        ideal_x = int(self.position.x) - GameSettings.SCREEN_WIDTH // 2
        ideal_y = int(self.position.y) - GameSettings.SCREEN_HEIGHT // 2
        map_width = self.game_manager.current_map._surface.get_width()
        map_height = self.game_manager.current_map._surface.get_height()
        clamped_x = max(0, min(ideal_x, map_width - GameSettings.SCREEN_WIDTH))
        clamped_y = max(0, min(ideal_y, map_height - GameSettings.SCREEN_HEIGHT))
        return PositionCamera(clamped_x, clamped_y)
            
    @classmethod
    @override
    def from_dict(cls, data: dict[str, object], game_manager: GameManager) -> Player:
        return cls(data["x"] * GameSettings.TILE_SIZE, data["y"] * GameSettings.TILE_SIZE, game_manager)

