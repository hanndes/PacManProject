import pygame
import random

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


class Ghost:
    """Hayalet sınıfı (Basit Utility-Based Agent)"""

    def __init__(self, x, y, color, name):
        self.grid_x = x
        self.grid_y = y
        self.x = x * CELL_SIZE
        self.y = y * CELL_SIZE
        self.color = color
        self.name = name
        self.speed = 1.5
        self.direction = [0, 0]
        self.eaten = False
        self.respawn_timer = 0
        self.original_x = x
        self.original_y = y
        self.immune = False

    def calculate_utility(self, pos, pacman, powered_up, grid):
        """Hayalet için Fayda Fonksiyonu"""
        x, y = pos
        utility = 0

        # Tünel geçişi kontrolü (Modülo ile)
        check_x = x % GRID_WIDTH

        # Duvar kontrolü
        if grid[y][check_x] == 1:
            return float('-inf')

        # Mesafeyi hesaplarken tüneli de hesaba katabiliriz ama şimdilik basit mesafe
        # Pacman'in wrap-around konumunu da düşünmek gerekir ama basit tutuyoruz.
        dist_to_pacman = abs(check_x - pacman.grid_x) + abs(y - pacman.grid_y)

        if powered_up and not self.immune:
            # Kaç
            utility += dist_to_pacman * 10
        else:
            # Takip et
            utility -= dist_to_pacman * 5

        utility += random.randint(-1, 1)

        return utility

    def get_best_move(self, grid, pacman, powered_up, other_ghosts):
        """En iyi hareketi seçer ve yönü ayarlar"""
        possible_moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        best_utility = float('-inf')
        best_direction = self.direction

        for dx, dy in possible_moves:
            # Gelecek konumu hesapla (Henüz wrap yapma, utility içinde bakacağız)
            move_x, move_y = self.grid_x + dx, self.grid_y + dy

            # Sadece Y sınırlarını kontrol et, X sınırları tünel için serbest (wrap olacak)
            if 0 <= move_y < GRID_HEIGHT:
                utility = self.calculate_utility((move_x, move_y), pacman, powered_up, grid)

                if utility > best_utility:
                    best_utility = utility
                    best_direction = [dx, dy]

        self.direction = best_direction
        return best_direction

    def update(self, grid, pacman, powered_up, other_ghosts):
        """Hayalet konumunu ve AI'ını günceller"""

        if not powered_up:
            self.immune = False

        if self.eaten:
            self.respawn_timer += 1
            if self.respawn_timer > 180:
                self.eaten = False
                self.respawn_timer = 0
                self.grid_x = self.original_x
                self.grid_y = self.original_y
                self.x = self.grid_x * CELL_SIZE
                self.y = self.grid_y * CELL_SIZE
                self.immune = True
            return

        if pygame.time.get_ticks() % 15 == 0:
            self.get_best_move(grid, pacman, powered_up, other_ghosts)

        # Hareketi uygula
        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed

        # --- TELEPORT MANTIĞI ---
        if new_x < -CELL_SIZE:
            new_x = GRID_WIDTH * CELL_SIZE
        elif new_x > GRID_WIDTH * CELL_SIZE:
            new_x = -CELL_SIZE

        # Grid konumu ve duvar kontrolü
        center_x = new_x + CELL_SIZE / 2
        center_y = new_y + CELL_SIZE / 2

        check_grid_x = int(center_x // CELL_SIZE) % GRID_WIDTH
        check_grid_y = int(center_y // CELL_SIZE)

        if (0 <= check_grid_y < GRID_HEIGHT and
                grid[check_grid_y][check_grid_x] != 1):
            self.x = new_x
            self.y = new_y
            self.grid_x = check_grid_x
            self.grid_y = check_grid_y

    def draw(self, screen, powered_up):
        """Hayaleti ekrana çizer"""
        center_x = int(self.x + CELL_SIZE // 2)
        center_y = int(self.y + CELL_SIZE // 2)
        radius = CELL_SIZE // 2 - 2

        if self.eaten:
            color = WHITE
        else:
            if powered_up and not self.immune:
                color = BLUE
            else:
                color = self.color

        pygame.draw.circle(screen, color, (center_x, center_y - 3), radius)

        points = [(center_x - radius, center_y)]
        for i in range(5):
            x = center_x - radius + (2 * radius * i // 4)
            y = center_y + radius if i % 2 == 0 else center_y + radius - 5
            points.append((x, y))
        points.append((center_x + radius, center_y))
        pygame.draw.polygon(screen, color, points)

        eye_offset = 5
        pupil_offset_x = self.direction[0] * 1
        pupil_offset_y = self.direction[1] * 1

        pygame.draw.circle(screen, WHITE, (center_x - eye_offset, center_y - 5), 4)
        pygame.draw.circle(screen, WHITE, (center_x + eye_offset, center_y - 5), 4)
        pygame.draw.circle(screen, BLACK, (center_x - eye_offset + pupil_offset_x, center_y - 5 + pupil_offset_y), 2)
        pygame.draw.circle(screen, BLACK, (center_x + eye_offset + pupil_offset_x, center_y - 5 + pupil_offset_y), 2)