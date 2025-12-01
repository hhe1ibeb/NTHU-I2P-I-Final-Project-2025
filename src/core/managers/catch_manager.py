from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass
import random
from typing import TYPE_CHECKING

from src.entities.battle_entity import BattleEntity

if TYPE_CHECKING:
    from src.core.managers.game_manager import GameManager

class CatchResultState(Enum):
    CAUGHT = auto()
    FAILED = auto()
    FLED = auto()

@dataclass
class CatchTurnResult:
    success: bool
    message: str
    state: CatchResultState

class CatchManager:
    wild_pokemon: BattleEntity
    catch_rate: float
    flee_rate: float

    def __init__(self, wild_pokemon: BattleEntity):
        self.wild_pokemon = wild_pokemon
        self.catch_rate = 0.4
        self.flee_rate = 0.1

    def throw_ball(self, game_manager: GameManager) -> CatchTurnResult:
        if game_manager.bag.get_item_count("Pokeball") <= 0:
            return CatchTurnResult(False, "You don't have any Pokeballs! Press space to continue.", CatchResultState.FAILED)

        game_manager.bag.remove_item("Pokeball")
        roll = random.random()
        
        if roll < self.catch_rate:
            game_manager.bag.add_monster(self.wild_pokemon.attributes)
            
            game_manager.save() 

            return CatchTurnResult(True, "Gotcha! The Pokémon was caught! Press space to continue.", CatchResultState.CAUGHT)
        else:
            return self._check_flee("It broke free! Press space to continue.")

    def throw_rock(self) -> CatchTurnResult:
        self.catch_rate = min(0.9, self.catch_rate + 0.2)
        self.flee_rate = min(1.0, self.flee_rate + 0.2)
        return self._check_flee("You threw a rock! It looks angry but vulnerable! Press space to continue.")

    def _check_flee(self, fail_message: str) -> CatchTurnResult:
        flee_roll = random.random()
        if flee_roll < self.flee_rate:
            return CatchTurnResult(False, "The wild Pokémon fled! Press space to continue.", CatchResultState.FLED)
        else:
            return CatchTurnResult(False, fail_message, CatchResultState.FAILED)