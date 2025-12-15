from __future__ import annotations
import pygame
from enum import Enum
from dataclasses import dataclass
from typing import override

from .entity import Entity
from src.sprites import Sprite, Animation
from src.core import GameManager
from src.core.services import input_manager, scene_manager
from src.utils import GameSettings, Direction, Position, PositionCamera
from src.interface.components import Text, Overlay
from src.scenes.scene_components.shop_overlay import ShopOverlay

class ShopNPCClassification(Enum):
    STATIONARY = "stationary"

@dataclass
class IdleMovement:
    def update(self, shop: "ShopNPC", dt: float) -> None:
        return

class ShopNPC(Entity):
    classification: ShopNPCClassification
    max_tiles: int | None
    _movement: IdleMovement
    warning_sign: Sprite
    warning_text: Text
    detected: bool
    los_direction: Direction
    shop_overlay: Overlay

    @override
    def __init__(
        self,
        x: float,
        y: float,
        game_manager: GameManager,
        classification: ShopNPCClassification = ShopNPCClassification.STATIONARY,
        max_tiles: int | None = 2,
        facing: Direction | None = None,
        products: dict | None = None,
    ) -> None:
        super().__init__(x, y, game_manager)
        self.animation = Animation(
            "character/ow4.png", ["down", "left", "right", "up"], 4,
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        )
        self.classification = classification
        self.max_tiles = max_tiles
        if classification == ShopNPCClassification.STATIONARY:
            self._movement = IdleMovement()
            if facing is None:
                raise ValueError("Idle ShopNPC requires a 'facing' Direction at instantiation")
            self._set_direction(facing)
        else:
            raise ValueError("Invalid classification")
        self.warning_sign = Sprite("exclamation.png", (GameSettings.TILE_SIZE // 2, GameSettings.TILE_SIZE // 2))
        self.warning_sign.update_pos(Position(x + GameSettings.TILE_SIZE // 4, y - GameSettings.TILE_SIZE // 2))
        self.warning_text = Text(
            "Press Space to Enter Shop", "Minecraft.ttf",
            20, 500, 500
        )
        self.detected = False
        
        # Default price map (could be moved to settings)
        base_prices = {
            "Potion": 50,
            "Pokeball": 100,
            "Super Potion": 150,
            "Great Ball": 200,
            "Dragonite": 9999, # Just in case monsters are sold
        }
        
        self.shop_items = {}
        self.shop_items_data = []
        
        if products and "items" in products:
            for item in products["items"]:
                name = item["name"]
                price = item.get("price", base_prices.get(name, 100))
                self.shop_items[name] = price
                # Store full item data
                item_data = item.copy()
                item_data["price"] = price # Ensure price is set
                self.shop_items_data.append(item_data)
        else:
            self.shop_items = base_prices
            # Reconstruct basic item data for default prices
            for name, price in base_prices.items():
                 # Default sprite path? We might have to guess or defaults
                 sprite = "ingame_ui/potion.png" if "Potion" in name else "ingame_ui/ball.png"
                 if "Coins" in name: sprite = "ingame_ui/coin.png"
                 self.shop_items_data.append({
                     "name": name,
                     "price": price,
                     "sprite_path": sprite,
                     "count": 1
                 })

        self.shop_monsters = []
        if products and "monsters" in products:
            for monster in products["monsters"]:
                # Store full monster data including price. 
                # If price is missing, default to a high value.
                if "price" not in monster:
                     monster["price"] = base_prices.get(monster["name"], 2000)
                self.shop_monsters.append(monster)
        
        self.shop_overlay = ShopOverlay(self, self.game_manager)

    @override
    def update(self, dt: float) -> None:
        self._movement.update(self, dt)
        self._has_los_to_player()
        
        if self.detected and input_manager.key_pressed(pygame.K_SPACE):
            self.shop_overlay.display(True)
            
        self.animation.update_pos(self.position)
        self.shop_overlay.update(dt)

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
        self.shop_overlay.draw(screen)

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
    def from_dict(cls, data: dict, game_manager: GameManager) -> "ShopNPC":
        classification = ShopNPCClassification(data.get("classification", "stationary"))
        max_tiles = data.get("max_tiles")
        facing_val = data.get("facing")
        facing: Direction | None = None
        if facing_val is not None:
            if isinstance(facing_val, str):
                facing = Direction[facing_val]
            elif isinstance(facing_val, Direction):
                facing = facing_val
        if facing is None and classification == ShopNPCClassification.STATIONARY:
            facing = Direction.DOWN
        
        products = data.get("products")
            
        return cls(
            data["x"] * GameSettings.TILE_SIZE,
            data["y"] * GameSettings.TILE_SIZE,
            game_manager,
            classification,
            max_tiles,
            facing,
            products,
        )

    @override
    def to_dict(self) -> dict[str, object]:
        base: dict[str, object] = super().to_dict()
        base["classification"] = self.classification.value
        base["facing"] = self.direction.name
        base["max_tiles"] = self.max_tiles
        return base