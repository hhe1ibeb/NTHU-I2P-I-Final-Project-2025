from __future__ import annotations
import pygame as pg
from enum import Enum, auto

from src.utils import Logger
from src.core.pokemon_data import POKEMON_EVOLUTIONS, POKEMON_SPRITES, POKEMON_ELEMENTS, Element, get_pokemon_battle_sprite
from src.sprites import BackgroundSprite, Sprite, Animation
from src.core import GameManager, BattleManager
from src.entities.battle_entity import BattleEntity
from src.interface.components import Overlay
from src.scenes.scene_components import (
    create_selection_overlay, 
    create_battle_action_overlay, 
    create_battle_message_overlay
)
from src.scenes.scene_components.item_selection_overlay import ItemSelectionOverlay
from src.scenes.scene_components.element_info_overlay import ElementInfoOverlay
from typing import Any

class BattleSceneState(Enum):
    SELECT_MONSTER = auto()  
    PLAYER_TURN = auto()     
    SHOWING_MESSAGE = auto() 
    SELECT_ITEM = auto()
    ANIMATING = auto()
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
        
        if "manager" in kwargs:
            self.game_manager = kwargs["manager"]
        
        self.pending_enemy_data = kwargs
        
        # Re-init interfaces to use the new game manager
        self._init_interface()

        self.selection_overlay.display(True)
        self.battle_action_overlay.display(False)
        self.battle_message_overlay.display(False)
        self.item_selection_overlay.display(False)
        
        Logger.info(f"Entered Battle with: {self.pending_enemy_data}")

    def on_select_monster(self, player_monster_data: dict):
        player_sprite_path = get_pokemon_battle_sprite(player_monster_data["name"])
        player_sprite = Sprite(player_sprite_path, (200, 200))
        player_entity = BattleEntity(player_sprite, player_monster_data, 'PLAYER')

        enemy_sprite_path = self.pending_enemy_data.get("enemy_sprite", "sprites/sprite9_idle.png")
        
        enemy_attributes = {
            "name": self.pending_enemy_data.get("name", "Unknown"),
            "sprite_path": enemy_sprite_path,
            "hp": self.pending_enemy_data.get("hp", 100),
            "max_hp": self.pending_enemy_data.get("hp", 100),
            "level": self.pending_enemy_data.get("level", 1)
        }
        
        if "menu_sprites" in enemy_sprite_path:
            enemy_sprite = Sprite(enemy_sprite_path, (200, 200))
        else:
            enemy_sprite = Animation(enemy_sprite_path, ['idle'], 4, (200, 200))
        enemy_entity = BattleEntity(enemy_sprite, enemy_attributes, 'ENEMY')

        self.battle_manager = BattleManager(player_entity, enemy_entity)
        
        self.state = BattleSceneState.PLAYER_TURN
        self.selection_overlay.display(False)
        self.battle_action_overlay.display(True)
        self.item_selection_overlay.display(False)

    def _init_interface(self):
        self.selection_overlay = create_selection_overlay(self.game_manager, self.on_select_monster)
        self.battle_action_overlay = create_battle_action_overlay(self.on_attack, self.on_run, self.on_bag)
        self.battle_message_overlay = create_battle_message_overlay("")
        self.item_selection_overlay = ItemSelectionOverlay(self.game_manager, self.on_select_item, self.on_bag_close)
        self.element_info_overlay = ElementInfoOverlay()
        
        from src.interface.components import Button
        self.info_button = Button(
            "exclamation.png", "exclamation.png",
            1200, 10, 50, 50,
            lambda: self.element_info_overlay.display(True)
        )
        
        self.selection_overlay.display(True)
        self.battle_action_overlay.display(False)
        self.battle_message_overlay.display(False)
        self.item_selection_overlay.display(False)
        self.element_info_overlay.display(False)

    def handle_event(self, event: pg.event.Event):
        if self.state == BattleSceneState.SHOWING_MESSAGE:
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self._advance_text()
                
    def _advance_text(self):
        self.battle_message_overlay.display(False)
        
        if self.battle_manager and self.battle_manager.is_battle_over():
            self._end_battle()
        else:
            if self.battle_manager.player_turn:
                self.state = BattleSceneState.PLAYER_TURN
                self.battle_action_overlay.display(True)
            else:
                self.on_enemy_turn()

    def on_attack(self):
        if self.state != BattleSceneState.PLAYER_TURN:
            return

        if self.battle_manager:
            # Play animation then execute
            self._play_attack_animation('PLAYER', self._after_player_attack)

    def _after_player_attack(self):
         result = self.battle_manager.execute_player_attack()
            
         if result.state_after_turn == result.state_after_turn.PLAYER_WIN:
             self._show_result_message(result.message)
         else:
             self._play_hit_animation('ENEMY')
             self.on_enemy_turn()

    def on_bag(self):
        if self.state != BattleSceneState.PLAYER_TURN:
            return
            
        self.state = BattleSceneState.SELECT_ITEM
        self.battle_action_overlay.display(False)
        self.item_selection_overlay.display(True)
        
    def on_bag_close(self):
        # Called when back button is pressed in bag
        self.state = BattleSceneState.PLAYER_TURN
        self.battle_action_overlay.display(True)
        self.item_selection_overlay.display(False)
            
    def on_select_item(self, item_name: str):
        self.item_selection_overlay.display(False)
        
        # Consume item
        if self.game_manager.bag.remove_item(item_name, 1):
             result = self.battle_manager.use_item(item_name)
             if result.success:
                 self._show_result_message(result.message)
             else:
                 self.game_manager.bag.add_item(item_name, 1) # Refund
                 self.state = BattleSceneState.PLAYER_TURN
                 self.battle_action_overlay.display(True)
        else:
             self.state = BattleSceneState.PLAYER_TURN
             self.battle_action_overlay.display(True)

    def on_enemy_turn(self):
        if self.battle_manager:
             self._play_attack_animation('ENEMY', self._after_enemy_attack)
             
    def _after_enemy_attack(self):
        result = self.battle_manager.execute_enemy_attack()
        self._play_hit_animation('PLAYER')
        self._show_result_message(result.message)

    def on_run(self):
        if self.state == BattleSceneState.PLAYER_TURN and self.battle_manager:
             if self.battle_manager.attempt_run():
                 self._end_battle()
    
    # Animation Helpers
    def _play_attack_animation(self, side: str, callback=None):
         entity = self.battle_manager.player if side == 'PLAYER' else self.battle_manager.enemy
         direction = 1 if side == 'PLAYER' else -1
         
         self.animation_state = "ATTACK"
         self.animation_timer = 0.0
         self.animator_entity = entity
         self.animator_direction = direction
         self.animation_callback = callback
         
         self.state = BattleSceneState.ANIMATING

    def _play_hit_animation(self, side: str):
        entity = self.battle_manager.player if side == 'PLAYER' else self.battle_manager.enemy
        
        if not hasattr(self, 'flashing_entities'):
            self.flashing_entities = []
            
        # Add to list with timer
        self.flashing_entities.append([entity, 0.5]) # [Entity, Timer]
        entity.is_flashing = True

    def _show_result_message(self, message: str):
        self.battle_action_overlay.display(False)
        self.selection_overlay.display(False)
        
        self.battle_message_overlay = create_battle_message_overlay(message)
        self.battle_message_overlay.display(True)
        
        self.state = BattleSceneState.SHOWING_MESSAGE

    def _end_battle(self):
        # Update player's pokemon state in bag
        if self.battle_manager and self.battle_manager.player:
             battle_player = self.battle_manager.player
             # Find in bag
             p_name = battle_player.attributes.get("name")
             
             target_monster_idx = -1
             target_monster = None
             
             if p_name:
                 for i, monster in enumerate(self.game_manager.bag._monsters_data):
                     if monster["name"] == p_name:
                         target_monster = monster
                         target_monster_idx = i
                         break
            
             if target_monster:
                 # Update HP
                 target_monster["hp"] = battle_player.hp
                 
                 # Logic for Win -> XP -> Level Up -> Evolution
                 if self.battle_manager.state == self.battle_manager.state.PLAYER_WIN:
                     self._handle_xp_and_evolution(target_monster)

             self.game_manager.save()

        from src.core.services import scene_manager
        scene_manager.change_scene('game')

    def _handle_xp_and_evolution(self, monster: dict):
        # 1. Gain XP
        xp_gain = 50 # Static XP for now
        monster["xp"] = monster.get("xp", 0) + xp_gain
        # We can't show message easily here without blocking scene change, 
        # so relying on console or future UI improvements. 
        # For now, let's just do logic.
        
        # 2. Check Level Up
        # Threshold: Level * 100
        while monster.get("xp", 0) >= monster["level"] * 100:
            monster["xp"] -= monster["level"] * 100
            monster["level"] += 1
            
            # Increase Stats
            monster["max_hp"] += 10
            monster["hp"] = monster["max_hp"] # Full heal on level up
            # (If we tracked attack/defense in dict, we would increase them here)
            
            Logger.info(f"{monster['name']} leveled up to {monster['level']}!")
            
            # 3. Check Evolution
            self._check_evolution(monster)

    def _check_evolution(self, monster: dict):
        name = monster["name"]
        if name in POKEMON_EVOLUTIONS:
            evo_data = POKEMON_EVOLUTIONS[name]
            if monster["level"] >= evo_data["level_requirement"]:
                # Evolve!
                new_name = evo_data["evolves_to"]
                monster["name"] = new_name
                
                # Update attributes
                # Look up new sprite?
                # Ideally sprite path should be in POKEMON_SPRITES or similar
                # Assuming standard naming or lookup
                # Let's use the one in POKEMON_SPRITES if available for menu, 
                # but for battle sprite we might need a mapping or just infer
                
                # Stat Boost (Significant)
                monster["max_hp"] += 50
                monster["hp"] = monster["max_hp"]
                
                Logger.info(f"What? {name} is evolving into {new_name}!")

    def update(self, dt: float) -> None:
        self.selection_overlay.update(dt)
        self.item_selection_overlay.update(dt)
        self.element_info_overlay.update(dt)
        
        # Only update info button if state allows (approximate check)
        # Assuming we can always open info unless in animation?
        if self.state not in [BattleSceneState.ANIMATING, BattleSceneState.BATTLE_OVER]:
             self.info_button.update(dt)
        
        # Handle flashing entities
        if hasattr(self, 'flashing_entities'):
            # Iterate backwards to allow removal
            for i in range(len(self.flashing_entities) - 1, -1, -1):
                data = self.flashing_entities[i]
                data[1] -= dt
                if data[1] <= 0:
                    data[0].is_flashing = False
                    self.flashing_entities.pop(i)
        
        # Handle simple attack animation state (Attack Lunge)
        if self.state == BattleSceneState.ANIMATING:
             self.animation_timer += dt
             # Lunge forward 0.2s, back 0.2s
             duration = 0.4
             if self.animation_timer < duration / 2:
                 self.animator_entity.offset_x += 200 * dt * self.animator_direction
                 self.animator_entity.offset_y -= 100 * dt * self.animator_direction 
             elif self.animation_timer < duration:
                 self.animator_entity.offset_x -= 200 * dt * self.animator_direction
                 self.animator_entity.offset_y += 100 * dt * self.animator_direction
             else:
                 # Done
                 self.animator_entity.offset_x = 0
                 self.animator_entity.offset_y = 0
                 
                 if self.animation_callback:
                     cb = self.animation_callback
                     self.animation_callback = None
                     cb()
                 # If callback changed state, good. If not, we might be stuck in ANIMATING?
                 # ideally callback should change state. 
                 # If no callback, we should revert to PLAYER_TURN or something?
                 # For now assuming callback always handles state transition.

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
        elif self.state == BattleSceneState.SELECT_ITEM:
            self.item_selection_overlay.draw(screen)

        self.info_button.draw(screen)
        self.element_info_overlay.draw(screen)

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

        # Player HUD
        draw_bar(50, 50, self.battle_manager.player.hp, self.battle_manager.player.max_hp)
        # Draw Element
        font = pg.font.Font(None, 24)
        elem_text = font.render(self.battle_manager.player.element.name, True, (0, 0, 0))
        screen.blit(elem_text, (50, 80))

        # Enemy HUD
        draw_bar(550, 50, self.battle_manager.enemy.hp, self.battle_manager.enemy.max_hp)
        # Draw Element
        elem_text = font.render(self.battle_manager.enemy.element.name, True, (0, 0, 0))
        screen.blit(elem_text, (550, 80))

    def exit(self):
        pass