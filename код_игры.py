import arcade
import random
import time
import threading

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
BACKGROUND_COLOR = (25, 30, 45)

class DraggableCard:
    def __init__(self, text, x, y, card_id):
        self.text = text
        self.x = x
        self.y = y
        self.dragging = False
        self.width = 70
        self.height = 70
        self.card_id = card_id
        
    def draw(self):
        color = (70, 110, 170) if not self.dragging else (200, 80, 80)
        arcade.draw_lbwh_rectangle_filled(
            self.x - 35, self.y - 35, 70, 70, color
        )
        arcade.draw_lbwh_rectangle_outline(
            self.x - 35, self.y - 35, 70, 70, (255,255,255), 2
        )
        font_size = 20 if len(self.text) > 2 else 26
        arcade.draw_text(self.text, self.x, self.y, (255,255,255), font_size,
                        anchor_x="center", anchor_y="center")
    
    def hit(self, x, y):
        return (self.x - 35 <= x <= self.x + 35 and
                self.y - 35 <= y <= self.y + 35)

class Game(arcade.View):
    def __init__(self):
        super().__init__()
        
        self.sections = {
            "МЕХАНИКА": [
                ("Путь при равномерном движении", ["S", "=", "v", "×", "t"]),
                ("Скорость при равномерном движении", ["v", "=", "S", "/", "t"]),
                ("Второй закон Ньютона", ["F", "=", "m", "×", "a"]),
                ("Кинетическая энергия", ["Eк", "=", "m", "×", "v", "^", "2", "/", "2"]),
                ("Потенциальная энергия", ["Eп", "=", "m", "×", "g", "×", "h"]),
                ("Импульс тела", ["p", "=", "m", "×", "v"]),
                ("Механическая работа", ["A", "=", "F", "×", "S"]),
                ("Мощность", ["P", "=", "A", "/", "t"]),
                ("Давление твёрдого тела", ["p", "=", "F", "/", "S"]),
                ("Сила Архимеда", ["Fа", "=", "ρ", "×", "g", "×", "V"]),
            ],
            "ЭЛЕКТРИЧЕСТВО": [
                ("Закон Ома", ["I", "=", "U", "/", "R"]),
                ("Мощность тока", ["P", "=", "I", "×", "U"]),
                ("Работа тока", ["A", "=", "I", "×", "U", "×", "t"]),
                ("Закон Джоуля-Ленца", ["Q", "=", "I", "^", "2", "×", "R", "×", "t"]),
                ("Последовательное соединение", ["R", "=", "R1", "+", "R2"]),
                ("Сопротивление проводника", ["R", "=", "ρ", "×", "l", "/", "S"]),
            ],
            "МКТ": [
                ("Кол-во теплоты при нагревании", ["Q", "=", "c", "×", "m", "×", "ΔT"]),
                ("Кол-во теплоты при сгорании", ["Q", "=", "q", "×", "m"]),
                ("Кол-во теплоты при плавлении", ["Q", "=", "λ", "×", "m"]),
                ("Уравнение Менделеева-Клапейрона", ["p", "×", "V", "=", "ν", "×", "R", "×", "T"]),
                ("Основное уравнение МКТ", ["p", "=", "1", "/", "3", "×", "n", "×", "m0", "×", "v", "^", "2"]),
            ],
            "ОПТИКА": [
                ("Оптическая сила линзы", ["D", "=", "1", "/", "F"]),
                ("Формула тонкой линзы", ["1", "/", "F", "=", "1", "/", "d", "+", "1", "/", "f"]),
                ("Увеличение линзы", ["Γ", "=", "f", "/", "d"]),
                ("Скорость света в среде", ["v", "=", "c", "/", "n"]),
                ("Закон преломления", ["n1", "×", "sinα", "=", "n2", "×", "sinβ"]),
            ],
        }
        
        self.all_symbols = ["S", "v", "t", "=", "/", "×", "F", "m", "a", "Eк", "Eп", "^", "2", 
                           "g", "h", "p", "A", "P", "I", "U", "R", "Q", "R1", "R2", "+", 
                           "c", "ΔT", "q", "λ", "V", "ν", "T", "D", "d", "f", "Γ", "n", "1",
                           "ρ", "l", "n1", "n2", "sinα", "sinβ", "m0", "Fа"]
        
        self.current_section = None
        self.current_formula_name = ""
        self.current_formula = []
        self.cards = []
        self.collected = []
        self.score = 0
        self.level = 0
        self.section_levels = []
        self.show_menu = True
        self.message = ""
        self.message_time = 0
        self.dragged_card = None
        self.time_left = 22
        self.start_time = 0
        self.waiting_for_next = False
        self.already_checked = False
        self.next_card_id = 0
        
    def get_next_id(self):
        self.next_card_id += 1
        return self.next_card_id
    
    def next_level_with_delay(self):
        """Задержка 2 секунды перед переходом на следующий уровень"""
        self.waiting_for_next = True
        self.already_checked = True
        self.message = "✓ ПРАВИЛЬНО! +1 очко"
        self.message_time = 60
        
        def delayed_load():
            time.sleep(2)
            self.level += 1
            self.load_level()
            self.waiting_for_next = False
            self.already_checked = False
        
        threading.Thread(target=delayed_load, daemon=True).start()
        
    def select_section(self, section):
        self.current_section = section
        self.section_levels = self.sections[section].copy()
        random.shuffle(self.section_levels)
        self.level = 0
        self.score = 0
        self.show_menu = False
        self.load_level()
    
    def load_level(self):
        if self.level >= len(self.section_levels):
            self.show_menu = True
            return
        
        self.current_formula_name, self.current_formula = self.section_levels[self.level]
        
        needed = self.current_formula.copy()
        extra = [s for s in self.all_symbols if s not in needed]
        random.shuffle(extra)
        extra = extra[:len(needed)]
        
        all_cards = needed + extra
        random.shuffle(all_cards)
        
        self.cards = []
        for i, sym in enumerate(all_cards):
            x = 120 + (i % 7) * 90
            y = 200 + (i // 7) * 80
            self.cards.append(DraggableCard(sym, x, y, self.get_next_id()))
        
        self.collected = []
        self.message = ""
        self.message_time = 0
        self.time_left = 22
        self.start_time = time.time()
        self.waiting_for_next = False
        self.already_checked = False
    
    def draw_menu(self):
        arcade.draw_text("ФИЗИКА: СОБЕРИ ФОРМУЛУ", SCREEN_WIDTH//2, 620, (255,255,255), 48, anchor_x="center")
        arcade.draw_text("Выбери раздел:", SCREEN_WIDTH//2, 540, (255,255,0), 28, anchor_x="center")
        
        y = 450
        for section in self.sections.keys():
            arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH//2 - 150, y - 25, 300, 50, (50,70,110))
            arcade.draw_text(section, SCREEN_WIDTH//2, y, (255,255,255), 22, anchor_x="center")
            y -= 70
    
    def draw_game(self):
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_left - int(elapsed))
        bar_width = 250
        arcade.draw_lbwh_rectangle_filled(50, SCREEN_HEIGHT - 50, bar_width, 15, (60,60,80))
        arcade.draw_lbwh_rectangle_filled(50, SCREEN_HEIGHT - 50, bar_width * (remaining/self.time_left), 15, 
                                          (0,200,0) if remaining > 7 else (200,0,0))
        arcade.draw_text(f"Время: {remaining} сек", 60, SCREEN_HEIGHT - 52, (255,255,255), 12)
        
        arcade.draw_text(f"Раздел: {self.current_section}", SCREEN_WIDTH - 300, SCREEN_HEIGHT - 40, (255,255,0), 16)
        arcade.draw_text(f"Уровень: {self.level+1}/{len(self.section_levels)}", SCREEN_WIDTH - 300, SCREEN_HEIGHT - 65, (255,255,255), 14)
        arcade.draw_text(f"Очки: {self.score}", SCREEN_WIDTH - 300, SCREEN_HEIGHT - 90, (255,255,0), 14)
        
        arcade.draw_text("Собери формулу:", SCREEN_WIDTH//2, 670, (255,255,255), 22, anchor_x="center")
        arcade.draw_text(self.current_formula_name, SCREEN_WIDTH//2, 630, (255,255,0), 24, anchor_x="center")
        
        zone_y = 480
        arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH//2 - 250, zone_y, 500, 70, (40,50,70))
        arcade.draw_lbwh_rectangle_outline(SCREEN_WIDTH//2 - 250, zone_y, 500, 70, (0,255,0), 3)
        arcade.draw_text("ПЕРЕТАЩИ СЮДА ЭЛЕМЕНТЫ", SCREEN_WIDTH//2, zone_y + 85, (0,255,0), 14, anchor_x="center")
        
        collected_text = " ".join(self.collected) if self.collected else "пусто"
        arcade.draw_text(collected_text, SCREEN_WIDTH//2, zone_y + 35, (255,255,255), 22, anchor_x="center", anchor_y="center")
        
        if self.message_time > 0:
            self.message_time -= 1
            arcade.draw_text(self.message, SCREEN_WIDTH//2, 430, (0,255,0) if "✓" in self.message else (255,100,100), 18, anchor_x="center")
        
        arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH-130, 20, 110, 45, (70,130,0))
        arcade.draw_text("ПРОВЕРИТЬ", SCREEN_WIDTH-75, 42, (255,255,255), 14, anchor_x="center")
        
        arcade.draw_lbwh_rectangle_filled(20, 20, 110, 45, (70,70,130))
        arcade.draw_text("МЕНЮ", 75, 42, (255,255,255), 16, anchor_x="center")
        
        arcade.draw_lbwh_rectangle_filled(145, 20, 100, 45, (130,70,70))
        arcade.draw_text("СБРОС", 195, 42, (255,255,255), 16, anchor_x="center")
        
        for card in self.cards:
            card.draw()
    
    def on_draw(self):
        self.clear()
        arcade.set_background_color(BACKGROUND_COLOR)
        
        if self.show_menu:
            self.draw_menu()
        else:
            self.draw_game()
    
    def on_mouse_press(self, x, y, button, modifiers):
        if self.show_menu:
            y_pos = 450
            for section in self.sections.keys():
                if SCREEN_WIDTH//2 - 150 <= x <= SCREEN_WIDTH//2 + 150 and y_pos - 25 <= y <= y_pos + 25:
                    self.select_section(section)
                    return
                y_pos -= 70
        else:
            if self.waiting_for_next:
                return
                
            if SCREEN_WIDTH-130 <= x <= SCREEN_WIDTH-20 and 20 <= y <= 65:
                self.check_formula(is_auto=False)
            elif 20 <= x <= 130 and 20 <= y <= 65:
                self.show_menu = True
            elif 145 <= x <= 245 and 20 <= y <= 65:
                self.load_level()
            else:
                for card in self.cards:
                    if card.hit(x, y):
                        self.dragged_card = card
                        self.dragged_card.dragging = True
                        break
    
    def on_mouse_motion(self, x, y, dx, dy):
        if self.dragged_card and self.dragged_card.dragging:
            self.dragged_card.x += dx
            self.dragged_card.y += dy
    
    def on_mouse_release(self, x, y, button, modifiers):
        if self.dragged_card:
            zone_y = 480
            if (SCREEN_WIDTH//2 - 250 <= self.dragged_card.x <= SCREEN_WIDTH//2 + 250 
                and zone_y <= self.dragged_card.y <= zone_y + 70):
                self.collected.append(self.dragged_card.text)
                self.cards.remove(self.dragged_card)
                
                if len(self.collected) == len(self.current_formula):
                    if sorted(self.collected) == sorted(self.current_formula):
                        self.next_level_with_delay()
            self.dragged_card.dragging = False
            self.dragged_card = None
    
    def check_formula(self, is_auto=False):
        if self.waiting_for_next or self.already_checked:
            return
        
        if sorted(self.collected) == sorted(self.current_formula):
            self.next_level_with_delay()
        else:
            if not is_auto:
                self.message = f"✗ НЕПРАВИЛЬНО!"
                self.message_time = 60
    
    def on_update(self, delta_time):
        if not self.show_menu and not self.waiting_for_next and not self.already_checked:
            elapsed = time.time() - self.start_time
            if elapsed >= self.time_left:
                if sorted(self.collected) == sorted(self.current_formula):
                    self.next_level_with_delay()
                else:
                    self.message = f"✗ ВРЕМЯ ВЫШЛО!"
                    self.message_time = 60
                    self.waiting_for_next = True
                    self.already_checked = True
                    
                    def wait_and_next():
                        time.sleep(5)
                        self.level += 1
                        self.load_level()
                        self.waiting_for_next = False
                        self.already_checked = False
                    
                    threading.Thread(target=wait_and_next, daemon=True).start()

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "ФИЗИКА: DRAG & DROP")
    game = Game()
    window.show_view(game)
    arcade.run()

if __name__ == "__main__":
    main()