# icons.py — Иконки из Nerd Font (только безопасный диапазон FA 4.7)

ICONS = {
    # === Меню и навигация ===
    "play": "\uf04b",
    "pause": "\uf04c",
    "stop": "\uf04d",
    "settings": "\uf013",
    "gear": "\uf085",
    "palette": "\uf1fc",
    "colors": "\uf1fc",
    "exit": "\uf011",
    "power": "\uf011",
    "back": "\uf060",
    "forward": "\uf061",
    "arrow_left": "\uf053",
    "arrow_right": "\uf054",
    "arrow_up": "\uf077",
    "arrow_down": "\uf078",
    "check": "\uf00c",
    "cross": "\uf00d",
    "plus": "\uf067",
    "minus": "\uf068",
    "home": "\uf015",

    # === Игроки и режимы ===
    "user": "\uf007",
    "users": "\uf0c0",
    "robot": "\uf2db",        # microchip — отлично для бота
    "chip": "\uf2db",
    "desktop": "\uf108",
    "laptop": "\uf109",
    "network": "\uf0ac",      # globe
    "wifi": "\uf1eb",
    "server": "\uf233",
    "link": "\uf0c1",
    "sitemap": "\uf0e8",

    # === Игра ===
    "trophy": "\uf091",
    "star": "\uf005",
    "heart": "\uf004",
    "flag": "\uf024",
    "flag_checkered": "\uf11e",
    "target": "\uf140",
    "crosshair": "\uf05b",
    "fire": "\uf06d",
    "bolt": "\uf0e7",
    "shield": "\uf132",
    "bomb": "\uf1e2",
    "magic": "\uf0d0",
    "gamepad": "\uf11b",
    "cube": "\uf1b2",
    "rocket": "\uf135",

    # === Состояния ===
    "warning": "\uf071",
    "info": "\uf05a",
    "error": "\uf057",
    "success": "\uf058",
    "question": "\uf059",
    "clock": "\uf017",
    "hourglass": "\uf254",
    "spinner": "\uf110",
    "ban": "\uf05e",

    # === Управление ===
    "keyboard": "\uf11c",
    "mouse_pointer": "\uf245",

    # === Сеть ===
    "disconnect": "\uf127",   # chain-broken
    "connect": "\uf0c1",
    "signal": "\uf012",
    "refresh": "\uf021",
    "search": "\uf002",
    "download": "\uf019",
    "upload": "\uf093",

    # === Разное ===
    "trash": "\uf1f8",
    "save": "\uf0c7",
    "eye": "\uf06e",
    "eye_slash": "\uf070",
    "lock": "\uf023",
    "unlock": "\uf09c",
    "volume": "\uf028",
    "mute": "\uf026",
    "list": "\uf03a",
    "bars": "\uf0c9",
    "language": "\uf1ab",
    "expand": "\uf065",
    "compress": "\uf066",
}

# Текстовые fallback'и, если глиф не найден в шрифте
ICON_FALLBACKS = {
    "play": ">",
    "pause": "||",
    "settings": "*",
    "gear": "*",
    "palette": "#",
    "colors": "#",
    "exit": "X",
    "power": "X",
    "back": "<",
    "forward": ">",
    "check": "v",
    "cross": "x",
    "user": "@",
    "users": "@@",
    "robot": "AI",
    "network": "N",
    "server": "S",
    "trophy": "!",
    "star": "*",
    "search": "?",
    "disconnect": "/",
    "refresh": "@",
    "warning": "!",
    "error": "X",
    "success": "v",
    "language": "A",
}
