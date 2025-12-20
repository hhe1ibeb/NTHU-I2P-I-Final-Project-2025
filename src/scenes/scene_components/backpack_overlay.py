import pygame as pg
from src.utils import GameSettings
from src.core.managers.game_manager import GameManager
from src.interface.components import Text, Overlay, Button, Frame
from typing import override
from src.core.pokemon_data import POKEMON_ELEMENTS, get_pokemon_menu_sprite
from src.core.element_system import Element
class BackpackOverlay(Overlay):
    def __init__(self, game_manager: GameManager):
        self.game_manager = game_manager
        self.px = GameSettings.SCREEN_WIDTH // 2
        self.py = GameSettings.SCREEN_HEIGHT // 2
        
        super().__init__(
            "UI/raw/UI_Flat_Frame03a.png", 
            self.px // 3, self.py // 3, 900, 500,
            160,
            default_display=False,
            components=[], 
            exit_key=[pg.K_ESCAPE]
        )
        
        self.static_components = self._create_static_ui()
        
        # Scroll settings
        self.scroll_y = 0
        self.target_scroll_y = 0
        self.max_scroll = 0
        self.scroll_speed = 40
        
        self.selected_item_name = None

        # Viewport for scrolling (adjust based on UI frame)
        # Frame is at px//3, py//3, 900, 500.
        # Static UI takes up some top space.
        self.view_rect = pg.Rect(self.px // 3 + 40, self.py // 3 + 100, 820, 320)
        self.scrollable_components = []
        
        self.refresh_content()

    def display(self, show: bool):
        if show:
            self.refresh_content()
            self.scroll_y = 0
            self.target_scroll_y = 0
        else:
             self.selected_item_name = None # Reset selection on close
        super().display(show)
        
    def select_item(self, item_name: str):
        if self.selected_item_name == item_name:
            self.selected_item_name = None # Deselect
        else:
            self.selected_item_name = item_name
        self.refresh_content()

    def use_item_on_monster(self, monster_index: int):
        if not self.selected_item_name:
            return

        # Check if we have the item
        count = self.game_manager.bag.get_item_count(self.selected_item_name)
        if count <= 0:
            self.selected_item_name = None
            self.refresh_content()
            return

        # Get monster
        monsters = self.game_manager.bag._monsters_data
        if not (0 <= monster_index < len(monsters)):
            return
            
        monster = monsters[monster_index]
        
        # Apply Item Logic
        success = False
        if self.selected_item_name == "Heal Potion":
            if monster["hp"] < monster["max_hp"]:
                monster["hp"] = min(monster["max_hp"], monster["hp"] + 50)
                success = True
        elif self.selected_item_name == "Potion":
            if monster["hp"] < monster["max_hp"]:
                monster["hp"] = min(monster["max_hp"], monster["hp"] + 20)
                success = True
        
        if success:
            self.game_manager.bag.remove_item(self.selected_item_name, 1)
            self.game_manager.save()
            
            # Check if we ran out
            if self.game_manager.bag.get_item_count(self.selected_item_name) <= 0:
                self.selected_item_name = None
                
            self.refresh_content()

    @override
    def update(self, dt):
        super().update(dt) # Handles Exit Key
        from src.core.services import input_manager
        
        if self.is_display:
            # Scroll Input
            if self.max_scroll > 0 and input_manager.mouse_wheel != 0:
                self.target_scroll_y -= input_manager.mouse_wheel * self.scroll_speed
                self.target_scroll_y = max(0, min(self.target_scroll_y, self.max_scroll))
            
            # Smooth Scroll
            diff = self.target_scroll_y - self.scroll_y
            if abs(diff) > 0.5:
                self.scroll_y += diff * 15 * dt
            else:
                self.scroll_y = self.target_scroll_y
                
            # Static Update
            for comp in self.static_components:
                comp.update(dt)
                
            # Scrollable Update
            # We must apply offset to check collisions for Buttons
            dy = int(self.scroll_y)
            
            for component in self.scrollable_components:
                # Move
                if hasattr(component, 'hitbox'):
                    original_y = component.hitbox.y
                    component.hitbox.y -= dy
                    
                    # Clip check: if button is outside view_rect, don't update (so can't click hidden buttons)
                    if self.view_rect.colliderect(component.hitbox):
                        component.update(dt)
                        
                    component.hitbox.y = original_y
                elif hasattr(component, 'update'):
                     component.update(dt) # Texts usually empty update

    def draw(self, screen: pg.Surface):
        if self.is_display:
            screen.blit(self.overlay_screen, (0, 0))
            screen.blit(self.overlay_img, self.overlay_img_rect)
            
            for component in self.static_components:
                component.draw(screen)
                
            # Draw scrollable area with clipping
            clip_rect = self.view_rect
            prev_clip = screen.get_clip()
            screen.set_clip(clip_rect)
            
            for component in self.scrollable_components:
                dy = int(self.scroll_y)
                
                if hasattr(component, 'hitbox'):
                    original_y = component.hitbox.y
                    component.hitbox.y -= dy
                    component.draw(screen)
                    component.hitbox.y = original_y
                elif hasattr(component, 'position'): # Text
                    original_pos = component.position
                    component.position = (original_pos[0], original_pos[1] - dy)
                    component.draw(screen)
                    component.position = original_pos
                    
                elif hasattr(component, 'rect'): 
                    if hasattr(component, 'rect'):
                        original_y = component.rect.y
                        component.rect.y -= dy
                        component.draw(screen)
                        component.rect.y = original_y
                    elif hasattr(component, 'y'): # Custom simple object?
                        original_y = component.y
                        component.y -= dy
                        component.draw(screen)
                        component.y = original_y
                    else:
                        component.draw(screen) # Fallback

                else:
                    component.draw(screen)
            
            screen.set_clip(prev_clip)

            # Draw scrollbar if needed
            if self.max_scroll > 0:
                bar_h = max(20, self.view_rect.height * (self.view_rect.height / (self.content_height + self.view_rect.height)))
                bar_y = self.view_rect.y + (self.scroll_y / self.max_scroll) * (self.view_rect.height - bar_h)
                pg.draw.rect(screen, (100, 100, 100), (self.view_rect.right - 10, self.view_rect.y, 8, self.view_rect.height))
                pg.draw.rect(screen, (200, 200, 200), (self.view_rect.right - 10, bar_y, 8, bar_h))

    def _create_static_ui(self):
        comps = []
        comps.append(Text("BACKPACK", "Minecraft.ttf", 50, self.px - 370, self.py - 190))
        comps.append(Text("Monsters", "Minecraft.ttf", 30, self.px - 370, self.py - 125, color=(60, 60, 60)))
        comps.append(Text("Items", "Minecraft.ttf", 30, self.px + 50, self.py - 125, color=(60, 60, 60)))
        comps.append(Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            self.px // 3 + 50, self.py // 3 + 420, 50, 50,
            lambda: self.display(False)
        ))
        return comps

    def refresh_content(self):
        self.scrollable_components = []
        
        bag_dict = self.game_manager.bag.to_dict()
        monster_list = bag_dict["monsters"]
        items_list = bag_dict["items"]
        
        # Refined Refresh Logic
        current_y_monsters = self.py - 90
        for i, monster in enumerate(monster_list):
             # Use Button for monster entry to allow clicking
             # We need a closure to capture 'i' correctly
             def make_callback(idx):
                 return lambda: self.use_item_on_monster(idx)
             
             element = POKEMON_ELEMENTS.get(monster["name"], Element.WATER)
             element_icon_path = f"ingame_ui/element_{element.name.lower()}.png"

             self.scrollable_components.extend([
                Button("UI/raw/UI_Flat_Banner04a.png", "UI/raw/UI_Flat_Banner04a.png", 
                       self.px - 375, current_y_monsters, 350, 60, make_callback(i)),
                Frame(get_pokemon_menu_sprite(monster["name"]), self.px - 350, current_y_monsters + 10, 40, 40),
                Frame(element_icon_path, self.px - 80, current_y_monsters + 20, 30, 30),
                Text(monster["name"], "Minecraft.ttf", 18, self.px - 300, current_y_monsters + 25),
                Text(f"HP: {monster['hp']}/{monster['max_hp']}", "Minecraft.ttf", 12, self.px - 200, current_y_monsters + 20, color=(255, 62, 23)),
                Text(f"Level: {monster['level']}", "Minecraft.ttf", 12, self.px - 200, current_y_monsters + 35, color=(16, 96, 201))
            ])
             current_y_monsters += 65
             
        current_y_items = self.py - 90
        for item in items_list:
            if item["count"] <= 0: continue
            
            name = item["name"]
            
            # Highlight if selected
            bg_image = "UI/raw/UI_Flat_Banner04a.png"
            if name == self.selected_item_name:
                bg_image = "UI/raw/UI_Flat_Banner03a.png" # Just using a different banner if available or same one?
                # Let's assume 03a exists or check resources?
                # Actually, let's just use the same one but maybe add a "Selected" text indicator or logic
                
            def make_select_callback(n):
                return lambda: self.select_item(n)

            # Check if selected to change appearance (optional, trying to keep it simple first)
            # If we don't have a different sprite, we can just add a Text "SELECTED"
            
            is_potion = "Potion" in name
            
            if is_potion:
                self.scrollable_components.append(
                    Button("UI/raw/UI_Flat_Banner04a.png", "UI/raw/UI_Flat_Banner04a.png" if name == self.selected_item_name else "UI/raw/UI_Flat_Banner04a.png", 
                           self.px + 50, current_y_items, 350, 60, make_select_callback(name))
                )
            else:
                # Non-selectable item
                self.scrollable_components.append(
                    Frame("UI/raw/UI_Flat_Banner04a.png", self.px + 50, current_y_items, 350, 60)
                )

            self.scrollable_components.extend([
                Frame(item["sprite_path"], self.px + 75, current_y_items + 15, 35, 35),
                Text(item["name"], "Minecraft.ttf", 24, self.px + 120, current_y_items + 20),
                Text(f"x {item['count']}", "Minecraft.ttf", 24, self.px + 320, current_y_items + 20)
            ])
            
            if name == self.selected_item_name:
                 self.scrollable_components.append(
                     Text("SELECTED", "Minecraft.ttf", 15, self.px + 350, current_y_items + 45, color=(255, 255, 0))
                 )

            current_y_items += 65
            
        # Calculate max content height
        max_y_content = max(current_y_monsters, current_y_items)
        self.content_height = max_y_content - (self.py - 90) + 50 # buffer
        self.max_scroll = max(0, self.content_height - self.view_rect.height)