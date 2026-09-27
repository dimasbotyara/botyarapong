# settings.py — Константы, конфиг, сохранение/загрузка
import json
import os
import sys

# === ПУТИ ===
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SAVES_DIR = os.path.join(BASE_DIR, "saves")
SETTINGS_FILE = os.path.join(SAVES_DIR, "settings.json")

# Путь к эмодзи-шрифту (скачивается или берётся из системы)
EMOJI_FONT_PATH = os.path.join(BASE_DIR, "NotoColorEmoji.ttf")

# === ЗНАЧЕНИЯ ПО УМОЛЧАНИЮ ===
DEFAULT_SETTINGS = {
    "resolution": [1280, 720],
    "fullscreen": True,
    "borderless": False,
    "player_name": "Player",
    "p1_color": [0, 150, 255],
    "p2_color": [255, 70, 70],
    "bg_effects": True,
    "language": "en",
    "last_max_score": 7,
    "last_game_mode": "normal",
    "last_bot_difficulty": "medium",
}

# === ИГРОВЫЕ КОНСТАНТЫ (относительные, 0.0 - 1.0) ===
FIELD_ASPECT = 16 / 9

PADDLE_WIDTH_REL = 0.015
PADDLE_HEIGHT_REL = 0.15
PADDLE_OFFSET_REL = 0.03
PADDLE_SPEED_REL = 0.7

BALL_SIZE_REL = 0.018
BALL_SPEED_REL = 0.5
BALL_MAX_SPEED_REL = 1.2
BALL_SPEED_INCREMENT = 1.03

POWERUP_SPAWN_MIN = 5.0
POWERUP_SPAWN_MAX = 15.0
POWERUP_SIZE_REL = 0.025
POWERUP_ATTRACT_RADIUS_REL = 0.15
POWERUP_ATTRACT_SPEED_REL = 0.3
POWERUP_NO_SPAWN_TIME = 3.0
MAX_POWERUPS_ON_FIELD = 2

# Цвета
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (100, 100, 100)
COLOR_DARK_GRAY = (40, 40, 40)
COLOR_LIGHT_GRAY = (180, 180, 180)
COLOR_GREEN = (0, 255, 100)
COLOR_RED = (255, 50, 50)
COLOR_YELLOW = (255, 255, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_MAGENTA = (255, 0, 255)
COLOR_ORANGE = (255, 165, 0)
COLOR_BLUE = (0, 100, 255)
COLOR_PURPLE = (150, 0, 255)

COLOR_PALETTE = [
    (255, 50, 50),
    (255, 100, 50),
    (255, 200, 50),
    (50, 255, 50),
    (50, 255, 200),
    (50, 200, 255),
    (50, 100, 255),
    (150, 50, 255),
    (255, 50, 200),
    (255, 255, 255),
    (200, 200, 200),
    (255, 150, 150),
    (150, 255, 150),
    (150, 150, 255),
    (255, 255, 150),
    (255, 150, 255),
]

FONT_NAME = None
BUTTON_HEIGHT_REL = 0.06
BUTTON_WIDTH_REL = 0.25
MENU_SPACING_REL = 0.02

STATE_MAIN_MENU = "main_menu"
STATE_SETTINGS = "settings"
STATE_COLOR_SELECT = "color_select"
STATE_MODE_SELECT = "mode_select"
STATE_GAME_SETUP = "game_setup"
STATE_BOT_DIFFICULTY = "bot_difficulty"
STATE_NETWORK_MENU = "network_menu"
STATE_NETWORK_LOBBY = "network_lobby"
STATE_GAME = "game"
STATE_COUNTDOWN = "countdown"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"

MODE_LOCAL = "local"
MODE_BOT = "bot"
MODE_NETWORK = "network"

POWERUP_CATEGORIES = {
    "paddle": [
        "magnet", "shield_tower", "sticky", "teleport", "phantom",
        "clone", "laser_sight", "power_ram", "titan", "electro_shield"
    ],
    "ball": [
        "fireball", "multifruit", "chaos_sphere", "heavy_ball", "stealth_ball",
        "ghost", "bomb", "ice_ball", "homing", "snail"
    ],
    "field": [
        "black_hole", "portals", "inversion", "earthquake", "mini_gravity",
        "speed_plates", "base_shield", "mirror_labyrinth"
    ]
}

POWERUP_DURATIONS = {
    "magnet": 8, "shield_tower": 10, "sticky": 8, "teleport": 0,
    "phantom": 7, "clone": 10, "laser_sight": 12, "power_ram": 0,
    "titan": 8, "electro_shield": 6, "fireball": 0, "multifruit": 10,
    "chaos_sphere": 5, "heavy_ball": 8, "stealth_ball": 7, "ghost": 0,
    "bomb": 0, "ice_ball": 6, "homing": 8, "snail": 4,
    "black_hole": 6, "portals": 10, "inversion": 5, "earthquake": 4,
    "mini_gravity": 8, "speed_plates": 10, "base_shield": 0,
    "mirror_labyrinth": 12,
}

POWERUP_COLORS = {
    "magnet": (200, 0, 0), "shield_tower": (0, 200, 200),
    "sticky": (200, 200, 0), "teleport": (150, 0, 255),
    "phantom": (100, 100, 100), "clone": (0, 200, 100),
    "laser_sight": (255, 0, 0), "power_ram": (255, 150, 0),
    "titan": (150, 150, 150), "electro_shield": (0, 150, 255),
    "fireball": (255, 100, 0), "multifruit": (0, 255, 0),
    "chaos_sphere": (255, 0, 255), "heavy_ball": (100, 80, 60),
    "stealth_ball": (50, 50, 50), "ghost": (200, 200, 255),
    "bomb": (255, 50, 0), "ice_ball": (150, 220, 255),
    "homing": (255, 200, 0), "snail": (100, 200, 100),
    "black_hole": (30, 0, 50), "portals": (0, 100, 255),
    "inversion": (255, 0, 100), "earthquake": (150, 100, 50),
    "mini_gravity": (100, 0, 200), "speed_plates": (255, 255, 0),
    "base_shield": (0, 255, 200), "mirror_labyrinth": (200, 200, 200),
}

POWERUP_NAMES = {
    "magnet": "Магнит", "shield_tower": "Щит-Небоскрёб",
    "sticky": "Липучка", "teleport": "Телепорт",
    "phantom": "Фантом", "clone": "Двойник",
    "laser_sight": "Лазерный прицел", "power_ram": "Силовой таран",
    "titan": "Титан", "electro_shield": "Электро-щит",
    "fireball": "Фаербол", "multifruit": "Мультифрукт",
    "chaos_sphere": "Хаос-сфера", "heavy_ball": "Тяжёлый шар",
    "stealth_ball": "Стелс-мяч", "ghost": "Призрак",
    "bomb": "Бомба", "ice_ball": "Ледяной мяч",
    "homing": "Самоходка", "snail": "Улитка",
    "black_hole": "Чёрная дыра", "portals": "Порталы",
    "inversion": "Инверсия", "earthquake": "Землетрясение",
    "mini_gravity": "Мини-гравитация", "speed_plates": "Ускоряющие плиты",
    "base_shield": "Щит базы", "mirror_labyrinth": "Зеркальный лабиринт",
}

# Текстовые иконки вместо эмодзи (для меню)
TEXT_ICONS = {
    "play": "[>]",
    "settings": "[=]",
    "colors": "[#]",
    "exit": "[X]",
    "local": "[2P]",
    "bot": "[AI]",
    "network": "[N]",
    "back": "<-",
    "disconnect": "[DC]",
}


class Settings:
    """Менеджер настроек с сохранением/загрузкой"""

    def __init__(self):
        self.data = dict(DEFAULT_SETTINGS)
        self.load()

    def load(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                for key, value in saved.items():
                    if key in self.data:
                        self.data[key] = value
        except (json.JSONDecodeError, IOError, OSError):
            pass

    def save(self):
        try:
            os.makedirs(SAVES_DIR, exist_ok=True)
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            print(f"Ошибка сохранения настроек: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    @property
    def resolution(self):
        return tuple(self.data["resolution"])

    @resolution.setter
    def resolution(self, value):
        self.data["resolution"] = list(value)

    @property
    def fullscreen(self):
        return self.data["fullscreen"]

    @fullscreen.setter
    def fullscreen(self, value):
        self.data["fullscreen"] = value

    @property
    def p1_color(self):
        return tuple(self.data["p1_color"])

    @p1_color.setter
    def p1_color(self, value):
        self.data["p1_color"] = list(value)

    @property
    def p2_color(self):
        return tuple(self.data["p2_color"])

    @p2_color.setter
    def p2_color(self, value):
        self.data["p2_color"] = list(value)

    @property
    def player_name(self):
        return self.data["player_name"]

    @player_name.setter
    def player_name(self, value):
        self.data["player_name"] = value[:20]

    @property
    def last_max_score(self):
        return self.data["last_max_score"]

    @last_max_score.setter
    def last_max_score(self, value):
        self.data["last_max_score"] = max(1, min(21, value))

    @property
    def last_game_mode(self):
        return self.data["last_game_mode"]

    @last_game_mode.setter
    def last_game_mode(self, value):
        self.data["last_game_mode"] = value

    @property
    def last_bot_difficulty(self):
        return self.data["last_bot_difficulty"]

    @last_bot_difficulty.setter
    def last_bot_difficulty(self, value):
        self.data["last_bot_difficulty"] = value

    @property
    def bg_effects(self):
        return self.data["bg_effects"]

    def get_field_rect(self, screen_w, screen_h):
        target_aspect = FIELD_ASPECT
        screen_aspect = screen_w / screen_h

        if screen_aspect > target_aspect:
            field_h = screen_h
            field_w = int(field_h * target_aspect)
        else:
            field_w = screen_w
            field_h = int(field_w / target_aspect)

        # Уменьшаем поле, чтобы оставить место для счёта сверху
        margin_top = max(60, int(screen_h * 0.08))
        margin_bottom = max(10, int(screen_h * 0.02))
        max_field_h = screen_h - margin_top - margin_bottom

        if field_h > max_field_h:
            field_h = max_field_h
            field_w = int(field_h * target_aspect)

        field_x = (screen_w - field_w) // 2
        field_y = margin_top + (max_field_h - field_h) // 2

        return (field_x, field_y, field_w, field_h)


settings = Settings()
