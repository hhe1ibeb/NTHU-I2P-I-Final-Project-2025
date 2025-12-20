import pygame as pg
from src.interface.components import Overlay, Text, Button, Frame
from src.core.engine import GameSettings

class ShopOverlay(Overlay):
    page: int # 1 = buy, 2 = sell
    static_components: list
    
    def __init__(self, shop_npc, game_manager):
        self.shop_npc = shop_npc
        self.game_manager = game_manager
        self.bag = game_manager.bag
        self.page = 1
        
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        overlay_x = px // 3
        overlay_y = py // 3

        print(self.bag._items_data)

        super().__init__(
            "UI/raw/UI_Flat_Frame03a.png",
            overlay_x, overlay_y, 900, 500,
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
        
        # Viewport for scrolling (adjust based on UI frame)
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        overlay_x = px // 3
        overlay_y = py // 3
        # Static UI takes up ~120px from top.
        self.view_rect = pg.Rect(overlay_x + 20, overlay_y + 120, 860, 350)
        
        self.scrollable_components = []
        self._refresh_content(1)
    
    def _create_static_ui(self):
        components = []
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        overlay_x = px // 3
        overlay_y = py // 3

        buy_button_x = overlay_x + 60
        buy_button_y = overlay_y + 40
        buy_button = Button(
            "UI/raw/UI_Flat_Button01a_2.png","UI/raw/UI_Flat_Button01a_1.png",
            buy_button_x, buy_button_y, 150, 60,
            lambda: self._refresh_content(1)
        )
        buy_text = Text(
            "Buy", "Minecraft.ttf",
            30, buy_button_x + 50, buy_button_y + 20
        )
        components.extend([buy_button, buy_text])

        sell_button_x = overlay_x + 250
        sell_button_y = overlay_y + 40
        sell_button = Button(
            "UI/raw/UI_Flat_Button01a_2.png","UI/raw/UI_Flat_Button01a_1.png",
            sell_button_x, sell_button_y, 150, 60,
            lambda: self._refresh_content(2)
        )
        sell_text = Text(
            "Sell", "Minecraft.ttf",
            30, sell_button_x + 50, sell_button_y + 20
        )
        components.extend([sell_button, sell_text])

        coins_pic_x = overlay_x + 500
        coins_pic_y = overlay_y + 60
        coins_pic = Frame("ingame_ui/coin.png", coins_pic_x, coins_pic_y, 30, 30)
        
        # Lambda for dynamic text update
        coins_text_var = Text("", "Minecraft.ttf", 20, coins_pic_x + 40, coins_pic_y + 10, 
                              lambda: f"Coins: {self.bag.get_item_count('Coins')}")
        components.extend([coins_pic, coins_text_var])

        exit_button_x = overlay_x + 750
        exit_button_y = overlay_y + 40
        exit_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            exit_button_x, exit_button_y, 70, 70,
            lambda: self.display(False)
        )
        components.append(exit_button)

        return components
    
    def _create_buy_page(self):
        components = []
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        overlay_x = px // 3
        overlay_y = py // 3
        
        start_y = overlay_y + 120
        item_spacing = 60
        
        for i, item_data in enumerate(self.shop_npc.shop_items_data):
            row_y = start_y + i * item_spacing
            
            item_name = item_data["name"]
            price = item_data["price"]
            sprite_path = item_data.get("sprite_path", "ingame_ui/potion.png")
            
            # Icon
            icon = Frame(sprite_path, overlay_x + 50, row_y + 10, 40, 40)
            
            # Item Name (Shifted right)
            name_text = Text(f"{item_name}", "Minecraft.ttf", 25, overlay_x + 100, row_y + 15)
            
            # Price
            price_text = Text(f"${price}", "Minecraft.ttf", 25, overlay_x + 300, row_y + 15)
            
            # Buy Button
            def make_buy_action(name=item_name, cost=price):
                return lambda: self._buy_item(name, cost)
                
            buy_btn = Button(
                "UI/raw/UI_Flat_Button01a_2.png", "UI/raw/UI_Flat_Button01a_1.png",
                overlay_x + 500, row_y, 100, 50,
                make_buy_action()
            )
            buy_label = Text("Buy", "Minecraft.ttf", 20, overlay_x + 525, row_y + 15)
            
            components.extend([icon, name_text, price_text, buy_btn, buy_label])
        
        # Add Monsters to Buy List
        item_count = len(self.shop_npc.shop_items_data)
        for i, monster_data in enumerate(self.shop_npc.shop_monsters):
            row_y = start_y + (item_count + i) * item_spacing
            
            monster_name = monster_data["name"]
            price = monster_data.get("price", 2000)
            sprite_path = monster_data.get("sprite_path", "menu_sprites/menusprite1.png")
            
            # Icon
            icon = Frame(sprite_path, overlay_x + 50, row_y + 10, 40, 40)
            
            # Name (Shifted)
            name_text = Text(f"{monster_name}", "Minecraft.ttf", 25, overlay_x + 100, row_y + 15)
            
            # Price
            price_text = Text(f"${price}", "Minecraft.ttf", 25, overlay_x + 300, row_y + 15)
            
            # Buy Button
            def make_buy_monster_action(m=monster_data):
                return lambda: self._buy_monster(m)
                
            buy_btn = Button(
                "UI/raw/UI_Flat_Button01a_2.png", "UI/raw/UI_Flat_Button01a_1.png",
                overlay_x + 500, row_y, 100, 50,
                make_buy_monster_action()
            )
            buy_label = Text("Buy", "Minecraft.ttf", 20, overlay_x + 525, row_y + 15)
            
            components.extend([icon, name_text, price_text, buy_btn, buy_label])

        return components
    
    def _buy_item(self, item_name: str, price: int):
        current_coins = self.bag.get_item_count("Coins")
        if current_coins >= price:
            self.bag.remove_item("Coins", price)
            self.bag.add_item(item_name)
            # self._refresh_content(1) # Refresh to update coins display? Text updates automatically, but maybe good to re-check affordability if we added that logic
        else:
            print("Not enough coins!")

    def _buy_monster(self, monster_data: dict):
        price = monster_data.get("price", 2000)
        current_coins = self.bag.get_item_count("Coins")
        if current_coins >= price:
            self.bag.remove_item("Coins", price)
            self.bag.add_monster(monster_data)
            self._refresh_content(1) # Refresh to update coins display and potentially monster list if we show owned monsters on buy page
        else:
            print(f"Not enough coins to buy {monster_data['name']}!")

    def _sell_monster(self, index: int, price: int):
        if self.bag.remove_monster(index):
            self.bag.add_item("Coins", price)
            self._refresh_content(2)
        else:
            print("Could not sell monster")

    def _create_sell_page(self):
        components = []
        
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        overlay_x = px // 3
        overlay_y = py // 3
        
        start_y = overlay_y + 120
        item_spacing = 60
        
        current_row_idx = 0
        
        # Display Items from Bag
        sellable_items = [i for i in self.bag._items_data if i.get("count") > 0 and i.get("name") != "Coins"]
        
        for i, item in enumerate(sellable_items):
            row_y = start_y + current_row_idx * item_spacing
            item_name = item["name"]
            count = item["count"]
            
            buy_price = self.shop_npc.shop_items.get(item_name, self.shop_npc.shop_items.get(item_name, 10))
            sell_price = buy_price // 2
            
            # Icon
            sprite_path = item.get("sprite_path", "ingame_ui/potion.png")
            icon = Frame(sprite_path, overlay_x + 50, row_y + 10, 40, 40)
            
            # Name (Shifted)
            components.append(icon)
            components.append(Text(f"{item_name} x{count}", "Minecraft.ttf", 25, 
                                 overlay_x + 100, row_y + 15, color=(0, 0, 0)))
            
            components.append(Text(f"+${sell_price}", "Minecraft.ttf", 25, 
                                 overlay_x + 400, row_y + 15, color=(0, 100, 0)))
            
            def make_sell_item_action(n=item_name, p=sell_price):
                return lambda: self._sell_item(n, p)

            sell_btn = Button(
                "UI/raw/UI_Flat_Button01a_2.png", "UI/raw/UI_Flat_Button01a_1.png",
                overlay_x + 650, row_y, 100, 50,
                make_sell_item_action()
            )
            sell_label = Text("Sell", "Minecraft.ttf", 20, overlay_x + 675, row_y + 15)
            
            components.extend([sell_btn, sell_label])
            current_row_idx += 1

        # Display Monsters from Bag
        for i, monster in enumerate(self.bag._monsters_data):
            row_y = start_y + current_row_idx * item_spacing
            monster_name = monster["name"]
            level = monster.get("level", 1)
            
            # Simple sell price logic
            base_val = 2000
            for sm in self.shop_npc.shop_monsters:
                if sm["name"] == monster_name:
                    base_val = sm.get("price", 2000)
                    break
            sell_price = base_val // 2
            
            # Icon
            sprite_path = monster.get("sprite_path", "menu_sprites/menusprite1.png")
            icon = Frame(sprite_path, overlay_x + 50, row_y + 10, 40, 40)
            components.append(icon)
            
            components.append(Text(f"{monster_name} Lv.{level}", "Minecraft.ttf", 25, 
                                 overlay_x + 100, row_y + 15, color=(0, 0, 0)))
            
            components.append(Text(f"+${sell_price}", "Minecraft.ttf", 25, 
                                 overlay_x + 400, row_y + 15, color=(0, 100, 0)))
            
            def make_sell_monster_action(idx=i, p=sell_price):
                return lambda: self._sell_monster(idx, p)

            sell_btn = Button(
                "UI/raw/UI_Flat_Button01a_2.png", "UI/raw/UI_Flat_Button01a_1.png",
                overlay_x + 650, row_y, 100, 50,
                make_sell_monster_action()
            )
            sell_label = Text("Sell", "Minecraft.ttf", 20, overlay_x + 675, row_y + 15)
            
            components.extend([sell_btn, sell_label])
            current_row_idx += 1

        if not components:
            empty_text = Text("Bag is empty!", "Minecraft.ttf", 30, overlay_x + 50, start_y)
            components.append(empty_text)

        return components

    def _sell_item(self, item_name: str, price: int):
        if self.bag.remove_item(item_name, 1):
            self.bag.add_item("Coins", price)
            self._refresh_content(2) # Refresh to update list and counts
        else:
            print("Could not sell item")

    def _refresh_content(self, page: int):
        self.components = self.static_components.copy()
        if page == 1:
            self.components.extend(self._create_buy_page())
        elif page == 2:
            self.components.extend(self._create_sell_page())
        self.page = page

        # Scroll settings initialization moved to __init__
        pass
        
    def display(self, state: bool):
        if state:
            self.scroll_y = 0
            self.target_scroll_y = 0
            self._refresh_content(self.page)
        super().display(state)

    def update(self, dt):
        super().update(dt)
        from src.core.services import input_manager
        
        if self.is_display:
            if self.max_scroll > 0 and input_manager.mouse_wheel != 0:
                self.target_scroll_y -= input_manager.mouse_wheel * self.scroll_speed
                self.target_scroll_y = max(0, min(self.target_scroll_y, self.max_scroll))
            
            diff = self.target_scroll_y - self.scroll_y
            if abs(diff) > 0.5:
                self.scroll_y += diff * 15 * dt
            else:
                self.scroll_y = self.target_scroll_y
                
            for comp in self.static_components:
                comp.update(dt)
                
            dy = int(self.scroll_y)
            for component in self.scrollable_components:
                if hasattr(component, 'hitbox'):
                    original_y = component.hitbox.y
                    component.hitbox.y -= dy
                    if self.view_rect.colliderect(component.hitbox):
                        component.update(dt)
                    component.hitbox.y = original_y
                elif hasattr(component, 'update'):
                     component.update(dt)

    def draw(self, screen):
        if self.is_display:
            screen.blit(self.overlay_screen, (0, 0))
            screen.blit(self.overlay_img, self.overlay_img_rect)
            
            for component in self.static_components:
                component.draw(screen)
                
            clip_rect = self.view_rect
            prev_clip = screen.get_clip()
            screen.set_clip(clip_rect)
            
            dy = int(self.scroll_y)
            for component in self.scrollable_components:
                if hasattr(component, 'hitbox'):
                    original_y = component.hitbox.y
                    component.hitbox.y -= dy
                    component.draw(screen)
                    component.hitbox.y = original_y
                elif hasattr(component, 'position'):
                    original_pos = component.position
                    component.position = (original_pos[0], original_pos[1] - dy)
                    component.draw(screen)
                    component.position = original_pos
                elif hasattr(component, 'rect'):
                    original_y = component.rect.y
                    component.rect.y -= dy
                    component.draw(screen)
                    component.rect.y = original_y
                else:
                    component.draw(screen)
            
            screen.set_clip(prev_clip)

            if self.max_scroll > 0:
                bar_h = max(20, self.view_rect.height * (self.view_rect.height / (self.content_height + self.view_rect.height)))
                bar_y = self.view_rect.y + (self.scroll_y / self.max_scroll) * (self.view_rect.height - bar_h)
                pg.draw.rect(screen, (100, 100, 100), (self.view_rect.right - 10, self.view_rect.y, 8, self.view_rect.height))
                pg.draw.rect(screen, (200, 200, 200), (self.view_rect.right - 10, bar_y, 8, bar_h))

    def _refresh_content(self, page: int):
        self.scrollable_components = []
        if page == 1:
            self.scrollable_components.extend(self._create_buy_page())
        elif page == 2:
            self.scrollable_components.extend(self._create_sell_page())
        self.page = page
        
        # Calculate content height
        # Estimate based on last component's bottom position or count
        # Or easier iteration:
        max_y = self.view_rect.y
        for c in self.scrollable_components:
            bottom = 0
            if hasattr(c, 'hitbox'): bottom = c.hitbox.bottom
            elif hasattr(c, 'position'): bottom = c.position[1] + 20 # text height approx
            elif hasattr(c, 'rect'): bottom = c.rect.bottom
            if bottom > max_y: max_y = bottom
            
        self.content_height = max_y - self.view_rect.y + 50
        self.max_scroll = max(0, self.content_height - self.view_rect.height)