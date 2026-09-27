# ui.py — Кнопки, слайдеры, UI компоненты
import pygame
from settings import (
    COLOR_WHITE, COLOR_BLACK, COLOR_GRAY, COLOR_DARK_GRAY,
    COLOR_GREEN,
)
from fonts import get_ui_font, get_accent_font, render_with_icons


# ===== ЕДИНЫЕ КОНСТАНТЫ ОТСТУПОВ =====
LABEL_SIZE = 21          # размер шрифта подписи
LABEL_GAP = 9            # зазор между подписью и элементом
LABEL_BLOCK = 30         # общая высота зоны подписи (текст + зазор)
FIELD_H = 40             # стандартная высота поля/дропдауна
ROW_GAP = 24             # вертикальный зазор между строками
BTN_H = 48               # высота кнопки


def render_text(text, size, color, weight="regular", accent=False):
    """Обёртка рендера текста с иконками [icon:name]"""
    return render_with_icons(text, size, color, weight, accent)


def _blit_label(surface, text, x, y, color=COLOR_WHITE):
    """Рисует подпись НАД элементом с нормальным отступом"""
    if not text:
        return
    surf = render_with_icons(text, LABEL_SIZE, color, "medium")
    surface.blit(surf, (x, y - surf.get_height() - LABEL_GAP))


class VStack:
    """Вертикальный layout-стек: считает Y-координаты за тебя"""

    def __init__(self, x, start_y, width):
        self.x = x
        self.y = start_y
        self.width = width

    def row(self, height=FIELD_H, labeled=False, gap=ROW_GAP):
        """Вернуть Y для элемента и сдвинуть курсор"""
        if labeled:
            self.y += LABEL_BLOCK
        y = self.y
        self.y += height + gap
        return y

    def space(self, px):
        self.y += px

    @property
    def bottom(self):
        return self.y

    @staticmethod
    def measure(rows):
        """
        Посчитать общую высоту заранее.
        rows = [(height, labeled, gap), ...]
        """
        total = 0
        for h, labeled, gap in rows:
            if labeled:
                total += LABEL_BLOCK
            total += h + gap
        return total


class Button:
    def __init__(self, x, y, w, h, text, color=COLOR_WHITE,
                 hover_color=COLOR_GREEN, text_color=COLOR_BLACK,
                 font_size=24, weight="medium"):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.weight = weight
        self.hovered = False
        self.enabled = True
        self._hover_anim = 0.0
        self._click_anim = 0.0

    def update(self, mouse_pos, dt):
        self.hovered = self.enabled and self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.hovered else 0.0
        self._hover_anim += (target - self._hover_anim) * min(dt * 8, 1.0)
        if self._click_anim > 0:
            self._click_anim = max(0, self._click_anim - dt * 5)

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.hovered = True
                self._click_anim = 1.0
                return True
        return False

    def draw(self, surface):
        t = self._hover_anim
        base = self.color if self.enabled else (70, 70, 75)
        hov = self.hover_color if self.enabled else base
        col = (
            int(base[0] + (hov[0] - base[0]) * t),
            int(base[1] + (hov[1] - base[1]) * t),
            int(base[2] + (hov[2] - base[2]) * t),
        )

        r = self.rect.copy()
        if self._click_anim > 0:
            s = 1.0 - self._click_anim * 0.05
            nw, nh = int(r.width * s), int(r.height * s)
            r.x += (r.width - nw) // 2
            r.y += (r.height - nh) // 2
            r.width, r.height = nw, nh

        shadow = r.copy()
        shadow.x += 3
        shadow.y += 3
        pygame.draw.rect(surface, (18, 18, 22), shadow, border_radius=8)
        pygame.draw.rect(surface, col, r, border_radius=8)
        pygame.draw.rect(surface, (235, 235, 240), r, 2, border_radius=8)

        tc = self.text_color if self.enabled else (140, 140, 145)
        ts = render_with_icons(self.text, self.font_size, tc, self.weight)
        surface.blit(ts, ts.get_rect(center=r.center))


class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, current_val,
                 label="", step=1, color=COLOR_WHITE):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = current_val
        self.label = label
        self.step = step
        self.color = color
        self.dragging = False
        self.handle_radius = 11

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hit = self.rect.inflate(0, 16)
            if hit.collidepoint(event.pos):
                self.dragging = True
                self._update_value(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value(event.pos[0])
            return True
        return False

    def _update_value(self, mx):
        ratio = (mx - self.rect.x) / max(1, self.rect.width)
        ratio = max(0.0, min(1.0, ratio))
        raw = self.min_val + ratio * (self.max_val - self.min_val)
        self.value = round(raw / self.step) * self.step
        self.value = int(max(self.min_val, min(self.max_val, self.value)))

    def _value_to_x(self):
        span = max(1, self.max_val - self.min_val)
        ratio = (self.value - self.min_val) / span
        return int(self.rect.x + ratio * self.rect.width)

    def draw(self, surface):
        _blit_label(surface, self.label, self.rect.x, self.rect.y)

        cy = self.rect.centery
        pygame.draw.rect(
            surface, (70, 70, 78),
            pygame.Rect(self.rect.x, cy - 3, self.rect.width, 6),
            border_radius=3
        )
        hx = self._value_to_x()
        pygame.draw.rect(
            surface, self.color,
            pygame.Rect(self.rect.x, cy - 3, hx - self.rect.x, 6),
            border_radius=3
        )
        pygame.draw.circle(surface, self.color, (hx, cy),
                           self.handle_radius)
        pygame.draw.circle(surface, COLOR_WHITE, (hx, cy),
                           self.handle_radius, 2)

        # Значение справа
        val = render_with_icons(str(self.value), 22, self.color,
                                "semibold")
        surface.blit(
            val, val.get_rect(midleft=(self.rect.right + 14, cy))
        )


class ColorPicker:
    def __init__(self, x, y, cell_size, columns, colors, selected_color):
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.columns = columns
        self.colors = colors
        self.gap = 7
        self.selected_index = 0
        for i, c in enumerate(colors):
            if list(c) == list(selected_color):
                self.selected_index = i
                break

    def _cell_rect(self, i):
        col = i % self.columns
        row = i // self.columns
        return pygame.Rect(
            self.x + col * (self.cell_size + self.gap),
            self.y + row * (self.cell_size + self.gap),
            self.cell_size, self.cell_size
        )

    @property
    def height(self):
        rows = (len(self.colors) + self.columns - 1) // self.columns
        return rows * (self.cell_size + self.gap) - self.gap

    @property
    def width(self):
        return self.columns * (self.cell_size + self.gap) - self.gap

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self.colors)):
                if self._cell_rect(i).collidepoint(event.pos):
                    self.selected_index = i
                    return True
        return False

    @property
    def selected_color(self):
        return self.colors[self.selected_index]

    def draw(self, surface):
        for i, color in enumerate(self.colors):
            rect = self._cell_rect(i)
            pygame.draw.rect(surface, color, rect, border_radius=5)
            if i == self.selected_index:
                pygame.draw.rect(surface, COLOR_WHITE,
                                 rect.inflate(7, 7), 3, border_radius=7)
            else:
                pygame.draw.rect(surface, (55, 55, 62), rect, 1,
                                 border_radius=5)


class TextInput:
    def __init__(self, x, y, w, h, text="", max_length=20,
                 placeholder="...", label=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.max_length = max_length
        self.placeholder = placeholder
        self.label = label
        self.active = False
        self.cursor_timer = 0
        self.cursor_visible = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.active = False
                return True
            if len(self.text) < self.max_length and \
                    event.unicode and event.unicode.isprintable():
                self.text += event.unicode
                return True
        return False

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, surface):
        _blit_label(surface, self.label, self.rect.x, self.rect.y)

        bg = (58, 58, 66) if self.active else (34, 34, 40)
        pygame.draw.rect(surface, bg, self.rect, border_radius=7)
        border = COLOR_GREEN if self.active else (85, 85, 95)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=7)

        if self.text:
            ts = render_with_icons(self.text, 22, COLOR_WHITE, "regular")
        else:
            ts = render_with_icons(self.placeholder, 22, (110, 110, 120),
                                   "regular")

        tr = ts.get_rect(midleft=(self.rect.x + 12, self.rect.centery))
        surface.set_clip(self.rect.inflate(-18, -6))
        surface.blit(ts, tr)
        surface.set_clip(None)

        if self.active and self.cursor_visible:
            cx = tr.right + 3 if self.text else self.rect.x + 12
            pygame.draw.line(
                surface, COLOR_WHITE,
                (cx, self.rect.y + 9), (cx, self.rect.bottom - 9), 2
            )


class Toggle:
    """Переключатель. rect = зона трека, подпись рисуется сверху."""

    TRACK_W = 54
    TRACK_H = 28

    def __init__(self, x, y, label="", state=False, color=COLOR_GREEN):
        self.rect = pygame.Rect(x, y, self.TRACK_W, self.TRACK_H)
        self.label = label
        self.state = state
        self.color = color
        self._anim = 1.0 if state else 0.0
        self._label_w = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hit = pygame.Rect(
                self.rect.x, self.rect.y - LABEL_BLOCK,
                max(self.rect.width, self._label_w + 10),
                self.rect.height + LABEL_BLOCK
            )
            if hit.collidepoint(event.pos):
                self.state = not self.state
                return True
        return False

    def update(self, dt):
        target = 1.0 if self.state else 0.0
        self._anim += (target - self._anim) * min(dt * 12, 1.0)

    def draw(self, surface):
        if self.label:
            ls = render_with_icons(self.label, LABEL_SIZE, COLOR_WHITE,
                                   "medium")
            self._label_w = ls.get_width()
            surface.blit(
                ls,
                (self.rect.x,
                 self.rect.y - ls.get_height() - LABEL_GAP)
            )

        off = (78, 78, 86)
        tc = (
            int(off[0] + (self.color[0] - off[0]) * self._anim),
            int(off[1] + (self.color[1] - off[1]) * self._anim),
            int(off[2] + (self.color[2] - off[2]) * self._anim),
        )
        pygame.draw.rect(surface, tc, self.rect, border_radius=14)

        knob_x = int(self.rect.x + 14 + self._anim * (self.TRACK_W - 28))
        pygame.draw.circle(surface, COLOR_WHITE,
                           (knob_x, self.rect.centery), 11)


class DropDown:
    """Выпадающий список. Открывается вверх, если не влезает вниз."""

    def __init__(self, x, y, w, h, options, selected=0, label=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.options = options
        self.selected = selected
        self.label = label
        self.open = False
        self._drop_up = False

    def _list_rects(self, surface_h=None):
        n = len(self.options)
        h = self.rect.height
        if surface_h is not None:
            below = surface_h - self.rect.bottom
            self._drop_up = below < n * h + 10
        rects = []
        for i in range(n):
            if self._drop_up:
                y = self.rect.top - (n - i) * h
            else:
                y = self.rect.bottom + i * h
            rects.append(pygame.Rect(self.rect.x, y, self.rect.width, h))
        return rects

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        if self.open:
            for i, r in enumerate(self._list_rects()):
                if r.collidepoint(event.pos):
                    self.selected = i
                    self.open = False
                    return True
            self.open = False
            return True
        if self.rect.collidepoint(event.pos):
            self.open = True
            return True
        return False

    @property
    def value(self):
        return self.options[self.selected][1] if self.options else None

    def draw(self, surface):
        _blit_label(surface, self.label, self.rect.x, self.rect.y)

        bg = (62, 62, 70) if self.open else (34, 34, 40)
        pygame.draw.rect(surface, bg, self.rect, border_radius=7)
        pygame.draw.rect(surface, (85, 85, 95), self.rect, 2,
                         border_radius=7)

        if self.options:
            ts = render_with_icons(
                self.options[self.selected][0], 22, COLOR_WHITE,
                "regular"
            )
            surface.blit(
                ts,
                ts.get_rect(midleft=(self.rect.x + 12,
                                     self.rect.centery))
            )

        ax = self.rect.right - 20
        ay = self.rect.centery
        up = self.open and not self._drop_up
        pts = ([(ax - 5, ay + 3), (ax + 5, ay + 3), (ax, ay - 4)]
               if up else
               [(ax - 5, ay - 3), (ax + 5, ay - 3), (ax, ay + 4)])
        pygame.draw.polygon(surface, (220, 220, 230), pts)

    def draw_overlay(self, surface):
        """Вызывать ПОСЛЕДНИМ — рисует список поверх всего"""
        if not self.open:
            return
        mp = pygame.mouse.get_pos()
        rects = self._list_rects(surface.get_height())

        shadow = rects[0].union(rects[-1]).inflate(6, 6)
        shadow.x += 3
        shadow.y += 3
        pygame.draw.rect(surface, (10, 10, 14), shadow, border_radius=7)

        for i, r in enumerate(rects):
            hovered = r.collidepoint(mp)
            bg = (78, 78, 92) if hovered else (46, 46, 54)
            if i == self.selected and not hovered:
                bg = (58, 58, 70)
            pygame.draw.rect(surface, bg, r)
            pygame.draw.rect(surface, (92, 92, 102), r, 1)
            ts = render_with_icons(
                self.options[i][0], 22,
                COLOR_WHITE if hovered else (215, 215, 225), "regular"
            )
            surface.blit(
                ts, ts.get_rect(midleft=(r.x + 12, r.centery))
            )


def draw_text_centered(surface, text, y, font_size=36,
                       color=COLOR_WHITE, weight="regular",
                       accent=False):
    s = render_with_icons(text, font_size, color, weight, accent)
    surface.blit(s, s.get_rect(center=(surface.get_width() // 2, y)))


def draw_text(surface, text, x, y, font_size=24, color=COLOR_WHITE,
              anchor="topleft", weight="regular", accent=False):
    s = render_with_icons(text, font_size, color, weight, accent)
    r = s.get_rect(**{anchor: (x, y)})
    surface.blit(s, r)
    return r
