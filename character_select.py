import pygame
from characters import get_character_pool

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

class CharacterSelect:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 20)
        self.pool = get_character_pool()  # dict tên: Character

        self.GRID_COLS = 4
        self.GRID_ROWS = 2
        self.GRID_CELL_SIZE = 100
        self.grid_start_x = (SCREEN_WIDTH - self.GRID_COLS * self.GRID_CELL_SIZE) // 2
        self.grid_start_y = 50

        self.SIDE_CELL_SIZE = 80
        self.side_start_y = 50
        self.left_grid_x = 20
        self.right_grid_x = SCREEN_WIDTH - 20 - self.SIDE_CELL_SIZE

        self.team_left = [None] * 4
        self.team_right = [None] * 4

        self.dragging = None
        self.drag_offset = (0, 0)

        self.btn_battle = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 80, 150, 50)
        self.ready_to_battle = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            idx = 0
            for name, char in list(self.pool.items()):
                col = idx % self.GRID_COLS
                row = idx // self.GRID_COLS
                x = self.grid_start_x + col * self.GRID_CELL_SIZE
                y = self.grid_start_y + row * self.GRID_CELL_SIZE
                cell_rect = pygame.Rect(x, y, self.GRID_CELL_SIZE - 10, self.GRID_CELL_SIZE - 10)
                if cell_rect.collidepoint(pos):
                    self.dragging = char
                    self.drag_offset = (pos[0] - x, pos[1] - y)
                    break
                idx += 1
            if self.btn_battle.collidepoint(pos):
                if any(self.team_left) and any(self.team_right):
                    self.ready_to_battle = True

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.dragging.pos = (event.pos[0] - self.drag_offset[0], event.pos[1] - self.drag_offset[1])
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                pos = pygame.mouse.get_pos()
                placed = False
                for i in range(4):
                    cell_rect = pygame.Rect(self.left_grid_x, self.side_start_y + i*(self.SIDE_CELL_SIZE+10),
                                              self.SIDE_CELL_SIZE, self.SIDE_CELL_SIZE)
                    if cell_rect.collidepoint(pos) and self.team_left[i] is None:
                        self.team_left[i] = self.dragging
                        placed = True
                        break
                if not placed:
                    for i in range(4):
                        cell_rect = pygame.Rect(self.right_grid_x, self.side_start_y + i*(self.SIDE_CELL_SIZE+10),
                                                  self.SIDE_CELL_SIZE, self.SIDE_CELL_SIZE)
                        if cell_rect.collidepoint(pos) and self.team_right[i] is None:
                            self.team_right[i] = self.dragging
                            placed = True
                            break
                if placed:
                    name_to_remove = None
                    for name, char in self.pool.items():
                        if char == self.dragging:
                            name_to_remove = name
                            break
                    if name_to_remove:
                        del self.pool[name_to_remove]
                self.dragging.pos = self.dragging.rect.topleft
                self.dragging = None

    def update(self):
        for char in self.pool.values():
            char.update()

    def draw(self):
        bg_image = pygame.image.load("Resource/bg-castorice.png")
        bg_image = pygame.transform.scale(bg_image, (1280, 720))
        self.screen.blit(bg_image, (0, 0))
        idx = 0
        for name, char in self.pool.items():
            col = idx % self.GRID_COLS
            row = idx // self.GRID_COLS
            x = self.grid_start_x + col * self.GRID_CELL_SIZE
            y = self.grid_start_y + row * self.GRID_CELL_SIZE
            cell_rect = pygame.Rect(x, y, self.GRID_CELL_SIZE - 10, self.GRID_CELL_SIZE - 10)
            pygame.draw.rect(self.screen, (200,200,200), cell_rect, 2)
            name_text = self.font.render(name, True, (0,0,0))
            self.screen.blit(name_text, (x+5, y+5))
            if char != self.dragging:
                char.pos = (x, y + 20)
            self.screen.blit(char.image, char.pos)
            idx += 1

        for i in range(4):
            left_rect = pygame.Rect(self.left_grid_x, self.side_start_y + i*(self.SIDE_CELL_SIZE+10),
                                      self.SIDE_CELL_SIZE, self.SIDE_CELL_SIZE)
            pygame.draw.rect(self.screen, (0,0,0), left_rect, 2)
            if self.team_left[i]:
                self.screen.blit(self.team_left[i].image, left_rect.topleft)
            right_rect = pygame.Rect(self.right_grid_x, self.side_start_y + i*(self.SIDE_CELL_SIZE+10),
                                       self.SIDE_CELL_SIZE, self.SIDE_CELL_SIZE)
            pygame.draw.rect(self.screen, (0,0,0), right_rect, 2)
            if self.team_right[i]:
                self.screen.blit(self.team_right[i].image, right_rect.topleft)
        
        pygame.draw.rect(self.screen, (100,200,100), self.btn_battle)
        battle_text = self.font.render("Chiến đấu", True, (0,0,0))
        text_rect = battle_text.get_rect(center=self.btn_battle.center)
        self.screen.blit(battle_text, text_rect)

    def get_teams(self):
        team_left = [char for char in self.team_left if char is not None]
        team_right = [char for char in self.team_right if char is not None]
        return team_left, team_right

    def reset(self):
        self.team_left = [None] * 4
        self.team_right = [None] * 4
        self.ready_to_battle = False
        self.pool = get_character_pool()
        idx = 0
        for name, char in self.pool.items():
            col = idx % self.GRID_COLS
            row = idx // self.GRID_COLS
            x = self.grid_start_x + col * self.GRID_CELL_SIZE
            y = self.grid_start_y + row * self.GRID_CELL_SIZE + 20
            char.pos = (x, y)
            char.rect.topleft = char.pos
            idx += 1
