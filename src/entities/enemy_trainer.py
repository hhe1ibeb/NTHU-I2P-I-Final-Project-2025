from __future__ import annotations
import pygame
from enum import Enum
from dataclasses import dataclass
from typing import override

from .entity import Entity
from src.sprites import Sprite
from src.core import GameManager
from src.core.services import input_manager, scene_manager
from src.utils import GameSettings, Direction, Position, PositionCamera
from src.interface.components import Text

class EnemyTrainerClassification(Enum):
    STATIONARY = "stationary"

@dataclass
class IdleMovement:
    def update(self, enemy: "EnemyTrainer", dt: float) -> None:
        return

class EnemyTrainer(Entity):
    classification: EnemyTrainerClassification
    max_tiles: int | None
    _movement: IdleMovement
    warning_sign: Sprite
    warning_text: Text
    detected: bool
    los_direction: Direction

    pokemon_name: str | None

    @override
    def __init__(
        self,
        x: float,
        y: float,
        game_manager: GameManager,
        classification: EnemyTrainerClassification = EnemyTrainerClassification.STATIONARY,
        max_tiles: int | None = 2,
        facing: Direction | None = None,
        pokemon_name: str | None = None
    ) -> None:
        super().__init__(x, y, game_manager)
        self.classification = classification
        self.max_tiles = max_tiles
        self.pokemon_name = pokemon_name
        
        if classification == EnemyTrainerClassification.STATIONARY:
            self._movement = IdleMovement()
            if facing is None:
                raise ValueError("Idle EnemyTrainer requires a 'facing' Direction at instantiation")
            self._set_direction(facing)
        else:
            raise ValueError("Invalid classification")
        self.warning_sign = Sprite("exclamation.png", (GameSettings.TILE_SIZE // 2, GameSettings.TILE_SIZE // 2))
        self.warning_sign.update_pos(Position(x + GameSettings.TILE_SIZE // 4, y - GameSettings.TILE_SIZE // 2))
        self.warning_text = Text(
            "Press Space to Enter Battle", "Minecraft.ttf",
            20, 500, 500
        )
        self.detected = False

    @override
    def update(self, dt: float) -> None:
        self._movement.update(self, dt)
        self._has_los_to_player()
        
        if self.detected and input_manager.key_pressed(pygame.K_SPACE):
            import random
            from src.core.pokemon_data import POKEMON_SPRITES, POKEMON_ELEMENTS
            
            name = self.pokemon_name
            
            # If no specific name or name invalid, pick random
            if not name or name not in POKEMON_SPRITES:
                available_pokemon = list(POKEMON_SPRITES.keys())
                name = random.choice(available_pokemon)
                
            sprite_path = POKEMON_SPRITES[name]
            
            battle_data = {
                "type": "TRAINER",
                "enemy_sprite": sprite_path,
                "name": name, 
                "level": 5,
                "hp": 100,
                "manager": self.game_manager
            }
            self.game_manager.save()
            scene_manager.change_scene("battle", **battle_data)
            
        self.animation.update_pos(self.position)

    @override
    def draw(self, screen: pygame.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        if self.detected:
            self.warning_sign.draw(screen, camera)
            self.warning_text.draw(screen)
        if GameSettings.DRAW_HITBOXES:
            los_rect = self._get_los_rect()
            if los_rect is not None:
                pygame.draw.rect(screen, (255, 255, 0), camera.transform_rect(los_rect), 1)

    def _set_direction(self, direction: Direction) -> None:
        self.direction = direction
        if direction == Direction.RIGHT:
            self.animation.switch("right")
        elif direction == Direction.LEFT:
            self.animation.switch("left")
        elif direction == Direction.DOWN:
            self.animation.switch("down")
        else:
            self.animation.switch("up")
        self.los_direction = self.direction

    def _get_los_rect(self) -> pygame.Rect | None:
        dir = self.direction.value
        hitbox = pygame.Rect(
            self._snap_to_grid(self.position.x) - (dir==3)*(self.max_tiles-1)*GameSettings.TILE_SIZE,
            self._snap_to_grid(self.position.y) - (dir==1)*(self.max_tiles-1)*GameSettings.TILE_SIZE,
            GameSettings.TILE_SIZE * (1 + (5 > dir >= 3)*(self.max_tiles - 1)),
            GameSettings.TILE_SIZE * (1 + (dir <= 2)*(self.max_tiles - 1))
        )
        return hitbox

    def _has_los_to_player(self) -> None:
        player = self.game_manager.player
        if player is None:
            self.detected = False
            return
        los_rect = self._get_los_rect()
        if los_rect is None:
            self.detected = False
            return
        if los_rect.colliderect(player.position.x, player.position.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE):
            self.detected = True
        else:
            self.detected = False

    @classmethod
    @override
    def from_dict(cls, data: dict, game_manager: GameManager) -> "EnemyTrainer":
        classification = EnemyTrainerClassification(data.get("classification", "stationary"))
        max_tiles = data.get("max_tiles")
        facing_val = data.get("facing")
        facing: Direction | None = None
        if facing_val is not None:
            if isinstance(facing_val, str):
                facing = Direction[facing_val]
            elif isinstance(facing_val, Direction):
                facing = facing_val
        if facing is None and classification == EnemyTrainerClassification.STATIONARY:
            facing = Direction.DOWN
            
        pokemon_name = data.get("pokemon_name") # Load specific pokemon name
        
        return cls(
            data["x"] * GameSettings.TILE_SIZE,
            data["y"] * GameSettings.TILE_SIZE,
            game_manager,
            classification,
            max_tiles,
            facing,
            pokemon_name
        )

    @override
    def to_dict(self) -> dict[str, object]:
        base: dict[str, object] = super().to_dict()
        base["classification"] = self.classification.value
        base["facing"] = self.direction.name
        base["max_tiles"] = self.max_tiles
        base["pokemon_name"] = self.pokemon_name
        return base