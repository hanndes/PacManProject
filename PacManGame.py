import pygame
import time
import numpy as np
from Ghost import Ghost
from PacMan import PacMan
from PacManAI import PacManAI

# Renkler
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (153, 51, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)

# Oyun ayarları
CELL_SIZE = 30
GRID_WIDTH = 21
GRID_HEIGHT = 22
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + 200
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 60
POWER_UP_DURATION = 15


class PacManGame:
    """Oyun Yöneticisi Sınıfı"""

    def __init__(self, mode="human"):
        self.mode = mode
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"Pac-Man - Utility-based Agent ({mode.upper()})")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.create_sounds()
        self.reset_game()
        self.load_high_score()

    def create_sounds(self):
        """Basit ses efektlerini oluşturur"""
        self.eat_sound = None
        self.power_sound = None
        self.ghost_eat_sound = None
        self.game_over_sound = None

        sample_rate = 44100

        def generate_sine_wave(frequency, duration, amplitude=0.01):
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            return (amplitude * np.sin(2.0 * np.pi * frequency * t) * (2 ** 15 - 1)).astype(np.int16)

        try:
            pygame.mixer.set_num_channels(8)
            wave_eat = generate_sine_wave(440, 0.05)
            self.eat_sound = pygame.mixer.Sound(wave_eat.tobytes())

            wave_power = generate_sine_wave(220, 0.15)
            self.power_sound = pygame.mixer.Sound(wave_power.tobytes())

            wave_ghost_eat = generate_sine_wave(660, 0.3)
            self.ghost_eat_sound = pygame.mixer.Sound(wave_ghost_eat.tobytes())

            wave_game_over = generate_sine_wave(100, 0.5)
            self.game_over_sound = pygame.mixer.Sound(wave_game_over.tobytes())

        except Exception as e:
            print(f"Ses hatası: {e}")

    def play_sound(self, sound):
        if sound:
            sound.play()

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                self.high_score_data = eval(f.read())
        except:
            self.high_score_data = {"human": (0, float('inf')), "ai": (0, float('inf'))}

    def save_high_score(self):
        elapsed_time = self.final_time if self.game_over else time.time() - self.start_time
        current_score = self.score
        old_score, old_time = self.high_score_data[self.mode]

        is_new_high_score = False
        if current_score > old_score:
            is_new_high_score = True
        elif current_score == old_score and elapsed_time < old_time:
            is_new_high_score = True

        if is_new_high_score:
            self.high_score_data[self.mode] = (current_score, elapsed_time)
            try:
                with open("highscore.txt", "w") as f:
                    f.write(str(self.high_score_data))
            except:
                pass

    def reset_game(self):
        self.grid = self.create_grid()

        if self.mode == "human":
            self.pacman = PacMan(1, 1)
        else:
            self.pacman = PacManAI(1, 1)

        # Hayaletleri evin içine yerleştir
        self.ghosts = [
            Ghost(9, 9, RED, "Blinky"),
            Ghost(10, 9, PINK, "Pinky"),
            Ghost(9, 10, CYAN, "Inky"),
            Ghost(10, 10, ORANGE, "Clyde")
        ]

        self.score = 0
        self.start_time = time.time()
        self.game_over = False
        self.win = False
        self.powered_up = False
        self.power_timer = 0
        self.final_time = 0.0

    def create_grid(self):
        """
        Klasik Pac-Man labirentini oluşturur.
        1: Duvar
        .: Yemek (2)
        P: Enerji Topu (3)
        0: Boş/Hayalet Evi
        """

        LAYOUT = [
            "111111111111111111111",
            "1.........1.........1",
            "1P111.111.1.111.111P1",
            "1.111.111.1.111.111.1",
            "1...................1",
            "1.111.1.11111.1.111.1",
            "1.....1...1...1.....1",
            "11111.111010111.11111",
            "00001.100000001.10000",
            "11111.1.10001.1.11111",
            "........10001........",
            "11111.1.11111.1.11111",
            "00001.1.......1.10000",
            "11111.1.11111.1.11111",
            "1.........1.........1",
            "1.111.111.1.111.111.1",
            "1P..1.....0.....1..P1",
            "111.1.1.11111.1.1.111",
            "1.....1...1...1.....1",
            "1.1111111.1.1111111.1",
            "1...................1",
            "111111111111111111111",
        ]

        # Grid boyutlarını layout'a göre ayarla
        actual_height = len(LAYOUT)
        actual_width = len(LAYOUT[0]) if LAYOUT else GRID_WIDTH

        grid = [[0 for _ in range(actual_width)] for _ in range(actual_height)]

        for y, row in enumerate(LAYOUT):
            for x, char in enumerate(row):
                if x < actual_width and y < actual_height:
                    if char == '1':
                        grid[y][x] = 1  # Duvar
                    elif char == '.':
                        grid[y][x] = 2  # Yemek
                    elif char == 'P':
                        grid[y][x] = 3  # Enerji Topu
                    elif char == '0':
                        grid[y][x] = 0  # Boş Alan

        # Pacman başlangıç noktasını temizle
        if 1 < actual_height and 1 < actual_width:
            grid[1][1] = 0

        # Hayalet evi merkezi temizle
        for gy in range(9, min(11, actual_height)):
            for gx in range(9, min(11, actual_width)):
                if grid[gy][gx] != 1:
                    grid[gy][gx] = 0

        return grid

    def count_pellets(self):
        count = 0
        for row in self.grid:
            count += row.count(2) + row.count(3)
        return count

    def update(self):
        if self.game_over:
            return

        # Pac-Man Hareketi
        if self.mode == "human":
            self.pacman.update(self.grid)
        elif self.mode == "ai":
            self.pacman.update_ai(self.grid, self.ghosts, self.powered_up)

        # Yiyecek Toplama
        x, y = self.pacman.grid_x, self.pacman.grid_y
        if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
            if self.grid[y][x] == 2:
                self.grid[y][x] = 0
                self.score += 10
                self.play_sound(self.eat_sound)
            elif self.grid[y][x] == 3:
                self.grid[y][x] = 0
                self.score += 50
                self.powered_up = True
                self.power_timer = time.time()
                self.play_sound(self.power_sound)

        # Power-up süresi kontrolü
        if self.powered_up and time.time() - self.power_timer > POWER_UP_DURATION:
            self.powered_up = False

        # Hayalet Hareketi
        for ghost in self.ghosts:
            ghost.update(self.grid, self.pacman, self.powered_up, self.ghosts)

            if (self.pacman.grid_x == ghost.grid_x and self.pacman.grid_y == ghost.grid_y):
                if self.powered_up and not ghost.eaten:
                    ghost.eaten = True
                    self.score += 200
                    self.play_sound(self.ghost_eat_sound)
                elif not ghost.eaten:
                    self.game_over = True
                    self.play_sound(self.game_over_sound)
                    self.final_time = time.time() - self.start_time

        if self.count_pellets() == 0:
            if not self.game_over:
                self.play_sound(self.ghost_eat_sound)
                self.final_time = time.time() - self.start_time
            self.game_over = True
            self.win = True

    def draw(self):
        self.screen.fill(BLACK)

        # Labirent çizimi
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.grid[y][x] == 1:
                    # Duvarları klasik Pac-Man stilinde çiz
                    pygame.draw.rect(self.screen, BLUE, rect, 2)
                    pygame.draw.rect(self.screen, (0, 0, 80), rect.inflate(-4, -4))
                elif self.grid[y][x] == 2:
                    pygame.draw.circle(self.screen, ORANGE, (rect.centerx, rect.centery), 3)
                elif self.grid[y][x] == 3:
                    # Yanıp sönen power pellet efekti
                    if time.time() % 0.5 < 0.25:
                        pygame.draw.circle(self.screen, WHITE, (rect.centerx, rect.centery), 8)
                    else:
                        pygame.draw.circle(self.screen, ORANGE, (rect.centerx, rect.centery), 8)

        self.pacman.draw(self.screen)
        for ghost in self.ghosts:
            ghost.draw(self.screen, self.powered_up)

        # Arayüz
        info_x = GRID_WIDTH * CELL_SIZE + 10
        if self.game_over:
            elapsed = int(self.final_time)
        else:
            elapsed = int(time.time() - self.start_time)

        high_score, high_time = self.high_score_data.get(self.mode, (0, float('inf')))
        hs_time_str = f"{int(high_time)}s" if high_time != float('inf') else "--s"

        self.screen.blit(self.font.render(f"Mod: {self.mode.upper()}", True, CYAN), (info_x, 20))
        self.screen.blit(self.font.render(f"Skor: {self.score}", True, WHITE), (info_x, 60))
        self.screen.blit(self.font.render(f"Süre: {elapsed}s", True, WHITE), (info_x, 100))
        self.screen.blit(self.small_font.render(f"Kalan: {self.count_pellets()}", True, WHITE), (info_x, 140))

        self.screen.blit(self.small_font.render("--- EN İYİ SKOR ---", True, YELLOW), (info_x, 200))
        self.screen.blit(self.small_font.render(f"Skor: {high_score}", True, YELLOW), (info_x, 230))
        self.screen.blit(self.small_font.render(f"Süre: {hs_time_str}", True, YELLOW), (info_x, 260))

        if self.powered_up:
            remaining_power = int(POWER_UP_DURATION - (time.time() - self.power_timer))
            self.screen.blit(self.font.render(f"GÜÇ: {remaining_power}s", True, GREEN), (info_x, 320))

        if self.game_over:
            self.save_high_score()
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            msg = "KAZANDINIZ!" if self.win else "GAME OVER!"
            color = GREEN if self.win else RED

            text = self.font.render(msg, True, color)
            text_rect = text.get_rect(center=(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2))
            self.screen.blit(text, text_rect)

            restart_text = self.small_font.render("R: Tekrar Oyna  Q: Çıkış", True, WHITE)
            self.screen.blit(restart_text, restart_text.get_rect(
                center=(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2 + 50)))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if self.mode == "human" and not self.game_over:
                        if event.key == pygame.K_UP:
                            self.pacman.set_direction(0, -1)
                        elif event.key == pygame.K_DOWN:
                            self.pacman.set_direction(0, 1)
                        elif event.key == pygame.K_LEFT:
                            self.pacman.set_direction(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.pacman.set_direction(1, 0)

                    if event.key == pygame.K_r and self.game_over:
                        return "restart"
                    elif event.key == pygame.K_q and self.game_over:
                        return None

            self.update()
            self.draw()
            self.clock.tick(FPS)
        return None