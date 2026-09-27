# powerups.py — Все 28 улучшений + спавн + таймеры
import pygame
import math
import random
from settings import (
    POWERUP_SIZE_REL, POWERUP_ATTRACT_RADIUS_REL, POWERUP_ATTRACT_SPEED_REL,
    POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX, POWERUP_NO_SPAWN_TIME,
    MAX_POWERUPS_ON_FIELD, POWERUP_CATEGORIES, POWERUP_DURATIONS,
    POWERUP_COLORS, POWERUP_NAMES, COLOR_WHITE
)


class PowerUp:
    """Улучшение на поле"""

    def __init__(self, powerup_type, rel_x, rel_y, field_rect):
        self.type = powerup_type
        self.rel_x = rel_x
        self.rel_y = rel_y
        self.field_rect = field_rect
        self.rel_size = POWERUP_SIZE_REL
        self.color = POWERUP_COLORS.get(powerup_type, COLOR_WHITE)
        self.name = POWERUP_NAMES.get(powerup_type, powerup_type)
        self.duration = POWERUP_DURATIONS.get(powerup_type, 5)
        self.active = True
        self.collected = False

        # Анимация
        self.pulse_phase = random.uniform(0, math.pi * 2)
        self.spawn_anim = 0.0  # 0 to 1 появление
        self.attracted = False  # притягивается ли к мячу

        # Определяем категорию
        self.category = "field"
        for cat, types in POWERUP_CATEGORIES.items():
            if powerup_type in types:
                self.category = cat
                break

    def update(self, dt, balls):
        """Обновление: притягивание к мячу"""
        if not self.active or self.collected:
            return

        self.pulse_phase += dt * 3
        self.spawn_anim = min(1.0, self.spawn_anim + dt * 3)

        # Притягивание к ближайшему мячу
        min_dist = float('inf')
        closest_ball = None
        for ball in balls:
            if not ball.active:
                continue
            dx = ball.rel_x - self.rel_x
            dy = ball.rel_y - self.rel_y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < min_dist:
                min_dist = dist
                closest_ball = ball

        if closest_ball and min_dist < POWERUP_ATTRACT_RADIUS_REL:
            self.attracted = True
            dx = closest_ball.rel_x - self.rel_x
            dy = closest_ball.rel_y - self.rel_y
            if min_dist > 0.001:
                # Скорость притяжения увеличивается при приближении
                attract_factor = 1.0 - (min_dist / POWERUP_ATTRACT_RADIUS_REL)
                speed = POWERUP_ATTRACT_SPEED_REL * (0.5 + attract_factor * 1.5)
                self.rel_x += (dx / min_dist) * speed * dt
                self.rel_y += (dy / min_dist) * speed * dt

            # Проверка подбора
            if min_dist < (self.rel_size + closest_ball.rel_size):
                self.collected = True
                self.active = False
                return closest_ball
        else:
            self.attracted = False

        return None

    def get_rect(self):
        fx, fy, fw, fh = self.field_rect
        size = int(self.rel_size * fh * self.spawn_anim)
        px = fx + int(self.rel_x * fw) - size // 2
        py = fy + int(self.rel_y * fh) - size // 2
        return pygame.Rect(px, py, size, size)

    def draw(self, surface):
        if not self.active:
            return

        rect = self.get_rect()
        center = (rect.centerx, rect.centery)
        radius = max(3, rect.width // 2)

        # Пульсация
        pulse = 1.0 + 0.15 * math.sin(self.pulse_phase)
        draw_radius = int(radius * pulse)

        # Аура притяжения
        if self.attracted:
            aura_radius = draw_radius + 8 + int(4 * math.sin(self.pulse_phase * 2))
            aura_surf = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (*self.color, 30),
                               (aura_radius, aura_radius), aura_radius)
            surface.blit(aura_surf,
                         (center[0] - aura_radius, center[1] - aura_radius))

        # Фон (тёмный круг)
        pygame.draw.circle(surface, (20, 20, 20), center, draw_radius + 2)

        # Основной круг
        pygame.draw.circle(surface, self.color, center, draw_radius)

        # Иконка (упрощённая)
        self._draw_icon(surface, center, draw_radius)

        # Обводка
        border_color = (
            min(255, self.color[0] + 50),
            min(255, self.color[1] + 50),
            min(255, self.color[2] + 50),
        )
        pygame.draw.circle(surface, border_color, center, draw_radius + 1, 2)

    def _draw_icon(self, surface, center, radius):
        """Рисуем символ улучшения"""
        cx, cy = center
        r = max(2, radius // 2)
        font = pygame.font.Font(None, max(12, radius))

        icon_map = {
            "magnet": "M", "shield_tower": "↑", "sticky": "●", "teleport": "T",
            "phantom": "Ø", "clone": "2", "laser_sight": "◎", "power_ram": "►",
            "titan": "▣", "electro_shield": "⚡",
            "fireball": "🔥", "multifruit": "3", "chaos_sphere": "?",
            "heavy_ball": "●", "stealth_ball": "◌", "ghost": "👻",
            "bomb": "💣", "ice_ball": "❄", "homing": "⌖", "snail": "🐌",
            "black_hole": "◉", "portals": "⊕", "inversion": "⇅",
            "earthquake": "〰", "mini_gravity": "↓",
            "speed_plates": "»", "base_shield": "▌", "mirror_labyrinth": "▦",
        }

        symbol = icon_map.get(self.type, "?")
        try:
            text_surf = font.render(symbol, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=center)
            surface.blit(text_surf, text_rect)
        except Exception:
            pygame.draw.circle(surface, (255, 255, 255), center, r, 1)

    def update_field(self, field_rect):
        self.field_rect = field_rect

    def serialize(self):
        return {
            'type': self.type,
            'rx': round(self.rel_x, 4),
            'ry': round(self.rel_y, 4),
            'active': self.active,
            'collected': self.collected,
        }


class PowerUpManager:
    """Менеджер улучшений"""

    def __init__(self, field_rect):
        self.field_rect = field_rect
        self.powerups = []
        self.spawn_timer = random.uniform(POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX)
        self.round_timer = 0
        self.all_types = []
        for types in POWERUP_CATEGORIES.values():
            self.all_types.extend(types)

        # Активные эффекты поля
        self.black_hole = None  # {'x', 'y', 'timer'}
        self.portals = None  # [{'x','y'}, {'x','y'}, timer]
        self.speed_plates = []  # [{'rect', 'timer'}]
        self.blocks = []  # [{'rect', 'hp'}]
        self.earthquake_target = 0  # 0=none, 1=p1, 2=p2
        self.earthquake_timer = 0

    def reset(self):
        self.powerups.clear()
        self.spawn_timer = random.uniform(POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX)
        self.round_timer = 0
        self.black_hole = None
        self.portals = None
        self.speed_plates.clear()
        self.blocks.clear()
        self.earthquake_target = 0
        self.earthquake_timer = 0

    def update_field(self, field_rect):
        self.field_rect = field_rect
        for p in self.powerups:
            p.update_field(field_rect)

    def update(self, dt, balls, paddles, particles=None):
        """Обновление спавна и сбора"""
        self.round_timer += dt

        # Спавн
        self.spawn_timer -= dt
        active_count = sum(1 for p in self.powerups if p.active)
        if self.spawn_timer <= 0 and self.round_timer > POWERUP_NO_SPAWN_TIME:
            if active_count < MAX_POWERUPS_ON_FIELD:
                self._spawn_random()
            self.spawn_timer = random.uniform(POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX)

        # Обновление улучшений
        for powerup in self.powerups[:]:
            result = powerup.update(dt, balls)
            if result is not None and isinstance(result, type(balls[0])) if balls else False:
                # Мяч подобрал улучшение
                ball = result
                player_id = ball.last_hit_by if ball.last_hit_by != 0 else 1
                self._activate(powerup, player_id, paddles, balls, particles)

            # Альтернативная проверка подбора (если update вернул мяч через collected)
            if powerup.collected and not powerup.active:
                # Найти мяч, который подобрал
                for ball in balls:
                    if not ball.active:
                        continue
                    dx = ball.rel_x - powerup.rel_x
                    dy = ball.rel_y - powerup.rel_y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < (powerup.rel_size + ball.rel_size) * 2:
                        player_id = ball.last_hit_by if ball.last_hit_by != 0 else 1
                        self._activate(powerup, player_id, paddles, balls, particles)
                        break

        # Убираем собранные
        self.powerups = [p for p in self.powerups if p.active]

        # Обновляем эффекты поля
        self._update_field_effects(dt, balls, paddles)

    def _spawn_random(self):
        """Спавн случайного улучшения"""
        ptype = random.choice(self.all_types)
        # Не в зонах ракеток
        rx = random.uniform(0.2, 0.8)
        ry = random.uniform(0.1, 0.9)
        powerup = PowerUp(ptype, rx, ry, self.field_rect)
        self.powerups.append(powerup)

    def _activate(self, powerup, player_id, paddles, balls, particles):
        """Активация улучшения"""
        ptype = powerup.type
        duration = powerup.duration

        # Находим игрока и соперника
        player = paddles[player_id - 1] if player_id <= len(paddles) else paddles[0]
        opponent_id = 2 if player_id == 1 else 1
        opponent = paddles[opponent_id - 1] if opponent_id <= len(paddles) else paddles[-1]

        main_ball = balls[0] if balls else None

        # === УЛУЧШЕНИЯ РАКЕТКИ ===
        if ptype == "magnet":
            player.magnet = True
            player.magnet_timer = duration

        elif ptype == "shield_tower":
            player.shield_tower = True
            player.shield_tower_timer = duration
            player.rel_height = player.base_rel_height * 2

        elif ptype == "sticky":
            player.sticky = True
            player.sticky_timer = duration

        elif ptype == "teleport":
            # Мгновенно телепортировать ракетку к мячу (по Y)
            if main_ball:
                player.rel_y = main_ball.rel_y

        elif ptype == "phantom":
            player.phantom = True
            player.phantom_timer = duration

        elif ptype == "clone":
            player.clone_active = True
            player.clone_timer = duration

        elif ptype == "laser_sight":
            player.laser_sight = True
            player.laser_timer = duration

        elif ptype == "power_ram":
            # Мощный удар — ускоряем мяч в 2 раза
            if main_ball and main_ball.last_hit_by == player_id:
                main_ball.vel_x *= 2.0
                main_ball.vel_y *= 1.5
                if particles:
                    cx, cy = main_ball.get_center()
                    particles.emit(cx, cy, (255, 150, 0), count=20, speed=200)

        elif ptype == "titan":
            player.titan = True
            player.titan_timer = duration
            player.rel_height = player.base_rel_height * 1.8

        elif ptype == "electro_shield":
            player.electro = True
            player.electro_timer = duration

        # === УЛУЧШЕНИЯ МЯЧА ===
        elif ptype == "fireball":
            if main_ball:
                main_ball.fireball = True
                main_ball.fireball_timer = 10  # Длится пока не ударит
                main_ball.vel_x *= 1.5
                main_ball.vel_y *= 1.5

        elif ptype == "multifruit":
            self._spawn_fake_balls(balls, main_ball)

        elif ptype == "chaos_sphere":
            if main_ball:
                main_ball.chaos = True
                main_ball.chaos_timer = duration

        elif ptype == "heavy_ball":
            if main_ball:
                main_ball.heavy = True
                main_ball.heavy_timer = duration

        elif ptype == "stealth_ball":
            if main_ball:
                main_ball.stealth = True
                main_ball.stealth_timer = duration

        elif ptype == "ghost":
            if main_ball:
                main_ball.ghost = True
                main_ball.ghost_uses = 1

        elif ptype == "bomb":
            # Визуальная бомба — обрабатывается в game.py через возврат
            if main_ball and particles:
                cx, cy = main_ball.get_center()
                particles.emit(cx, cy, (255, 200, 0), count=40, speed=300,
                               lifetime=1.0, size=5)

        elif ptype == "ice_ball":
            if main_ball:
                main_ball.ice = True
                main_ball.ice_timer = duration

        elif ptype == "homing":
            if main_ball:
                main_ball.homing = True
                main_ball.homing_timer = duration

        elif ptype == "snail":
            if main_ball:
                main_ball.snail = True
                main_ball.snail_timer = duration
                main_ball.vel_x *= 0.3
                main_ball.vel_y *= 0.3

        # === ЭФФЕКТЫ ПОЛЯ ===
        elif ptype == "black_hole":
            self.black_hole = {
                'x': 0.5, 'y': 0.5,
                'timer': duration
            }

        elif ptype == "portals":
            self.portals = {
                'blue': {'x': 0.3, 'y': random.uniform(0.2, 0.8)},
                'orange': {'x': 0.7, 'y': random.uniform(0.2, 0.8)},
                'timer': duration
            }

        elif ptype == "inversion":
            opponent.inverted = True
            opponent.inverted_timer = duration

        elif ptype == "earthquake":
            self.earthquake_target = opponent_id
            self.earthquake_timer = duration

        elif ptype == "mini_gravity":
            if main_ball:
                main_ball.gravity_affected = True
                main_ball.gravity_timer = duration

        elif ptype == "speed_plates":
            self._spawn_speed_plates(duration)

        elif ptype == "base_shield":
            player.base_shield = True
            player.base_shield_wall_active = True
            player.base_shield_timer = 15  # Максимальное время жизни

        elif ptype == "mirror_labyrinth":
            self._spawn_blocks()

        # Эффект подбора
        if particles:
            fx, fy, fw, fh = self.field_rect
            px = fx + int(powerup.rel_x * fw)
            py = fy + int(powerup.rel_y * fh)
            particles.emit(px, py, powerup.color, count=15, speed=100, lifetime=0.6)

        return ptype

    def _spawn_fake_balls(self, balls, main_ball):
        """Мультифрукт — 3 мяча"""
        if not main_ball:
            return

        for i in range(2):
            fake = type(main_ball)(main_ball.field_rect)
            fake.rel_x = main_ball.rel_x
            fake.rel_y = main_ball.rel_y
            fake.vel_x = main_ball.vel_x
            fake.vel_y = main_ball.vel_y + random.uniform(-0.15, 0.15)
            fake.rel_speed = main_ball.rel_speed
            fake.is_fake = True
            fake.color = (255, 0, 0)  # Сначала красные
            fake.active = True
            fake.last_hit_by = main_ball.last_hit_by
            balls.append(fake)

        # Оригинал сначала зелёный
        main_ball.color = (0, 255, 0)
        # Через 3 секунды перейдёт в обычный — обрабатывается в game.py
        main_ball._multifruit_timer = 10.0
        main_ball._multifruit_green_timer = 3.0

    def _spawn_speed_plates(self, duration):
        """Спавн ускоряющих плит"""
        fx, fy, fw, fh = self.field_rect
        for _ in range(3):
            rx = random.uniform(0.25, 0.75)
            ry = random.uniform(0.1, 0.9)
            plate_w = 0.05
            plate_h = 0.1
            self.speed_plates.append({
                'rx': rx, 'ry': ry,
                'rw': plate_w, 'rh': plate_h,
                'timer': duration
            })

    def _spawn_blocks(self):
        """Спавн блоков зеркального лабиринта"""
        fx, fy, fw, fh = self.field_rect
        self.blocks.clear()
        for row in range(4):
            for col in range(2):
                bx = 0.42 + col * 0.08
                by = 0.2 + row * 0.17
                block_w = int(0.06 * fw)
                block_h = int(0.05 * fh)
                rect = pygame.Rect(
                    fx + int(bx * fw), fy + int(by * fh),
                    block_w, block_h
                )
                self.blocks.append({
                    'rect': rect,
                    'hp': 2,
                    'rx': bx, 'ry': by,
                    'rw': 0.06, 'rh': 0.05,
                })

    def _update_field_effects(self, dt, balls, paddles):
        """Обновление эффектов поля"""
        # Чёрная дыра
        if self.black_hole:
            self.black_hole['timer'] -= dt
            if self.black_hole['timer'] <= 0:
                # Выплёвываем мяч в случайную сторону
                for ball in balls:
                    if ball.active:
                        angle = random.uniform(0, math.pi * 2)
                        speed = ball.get_speed()
                        ball.vel_x = math.cos(angle) * speed
                        ball.vel_y = math.sin(angle) * speed
                self.black_hole = None
            else:
                # Притягиваем мячи
                for ball in balls:
                    if not ball.active:
                        continue
                    dx = self.black_hole['x'] - ball.rel_x
                    dy = self.black_hole['y'] - ball.rel_y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist > 0.01:
                        force = 0.5 / max(dist, 0.05)
                        ball.vel_x += dx * force * dt
                        ball.vel_y += dy * force * dt

        # Порталы
        if self.portals:
            self.portals['timer'] -= dt
            if self.portals['timer'] <= 0:
                self.portals = None
            else:
                for ball in balls:
                    if not ball.active:
                        continue
                    # Проверка попадания в синий портал
                    dx_b = ball.rel_x - self.portals['blue']['x']
                    dy_b = ball.rel_y - self.portals['blue']['y']
                    if math.sqrt(dx_b ** 2 + dy_b ** 2) < 0.03:
                        ball.rel_x = self.portals['orange']['x']
                        ball.rel_y = self.portals['orange']['y']
                    # Проверка оранжевого
                    dx_o = ball.rel_x - self.portals['orange']['x']
                    dy_o = ball.rel_y - self.portals['orange']['y']
                    if math.sqrt(dx_o ** 2 + dy_o ** 2) < 0.03:
                        ball.rel_x = self.portals['blue']['x']
                        ball.rel_y = self.portals['blue']['y']

        # Землетрясение
        if self.earthquake_timer > 0:
            self.earthquake_timer -= dt
            if self.earthquake_timer <= 0:
                self.earthquake_target = 0

        # Ускоряющие плиты
        for plate in self.speed_plates[:]:
            plate['timer'] -= dt
            if plate['timer'] <= 0:
                self.speed_plates.remove(plate)
                continue
            for ball in balls:
                if not ball.active:
                    continue
                if (abs(ball.rel_x - plate['rx']) < plate['rw'] / 2 and
                        abs(ball.rel_y - plate['ry']) < plate['rh'] / 2):
                    speed = ball.get_speed()
                    if speed < ball.base_rel_speed * 3:
                        ball.vel_x *= 1.02
                        ball.vel_y *= 1.02

        # Блоки — обновление rect при изменении поля
        fx, fy, fw, fh = self.field_rect
        for block in self.blocks:
            block['rect'] = pygame.Rect(
                fx + int(block['rx'] * fw), fy + int(block['ry'] * fh),
                int(block['rw'] * fw), int(block['rh'] * fh)
            )

        # Chaos — случайное изменение перед ракеткой
        for ball in balls:
            if ball.chaos and ball.active:
                # Перед ракеткой (близко к краям)
                if ball.rel_x < 0.15 or ball.rel_x > 0.85:
                    if random.random() < dt * 2:  # ~2 раза в секунду
                        ball.vel_y += random.uniform(-0.3, 0.3)

    def draw(self, surface):
        """Отрисовка улучшений и эффектов поля"""
        fx, fy, fw, fh = self.field_rect

        # Улучшения
        for powerup in self.powerups:
            powerup.draw(surface)

        # Чёрная дыра
        if self.black_hole:
            cx = fx + int(self.black_hole['x'] * fw)
            cy = fy + int(self.black_hole['y'] * fh)
            radius = int(fh * 0.06)
            # Вращающееся кольцо
            t = pygame.time.get_ticks() / 200
            for i in range(8):
                angle = t + i * math.pi / 4
                rx = int(cx + math.cos(angle) * radius)
                ry = int(cy + math.sin(angle) * radius)
                pygame.draw.circle(surface, (100, 0, 200), (rx, ry), 3)
            pygame.draw.circle(surface, (20, 0, 40), (cx, cy), radius // 2)
            pygame.draw.circle(surface, (80, 0, 160), (cx, cy), radius, 2)

        # Порталы
        if self.portals:
            t = pygame.time.get_ticks() / 300
            # Синий
            bx = fx + int(self.portals['blue']['x'] * fw)
            by = fy + int(self.portals['blue']['y'] * fh)
            r = int(fh * 0.035 + 3 * math.sin(t))
            pygame.draw.circle(surface, (0, 100, 255), (bx, by), r, 3)
            pygame.draw.circle(surface, (100, 180, 255), (bx, by), r - 3)
            # Оранжевый
            ox = fx + int(self.portals['orange']['x'] * fw)
            oy = fy + int(self.portals['orange']['y'] * fh)
            pygame.draw.circle(surface, (255, 150, 0), (ox, oy), r, 3)
            pygame.draw.circle(surface, (255, 200, 100), (ox, oy), r - 3)

        # Ускоряющие плиты
        for plate in self.speed_plates:
            pr = pygame.Rect(
                fx + int((plate['rx'] - plate['rw'] / 2) * fw),
                fy + int((plate['ry'] - plate['rh'] / 2) * fh),
                int(plate['rw'] * fw),
                int(plate['rh'] * fh)
            )
            plate_surf = pygame.Surface((pr.width, pr.height), pygame.SRCALPHA)
            plate_surf.fill((255, 255, 0, 50))
            surface.blit(plate_surf, pr.topleft)
            pygame.draw.rect(surface, (255, 255, 0), pr, 2, border_radius=3)
            # Стрелки >>
            font = pygame.font.Font(None, 20)
            arr_surf = font.render("»", True, (255, 255, 0))
            surface.blit(arr_surf, arr_surf.get_rect(center=pr.center))

        # Блоки
        for block in self.blocks:
            color = (200, 200, 200) if block['hp'] > 1 else (150, 100, 100)
            pygame.draw.rect(surface, color, block['rect'], border_radius=3)
            pygame.draw.rect(surface, (100, 100, 100), block['rect'], 1,
                             border_radius=3)

    def draw_laser(self, surface, paddle, balls):
        """Рисуем лазерный прицел"""
        if not paddle.laser_sight:
            return

        main_ball = None
        for b in balls:
            if b.active and not b.is_fake and b.last_hit_by == paddle.player_id:
                main_ball = b
                break

        if not main_ball:
            return

        fx, fy, fw, fh = self.field_rect

        # Рейкаст
        bx = main_ball.rel_x
        by = main_ball.rel_y
        vx = main_ball.vel_x
        vy = main_ball.vel_y

        points = [(fx + int(bx * fw), fy + int(by * fh))]

        for _ in range(5):  # Максимум 5 отскоков
            if abs(vx) < 0.001:
                break

            # Время до стенки (вверх/вниз)
            if vy > 0:
                t_wall = (1.0 - by - main_ball.rel_size) / vy if vy > 0 else 9999
            elif vy < 0:
                t_wall = (main_ball.rel_size - by) / vy if vy < 0 else 9999
            else:
                t_wall = 9999

            # Время до края поля (лево/право)
            if vx > 0:
                t_edge = (1.0 - bx) / vx
            else:
                t_edge = -bx / vx

            t = min(abs(t_wall), abs(t_edge))
            if t > 10:
                break

            bx += vx * t
            by += vy * t

            if abs(t_wall) <= abs(t_edge):
                vy = -vy

            points.append((fx + int(bx * fw), fy + int(by * fh)))

            if abs(t_edge) <= abs(t_wall):
                break  # Достигли края

        # Рисуем пунктирную линию
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            # Пунктир
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 1:
                continue
            segments = int(dist / 10)
            for j in range(0, segments, 2):
                t1 = j / segments
                t2 = min((j + 1) / segments, 1.0)
                sp = (int(p1[0] + dx * t1), int(p1[1] + dy * t1))
                ep = (int(p1[0] + dx * t2), int(p1[1] + dy * t2))
                alpha = max(50, 200 - i * 40)
                color = (255, 0, 0, alpha) if i == 0 else (255, 100, 100, alpha)
                pygame.draw.line(surface, color[:3], sp, ep, 1)

    def serialize(self):
        data = {
            'powerups': [p.serialize() for p in self.powerups],
            'black_hole': self.black_hole,
            'earthquake_target': self.earthquake_target,
            'earthquake_timer': self.earthquake_timer,
        }
        if self.portals:
            data['portals'] = {
                'blue': self.portals['blue'],
                'orange': self.portals['orange'],
                'timer': self.portals['timer']
            }
        data['speed_plates'] = [
            {'rx': p['rx'], 'ry': p['ry'], 'rw': p['rw'],
             'rh': p['rh'], 'timer': p['timer']}
            for p in self.speed_plates
        ]
        data['blocks'] = [
            {'rx': b['rx'], 'ry': b['ry'], 'rw': b['rw'],
             'rh': b['rh'], 'hp': b['hp']}
            for b in self.blocks
        ]
        return data
