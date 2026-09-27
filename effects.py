# effects.py — Визуальные эффекты, частицы, фоновые эффекты
import pygame
import math
import random
from settings import COLOR_WHITE, COLOR_DARK_GRAY


class Particle:
    """Одна частица"""

    def __init__(self, x, y, vx, vy, color, lifetime=1.0, size=3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        self.vy += 50 * dt  # Немного гравитации
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        alpha = max(0, self.lifetime / self.max_lifetime)
        size = max(1, int(self.size * alpha))
        color = (
            min(255, int(self.color[0] * alpha + 50 * (1 - alpha))),
            min(255, int(self.color[1] * alpha + 50 * (1 - alpha))),
            min(255, int(self.color[2] * alpha + 50 * (1 - alpha))),
        )
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), size)


class ParticleSystem:
    """Менеджер частиц"""

    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=10, speed=100, lifetime=0.8, size=3):
        """Выпустить частицы из точки"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(speed * 0.3, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            lt = random.uniform(lifetime * 0.5, lifetime)
            sz = random.randint(max(1, size - 1), size + 1)
            self.particles.append(Particle(x, y, vx, vy, color, lt, sz))

    def emit_line(self, x1, y1, x2, y2, color, count=15, speed=80,
                  lifetime=0.5, size=2):
        """Частицы вдоль линии"""
        for i in range(count):
            t = i / max(1, count - 1)
            px = x1 + (x2 - x1) * t
            py = y1 + (y2 - y1) * t
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(speed * 0.2, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            self.particles.append(
                Particle(px, py, vx, vy, color, lifetime, size)
            )

    def emit_directional(self, x, y, direction, spread, color,
                         count=8, speed=150, lifetime=0.6, size=3):
        """Частицы в определённом направлении"""
        for _ in range(count):
            angle = direction + random.uniform(-spread, spread)
            spd = random.uniform(speed * 0.5, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            self.particles.append(
                Particle(x, y, vx, vy, color, lifetime, size)
            )

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def clear(self):
        self.particles.clear()


class BallTrail:
    """Шлейф за мячом"""

    def __init__(self, max_points=15):
        self.points = []
        self.max_points = max_points

    def add_point(self, x, y, color):
        self.points.append((x, y, color, 1.0))
        if len(self.points) > self.max_points:
            self.points.pop(0)

    def update(self, dt):
        new_points = []
        for x, y, color, alpha in self.points:
            alpha -= dt * 3
            if alpha > 0:
                new_points.append((x, y, color, alpha))
        self.points = new_points

    def draw(self, surface, ball_size):
        for i, (x, y, color, alpha) in enumerate(self.points):
            size = max(1, int(ball_size * alpha * 0.8))
            c = (
                int(color[0] * alpha * 0.5),
                int(color[1] * alpha * 0.5),
                int(color[2] * alpha * 0.5),
            )
            pygame.draw.circle(surface, c, (int(x), int(y)), size)

    def clear(self):
        self.points.clear()


class ScreenShake:
    """Тряска экрана"""

    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.timer = 0
        self.offset_x = 0
        self.offset_y = 0

    def start(self, intensity=10, duration=0.5):
        self.intensity = intensity
        self.duration = duration
        self.timer = duration

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            progress = self.timer / self.duration
            current_intensity = self.intensity * progress
            self.offset_x = random.uniform(-current_intensity, current_intensity)
            self.offset_y = random.uniform(-current_intensity, current_intensity)
        else:
            self.offset_x = 0
            self.offset_y = 0

    @property
    def active(self):
        return self.timer > 0

    @property
    def offset(self):
        return (int(self.offset_x), int(self.offset_y))


class FlashEffect:
    """Вспышка экрана (для бомбы и т.д.)"""

    def __init__(self):
        self.timer = 0
        self.duration = 0
        self.color = COLOR_WHITE
        self.max_alpha = 200

    def start(self, color=COLOR_WHITE, duration=0.5, max_alpha=200):
        self.color = color
        self.duration = duration
        self.timer = duration
        self.max_alpha = max_alpha

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt

    def draw(self, surface):
        if self.timer > 0:
            progress = self.timer / self.duration
            alpha = int(self.max_alpha * progress)
            flash_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            flash_surf.fill((*self.color[:3], alpha))
            surface.blit(flash_surf, (0, 0))

    @property
    def active(self):
        return self.timer > 0


class BackgroundEffect:
    """Фоновые звёзды/частицы"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.stars = []
        self.resize(width, height)

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.stars = []
        for _ in range(80):
            self.stars.append({
                'x': random.uniform(0, 1),
                'y': random.uniform(0, 1),
                'speed': random.uniform(0.005, 0.02),
                'size': random.uniform(1, 3),
                'brightness': random.uniform(0.2, 0.7),
                'phase': random.uniform(0, math.pi * 2),
            })

    def update(self, dt):
        for star in self.stars:
            star['x'] += star['speed'] * dt * 0.3
            star['phase'] += dt * random.uniform(0.5, 2.0)
            if star['x'] > 1.0:
                star['x'] = 0
                star['y'] = random.uniform(0, 1)

    def draw(self, surface, field_rect=None):
        for star in self.stars:
            x = int(star['x'] * self.width)
            y = int(star['y'] * self.height)
            # Мерцание
            flicker = 0.7 + 0.3 * math.sin(star['phase'])
            brightness = star['brightness'] * flicker
            c = int(255 * brightness)
            color = (c // 2, c // 2, c)  # Голубоватые звёзды
            size = max(1, int(star['size']))
            pygame.draw.circle(surface, color, (x, y), size)


class GoalFlash:
    """Эффект при забитом голе"""

    def __init__(self):
        self.timer = 0
        self.duration = 1.5
        self.player_color = COLOR_WHITE
        self.particles = ParticleSystem()

    def start(self, player_color, field_rect):
        self.timer = self.duration
        self.player_color = player_color
        # Залп частиц
        cx = field_rect[0] + field_rect[2] // 2
        cy = field_rect[1] + field_rect[3] // 2
        self.particles.emit(cx, cy, player_color, count=50, speed=300,
                            lifetime=1.2, size=4)

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            self.particles.update(dt)

    def draw(self, surface):
        if self.timer > 0:
            self.particles.draw(surface)

    @property
    def active(self):
        return self.timer > 0


class CountdownDisplay:
    """Отображение обратного отсчёта 3, 2, 1, GO!"""

    def __init__(self):
        self.timer = 0
        self.total = 4.0  # 3 секунды + "GO!" 1с
        self.active = False

    def start(self):
        self.timer = self.total
        self.active = True

    def update(self, dt):
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False
                self.timer = 0
                return True  # Сигнал: отсчёт завершён
        return False

    def draw(self, surface, field_rect):
        if not self.active:
            return

        cx = field_rect[0] + field_rect[2] // 2
        cy = field_rect[1] + field_rect[3] // 2

        if self.timer > 3.0:
            text = "3"
            scale = 1.0 - (self.timer - 3.0)
        elif self.timer > 2.0:
            text = "2"
            scale = 1.0 - (self.timer - 2.0)
        elif self.timer > 1.0:
            text = "1"
            scale = 1.0 - (self.timer - 1.0)
        else:
            text = "GO!"
            scale = self.timer

        # Размер с анимацией
        font_size = int(120 + 40 * (1 - scale))
        alpha = max(0, min(255, int(255 * (0.3 + 0.7 * (1 - scale)))))

        font = pygame.font.Font(None, font_size)
        if text == "GO!":
            color = (0, 255, 100)
        else:
            color = COLOR_WHITE

        text_surf = font.render(text, True, color)

        # Полупрозрачность
        alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.blit(text_surf, (0, 0))
        alpha_surf.set_alpha(alpha)

        rect = alpha_surf.get_rect(center=(cx, cy))
        surface.blit(alpha_surf, rect)


class PowerupIndicator:
    """Индикатор активного улучшения (полоска над ракеткой)"""

    @staticmethod
    def draw(surface, x, y, width, remaining, total, color, name):
        if total <= 0:
            return

        bar_width = width
        bar_height = 6
        ratio = max(0, remaining / total)

        # Фон
        bg_rect = pygame.Rect(x - bar_width // 2, y - 15, bar_width, bar_height)
        pygame.draw.rect(surface, (40, 40, 40), bg_rect, border_radius=3)

        # Заполнение
        fill_rect = pygame.Rect(
            bg_rect.x, bg_rect.y,
            int(bar_width * ratio), bar_height
        )
        pygame.draw.rect(surface, color, fill_rect, border_radius=3)

        # Название
        font = pygame.font.Font(None, 18)
        name_surf = font.render(name, True, color)
        name_rect = name_surf.get_rect(center=(x, y - 25))
        surface.blit(name_surf, name_rect)
