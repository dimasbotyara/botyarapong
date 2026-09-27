# objects.py — Paddle, Ball, коллизии
import pygame
import math
import random
from settings import (
    PADDLE_WIDTH_REL, PADDLE_HEIGHT_REL, PADDLE_OFFSET_REL,
    PADDLE_SPEED_REL, BALL_SIZE_REL, BALL_SPEED_REL,
    BALL_MAX_SPEED_REL, BALL_SPEED_INCREMENT,
    COLOR_WHITE, COLOR_GRAY
)


class Paddle:
    """Ракетка игрока"""

    def __init__(self, player_id, color, field_rect):
        self.player_id = player_id  # 1 или 2
        self.color = color
        self.field_rect = field_rect

        # Относительные координаты (0-1)
        self.rel_y = 0.5  # Центр
        self.rel_width = PADDLE_WIDTH_REL
        self.rel_height = PADDLE_HEIGHT_REL
        self.base_rel_height = PADDLE_HEIGHT_REL
        self.rel_speed = PADDLE_SPEED_REL

        # Позиция по X (фиксированная, зависит от player_id)
        if player_id == 1:
            self.rel_x = PADDLE_OFFSET_REL
        else:
            self.rel_x = 1.0 - PADDLE_OFFSET_REL - PADDLE_WIDTH_REL

        # Состояния улучшений
        self.frozen = False
        self.frozen_timer = 0
        self.inverted = False
        self.inverted_timer = 0
        self.phantom = False
        self.phantom_timer = 0
        self.titan = False
        self.titan_timer = 0
        self.magnet = False
        self.magnet_timer = 0
        self.sticky = False
        self.sticky_timer = 0
        self.sticky_ball_held = False
        self.sticky_hold_timer = 0
        self.electro = False
        self.electro_timer = 0
        self.clone_active = False
        self.clone_timer = 0
        self.laser_sight = False
        self.laser_timer = 0
        self.shield_tower = False
        self.shield_tower_timer = 0
        self.base_shield = False
        self.base_shield_timer = 0
        self.base_shield_wall_active = False
        self.stunned = False
        self.stunned_timer = 0
        self.pushed_back = False
        self.pushed_back_timer = 0
        self.push_offset = 0

        # Анимация
        self.hit_anim = 0

    def reset(self):
        """Сброс позиции"""
        self.rel_y = 0.5
        self.rel_height = self.base_rel_height
        self.clear_effects()

    def clear_effects(self):
        """Сброс всех эффектов"""
        self.frozen = False
        self.frozen_timer = 0
        self.inverted = False
        self.inverted_timer = 0
        self.phantom = False
        self.phantom_timer = 0
        self.titan = False
        self.titan_timer = 0
        self.magnet = False
        self.magnet_timer = 0
        self.sticky = False
        self.sticky_timer = 0
        self.sticky_ball_held = False
        self.sticky_hold_timer = 0
        self.electro = False
        self.electro_timer = 0
        self.clone_active = False
        self.clone_timer = 0
        self.laser_sight = False
        self.laser_timer = 0
        self.shield_tower = False
        self.shield_tower_timer = 0
        self.base_shield = False
        self.base_shield_wall_active = False
        self.stunned = False
        self.stunned_timer = 0
        self.pushed_back = False
        self.push_offset = 0
        self.rel_height = self.base_rel_height

    def update_field(self, field_rect):
        self.field_rect = field_rect

    def move(self, direction, dt):
        """Двигать ракетку. direction: -1 (вверх) или +1 (вниз)"""
        if self.frozen or self.stunned:
            return
        if self.base_shield_wall_active:
            return

        actual_dir = direction
        if self.inverted:
            actual_dir = -direction

        speed = self.rel_speed
        if self.titan:
            speed *= 0.35

        self.rel_y += actual_dir * speed * dt

        # Ограничение
        half_h = self.rel_height / 2
        self.rel_y = max(half_h, min(1.0 - half_h, self.rel_y))

    def update(self, dt):
        """Обновление таймеров"""
        # Frozen
        if self.frozen:
            self.frozen_timer -= dt
            if self.frozen_timer <= 0:
                self.frozen = False

        # Stunned
        if self.stunned:
            self.stunned_timer -= dt
            if self.stunned_timer <= 0:
                self.stunned = False

        # Inverted
        if self.inverted:
            self.inverted_timer -= dt
            if self.inverted_timer <= 0:
                self.inverted = False

        # Phantom
        if self.phantom:
            self.phantom_timer -= dt
            if self.phantom_timer <= 0:
                self.phantom = False

        # Titan
        if self.titan:
            self.titan_timer -= dt
            if self.titan_timer <= 0:
                self.titan = False
                self.rel_height = self.base_rel_height

        # Magnet
        if self.magnet:
            self.magnet_timer -= dt
            if self.magnet_timer <= 0:
                self.magnet = False

        # Sticky
        if self.sticky:
            self.sticky_timer -= dt
            if self.sticky_timer <= 0:
                self.sticky = False
                self.sticky_ball_held = False

        if self.sticky_ball_held:
            self.sticky_hold_timer -= dt
            if self.sticky_hold_timer <= 0:
                self.sticky_ball_held = False

        # Electro
        if self.electro:
            self.electro_timer -= dt
            if self.electro_timer <= 0:
                self.electro = False

        # Clone
        if self.clone_active:
            self.clone_timer -= dt
            if self.clone_timer <= 0:
                self.clone_active = False

        # Laser
        if self.laser_sight:
            self.laser_timer -= dt
            if self.laser_timer <= 0:
                self.laser_sight = False

        # Shield tower
        if self.shield_tower:
            self.shield_tower_timer -= dt
            if self.shield_tower_timer <= 0:
                self.shield_tower = False
                self.rel_height = self.base_rel_height

        # Base shield
        if self.base_shield_wall_active:
            self.base_shield_timer -= dt
            if self.base_shield_timer <= 0:
                self.base_shield_wall_active = False
                self.base_shield = False

        # Pushed back
        if self.pushed_back:
            self.pushed_back_timer -= dt
            self.push_offset *= 0.9
            if self.pushed_back_timer <= 0:
                self.pushed_back = False
                self.push_offset = 0

        # Hit anim
        if self.hit_anim > 0:
            self.hit_anim -= dt * 5

    def get_rect(self):
        """Получить pygame.Rect в экранных координатах"""
        fx, fy, fw, fh = self.field_rect
        px = fx + self.rel_x * fw
        py = fy + (self.rel_y - self.rel_height / 2) * fh
        pw = self.rel_width * fw
        ph = self.rel_height * fh

        # Учёт push_offset
        if self.pushed_back and self.push_offset:
            px += self.push_offset * fw

        return pygame.Rect(int(px), int(py), int(pw), int(ph))

    def get_clone_rect(self):
        """Прямоугольник двойника"""
        if not self.clone_active:
            return None
        rect = self.get_rect()
        clone_rect = rect.copy()
        clone_rect.y -= rect.height + 5
        # Ограничение в поле
        if clone_rect.y < self.field_rect[1]:
            clone_rect.y = self.field_rect[1]
        return clone_rect

    def get_base_shield_rect(self):
        """Прямоугольник щита базы"""
        if not self.base_shield_wall_active:
            return None
        fx, fy, fw, fh = self.field_rect
        if self.player_id == 1:
            sx = fx + 2
        else:
            sx = fx + fw - 8
        return pygame.Rect(sx, fy, 6, fh)

    def draw(self, surface):
        rect = self.get_rect()

        # Phantom — полупрозрачность
        if self.phantom:
            alpha_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            alpha_surf.fill((*self.color, 60))
            surface.blit(alpha_surf, rect.topleft)
        else:
            # Hit animation (подсветка)
            if self.hit_anim > 0:
                glow_color = (
                    min(255, self.color[0] + int(100 * self.hit_anim)),
                    min(255, self.color[1] + int(100 * self.hit_anim)),
                    min(255, self.color[2] + int(100 * self.hit_anim)),
                )
                pygame.draw.rect(surface, glow_color, rect.inflate(4, 4),
                                 border_radius=4)

            pygame.draw.rect(surface, self.color, rect, border_radius=3)

            # Frozen overlay
            if self.frozen:
                ice_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                ice_surf.fill((150, 220, 255, 120))
                surface.blit(ice_surf, rect.topleft)

            # Stunned overlay
            if self.stunned:
                stun_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                stun_surf.fill((255, 255, 0, 100))
                surface.blit(stun_surf, rect.topleft)

            # Titan glow
            if self.titan:
                pygame.draw.rect(surface, (200, 200, 200), rect.inflate(4, 4), 2,
                                 border_radius=5)

            # Electro sparks
            if self.electro:
                for _ in range(3):
                    sx = rect.x + random.randint(0, rect.width)
                    sy = rect.y + random.randint(0, rect.height)
                    pygame.draw.circle(surface, (100, 200, 255), (sx, sy), 2)

        # Двойник
        if self.clone_active:
            clone_rect = self.get_clone_rect()
            if clone_rect:
                clone_surf = pygame.Surface(
                    (clone_rect.width, clone_rect.height), pygame.SRCALPHA
                )
                clone_surf.fill((*self.color, 140))
                surface.blit(clone_surf, clone_rect.topleft)

        # Щит базы
        if self.base_shield_wall_active:
            shield_rect = self.get_base_shield_rect()
            if shield_rect:
                pygame.draw.rect(surface, (0, 255, 200), shield_rect, border_radius=2)

        # Magnet indicator
        if self.magnet:
            pygame.draw.circle(surface, (255, 0, 0),
                               rect.center, rect.width + 8, 2)

        # Sticky indicator
        if self.sticky:
            pygame.draw.rect(surface, (200, 200, 0), rect.inflate(6, 6), 2,
                             border_radius=5)

    def get_active_effects(self):
        """Список активных эффектов для индикации"""
        effects = []
        if self.frozen:
            effects.append(("Заморозка", self.frozen_timer, 1.5, (150, 220, 255)))
        if self.stunned:
            effects.append(("Оглушение", self.stunned_timer, 1.0, (255, 255, 0)))
        if self.inverted:
            effects.append(("Инверсия", self.inverted_timer, 5.0, (255, 0, 100)))
        if self.phantom:
            effects.append(("Фантом", self.phantom_timer, 7.0, (100, 100, 100)))
        if self.titan:
            effects.append(("Титан", self.titan_timer, 8.0, (150, 150, 150)))
        if self.magnet:
            effects.append(("Магнит", self.magnet_timer, 8.0, (200, 0, 0)))
        if self.sticky:
            effects.append(("Липучка", self.sticky_timer, 8.0, (200, 200, 0)))
        if self.electro:
            effects.append(("Электро", self.electro_timer, 6.0, (0, 150, 255)))
        if self.clone_active:
            effects.append(("Двойник", self.clone_timer, 10.0, (0, 200, 100)))
        if self.laser_sight:
            effects.append(("Лазер", self.laser_timer, 12.0, (255, 0, 0)))
        if self.shield_tower:
            effects.append(("Небоскрёб", self.shield_tower_timer, 10.0, (0, 200, 200)))
        if self.base_shield_wall_active:
            effects.append(("Щит базы", self.base_shield_timer, 15.0, (0, 255, 200)))
        return effects


class Ball:
    """Мяч"""

    def __init__(self, field_rect):
        self.field_rect = field_rect
        self.rel_x = 0.5
        self.rel_y = 0.5
        self.rel_size = BALL_SIZE_REL
        self.rel_speed = BALL_SPEED_REL
        self.base_rel_speed = BALL_SPEED_REL
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.color = COLOR_WHITE
        self.last_hit_by = 0  # 0 — никто, 1 или 2
        self.is_fake = False
        self.active = True

        # Эффекты мяча
        self.fireball = False
        self.fireball_timer = 0
        self.chaos = False
        self.chaos_timer = 0
        self.heavy = False
        self.heavy_timer = 0
        self.stealth = False
        self.stealth_timer = 0
        self.ghost = False
        self.ghost_uses = 0
        self.ice = False
        self.ice_timer = 0
        self.homing = False
        self.homing_timer = 0
        self.snail = False
        self.snail_timer = 0
        self.gravity_affected = False
        self.gravity_timer = 0

    def reset(self, direction=None):
        """Сброс мяча в центр"""
        self.rel_x = 0.5
        self.rel_y = 0.5
        self.rel_speed = self.base_rel_speed
        self.last_hit_by = 0
        self.clear_effects()

        if direction is None:
            direction = random.choice([-1, 1])

        angle = random.uniform(-math.pi / 4, math.pi / 4)
        self.vel_x = math.cos(angle) * self.rel_speed * direction
        self.vel_y = math.sin(angle) * self.rel_speed

    def clear_effects(self):
        """Сброс всех эффектов"""
        self.fireball = False
        self.chaos = False
        self.heavy = False
        self.stealth = False
        self.ghost = False
        self.ghost_uses = 0
        self.ice = False
        self.homing = False
        self.snail = False
        self.gravity_affected = False
        self.color = COLOR_WHITE

    def update_field(self, field_rect):
        self.field_rect = field_rect

    def update(self, dt, paddles=None):
        """Обновление позиции и эффектов"""
        if not self.active:
            return

        # Таймеры
        if self.fireball:
            self.fireball_timer -= dt
            if self.fireball_timer <= 0:
                self.fireball = False
                self.color = COLOR_WHITE

        if self.chaos:
            self.chaos_timer -= dt
            if self.chaos_timer <= 0:
                self.chaos = False

        if self.heavy:
            self.heavy_timer -= dt
            if self.heavy_timer <= 0:
                self.heavy = False

        if self.stealth:
            self.stealth_timer -= dt
            if self.stealth_timer <= 0:
                self.stealth = False

        if self.ice:
            self.ice_timer -= dt
            if self.ice_timer <= 0:
                self.ice = False

        if self.homing and paddles:
            self.homing_timer -= dt
            if self.homing_timer <= 0:
                self.homing = False
            else:
                self._apply_homing(paddles, dt)

        if self.snail:
            self.snail_timer -= dt
            if self.snail_timer <= 0:
                self.snail = False
                # Восстановить скорость
                speed = math.sqrt(self.vel_x ** 2 + self.vel_y ** 2)
                if speed > 0:
                    factor = self.rel_speed / speed
                    self.vel_x *= factor
                    self.vel_y *= factor

        if self.gravity_affected:
            self.gravity_timer -= dt
            if self.gravity_timer <= 0:
                self.gravity_affected = False
            else:
                self.vel_y += 0.3 * dt

        # Обновляем цвет на основе эффектов
        if self.fireball:
            self.color = (255, 100 + int(50 * math.sin(pygame.time.get_ticks() / 100)), 0)
        elif self.ice:
            self.color = (150, 220, 255)
        elif self.heavy:
            self.color = (100, 80, 60)
        elif self.snail:
            self.color = (100, 200, 100)
        elif self.chaos:
            self.color = (255, 0, 255)
        elif self.stealth:
            pass  # Handled in draw
        elif not self.is_fake:
            self.color = COLOR_WHITE

        # Перемещение
        self.rel_x += self.vel_x * dt
        self.rel_y += self.vel_y * dt

        # Отскок от верха/низа
        half_size = self.rel_size / 2
        if self.rel_y - half_size <= 0:
            self.rel_y = half_size
            self.vel_y = abs(self.vel_y)
        elif self.rel_y + half_size >= 1.0:
            self.rel_y = 1.0 - half_size
            self.vel_y = -abs(self.vel_y)

    def _apply_homing(self, paddles, dt):
        """Самоходка — подруливание к слабому месту"""
        # Определяем к какой ракетке летит мяч
        target_paddle = None
        if self.vel_x > 0 and len(paddles) > 1:
            target_paddle = paddles[1]  # Правый
        elif self.vel_x < 0 and len(paddles) > 0:
            target_paddle = paddles[0]  # Левый

        if target_paddle:
            # Целимся чуть выше/ниже ракетки
            target_y = target_paddle.rel_y
            if self.rel_y < target_y:
                # Целимся к краю ракетки снизу
                target_y += target_paddle.rel_height / 2 + 0.05
            else:
                target_y -= target_paddle.rel_height / 2 + 0.05

            # Плавно подруливаем
            diff = target_y - self.rel_y
            self.vel_y += diff * 0.5 * dt

    def get_rect(self):
        """Экранные координаты"""
        fx, fy, fw, fh = self.field_rect
        size = int(self.rel_size * fh)
        bx = fx + int(self.rel_x * fw) - size // 2
        by = fy + int(self.rel_y * fh) - size // 2
        return pygame.Rect(bx, by, size, size)

    def get_center(self):
        """Экранный центр"""
        fx, fy, fw, fh = self.field_rect
        return (fx + int(self.rel_x * fw), fy + int(self.rel_y * fh))

    def draw(self, surface):
        if not self.active:
            return

        rect = self.get_rect()
        center = self.get_center()
        radius = rect.width // 2

        # Stealth — прозрачность в центре поля
        if self.stealth:
            dist_from_center = abs(self.rel_x - 0.5) / 0.5  # 0 в центре, 1 у краёв
            if dist_from_center < 0.4:
                alpha = int(255 * (dist_from_center / 0.4))
                s = pygame.Surface((rect.width * 2, rect.height * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color, alpha),
                                   (rect.width, rect.height), radius)
                surface.blit(s, (center[0] - rect.width, center[1] - rect.height))
                return

        # Fireball glow
        if self.fireball:
            glow_surf = pygame.Surface((radius * 6, radius * 6), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 100, 0, 40),
                               (radius * 3, radius * 3), radius * 3)
            surface.blit(glow_surf,
                         (center[0] - radius * 3, center[1] - radius * 3))

        # Ghost
        if self.ghost and self.ghost_uses > 0:
            ghost_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.circle(ghost_surf, (*self.color, 130),
                               (radius, radius), radius)
            surface.blit(ghost_surf, rect.topleft)
            return

        # Обычная отрисовка
        pygame.draw.circle(surface, self.color, center, radius)

        # Ice shimmer
        if self.ice:
            pygame.draw.circle(surface, (200, 240, 255), center, radius + 3, 2)

        # Heavy — жирный контур
        if self.heavy:
            pygame.draw.circle(surface, (60, 50, 40), center, radius + 2, 3)

    def get_speed(self):
        return math.sqrt(self.vel_x ** 2 + self.vel_y ** 2)

    def set_speed(self, new_speed):
        current = self.get_speed()
        if current > 0:
            factor = new_speed / current
            self.vel_x *= factor
            self.vel_y *= factor

    def accelerate(self, factor=BALL_SPEED_INCREMENT):
        """Ускорить мяч"""
        self.vel_x *= factor
        self.vel_y *= factor
        # Ограничение
        speed = self.get_speed()
        if speed > BALL_MAX_SPEED_REL:
            self.set_speed(BALL_MAX_SPEED_REL)
        self.rel_speed = self.get_speed()

    def serialize(self):
        """Сериализация для сети"""
        return {
            'rx': round(self.rel_x, 4),
            'ry': round(self.rel_y, 4),
            'vx': round(self.vel_x, 4),
            'vy': round(self.vel_y, 4),
            'color': self.color,
            'active': self.active,
            'is_fake': self.is_fake,
            'last_hit': self.last_hit_by,
            'fireball': self.fireball,
            'ice': self.ice,
            'stealth': self.stealth,
            'heavy': self.heavy,
            'ghost': self.ghost,
            'chaos': self.chaos,
            'snail': self.snail,
            'homing': self.homing,
        }

    def deserialize(self, data):
        """Десериализация"""
        self.rel_x = data.get('rx', self.rel_x)
        self.rel_y = data.get('ry', self.rel_y)
        self.vel_x = data.get('vx', self.vel_x)
        self.vel_y = data.get('vy', self.vel_y)
        self.color = tuple(data.get('color', self.color))
        self.active = data.get('active', True)
        self.is_fake = data.get('is_fake', False)
        self.last_hit_by = data.get('last_hit', 0)
        self.fireball = data.get('fireball', False)
        self.ice = data.get('ice', False)
        self.stealth = data.get('stealth', False)
        self.heavy = data.get('heavy', False)
        self.ghost = data.get('ghost', False)
        self.chaos = data.get('chaos', False)
        self.snail = data.get('snail', False)
        self.homing = data.get('homing', False)


def check_paddle_ball_collision(paddle, ball, particles=None):
    """Проверка столкновения ракетки и мяча, возвращает True если было"""
    if not ball.active:
        return False

    paddle_rect = paddle.get_rect()
    ball_rect = ball.get_rect()

    if not paddle_rect.colliderect(ball_rect):
        # Проверяем двойника
        if paddle.clone_active:
            clone_rect = paddle.get_clone_rect()
            if clone_rect and clone_rect.colliderect(ball_rect):
                paddle_rect = clone_rect  # Используем клон для отскока
            else:
                return False
        else:
            return False

    # Ghost — проходит сквозь
    if ball.ghost and ball.ghost_uses > 0 and ball.last_hit_by != paddle.player_id:
        ball.ghost_uses -= 1
        if ball.ghost_uses <= 0:
            ball.ghost = False
        return False

    # Рассчитываем угол отскока
    paddle_center_y = paddle_rect.centery
    hit_pos = (ball_rect.centery - paddle_center_y) / (paddle_rect.height / 2)
    hit_pos = max(-1, min(1, hit_pos))

    # Угол от -60° до 60°
    max_angle = math.pi / 3
    angle = hit_pos * max_angle

    speed = ball.get_speed()
    if speed < ball.base_rel_speed:
        speed = ball.base_rel_speed

    # Направление
    if paddle.player_id == 1:
        ball.vel_x = abs(math.cos(angle) * speed)
    else:
        ball.vel_x = -abs(math.cos(angle) * speed)
    ball.vel_y = math.sin(angle) * speed

    # Вытолкнуть мяч из ракетки
    if paddle.player_id == 1:
        ball.rel_x = (paddle_rect.right - paddle.field_rect[0]) / paddle.field_rect[2] + ball.rel_size / 2
    else:
        ball.rel_x = (paddle_rect.left - paddle.field_rect[0]) / paddle.field_rect[2] - ball.rel_size / 2

    ball.last_hit_by = paddle.player_id
    ball.accelerate()
    paddle.hit_anim = 1.0

    # Частицы
    if particles:
        cx, cy = ball.get_center()
        particles.emit(cx, cy, paddle.color, count=12, speed=120, lifetime=0.5)

    return True


def check_block_collision(ball, blocks):
    """Столкновение мяча с блоками лабиринта"""
    if not blocks:
        return
    ball_rect = ball.get_rect()
    for block in blocks[:]:
        if ball_rect.colliderect(block['rect']):
            block['hp'] -= 1
            if block['hp'] <= 0:
                blocks.remove(block)

            # Определяем сторону столкновения
            dx = ball_rect.centerx - block['rect'].centerx
            dy = ball_rect.centery - block['rect'].centery

            if abs(dx) > abs(dy):
                ball.vel_x = -ball.vel_x
            else:
                ball.vel_y = -ball.vel_y
            break
