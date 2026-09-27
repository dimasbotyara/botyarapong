from settings import settings

# Языки
LANG_EN = "en"
LANG_RU = "ru"

# Все строки
STRINGS = {
    # === MAIN MENU ===
    "main.title": {
        "en": "botyarapong",
        "ru": "botyarapong",
    },
    "main.subtitle": {
        "en": "Classic Pong on steroids",
        "ru": "Классический Понг на стероидах",
    },
    "main.play": {
        "en": "[icon:play]  Play",
        "ru": "[icon:play]  Играть",
    },
    "main.settings": {
        "en": "[icon:settings]  Settings",
        "ru": "[icon:settings]  Настройки",
    },
    "main.colors": {
        "en": "[icon:palette]  Player Colors",
        "ru": "[icon:palette]  Цвета игроков",
    },
    "main.exit": {
        "en": "[icon:exit]  Exit",
        "ru": "[icon:exit]  Выход",
    },
    "main.version": {
        "en": "v1.0",
        "ru": "v1.0",
    },

    # === SETTINGS ===
    "settings.title": {
        "en": "SETTINGS",
        "ru": "НАСТРОЙКИ",
    },
    "settings.resolution": {
        "en": "Resolution",
        "ru": "Разрешение",
    },
    "settings.fullscreen": {
        "en": "Fullscreen",
        "ru": "Полный экран",
    },
    "settings.bg_effects": {
        "en": "Background Effects",
        "ru": "Фоновые эффекты",
    },
    "settings.player_name": {
        "en": "Player name",
        "ru": "Имя игрока",
    },
    "settings.language": {
        "en": "Language",
        "ru": "Язык",
    },
    "settings.language_en": {
        "en": "English",
        "ru": "English",
    },
    "settings.language_ru": {
        "en": "Русский",
        "ru": "Русский",
    },
    "settings.back": {
        "en": "[icon:back]  Back",
        "ru": "[icon:back]  Назад",
    },

    # === COLOR SELECT ===
    "colors.title": {
        "en": "PLAYER COLORS",
        "ru": "ЦВЕТА ИГРОКОВ",
    },
    "colors.player1": {
        "en": "Player 1",
        "ru": "Игрок 1",
    },
    "colors.player2": {
        "en": "Player 2",
        "ru": "Игрок 2",
    },

    # === MODE SELECT ===
    "mode.title": {
        "en": "SELECT MODE",
        "ru": "ВЫБЕРИТЕ РЕЖИМ",
    },
    "mode.local": {
        "en": "[icon:users]  Local 2 Players",
        "ru": "[icon:users]  2 игрока локально",
    },
    "mode.bot": {
        "en": "[icon:robot]  vs Bot",
        "ru": "[icon:robot]  Против бота",
    },
    "mode.network": {
        "en": "[icon:network]  Network",
        "ru": "[icon:network]  По сети",
    },

    # === BOT DIFFICULTY ===
    "bot.title": {
        "en": "BOT DIFFICULTY",
        "ru": "СЛОЖНОСТЬ БОТА",
    },
    "bot.easy": {
        "en": "Easy",
        "ru": "Лёгкий",
    },
    "bot.medium": {
        "en": "Medium",
        "ru": "Средний",
    },
    "bot.hard": {
        "en": "Hard",
        "ru": "Сложный",
    },
    "bot.easy_full": {
        "en": "Easy",
        "ru": "Лёгкий",
    },
    "bot.medium_full": {
        "en": "Medium",
        "ru": "Средний",
    },
    "bot.hard_full": {
        "en": "Hard",
        "ru": "Сложный",
    },

    # === GAME SETUP ===
    "setup.title": {
        "en": "GAME SETUP",
        "ru": "НАСТРОЙКА МАТЧА",
    },
    "setup.mode": {
        "en": "Game Mode",
        "ru": "Режим игры",
    },
    "setup.mode_normal": {
        "en": "Normal",
        "ru": "Обычный",
    },
    "setup.mode_powerups": {
        "en": "Power-ups",
        "ru": "С улучшениями",
    },
    "setup.score": {
        "en": "Score to win",
        "ru": "Очков до победы",
    },
    "setup.start": {
        "en": "[icon:play]  START!",
        "ru": "[icon:play]  СТАРТ!",
    },
    "setup.vs_local": {
        "en": "Local 2 Players",
        "ru": "2 игрока локально",
    },
    "setup.vs_bot": {
        "en": "vs Bot ({diff})",
        "ru": "Против бота ({diff})",
    },
    "setup.vs_network": {
        "en": "Network vs {name}",
        "ru": "По сети vs {name}",
    },

    # === NETWORK ===
    "network.title": {
        "en": "NETWORK PLAY",
        "ru": "СЕТЕВАЯ ИГРА",
    },
    "network.create": {
        "en": "[icon:server]  Create Room",
        "ru": "[icon:server]  Создать комнату",
    },
    "network.find": {
        "en": "[icon:search]  Find Servers",
        "ru": "[icon:search]  Найти серверы",
    },
    "network.ip_label": {
        "en": "Or connect by IP:",
        "ru": "Или подключиться по IP:",
    },
    "network.ip_placeholder": {
        "en": "IP address...",
        "ru": "IP адрес...",
    },
    "network.join": {
        "en": "Join",
        "ru": "Войти",
    },
    "network.searching": {
        "en": "Searching...",
        "ru": "Поиск...",
    },
    "network.found_servers": {
        "en": "Found servers:",
        "ru": "Найденные серверы:",
    },
    "network.waiting": {
        "en": "Waiting for players...",
        "ru": "Ожидание игроков...",
    },
    "network.connecting": {
        "en": "Connecting to {ip}...",
        "ru": "Подключение к {ip}...",
    },
    "network.connected": {
        "en": "Connected to {name}",
        "ru": "Подключено к {name}",
    },
    "network.failed": {
        "en": "Connection failed!",
        "ru": "Ошибка подключения!",
    },
    "network.joined": {
        "en": "{name} joined!",
        "ru": "{name} подключился!",
    },
    "network.player_disconnected": {
        "en": "Player disconnected",
        "ru": "Игрок отключился",
    },
    "network.lobby": {
        "en": "LOBBY",
        "ru": "ЛОББИ",
    },
    "network.player_connected": {
        "en": "Player connected!",
        "ru": "Игрок подключён!",
    },
    "network.start_game": {
        "en": "[icon:play]  Start Game",
        "ru": "[icon:play]  Начать игру",
    },
    "network.cancel": {
        "en": "[icon:back]  Cancel",
        "ru": "[icon:back]  Отмена",
    },
    "network.reconnecting": {
        "en": "Reconnecting... {sec}s",
        "ru": "Переподключение... {sec}с",
    },
    "network.interrupted": {
        "en": "CONNECTION INTERRUPTED",
        "ru": "СОЕДИНЕНИЕ ПРЕРВАНО",
    },
    "network.lost": {
        "en": "CONNECTION LOST",
        "ru": "СОЕДИНЕНИЕ ПОТЕРЯНО",
    },
    "network.waiting_for": {
        "en": "Waiting for {name}...",
        "ru": "Ожидание {name}...",
    },
    "network.disconnected_msg": {
        "en": "{name} disconnected",
        "ru": "{name} отключился",
    },
    "network.disconnect_btn": {
        "en": "[icon:disconnect]  Disconnect",
        "ru": "[icon:disconnect]  Отключиться",
    },
    "network.esc_or_button": {
        "en": "ESC or button to disconnect",
        "ru": "ESC или кнопка для отключения",
    },
    "network.attempting": {
        "en": "Attempting to reconnect{dots}",
        "ru": "Попытка переподключения{dots}",
    },
    "network.press_any": {
        "en": "Press any key to return to menu",
        "ru": "Нажмите любую клавишу для возврата",
    },

    # === GAME ===
    "game.first_to": {
        "en": "First to {n}",
        "ru": "До {n} очков",
    },
    "game.powerups_mode": {
        "en": "POWER-UPS",
        "ru": "УЛУЧШЕНИЯ",
    },
    "game.paused": {
        "en": "PAUSED",
        "ru": "ПАУЗА",
    },
    "game.esc_resume": {
        "en": "ESC — resume",
        "ru": "ESC — продолжить",
    },
    "game.q_quit": {
        "en": "Q — quit to menu",
        "ru": "Q — выйти в меню",
    },
    "game.network_continues": {
        "en": "(Game continues in network mode!)",
        "ru": "(В сетевой игре геймплей продолжается!)",
    },
    "game.winner": {
        "en": "WINNER!",
        "ru": "ПОБЕДА!",
    },
    "game.game_over": {
        "en": "GAME OVER",
        "ru": "ИГРА ОКОНЧЕНА",
    },
    "game.back_to_menu": {
        "en": "ENTER — back to menu",
        "ru": "ENTER — в меню",
    },
    "game.go": {
        "en": "GO!",
        "ru": "GO!",
    },

    # === POWERUP NAMES (для индикаторов) ===
    "pu.magnet": {"en": "Magnet", "ru": "Магнит"},
    "pu.shield_tower": {"en": "Shield Tower", "ru": "Небоскрёб"},
    "pu.sticky": {"en": "Sticky", "ru": "Липучка"},
    "pu.teleport": {"en": "Teleport", "ru": "Телепорт"},
    "pu.phantom": {"en": "Phantom", "ru": "Фантом"},
    "pu.clone": {"en": "Clone", "ru": "Двойник"},
    "pu.laser_sight": {"en": "Laser", "ru": "Лазер"},
    "pu.power_ram": {"en": "Ram", "ru": "Таран"},
    "pu.titan": {"en": "Titan", "ru": "Титан"},
    "pu.electro_shield": {"en": "Electro", "ru": "Электро"},
    "pu.fireball": {"en": "Fireball", "ru": "Фаербол"},
    "pu.multifruit": {"en": "Multifruit", "ru": "Мультифрукт"},
    "pu.chaos_sphere": {"en": "Chaos", "ru": "Хаос"},
    "pu.heavy_ball": {"en": "Heavy", "ru": "Тяжёлый"},
    "pu.stealth_ball": {"en": "Stealth", "ru": "Стелс"},
    "pu.ghost": {"en": "Ghost", "ru": "Призрак"},
    "pu.bomb": {"en": "Bomb", "ru": "Бомба"},
    "pu.ice_ball": {"en": "Ice", "ru": "Лёд"},
    "pu.homing": {"en": "Homing", "ru": "Самонав."},
    "pu.snail": {"en": "Snail", "ru": "Улитка"},
    "pu.frozen": {"en": "Frozen", "ru": "Заморозка"},
    "pu.stunned": {"en": "Stunned", "ru": "Оглушение"},
    "pu.inverted": {"en": "Inverted", "ru": "Инверсия"},
    "pu.base_shield": {"en": "Base Shield", "ru": "Щит базы"},
}


def t(key, **kwargs):
    """Получить локализованную строку. Поддерживает форматирование."""
    entry = STRINGS.get(key)
    if not entry:
        return key

    lang = settings.get("language", LANG_EN)
    text = entry.get(lang) or entry.get(LANG_EN, key)

    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def get_available_languages():
    """Список доступных языков для UI"""
    return [
        (t("settings.language_en"), LANG_EN),
        (t("settings.language_ru"), LANG_RU),
    ]
