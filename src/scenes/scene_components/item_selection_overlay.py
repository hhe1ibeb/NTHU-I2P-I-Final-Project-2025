import pygame as pg
from src.utils import GameSettings
from src.interface.components import Overlay, Text, Button, Frame
from src.core.managers.game_manager import GameManager

class ItemSelectionOverlay(Overlay):
    def __init__(self, game_manager: GameManager, on_select_item, on_close=None):
        self.game_manager = game_manager
        self.on_select_item = on_select_item
        self.on_close = on_close
        
        self.px = GameSettings.SCREEN_WIDTH // 2 - 200
        self.py = GameSettings.SCREEN_HEIGHT // 2 - 200
        
        super().__init__(
            "UI/raw/UI_Flat_Frame02a.png",
            self.px, self.py, 400, 400,
            160,
            default_display=False,
            components=[],
            exit_key=[] # Disable default exit key to handle it manually with callback
        )
        
        self.bg_components = [
             Text("Select Item", "Minecraft.ttf", 30, self.px + 110, self.py + 30),
             Button(
                "UI/button_back.png", "UI/button_back_hover.png",
                self.px + 175, self.py + 340, 50, 50,
                lambda: self.close()
             )
        ]

    def close(self):
        self.display(False)
        if self.on_close:
            self.on_close()

    def update(self, dt):
        super().update(dt)
        
        # Manual exit key handling
        from src.core.services import input_manager
        if self.is_display and input_manager.key_pressed(pg.K_ESCAPE):
            self.close()
            
    def display(self, show: bool):
        if show:
            self.refresh_items()
        super().display(show)
        
    def refresh_items(self):
        self.components = [] 
        # Re-add static bg components
        self.components.extend(self.bg_components)
        
        items = self.game_manager.bag.to_dict()["items"]
        
        current_y = self.py + 80
        valid_items = ["Heal Potion", "Strength Potion", "Defense Potion"]
        
        for item in items:
            name = item["name"]
            count = item["count"]
            
            if count > 0 and name in valid_items:
                # Create a button for the item
                # We'll use a frame as background and a translucent button on top or just a button with text?
                # Using a Frame and a transparent button is a good pattern if we had one.
                # Let's use a Text Button or similar.
                
                # Using a Frame for look
                self.components.append(Frame("UI/raw/UI_Flat_Banner04a.png", self.px + 50, current_y, 300, 50))
                
                # Icon
                self.components.append(Frame(item.get("sprite_path", "ingame_ui/potion.png"), self.px + 60, current_y + 5, 40, 40))
                
                # Text
                self.components.append(Text(f"{name} x{count}", "Minecraft.ttf", 20, self.px + 110, current_y + 15))
                
                # Invisible Button for clicking
                # Since we don't have an invisible button sprite easily, we can reuse the generic button or something matching.
                # Actually, let's just make a button that looks like the banner or just use the banner area logic if we could.
                # We'll use a small "USE" button next to it.
                
                # Capture name in closure
                def make_callback(n):
                    return lambda: self.on_select_item(n)
                
                self.components.append(Button(
                    "UI/button_play.png", "UI/button_play_hover.png",
                    self.px + 300, current_y + 5, 40, 40,
                    make_callback(name)
                ))
                
                current_y += 60
