from __future__ import annotations
import pygame as pg

from src.utils import GameSettings
from src.sprites import BackgroundSprite
from src.core.services import scene_manager, sound_manager, input_manager
from src.interface.components import Button, Overlay, Toggle, Text, Slider

class SettingScene:
    title_text: Text
    volume_text: Text
    volume_amount: Text
    volume_slider: Slider
    audio_mute_text: Text
    audio_mute_indicate: Text
    audio_mute_toggle: Toggle
    exit_button: Button
    settings_overlay: Overlay

    def __init__(self) -> None:
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")

        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2

        self.title_text = Text(
            "SETTINGS", 
            "Minecraft.ttf",
            50, px - 350, py - 180
        )

        self.volume_text = Text(
            "Volume: ", 
            "Minecraft.ttf",
            30, px - 350, py - 100
        )

        self.volume_amount = Text(
            str(GameSettings.AUDIO_VOLUME * 100),
            "Minecraft.ttf", 
            30, px - 200, py - 100, 
            lambda: f"{int(GameSettings.AUDIO_VOLUME * 100)}"
        )

        self.volume_slider = Slider(
            "UI/raw/UI_Flat_BarFill01f.png", "UI/raw/UI_Flat_Handle03a.png",
            px - 350, py - 50, 700, 20, 30, 50,
            current_value=GameSettings.AUDIO_VOLUME, 
            max_value=1.0,
            on_change=lambda v: sound_manager.set_global_volume(v)
        )

        self.audio_mute_text = Text(
            "Mute: ", 
            "Minecraft.ttf",
            30, px - 350, py
        )
        
        state = lambda: "On" if GameSettings.AUDIO_MUTED else "Off"
        self.audio_mute_indicate = Text(
            "On" if GameSettings.AUDIO_MUTED else "Off", 
            "Minecraft.ttf",
            30, px - 270, py,
            state
        )

        self.audio_mute_toggle = Toggle(
            "UI/raw/UI_Flat_ToggleOff03a.png", "UI/raw/UI_Flat_ToggleOn03a.png",
            px - 200, py - 5, 40, 40,
            lambda: GameSettings.AUDIO_MUTED,
            toggled_on=lambda: sound_manager.set_mute(True),
            toggled_off=lambda: sound_manager.set_mute(False)
        )

        exit_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px // 3 + 50, py // 3 + 400, 50, 50,
            lambda: scene_manager.change_scene("menu")
        )
        exit_text = Text(
            "Press ESC to exit",
            "Minecraft.ttf",
            24, 
            px // 3 + 120, py // 3 + 415,
            color=(50, 50, 50)
        )

        self.settings_overlay = Overlay(
            "UI/raw/UI_Flat_Frame03a.png", 
            px // 3, py // 3, 900, 500,
            160,
            default_display=True,
            components=[exit_button, exit_text],
        )

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def update(self, dt: float) -> None:
        if input_manager.key_down(pg.K_ESCAPE):
            scene_manager.change_scene("menu")
        self.volume_slider.update(dt)
        self.volume_amount.update(dt)
        self.audio_mute_toggle.update(dt)
        self.audio_mute_indicate.update(dt)
        self.settings_overlay.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        self.settings_overlay.draw(screen)

        self.title_text.draw(screen)
        self.volume_text.draw(screen)
        self.volume_amount.draw(screen)
        self.volume_slider.draw(screen)
        self.audio_mute_text.draw(screen)
        self.audio_mute_indicate.draw(screen)
        self.audio_mute_toggle.draw(screen)