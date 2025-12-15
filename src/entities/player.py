from __future__ import annotations
import pygame as pg
from .entity import Entity
from src.core.services import input_manager, scene_manager
from src.utils import Position, PositionCamera, GameSettings, Logger, Direction
from src.interface.components import Overlay, Text
from src.core import GameManager
from typing import override

class Player(Entity):
    speed: float = 350.0
    game_manager: GameManager
    catch_message: Overlay

    def __init__(self, x: float, y: float, game_manager: GameManager) -> None:
        super().__init__(x, y, game_manager)
        self.is_teleporting = False
        
        catch_text = Text(
            "Found a pokemon! Press C to catch",
            "Minecraft.ttf",
            30, 150, 550
        )
        self.catch_message = Overlay(
            "UI/raw/UI_Flat_Frame01a.png",
            0, 0, 800, 200, 0,
            False,
            [catch_text]
        )

    @override
    def update(self, dt: float) -> None:
        dis = Position(0, 0)

        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            self.direction = Direction.LEFT
            dis.x -= 1
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            self.direction = Direction.RIGHT
            dis.x += 1
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            self.direction = Direction.UP
            dis.y -= 1
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            self.direction = Direction.DOWN
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

        player_rect = pg.Rect(int(self.position.x), int(self.position.y), GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        if self.game_manager.check_bush(player_rect):
            if not hasattr(self, "_waiting_to_catch"):
                self._waiting_to_catch = True
            else:
                keys = pg.key.get_pressed()
                message_x = 200
                message_y = 600
                catch_text = Text(
                    "Found a pokemon! Press C to catch",
                    "Minecraft.ttf",
                    30, message_x + 40, message_y + 25
                )
                self.catch_message = Overlay(
                    "UI/raw/UI_Flat_Frame01a.png",
                    message_x, message_y, 800, 100, 0,
                    False,
                    [catch_text]
                )
                self.catch_message.display(True)
                if keys[pg.K_c]:
                    self.game_manager.save()
                    scene_manager.change_scene("catch")
        else:
            self._waiting_to_catch = False
            self.catch_message.display(False)

        super().update(dt)

    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        self.catch_message.draw(screen)
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

