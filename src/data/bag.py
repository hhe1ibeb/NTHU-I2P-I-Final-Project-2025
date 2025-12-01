import pygame as pg
import json
from src.utils import GameSettings
from src.utils.definition import Monster, Item 

class Bag:
    _monsters_data: list[Monster]
    _items_data: list[Item]

    def __init__(self, monsters_data: list[Monster] | None = None, items_data: list[Item] | None = None):
        self._monsters_data = monsters_data if monsters_data else []
        self._items_data = items_data if items_data else []

    def add_monster(self, monster_data: dict):
        self._monsters_data.append(monster_data)

    def get_item_count(self, item_name: str) -> int:
        for item in self._items_data:
            if item.get("name") == item_name:
                return item.get("count", 0)
        return 0

    def remove_item(self, item_name: str, amount: int = 1) -> bool:
        for item in self._items_data:
            if item.get("name") == item_name:
                current_count = item.get("count", 0)
                if current_count >= amount:
                    item["count"] = current_count - amount
                    return True
                else:
                    return False
        return False

    def update(self, dt: float):
        pass

    def draw(self, screen: pg.Surface):
        pass

    def to_dict(self) -> dict[str, object]:
        return {
            "monsters": list(self._monsters_data),
            "items": list(self._items_data)
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Bag":
        monsters = data.get("monsters") or []
        items = data.get("items") or []
        bag = cls(monsters, items)
        return bag