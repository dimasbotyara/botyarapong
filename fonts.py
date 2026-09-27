# fonts.py — Менеджер шрифтов (Inter UI, Geist акценты, Nerd Font иконки)
import os
import pygame
from settings import BASE_DIR

FONTS_DIR = os.path.join(BASE_DIR, "fonts")

FONT_PATHS = {
    "inter_regular": os.path.join(FONTS_DIR, "Inter", "Inter-Regular.ttf"),
    "inter_medium": os.path.join(FONTS_DIR, "Inter", "Inter-Medium.ttf"),
    "inter_semibold": os.path.join(FONTS_DIR, "Inter", "Inter-SemiBold.ttf"),
    "inter_bold": os.path.join(FONTS_DIR, "Inter", "Inter-Bold.ttf"),
    "geist_regular": os.path.join(FONTS_DIR, "Geist", "Geist-Regular.ttf"),
    "geist_medium": os.path.join(FONTS_DIR, "Geist", "Geist-Medium.ttf"),
    "geist_semibold": os.path.join(FONTS_DIR, "Geist", "Geist-SemiBold.ttf"),
    "geist_bold": os.path.join(FONTS_DIR, "Geist", "Geist-Bold.ttf"),
    "nerd": os.path.join(FONTS_DIR, "Symbols", "SymbolsNerdFont-Regular.ttf"),
}

_font_cache = {}
_render_cache = {}
_glyph_cache = {}
_MAX_CACHE = 600


def _load_font(font_key, size):
    cache_key = (font_key, size)
    if cache_key in _font_cache:
        return _font_cache[cache_key]

    path = FONT_PATHS.get(font_key)
    font = None
    try:
        if path and os.path.exists(path):
            font = pygame.font.Font(path, size)
    except Exception:
        font = None

    if font is None:
        try:
            font = pygame.font.SysFont("dejavusans,arial,sans", size)
        except Exception:
            font = pygame.font.Font(None, size)

    _font_cache[cache_key] = font
    return font


def get_ui_font(size, weight="regular"):
    key = f"inter_{weight}"
    if key not in FONT_PATHS:
        key = "inter_regular"
    return _load_font(key, size)


def get_accent_font(size, weight="bold"):
    key = f"geist_{weight}"
    if key not in FONT_PATHS:
        key = "geist_bold"
    return _load_font(key, size)


def get_nerd_font(size):
    return _load_font("nerd", size)


def glyph_exists(font, char):
    """Проверить, есть ли глиф в шрифте"""
    key = (id(font), char)
    if key in _glyph_cache:
        return _glyph_cache[key]
    result = False
    try:
        metrics = font.metrics(char)
        result = bool(metrics) and metrics[0] is not None
    except Exception:
        result = False
    _glyph_cache[key] = result
    return result


def render_with_icons(text, size, color, weight="regular", accent=False):
    """Рендер строки с маркерами [icon:name]"""
    from icons import ICONS, ICON_FALLBACKS

    cache_key = (text, size, tuple(color), weight, accent)
    if cache_key in _render_cache:
        return _render_cache[cache_key]

    if accent:
        main_font = get_accent_font(size, weight)
    else:
        main_font = get_ui_font(size, weight)

    icon_size = max(8, int(size * 0.92))
    icon_font = get_nerd_font(icon_size)

    # === Парсинг маркеров ===
    parts = []
    current = ""
    i = 0
    while i < len(text):
        if text[i:i + 6] == "[icon:":
            end = text.find("]", i)
            if end == -1:
                current += text[i]
                i += 1
                continue
            if current:
                parts.append(("text", current))
                current = ""
            icon_name = text[i + 6:end]
            icon_char = ICONS.get(icon_name)
            if icon_char and glyph_exists(icon_font, icon_char):
                parts.append(("icon", icon_char))
            else:
                fb = ICON_FALLBACKS.get(icon_name, "")
                if fb:
                    parts.append(("text", fb))
            i = end + 1
        else:
            current += text[i]
            i += 1
    if current:
        parts.append(("text", current))

    if not parts:
        surf = main_font.render(" ", True, color)
        _add_to_cache(cache_key, surf)
        return surf

    # === Рендер частей ===
    rendered = []
    total_w = 0
    max_h = 0
    for kind, content in parts:
        try:
            if kind == "icon":
                s = icon_font.render(content, True, color)
            else:
                s = main_font.render(content, True, color)
        except Exception:
            s = main_font.render("?", True, color)
        rendered.append(s)
        total_w += s.get_width()
        max_h = max(max_h, s.get_height())

    if total_w <= 0 or max_h <= 0:
        surf = main_font.render(" ", True, color)
        _add_to_cache(cache_key, surf)
        return surf

    result = pygame.Surface((total_w, max_h), pygame.SRCALPHA)
    x = 0
    for s in rendered:
        y = (max_h - s.get_height()) // 2
        result.blit(s, (x, y))
        x += s.get_width()

    _add_to_cache(cache_key, result)
    return result


def _add_to_cache(key, surf):
    if len(_render_cache) >= _MAX_CACHE:
        _render_cache.pop(next(iter(_render_cache)))
    _render_cache[key] = surf


def clear_cache():
    _render_cache.clear()
    _glyph_cache.clear()
