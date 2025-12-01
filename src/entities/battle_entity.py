from __future__ import annotations
import pygame as pg
from src.sprites import Sprite, Animation
from src.utils import Position
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

    def __init__(self, sprite, attributes, side):
        self.attributes = attributes 
        
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

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
            
        self.attributes['hp'] = self.hp 

    def is_alive(self):
        return self.hp > 0
    
    def draw(self, screen):
        self.sprite.draw(screen)