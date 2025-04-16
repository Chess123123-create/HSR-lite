import random, pygame

class Character(pygame.sprite.Sprite):
    def __init__(self, name, role, HP, DEF, ATK, SPD, BP=200, BE=1.0, CR=0.05, CD=0.5):
        super().__init__()
        self.name = name
        self.role = role
        self.HP = HP
        self.max_HP = HP
        self.DEF = DEF
        self.ATK = ATK
        self.SPD = SPD
        self.BP = BP
        self.BE = BE
        self.CR = CR
        self.CD = CD
        self.shield = 0  # shield từ các nguồn khác nếu có
        self.march_shield = 0  # thanh HP ảo buff của March7th (không cộng dồn)
        if self.name == "March7th":
            self.buff_cooldown = 0
        self.skill_type = None
        self.skill_target = None
        self.summoned = None  # Dành cho Castorice, lưu đối tượng summon khi đã được triệu hồi
        self.sunday_action_count = 0

        # Nếu là summon, đánh dấu và khởi tạo biến đếm lượt tấn công cho summon
        if self.name.endswith("_Summon"):
            self.is_summon = True
            self.summon_turn_count = 0
        else:
            self.is_summon = False

        # Để theo dõi sát thương DOT khi bị tác động (ví dụ từ Kafka)
        self.dot = 0

        try:
            self.image = pygame.image.load(f"Resource/{name}.png").convert_alpha()
        except Exception as e:
            print(f"Không tải được hình cho {name}: {e}")
            self.image = pygame.Surface((80,80))
            self.image.fill((150,150,150))
        self.image = pygame.transform.scale(self.image, (80,80))
        self.rect = self.image.get_rect()
        self.pos = self.rect.topleft

    def update(self):
        self.rect.topleft = self.pos

    def draw_status(self, screen):
        font = pygame.font.SysFont("Arial", 14)
        hp_text = font.render(f"HP: {self.HP}/{self.max_HP}", True, (0,0,0))
        screen.blit(hp_text, (self.pos[0], self.pos[1] - 45))
        bp_text = font.render(f"BP: {self.BP}", True, (0,0,0))
        screen.blit(bp_text, (self.pos[0], self.pos[1] - 30))
        # Hiển thị shield từ các nguồn khác
        if self.shield > 0:
            shield_text = font.render(f"Shield: {int(self.shield)}", True, (0,0,255))
            screen.blit(shield_text, (self.pos[0], self.pos[1] - 15))
        # Hiển thị buff giáp của March7th (virtual HP)
        if self.march_shield > 0:
            march_shield_text = font.render(f"Giáp: {int(self.march_shield)}", True, (0,128,128))
            screen.blit(march_shield_text, (self.pos[0], self.pos[1] - 60))
        # Hiển thị DOT nếu có
        if self.dot > 0:
            dot_text = font.render(f"DOT: {self.dot}", True, (255,0,0))
            screen.blit(dot_text, (self.pos[0], self.pos[1] - 75))

    def energy_cost_available(self):
        # Với Castorice, skill không tiêu tốn năng lượng
        return True

    def get_normal_attack_type(self):
        mapping = {
            "Yunli": "yunli_attack",
            "Kafka": "kafka_attack",
            "March7th": "march_attack",  # March7th có hoạt ảnh riêng
            "Ruan Mei": "ruanmei_attack",
            "FuXuan": "fuxuan_attack",
            "Lynx": "lynx_attack",
            "Castorice": "castorice_attack",
            "Sunday": "sunday_attack",
            # Mapping cho summon của Castorice (phần này đang lỗi)
            "Castorice_Summon": "castorice_summon_attack"
        }
        return mapping.get(self.name, "default_attack")

    def use_skill_special(self, allies, enemies):
        """
        Phương thức dùng skill đặc biệt của nhân vật.
        Đối với March7th: tiêu hao năng lượng (đã kiểm tra bên Battle)
          - Tìm đồng minh (trong phe) có HP hiện tại thấp nhất và chưa có giáp buff (march_shield == 0).
          - Áp dụng buff giáp với lượng = 15% max_HP của đồng minh đó.
        Các nhân vật khác xử lý như cũ.
        """
        if self.name == "March7th":
            # Chọn đồng minh có HP hiện tại thấp nhất (theo giá trị tuyệt đối) và chưa có buff giáp của March7th
            candidate = None
            for ally in allies:
                # Nếu đồng minh đã có buff giáp thì bỏ qua (không cộng dồn)
                if ally.march_shield > 0:
                    continue
                if candidate is None or ally.HP < candidate.HP:
                    candidate = ally
            if candidate is not None:
                self.skill_type = "march_shield"
                candidate.march_shield = int(candidate.max_HP * 0.15)
                print(f"{self.name}: Cấp giáp cho {candidate.name} với {candidate.march_shield} HP ảo.")
                return True
            return False

        # Các xử lý skill cho các nhân vật khác (ví dụ từ đoạn code cũ)
        if self.name == "Yunli":
            condition = (self.HP / self.max_HP < 0.3) or any(e.HP > self.HP for e in enemies)
            if condition:
                self.skill_type = "yunli_chain"
                self.skill_target = random.choice(enemies)
                print(f"{self.name}: Sử dụng skill chain attack.")
                return True
            return False

        if self.name == "Kafka":
            condition = (self.HP / self.max_HP < 0.3) or any(e.HP > self.HP for e in enemies)
            if condition:
                self.skill_type = "kafka_chain"
                self.skill_target = random.choice(enemies)
                if not hasattr(self.skill_target, 'dot'):
                    self.skill_target.dot = 0
                self.skill_target.dot += 1
                print(f"{self.name}: Sử dụng skill chain attack và tăng DOT.")
                return True
            else:
                if not hasattr(self.skill_target, 'dot'):
                    self.skill_target.dot = 0
                self.skill_target.dot += 1
                if self.skill_target.dot >= 2:
                    self.skill_type = "kafka_dot"
                    self.skill_target.dot = 0
                    print(f"{self.name}: Kích hoạt hiệu ứng DOT.")
                    return True
            return False

        if self.name == "FuXuan":
            self.skill_type = "fuxuan_guard"
            for ally in allies:
                if ally != self:
                    ally.fuxuan_buff = 3
            print(f"{self.name}: Sử dụng skill nhận thay cho đồng đội.")
            return True

        if self.name == "Lynx":
            if allies:
                self.skill_type = "lynx_heal"
                target = min(allies, key=lambda c: c.HP / c.max_HP)
                if target.HP / target.max_HP < 0.95:
                    self.skill_target = target
                    target.HP += int(self.ATK * 0.2)
                    target.HP = min(target.HP, target.max_HP)
                    print(f"{self.name}: Sử dụng skill heal cho {target.name}.")
                    return True
            return False

        if self.name == "Ruan Mei":
            self.skill_type = "ruanmei_buff"
            for ally in allies:
                ally.ruanmei_buff = 2
            print(f"{self.name}: Sử dụng skill buff cho toàn đội.")
            return True

        if self.name == "Sunday":
            if allies:
                self.skill_type = "sunday_buff"
                target = max(allies, key=lambda c: c.ATK)
                self.skill_target = target
                target.spd_buff = 100
                target.damage_buff = 0.2
                self.sunday_action_count += 1
                if self.sunday_action_count % 2 == 0:
                    self.heal_energy = True
                print(f"{self.name}: Sử dụng skill buff cho {target.name}.")
                return True
            return False

        if self.name == "Castorice":
            # Giai đoạn 1: Triệu hồi summon – chỉ xảy ra khi Castorice sử dụng skill lần đầu tiên.
            if not self.summoned:
                self.skill_type = "castorice_summon"
                total_sacrifice = 0
                for ally in allies:
                    if ally is not self:  # chỉ hy sinh HP của đồng đội (có thể bỏ qua chính mình)
                        sacrifice = int(ally.HP * 0.1)
                        ally.HP = max(ally.HP - sacrifice, 0)
                        total_sacrifice += sacrifice
                self.total_sacrifice = total_sacrifice
                # Thay vì tạo summon ngay, đánh dấu cờ yêu cầu triệu hồi
                self.summon_pending = True
                print(f"{self.name}: Yêu cầu triệu hồi summon, đã hy sinh tổng {total_sacrifice} HP của đồng đội.")
                return True
            else:
                self.skill_type = "castorice_attack_all"
                damage = int(self.total_sacrifice * 0.15 * 3)
                for enemy in enemies:
                    enemy.HP = max(enemy.HP - damage, 0)
                heal_amount = int(self.summoned.max_HP * 0.3)
                self.summoned.HP = min(self.summoned.HP + heal_amount, self.summoned.max_HP)
                print(f"{self.name}: Tấn công toàn địch gây {damage} sát thương và hồi {self.summoned.name} {heal_amount} HP.")
                return True


        return False

    def summon_skill(self, enemies):
        """
        Phương thức tấn công của summon (Castorice_Summon).
        """
        if not self.is_summon:
            return False

        current_turn = self.summon_turn_count

        if current_turn < 2:
            sacrifice = int(self.HP * 0.8)
            self.HP = max(self.HP - sacrifice, 0)
            damage1 = int(sacrifice * 0.10)
            for enemy in enemies:
                enemy.HP = max(enemy.HP - damage1, 0)
            damage2 = int(self.max_HP * 0.05)
            for enemy in enemies:
                enemy.HP = max(enemy.HP - damage2, 0)
            heal_amount = int(self.max_HP * 0.20)
            self.HP = min(self.HP + heal_amount, self.max_HP)
            print(f"{self.name}: (Turn {current_turn+1}) Tiêu hao {sacrifice} HP, gây sát thương {damage1} + {damage2}, hồi {heal_amount} HP.")
        else:
            sacrifice = self.HP
            damage = int(sacrifice * 0.15)
            for enemy in enemies:
                enemy.HP = max(enemy.HP - damage, 0)
            self.HP = 0
            print(f"{self.name}: (Turn {current_turn+1}) Tiêu hao toàn bộ HP ({sacrifice}), gây sát thương {damage} và rời sân.")
        self.summon_turn_count += 1
        return True

def get_character_pool():
    pool = {
        "March7th": {"role": "dps", "HP": random.randint(3400,3600), "DEF": random.randint(1400,1600), "ATK": random.randint(3600,3800), "SPD": random.randint(148,155)},
        "Lynx": {"role": "dps", "HP": random.randint(3400,3600), "DEF": random.randint(1400,1600), "ATK": random.randint(3600,3800), "SPD": random.randint(148,155)},
        "Ruan Mei": {"role": "healer", "HP": random.randint(4400,4600), "DEF": random.randint(1700,1900), "ATK": random.randint(3300,3500), "SPD": random.randint(138,145)},
        "Sunday": {"role": "supporter", "HP": random.randint(3400,3600), "DEF": random.randint(1400,1600), "ATK": random.randint(3300,3500), "SPD": random.randint(138,145)},
        "Yunli": {"role": "tanker", "HP": random.randint(4400,4600), "DEF": random.randint(2100,2300), "ATK": random.randint(3300,3500), "SPD": random.randint(128,135)},
        "FuXuan": {"role": "healer", "HP": 8670, "DEF": 1523, "ATK": random.randint(3300,3500), "SPD": random.randint(138,145)},
        "Castorice": {"role": "supporter", "HP": random.randint(3400,3600), "DEF": random.randint(1400,1600), "ATK": random.randint(3300,3500), "SPD": random.randint(138,145)},
        "Kafka": {"role": "dps", "HP": random.randint(3400,3600), "DEF": random.randint(1400,1600), "ATK": random.randint(3600,3800), "SPD": random.randint(148,155)}
    }
    character_pool = {}
    for name, stats in pool.items():
        character_pool[name] = Character(name, stats["role"], stats["HP"], stats["DEF"], stats["ATK"], stats["SPD"])
    return character_pool
