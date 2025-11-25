import pygame
import math

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
GRID_HEIGHT = 22  # Main.py'deki yeni ayara göre güncellendi
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + 200
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 60


class PacMan:
    """Temel Pac-Man sınıfı (İnsan kontrolü)"""

    def __init__(self, x, y):
        self.grid_x = x
        self.grid_y = y
        self.x = x * CELL_SIZE
        self.y = y * CELL_SIZE
        self.dx = 0
        self.dy = 0
        self.speed = 2
        self.mouth_open = 0
        self.is_moving = False

    def set_direction(self, dx, dy):
        """Klavye girişine göre yönü ayarlar"""
        self.dx = dx
        self.dy = dy

    def update(self, grid):
        """Konumu günceller ve duvar çarpışmasını/ışınlanmayı kontrol eder"""
        new_x = self.x + self.dx * self.speed
        new_y = self.y + self.dy * self.speed

        # --- TELEPORT (IŞINLANMA) MANTIĞI ---
        # Ekranın solundan tamamen çıkarsa sağa at
        if new_x < -CELL_SIZE:
            new_x = GRID_WIDTH * CELL_SIZE
        # Ekranın sağından tamamen çıkarsa sola at
        elif new_x > GRID_WIDTH * CELL_SIZE:
            new_x = -CELL_SIZE

        # Grid koordinatlarını hesapla (Modülo ile sınır dışını içeri sar)
        # Bu sayede -1. indeks aslında listenin son elemanı gibi davranmaz,
        # mantıksal kontrol yaparız.
        center_x = new_x + CELL_SIZE / 2
        center_y = new_y + CELL_SIZE / 2

        check_grid_x = int(center_x // CELL_SIZE) % GRID_WIDTH
        check_grid_y = int(center_y // CELL_SIZE)

        prev_x, prev_y = self.x, self.y

        # Duvar kontrolü
        # Eğer tüneldeysek (ekran dışındaysak) duvar kontrolünü atla veya
        # karşı tarafın duvarına bak.
        can_move = True

        if 0 <= check_grid_y < GRID_HEIGHT:
            if grid[check_grid_y][check_grid_x] == 1:
                can_move = False

        if can_move:
            self.x = new_x
            self.y = new_y
            # Grid koordinatını güncelle (Ekran dışı değerler olabilir, sorun yok)
            # Ama oyunda kullanırken modülo alarak kullanacağız
            self.grid_x = int((self.x + CELL_SIZE / 2) // CELL_SIZE) % GRID_WIDTH
            self.grid_y = int((self.y + CELL_SIZE / 2) // CELL_SIZE)

        # Eğer bir duvara çarpıyorsa hareketi durdur
        else:
            self.dx = 0
            self.dy = 0

        # Hareket durumu kontrolü
        self.is_moving = (abs(self.x - prev_x) > 0.1 or abs(self.y - prev_y) > 0.1)

        # Ağız animasyonu
        self.mouth_open = (self.mouth_open + 5) % 360

    def draw(self, screen):
        """Pac-Man'i ekrana çizer"""
        center_x = int(self.x + CELL_SIZE // 2)
        center_y = int(self.y + CELL_SIZE // 2)
        radius = CELL_SIZE // 2 - 2

        pygame.draw.circle(screen, YELLOW, (center_x, center_y), radius)

        # Ağız çizimi
        if self.dx != 0 or self.dy != 0:
            angle_deg = math.degrees(math.atan2(-self.dy, self.dx))
            if angle_deg < 0:
                angle_deg += 360

            mouth_size = 30 * (abs(math.cos(math.radians(self.mouth_open))))

            if mouth_size < 28:
                points = [(center_x, center_y)]
                points.append((center_x + radius * math.cos(math.radians(angle_deg + mouth_size)),
                               center_y - radius * math.sin(math.radians(angle_deg + mouth_size))))
                points.append((center_x + radius * math.cos(math.radians(angle_deg - mouth_size)),
                               center_y - radius * math.sin(math.radians(angle_deg - mouth_size))))

                if len(points) == 3:
                    pygame.draw.polygon(screen, BLACK, points)