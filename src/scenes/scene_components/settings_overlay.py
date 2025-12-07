import pygame as pg

from src.utils import GameSettings
from src.core import GameManager
from src.core.services import sound_manager
from src.interface.components import Text, Slider, Button, Toggle, Overlay

class SettingsOverlay(Overlay):
    def __init__(self, on_save, on_load):
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2

        title_text = Text(
            "SETTINGS", 
            "Minecraft.ttf",
            50, px - 350, py - 180
        )

        volume_text = Text(
            "Volume: ", 
            "Minecraft.ttf",
            30, px - 350, py - 100
        )

        volume_amount = Text(
            str(GameSettings.AUDIO_VOLUME * 100),
            "Minecraft.ttf", 
            30, px - 200, py - 100, 
            lambda: f"{int(GameSettings.AUDIO_VOLUME * 100)}"
        )

        volume_slider = Slider(
            "UI/raw/UI_Flat_BarFill01f.png", "UI/raw/UI_Flat_Handle03a.png",
            px - 350, py - 50, 700, 20, 30, 50,
            current_value=GameSettings.AUDIO_VOLUME, 
            max_value=1.0,
            on_change=lambda v: sound_manager.set_global_volume(v)
        )

        audio_mute_text = Text(
            "Mute: ", 
            "Minecraft.ttf",
            30, px - 350, py
        )

        state = lambda: "On" if GameSettings.AUDIO_MUTED else "Off"
        audio_mute_indicate = Text(
            "On" if GameSettings.AUDIO_MUTED else "Off", 
            "Minecraft.ttf",
            30, px - 270, py,
            state
        )

        audio_mute_toggle = Toggle(
            "UI/raw/UI_Flat_ToggleOff03a.png", "UI/raw/UI_Flat_ToggleOn03a.png",
            px - 200, py - 5, 40, 40,
            lambda: GameSettings.AUDIO_MUTED,
            toggled_on=lambda: sound_manager.set_mute(True),
            toggled_off=lambda: sound_manager.set_mute(False)
        )

        save_button = Button(
            "UI/button_save.png", "UI/button_save_hover.png",
            px - 50, py + 70, 60, 60,
            on_save
        )

        save_text = Text(
            "Save",
            "Minecraft.ttf",
            24, 
            px - 50, py + 130
        )

        load_button = Button(
            "UI/button_load.png", "UI/button_load_hover.png",
            px + 50, py + 70, 60, 60,
            on_load
        )

        load_text = Text(
            "Load",
            "Minecraft.ttf",
            24, 
            px + 50, py + 130
        )

        exit_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px // 3 + 50, py // 3 + 400, 50, 50,
            lambda: self.display(False)
        )
        exit_text = Text(
            "Press ESC to exit",
            "Minecraft.ttf",
            24, 
            px // 3 + 120, py // 3 + 415,
            color=(50, 50, 50)
        )
        
        components=[
            title_text, 
            volume_text, volume_amount, volume_slider,
            audio_mute_text, audio_mute_indicate, audio_mute_toggle, 
            save_button, load_button,
            save_text, load_text,
            exit_button, exit_text
        ]

        self.components = components

        super().__init__(
            "UI/raw/UI_Flat_Frame03a.png", 
            px // 3, py // 3, 900, 500,
            160,
            default_display=False,
            components=components,
            exit_key=[pg.K_ESCAPE]
        )
    
    def update(self, dt):
        return super().update(dt)

    def draw(self, screen):
        return super().draw(screen)
    
    def display(self, state):
        return super().display(state)