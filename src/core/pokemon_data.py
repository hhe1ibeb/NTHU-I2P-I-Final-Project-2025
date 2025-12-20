from src.core.element_system import Element

POKEMON_ELEMENTS = {
    "Dragonite": Element.FIRE,  
    "Charizard": Element.FIRE,
    "Blastoise": Element.WATER,
    "Venusaur": Element.GRASS,
    "Capybara": Element.ELECTRIC,
    "Snorlax": Element.WATER,   
    "Gengar": Element.FIRE,     
    "Mega Capy": Element.ELECTRIC,
    "Mega Charizard X": Element.FIRE
}

POKEMON_SPRITES = {
    "Charizard": "menu_sprites/menusprite1.png",
    "Blastoise": "menu_sprites/menusprite2.png",
    "Venusaur": "menu_sprites/menusprite3.png",
    "Capybara": "menu_sprites/menusprite4.png",
    "Gengar": "menu_sprites/menusprite5.png",
    "Dragonite": "menu_sprites/menusprite6.png",
    "Mega Capy": "menu_sprites/megacapy_menu.png",
    "Mega Charizard X": "menu_sprites/charizard_mega_menu.png" 
}

POKEMON_EVOLUTIONS = {
    "Capybara": {
        "evolves_to": "Mega Capy",
        "level_requirement": 3  
    },
    "Charizard": {
        "evolves_to": "Mega Charizard X",
        "level_requirement": 5 
    }
}

def get_pokemon_menu_sprite(name: str) -> str:
    """Returns the menu sprite path for a given pokemon name."""
    return POKEMON_SPRITES.get(name, "menu_sprites/menusprite1.png")

def get_pokemon_battle_sprite(name: str) -> str:
    """Returns the battle sprite path for a given pokemon name."""
    # User requested to use menu sprites for battle to avoid mapping issues
    return get_pokemon_menu_sprite(name)
