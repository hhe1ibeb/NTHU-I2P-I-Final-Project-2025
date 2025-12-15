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
from typing import override

class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite
    
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
        self.sprite_online = Sprite("ingame_ui/options1.png", (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))

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
            self.game_manager.player.update(dt)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.update(dt)
        for shop_npc in self.game_manager.current_shop_npcs:
            shop_npc.update(dt)
            
        self.game_manager.bag.update(dt)
        self.backpack_button.update(dt)
        self.settings_button.update(dt)
        self.backpack_overlay.update(dt)
        self.settings_overlay.update(dt)

        if self.game_manager.player is not None and self.online_manager is not None:
            _ = self.online_manager.update(
                self.game_manager.player.position.x, 
                self.game_manager.player.position.y,
                self.game_manager.current_map.path_name
            )
        
    @override
    def draw(self, screen: pg.Surface):        
        if self.game_manager.player:
            camera = self.game_manager.player.camera
            self.game_manager.current_map.draw(screen, camera)
            self.game_manager.player.draw(screen, camera)
        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)
        for shop_npc in self.game_manager.current_shop_npcs:
            shop_npc.draw(screen, camera)

        self.game_manager.bag.draw(screen)
        self.backpack_button.draw(screen)
        self.settings_button.draw(screen)
        self.backpack_overlay.draw(screen)
        self.settings_overlay.draw(screen)
        
        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            for player in list_online:
                if player["map"] == self.game_manager.current_map.path_name:
                    cam = self.game_manager.player.camera
                    pos = cam.transform_position_as_position(Position(player["x"], player["y"]))
                    self.sprite_online.update_pos(pos)
                    self.sprite_online.draw(screen)
