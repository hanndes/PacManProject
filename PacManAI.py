import time
from collections import deque
from PacMan import PacMan

CELL_SIZE = 30
GRID_WIDTH = 20
GRID_HEIGHT = 22


class PacManAI(PacMan):
    """
    Gelişmiş Utility-Based Agent (Paranoyak Mod).
    Özellikler:
    - Paranoyak Kaçış (Üstel Korku)
    - Panik Modu (Yemekleri Unutma)
    - Enerji Topuna Sığınma
    - Sıkılma Cezası (Takılmayı Önleme)
    """

    def __init__(self, x, y):
        super().__init__(x, y)
        self.last_move_time = time.time()
        self.move_delay = 0.10  # Tepki süresi (Daha hızlı düşünür)

        # --- PARANOYAK AYARLAR (HAYATTA KALMA ODAKLI) ---

        self.FOOD_WEIGHT = 40.0  # Yemek yeme isteği
        self.POWER_WEIGHT = 500.0  # Enerji topu = Can Simidi (Çok yüksek)
        self.GHOST_HUNT_WEIGHT = 600.0  # Güçlüyken avlama isteği

        # Ölüm korkusu çok yüksek. Hayalete yaklaşmak "intihar" sayılır.
        self.GHOST_AVOID_WEIGHT = -10000.0

        self.EXPLORATION_BONUS = 10.0  # Kararlılık (Momentum)
        self.REVERSE_PENALTY = 20.0  # U-Dönüşü yapmama
        self.BOREDOM_PENALTY = 100.0  # Aynı yerde bekleme cezası

        # Hafıza: Son 20 kareyi hatırlar (Takılmayı önlemek için)
        self.location_history = deque(maxlen=20)

    def calculate_utility(self, pos, grid, ghosts, powered_up):
        """
        Her kare için bir 'Çekicilik Puanı' hesaplar.
        """
        x, y = pos
        utility = 0

        # --- 1. DUVAR KONTROLÜ (Kesin Kural) ---
        if grid[y][x] == 1:
            return float('-inf')

        # --- MESAFE VE TEHLİKE ANALİZİ ---

        # En yakın hayaleti bul
        min_ghost_dist = float('inf')
        for ghost in ghosts:
            if ghost.eaten: continue  # Yenmiş hayalet tehdit değildir
            dist = abs(x - ghost.grid_x) + abs(y - ghost.grid_y)
            if dist < min_ghost_dist:
                min_ghost_dist = dist

        # --- PANİK MODU ---
        # Eğer hayalet çok yakındaysa (5 birim), yemekleri tamamen UNUT.
        # Tek amaç: Hayatta kalmak.
        is_panic = (min_ghost_dist < 5 and not powered_up)

        current_food_weight = 0 if is_panic else self.FOOD_WEIGHT
        # Panik anında enerji topuna gitmek 2 kat daha önemlidir
        current_power_weight = self.POWER_WEIGHT * 2 if is_panic else self.POWER_WEIGHT
        current_ghost_weight = self.GHOST_AVOID_WEIGHT

        if powered_up:
            # Güçlüyken korku yok, avcılık var
            current_ghost_weight = self.GHOST_HUNT_WEIGHT
            current_food_weight = self.FOOD_WEIGHT / 2

            # --- PUANLAMA MOTORU ---

        # 1. Hayalet Etkisi (ÜSTEL KORKU)
        if min_ghost_dist < 15:
            if min_ghost_dist <= 1:
                if not powered_up: return float('-inf')  # Kesin ölüm riski

            # Formül: Mesafe'nin KARESİ (Squared Distance)
            # Hayalet 1 adım yaklaştığında korku 2 kat değil, 4-5 kat artar.
            # Bu, hayalet yaklaştıkça kaçma isteğini "çıldırtır".
            if not powered_up:
                utility += (200.0 / (min_ghost_dist ** 2 + 0.1)) * current_ghost_weight
            else:
                # Güçlüyken normal yaklaşım (Lineer)
                utility += (10.0 / (min_ghost_dist + 1)) * current_ghost_weight

        # 2. Enerji Topu (Can Simidi)
        min_power_dist = float('inf')
        power_pellets = [(px, py) for py in range(GRID_HEIGHT) for px in range(GRID_WIDTH) if grid[py][px] == 3]
        if power_pellets:
            for px, py in power_pellets:
                d = abs(x - px) + abs(y - py)
                if d < min_power_dist:
                    min_power_dist = d

        if min_power_dist != float('inf'):
            utility += (50.0 / (min_power_dist + 1)) * current_power_weight

        # 3. Yemek Etkisi (Sadece güvendeysen ye)
        if not is_panic:
            min_pellet_dist = float('inf')
            pellets = [(px, py) for py in range(GRID_HEIGHT) for px in range(GRID_WIDTH) if grid[py][px] == 2]
            if pellets:
                for px, py in pellets:
                    d = abs(x - px) + abs(y - py)
                    if d < min_pellet_dist:
                        min_pellet_dist = d

            if min_pellet_dist != float('inf'):
                utility += (20.0 / (min_pellet_dist + 1)) * current_food_weight

            # Anlık ödül (O karenin üstündeki yemek)
            if grid[y][x] == 2: utility += 20

        # 4. Sıkılma/Takılma Cezası
        # Eğer bu kareye son zamanlarda çok geldiyse puanını kır.
        visit_count = self.location_history.count((x, y))
        if visit_count > 0:
            utility -= visit_count * self.BOREDOM_PENALTY

        return utility

    def get_best_move(self, grid, ghosts, powered_up):
        """Mevcut konumdan gidilebilecek en iyi yönü seçer"""
        current_x, current_y = self.grid_x, self.grid_y
        possible_moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        best_move_delta = (self.dx, self.dy)
        best_utility = float('-inf')

        # Olası 4 yönü dene
        for dx, dy in possible_moves:
            next_x, next_y = current_x + dx, current_y + dy

            # Sadece geçerli ve duvar olmayan hareketleri değerlendir
            if 0 <= next_x < GRID_WIDTH and 0 <= next_y < GRID_HEIGHT and grid[next_y][next_x] != 1:

                utility = self.calculate_utility((next_x, next_y), grid, ghosts, powered_up)

                # Momentum Bonusu (Kararlılık - Titremeyi önler)
                if (dx, dy) == (self.dx, self.dy):
                    utility += self.EXPLORATION_BONUS

                # U-Dönüşü Cezası (Gereksiz geri dönmeyi engelle)
                if (dx, dy) == (-self.dx, -self.dy):
                    utility -= self.REVERSE_PENALTY

                if utility > best_utility:
                    best_utility = utility
                    best_move_delta = (dx, dy)

        # --- HİZALAMA (SNAP TO GRID) ---
        # Köşeleri rahat dönmesi için piksel ayarı
        if best_move_delta != (self.dx, self.dy):
            if best_move_delta[0] != 0:
                self.y = round(self.y / CELL_SIZE) * CELL_SIZE
                self.grid_y = round(self.y / CELL_SIZE)
            elif best_move_delta[1] != 0:
                self.x = round(self.x / CELL_SIZE) * CELL_SIZE
                self.grid_x = round(self.x / CELL_SIZE)

        self.set_direction(best_move_delta[0], best_move_delta[1])

    def update_ai(self, grid, ghosts, powered_up):
        """Ana oyun döngüsü tarafından çağrılır"""

        # Konum kaydı (Hafıza için)
        grid_pos = (self.grid_x, self.grid_y)
        self.location_history.append(grid_pos)

        # Takılma kontrolü (Hız 0 ise bekleme!)
        is_stuck = (self.dx == 0 and self.dy == 0)

        if is_stuck or (time.time() - self.last_move_time > self.move_delay):
            self.get_best_move(grid, ghosts, powered_up)
            self.last_move_time = time.time()

        self.update(grid)