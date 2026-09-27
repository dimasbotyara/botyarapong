# game.py — Основная игровая логика, состояния
import pygame
import math
import random

from settings import (
    settings, STATE_GAME, STATE_COUNTDOWN, STATE_PAUSED, STATE_GAME_OVER,
    MODE_LOCAL, MODE_BOT, MODE_NETWORK,
    COLOR_WHITE, COLOR_GRAY, COLOR_BLACK, COLOR_GREEN,
    BALL_SIZE_REL,
)
from objects import (
    Paddle, Ball, check_paddle_ball_collision, check_block_collision
)
from powerups import PowerUpManager
from effects import (
    ParticleSystem, BallTrail, ScreenShake, FlashEffect,
    CountdownDisplay, GoalFlash, PowerupIndicator, BackgroundEffect
)
from ai import Bot
from ui import Button, draw_text_centered, draw_text, render_text
from i18n import t


class Game:
    """Основной игровой класс"""

    # =================================================================
    #  INIT
    # =================================================================

    def __init__(self, screen, mode, game_mode, p1_color, p2_color,
                 max_score=7, bot_difficulty="medium",
                 network_server=None, network_client=None,
                 p1_name="Player 1", p2_name="Player 2"):
        self.screen = screen
        self.mode = mode
        self.game_mode = game_mode
        self.max_score = max_score
        self.bot_difficulty = bot_difficulty

        self.screen_w = screen.get_width()
        self.screen_h = screen.get_height()
        self.field_rect = settings.get_field_rect(
            self.screen_w, self.screen_h
        )

        # --- Счёт и имена ---
        self.score = [0, 0]
        self.p1_name = p1_name
        self.p2_name = p2_name

        # --- Ракетки ---
        self.paddles = [
            Paddle(1, p1_color, self.field_rect),
            Paddle(2, p2_color, self.field_rect),
        ]

        # --- Мячи ---
        self.balls = [Ball(self.field_rect)]
        self.balls[0].reset()

        # --- Улучшения ---
        if game_mode == "powerups":
            self.powerup_manager = PowerUpManager(self.field_rect)
        else:
            self.powerup_manager = None

        # --- Эффекты ---
        self.particles = ParticleSystem()
        self.trail = BallTrail()
        self.shake = ScreenShake()
        self.flash = FlashEffect()
        self.countdown = CountdownDisplay()
        self.goal_flash = GoalFlash()
        self.bg_effect = BackgroundEffect(self.screen_w, self.screen_h)

        # --- Бот ---
        self.bot = Bot(bot_difficulty) if mode == MODE_BOT else None

        # --- Сеть ---
        self.network_server = network_server
        self.network_client = network_client
        self.is_host = network_server is not None
        self.is_client = network_client is not None

        # --- Состояние ---
        self.state = STATE_COUNTDOWN
        self.countdown.start()
        self.paused = False
        self.winner = None
        self.round_timer = 0
        self._goal_freeze = 0

        # --- Бомба (ослепление) ---
        self._bomb_flash_active = False
        self._bomb_flash_timer = 0
        self._bomb_flash_duration = 2.0

        # --- Липучка ---
        self._sticky_release_timers = {}

        # --- Сетевое переподключение ---
        self.network_paused = False
        self.network_gave_up = False
        self.network_status_text = ""

        # --- Кнопка отключения ---
        self.disconnect_btn = None
        self._build_disconnect_button()

    def _build_disconnect_button(self):
        btn_w = 280
        self.disconnect_btn = Button(
            (self.screen_w - btn_w) // 2,
            self.screen_h // 2 + 105,
            btn_w, 48,
            t("network.disconnect_btn"),
            font_size=24, weight="medium",
            color=(200, 60, 60), hover_color=(255, 80, 80),
            text_color=COLOR_WHITE
        )

    # =================================================================
    #  EVENTS
    # =================================================================

    def handle_event(self, event):
        """Обработка событий. Возвращает 'menu' / 'paused' / None"""

        # --- Оверлей: ждём переподключения ---
        if self.network_paused and not self.network_gave_up:
            mouse_pos = pygame.mouse.get_pos()
            self.disconnect_btn.update(mouse_pos, 0.016)
            if self.disconnect_btn.handle_event(event):
                self._network_force_disconnect()
                return "menu"
            if event.type == pygame.KEYDOWN and \
                    event.key == pygame.K_ESCAPE:
                self._network_force_disconnect()
                return "menu"
            return None

        # --- Оверлей: соединение потеряно окончательно ---
        if self.network_gave_up:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return "menu"
            return None

        # --- Обычные события ---
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                if self.state == STATE_GAME:
                    self.state = STATE_PAUSED
                    self.paused = True
                    return "paused"
                elif self.state == STATE_PAUSED:
                    self.state = STATE_COUNTDOWN
                    self.countdown.start()
                    self.paused = False
                elif self.state == STATE_GAME_OVER:
                    return "menu"

            elif self.state == STATE_GAME_OVER:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE,
                                 pygame.K_KP_ENTER):
                    return "menu"

            elif self.state == STATE_PAUSED:
                if event.key == pygame.K_q:
                    if self.mode == MODE_NETWORK:
                        self._network_force_disconnect()
                    return "menu"

        return None

    # =================================================================
    #  NETWORK
    # =================================================================

    def _network_force_disconnect(self):
        """Принудительное отключение"""
        try:
            if self.network_server:
                self.network_server.force_disconnect()
                self.network_server.stop()
        except Exception:
            pass
        try:
            if self.network_client:
                self.network_client.force_disconnect()
        except Exception:
            pass

    def _check_network_status(self):
        """Проверка живости сетевого соединения"""
        if self.network_server:
            waiting, time_left, gave_up = \
                self.network_server.get_reconnect_status()
            opponent = self.network_server.client_name or self.p2_name
        elif self.network_client:
            waiting, time_left, gave_up = \
                self.network_client.get_reconnect_status()
            opponent = self.network_client.host_name or self.p1_name
        else:
            return

        if gave_up:
            self.network_paused = True
            self.network_gave_up = True
            self.network_status_text = t(
                "network.disconnected_msg", name=opponent
            )
        elif waiting:
            self.network_paused = True
            self.network_gave_up = False
            self.network_status_text = t(
                "network.waiting_for", name=opponent
            )
        else:
            if not self.network_gave_up:
                self.network_paused = False

    def _get_reconnect_time_left(self):
        try:
            if self.network_server:
                return self.network_server.get_reconnect_status()[1]
            if self.network_client:
                return self.network_client.get_reconnect_status()[1]
        except Exception:
            pass
        return 0

    # =================================================================
    #  UPDATE
    # =================================================================

    def update(self, dt):
        # Фон всегда живёт
        if settings.bg_effects:
            self.bg_effect.update(dt)

        # Сетевой статус
        if self.mode == MODE_NETWORK:
            self._check_network_status()

        # Разрыв → всё замирает
        if self.network_paused:
            self.particles.update(dt)
            self.flash.update(dt)
            return

        # Эффекты
        self.particles.update(dt)
        self.shake.update(dt)
        self.flash.update(dt)
        self.goal_flash.update(dt)
        self.trail.update(dt)

        # Ослепление от бомбы
        if self._bomb_flash_active:
            self._bomb_flash_timer -= dt
            if self._bomb_flash_timer <= 0:
                self._bomb_flash_active = False

        # --- Countdown ---
        if self.state == STATE_COUNTDOWN:
            if self.countdown.update(dt):
                self.state = STATE_GAME
            return

        # --- Pause ---
        if self.state == STATE_PAUSED:
            # В сетевой игре геймплей НЕ останавливается
            if self.mode == MODE_NETWORK:
                self._update_gameplay(dt)
            return

        # --- Game Over ---
        if self.state == STATE_GAME_OVER:
            return

        # --- Playing ---
        if self.state == STATE_GAME:
            if self._goal_freeze > 0:
                self._goal_freeze -= dt
                return
            self._update_gameplay(dt)

    # =================================================================
    #  GAMEPLAY
    # =================================================================

    def _update_gameplay(self, dt):
        self.round_timer += dt
        keys = pygame.key.get_pressed()

        # ===== INPUT: Player 1 =====
        if self.mode != MODE_NETWORK or self.is_host:
            if keys[pygame.K_w]:
                self.paddles[0].move(-1, dt)
            if keys[pygame.K_s]:
                self.paddles[0].move(1, dt)

        # ===== INPUT: Player 2 =====
        if self.mode == MODE_LOCAL:
            if keys[pygame.K_UP]:
                self.paddles[1].move(-1, dt)
            if keys[pygame.K_DOWN]:
                self.paddles[1].move(1, dt)

        elif self.mode == MODE_BOT:
            direction = self.bot.update(
                dt, self.paddles[1], self.balls, self.powerup_manager
            )
            if direction:
                self.paddles[1].move(direction, dt)

        elif self.mode == MODE_NETWORK:
            if self.is_host and self.network_server:
                ci = self.network_server.get_client_input()
                if ci.get('up'):
                    self.paddles[1].move(-1, dt)
                if ci.get('down'):
                    self.paddles[1].move(1, dt)

            elif self.is_client:
                self.network_client.send_input({
                    'up': keys[pygame.K_w] or keys[pygame.K_UP],
                    'down': keys[pygame.K_s] or keys[pygame.K_DOWN],
                })
                state = self.network_client.get_state()
                if state:
                    self._apply_network_state(state)
                # Клиент не считает физику
                main_ball = self._get_main_ball()
                if main_ball and main_ball.active:
                    cx, cy = main_ball.get_center()
                    self.trail.add_point(cx, cy, main_ball.color)
                return

        # ===== PADDLES =====
        for paddle in self.paddles:
            paddle.update(dt)

        self._update_sticky_release(dt)

        # ===== BALLS =====
        for ball in self.balls:
            ball.update(dt, self.paddles)

        # ===== TRAIL =====
        main_ball = self._get_main_ball()
        if main_ball and main_ball.active:
            cx, cy = main_ball.get_center()
            self.trail.add_point(cx, cy, main_ball.color)

        # ===== COLLISIONS =====
        for ball in self.balls:
            if not ball.active:
                continue
            for paddle in self.paddles:
                if check_paddle_ball_collision(
                        paddle, ball, self.particles):
                    self._on_paddle_hit(paddle, ball)

        # ===== BLOCKS =====
        if self.powerup_manager and self.powerup_manager.blocks:
            for ball in self.balls:
                if ball.active:
                    check_block_collision(
                        ball, self.powerup_manager.blocks
                    )

        # ===== POWER-UPS =====
        if self.powerup_manager:
            self.powerup_manager.update(
                dt, self.balls, self.paddles, self.particles
            )
            if self.powerup_manager.earthquake_target:
                self.shake.start(intensity=8, duration=0.12)

        # ===== MULTIFRUIT =====
        self._update_multifruit(dt)

        # ===== GOALS =====
        self._check_goals()

        # ===== CLEANUP =====
        if len(self.balls) > 1:
            self.balls = [
                b for b in self.balls
                if b.active or b is self.balls[0]
            ]
        if not any(b.active for b in self.balls):
            self.balls = [Ball(self.field_rect)]
            self.balls[0].reset()

        # ===== NETWORK SEND =====
        if self.is_host and self.network_server:
            self.network_server.send_state(self._serialize_state())

    # =================================================================
    #  COLLISION EFFECTS
    # =================================================================

    def _on_paddle_hit(self, paddle, ball):
        opponent_id = 2 if paddle.player_id == 1 else 1
        opponent = self.paddles[opponent_id - 1]

        # --- Липучка ---
        if paddle.sticky and not paddle.sticky_ball_held:
            paddle.sticky_ball_held = True
            paddle.sticky_hold_timer = 1.5
            self._sticky_release_timers[paddle.player_id] = {
                'timer': 1.5,
                'ball': ball,
                'speed': max(ball.get_speed(), ball.base_rel_speed),
                'direction': 1 if paddle.player_id == 1 else -1,
            }
            ball.vel_x = 0
            ball.vel_y = 0

        # --- Электро-щит ---
        if paddle.electro:
            opponent.stunned = True
            opponent.stunned_timer = 1.0
            self.flash.start((0, 150, 255), 0.25, 90)
            cx, cy = ball.get_center()
            self.particles.emit(
                cx, cy, (0, 180, 255),
                count=18, speed=200, lifetime=0.45
            )

        # --- Фаербол ---
        if ball.fireball:
            opponent.rel_height = max(
                opponent.base_rel_height * 0.3,
                opponent.rel_height * 0.5
            )
            ball.fireball = False
            ball.fireball_timer = 0
            ball.color = COLOR_WHITE
            cx, cy = ball.get_center()
            self.particles.emit(
                cx, cy, (255, 110, 0),
                count=28, speed=220, lifetime=0.75, size=4
            )
            self.shake.start(10, 0.3)

        # --- Тяжёлый шар ---
        if ball.heavy:
            opponent.push_offset = \
                -0.03 if opponent.player_id == 1 else 0.03
            opponent.pushed_back = True
            opponent.pushed_back_timer = 0.5
            self.shake.start(6, 0.2)

        # --- Ледяной мяч ---
        if ball.ice:
            opponent.frozen = True
            opponent.frozen_timer = 1.5
            orect = opponent.get_rect()
            self.particles.emit(
                orect.centerx, orect.centery,
                (150, 220, 255),
                count=22, speed=110, lifetime=0.65
            )

        # --- Магнит ---
        if paddle.magnet:
            speed = ball.get_speed()
            if paddle.player_id == 1:
                ball.vel_x = abs(speed * 0.8)
            else:
                ball.vel_x = -abs(speed * 0.8)
            ball.vel_y *= 0.5

        # --- Бомба ---
        if getattr(ball, '_is_bomb', False):
            self._trigger_bomb(ball)
            ball._is_bomb = False

    def _trigger_bomb(self, ball):
        self._bomb_flash_active = True
        self._bomb_flash_timer = self._bomb_flash_duration
        self.shake.start(22, 0.8)
        self.flash.start(COLOR_WHITE, 0.5, 220)
        cx, cy = ball.get_center()
        self.particles.emit(
            cx, cy, (255, 200, 0),
            count=55, speed=360, lifetime=1.2, size=5
        )
        self.particles.emit(
            cx, cy, (255, 90, 0),
            count=35, speed=250, lifetime=0.85, size=3
        )

    # =================================================================
    #  STICKY
    # =================================================================

    def _update_sticky_release(self, dt):
        to_remove = []
        for pid, data in self._sticky_release_timers.items():
            data['timer'] -= dt
            ball = data['ball']

            # Мяч едет вместе с ракеткой
            if ball.active and abs(ball.vel_x) < 0.001 \
                    and abs(ball.vel_y) < 0.001:
                if 1 <= pid <= len(self.paddles):
                    ball.rel_y = self.paddles[pid - 1].rel_y

            if data['timer'] <= 0:
                if ball.active:
                    speed = data['speed']
                    direction = data['direction']
                    angle = random.uniform(-math.pi / 6, math.pi / 6)
                    ball.vel_x = math.cos(angle) * speed * direction
                    ball.vel_y = math.sin(angle) * speed
                    ball.last_hit_by = pid
                    cx, cy = ball.get_center()
                    self.particles.emit(
                        cx, cy, (220, 220, 0),
                        count=10, speed=120, lifetime=0.4
                    )
                if 1 <= pid <= len(self.paddles):
                    self.paddles[pid - 1].sticky_ball_held = False
                to_remove.append(pid)

        for pid in to_remove:
            self._sticky_release_timers.pop(pid, None)

    # =================================================================
    #  MULTIFRUIT
    # =================================================================

    def _update_multifruit(self, dt):
        for ball in self.balls:
            if not hasattr(ball, '_multifruit_timer'):
                continue

            ball._multifruit_timer -= dt
            if hasattr(ball, '_multifruit_green_timer'):
                ball._multifruit_green_timer -= dt
            green = getattr(ball, '_multifruit_green_timer', 0)

            if green > 0:
                # Первые 3 сек: оригинал зелёный, фейки красные
                ball.color = (255, 0, 0) if ball.is_fake else (0, 255, 0)
            else:
                # Плавный переход к белому за 3 сек
                blend = min(1.0, abs(green) / 3.0)
                v = int(255 * blend)
                if ball.is_fake:
                    ball.color = (255, v, v)
                else:
                    ball.color = (v, 255, v)

            if ball._multifruit_timer <= 0:
                if ball.is_fake:
                    if ball.active:
                        cx, cy = ball.get_center()
                        self.particles.emit(
                            cx, cy, (200, 200, 200),
                            count=10, speed=70, lifetime=0.4
                        )
                    ball.active = False
                else:
                    ball.color = COLOR_WHITE
                for attr in ('_multifruit_timer',
                             '_multifruit_green_timer'):
                    if hasattr(ball, attr):
                        try:
                            delattr(ball, attr)
                        except AttributeError:
                            pass

    # =================================================================
    #  GOALS
    # =================================================================

    def _check_goals(self):
        fx, fy, fw, fh = self.field_rect

        for ball in self.balls[:]:
            if not ball.active:
                continue

            scorer = 0

            # --- За левой стенкой ---
            if ball.rel_x < -0.05:
                if ball.is_fake:
                    ball.active = False
                    continue
                if self.paddles[0].base_shield_wall_active:
                    ball.vel_x = abs(ball.vel_x)
                    ball.rel_x = 0.03
                    self.paddles[0].base_shield_wall_active = False
                    self.paddles[0].base_shield = False
                    self.particles.emit_line(
                        fx + 5, fy, fx + 5, fy + fh,
                        (0, 255, 200), count=25, speed=120
                    )
                    self.shake.start(8, 0.25)
                else:
                    scorer = 2

            # --- За правой стенкой ---
            elif ball.rel_x > 1.05:
                if ball.is_fake:
                    ball.active = False
                    continue
                if self.paddles[1].base_shield_wall_active:
                    ball.vel_x = -abs(ball.vel_x)
                    ball.rel_x = 0.97
                    self.paddles[1].base_shield_wall_active = False
                    self.paddles[1].base_shield = False
                    self.particles.emit_line(
                        fx + fw - 5, fy, fx + fw - 5, fy + fh,
                        (0, 255, 200), count=25, speed=120
                    )
                    self.shake.start(8, 0.25)
                else:
                    scorer = 1

            if scorer:
                self._goal_scored(scorer)
                break

    def _goal_scored(self, scorer):
        self.score[scorer - 1] += 1
        color = self.paddles[scorer - 1].color

        self.goal_flash.start(color, self.field_rect)
        self.shake.start(16, 0.5)
        self.flash.start(color, 0.3, 140)

        if self.score[scorer - 1] >= self.max_score:
            self.winner = scorer
            self.state = STATE_GAME_OVER
            return

        self._goal_freeze = 1.0
        self._reset_round(direction=-1 if scorer == 1 else 1)

    def _reset_round(self, direction=None):
        self.balls = [Ball(self.field_rect)]
        self.balls[0].reset(direction)

        for paddle in self.paddles:
            paddle.reset()

        if self.powerup_manager:
            self.powerup_manager.reset()

        self.round_timer = 0
        self.trail.clear()
        self.particles.clear()
        self._sticky_release_timers.clear()
        self._bomb_flash_active = False
        self._bomb_flash_timer = 0

    # =================================================================
    #  NETWORK SYNC
    # =================================================================

    def _serialize_state(self):
        state = {
            'paddles': [],
            'balls': [b.serialize() for b in self.balls],
            'score': list(self.score),
            'game_state': (
                'game_over' if self.state == STATE_GAME_OVER else 'playing'
            ),
            'winner': self.winner,
            'bomb_flash': self._bomb_flash_active,
        }

        for p in self.paddles:
            state['paddles'].append({
                'ry': round(p.rel_y, 4),
                'rh': round(p.rel_height, 4),
                'frozen': p.frozen,
                'ft': round(p.frozen_timer, 2),
                'stunned': p.stunned,
                'st': round(p.stunned_timer, 2),
                'inv': p.inverted,
                'invt': round(p.inverted_timer, 2),
                'ph': p.phantom,
                'pht': round(p.phantom_timer, 2),
                'tit': p.titan,
                'titt': round(p.titan_timer, 2),
                'mag': p.magnet,
                'magt': round(p.magnet_timer, 2),
                'stk': p.sticky,
                'stkt': round(p.sticky_timer, 2),
                'el': p.electro,
                'elt': round(p.electro_timer, 2),
                'cl': p.clone_active,
                'clt': round(p.clone_timer, 2),
                'ls': p.laser_sight,
                'lst': round(p.laser_timer, 2),
                'sht': p.shield_tower,
                'shtt': round(p.shield_tower_timer, 2),
                'bs': p.base_shield_wall_active,
                'bst': round(p.base_shield_timer, 2),
                'pb': p.pushed_back,
                'po': round(p.push_offset, 4),
            })

        if self.powerup_manager:
            state['powerups'] = self.powerup_manager.serialize()

        return state

    def _apply_network_state(self, state):
        if not state:
            return

        # --- Ракетки ---
        for i, pd in enumerate(state.get('paddles', [])):
            if i >= len(self.paddles):
                break
            p = self.paddles[i]
            p.rel_y = pd.get('ry', p.rel_y)
            p.rel_height = pd.get('rh', p.rel_height)
            p.frozen = pd.get('frozen', False)
            p.frozen_timer = pd.get('ft', 0)
            p.stunned = pd.get('stunned', False)
            p.stunned_timer = pd.get('st', 0)
            p.inverted = pd.get('inv', False)
            p.inverted_timer = pd.get('invt', 0)
            p.phantom = pd.get('ph', False)
            p.phantom_timer = pd.get('pht', 0)
            p.titan = pd.get('tit', False)
            p.titan_timer = pd.get('titt', 0)
            p.magnet = pd.get('mag', False)
            p.magnet_timer = pd.get('magt', 0)
            p.sticky = pd.get('stk', False)
            p.sticky_timer = pd.get('stkt', 0)
            p.electro = pd.get('el', False)
            p.electro_timer = pd.get('elt', 0)
            p.clone_active = pd.get('cl', False)
            p.clone_timer = pd.get('clt', 0)
            p.laser_sight = pd.get('ls', False)
            p.laser_timer = pd.get('lst', 0)
            p.shield_tower = pd.get('sht', False)
            p.shield_tower_timer = pd.get('shtt', 0)
            p.base_shield_wall_active = pd.get('bs', False)
            p.base_shield_timer = pd.get('bst', 0)
            p.pushed_back = pd.get('pb', False)
            p.push_offset = pd.get('po', 0)

        # --- Мячи ---
        ball_data = state.get('balls', [])
        if ball_data:
            while len(self.balls) < len(ball_data):
                self.balls.append(Ball(self.field_rect))
            while len(self.balls) > len(ball_data):
                self.balls.pop()
            for i, bd in enumerate(ball_data):
                self.balls[i].deserialize(bd)

        # --- Счёт ---
        if 'score' in state:
            self.score = list(state['score'])

        # --- Конец игры ---
        if state.get('game_state') == 'game_over':
            self.state = STATE_GAME_OVER
            self.winner = state.get('winner') or 0

        # --- Бомба ---
        if state.get('bomb_flash') and not self._bomb_flash_active:
            self._bomb_flash_active = True
            self._bomb_flash_timer = self._bomb_flash_duration
            self.shake.start(22, 0.8)

    # =================================================================
    #  HELPERS
    # =================================================================

    def _get_main_ball(self):
        for b in self.balls:
            if b.active and not b.is_fake:
                return b
        for b in self.balls:
            if b.active:
                return b
        return self.balls[0] if self.balls else None

    def _get_paddle_effects(self, paddle):
        """Локализованный список активных эффектов ракетки"""
        e = []
        if paddle.frozen:
            e.append((t("pu.frozen"), paddle.frozen_timer,
                      1.5, (150, 220, 255)))
        if paddle.stunned:
            e.append((t("pu.stunned"), paddle.stunned_timer,
                      1.0, (255, 255, 0)))
        if paddle.inverted:
            e.append((t("pu.inverted"), paddle.inverted_timer,
                      5.0, (255, 0, 100)))
        if paddle.phantom:
            e.append((t("pu.phantom"), paddle.phantom_timer,
                      7.0, (140, 140, 140)))
        if paddle.titan:
            e.append((t("pu.titan"), paddle.titan_timer,
                      8.0, (170, 170, 170)))
        if paddle.magnet:
            e.append((t("pu.magnet"), paddle.magnet_timer,
                      8.0, (220, 40, 40)))
        if paddle.sticky:
            e.append((t("pu.sticky"), paddle.sticky_timer,
                      8.0, (220, 220, 0)))
        if paddle.electro:
            e.append((t("pu.electro_shield"), paddle.electro_timer,
                      6.0, (0, 170, 255)))
        if paddle.clone_active:
            e.append((t("pu.clone"), paddle.clone_timer,
                      10.0, (0, 220, 120)))
        if paddle.laser_sight:
            e.append((t("pu.laser_sight"), paddle.laser_timer,
                      12.0, (255, 40, 40)))
        if paddle.shield_tower:
            e.append((t("pu.shield_tower"), paddle.shield_tower_timer,
                      10.0, (0, 220, 220)))
        if paddle.base_shield_wall_active:
            e.append((t("pu.base_shield"), paddle.base_shield_timer,
                      15.0, (0, 255, 200)))
        return e

    # =================================================================
    #  DRAW
    # =================================================================

    def draw(self):
        self.screen.fill((10, 10, 15))

        if settings.bg_effects:
            self.bg_effect.draw(self.screen, self.field_rect)

        ox, oy = self.shake.offset
        fx, fy, fw, fh = self.field_rect
        fx += ox
        fy += oy

        # ===== ПОЛЕ =====
        field_area = pygame.Rect(fx, fy, fw, fh)
        pygame.draw.rect(self.screen, (15, 15, 20), field_area)
        pygame.draw.rect(self.screen, COLOR_GRAY, field_area, 2)

        # Центральная пунктирная линия
        cx = fx + fw // 2
        y = fy
        while y < fy + fh:
            pygame.draw.line(
                self.screen, (42, 42, 48),
                (cx, y), (cx, min(y + 15, fy + fh)), 2
            )
            y += 25

        # Центральный круг
        pygame.draw.circle(
            self.screen, (32, 32, 38),
            (fx + fw // 2, fy + fh // 2), int(fh * 0.1), 2
        )

        # ===== УЛУЧШЕНИЯ =====
        if self.powerup_manager:
            self.powerup_manager.draw(self.screen)

        # ===== ШЛЕЙФ =====
        if self.balls:
            self.trail.draw(self.screen, int(BALL_SIZE_REL * fh))

        # ===== МЯЧИ =====
        for ball in self.balls:
            ball.draw(self.screen)

        # ===== РАКЕТКИ =====
        for paddle in self.paddles:
            paddle.draw(self.screen)

        # ===== ЛАЗЕРНЫЙ ПРИЦЕЛ =====
        if self.powerup_manager:
            for paddle in self.paddles:
                if paddle.laser_sight:
                    self.powerup_manager.draw_laser(
                        self.screen, paddle, self.balls
                    )

        # ===== ЧАСТИЦЫ =====
        self.particles.draw(self.screen)

        # ===== ВСПЫШКИ =====
        self.flash.draw(self.screen)
        self.goal_flash.draw(self.screen)

        if self._bomb_flash_active and self._bomb_flash_timer > 0:
            prog = self._bomb_flash_timer / self._bomb_flash_duration
            alpha = int(255 * prog * 0.9)
            surf = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            surf.fill((255, 255, 210, alpha))
            self.screen.blit(surf, (0, 0))

        # ===== HUD =====
        self._draw_hud(fx, fy, fw, fh)

        # ===== ОВЕРЛЕИ =====
        if self.state == STATE_COUNTDOWN:
            self.countdown.draw(self.screen, self.field_rect)

        if self.state == STATE_PAUSED:
            self._draw_pause_overlay()

        if self.state == STATE_GAME_OVER:
            self._draw_game_over()

        if self.network_paused or self.network_gave_up:
            self._draw_network_overlay()

    # -----------------------------------------------------------------

    def _draw_hud(self, fx, fy, fw, fh):
        """Счёт, имена, индикаторы"""
        # Счёт рисуем над полем
        score_y = max(38, fy - 42)
        name_y = score_y + 32

        # --- Счёт P1 ---
        s1 = render_text(
            str(self.score[0]), 62, self.paddles[0].color,
            weight="bold", accent=True
        )
        self.screen.blit(
            s1, s1.get_rect(center=(fx + fw // 4, score_y))
        )

        # --- Разделитель ---
        sep = render_text(":", 52, (70, 70, 78),
                          weight="bold", accent=True)
        self.screen.blit(
            sep, sep.get_rect(center=(fx + fw // 2, score_y - 3))
        )

        # --- Счёт P2 ---
        s2 = render_text(
            str(self.score[1]), 62, self.paddles[1].color,
            weight="bold", accent=True
        )
        self.screen.blit(
            s2, s2.get_rect(center=(fx + 3 * fw // 4, score_y))
        )

        # --- Имена ---
        n1 = render_text(
            self.p1_name, 20, self.paddles[0].color, weight="medium"
        )
        self.screen.blit(
            n1, n1.get_rect(center=(fx + fw // 4, name_y))
        )
        n2 = render_text(
            self.p2_name, 20, self.paddles[1].color, weight="medium"
        )
        self.screen.blit(
            n2, n2.get_rect(center=(fx + 3 * fw // 4, name_y))
        )

        # --- "До N очков" ---
        goal = render_text(
            t("game.first_to", n=self.max_score), 16,
            (95, 95, 105), weight="regular"
        )
        self.screen.blit(
            goal, goal.get_rect(center=(fx + fw // 2, name_y))
        )

        # --- Индикаторы улучшений ---
        if self.powerup_manager:
            for paddle in self.paddles:
                effects = self._get_paddle_effects(paddle)
                if not effects:
                    continue
                prect = paddle.get_rect()
                for i, (name, remaining, total, color) in \
                        enumerate(effects):
                    iy = prect.y - 32 - i * 30
                    if iy < fy + 12:
                        iy = fy + 12 + i * 30
                    PowerupIndicator.draw(
                        self.screen, prect.centerx, iy,
                        76, remaining, total, color, name
                    )

            # --- Бейдж режима ---
            badge = render_text(
                t("game.powerups_mode"), 15, (120, 110, 40),
                weight="semibold"
            )
            self.screen.blit(badge, (fx + 8, fy + fh + 6))

    # -----------------------------------------------------------------

    def _draw_pause_overlay(self):
        sw, sh = self.screen_w, self.screen_h

        if self.mode != MODE_NETWORK:
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 130))
            self.screen.blit(overlay, (0, 0))

        draw_text_centered(
            self.screen, t("game.paused"), sh // 2 - 70,
            font_size=68, color=COLOR_WHITE, weight="bold", accent=True
        )
        draw_text_centered(
            self.screen, t("game.esc_resume"), sh // 2 + 10,
            font_size=24, color=(170, 170, 180), weight="medium"
        )
        draw_text_centered(
            self.screen, t("game.q_quit"), sh // 2 + 45,
            font_size=24, color=(170, 170, 180), weight="medium"
        )

        if self.mode == MODE_NETWORK:
            draw_text_centered(
                self.screen, t("game.network_continues"),
                sh // 2 + 92, font_size=20,
                color=(255, 200, 100), weight="medium"
            )

    # -----------------------------------------------------------------

    def _draw_game_over(self):
        sw, sh = self.screen_w, self.screen_h

        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        self.screen.blit(overlay, (0, 0))

        if self.winner:
            winner_name = (
                self.p1_name if self.winner == 1 else self.p2_name
            )
            winner_color = self.paddles[self.winner - 1].color

            draw_text_centered(
                self.screen, "[icon:trophy]  " + t("game.winner"),
                sh // 2 - 100, font_size=40,
                color=(255, 210, 60), weight="bold", accent=True
            )
            draw_text_centered(
                self.screen, winner_name, sh // 2 - 40,
                font_size=62, color=winner_color,
                weight="bold", accent=True
            )
            draw_text_centered(
                self.screen,
                f"{self.score[0]}   :   {self.score[1]}",
                sh // 2 + 32, font_size=44,
                color=COLOR_WHITE, weight="semibold", accent=True
            )
            draw_text_centered(
                self.screen, t("game.back_to_menu"), sh // 2 + 100,
                font_size=22, color=(160, 160, 170), weight="medium"
            )
        else:
            draw_text_centered(
                self.screen, t("game.game_over"), sh // 2,
                font_size=60, color=COLOR_WHITE,
                weight="bold", accent=True
            )

    # -----------------------------------------------------------------

    def _draw_network_overlay(self):
        sw, sh = self.screen_w, self.screen_h

        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        if self.network_gave_up:
            # ---- Соединение потеряно окончательно ----
            draw_text_centered(
                self.screen, "[icon:error]  " + t("network.lost"),
                sh // 2 - 85, font_size=48,
                color=(255, 95, 95), weight="bold", accent=True
            )
            draw_text_centered(
                self.screen, self.network_status_text, sh // 2 - 22,
                font_size=28, color=COLOR_WHITE, weight="medium"
            )
            draw_text_centered(
                self.screen,
                f"{self.score[0]}  :  {self.score[1]}",
                sh // 2 + 30, font_size=34,
                color=(150, 150, 160), weight="semibold", accent=True
            )
            draw_text_centered(
                self.screen, t("network.press_any"), sh // 2 + 90,
                font_size=21, color=(130, 130, 140), weight="regular"
            )
        else:
            # ---- Ожидание переподключения ----
            time_left = self._get_reconnect_time_left()

            draw_text_centered(
                self.screen,
                "[icon:warning]  " + t("network.interrupted"),
                sh // 2 - 125, font_size=40,
                color=(255, 200, 100), weight="bold", accent=True
            )
            draw_text_centered(
                self.screen, self.network_status_text, sh // 2 - 62,
                font_size=28, color=COLOR_WHITE, weight="medium"
            )

            seconds = int(time_left) + 1
            if time_left > 10:
                bar_color = (90, 240, 120)
            elif time_left > 5:
                bar_color = (255, 220, 90)
            else:
                bar_color = (255, 90, 90)

            draw_text_centered(
                self.screen,
                t("network.reconnecting", sec=seconds), sh // 2 - 12,
                font_size=26, color=bar_color, weight="semibold"
            )

            # --- Прогресс-бар ---
            try:
                from network import RECONNECT_WINDOW
            except Exception:
                RECONNECT_WINDOW = 15.0

            bar_w, bar_h = 420, 20
            bar_x = (sw - bar_w) // 2
            bar_y = sh // 2 + 28

            pygame.draw.rect(
                self.screen, (38, 38, 44),
                (bar_x, bar_y, bar_w, bar_h), border_radius=10
            )
            prog = max(0.0, min(1.0, time_left / RECONNECT_WINDOW))
            fill_w = int(bar_w * prog)
            if fill_w > 0:
                pygame.draw.rect(
                    self.screen, bar_color,
                    (bar_x, bar_y, fill_w, bar_h), border_radius=10
                )
            pygame.draw.rect(
                self.screen, (220, 220, 230),
                (bar_x, bar_y, bar_w, bar_h), 2, border_radius=10
            )

            # --- Анимированные точки ---
            dots = "." * (int(pygame.time.get_ticks() / 400) % 4)
            draw_text_centered(
                self.screen, t("network.attempting", dots=dots),
                sh // 2 + 68, font_size=20,
                color=(145, 145, 155), weight="regular"
            )

            # --- Кнопка ---
            self.disconnect_btn.update(pygame.mouse.get_pos(), 0.016)
            self.disconnect_btn.draw(self.screen)

            draw_text_centered(
                self.screen, t("network.esc_or_button"), sh // 2 + 172,
                font_size=18, color=(95, 95, 105), weight="regular"
            )

    # =================================================================
    #  RESIZE
    # =================================================================

    def resize(self, new_w, new_h):
        self.screen_w = new_w
        self.screen_h = new_h
        self.field_rect = settings.get_field_rect(new_w, new_h)

        for paddle in self.paddles:
            paddle.update_field(self.field_rect)
        for ball in self.balls:
            ball.update_field(self.field_rect)
        if self.powerup_manager:
            self.powerup_manager.update_field(self.field_rect)

        self.bg_effect.resize(new_w, new_h)
        self._build_disconnect_button()
