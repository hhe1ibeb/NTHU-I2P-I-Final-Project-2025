from enum import Enum, auto

class Element(Enum):
    WATER = auto()
    FIRE = auto()
    GRASS = auto()
    ELECTRIC = auto()

def get_effectiveness(attacker: Element, defender: Element) -> float:
    # Default is 1.0
    if attacker == Element.WATER:
        if defender == Element.FIRE: return 2.0
        if defender == Element.GRASS: return 0.5
        if defender == Element.WATER: return 0.5
        
    elif attacker == Element.FIRE:
        if defender == Element.GRASS: return 2.0
        if defender == Element.WATER: return 0.5
        if defender == Element.FIRE: return 0.5
        
    elif attacker == Element.GRASS:
        if defender == Element.WATER: return 2.0
        if defender == Element.ELECTRIC: return 2.0
        if defender == Element.FIRE: return 0.5
        if defender == Element.GRASS: return 0.5
        
    elif attacker == Element.ELECTRIC:
        if defender == Element.WATER: return 2.0
        if defender == Element.GRASS: return 0.5
        if defender == Element.ELECTRIC: return 0.5
        
    return 1.0
