from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from src.entities.battle_entity import BattleEntity
from src.core.element_system import get_effectiveness

class BattleState(Enum):
    ONGOING = auto()
    PLAYER_WIN = auto()
    ENEMY_WIN = auto()

@dataclass
class TurnResult:
    success: bool
    damage_dealt: int
    message: str
    state_after_turn: BattleState

class BattleManager:
    def __init__(self, player: BattleEntity, enemy: BattleEntity):
        self.player = player
        self.enemy = enemy
        self.player_turn = True
        self.state = BattleState.ONGOING

    def execute_player_attack(self) -> TurnResult:
        if not self.player_turn or self.state != BattleState.ONGOING:
            return TurnResult(False, 0, "Not your turn!", self.state)

        base_damage = 20
        effectiveness = get_effectiveness(self.player.element, self.enemy.element)
        
        # Damage Formula: Base * (Atk / Def) * Eff
        atk_mult = self.player.attack_multiplier
        def_mult = self.enemy.defense_multiplier
        
        damage = int(base_damage * (atk_mult / def_mult) * effectiveness)
        
        self.enemy.take_damage(damage)
        
        message = f"You hit the enemy for {damage} damage!"
        if effectiveness > 1.0:
            message += " It's super effective!"
        elif effectiveness < 1.0:
            message += " It's not very effective..."
            
        if not self.enemy.is_alive():
            self.state = BattleState.PLAYER_WIN
            message = "Enemy fainted! You Won!"
        else:
            self.player_turn = False
        
        return TurnResult(True, damage, message, self.state)

    def execute_enemy_attack(self) -> TurnResult:
        if self.player_turn or self.state != BattleState.ONGOING:
             return TurnResult(False, 0, "Waiting for player...", self.state)

        base_damage = 15
        effectiveness = get_effectiveness(self.enemy.element, self.player.element)
        
        atk_mult = self.enemy.attack_multiplier
        def_mult = self.player.defense_multiplier
        
        damage = int(base_damage * (atk_mult / def_mult) * effectiveness)
        
        self.player.take_damage(damage)
        
        message = f"Enemy hit you for {damage} damage!"
        if effectiveness > 1.0:
            message += " Super effective!"
        elif effectiveness < 1.0:
            message += " Not very effective..."
        message += " Press space to continue."

        if not self.player.is_alive():
            self.state = BattleState.ENEMY_WIN
            message = "You fainted... You Lost."
        else:
            self.player_turn = True
            
        return TurnResult(True, damage, message, self.state)
        
    def use_item(self, item_name: str) -> TurnResult:
        if not self.player_turn or self.state != BattleState.ONGOING:
            return TurnResult(False, 0, "Not your turn!", self.state)
            
        message = ""
        success = True
        
        if item_name == "Heal Potion":
            self.player.heal(50)
            message = "Used Heal Potion! Recovered 50 HP."
        elif item_name == "Strength Potion":
            self.player.boost_attack(1.5)
            message = "Used Strength Potion! Attack rose!"
        elif item_name == "Defense Potion":
            self.player.boost_defense(1.5)
            message = "Used Defense Potion! Defense rose!"
        else:
            success = False
            message = "Cannot use this item!"
            
        if success:
            self.player_turn = False
            
        return TurnResult(success, 0, message, self.state)

        if not self.player.is_alive():
            self.state = BattleState.ENEMY_WIN
            message = "You fainted... You Lost."
        else:
            self.player_turn = True
            
        return TurnResult(True, damage, message, self.state)

    def attempt_run(self) -> bool:
        self.state = BattleState.PLAYER_WIN # Treat as win to exit battle
        return True

    def is_battle_over(self) -> bool:
        return self.state != BattleState.ONGOING