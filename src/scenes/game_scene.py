import pygame as pg
import threading
import time

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import sound_manager
from src.sprites import Sprite
from src.interface.components import Button, Overlay
from src.scenes.scene_components import SettingsOverlay, BackpackOverlay
from src.interface.components.chat_overlay import ChatOverlay
from typing import override

class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    online_sprites: dict[int, Sprite]
    
    # fixed buttons
    backpack_button: Button
    settings_button: Button

    # overlays
    backpack_overlay: Overlay
    settings_overlay: Overlay

    def __init__(self):
        super().__init__()
        # Game Manager
        manager = GameManager.load("saves/game0.json")
        if manager is None:
            Logger.error("Failed to load game manager")
            exit(1)
        self.game_manager = manager
        
        # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
        else:
            self.online_manager = None
        
        # Use Animation for online players
        self.online_sprites = {} 

        # fixed buttons
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        self.backpack_button = Button(
            "UI/button_backpack.png", "UI/button_backpack_hover.png",
            px + 550, py - 350, 70, 70,
            lambda: self.backpack_overlay.display(True)
        )

        self.settings_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            px + 470, py - 350, 70, 70,
            lambda: self.settings_overlay.display(True)
        )

        # overlays
        self.settings_overlay = SettingsOverlay(
            lambda: self.game_manager.save(),
            self._load_game
        )
        self.backpack_overlay = BackpackOverlay(self.game_manager)
        
        self.chat_overlay = None
        if self.online_manager:
            self.chat_overlay = ChatOverlay(
                send_callback=self.online_manager.send_chat,
                get_messages=self.online_manager.get_recent_chat
            )
    
    def _load_game(self):
        manager = GameManager.load("saves/game0.json")
        if manager:
            self.game_manager = manager
            Logger.info("Game loaded successfully")
        else:
            Logger.warning("Failed to load game")

    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 103 Pallet Town.ogg")
        if self.online_manager:
            self.online_manager.enter()

        self.game_manager = GameManager.load("saves/game0.json")
        
        self.backpack_overlay.game_manager = self.game_manager
        self.settings_overlay.game_manager = self.game_manager

    @override
    def exit(self) -> None:
        if self.online_manager:
            self.online_manager.exit()
        
    @override
    def update(self, dt: float):
        self.game_manager.try_switch_map()
        
        if self.game_manager.player:
            # Block player movement if chat is open
            if not (self.chat_overlay and self.chat_overlay.is_open):
                self.game_manager.player.update(dt)
            else:
                # Still allow catch message update if needed, but for now just skip full update to freeze movement
                # But we might need animations to run? 
                # If we skip update, animation stops. 
                # Better: Allow update but ensure player knows input is blocked?
                # For now, freezing completely is the requested behavior "disable wasd".
                # If we want animations (like idle) to continue, we'd need to modify Player.update to take a 'input_blocked' flag.
                # Given the constraints, skipping update is the safest quick fix to disable control.
                pass
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.update(dt)
        for shop_npc in self.game_manager.current_shop_npcs:
            shop_npc.update(dt)
            
        self.game_manager.bag.update(dt)
        self.backpack_button.update(dt)
        self.settings_button.update(dt)
        self.backpack_overlay.update(dt)
        self.settings_overlay.update(dt)
        if self.chat_overlay:
            from src.core.services import input_manager
            import pygame as pg
            if input_manager.key_pressed(pg.K_t):
                 self.chat_overlay.open()
            self.chat_overlay.update(dt)

        if self.game_manager.player is not None and self.online_manager is not None:
            # Send our status
            is_moving = getattr(self.game_manager.player, "is_moving", False)
            _ = self.online_manager.update(
                self.game_manager.player.position.x, 
                self.game_manager.player.position.y,
                self.game_manager.current_map.path_name,
                self.game_manager.player.direction.name,
                is_moving
            )
            
            # Update other players
            list_online = self.online_manager.get_list_players()
            current_ids = set()
            
            from src.sprites import Animation # Local import
            
            for p in list_online:
                pid = p["id"]
                current_ids.add(pid)
                
                # Create sprite if new
                if pid not in self.online_sprites:
                    # Using ow1.png for other players
                    anim = Animation(
                        "character/ow1.png", ["down", "left", "right", "up"], 4,
                        (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
                    )
                    self.online_sprites[pid] = anim
                
                anim = self.online_sprites[pid]
                
                # Update Animation State
                direction_str = p.get("direction", "DOWN").lower()
                is_moving_remote = p.get("is_moving", False)
                
                anim.switch(direction_str)
                
                # Update position
                px, py = p["x"], p["y"]
                anim.update_pos(Position(px, py))
                
                if is_moving_remote:
                    anim.update(dt)
                else:
                    anim.accumulator = 0 # Reset to idle frame

            # Remove disconnected players from sprite dict
            for pid in list(self.online_sprites.keys()):
                if pid not in current_ids:
                    del self.online_sprites[pid]

    @override
    def draw(self, screen: pg.Surface):        
        if self.game_manager.player:
            camera = self.game_manager.player.camera
            self.game_manager.current_map.draw(screen, camera)
            self.game_manager.player.draw(screen, camera)
        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)
            
        # Draw online players
        if self.online_manager and self.game_manager.player:
            if self.game_manager.current_map:
                current_map_name = self.game_manager.current_map.path_name
                list_online = self.online_manager.get_list_players()
                
                camera = self.game_manager.player.camera
                
                for p in list_online:
                    # Strip any potential null bytes or whitespace just in case
                    p_map = p.get("map", "").strip()
                    if p_map == current_map_name:
                        pid = p["id"]
                        
                        # Create sprite if new
                        if pid not in self.online_sprites:
                            # Use ow1.png to match standard player appearance
                            anim = Animation(
                                "character/ow1.png", ["down", "left", "right", "up"], 4,
                                (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
                            )
                            self.online_sprites[pid] = anim
                        
                        anim = self.online_sprites[pid]
                        anim.draw(screen, camera)

        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)
        for shop_npc in self.game_manager.current_shop_npcs:
            shop_npc.draw(screen, camera)

        self.game_manager.bag.draw(screen)
        self.backpack_button.draw(screen)
        self.settings_button.draw(screen)
        self.backpack_overlay.draw(screen)
        self.settings_overlay.draw(screen)
        if self.chat_overlay:
            self.chat_overlay.draw(screen)
