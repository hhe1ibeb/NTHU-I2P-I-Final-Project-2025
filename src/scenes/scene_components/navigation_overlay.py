import pygame as pg
from src.interface.components import Overlay, Text, Button
from src.utils import GameSettings, Logger, Position
from src.core.managers.navigation_manager import NavigationManager
from src.core.managers.game_manager import GameManager
from typing import Callable

class NavigationOverlay(Overlay):
    def __init__(self, game_manager: GameManager, navigate_callback: Callable[[list[Position]], None]):
        self.game_manager = game_manager
        self.navigate_callback = navigate_callback
        
        self.px = GameSettings.SCREEN_WIDTH // 2
        self.py = GameSettings.SCREEN_HEIGHT // 2
        
        super().__init__(
            "UI/raw/UI_Flat_Frame03a.png",
            self.px // 2, self.py // 4, 600, 400,
            160,
            default_display=False,
            components=[],
            exit_key=[pg.K_ESCAPE]
        )
        
        self.static_components = [
            Text("Navigation", "Minecraft.ttf", 40, self.px - 100, self.py - 180),
            Button(
                "UI/button_back.png", "UI/button_back_hover.png",
                self.px + 220, self.py - 180, 50, 50,
                lambda: self.display(False)
            )
        ]
        
        # Places derived from game0.json
        self.places = [
            ("Home", (16, 29)),        # Near House entrance (16, 28)
            ("Gym", (24, 24)),         # Near Gym entrance (24, 23)
        ]
        
        self.refresh_places_ui()

    def refresh_places_ui(self):
        self.components = list(self.static_components)
        
        start_y = self.py - 100
        for name, (tx, ty) in self.places:
            # Button for each place
            btn = Button(
                "UI/raw/UI_Flat_Banner01a.png", "UI/raw/UI_Flat_Banner01a.png", # Using same for hover for now, or maybe tint
                self.px - 150, start_y, 300, 50,
                lambda t=(tx,ty): self.start_navigation(t)
            )
            
            # Using Black color for text to ensure visibility against light banner
            lbl = Text(name, "Minecraft.ttf", 25, self.px - 20, start_y + 15, color=(0, 0, 0))
            
            self.components.append(btn)
            self.components.append(lbl)
            
            start_y += 60
            
    def start_navigation(self, target_tile: tuple[int, int]):
        Logger.info(f"Navigating to {target_tile}")
        
        if not self.game_manager.player:
            return

        start_pos = self.game_manager.player.position
        end_pos = Position(target_tile[0] * GameSettings.TILE_SIZE, target_tile[1] * GameSettings.TILE_SIZE)
        
        # Collect Dynamic Obstacles
        dynamic_obstacles = set()
        
        # Enemy Trainers
        for enemy in self.game_manager.current_enemy_trainers:
            tx = int(enemy.position.x // GameSettings.TILE_SIZE)
            ty = int(enemy.position.y // GameSettings.TILE_SIZE)
            dynamic_obstacles.add((tx, ty))
            
        # Shop NPCs
        for npc in self.game_manager.current_shop_npcs:
            tx = int(npc.position.x // GameSettings.TILE_SIZE)
            ty = int(npc.position.y // GameSettings.TILE_SIZE)
            dynamic_obstacles.add((tx, ty))

        # Teleporters
        if self.game_manager.current_map and self.game_manager.current_map.teleporters:
            for teleport in self.game_manager.current_map.teleporters:
                tx = int(teleport.pos.x // GameSettings.TILE_SIZE)
                ty = int(teleport.pos.y // GameSettings.TILE_SIZE)
                
                if (tx, ty) != target_tile:
                     dynamic_obstacles.add((tx, ty))

        path = NavigationManager.bfs(start_pos, end_pos, self.game_manager.current_map, dynamic_obstacles)
        
        if path:
            Logger.info(f"Path found with {len(path)} steps.")
            self.navigate_callback(path)
            self.display(False)
        else:
            Logger.warning("No path found!")
