from __future__ import annotations
import pygame as pg
from enum import Enum, auto

from src.utils import GameSettings
from src.sprites import BackgroundSprite, Animation, Sprite
from src.core import GameManager, CatchManager
from src.entities.battle_entity import BattleEntity
from src.interface.components import Overlay, Text, Button
from src.scenes.scene_components import create_battle_message_overlay

class CatchSceneState(Enum):
    DECIDING = auto()
    SHOWING_RESULT = auto()

class CatchScene:
    game_manager: GameManager
    catch_manager: CatchManager | None
    
    # UI
    action_overlay: Overlay
    message_overlay: Overlay
    state: CatchSceneState
    
    def __init__(self) -> None:
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.game_manager = GameManager.load("saves/game0.json")
        self.catch_manager = None
        
        self._init_interface()

    def _init_interface(self):
        self.action_overlay = Overlay(
            "UI/raw/UI_Flat_Frame01a.png", 0, 520, 1280, 200, 0, True, 
            [
                Button("UI/raw/UI_Flat_Button01a_2.png", "UI/raw/UI_Flat_Button01a_1.png",
                    300, 580, 230, 60, self.on_throw_ball),
                Text("Throw ball", "Minecraft.ttf", 30, 330, 605),
                
                Button("UI/raw/UI_Flat_Button01a_2.png", "UI/raw/UI_Flat_Button01a_1.png",
                    600, 580, 230, 60, self.on_throw_rock),
                Text("Throw rock", "Minecraft.ttf", 30, 630, 605),
                
                Button("UI/raw/UI_Flat_Button01a_2.png", "UI/raw/UI_Flat_Button01a_1.png",
                    900, 580, 230, 60, self.on_run),
                Text("Run", "Minecraft.ttf", 30, 950, 605),
            ],
        )
        self.message_overlay = create_battle_message_overlay("")
        
        self.action_overlay.display(False)
        self.message_overlay.display(False)

    def enter(self, **kwargs) -> None:
        from src.core.services import sound_manager
        sound_manager.play_bgm("RBY 107 Battle! (Trainer).ogg")

        wild_data = kwargs if kwargs else {
            "sprite_path": "menu_sprites/menusprite10.png", "name": "Wild Mon", "hp": 100, "max_hp": 100, "level": 10
        }
        
        wild_sprite = Sprite(wild_data.get("sprite_path"), (200, 200))
        wild_entity = BattleEntity(wild_sprite, wild_data, 'ENEMY')
        
        self.catch_manager = CatchManager(wild_entity)
        self.state = CatchSceneState.DECIDING
        
        self.action_overlay.display(True)
        self.message_overlay.display(False)

    def exit(self) -> None:
        pass

    def handle_event(self, event: pg.event.Event):
        if self.state == CatchSceneState.SHOWING_RESULT:
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self._advance_text()
        
        if self.state == CatchSceneState.DECIDING:
            self.action_overlay.handle_event(event)

    def _show_result(self, result):
        self.last_result_state = result.state 
        
        self.state = CatchSceneState.SHOWING_RESULT
        self.action_overlay.display(False)
        
        self.message_overlay = create_battle_message_overlay(result.message)
        self.message_overlay.display(True)

    def _advance_text(self):
        self.message_overlay.display(False)

        from src.core.managers.catch_manager import CatchResultState

        if self.last_result_state == CatchResultState.CAUGHT:
            print("Pokemon caught! Exiting...")
            self._end_scene()
            
        elif self.last_result_state == CatchResultState.FLED:
            print("Pokemon fled! Exiting...")
            self._end_scene()
            
        else:
            print("Failed, returning to menu...")
            self.state = CatchSceneState.DECIDING
            self.action_overlay.display(True)

    def on_throw_ball(self):
        if self.state != CatchSceneState.DECIDING or not self.catch_manager:
            return
        result = self.catch_manager.throw_ball(self.game_manager)
        self._show_result(result)

    def on_throw_rock(self):
        if self.state != CatchSceneState.DECIDING or not self.catch_manager:
            return
        result = self.catch_manager.throw_rock()
        self._show_result(result)

    def on_run(self):
        self._end_scene()

    def _end_scene(self):
        from src.core.services import scene_manager
        scene_manager.change_scene('game')

    def update(self, dt: float) -> None:
        self.action_overlay.update(dt)
        self.message_overlay.update(dt)
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE] and self.state == CatchSceneState.SHOWING_RESULT:
            self._advance_text()
        if self.catch_manager:
            pass 

    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        
        if self.catch_manager:
            self.catch_manager.wild_pokemon.sprite.draw(screen)

        if self.state == CatchSceneState.DECIDING:
            self.action_overlay.draw(screen)
        elif self.state == CatchSceneState.SHOWING_RESULT:
            self.message_overlay.draw(screen)