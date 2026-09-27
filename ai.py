# ai.py — Логика бота (с контролируемыми промахами)
import math
import random


class Bot:
    """AI: почти всегда отбивает, но иногда специально промахивается"""

    def __init__(self, difficulty="medium"):
        self.difficulty = difficulty
        self.target_y = 0.5
        self.update_timer = 0

        # === Параметры по сложности ===
        self.configs = {
            "easy": {
                "update_interval": 0.10,   # часто обновляет цель
                "reaction_delay": 0.15,    # быстрая реакция
                "error_range": 0.03,       # маленькая ошибка (для реализма)
                "speed_factor": 0.75,      # нормальная скорость
                "dead_zone": 0.03,
                "prediction_bounces": 0,   # не предсказывает отскоки
                "miss_rate": 0.04,         # 1 промах на ~25 подач
                "miss_offset": (0.18, 0.28),  # насколько мимо целится
                "return_to_center": True,
                "center_threshold": 0.55,
            },
            "medium": {
                "update_interval": 0.08,
                "reaction_delay": 0.10,
                "error_range": 0.02,
                "speed_factor": 0.85,
                "dead_zone": 0.02,
                "prediction_bounces": 1,   # 1 отскок
                "miss_rate": 0.02,         # 1 на ~50 подач
                "miss_offset": (0.12, 0.22),
                "return_to_center": True,
                "center_threshold": 0.7,
            },
            "hard": {
                "update_interval": 0.05,
                "reaction_delay": 0.05,
                "error_range": 0.01,
                "speed_factor": 1.0,
                "dead_zone": 0.015,
                "prediction_bounces": 3,   # почти идеальное предсказание
                "miss_rate": 0.01,         # 1 на ~100 подач
                "miss_offset": (0.08, 0.15),
                "return_to_center": False,
                "center_threshold": 1.0,
            },
        }

        self.config = self.configs.get(difficulty, self.configs["medium"])

        # Восприятие мяча с задержкой (реакция)
        self.perceived_ball_y = 0.5
        self.perceived_ball_x = 0.5
        self.perceived_ball_vx = 0
        self.perceived_ball_vy = 0

        # Плавающая ошибка прицела
        self.current_error = 0
        self.target_error = self._new_error()

        # Счётчик промахов
        self._was_ball_coming = False
        self._miss_this_shot = False
        self._miss_offset_value = 0

    def _new_error(self):
        return random.uniform(
            -self.config["error_range"],
            self.config["error_range"]
        )

    def update(self, dt, paddle, balls, powerup_manager=None):
        """Обновить бота, вернуть direction"""

        # === Плавно меняющаяся ошибка (реалистичность) ===
        diff = self.target_error - self.current_error
        self.current_error += diff * 2.0 * dt
        if random.random() < dt * 0.5:
            self.target_error = self._new_error()

        # === Находим мяч ===
        main_ball = self._find_relevant_ball(paddle, balls)
        if main_ball is None:
            self.target_y = 0.5
            return self._move_to_target(paddle)

        # === Восприятие с задержкой реакции ===
        reaction = max(self.config["reaction_delay"], 0.01)
        t = min(dt / reaction, 1.0)
        self.perceived_ball_y += (main_ball.rel_y - self.perceived_ball_y) * t
        self.perceived_ball_x += (main_ball.rel_x - self.perceived_ball_x) * t
        self.perceived_ball_vx += (main_ball.vel_x - self.perceived_ball_vx) * t
        self.perceived_ball_vy += (main_ball.vel_y - self.perceived_ball_vy) * t

        # === Детект новой подачи (мяч только начал лететь к нам) ===
        is_coming = self._is_ball_coming(paddle)
        if is_coming and not self._was_ball_coming:
            # Новая подача → решаем, промахнёмся или нет
            if random.random() < self.config["miss_rate"]:
                self._miss_this_shot = True
                lo, hi = self.config["miss_offset"]
                # Куда промахнуться — вверх или вниз
                self._miss_offset_value = random.uniform(lo, hi)
                if random.random() < 0.5:
                    self._miss_offset_value = -self._miss_offset_value
            else:
                self._miss_this_shot = False
                self._miss_offset_value = 0
        self._was_ball_coming = is_coming

        # === Обновление цели (не каждый кадр) ===
        self.update_timer += dt
        if self.update_timer < self.config["update_interval"]:
            return self._move_to_target(paddle)
        self.update_timer = 0

        # === Расчёт цели ===
        if is_coming:
            # Мяч летит к нам — предсказываем
            predicted = self._predict_y(paddle)

            if self._miss_this_shot:
                # Целимся МИМО
                self.target_y = predicted + self._miss_offset_value
            else:
                # Целимся точно + маленькая плавающая ошибка
                self.target_y = predicted + self.current_error
        else:
            # Мяч летит ОТ нас
            if self.config["return_to_center"]:
                dist = abs(self.perceived_ball_x - paddle.rel_x)
                if dist > self.config["center_threshold"]:
                    # Мяч далеко — плавно к центру
                    self.target_y = 0.5 + self.current_error
                else:
                    # Мяч рядом — следим
                    self.target_y = self.perceived_ball_y + self.current_error
            else:
                # Hard бот всегда следит
                self.target_y = self.perceived_ball_y + self.current_error * 0.5

        # Ограничение
        self.target_y = max(0.05, min(0.95, self.target_y))

        return self._move_to_target(paddle)

    def _find_relevant_ball(self, paddle, balls):
        """Найти мяч для реакции"""
        best = None
        min_dist = float('inf')

        for ball in balls:
            if not ball.active:
                continue

            coming = False
            dist = 0
            if paddle.player_id == 2 and ball.vel_x > 0:
                coming = True
                dist = 1.0 - ball.rel_x
            elif paddle.player_id == 1 and ball.vel_x < 0:
                coming = True
                dist = ball.rel_x

            if coming and dist < min_dist:
                min_dist = dist
                best = ball

        if best is None:
            for ball in balls:
                if ball.active and not ball.is_fake:
                    return ball
            for ball in balls:
                if ball.active:
                    return ball

        return best

    def _is_ball_coming(self, paddle):
        """Мяч летит к нам?"""
        if paddle.player_id == 2:
            return self.perceived_ball_vx > 0.01
        else:
            return self.perceived_ball_vx < -0.01

    def _predict_y(self, paddle):
        """Предсказать Y мяча при достижении ракетки"""
        bx = self.perceived_ball_x
        by = self.perceived_ball_y
        vx = self.perceived_ball_vx
        vy = self.perceived_ball_vy

        if abs(vx) < 0.001:
            return by

        target_x = paddle.rel_x
        t = abs((target_x - bx) / vx)

        pred_y = by + vy * t

        # Предсказание отскоков
        bounces = self.config["prediction_bounces"]
        for _ in range(bounces * 2 + 2):
            if pred_y < 0:
                pred_y = -pred_y
            elif pred_y > 1.0:
                pred_y = 2.0 - pred_y
            else:
                break

        return max(0.05, min(0.95, pred_y))

    def _move_to_target(self, paddle):
        """Двигаться к цели"""
        diff = self.target_y - paddle.rel_y
        dead_zone = self.config["dead_zone"]
        speed_factor = self.config["speed_factor"]

        if abs(diff) < dead_zone:
            return 0

        if diff > 0:
            return speed_factor
        else:
            return -speed_factor

    def should_use_powerup(self, paddle, powerup_type):
        """Решение бота об использовании улучшения"""
        if self.difficulty == "easy":
            return random.random() < 0.3
        elif self.difficulty == "medium":
            return random.random() < 0.6
        else:
            return random.random() < 0.85
