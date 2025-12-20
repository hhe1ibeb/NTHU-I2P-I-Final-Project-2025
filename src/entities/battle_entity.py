from __future__ import annotations
import pygame as pg
from src.sprites import Sprite, Animation
from src.utils import Position
from src.core.pokemon_data import POKEMON_ELEMENTS
from src.core.element_system import Element
from enum import Enum

Side = Enum('Side', ['PLAYER', 'ENEMY'])

class BattleEntity:
    sprite: Sprite
    hp: int
    max_hp: int
    level: int
    x: int
    y: int
    side: Side
    attributes: dict
    element: Element

    def __init__(self, sprite, attributes, side):
        self.attributes = attributes 
        
        # Determine element based on name, default to NORMAL if not found or if name not in attributes
        name = attributes.get("name", "Unknown")
        self.element = POKEMON_ELEMENTS.get(name, Element.WATER)

        self.hp = attributes["hp"]
        self.max_hp = attributes["max_hp"]
        self.level = attributes["level"]

        if side == 'PLAYER':
            self.x = 100
            self.y = 300
            self.side = Side.PLAYER
        elif side == 'ENEMY':
            self.x = 800
            self.y = 100
            self.side = Side.ENEMY
        else: 
            raise ValueError(f"Side name cannot be {side.name}")

        self.sprite = sprite
        self.sprite.update_pos(Position(self.x, self.y))
        
        self.attack_multiplier = 1.0
        self.defense_multiplier = 1.0
        
        # Animation properties
        self.offset_x = 0
        self.offset_y = 0
        self.is_flashing = False

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
            
        self.attributes['hp'] = self.hp 
        
    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)
        self.attributes['hp'] = self.hp

    def boost_attack(self, multiplier: float):
        self.attack_multiplier = multiplier

    def boost_defense(self, multiplier: float):
        self.defense_multiplier = multiplier 

    def is_alive(self):
        return self.hp > 0
    
    def draw(self, screen):
        if self.is_flashing:
            # Simple flash effect: don't draw every other frame or use a timer
            # For simplicity let's just use a color modifier or skip drawing
            # Actually, skipping drawing is easiest for "blinking"
            import time
            if int(time.time() * 20) % 2 == 0:
                pass # Don't draw
            else:
                 # Update pos with offset before drawing
                 original_pos = Position(self.x, self.y)
                 temp_pos = Position(self.x + self.offset_x, self.y + self.offset_y)
                 self.sprite.update_pos(temp_pos)
                 self.sprite.draw(screen)
                 self.sprite.update_pos(original_pos) # Restore
        else:
             original_pos = Position(self.x, self.y)
             temp_pos = Position(self.x + self.offset_x, self.y + self.offset_y)
             self.sprite.update_pos(temp_pos)
             self.sprite.draw(screen)
             self.sprite.update_pos(original_pos)