# animations.py
import pygame
import math
import time

# Các hàm tiện ích chung:

def move_sprite(sprite, start_pos, end_pos, duration, surface, clock, redraw_callback):
    """
    Di chuyển sprite từ start_pos đến end_pos trong khoảng thời gian duration (giây).
    Thay vì dùng fill toàn màn hình, gọi redraw_callback để vẽ lại giao diện game.
    """
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        t = min(1, elapsed / duration)
        new_x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
        new_y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
        sprite.rect.topleft = (new_x, new_y)
        
        redraw_callback()
        surface.blit(sprite.image, sprite.rect)
        pygame.display.flip()
        clock.tick(60)
        if t >= 1:
            break

def glow_effect(surface, position, color, max_radius, duration, clock, redraw_callback):
    """
    Tạo hiệu ứng phát sáng bằng cách vẽ vòng tròn với bán kính tăng dần và alpha giảm dần.
    """
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        t = min(1, elapsed / duration)
        radius = int(max_radius * t)
        alpha = int(255 * (1 - t))
        glow_surf = pygame.Surface((max_radius * 2, max_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, color + (alpha,), (max_radius, max_radius), radius)
        
        redraw_callback()
        rect = glow_surf.get_rect(center=position)
        surface.blit(glow_surf, rect)
        pygame.display.flip()
        clock.tick(60)
        if t >= 1:
            break

def explosion_effect(surface, position, color, max_radius, duration, clock, redraw_callback):
    """
    Tạo hiệu ứng vụ nổ bằng cách vẽ vòng tròn mở rộng với alpha giảm dần.
    """
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        t = min(1, elapsed / duration)
        radius = int(max_radius * t)
        alpha = int(255 * (1 - t))
        explosion_surf = pygame.Surface((max_radius * 2, max_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(explosion_surf, color + (alpha,), (max_radius, max_radius), radius)
        
        redraw_callback()
        rect = explosion_surf.get_rect(center=position)
        surface.blit(explosion_surf, rect)
        pygame.display.flip()
        clock.tick(60)
        if t >= 1:
            break

# Lớp AnimationHandler, chứa các hàm hoạt ảnh riêng cho từng nhân vật

class AnimationHandler:
    def __init__(self, surface):
        self.surface = surface
        self.clock = pygame.time.Clock()

    # ------------------------ Kafka -------------------------
    def animate_kafka_attack(self, kafka_sprite, target_pos, redraw_callback):
        """Kafka: tấn công thường – lao vào target, hiệu ứng splash màu tím, sau đó quay về."""
        original_pos = kafka_sprite.rect.topleft
        move_sprite(kafka_sprite, original_pos, target_pos, duration=0.2,
                    surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)
        splash_color = (128, 0, 128)
        glow_effect(self.surface, target_pos, splash_color, max_radius=50, duration=0.2,
                    clock=self.clock, redraw_callback=redraw_callback)
        time.sleep(0.05)
        move_sprite(kafka_sprite, target_pos, original_pos, duration=0.2,
                    surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)

    def animate_kafka_skill(self, kafka_sprite, target_pos, redraw_callback):
        """Kafka: sử dụng skill – lao vào target, tạo hiệu ứng mạng nhện màu tím, sau đó quay lại."""
        original_pos = kafka_sprite.rect.topleft
        move_sprite(kafka_sprite, original_pos, target_pos, duration=0.25,
                    surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)
        splash_color = (128, 0, 128)
        for i in range(5):
            angle = (2 * math.pi * i) / 5
            end_x = target_pos[0] + int(50 * math.cos(angle))
            end_y = target_pos[1] + int(50 * math.sin(angle))
            redraw_callback()
            pygame.draw.line(self.surface, splash_color, target_pos, (end_x, end_y), 2)
            pygame.display.flip()
            self.clock.tick(60)
        time.sleep(0.25)
        move_sprite(kafka_sprite, target_pos, original_pos, duration=0.25,
                    surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)

    # ------------------------ Sunday -------------------------
    def animate_sunday_attack(self, sunday_sprite, target_pos, redraw_callback):
        """Sunday: tấn công – hiệu ứng rung nhẹ và vụ nổ màu vàng tại target."""
        original_pos = sunday_sprite.rect.topleft
        for offset in [(-5, 0), (5, 0), (-3, 0), (3, 0)]:
            sunday_sprite.rect.topleft = (original_pos[0] + offset[0], original_pos[1] + offset[1])
            redraw_callback()
            pygame.display.flip()
            self.clock.tick(30)
        sunday_sprite.rect.topleft = original_pos
        explosion_color = (255, 215, 0)  # vàng óng
        explosion_effect(self.surface, target_pos, explosion_color, max_radius=30, duration=0.2,
                         clock=self.clock, redraw_callback=redraw_callback)

    def animate_sunday_buff(self, ally_sprite, redraw_callback):
        """Sunday: sử dụng buff – tạo vùng hào quang vàng quanh đồng minh."""
        aura_color = (255, 215, 0)
        center = ally_sprite.rect.center
        glow_effect(self.surface, center, aura_color, max_radius=40, duration=0.3,
                    clock=self.clock, redraw_callback=redraw_callback)

    # ------------------------ Fuxuan -------------------------
    def animate_fuxuan_attack(self, fuxuan_sprite, target_pos, redraw_callback):
        """Fuxuan: tấn công – hiệu ứng rung nhẹ với màu tím, hiệu ứng vụ nổ màu tím."""
        original_pos = fuxuan_sprite.rect.topleft
        for offset in [(-3, 0), (3, 0), (-2, 0), (2, 0)]:
            fuxuan_sprite.rect.topleft = (original_pos[0] + offset[0], original_pos[1] + offset[1])
            redraw_callback()
            pygame.display.flip()
            self.clock.tick(30)
        fuxuan_sprite.rect.topleft = original_pos
        explosion_color = (128, 0, 128)
        explosion_effect(self.surface, target_pos, explosion_color, max_radius=35, duration=0.25,
                         clock=self.clock, redraw_callback=redraw_callback)

    def animate_fuxuan_skill(self, team_sprites, redraw_callback):
        """Fuxuan: sử dụng skill – tạo ra kết giới màu tím bao quanh toàn đội."""
        if not team_sprites:
            return
        centers = [sprite.rect.center for sprite in team_sprites]
        avg_x = sum(c[0] for c in centers) // len(centers)
        avg_y = sum(c[1] for c in centers) // len(centers)
        barrier_center = (avg_x, avg_y)
        barrier_color = (128, 0, 128)
        glow_effect(self.surface, barrier_center, barrier_color, max_radius=80, duration=0.5,
                    clock=self.clock, redraw_callback=redraw_callback)

    # ------------------------ Lynx -------------------------
    def animate_lynx_attack(self, lynx_sprite, target_pos, redraw_callback):
        """Lynx: tấn công – di chuyển tới target, hiệu ứng splash màu xanh lam, sau đó quay lại."""
        original_pos = lynx_sprite.rect.topleft
        move_sprite(lynx_sprite, original_pos, target_pos, duration=0.2,
                    surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)
        splash_color = (0, 0, 255)  # xanh lam
        glow_effect(self.surface, target_pos, splash_color, max_radius=50, duration=0.2,
                    clock=self.clock, redraw_callback=redraw_callback)
        time.sleep(0.05)
        move_sprite(lynx_sprite, target_pos, original_pos, duration=0.2,
                    surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)

    def animate_lynx_skill(self, ally_sprite, redraw_callback):
        """Lynx: sử dụng skill – hiệu ứng hồi máu (healing) màu xanh dương sáng."""
        center = ally_sprite.rect.center
        healing_color = (0, 191, 255)
        glow_effect(self.surface, center, healing_color, max_radius=40, duration=0.3,
                    clock=self.clock, redraw_callback=redraw_callback)

    # ------------------------ Ruan Mei -------------------------
    def animate_ruanmei_attack(self, ruanmei_sprite, target_pos, redraw_callback):
        """Ruan Mei: tấn công – tương tự hiệu ứng của Sunday nhưng với màu xanh be nhạt."""
        original_pos = ruanmei_sprite.rect.topleft
        for offset in [(-4, 0), (4, 0), (-2, 0), (2, 0)]:
            ruanmei_sprite.rect.topleft = (original_pos[0] + offset[0], original_pos[1] + offset[1])
            redraw_callback()
            pygame.display.flip()
            self.clock.tick(30)
        ruanmei_sprite.rect.topleft = original_pos
        explosion_color = (205, 197, 191)  # xanh be nhạt
        explosion_effect(self.surface, target_pos, explosion_color, max_radius=30, duration=0.2,
                         clock=self.clock, redraw_callback=redraw_callback)

    def animate_ruanmei_skill(self, team_sprites, redraw_callback):
        """Ruan Mei: sử dụng skill – tạo kết giới màu xanh be nhạt bao quanh đội."""
        if not team_sprites:
            return
        centers = [sprite.rect.center for sprite in team_sprites]
        avg_x = sum(c[0] for c in centers) // len(centers)
        avg_y = sum(c[1] for c in centers) // len(centers)
        barrier_center = (avg_x, avg_y)
        barrier_color = (205, 197, 191)
        glow_effect(self.surface, barrier_center, barrier_color, max_radius=80, duration=0.5,
                    clock=self.clock, redraw_callback=redraw_callback)

    # ------------------------ Yunli -------------------------
    def animate_yunli_attack(self, yunli_sprite, target_pos, redraw_callback):
        """Yunli: tấn công – di chuyển, tạo splash màu xám, sau đó quay lại."""
        original_pos = yunli_sprite.rect.topleft
        move_sprite(yunli_sprite, original_pos, target_pos, duration=0.2,
                    surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)
        splash_color = (128, 128, 128)  # xám
        glow_effect(self.surface, target_pos, splash_color, max_radius=50, duration=0.2,
                    clock=self.clock, redraw_callback=redraw_callback)
        time.sleep(0.05)
        move_sprite(yunli_sprite, target_pos, original_pos, duration=0.2,
                    surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)

    def animate_yunli_skill(self, yunli_sprite, main_target_pos, side_target1_pos, side_target2_pos, redraw_callback):
        """Yunli: sử dụng skill – lao tới target chính, tạo splash lớn màu xám, và splash phụ cho 2 kẻ bên cạnh."""
        original_pos = yunli_sprite.rect.topleft
        move_sprite(yunli_sprite, original_pos, main_target_pos, duration=0.25,
                    surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)
        splash_color = (128, 128, 128)
        glow_effect(self.surface, main_target_pos, splash_color, max_radius=60, duration=0.25,
                    clock=self.clock, redraw_callback=redraw_callback)
        glow_effect(self.surface, side_target1_pos, splash_color, max_radius=50, duration=0.25,
                    clock=self.clock, redraw_callback=redraw_callback)
        glow_effect(self.surface, side_target2_pos, splash_color, max_radius=50, duration=0.25,
                    clock=self.clock, redraw_callback=redraw_callback)
        time.sleep(0.05)
        move_sprite(yunli_sprite, main_target_pos, original_pos, duration=0.25,
                    surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)

    # ------------------------ March7th -------------------------
    def animate_march7th_attack(self, march_sprite, target_pos, redraw_callback):
        """March7th: tấn công – tương tự hiệu ứng của Sunday nhưng với yếu tố 'băng' (màu xanh băng)."""
        original_pos = march_sprite.rect.topleft
        for offset in [(-3, 0), (3, 0)]:
            march_sprite.rect.topleft = (original_pos[0] + offset[0], original_pos[1] + offset[1])
            redraw_callback()
            pygame.display.flip()
            self.clock.tick(30)
        march_sprite.rect.topleft = original_pos
        explosion_color = (173, 216, 230)  # màu xanh băng nhẹ
        explosion_effect(self.surface, target_pos, explosion_color, max_radius=30, duration=0.2,
                         clock=self.clock, redraw_callback=redraw_callback)

    def animate_march7th_skill(self, ally_sprite, redraw_callback):
        """March7th: sử dụng skill – tạo hiệu ứng bong bóng tại vị trí đồng minh."""
        center = ally_sprite.rect.center
        bubble_color = (173, 216, 230)
        glow_effect(self.surface, center, bubble_color, max_radius=40, duration=0.3,
                    clock=self.clock, redraw_callback=redraw_callback)

    # ------------------------ Castorice -------------------------
    def animate_castorice_attack(self, castorice_sprite, target_pos, redraw_callback):
        """Castorice: tấn công – di chuyển đến target, tạo hiệu ứng splash màu chàm, rồi quay lại vị trí ban đầu."""
        original_pos = castorice_sprite.rect.topleft
        # Di chuyển tới target
        move_sprite(castorice_sprite, original_pos, target_pos, duration=0.2,
                    surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)
        # Tạo hiệu ứng splash với màu chàm
        splash_color = (50, 50, 50)  # màu chàm
        glow_effect(self.surface, target_pos, splash_color, max_radius=50, duration=0.2,
                    clock=self.clock, redraw_callback=redraw_callback)
        # Giảm sleep nếu cần (0.05 là hợp lý để không gián đoạn)
        time.sleep(0.05)
        # Di chuyển quay trở về vị trí ban đầu
        move_sprite(castorice_sprite, target_pos, original_pos, duration=0.2,
                    surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)


    def animate_castorice_skill(self, castorice_sprite, main_target_pos, side_target1_pos, side_target2_pos, redraw_callback):
        """Castorice: sử dụng skill – di chuyển đến target chính, tạo splash đồng thời hiệu ứng cho 2 target phụ, rồi quay lại."""
        original_pos = castorice_sprite.rect.topleft
        move_sprite(castorice_sprite, original_pos, main_target_pos, duration=0.25,
                    surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)
        splash_color = (50, 50, 50)  # màu chàm
        # Hiệu ứng splash cho target chính
        glow_effect(self.surface, main_target_pos, splash_color, max_radius=60, duration=0.25,
                    clock=self.clock, redraw_callback=redraw_callback)
        # Hiệu ứng cho các target phụ
        glow_effect(self.surface, side_target1_pos, splash_color, max_radius=50, duration=0.25,
                    clock=self.clock, redraw_callback=redraw_callback)
        glow_effect(self.surface, side_target2_pos, splash_color, max_radius=50, duration=0.25,
                    clock=self.clock, redraw_callback=redraw_callback)
        time.sleep(0.05)
        move_sprite(castorice_sprite, main_target_pos, original_pos, duration=0.25,
                    surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)

    def animate_castorice_summon_attack(self, summon_sprite, target_pos_list, attack_count, redraw_callback):
        """
        Castorice_Summon:
        - Đối với mỗi lượt attack, summon bắn tia năng lượng (vẽ các đường line đỏ) tới các target.
        - Nếu attack_count == 3, summon lao vào trung tâm đội địch, tạo hiệu ứng vụ nổ.
        """
        # Giai đoạn 1: Tấn công bằng tia năng lượng
        for i in range(attack_count):
            for target_pos in target_pos_list:
                redraw_callback()
                pygame.draw.line(self.surface, (255, 0, 0), summon_sprite.rect.center, target_pos, 2)
            pygame.display.flip()
            time.sleep(0.1)  # Có thể điều chỉnh thời gian này để hiệu ứng mượt hơn
            redraw_callback()

        # Giai đoạn 2: Nếu đây là lượt thứ 3, lao vào trung tâm đội địch và tạo vụ nổ
        if attack_count == 3 and target_pos_list:
            # Giả sử trung tâm của đội địch là vị trí của target đầu tiên
            center_target = target_pos_list[0]
            move_sprite(summon_sprite, summon_sprite.rect.topleft, center_target, duration=0.3,
                        surface=self.surface, clock=self.clock, redraw_callback=redraw_callback)
            explosion_effect(self.surface, center_target, (255, 0, 0), max_radius=70, duration=0.3,
                            clock=self.clock, redraw_callback=redraw_callback)
        # Sau khi hoàn thành, gọi xử lý bên ngoài để loại bỏ summon khỏi game (nếu cần)

    # ------------------------ March7th -------------------------
    def animate_march7th_attack(self, march_sprite, target_pos, redraw_callback):
        """
        March7th tấn công thường: đứng yên tại chỗ và bắn ra 1 mũi tên băng.
        Hoạt ảnh: vẽ mũi tên di chuyển từ vị trí March7th tới target.
        """
        original_pos = march_sprite.rect.center
        # Tạo mũi tên băng (một hình chữ nhật nhỏ)
        arrow = pygame.Surface((30, 5), pygame.SRCALPHA)
        arrow.fill((173, 216, 230))  # màu xanh băng nhẹ
        arrow_rect = arrow.get_rect(center=original_pos)
        
        start_time = time.time()
        duration = 0.3
        clock = pygame.time.Clock()
        
        # Vòng lặp animation
        while True:
            elapsed = time.time() - start_time
            t = min(1, elapsed / duration)
            # Tính vị trí mũi tên trên đường thẳng từ March7th đến target
            new_x = original_pos[0] + (target_pos[0] - original_pos[0]) * t
            new_y = original_pos[1] + (target_pos[1] - original_pos[1]) * t
            arrow_rect.center = (new_x, new_y)
            
            # Gọi lại hàm redraw để vẽ lại background và các sprite hiện tại
            redraw_callback()
            
            # Vẽ March7th đứng yên (giả sử redraw_callback đã vẽ march_sprite)
            # Vẽ mũi tên băng
            screen = pygame.display.get_surface()
            screen.blit(arrow, arrow_rect)
            pygame.display.update()
            
            clock.tick(60)  # Giới hạn FPS
            
            if t >= 1:
                break

    def animate_march7th_counter(self, march_sprite, target_pos, redraw_callback):
        """
        Hiệu ứng phản đòn của March7th:
        March7th thực hiện đòn phản đòn ngay lập tức với mục tiêu (target_pos).
        Hoạt ảnh: vẽ một mũi tên counter (màu cam nổi bật) di chuyển từ vị trí March7th đến target.
        """
        original_pos = march_sprite.rect.center
        # Tạo mũi tên counter với màu cam (có thể thay đổi màu nếu muốn)
        arrow = pygame.Surface((30, 5), pygame.SRCALPHA)
        arrow.fill((255, 165, 0))  # màu cam đặc trưng cho đòn counter
        arrow_rect = arrow.get_rect(center=original_pos)
        
        start_time = time.time()
        duration = 0.25  # Hoạt ảnh nhanh hơn chút so với đòn tấn công thường
        clock = pygame.time.Clock()
        
        while True:
            elapsed = time.time() - start_time
            t = min(1, elapsed / duration)
            # Tính vị trí mũi tên trên đường thẳng từ vị trí ban đầu đến target
            new_x = original_pos[0] + (target_pos[0] - original_pos[0]) * t
            new_y = original_pos[1] + (target_pos[1] - original_pos[1]) * t
            arrow_rect.center = (new_x, new_y)
            
            # Gọi callback vẽ lại màn hình (background, sprite hiện tại, …)
            redraw_callback()
            
            # Vẽ mũi tên counter
            screen = pygame.display.get_surface()
            screen.blit(arrow, arrow_rect)
            pygame.display.update()
            
            clock.tick(60)  # Giới hạn FPS
            
            if t >= 1:
                break
