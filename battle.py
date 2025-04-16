import pygame, random, math, time
from animations import AnimationHandler  # Import module hoạt ảnh đã chỉnh sửa
from characters import Character  # Đảm bảo class Character được import (nếu cần)

TEXT_UPDATE_INTERVAL = 0.5  

class Battle:
    def __init__(self, screen, team_left, team_right, manager=None):
        self.screen = screen
        self.manager = manager
        self.font = pygame.font.SysFont("Arial", 24)
        self.turn_font = pygame.font.SysFont("Arial", 16)
        
        self.team_left = team_left[:]  
        self.team_right = team_right[:]
        self.all_characters = self.team_left + self.team_right
        self.position_teams()
        
        # Turn order (sắp xếp dựa trên SPD giảm dần)
        self.turn_order = sorted(self.all_characters, key=lambda c: c.SPD, reverse=True)
        self.attacker = None
        self.target = None

        self.max_energy = 5
        self.energy_left = 3
        self.energy_right = 3

        self.prediction_phase = True
        self.prediction = None
        self.battle_over = False
        
        self._message = "Dự đoán đội thắng: Nhấn L (Đội Trái) hoặc R (Đội Phải)"
        self.message = self.font.render(self._message, True, (0, 0, 0))
        self.last_text_update = time.time()

        # --- Tích hợp AnimationHandler ---
        self.animation_handler = AnimationHandler(self.screen)

        # --- CHỈNH SỬA: Load background riêng cho battle
        try:
            self.battle_bg = pygame.image.load("Resource/battle-bg.png").convert()
        except Exception as e:
            print("Không tải được battle-bg.png:", e)
            self.battle_bg = None

    def position_teams(self):
        screen_h = self.screen.get_height()
        left_x = 100  
        num_left = len(self.team_left)
        gap_left = (screen_h - 200) // (num_left + 1) if num_left else 0
        for idx, char in enumerate(self.team_left):
            y = 100 + (idx + 1) * gap_left
            char.pos = (left_x, y)
            char.rect.topleft = char.pos

        right_x = self.screen.get_width() - 180  
        num_right = len(self.team_right)
        gap_right = (screen_h - 200) // (num_right + 1) if num_right else 0
        for idx, char in enumerate(self.team_right):
            y = 100 + (idx + 1) * gap_right
            char.pos = (right_x, y)
            char.rect.topleft = char.pos

    def redraw_screen(self):
        """
        Callback để các hàm animation vẽ lại toàn bộ giao diện game.
        """
        self.draw()

    def handle_event(self, event):
        if self.battle_over:
            return
        if self.prediction_phase:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    self.prediction = "left"
                    self.prediction_phase = False
                    self._message = "Dự đoán của bạn: Đội Trái. Trận chiến bắt đầu!"
                elif event.key == pygame.K_r:
                    self.prediction = "right"
                    self.prediction_phase = False
                    self._message = "Dự đoán của bạn: Đội Phải. Trận chiến bắt đầu!"
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.battle_over = True

    def get_global_status(self):
        status_list = []
        for char in self.all_characters:
            status = f"{char.name}: HP {char.HP}/{char.max_HP}, BP {char.BP}"
            if hasattr(char, "dot"):
                status += f", DOT {char.dot}"
            if hasattr(char, "is_summon") and char.is_summon:
                status += f", Turn {char.summon_turn_count}"
            status_list.append(status)
        return " || ".join(status_list)

    def update_message(self):
        if time.time() - self.last_text_update > TEXT_UPDATE_INTERVAL:
            global_status = self.get_global_status()
            combined_message = self._message + " || " + global_status
            self.message = self.font.render(combined_message, True, (0, 0, 0))
            self.last_text_update = time.time()
            print("[DEBUG STATUS]", combined_message)

    def apply_dot_damage(self):
        dot_message = ""
        for char in self.all_characters:
            if hasattr(char, "dot") and char.dot > 0:
                dot_damage = char.dot * 50
                char.HP = max(char.HP - dot_damage, 0)
                dot_message += f"{char.name} nhận {dot_damage} DOT; "
        if dot_message:
            self._message += " | DOT: " + dot_message
            print("[DEBUG DOT]", dot_message)

    def update(self):
        if self.prediction_phase or self.battle_over:
            self.update_message()
            return

        self.apply_dot_damage()

        # Lấy attacker từ đầu turn_order
        self.attacker = self.turn_order[0]

        # Nếu attacker là summon, gọi summon_skill()
        if hasattr(self.attacker, "is_summon") and self.attacker.is_summon:
            if self.attacker.summon_skill(self.get_enemies(self.attacker)):
                self._message = f"{self.attacker.name} thực hiện hành động summon (Turn {self.attacker.summon_turn_count})."
                self.turn_order.append(self.turn_order.pop(0))
                self.update_message()
                self.check_battle_over()
                return

        if getattr(self.attacker, 'penalized', False) and self.attacker.penalty_duration > 0:
            self.attacker.penalty_duration = 0
            if hasattr(self.attacker, 'original_SPD'):
                self.attacker.SPD = self.attacker.original_SPD
            if hasattr(self.attacker, 'original_DEF'):
                self.attacker.DEF = self.attacker.original_DEF
            self.attacker.BP = 200
            self.attacker.penalized = False
            self._message = f"{self.attacker.name} bị hủy lượt do hết BP!"
            print(self._message)
            self.turn_order.append(self.turn_order.pop(0))
            self.update_message()
            return

        # Sử dụng skill đặc biệt nếu có năng lượng
        if self.attacker.energy_cost_available():
            # Xử lý đội trái
            if self.attacker in self.team_left and self.energy_left > 0:
                if self.attacker.use_skill_special(self.get_allies(self.attacker), self.get_enemies(self.attacker)):
                    print(f"{self.attacker.name} sử dụng skill: {self.attacker.skill_type}")
                    self.energy_left -= 1
                    self._message = f"{self.attacker.name} sử dụng skill: {self.attacker.skill_type}"
                    self.target = (self.attacker.skill_target if hasattr(self.attacker, 'skill_target')
                                   else random.choice(self.get_enemies(self.attacker)))
                    
                    # Nếu Castorice dùng skill triệu hồi, tạo summon ngay sau khi sử dụng skill
                    if self.attacker.name == "Castorice" and getattr(self.attacker, "summon_pending", False):
                        summoned = Character(f"{self.attacker.name}_Summon", self.attacker.role,
                                               self.attacker.max_HP, self.attacker.DEF, self.attacker.ATK, self.attacker.SPD)
                        self.attacker.summoned = summoned
                        self.attacker.summon_pending = False
                        offset = 90
                        summoned.pos = (self.attacker.pos[0] + offset, self.attacker.pos[1])
                        summoned.rect.topleft = summoned.pos
                        if self.attacker in self.team_left:
                            self.team_left.append(summoned)
                        else:
                            self.team_right.append(summoned)
                        self.all_characters.append(summoned)
                        print(f"{self.attacker.name}: Triệu hồi {summoned.name} thành công!")
                    
                    # Gọi animation tương ứng dựa trên tên nhân vật
                    name_lower = self.attacker.name.lower()
                    if name_lower == "kafka":
                        self.animation_handler.animate_kafka_skill(self.attacker, self.target.pos, redraw_callback=self.redraw_screen)
                    elif name_lower == "sunday":
                        self.animation_handler.animate_sunday_buff(self.target, redraw_callback=self.redraw_screen)
                    elif name_lower == "march7th" and self.attacker.skill_type == "march_shield":
                        # March7th skill không cần animation riêng
                        pass
                    elif name_lower == "castorice" and self.attacker.skill_type in ["castorice_summon", "castorice_attack_all"]:
                        # Nếu là sử dụng skill của Castorice, gọi animation skill
                        # Giả sử bạn xác định main_target_pos và 2 side_target_pos phù hợp (có thể dùng self.target.pos cho main)
                        if self.target is None:
                            self.target = random.choice(self.get_enemies(self.attacker))

                        main_target_pos = self.target.pos
                        # Với đơn giản, ta dùng vị trí random cho 2 target phụ (có thể cải tiến sau)
                        side_target1_pos = (self.target.pos[0] + 50, self.target.pos[1])
                        side_target2_pos = (self.target.pos[0] - 50, self.target.pos[1])
                        self.animation_handler.animate_castorice_skill(self.attacker, main_target_pos, side_target1_pos, side_target2_pos, redraw_callback=self.redraw_screen)
                    self.update_message()
                    self.turn_order.append(self.turn_order.pop(0))
                    self.check_battle_over()
                    return
            # Xử lý đội phải
            elif self.attacker in self.team_right and self.energy_right > 0:
                if self.attacker.use_skill_special(self.get_allies(self.attacker), self.get_enemies(self.attacker)):
                    print(f"{self.attacker.name} sử dụng skill: {self.attacker.skill_type}")
                    self.energy_right -= 1
                    self._message = f"{self.attacker.name} sử dụng skill: {self.attacker.skill_type}"
                    self.target = (self.attacker.skill_target if hasattr(self.attacker, 'skill_target')
                                   else random.choice(self.get_enemies(self.attacker)))
                    
                    if self.attacker.name == "Castorice" and getattr(self.attacker, "summon_pending", False):
                        summoned = Character(f"{self.attacker.name}_Summon", self.attacker.role,
                                               self.attacker.max_HP, self.attacker.DEF, self.attacker.ATK, self.attacker.SPD)
                        self.attacker.summoned = summoned
                        self.attacker.summon_pending = False
                        offset = 90
                        summoned.pos = (self.attacker.pos[0] + offset, self.attacker.pos[1])
                        summoned.rect.topleft = summoned.pos
                        if self.attacker in self.team_left:
                            self.team_left.append(summoned)
                        else:
                            self.team_right.append(summoned)
                        self.all_characters.append(summoned)
                        print(f"{self.attacker.name}: Triệu hồi {summoned.name} thành công!")
                    
                    name_lower = self.attacker.name.lower()
                    if name_lower == "kafka":
                        self.animation_handler.animate_kafka_skill(self.attacker, self.target.pos, redraw_callback=self.redraw_screen)
                    elif name_lower == "sunday":
                        self.animation_handler.animate_sunday_buff(self.target, redraw_callback=self.redraw_screen)
                    elif name_lower == "march7th" and self.attacker.skill_type == "march_shield":
                        pass
                    elif name_lower == "castorice" and self.attacker.skill_type in ["castorice_summon", "castorice_attack_all"]:
                        # Đảm bảo rằng self.target có giá trị
                        if self.target is None:
                            self.target = random.choice(self.get_enemies(self.attacker))
        
                        main_target_pos = self.target.pos
                        side_target1_pos = (self.target.pos[0] + 50, self.target.pos[1])
                        side_target2_pos = (self.target.pos[0] - 50, self.target.pos[1])
                        self.animation_handler.animate_castorice_skill(self.attacker, main_target_pos, side_target1_pos, side_target2_pos, redraw_callback=self.redraw_screen)

                    self.update_message()
                    self.turn_order.append(self.turn_order.pop(0))
                    self.check_battle_over()
                    return

        # --- Phần tấn công thông thường ---
        self.animation_type = self.attacker.get_normal_attack_type()
        self.target = random.choice(self.get_enemies(self.attacker))
        
        # Gọi animation tấn công dựa trên tên nhân vật (so sánh lower-case)
        name_lower = self.attacker.name.lower()
        if name_lower == "kafka":
            self.animation_handler.animate_kafka_attack(self.attacker, self.target.pos, redraw_callback=self.redraw_screen)
        elif name_lower == "sunday":
            self.animation_handler.animate_sunday_attack(self.attacker, self.target.pos, redraw_callback=self.redraw_screen)
        elif name_lower == "yunli":
            self.animation_handler.animate_yunli_attack(self.attacker, self.target.pos, redraw_callback=self.redraw_screen)
        elif name_lower == "march7th":
            self.animation_handler.animate_march7th_attack(self.attacker, self.target.pos, redraw_callback=self.redraw_screen)
        elif name_lower == "lynx":
            self.animation_handler.animate_lynx_attack(self.attacker, self.target.pos, redraw_callback=self.redraw_screen)
        elif name_lower == "ruan mei":
            self.animation_handler.animate_ruanmei_attack(self.attacker, self.target.pos, redraw_callback=self.redraw_screen)
        elif name_lower == "fuxuan":
            self.animation_handler.animate_fuxuan_attack(self.attacker, self.target.pos, redraw_callback=self.redraw_screen)
        elif name_lower == "castorice":
            self.animation_handler.animate_castorice_attack(self.attacker, self.target.pos, redraw_callback=self.redraw_screen)
        elif name_lower == "castorice_summon":
            # Nếu attacker là summon của Castorice, gọi animation summon attack
            # Giả sử bạn cung cấp danh sách vị trí target cho summon (có thể là vị trí của các kẻ địch)
            target_positions = [enemy.pos for enemy in self.get_enemies(self.attacker)]
            attack_count = self.attacker.summon_turn_count + 1  # hoặc một logic khác
            self.animation_handler.animate_castorice_summon_attack(self.attacker, target_positions, attack_count, redraw_callback=self.redraw_screen)
        else:
            # Nếu không có animation riêng, chỉ gọi redraw
            self.redraw_screen()

        # --- Tính sát thương với buff giáp (march_shield) ---
        incoming_damage = max(30, int(self.attacker.ATK * 0.08) - self.target.DEF // 100)
        if random.random() < self.attacker.CR:
            incoming_damage = int(incoming_damage * (1 + self.attacker.CD))
            self._message += f" | Crit từ {self.attacker.name}!"
        
        if self.target.shield > 0:
            absorbed = min(self.target.shield, incoming_damage)
            self.target.shield -= absorbed
            incoming_damage -= absorbed
            self._message += f" | {self.target.name} hấp thụ {absorbed} sát thương từ shield!"
        
        counter_trigger = False
        if self.target.march_shield > 0:
            counter_trigger = True
            if incoming_damage <= self.target.march_shield:
                self.target.march_shield -= incoming_damage
                incoming_damage = 0
            else:
                incoming_damage -= self.target.march_shield
                self.target.march_shield = 0

        if incoming_damage > 0:
            self.target.HP -= incoming_damage
        
        if self.target.HP <= 0:
            self.target.HP = 0
            self._message = f"{self.attacker.name} tấn công {self.target.name} (-{incoming_damage} HP) -> {self.target.name} bị loại!"
            if self.target in self.team_left:
                self.team_left.remove(self.target)
            elif self.target in self.team_right:
                self.team_right.remove(self.target)
            if self.target in self.turn_order:
                self.turn_order.remove(self.target)
            if (self.target.name == "Castorice" and hasattr(self.target, 'summoned') and self.target.summoned):
                castorice_summon = self.target.summoned
                if castorice_summon in self.team_left:
                    self.team_left.remove(castorice_summon)
                elif castorice_summon in self.team_right:
                    self.team_right.remove(castorice_summon)
                if castorice_summon in self.turn_order:
                    self.turn_order.remove(castorice_summon)
                self._message += f" | {castorice_summon.name} (summon của Castorice) cũng bị loại!"
        else:
            self._message = f"{self.attacker.name} tấn công {self.target.name} (-{incoming_damage} HP)"
            self.target.BP = max(0, self.target.BP - 45)
            if self.target.BP == 0 and not getattr(self.target, 'penalized', False):
                self.target.penalized = True
                self.target.penalty_duration = 1
                self.target.original_SPD = self.target.SPD
                self.target.original_DEF = self.target.DEF
                self.target.SPD = int(self.target.SPD * 0.7)
                self.target.DEF = int(self.target.DEF * 0.9)
                self._message += f" | {self.target.name} hết BP: bị phạt!"
        print(f"{self.attacker.name} tấn công {self.target.name} gây {incoming_damage} sát thương.")

        if counter_trigger:
            march = None
            for c in self.get_allies(self.target):
                if c.name.lower() == "march7th":
                    march = c
                    break
            if march is not None and march.HP > 0:
                print(f"{march.name} phản đòn {self.attacker.name} nhờ buff giáp!")
                self.animation_handler.animate_march7th_counter(march, self.attacker.pos, redraw_callback=self.redraw_screen)
                counter_damage = int(march.ATK * 0.8) - self.attacker.DEF // 100
                counter_damage = int(counter_damage * 0.95)  # giảm sát thương 5%
                counter_damage = max(20, counter_damage)
                self.attacker.HP = max(self.attacker.HP - counter_damage, 0)
                self._message += f" | {march.name} phản đòn gây {counter_damage} sát thương cho {self.attacker.name}!"
                print(f"{march.name} phản đòn {self.attacker.name} gây {counter_damage} sát thương.")
        
        if self.attacker in self.team_left and self.energy_left < self.max_energy:
            self.energy_left += 1
        elif self.attacker in self.team_right and self.energy_right < self.max_energy:
            self.energy_right += 1

        if (self.attacker.name == "Castorice" and hasattr(self.attacker, 'summoned') and self.attacker.summoned):
            summon = self.attacker.summoned
            offset = 90
            summon.pos = (self.attacker.pos[0] + offset, self.attacker.pos[1])
            summon.rect.topleft = summon.pos
        
        self.turn_order.append(self.turn_order.pop(0))
        self.update_message()
        self.check_battle_over()

    def check_battle_over(self):
        if not self.team_left or not self.team_right:
            self.battle_over = True
            winner = "left" if not self.team_left else "right"
            if self.prediction is not None:
                if self.prediction == winner:
                    self._message += " | Dự đoán của bạn đúng!"
                else:
                    self._message += " | Dự đoán của bạn sai!"
            print(f"Kết quả trận đấu: Đội {winner} thắng.")
            self.update_message()

    def get_allies(self, character):
        return self.team_left if character in self.team_left else self.team_right

    def get_enemies(self, character):
        return self.team_right if character in self.team_left else self.team_left

    def draw_turn_order(self):
        bar_height = 80
        y_pos = self.screen.get_height() - bar_height
        pygame.draw.rect(self.screen, (220, 220, 220), (0, y_pos, self.screen.get_width(), bar_height))
        gap = 10
        icon_size = 50
        x_pos = gap
        for idx, c in enumerate(self.turn_order):
            icon = pygame.transform.scale(c.image, (icon_size, icon_size))
            self.screen.blit(icon, (x_pos, y_pos + (bar_height - icon_size) // 2))
            timer_text = self.turn_font.render(str(c.SPD), True, (0, 0, 0))
            self.screen.blit(timer_text, (x_pos, y_pos + (bar_height - icon_size) // 2 + icon_size))
            if idx == 0:
                pygame.draw.rect(self.screen, (255, 0, 0),
                                 (x_pos, y_pos + (bar_height - icon_size) // 2, icon_size, icon_size), 3)
            x_pos += icon_size + gap

    def draw_energy_bars(self):
        bar_width = 150
        bar_height = 20
        padding = 20

        left_bar = pygame.Rect(padding, padding, bar_width, bar_height)
        pygame.draw.rect(self.screen, (200,200,200), left_bar)
        filled_width = int((self.energy_left / self.max_energy) * bar_width)
        pygame.draw.rect(self.screen, (0, 128, 0), pygame.Rect(padding, padding, filled_width, bar_height))
        left_text = self.turn_font.render(f"Chiến kỹ: {self.energy_left}/{self.max_energy}", True, (0,0,0))
        self.screen.blit(left_text, (padding, padding + bar_height + 5))

        right_bar = pygame.Rect(self.screen.get_width() - bar_width - padding, padding, bar_width, bar_height)
        pygame.draw.rect(self.screen, (200,200,200), right_bar)
        filled_width = int((self.energy_right / self.max_energy) * bar_width)
        pygame.draw.rect(self.screen, (0, 128, 0), pygame.Rect(self.screen.get_width() - bar_width - padding, padding, filled_width, bar_height))
        right_text = self.turn_font.render(f"Chiến kỹ: {self.energy_right}/{self.max_energy}", True, (0,0,0))
        self.screen.blit(right_text, (self.screen.get_width() - bar_width - padding, padding + bar_height + 5))

    def draw(self):
        if self.battle_bg:
            self.battle_bg = pygame.transform.scale(self.battle_bg, (1280, 720))
            self.screen.blit(self.battle_bg, (0, 0))
        else:
            self.screen.fill((255, 255, 255))
        
        self.screen.blit(self.message, (20, 20))
        for char in self.team_left:
            self.screen.blit(char.image, char.pos)
            char.draw_status(self.screen)
        for char in self.team_right:
            self.screen.blit(char.image, char.pos)
            char.draw_status(self.screen)
        self.draw_turn_order()
        self.draw_energy_bars()
