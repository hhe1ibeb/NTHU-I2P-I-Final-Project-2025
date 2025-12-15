from __future__ import annotations
import pygame as pg
from typing import Optional, Callable, List, Dict
from .component import UIComponent
from src.core.services import input_manager
from src.utils import Logger


class ChatOverlay(UIComponent):
    """Lightweight chat UI similar to Minecraft: toggle with a key, type, press Enter to send."""
    is_open: bool
    _input_text: str
    _cursor_timer: float
    _cursor_visible: bool
    _just_opened: bool
    _send_callback: Callable[[str], bool] | None    #  NOTE: This is a callable function, you need to give it a function that sends the message
    _get_messages: Callable[[int], list[dict]] | None # NOTE: This is a callable function, you need to give it a function that gets the messages
    _font_msg: pg.font.Font
    _font_input: pg.font.Font

    def __init__(
        self,
        send_callback: Callable[[str], bool] | None = None,
        get_messages: Callable[[int], list[dict]] | None = None,
        *,
        font_path: str = "assets/fonts/Minecraft.ttf"
    ) -> None:
        self.is_open = False
        self._input_text = ""
        self._cursor_timer = 0.0
        self._cursor_visible = True
        self._just_opened = False
        self._send_callback = send_callback
        self._get_messages = get_messages

        try:
            self._font_msg = pg.font.Font(font_path, 14)
            self._font_input = pg.font.Font(font_path, 14)
        except Exception:
            self._font_msg = pg.font.SysFont("Arial", 14)
            self._font_input = pg.font.SysFont("Arial", 14)

    def open(self) -> None:
        if not self.is_open:
            self.is_open = True
            self._cursor_timer = 0.0
            self._cursor_visible = True
            self._just_opened = True

    def close(self) -> None:
        self.is_open = False

    def _handle_typing(self) -> None:
        # Text Input
        if input_manager.text_input:
            self._input_text += input_manager.text_input
            
        # Backspace
        if input_manager.key_pressed(pg.K_BACKSPACE):
             self._input_text = self._input_text[:-1]

        # Delete
        if input_manager.key_pressed(pg.K_DELETE):
             self._input_text = self._input_text[:-1]

        # Enter to send
        if input_manager.key_pressed(pg.K_RETURN) or input_manager.key_pressed(pg.K_KP_ENTER):
            txt = self._input_text.strip()
            if txt and self._send_callback:
                ok = False
                try:
                    ok = self._send_callback(txt)
                except Exception:
                    ok = False
                if ok:
                    self._input_text = ""
            self.close() # Close after sending? Or keep open? User preference usually close.
            # If we want to keep it open, remove self.close()
            # But typically single-line chat closes on enter.
            self.close()

    def update(self, dt: float) -> None:
        if not self.is_open:
            return
        # Close on Escape
        if input_manager.key_pressed(pg.K_ESCAPE):
            self.close()
            return
        # Typing
        if self._just_opened:
            self._just_opened = False
        else:
            self._handle_typing()
        # Cursor blink
        self._cursor_timer += dt
        if self._cursor_timer >= 0.5:
            self._cursor_timer = 0.0
            self._cursor_visible = not self._cursor_visible

    def draw(self, screen: pg.Surface) -> None:
        # Always draw recent messages faintly, even when closed
        msgs = self._get_messages(8) if self._get_messages else []
        sw, sh = screen.get_size()
        x = 10
        y_bottom = sh - 100
        
        # Prepare content to draw (wrap text)
        lines_to_draw = []
        container_w = max(100, int((sw - 20) * 0.6))
        max_text_w = container_w - 20
        
        if msgs:
             for m in msgs:
                sender = str(m.get("from", ""))
                text = str(m.get("text", ""))
                full_text = f"{sender}: {text}"
                
                # Simple char wrapping
                words = full_text.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    w, h = self._font_msg.size(test_line)
                    if w <= max_text_w:
                        current_line = test_line
                    else:
                        if current_line:
                            lines_to_draw.append(current_line)
                        current_line = word
                if current_line:
                    lines_to_draw.append(current_line)
                    
        # Keep only last 8 wrapped lines
        lines_to_draw = lines_to_draw[-8:]
        
        # Calculate background height
        line_height = self._font_msg.get_height() + 4
        total_h = len(lines_to_draw) * line_height + 10
        y_start = y_bottom - total_h
        
        # Draw background
        if lines_to_draw:
            bg = pg.Surface((container_w, total_h), pg.SRCALPHA)
            bg.fill((0, 0, 0, 90 if self.is_open else 60))
            screen.blit(bg, (x, y_start))
            
            # Draw text
            draw_y = y_start + 5
            for line in lines_to_draw:
                surf = self._font_msg.render(line, True, (255, 255, 255))
                screen.blit(surf, (x + 10, draw_y))
                draw_y += line_height

        # If not open, skip input field
        if not self.is_open:
            return
            
        # Input box
        box_h = 28
        box_w = max(100, int((sw - 20) * 0.6))
        box_y = sh - box_h - 6
        # Background box
        bg2 = pg.Surface((box_w, box_h), pg.SRCALPHA)
        bg2.fill((0, 0, 0, 160))
        screen.blit(bg2, (x, box_y))
        
        # Text
        txt = self._input_text
        text_surf = self._font_input.render(txt, True, (255, 255, 255))
        
        # Clip input text if too long
        # Simple scroll: show end
        input_view_w = box_w - 16
        if text_surf.get_width() > input_view_w:
             # Just drawing right aligned-ish by cropping logic? 
             # Easier: just don't draw start.
             # Or let's just let it overflow clip
             area = pg.Rect(text_surf.get_width() - input_view_w, 0, input_view_w, text_surf.get_height())
             screen.blit(text_surf, (x + 8, box_y + 4), area)
             caret_x = x + 8 + input_view_w + 2
        else:
             screen.blit(text_surf, (x + 8, box_y + 4))
             caret_x = x + 8 + text_surf.get_width() + 2

        # Caret
        if self._cursor_visible:
            cy = box_y + 4
            pg.draw.rect(screen, (255, 255, 255), pg.Rect(caret_x, cy, 2, box_h - 8))