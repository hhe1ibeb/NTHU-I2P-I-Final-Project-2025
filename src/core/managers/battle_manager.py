from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from src.entities.battle_entity import BattleEntity

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

        damage = 20
        self.enemy.take_damage(damage)
        
        message = f"You hit the enemy for {damage} damage!"
        
        if not self.enemy.is_alive():
            self.state = BattleState.PLAYER_WIN
            message = "Enemy fainted! You Won!"
        else:
            self.player_turn = False
            
        return TurnResult(True, damage, message, self.state)

    def execute_enemy_attack(self) -> TurnResult:
        if self.player_turn or self.state != BattleState.ONGOING:
             return TurnResult(False, 0, "Waiting for player...", self.state)

        damage = 15
        self.player.take_damage(damage)
        
        message = f"Enemy hit you for {damage} damage! Press space to continue."

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