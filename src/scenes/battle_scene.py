from __future__ import annotations
import pygame as pg
from enum import Enum, auto

from src.utils import Logger
from src.sprites import BackgroundSprite, Sprite, Animation
from src.core import GameManager, BattleManager
from src.entities.battle_entity import BattleEntity
from src.interface.components import Overlay
from src.scenes.scene_components import (
    create_selection_overlay, 
    create_battle_action_overlay, 
    create_battle_message_overlay
)
from typing import Any

class BattleSceneState(Enum):
    SELECT_MONSTER = auto()  
    PLAYER_TURN = auto()     
    SHOWING_MESSAGE = auto() 
    BATTLE_OVER = auto()     

class BattleScene:
    pending_enemy_data: dict = {}

    def __init__(self) -> None:
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        
        self.game_manager = GameManager.load("saves/game0.json")
        self._init_interface()

    def enter(self, **kwargs: Any) -> None:
        from src.core.services import sound_manager
        sound_manager.play_bgm("RBY 107 Battle! (Trainer).ogg")

        self.battle_manager = None
        self.state = BattleSceneState.SELECT_MONSTER
        
        self.pending_enemy_data = kwargs

        self.selection_overlay.display(True)
        self.battle_action_overlay.display(False)
        self.battle_message_overlay.display(False)
        
        Logger.info(f"Entered Battle with: {self.pending_enemy_data}")

    def on_select_monster(self, player_monster_data: dict):
        player_sprite = Sprite(player_monster_data["sprite_path"], (200, 200))
        player_entity = BattleEntity(player_sprite, player_monster_data, 'PLAYER')

        enemy_sprite_path = self.pending_enemy_data.get("enemy_sprite", "sprites/sprite9_idle.png")
        
        enemy_attributes = {
            "sprite_path": enemy_sprite_path,
            "hp": self.pending_enemy_data.get("hp", 100),
            "max_hp": self.pending_enemy_data.get("hp", 100),
            "level": self.pending_enemy_data.get("level", 1)
        }
        
        enemy_sprite = Animation(enemy_sprite_path, ['idle'], 4, (200, 200))
        enemy_entity = BattleEntity(enemy_sprite, enemy_attributes, 'ENEMY')

        self.battle_manager = BattleManager(player_entity, enemy_entity)
        
        self.state = BattleSceneState.PLAYER_TURN
        self.selection_overlay.display(False)
        self.battle_action_overlay.display(True)

    def _init_interface(self):
        self.selection_overlay = create_selection_overlay(self.game_manager, self.on_select_monster)
        self.battle_action_overlay = create_battle_action_overlay(self.on_attack, self.on_run)
        self.battle_message_overlay = create_battle_message_overlay("")
        
        self.selection_overlay.display(True)
        self.battle_action_overlay.display(False)
        self.battle_message_overlay.display(False)

    def handle_event(self, event: pg.event.Event):
        if self.state == BattleSceneState.SHOWING_MESSAGE:
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self._advance_text()
                
    def _advance_text(self):
        self.battle_message_overlay.display(False)
        
        if self.battle_manager and self.battle_manager.is_battle_over():
            self._end_battle()
        else:
            self.state = BattleSceneState.PLAYER_TURN
            self.battle_action_overlay.display(True)

    def on_attack(self):
        if self.state != BattleSceneState.PLAYER_TURN:
            return

        if self.battle_manager:
            result = self.battle_manager.execute_player_attack()
            
            if result.state_after_turn == result.state_after_turn.PLAYER_WIN:
                self._show_result_message(result.message)
            else:
                self.on_enemy_turn()

    def on_enemy_turn(self):
        if self.battle_manager:
            result = self.battle_manager.execute_enemy_attack()
            self._show_result_message(result.message)

    def on_run(self):
        if self.state == BattleSceneState.PLAYER_TURN and self.battle_manager:
             if self.battle_manager.attempt_run():
                 self._end_battle()

    def _show_result_message(self, message: str):
        self.battle_action_overlay.display(False)
        self.selection_overlay.display(False)
        
        self.battle_message_overlay = create_battle_message_overlay(message)
        self.battle_message_overlay.display(True)
        
        self.state = BattleSceneState.SHOWING_MESSAGE

    def _end_battle(self):
        from src.core.services import scene_manager
        scene_manager.change_scene('game')

    def update(self, dt: float) -> None:
        self.selection_overlay.update(dt)
        
        if self.state == BattleSceneState.PLAYER_TURN:
            self.battle_action_overlay.update(dt)
            
        self.battle_message_overlay.update(dt)
        
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE] and self.state == BattleSceneState.SHOWING_MESSAGE:
            self._advance_text()

    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        
        if self.battle_manager:
            self.battle_manager.player.draw(screen)
            self.battle_manager.enemy.draw(screen)
            self._draw_battle_hud(screen)

        if self.state == BattleSceneState.SELECT_MONSTER:
            self.selection_overlay.draw(screen)
        elif self.state == BattleSceneState.PLAYER_TURN:
            self.battle_action_overlay.draw(screen)
        elif self.state == BattleSceneState.SHOWING_MESSAGE:
            self.battle_message_overlay.draw(screen)

    def _draw_battle_hud(self, screen: pg.Surface):
        if not self.battle_manager:
            return

        BAR_W, BAR_H = 200, 25
        COLOR_BG = (255, 0, 0)
        COLOR_FG = (0, 255, 0)
        
        def draw_bar(x, y, current, max_val):
            ratio = max(0, min(1, current / max_val))
            pg.draw.rect(screen, COLOR_BG, (x, y, BAR_W, BAR_H))
            pg.draw.rect(screen, COLOR_FG, (x, y, BAR_W * ratio, BAR_H))

        draw_bar(50, 50, self.battle_manager.player.hp, self.battle_manager.player.max_hp)
        draw_bar(550, 50, self.battle_manager.enemy.hp, self.battle_manager.enemy.max_hp)
        pass

    def exit(self):
        pass