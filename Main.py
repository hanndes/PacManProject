import pygame
from PacManGame import PacManGame

# Pygame başlatma ve Mikseri başlatma
pygame.init()
pygame.mixer.init()

# Renkler
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 128, 0)
BLUE = (34, 172, 182)

GRAY_WITH_ALPHA = (50, 50, 50, 50)

# --- DÜZELTME: Boyutlar PacManGame.py ile eşitlendi ---
CELL_SIZE = 30
GRID_WIDTH = 21  # ESKİSİ 20 İDİ, 21 YAPILDI
GRID_HEIGHT = 22  # ESKİSİ 20/22 KARIŞIKTI, 22 YAPILDI
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + 200
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE


def main_menu():
    """Ana menü ekranı"""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pac-Man - Ana Menü")
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)

    # --- 1. RESMİ YÜKLEME KISMI ---
    background_image = None
    try:
        background_image = pygame.image.load("pacman.png")
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        pass  # Resim yoksa sessizce siyah ekrana geç

    running = True
    selected = 0
    options = ["İnsan Oyuncu", "Bilgisayar (AI)", "Çıkış"]

    while running:
        # --- 2. ARKA PLAN ÇİZİMİ ---
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(BLACK)

        # --- 3. SEÇENEKLERİ ÇİZME ---
        for i, option in enumerate(options):
            color = BLUE if i == selected else WHITE

            text = small_font.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 60))

            # Seçili ise arkasına kutu çiz
            if i == selected:
                padding_x = 60
                padding_y = 20
                box_width = text_rect.width + padding_x
                box_height = text_rect.height + padding_y

                selection_box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
                pygame.draw.rect(selection_box, GRAY_WITH_ALPHA, selection_box.get_rect(), border_radius=20)

                box_rect = selection_box.get_rect(center=text_rect.center)
                screen.blit(selection_box, box_rect)

            screen.blit(text, text_rect)

        info = small_font.render("Ok tuşları: Seç   |   Enter: Başlat/Çıkış", True, BLACK)
        screen.blit(info, info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        return "human"
                    elif selected == 1:
                        return "ai"
                    else:
                        return None
    return None


def main():
    while True:
        choice = main_menu()

        if choice in ["human", "ai"]:
            game = PacManGame(mode=choice)
            result = game.run()
            if result is None:
                break
        else:
            break

    pygame.quit()


if __name__ == "__main__":
    main()