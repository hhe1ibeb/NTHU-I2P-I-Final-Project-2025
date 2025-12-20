import pygame as pg
from src.core.managers.game_manager import GameManager
from src.utils import GameSettings, Position

class Minimap:
    def __init__(self, x: int, y: int, width: int, height: int, game_manager: GameManager):
        self.rect = pg.Rect(x, y, width, height)
        self.game_manager = game_manager
        
        self.border_color = (255, 255, 255)
        self.player_dot_color = (255, 0, 0)
        self.bg_color = (0, 0, 0, 150) # Semi-transparent black
        
        # Cache properties
        self.current_map_name = ""
        self.cached_surface = None
        self.map_scale_x = 1.0
        self.map_scale_y = 1.0
        
    def update(self) -> None:
        if not self.game_manager.current_map:
            return
            
        map_name = self.game_manager.current_map.path_name
        
        # Check if map changed
        if map_name != self.current_map_name:
            self.current_map_name = map_name
            self._generate_minimap_surface()
            
    def _generate_minimap_surface(self) -> None:
        game_map = self.game_manager.current_map
        if not game_map:
            return
            
        # Get the full map surface
        # Note: accessing protected member logic here, but Map exposes _surface effectively
        # Ideally Map should have a public getter or we use what draw uses. 
        # For now accessing game_map._surface is consistent with internal access patterns I found.
        # But wait, game_map._surface is the cached big surface.
        
        original_surface = game_map._surface
        original_w, original_h = original_surface.get_size()
        
        # Calculate aspect ratio to fit in self.rect
        scale_w = self.rect.width / original_w
        scale_h = self.rect.height / original_h
        
        # We want to maintain aspect ratio, or fill? 
        # Usually minimaps might fill or be decentered. Let's fit-scale (uniform).
        scale = min(scale_w, scale_h)
        
        new_w = int(original_w * scale)
        new_h = int(original_h * scale)
        
        self.map_scale_x = scale
        self.map_scale_y = scale
        
        # Scale it
        self.cached_surface = pg.transform.scale(original_surface, (new_w, new_h))
        
        # Determine offset to center it in our rect
        self.offset_x = (self.rect.width - new_w) // 2
        self.offset_y = (self.rect.height - new_h) // 2
        
    def draw(self, screen: pg.Surface) -> None:
        if not self.cached_surface:
            return
            
        # Draw background and border
        # Create a surface for the minimap background to support alpha
        bg_surface = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
        pg.draw.rect(bg_surface, self.bg_color, (0, 0, self.rect.width, self.rect.height))
        screen.blit(bg_surface, self.rect.topleft)
        
        pg.draw.rect(screen, self.border_color, self.rect, 2)
        
        # Draw map
        draw_pos = (self.rect.x + self.offset_x, self.rect.y + self.offset_y)
        screen.blit(self.cached_surface, draw_pos)
        
        # Draw Player
        if self.game_manager.player:
            player_pos = self.game_manager.player.position
            
            # Map world pos to minimap pos
            # world_x -> scale -> + offset + rect_x
            
            # We need to consider how Position works.
            mx = (player_pos.x * self.map_scale_x) + self.rect.x + self.offset_x
            my = (player_pos.y * self.map_scale_y) + self.rect.y + self.offset_y
            
            pg.draw.circle(screen, self.player_dot_color, (int(mx), int(my)), 3)
