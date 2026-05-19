import pygame
import random
import math
import sys
import json
import os

# Инициализация Pygame
pygame.init()

# Константы экрана
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 100)
PURPLE = (200, 50, 255)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (100, 200, 255)
DARK_RED = (139, 0, 0)
GOLD = (255, 215, 0)
DARK_GREEN = (0, 100, 0)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)
DARK_ORANGE = (255, 140, 0)
SILVER = (192, 192, 192)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defence - Магазин скинов")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)
font_big = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 24)

# Путь для мобов
waypoints = [(100, 300), (200, 300), (400, 300), (500, 200), (700, 200), (800, 400), (900, 400)]
start_pos = waypoints[0]
end_pos = waypoints[-1]

# ===== ЗОНА ЗАПРЕТА УСТАНОВКИ ТУРЕЛЕЙ =====
forbidden_zones = [
    {"x": 300, "y": 250, "radius": 50},
    {"x": 600, "y": 150, "radius": 40},
    {"x": 750, "y": 350, "radius": 45},
]

# ===== МУЗЫКА =====
MUSIC_PATH = "background_music.mp3"

def init_music():
    try:
        if os.path.exists(MUSIC_PATH):
            pygame.mixer.music.load(MUSIC_PATH)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            return True
    except:
        pass
    return False

# ===== ЗАГРУЗКА ИЗОБРАЖЕНИЙ =====
def load_image(path, default_size, default_color, fallback_shape="rect"):
    try:
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, default_size)
        else:
            raise FileNotFoundError
    except:
        surf = pygame.Surface(default_size, pygame.SRCALPHA)
        if fallback_shape == "circle":
            pygame.draw.circle(surf, default_color, (default_size[0]//2, default_size[1]//2), default_size[0]//2)
            pygame.draw.circle(surf, WHITE, (default_size[0]//2, default_size[1]//2), default_size[0]//2, 2)
        else:
            pygame.draw.rect(surf, default_color, (0, 0, default_size[0], default_size[1]))
            pygame.draw.rect(surf, WHITE, (0, 0, default_size[0], default_size[1]), 2)
        return surf

MOB_IMAGE_PATH = "mob.png"
BOSS_IMAGE_PATH = "boss.png"
TOWER_IMAGE_PATH = "tower.png"
BULLET_IMAGE_PATH = "bullet.png"
FINISH_TOWER_IMAGE_PATH = "finish_tower.png"
RANGED_MOB_IMAGE_PATH = "ranged_mob.png"
BARRIER_IMAGE_PATH = "barrier.png"

# СКИНЫ для турелей
TOWER_SKIN1_PATH = "tower_skin1.png"   # Скин 1 (300 монет)
TOWER_SKIN2_PATH = "tower_skin2.png"   # Скин 2 (499 монет)

mob_image = load_image(MOB_IMAGE_PATH, (40, 40), RED, "circle")
boss_image = load_image(BOSS_IMAGE_PATH, (70, 70), PURPLE, "circle")
tower_image = load_image(TOWER_IMAGE_PATH, (36, 36), BLUE, "rect")
tower_skin1_image = load_image(TOWER_SKIN1_PATH, (36, 36), GOLD, "rect")
tower_skin2_image = load_image(TOWER_SKIN2_PATH, (36, 36), SILVER, "rect")
bullet_image = load_image(BULLET_IMAGE_PATH, (8, 8), YELLOW, "circle")
finish_tower_image = load_image(FINISH_TOWER_IMAGE_PATH, (60, 60), GREEN, "rect")
ranged_mob_image = load_image(RANGED_MOB_IMAGE_PATH, (35, 35), CYAN, "circle")
barrier_image = load_image(BARRIER_IMAGE_PATH, (40, 40), DARK_ORANGE, "rect")

# ===== КЛАСС ПУЛИ МОБОВ =====
class MobBullet:
    def __init__(self, x, y, target_tower, damage, speed=5):
        self.x = x
        self.y = y
        self.target = target_tower
        self.damage = damage
        self.speed = speed
        self.active = True
        self.image = bullet_image
    
    def update(self):
        if not self.target or not self.target.active:
            self.active = False
            return
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.hypot(dx, dy)
        
        if distance < self.speed:
            self.target.health -= self.damage
            self.active = False
        else:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
    
    def draw(self, surface):
        img_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.image, img_rect)

# ===== КЛАСС ПУЛИ ТУРЕЛЕЙ =====
class TowerBullet:
    def __init__(self, x, y, target_mob, damage, speed=10):
        self.x = x
        self.y = y
        self.target = target_mob
        self.damage = damage
        self.speed = speed
        self.active = True
        self.image = bullet_image
    
    def update(self):
        if not self.target or not self.target.alive:
            self.active = False
            return
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.hypot(dx, dy)
        
        if distance < self.speed:
            self.target.health -= self.damage
            self.active = False
        else:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
    
    def draw(self, surface):
        img_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.image, img_rect)

# ===== КЛАСС БАШНИ-ФИНИША =====
class FinishTower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_health = 500
        self.health = 500
        self.image = finish_tower_image
        self.size = 30
        self.active = True
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.active = False
        return self.health <= 0
    
    def draw(self, surface):
        img_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.image, img_rect)
        
        bar_width = 80
        bar_height = 12
        health_percent = self.health / self.max_health
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 40
        
        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, bar_width * health_percent, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        hp_text = font_small.render(f"HP: {int(self.health)}/{int(self.max_health)}", True, WHITE)
        surface.blit(hp_text, (self.x - 35, bar_y - 20))

# ===== КЛАСС БАШНИ-ТУРЕЛИ =====
class Tower:
    def __init__(self, x, y, attack_power=15, range_radius=120, cooldown_max=30, skin=0):
        self.x = x
        self.y = y
        self.attack_power = attack_power
        self.range_radius = range_radius
        self.cooldown = 0
        self.cooldown_max = cooldown_max
        self.skin = skin
        # Выбор изображения в зависимости от скина
        if skin == 1:
            self.image = tower_skin1_image
        elif skin == 2:
            self.image = tower_skin2_image
        else:
            self.image = tower_image
        self.bullets = []
        self.max_health = 400
        self.health = 400
        self.active = True
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.active = False
        return self.health <= 0
    
    def update(self, mobs):
        if not self.active:
            return None
        
        if self.cooldown > 0:
            self.cooldown -= 1
            return None
        
        closest_mob = None
        min_distance = float('inf')
        
        for mob in mobs:
            distance = math.hypot(self.x - mob.x, self.y - mob.y)
            if distance <= self.range_radius and distance < min_distance:
                min_distance = distance
                closest_mob = mob
        
        if closest_mob:
            self.cooldown = self.cooldown_max
            bullet = TowerBullet(self.x, self.y, closest_mob, self.attack_power)
            self.bullets.append(bullet)
            return closest_mob
        
        return None
    
    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
    
    def draw(self, surface):
        if not self.active:
            return
        
        bar_width = 36
        bar_height = 6
        health_percent = self.health / self.max_health
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 25
        
        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, bar_width * health_percent, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        
        img_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.image, img_rect)
        
        for bullet in self.bullets:
            bullet.draw(surface)
        
        mouse_pos = pygame.mouse.get_pos()
        distance_to_mouse = math.hypot(self.x - mouse_pos[0], self.y - mouse_pos[1])
        if distance_to_mouse < 30:
            alpha_surf = pygame.Surface((self.range_radius * 2, self.range_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surf, (100, 100, 255, 50), (self.range_radius, self.range_radius), self.range_radius)
            surface.blit(alpha_surf, (self.x - self.range_radius, self.y - self.range_radius))

# ===== КЛАСС БАШНИ-БАРЬЕРА =====
class BarrierTower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_health = 250
        self.health = 250
        self.image = barrier_image
        self.active = True
        self.stun_duration = 30
        self.affected_mobs = {}
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.active = False
        return self.health <= 0
    
    def update(self, mobs):
        if not self.active:
            return
        
        for mob in list(self.affected_mobs.keys()):
            if mob not in mobs or mob.alive == False:
                del self.affected_mobs[mob]
            else:
                self.affected_mobs[mob] -= 1
                if self.affected_mobs[mob] <= 0:
                    del self.affected_mobs[mob]
        
        for mob in mobs:
            if mob not in self.affected_mobs:
                distance = math.hypot(self.x - mob.x, self.y - mob.y)
                if distance < 30:
                    if mob.is_boss:
                        self.take_damage(999)
                        return
                    else:
                        self.affected_mobs[mob] = self.stun_duration
    
    def draw(self, surface):
        if not self.active:
            return
        
        bar_width = 40
        bar_height = 6
        health_percent = self.health / self.max_health
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 25
        
        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, bar_width * health_percent, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        
        img_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.image, img_rect)

# ===== КЛАСС МОБА =====
class Mob:
    def __init__(self, wave, is_boss=False, boss_streak=0, is_ranged=False):
        self.wave = wave
        self.is_boss = is_boss
        self.is_ranged_attacker = is_ranged
        self.alive = True
        self.stunned = False
        self.stun_timer = 0
        
        wave_bonus = 1 + (wave // 3) * 0.5
        
        if is_boss:
            boss_bonus = 1 + (wave // 5) * 0.8
            extra_bonus = 2.0 if (boss_streak > 0 and boss_streak % 3 == 0) else 1.0
            
            base_health = 200 + wave * 20
            self.health = int(base_health * wave_bonus * boss_bonus * extra_bonus)
            self.max_health = self.health
            self.speed = 1.0
            self.size = 35
            self.image = boss_image
            self.crystals_reward = 15
            self.coins_reward = 30 + wave * 4
            self.damage_to_finish = 500
            self.attack_cooldown = 0
            self.attack_range = 150
            self.attack_damage = 50
        elif is_ranged:
            base_health = int((25 + wave * 4) * wave_bonus)
            self.health = int(base_health / 1.5)
            self.max_health = self.health
            self.speed = 1.5 + wave * 0.1
            self.size = 18
            self.image = ranged_mob_image
            self.crystals_reward = 7
            self.coins_reward = 8 + wave
            self.damage_to_finish = 5
            self.attack_cooldown = 0
            self.attack_range = 180
            self.attack_damage = 8
        else:
            self.health = int((30 + wave * 5) * wave_bonus)
            self.max_health = self.health
            self.speed = 2 + wave * 0.1
            self.size = 20
            self.image = mob_image
            self.crystals_reward = 5
            self.coins_reward = 5 + wave
            self.damage_to_finish = 10
            self.attack_cooldown = 0
            self.attack_range = 0
            self.attack_damage = 0
        
        self.x, self.y = start_pos
        self.waypoint_index = 1
        self.target_tower = None
        self.original_speed = self.speed
    
    def apply_stun(self, duration):
        if not self.is_boss:
            self.stunned = True
            self.stun_timer = duration
            self.speed = 0
    
    def move(self):
        if self.stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stunned = False
                self.speed = self.original_speed
            return
        
        target_x, target_y = waypoints[self.waypoint_index]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)
        if distance < self.speed:
            self.x, self.y = target_x, target_y
            if self.waypoint_index < len(waypoints) - 1:
                self.waypoint_index += 1
        else:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
    
    def attack_towers(self, towers, finish_tower):
        if self.attack_range == 0:
            return None
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            return None
        
        nearest_tower = None
        min_distance = float('inf')
        
        for tower in towers:
            if tower.active:
                distance = math.hypot(self.x - tower.x, self.y - tower.y)
                if distance <= self.attack_range and distance < min_distance:
                    min_distance = distance
                    nearest_tower = tower
        
        if nearest_tower:
            self.attack_cooldown = 40
            nearest_tower.take_damage(self.attack_damage)
            return nearest_tower
        
        return None
    
    def reached_end(self):
        return math.hypot(self.x - end_pos[0], self.y - end_pos[1]) < 20
    
    def draw(self, surface):
        if self.is_boss and self.health > self.max_health * 0.8:
            glow = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 100, 0, 100), (self.size, self.size), self.size)
            surface.blit(glow, (self.x - self.size, self.y - self.size))
        
        if self.is_ranged_attacker:
            pygame.draw.circle(surface, CYAN, (int(self.x), int(self.y)), self.size + 5, 2)
        
        if self.stunned:
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.size + 3, 3)
        
        img_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.image, img_rect)
        
        bar_width = self.size * 2
        bar_height = 6
        health_percent = self.health / self.max_health
        pygame.draw.rect(surface, RED, (self.x - self.size, self.y - self.size - 10, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (self.x - self.size, self.y - self.size - 10, bar_width * health_percent, bar_height))
        
        if self.is_boss:
            boss_text = font_small.render("BOSS", True, WHITE)
            surface.blit(boss_text, (self.x - 20, self.y - self.size - 25))
            if self.health > self.max_health * 0.8:
                elite_text = font_small.render("ELITE", True, GOLD)
                surface.blit(elite_text, (self.x - 20, self.y - self.size - 40))
        elif self.is_ranged_attacker:
            ranged_text = font_small.render("ARCHER", True, CYAN)
            surface.blit(ranged_text, (self.x - 25, self.y - self.size - 25))

# ===== СИСТЕМА АВТО-СОХРАНЕНИЯ =====
SAVE_FILE = "save.json"

def save_game(wave, crystals, coins, upgrade_levels, boss_rush_mode, finish_tower_health, coins_for_shop, skin_unlocked, current_skin):
    save_data = {
        "wave": wave,
        "crystals": crystals,
        "coins": coins,
        "upgrade_levels": upgrade_levels,
        "boss_rush_mode": boss_rush_mode,
        "finish_tower_health": finish_tower_health,
        "coins_for_shop": coins_for_shop,
        "skin_unlocked": skin_unlocked,
        "current_skin": current_skin
    }
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(save_data, f, indent=4)
        return True
    except:
        return False

def load_game():
    default_data = (1, 0, 0, {"damage": 15, "range": 120, "cooldown": 30}, False, 500, 0, [False, False], 0)
    if not os.path.exists(SAVE_FILE):
        return default_data
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        return (data.get("wave", 1),
                data.get("crystals", 0),
                data.get("coins", 0),
                data.get("upgrade_levels", {"damage": 15, "range": 120, "cooldown": 30}),
                data.get("boss_rush_mode", False),
                data.get("finish_tower_health", 500),
                data.get("coins_for_shop", 0),
                data.get("skin_unlocked", [False, False]),
                data.get("current_skin", 0))
    except:
        return default_data

# ===== МАГАЗИН (с вкладками) =====
def shop_menu(coins_for_shop, skin_unlocked, current_skin):
    barrier_price = 300  # Цена барьер-башни 300 монет
    skin1_price = 300
    skin2_price = 499
    
    tab = 0  # 0 - товары, 1 - скины
    barrier_bought = False
    
    while True:
        screen.fill(BLACK)
        
        title = font_big.render("МАГАЗИН", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        info = font.render(f"Монеты для магазина: {coins_for_shop}", True, LIGHT_BLUE)
        screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, 90))
        
        # Вкладки
        tab1_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 130, 150, 40)
        tab2_rect = pygame.Rect(SCREEN_WIDTH // 2, 130, 150, 40)
        
        pygame.draw.rect(screen, GREEN if tab == 0 else GRAY, tab1_rect)
        pygame.draw.rect(screen, GREEN if tab == 1 else GRAY, tab2_rect)
        
        tab1_text = font.render("ТОВАРЫ", True, BLACK)
        tab2_text = font.render("СКИНЫ", True, BLACK)
        screen.blit(tab1_text, (SCREEN_WIDTH // 2 - 100, 145))
        screen.blit(tab2_text, (SCREEN_WIDTH // 2 + 40, 145))
        
        if tab == 0:
            # Вкладка ТОВАРЫ
            # Башня-барьер
            barrier_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 190, 300, 200)
            pygame.draw.rect(screen, DARK_ORANGE, barrier_rect)
            pygame.draw.rect(screen, WHITE, barrier_rect, 3)
            
            barrier_title = font.render("Башня-Барьер", True, WHITE)
            screen.blit(barrier_title, (SCREEN_WIDTH // 2 - 70, 210))
            
            barrier_desc1 = font_small.render("Ставится НА ПУТЬ", True, YELLOW)
            barrier_desc2 = font_small.render("Останавливает врагов", True, WHITE)
            barrier_desc3 = font_small.render("HP: 250 | Босс ломает с 1 удара", True, RED)
            screen.blit(barrier_desc1, (SCREEN_WIDTH // 2 - 100, 240))
            screen.blit(barrier_desc2, (SCREEN_WIDTH // 2 - 85, 260))
            screen.blit(barrier_desc3, (SCREEN_WIDTH // 2 - 130, 280))
            
            price_text = font.render(f"Цена: {barrier_price} монет", True, GOLD)
            screen.blit(price_text, (SCREEN_WIDTH // 2 - 70, 310))
            
            buy_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, 340, 100, 35)
            color = GREEN if coins_for_shop >= barrier_price else RED
            pygame.draw.rect(screen, color, buy_rect)
            buy_text = font.render("КУПИТЬ", True, BLACK)
            screen.blit(buy_text, (SCREEN_WIDTH // 2 - 35, 348))
            
            if barrier_bought:
                owned_text = font.render("✓ Уже куплено", True, GREEN)
                screen.blit(owned_text, (SCREEN_WIDTH // 2 - 60, 390))
        
        else:
            # Вкладка СКИНЫ
            # Скин 1
            skin1_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, 190, 220, 200)
            pygame.draw.rect(screen, GOLD, skin1_rect)
            pygame.draw.rect(screen, WHITE, skin1_rect, 3)
            
            skin1_title = font.render("Скин 1 (Золотой)", True, BLACK)
            screen.blit(skin1_title, (SCREEN_WIDTH // 2 - 220, 210))
            
            # Превью скина
            preview_rect1 = pygame.Rect(SCREEN_WIDTH // 2 - 200, 230, 40, 40)
            pygame.draw.rect(screen, GOLD, preview_rect1)
            pygame.draw.rect(screen, WHITE, preview_rect1, 2)
            
            skin1_desc = font_small.render("Золотая турель", True, DARK_GREEN)
            screen.blit(skin1_desc, (SCREEN_WIDTH // 2 - 210, 280))
            
            if skin_unlocked[0]:
                status_text = font.render("КУПЛЕНО", True, GREEN)
                screen.blit(status_text, (SCREEN_WIDTH // 2 - 180, 320))
                if current_skin == 1:
                    equipped_text = font.render("▲ ЭКИПИРОВАН", True, YELLOW)
                    screen.blit(equipped_text, (SCREEN_WIDTH // 2 - 200, 350))
            else:
                price1_text = font.render(f"Цена: {skin1_price} монет", True, GOLD)
                screen.blit(price1_text, (SCREEN_WIDTH // 2 - 180, 320))
                buy1_rect = pygame.Rect(SCREEN_WIDTH // 2 - 170, 350, 80, 30)
                pygame.draw.rect(screen, GREEN if coins_for_shop >= skin1_price else RED, buy1_rect)
                buy1_text = font.render("КУПИТЬ", True, BLACK)
                screen.blit(buy1_text, (SCREEN_WIDTH // 2 - 155, 356))
            
            # Скин 2
            skin2_rect = pygame.Rect(SCREEN_WIDTH // 2 + 30, 190, 220, 200)
            pygame.draw.rect(screen, SILVER, skin2_rect)
            pygame.draw.rect(screen, WHITE, skin2_rect, 3)
            
            skin2_title = font.render("Скин 2 (Платиновый)", True, BLACK)
            screen.blit(skin2_title, (SCREEN_WIDTH // 2 + 50, 210))
            
            preview_rect2 = pygame.Rect(SCREEN_WIDTH // 2 + 80, 230, 40, 40)
            pygame.draw.rect(screen, SILVER, preview_rect2)
            pygame.draw.rect(screen, WHITE, preview_rect2, 2)
            
            skin2_desc = font_small.render("Платиновая турель", True, DARK_GREEN)
            screen.blit(skin2_desc, (SCREEN_WIDTH // 2 + 60, 280))
            
            if skin_unlocked[1]:
                status_text = font.render("КУПЛЕНО", True, GREEN)
                screen.blit(status_text, (SCREEN_WIDTH // 2 + 110, 320))
                if current_skin == 2:
                    equipped_text = font.render("▲ ЭКИПИРОВАН", True, YELLOW)
                    screen.blit(equipped_text, (SCREEN_WIDTH // 2 + 80, 350))
            else:
                price2_text = font.render(f"Цена: {skin2_price} монет", True, GOLD)
                screen.blit(price2_text, (SCREEN_WIDTH // 2 + 110, 320))
                buy2_rect = pygame.Rect(SCREEN_WIDTH // 2 + 120, 350, 80, 30)
                pygame.draw.rect(screen, GREEN if coins_for_shop >= skin2_price else RED, buy2_rect)
                buy2_text = font.render("КУПИТЬ", True, BLACK)
                screen.blit(buy2_text, (SCREEN_WIDTH // 2 + 135, 356))
            
            # Кнопка экипировки для купленных скинов
            if skin_unlocked[0] and current_skin != 1:
                equip1_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, 410, 220, 30)
                pygame.draw.rect(screen, BLUE, equip1_rect)
                equip1_text = font_small.render("ЭКИПИРОВАТЬ СКИН 1", True, WHITE)
                screen.blit(equip1_text, (SCREEN_WIDTH // 2 - 235, 417))
            elif not skin_unlocked[0]:
                lock1_text = font_small.render("Не куплен", True, RED)
                screen.blit(lock1_text, (SCREEN_WIDTH // 2 - 250, 410))
            
            if skin_unlocked[1] and current_skin != 2:
                equip2_rect = pygame.Rect(SCREEN_WIDTH // 2 + 30, 410, 220, 30)
                pygame.draw.rect(screen, BLUE, equip2_rect)
                equip2_text = font_small.render("ЭКИПИРОВАТЬ СКИН 2", True, WHITE)
                screen.blit(equip2_text, (SCREEN_WIDTH // 2 + 45, 417))
            elif not skin_unlocked[1]:
                lock2_text = font_small.render("Не куплен", True, RED)
                screen.blit(lock2_text, (SCREEN_WIDTH // 2 + 30, 410))
        
        # Кнопка выхода
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, 460, 100, 40)
        pygame.draw.rect(screen, GRAY, back_rect)
        back_text = font.render("НАЗАД", True, BLACK)
        screen.blit(back_text, (SCREEN_WIDTH // 2 - 35, 470))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Переключение вкладок
                if tab1_rect.collidepoint(mouse_pos):
                    tab = 0
                elif tab2_rect.collidepoint(mouse_pos):
                    tab = 1
                
                if tab == 0:
                    if 'buy_rect' in locals() and buy_rect.collidepoint(mouse_pos) and coins_for_shop >= barrier_price:
                        coins_for_shop -= barrier_price
                        barrier_bought = True
                else:
                    if not skin_unlocked[0] and 'buy1_rect' in locals() and buy1_rect.collidepoint(mouse_pos) and coins_for_shop >= skin1_price:
                        coins_for_shop -= skin1_price
                        skin_unlocked[0] = True
                    elif not skin_unlocked[1] and 'buy2_rect' in locals() and buy2_rect.collidepoint(mouse_pos) and coins_for_shop >= skin2_price:
                        coins_for_shop -= skin2_price
                        skin_unlocked[1] = True
                    elif skin_unlocked[0] and 'equip1_rect' in locals() and equip1_rect.collidepoint(mouse_pos):
                        current_skin = 1
                    elif skin_unlocked[1] and 'equip2_rect' in locals() and equip2_rect.collidepoint(mouse_pos):
                        current_skin = 2
                
                if back_rect.collidepoint(mouse_pos):
                    return coins_for_shop, barrier_bought, skin_unlocked, current_skin

# ===== ГЛАВНОЕ МЕНЮ =====
def main_menu(crystals, coins, wave, upgrade_levels, boss_rush_mode, finish_tower_health, coins_for_shop, barrier_unlocked, skin_unlocked, current_skin):
    selected_upgrade = 0
    upgrades = [
        "Урон башен (+3) - 60 монет",
        "Дальность башен (+20) - 50 монет",
        "Скорострельность (-3 кадра) - 70 монет"
    ]
    
    music_on = True
    init_music()
    
    while True:
        screen.fill(BLACK)
        
        for i in range(50):
            pygame.draw.circle(screen, (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150)), 
                             (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)), 1)
        
        title = font_big.render("TOWER DEFENCE - ХАРДКОР", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        info = font.render(f"Монет: {coins}   Кристаллы: {crystals}   Волна: {wave}   Башня финиш HP: {int(finish_tower_health)}", True, LIGHT_BLUE)
        screen.blit(info, (20, 100))
        
        shop_info = font.render(f"Монет для магазина: {coins_for_shop}", True, GOLD)
        screen.blit(shop_info, (20, 140))
        
        skin_text = "Скин: "
        if current_skin == 1:
            skin_text += "ЗОЛОТОЙ"
        elif current_skin == 2:
            skin_text += "ПЛАТИНОВЫЙ"
        else:
            skin_text += "ОБЫЧНЫЙ"
        skin_info = font_small.render(skin_text, True, CYAN)
        screen.blit(skin_info, (20, 170))
        
        stats_text = font_small.render(f"Текущие статы: Урон: {upgrade_levels['damage']} | Дальность: {upgrade_levels['range']} | Перезарядка: {upgrade_levels['cooldown']} кадров", True, WHITE)
        screen.blit(stats_text, (20, 200))

        mouse_x, mouse_y = pygame.mouse.get_pos()

        for i, up_text in enumerate(upgrades):
            y = 240 + i * 50
            color = GREEN if selected_upgrade == i else GRAY
            pygame.draw.rect(screen, color, (150, y, 700, 40))
            text_surf = font.render(up_text, True, BLACK)
            screen.blit(text_surf, (170, y + 8))

        buy_rect = pygame.Rect(150, 410, 300, 50)
        pygame.draw.rect(screen, ORANGE, buy_rect)
        buy_text = font.render("Купить выбранное улучшение", True, BLACK)
        screen.blit(buy_text, (160, 425))

        shop_rect = pygame.Rect(150, 470, 200, 50)
        pygame.draw.rect(screen, PINK, shop_rect)
        shop_text = font.render("МАГАЗИН", True, BLACK)
        screen.blit(shop_text, (210, 485))

        boss_rect = pygame.Rect(370, 470, 200, 50)
        pygame.draw.rect(screen, PURPLE if boss_rush_mode else GRAY, boss_rect)
        boss_text = font.render("BOSS RUSH", True, BLACK)
        screen.blit(boss_text, (400, 485))

        help_rect = pygame.Rect(590, 470, 200, 50)
        pygame.draw.rect(screen, BLUE, help_rect)
        help_text = font.render("HELP", True, BLACK)
        screen.blit(help_text, (660, 485))
        
        music_rect = pygame.Rect(810, 470, 100, 50)
        pygame.draw.rect(screen, GREEN if music_on else RED, music_rect)
        music_text = font.render("MUSIC", True, BLACK)
        screen.blit(music_text, (835, 485))

        start_rect = pygame.Rect(150, 540, 300, 50)
        pygame.draw.rect(screen, GREEN, start_rect)
        start_text = font.render("Начать волну", True, BLACK)
        screen.blit(start_text, (240, 555))
        
        newgame_rect = pygame.Rect(470, 540, 200, 50)
        pygame.draw.rect(screen, RED, newgame_rect)
        newgame_text = font.render("Новая игра", True, WHITE)
        screen.blit(newgame_text, (520, 555))
        
        save_rect = pygame.Rect(690, 540, 200, 50)
        pygame.draw.rect(screen, GRAY, save_rect)
        save_text = font.render("Сохранить и выйти", True, WHITE)
        screen.blit(save_text, (715, 555))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(wave, crystals, coins, upgrade_levels, boss_rush_mode, finish_tower_health, coins_for_shop, skin_unlocked, current_skin)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_upgrade = (selected_upgrade - 1) % 3
                if event.key == pygame.K_DOWN:
                    selected_upgrade = (selected_upgrade + 1) % 3
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buy_rect.collidepoint(mouse_x, mouse_y):
                    if selected_upgrade == 0 and coins >= 60:
                        coins -= 60
                        upgrade_levels["damage"] += 3
                    elif selected_upgrade == 1 and coins >= 50:
                        coins -= 50
                        upgrade_levels["range"] += 20
                    elif selected_upgrade == 2 and coins >= 70:
                        coins -= 70
                        upgrade_levels["cooldown"] = max(15, upgrade_levels["cooldown"] - 3)
                elif start_rect.collidepoint(mouse_x, mouse_y):
                    save_game(wave, crystals, coins, upgrade_levels, boss_rush_mode, finish_tower_health, coins_for_shop, skin_unlocked, current_skin)
                    return coins, upgrade_levels, boss_rush_mode, finish_tower_health, coins_for_shop, barrier_unlocked, skin_unlocked, current_skin
                elif help_rect.collidepoint(mouse_x, mouse_y):
                    show_help()
                elif boss_rect.collidepoint(mouse_x, mouse_y):
                    boss_rush_mode = not boss_rush_mode
                elif shop_rect.collidepoint(mouse_x, mouse_y):
                    new_coins, barrier_unlocked, skin_unlocked, current_skin = shop_menu(coins_for_shop, skin_unlocked, current_skin)
                    coins_for_shop = new_coins
                    save_game(wave, crystals, coins, upgrade_levels, boss_rush_mode, finish_tower_health, coins_for_shop, skin_unlocked, current_skin)
                elif newgame_rect.collidepoint(mouse_x, mouse_y):
                    return 0, {"damage": 15, "range": 120, "cooldown": 30}, False, 500, 0, False, [False, False], 0
                elif save_rect.collidepoint(mouse_x, mouse_y):
                    save_game(wave, crystals, coins, upgrade_levels, boss_rush_mode, finish_tower_health, coins_for_shop, skin_unlocked, current_skin)
                    pygame.quit()
                    sys.exit()
                elif music_rect.collidepoint(mouse_x, mouse_y):
                    if music_on:
                        pygame.mixer.music.pause()
                        music_on = False
                    else:
                        pygame.mixer.music.unpause()
                        music_on = True

def show_help():
    help_text = [
        "========== TOWER DEFENCE - ХАРДКОР ==========",
        "",
        "1. ТУРЕЛИ:",
        "   - ХП: 400",
        "   - Можно менять скины в магазине",
        "",
        "2. МАГАЗИН:",
        "   - ТОВАРЫ: Башня-Барьер (300 монет)",
        "   - СКИНЫ: Скин 1 (300 монет), Скин 2 (499 монет)",
        "",
        "3. БАШНЯ-БАРЬЕР:",
        "   - Ставится НА ПУТЬ",
        "   - Останавливает врагов",
        "   - Босс ломает с 1 удара",
        "",
        "4. СТРЕЛКИ появляются с 6 волны",
        "5. Босс убивает башню-финиш за 1 удар",
        "6. Клавиши: 1 - Турель, 2 - Барьер",
        "",
        "Нажмите ЛЮБУЮ клавишу"
    ]
    waiting = True
    while waiting:
        screen.fill(BLACK)
        y = 50
        for line in help_text:
            text = font_small.render(line, True, WHITE)
            screen.blit(text, (50, y))
            y += 25
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# ===== ОСНОВНОЙ ИГРОВОЙ ЦИКЛ =====
def game_loop():
    wave, crystals, coins, upgrade_levels, boss_rush_mode, finish_tower_health, coins_for_shop, skin_unlocked, current_skin = load_game()
    barrier_unlocked = False
    
    while True:
        result = main_menu(crystals, coins, wave, upgrade_levels, boss_rush_mode, finish_tower_health, coins_for_shop, barrier_unlocked, skin_unlocked, current_skin)
        coins, upgrade_levels, boss_rush_mode, finish_tower_health, coins_for_shop, barrier_unlocked, skin_unlocked, current_skin = result
        
        if coins == 0 and upgrade_levels == {"damage": 15, "range": 120, "cooldown": 30}:
            wave = 1
            crystals = 0
            coins = 0
            finish_tower_health = 500
            coins_for_shop = 0
            barrier_unlocked = False
            skin_unlocked = [False, False]
            current_skin = 0
            upgrade_levels = {"damage": 15, "range": 120, "cooldown": 30}
            boss_rush_mode = False
            save_game(wave, crystals, coins, upgrade_levels, boss_rush_mode, finish_tower_health, coins_for_shop, skin_unlocked, current_skin)
        
        if finish_tower_health <= 0:
            game_over_text = font_big.render("GAME OVER! Башня финиш разрушена!", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            wave, crystals, coins, upgrade_levels, boss_rush_mode, finish_tower_health, coins_for_shop, skin_unlocked, current_skin = load_game()
            continue
        
        crystals = 30
        
        finish_tower = FinishTower(end_pos[0], end_pos[1])
        finish_tower.health = finish_tower_health
        
        mobs = []
        wave_active = True
        towers = []
        barriers = []
        boss_streak = 0
        selected_tower_type = 0
        
        if boss_rush_mode:
            mobs_to_spawn = 3 + wave // 3
        else:
            mobs_to_spawn = 5 + wave // 2
        
        spawn_timer = 0
        is_boss_wave = (wave % 5 == 0) or boss_rush_mode
        boss_spawned_for_wave = False
        
        while wave_active:
            screen.fill(BLACK)
            
            for i in range(len(waypoints) - 1):
                pygame.draw.line(screen, GRAY, waypoints[i], waypoints[i + 1], 8)
                pygame.draw.line(screen, BROWN, waypoints[i], waypoints[i + 1], 4)
            
            for zone in forbidden_zones:
                alpha_surf = pygame.Surface((zone["radius"] * 2, zone["radius"] * 2), pygame.SRCALPHA)
                pygame.draw.circle(alpha_surf, (255, 0, 0, 100), (zone["radius"], zone["radius"]), zone["radius"])
                screen.blit(alpha_surf, (zone["x"] - zone["radius"], zone["y"] - zone["radius"]))
                pygame.draw.circle(screen, RED, (zone["x"], zone["y"]), zone["radius"], 2)
            
            pygame.draw.circle(screen, GREEN, start_pos, 20)
            finish_tower.draw(screen)
            start_text = font_small.render("СТАРТ", True, WHITE)
            screen.blit(start_text, (start_pos[0] - 20, start_pos[1] - 35))
            
            if spawn_timer <= 0 and len(mobs) < mobs_to_spawn:
                if boss_rush_mode:
                    boss_streak += 1
                    mobs.append(Mob(wave, is_boss=True, boss_streak=boss_streak))
                    spawn_timer = 60
                else:
                    if is_boss_wave and not boss_spawned_for_wave and len(mobs) == 0:
                        mobs.append(Mob(wave, is_boss=True))
                        boss_spawned_for_wave = True
                        spawn_timer = 60
                    else:
                        is_ranged = (wave >= 6 and random.random() < 0.3)
                        mobs.append(Mob(wave, is_boss=False, is_ranged=is_ranged))
                        spawn_timer = 40
            else:
                if spawn_timer > 0:
                    spawn_timer -= 1
            
            for barrier in barriers:
                barrier.update(mobs)
                for mob in mobs:
                    if barrier.affected_mobs.get(mob, 0) > 0:
                        mob.speed = 0
                    else:
                        mob.speed = mob.original_speed
            
            for mob in mobs[:]:
                mob.move()
                if mob.reached_end():
                    finish_tower.health -= mob.damage_to_finish
                    mobs.remove(mob)
                    if finish_tower.health <= 0:
                        wave_active = False
                        break
            
            for mob in mobs:
                mob.attack_towers(towers, finish_tower)
            
            towers = [t for t in towers if t.active]
            barriers = [b for b in barriers if b.active]
            
            for tower in towers:
                tower.update(mobs)
                tower.update_bullets()
            
            for mob in mobs[:]:
                if mob.health <= 0:
                    crystals += mob.crystals_reward
                    coins += mob.coins_reward
                    coins_for_shop += mob.coins_reward // 2
                    mobs.remove(mob)
            
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_game(wave, crystals, coins, upgrade_levels, boss_rush_mode, finish_tower.health, coins_for_shop, skin_unlocked, current_skin)
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        selected_tower_type = 0
                    if event.key == pygame.K_2 and barrier_unlocked:
                        selected_tower_type = 1
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    exit_rect = pygame.Rect(SCREEN_WIDTH - 120, 10, 110, 30)
                    if exit_rect.collidepoint(mouse_pos):
                        wave_active = False
                        break
                    
                    if crystals >= 25:
                        can_place = True
                        
                        if selected_tower_type == 0:
                            for point in waypoints:
                                if math.hypot(mouse_pos[0] - point[0], mouse_pos[1] - point[1]) < 35:
                                    can_place = False
                            
                            for tower in towers:
                                if math.hypot(mouse_pos[0] - tower.x, mouse_pos[1] - tower.y) < 40:
                                    can_place = False
                            
                            if math.hypot(mouse_pos[0] - finish_tower.x, mouse_pos[1] - finish_tower.y) < 40:
                                can_place = False
                            
                            for zone in forbidden_zones:
                                if math.hypot(mouse_pos[0] - zone["x"], mouse_pos[1] - zone["y"]) < zone["radius"]:
                                    can_place = False
                            
                            if can_place:
                                towers.append(Tower(mouse_pos[0], mouse_pos[1],
                                                    upgrade_levels["damage"],
                                                    upgrade_levels["range"],
                                                    upgrade_levels["cooldown"],
                                                    current_skin))
                                crystals -= 25
                        
                        elif selected_tower_type == 1 and barrier_unlocked:
                            on_path = False
                            for i in range(len(waypoints) - 1):
                                p1 = waypoints[i]
                                p2 = waypoints[i + 1]
                                dist = abs((p2[1]-p1[1])*mouse_pos[0] - (p2[0]-p1[0])*mouse_pos[1] + p2[0]*p1[1] - p2[1]*p1[0]) / math.hypot(p2[0]-p1[0], p2[1]-p1[1])
                                if dist < 30:
                                    on_path = True
                                    break
                            
                            for barrier in barriers:
                                if math.hypot(mouse_pos[0] - barrier.x, mouse_pos[1] - barrier.y) < 40:
                                    can_place = False
                            
                            if on_path and can_place:
                                barriers.append(BarrierTower(mouse_pos[0], mouse_pos[1]))
                                crystals -= 25
            
            for mob in mobs:
                mob.draw(screen)
            for tower in towers:
                tower.draw(screen)
            for barrier in barriers:
                barrier.draw(screen)
            
            pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, 80))
            pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
            
            mode_text = "BOSS RUSH" if boss_rush_mode else "ОБЫЧНЫЙ"
            tower_type_text = "БАРЬЕР" if (selected_tower_type == 1 and barrier_unlocked) else "ТУРЕЛЬ"
            ui_text = font.render(f"Кристаллы: {crystals}   Монеты: {coins}   Волна: {wave}   Режим: {mode_text}   Тип: {tower_type_text} (1/2)", True, YELLOW)
            screen.blit(ui_text, (10, 10))
            tower_cost = font.render("Новая башня: 25 кристаллов (клик по полю)", True, LIGHT_BLUE)
            screen.blit(tower_cost, (10, 45))
            mobs_left = font.render(f"Врагов: {len(mobs)}/{mobs_to_spawn}", True, WHITE)
            screen.blit(mobs_left, (SCREEN_WIDTH - 200, 20))
            tower_count = font.render(f"Башен: {len(towers)}   Барьеров: {len(barriers)}", True, WHITE)
            screen.blit(tower_count, (SCREEN_WIDTH - 250, 50))
            
            exit_rect = pygame.Rect(SCREEN_WIDTH - 120, 10, 110, 30)
            pygame.draw.rect(screen, DARK_RED, exit_rect)
            pygame.draw.rect(screen, WHITE, exit_rect, 2)
            exit_text = font_small.render("Выйти", True, WHITE)
            screen.blit(exit_text, (SCREEN_WIDTH - 85, 15))
            
            if crystals >= 25:
                hint_text = font_small.render("✓ Можно поставить башню (25 кристаллов)", True, GREEN)
            else:
                hint_text = font_small.render("✗ Недостаточно кристаллов (нужно 25)", True, RED)
            screen.blit(hint_text, (SCREEN_WIDTH - 350, SCREEN_HEIGHT - 35))
            
            hint2_text = font_small.render("1 - Турель | 2 - Барьер", True, CYAN)
            screen.blit(hint2_text, (SCREEN_WIDTH - 350, SCREEN_HEIGHT - 55))
            
            pygame.display.flip()
            clock.tick(FPS)
            
            if len(mobs) == 0 and spawn_timer <= 0 and wave_active:
                wave_active = False
                break
            
            if finish_tower.health <= 0:
                wave_active = False
                break
        
        save_game(wave, crystals, coins, upgrade_levels, boss_rush_mode, finish_tower.health, coins_for_shop, skin_unlocked, current_skin)
        
        if finish_tower.health > 0:
            wave += 1

if __name__ == "__main__":
    game_loop()