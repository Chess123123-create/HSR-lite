import pygame
import sys
import pygame_gui
from battle import Battle
from character_select import CharacterSelect

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
current_music = None

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("HSR: bet")
clock = pygame.time.Clock()
FPS = 120

manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# Các trạng thái của game
STATE_START = "start"
STATE_CHARACTER_SELECT = "select"
STATE_BATTLE = "battle"
game_state = STATE_START

# Tạo giao diện Start Screen với nút “Bắt đầu”
start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT//2 - 25, 150, 50)),
                                              text='Bắt đầu',
                                              manager=manager)

# Khởi tạo màn hình chọn nhân vật (khi bắt đầu game)
character_select = CharacterSelect(screen)
battle = None

def play_music(music_path, volume=0.5):
    global current_music
    if current_music != music_path:
        pygame.mixer.music.stop() 
        pygame.mixer.music.load(music_path)  
        pygame.mixer.music.play(-1) 
        pygame.mixer.music.set_volume(volume)  
        current_music = music_path  

# Tạo nút "Chơi lại" cho màn hình battle (ẩn ban đầu)
play_again_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT - 100, 150, 50)),
                                                   text='Chơi lại',
                                                   manager=manager)
play_again_button.hide()

while True:
    time_delta = clock.tick(FPS) / 500.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        manager.process_events(event)
        
        if game_state == STATE_START:
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == start_button:
                game_state = STATE_CHARACTER_SELECT
                start_button.hide()
        elif game_state == STATE_CHARACTER_SELECT:
            character_select.handle_event(event)
            if character_select.ready_to_battle:
                teams = character_select.get_teams()
                if teams[0] and teams[1]:
                    battle = Battle(screen, teams[0], teams[1], manager)
                    game_state = STATE_BATTLE
                    play_again_button.hide()
                else:
                    character_select.ready_to_battle = False
        elif game_state == STATE_BATTLE:
            battle.handle_event(event)
            if battle.battle_over:
                play_again_button.show()
                if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == play_again_button:
                    character_select.reset()
                    game_state = STATE_CHARACTER_SELECT
                    play_again_button.hide()
    
    if game_state == STATE_START:
        bg_image = pygame.image.load("Resource/login-bg.png")
        bg_image = pygame.transform.scale(bg_image, (1280, 720))
        screen.blit(bg_image, (0, 0))
        play_music("Resource/sound/Star Rail (Login Menu BGM) - Honkai_ Star Rail 1.0 OST.ogg")
        
        font = pygame.font.SysFont("Arial", 48)
        title = font.render("Honkai Impact: Star Rail 3", True, (255,255,255))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 100))

        manager.update(time_delta)
        manager.draw_ui(screen)

    elif game_state == STATE_CHARACTER_SELECT:
        play_music("Resource/sound/The Player on The Other Side · Penacony Battle Theme - Honkai_ Star Rail 2.0 OST.ogg")
        character_select.update()
        character_select.draw()

    elif game_state == STATE_BATTLE:
        battle.update()
        battle.draw()
    
    manager.update(time_delta)
    manager.draw_ui(screen)
    
    pygame.display.flip()
