# menu.py — Меню, настройки, выбор цвета, настройка матча
import pygame
import sys
import threading

from settings import (
    settings, COLOR_WHITE, COLOR_BLACK, COLOR_GRAY, COLOR_GREEN,
    COLOR_PALETTE,
    STATE_MAIN_MENU, STATE_SETTINGS, STATE_COLOR_SELECT,
    STATE_MODE_SELECT, STATE_GAME_SETUP, STATE_BOT_DIFFICULTY,
    STATE_NETWORK_MENU, STATE_NETWORK_LOBBY,
    MODE_LOCAL, MODE_BOT, MODE_NETWORK,
)
from ui import (
    Button, Slider, ColorPicker, TextInput, Toggle, DropDown, VStack,
    draw_text_centered, draw_text, render_text,
    FIELD_H, BTN_H, ROW_GAP, LABEL_BLOCK,
)
from effects import BackgroundEffect
from network import ServerDiscovery, GameServer, GameClient
from i18n import t, LANG_EN, LANG_RU


TITLE_Y = 58
PANEL_W = 340
BTN_W = 340


class Menu:

    def __init__(self, screen):
        self.screen = screen
        self.state = STATE_MAIN_MENU
        self.bg_effect = BackgroundEffect(
            screen.get_width(), screen.get_height()
        )

        self._pending_mode = None
        self._pending_difficulty = None

        self.discovery = ServerDiscovery()
        self.server = None
        self.client = None
        self.status_key = ""
        self.status_args = {}
        self.lobby_ready = False
        self._discovery_active = False

        self.waiting_for_host = False
        self._network_start_config = None

        self._rebuild_all()

    # =================================================================
    #  BUILD
    # =================================================================

    def _rebuild_all(self):
        sw, sh = self.screen.get_size()
        self._build_main(sw, sh)
        self._build_settings(sw, sh)
        self._build_colors(sw, sh)
        self._build_mode(sw, sh)
        self._build_bot(sw, sh)
        self._build_setup(sw, sh)
        self._build_network(sw, sh)
        self.bg_effect.resize(sw, sh)

    def _cx(self, w=PANEL_W):
        return (self.screen.get_width() - w) // 2

    # ---- Main ----
    def _build_main(self, sw, sh):
        x = self._cx(BTN_W)
        total = 4 * BTN_H + 3 * 18
        y = max(sh // 2 - 40, sh // 2 - total // 2 + 40)
        st = VStack(x, y, BTN_W)

        self.main_buttons = [
            Button(x, st.row(BTN_H, gap=18), BTN_W, BTN_H,
                   t("main.play"), font_size=27, weight="semibold"),
            Button(x, st.row(BTN_H, gap=18), BTN_W, BTN_H,
                   t("main.settings"), font_size=27, weight="semibold"),
            Button(x, st.row(BTN_H, gap=18), BTN_W, BTN_H,
                   t("main.colors"), font_size=27, weight="semibold"),
            Button(x, st.row(BTN_H, gap=0), BTN_W, BTN_H,
                   t("main.exit"), font_size=27, weight="semibold",
                   color=(196, 62, 62), hover_color=(255, 84, 84),
                   text_color=COLOR_WHITE),
        ]

    # ---- Settings ----
    def _build_settings(self, sw, sh):
        x = self._cx(PANEL_W)

        rows = [
            (FIELD_H, True, ROW_GAP),   # resolution
            (FIELD_H, True, ROW_GAP),   # language
            (Toggle.TRACK_H, True, ROW_GAP),  # fullscreen
            (Toggle.TRACK_H, True, ROW_GAP),  # bg effects
            (FIELD_H, True, ROW_GAP + 8),     # name
            (BTN_H, False, 0),                # back
        ]
        total = VStack.measure(rows)
        top = max(TITLE_Y + 62, (sh - total) // 2 + 24)
        st = VStack(x, top, PANEL_W)

        resolutions = [
            ("1280 x 720", (1280, 720)),
            ("1600 x 900", (1600, 900)),
            ("1920 x 1080", (1920, 1080)),
            ("2560 x 1440", (2560, 1440)),
        ]
        cur_res = 0
        for i, (_, r) in enumerate(resolutions):
            if list(r) == list(settings.resolution):
                cur_res = i

        langs = [
            (t("settings.language_en"), LANG_EN),
            (t("settings.language_ru"), LANG_RU),
        ]
        cur_lang = 0
        for i, (_, l) in enumerate(langs):
            if l == settings.get("language", LANG_EN):
                cur_lang = i

        self.res_dd = DropDown(
            x, st.row(FIELD_H, labeled=True), PANEL_W, FIELD_H,
            resolutions, cur_res, t("settings.resolution")
        )
        self.lang_dd = DropDown(
            x, st.row(FIELD_H, labeled=True), PANEL_W, FIELD_H,
            langs, cur_lang, t("settings.language")
        )
        self.fs_toggle = Toggle(
            x, st.row(Toggle.TRACK_H, labeled=True),
            t("settings.fullscreen"), settings.fullscreen
        )
        self.bg_toggle = Toggle(
            x, st.row(Toggle.TRACK_H, labeled=True),
            t("settings.bg_effects"), settings.bg_effects
        )
        self.name_input = TextInput(
            x, st.row(FIELD_H, labeled=True, gap=ROW_GAP + 8),
            PANEL_W, FIELD_H,
            text=settings.player_name,
            placeholder=t("settings.player_name"),
            label=t("settings.player_name")
        )
        self.settings_back = Button(
            x, st.row(BTN_H, gap=0), PANEL_W, BTN_H,
            t("settings.back"), font_size=25, weight="medium"
        )

    # ---- Colors ----
    def _build_colors(self, sw, sh):
        cell = 44
        cols = 8
        picker_w = cols * (cell + 7) - 7
        x = (sw - picker_w) // 2

        block_h = 0
        tmp = ColorPicker(0, 0, cell, cols, COLOR_PALETTE,
                          settings.p1_color)
        ph = tmp.height
        block_h = (LABEL_BLOCK + ph) * 2 + 46 + BTN_H + 30
        top = max(TITLE_Y + 70, (sh - block_h) // 2 + 20)

        self.p1_picker = ColorPicker(
            x, top + LABEL_BLOCK, cell, cols, COLOR_PALETTE,
            settings.p1_color
        )
        y2 = top + LABEL_BLOCK + ph + 46
        self.p2_picker = ColorPicker(
            x, y2 + LABEL_BLOCK, cell, cols, COLOR_PALETTE,
            settings.p2_color
        )
        by = y2 + LABEL_BLOCK + ph + 40
        self.colors_back = Button(
            self._cx(PANEL_W), min(by, sh - BTN_H - 24),
            PANEL_W, BTN_H, t("settings.back"),
            font_size=25, weight="medium"
        )

    # ---- Mode ----
    def _build_mode(self, sw, sh):
        x = self._cx(BTN_W)
        total = 3 * BTN_H + 2 * 18 + 34 + BTN_H
        top = max(TITLE_Y + 80, (sh - total) // 2)
        st = VStack(x, top, BTN_W)

        self.mode_buttons = [
            Button(x, st.row(BTN_H, gap=18), BTN_W, BTN_H,
                   t("mode.local"), font_size=25, weight="semibold"),
            Button(x, st.row(BTN_H, gap=18), BTN_W, BTN_H,
                   t("mode.bot"), font_size=25, weight="semibold"),
            Button(x, st.row(BTN_H, gap=34), BTN_W, BTN_H,
                   t("mode.network"), font_size=25, weight="semibold"),
            Button(x, st.row(BTN_H, gap=0), BTN_W, BTN_H,
                   t("settings.back"), font_size=25, weight="medium"),
        ]

    # ---- Bot difficulty ----
    def _build_bot(self, sw, sh):
        x = self._cx(BTN_W)
        total = 3 * BTN_H + 2 * 18 + 34 + BTN_H
        top = max(TITLE_Y + 80, (sh - total) // 2)
        st = VStack(x, top, BTN_W)

        self.bot_buttons = [
            Button(x, st.row(BTN_H, gap=18), BTN_W, BTN_H,
                   t("bot.easy"), font_size=25, weight="semibold",
                   color=(96, 224, 112), hover_color=(140, 255, 160)),
            Button(x, st.row(BTN_H, gap=18), BTN_W, BTN_H,
                   t("bot.medium"), font_size=25, weight="semibold",
                   color=(240, 190, 90), hover_color=(255, 220, 140)),
            Button(x, st.row(BTN_H, gap=34), BTN_W, BTN_H,
                   t("bot.hard"), font_size=25, weight="semibold",
                   color=(232, 92, 92), hover_color=(255, 140, 140)),
            Button(x, st.row(BTN_H, gap=0), BTN_W, BTN_H,
                   t("settings.back"), font_size=25, weight="medium"),
        ]

    # ---- Game setup ----
    def _build_setup(self, sw, sh):
        x = self._cx(PANEL_W)

        rows = [
            (FIELD_H, True, ROW_GAP + 6),
            (FIELD_H, True, ROW_GAP + 18),
            (56, False, 16),
            (BTN_H, False, 0),
        ]
        total = VStack.measure(rows)
        top = max(TITLE_Y + 96, (sh - total) // 2 + 20)
        st = VStack(x, top, PANEL_W)

        modes = [
            (t("setup.mode_normal"), "normal"),
            (t("setup.mode_powerups"), "powerups"),
        ]
        cur = 0
        for i, (_, m) in enumerate(modes):
            if m == settings.last_game_mode:
                cur = i

        self.setup_mode_dd = DropDown(
            x, st.row(FIELD_H, labeled=True, gap=ROW_GAP + 6),
            PANEL_W, FIELD_H, modes, cur, t("setup.mode")
        )
        self.setup_score = Slider(
            x, st.row(FIELD_H, labeled=True, gap=ROW_GAP + 18),
            PANEL_W - 46, FIELD_H, 1, 21,
            settings.last_max_score,
            label=t("setup.score"), color=COLOR_GREEN
        )
        self.setup_start = Button(
            x, st.row(56, gap=16), PANEL_W, 56,
            t("setup.start"), font_size=30, weight="bold",
            color=COLOR_GREEN, hover_color=(110, 255, 160),
            text_color=COLOR_BLACK
        )
        self.setup_back = Button(
            x, st.row(BTN_H, gap=0), PANEL_W, BTN_H,
            t("settings.back"), font_size=25, weight="medium"
        )
        self._setup_header_y = top - 34

    # ---- Network ----
    def _build_network(self, sw, sh):
        x = self._cx(BTN_W)
        top = max(TITLE_Y + 74, sh // 2 - 230)
        st = VStack(x, top, BTN_W)

        self.net_create = Button(
            x, st.row(BTN_H, gap=16), BTN_W, BTN_H,
            t("network.create"), font_size=25, weight="semibold"
        )
        self.net_find = Button(
            x, st.row(BTN_H, gap=30), BTN_W, BTN_H,
            t("network.find"), font_size=25, weight="semibold"
        )

        ip_y = st.row(FIELD_H, labeled=True, gap=26)
        self.ip_input = TextInput(
            x, ip_y, BTN_W - 112, FIELD_H,
            placeholder=t("network.ip_placeholder"),
            label=t("network.ip_label")
        )
        self.ip_join = Button(
            x + BTN_W - 102, ip_y, 102, FIELD_H,
            t("network.join"), font_size=22, weight="medium"
        )

        self.net_back = Button(
            x, st.row(BTN_H, gap=24), BTN_W, BTN_H,
            t("settings.back"), font_size=25, weight="medium"
        )
        self._servers_top = st.bottom + 6

        # Lobby
        self.lobby_start = Button(
            x, sh // 2 + 40, BTN_W, BTN_H,
            t("network.start_game"), font_size=25, weight="semibold",
            color=COLOR_GREEN, text_color=COLOR_BLACK
        )
        self.lobby_back = Button(
            x, sh // 2 + 40 + BTN_H + 16, BTN_W, BTN_H,
            t("network.cancel"), font_size=25, weight="medium"
        )

    def _server_rect(self, idx):
        sw = self.screen.get_width()
        return pygame.Rect(
            (sw - BTN_W) // 2, self._servers_top + 26 + idx * 44,
            BTN_W, 40
        )

    # =================================================================
    #  EVENTS
    # =================================================================

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go_back()
            return None

        h = {
            STATE_MAIN_MENU: self._ev_main,
            STATE_SETTINGS: self._ev_settings,
            STATE_COLOR_SELECT: self._ev_colors,
            STATE_MODE_SELECT: self._ev_mode,
            STATE_BOT_DIFFICULTY: self._ev_bot,
            STATE_GAME_SETUP: self._ev_setup,
            STATE_NETWORK_MENU: self._ev_network,
            STATE_NETWORK_LOBBY: self._ev_lobby,
        }.get(self.state)
        return h(event) if h else None

    def _go_back(self):
        if self.state == STATE_GAME_SETUP:
            if self._pending_mode == MODE_BOT:
                self.state = STATE_BOT_DIFFICULTY
            elif self._pending_mode == MODE_NETWORK:
                self.state = STATE_NETWORK_LOBBY
            else:
                self.state = STATE_MODE_SELECT
        elif self.state == STATE_NETWORK_LOBBY:
            self._leave_lobby()
            self.state = STATE_NETWORK_MENU
        elif self.state == STATE_NETWORK_MENU:
            self._stop_discovery()
            self.state = STATE_MODE_SELECT
        elif self.state == STATE_BOT_DIFFICULTY:
            self.state = STATE_MODE_SELECT
        elif self.state != STATE_MAIN_MENU:
            self.state = STATE_MAIN_MENU

    def _ev_main(self, e):
        for i, b in enumerate(self.main_buttons):
            if b.handle_event(e):
                sw, sh = self.screen.get_size()
                if i == 0:
                    self._build_mode(sw, sh)
                    self.state = STATE_MODE_SELECT
                elif i == 1:
                    self._build_settings(sw, sh)
                    self.state = STATE_SETTINGS
                elif i == 2:
                    self._build_colors(sw, sh)
                    self.state = STATE_COLOR_SELECT
                elif i == 3:
                    self.cleanup()
                    pygame.quit()
                    sys.exit()
        return None

    def _ev_settings(self, e):
        if self.res_dd.open:
            self.res_dd.handle_event(e)
            return None
        if self.lang_dd.open:
            self.lang_dd.handle_event(e)
            return None

        self.res_dd.handle_event(e)
        self.lang_dd.handle_event(e)
        self.fs_toggle.handle_event(e)
        self.bg_toggle.handle_event(e)
        self.name_input.handle_event(e)

        if self.settings_back.handle_event(e):
            old_res = settings.resolution
            old_fs = settings.fullscreen
            old_lang = settings.get("language", LANG_EN)

            if self.res_dd.value:
                settings.resolution = self.res_dd.value
            settings.fullscreen = self.fs_toggle.state
            settings.data["bg_effects"] = self.bg_toggle.state
            settings.player_name = self.name_input.text.strip() or "Player"
            new_lang = self.lang_dd.value or LANG_EN
            settings.set("language", new_lang)
            settings.save()

            self.state = STATE_MAIN_MENU

            if new_lang != old_lang:
                self._rebuild_all()
            if (settings.resolution != old_res or
                    settings.fullscreen != old_fs):
                return "apply_settings"
        return None

    def _ev_colors(self, e):
        self.p1_picker.handle_event(e)
        self.p2_picker.handle_event(e)
        if self.colors_back.handle_event(e):
            settings.p1_color = self.p1_picker.selected_color
            settings.p2_color = self.p2_picker.selected_color
            settings.save()
            self.state = STATE_MAIN_MENU
        return None

    def _ev_mode(self, e):
        for i, b in enumerate(self.mode_buttons):
            if b.handle_event(e):
                sw, sh = self.screen.get_size()
                if i == 0:
                    self._pending_mode = MODE_LOCAL
                    self._pending_difficulty = None
                    self._build_setup(sw, sh)
                    self.state = STATE_GAME_SETUP
                elif i == 1:
                    self._build_bot(sw, sh)
                    self.state = STATE_BOT_DIFFICULTY
                elif i == 2:
                    self._build_network(sw, sh)
                    self.state = STATE_NETWORK_MENU
                elif i == 3:
                    self.state = STATE_MAIN_MENU
        return None

    def _ev_bot(self, e):
        diffs = ["easy", "medium", "hard"]
        for i, b in enumerate(self.bot_buttons):
            if b.handle_event(e):
                if i < 3:
                    self._pending_mode = MODE_BOT
                    self._pending_difficulty = diffs[i]
                    sw, sh = self.screen.get_size()
                    self._build_setup(sw, sh)
                    self.state = STATE_GAME_SETUP
                else:
                    self.state = STATE_MODE_SELECT
        return None

    def _ev_setup(self, e):
        if self.setup_mode_dd.open:
            self.setup_mode_dd.handle_event(e)
            return None

        self.setup_mode_dd.handle_event(e)
        self.setup_score.handle_event(e)

        if self.setup_start.handle_event(e):
            gm = self.setup_mode_dd.value or "normal"
            ms = int(self.setup_score.value)
            settings.last_game_mode = gm
            settings.last_max_score = ms
            if self._pending_difficulty:
                settings.last_bot_difficulty = self._pending_difficulty
            settings.save()

            res = {
                "action": "start_game",
                "mode": self._pending_mode,
                "game_mode": gm,
                "max_score": ms,
            }
            if self._pending_mode == MODE_BOT:
                res["difficulty"] = self._pending_difficulty

            # Если это сетевой матч и мы ХОСТ — рассылаем настройки клиенту
            if (self._pending_mode == MODE_NETWORK and
                    self.server is not None):
                config = {
                    "game_mode": gm,
                    "max_score": ms,
                }
                self.server.send_start_config(config)
                # Передаём конфиг в main.py через результат
                res["network_config"] = config
                res["is_host"] = True

            return res

        if self.setup_back.handle_event(e):
            self._go_back()
        return None

    def _ev_network(self, e):
        if self.net_create.handle_event(e):
            self._create_server()
            return None
        if self.net_find.handle_event(e):
            if not self._discovery_active:
                self.discovery.start_listening()
                self._discovery_active = True
            self.status_key = "network.searching"
            self.status_args = {}
            return None
        if self.net_back.handle_event(e):
            self._stop_discovery()
            self.state = STATE_MODE_SELECT
            return None

        self.ip_input.handle_event(e)
        if self.ip_join.handle_event(e):
            ip = self.ip_input.text.strip()
            if ip:
                self._connect(ip)
            return None

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for idx, ip in enumerate(self.discovery.get_servers().keys()):
                if self._server_rect(idx).collidepoint(e.pos):
                    self._connect(ip)
                    break
        return None

    def _ev_lobby(self, e):
        if self.lobby_back.handle_event(e):
            self._leave_lobby()
            self.state = STATE_NETWORK_MENU
            return None

        # Только ХОСТ может запускать настройку матча
        is_host = self.server is not None
        if is_host and self.lobby_ready and self.lobby_start.handle_event(e):
            self._pending_mode = MODE_NETWORK
            sw, sh = self.screen.get_size()
            self._build_setup(sw, sh)
            self.state = STATE_GAME_SETUP
        return None

    # =================================================================
    #  NETWORK
    # =================================================================

    def _create_server(self):
        self._stop_discovery()
        self.server = GameServer(settings.player_name, settings.p1_color)
        self.server.on_client_connect = self._on_client_join
        self.server.on_client_disconnect = self._on_client_leave
        self.server.on_client_ready = self._on_client_ready
        self.server.start()
        self.status_key = "network.waiting"
        self.status_args = {}
        self.lobby_ready = False
        self.state = STATE_NETWORK_LOBBY

    def _on_client_ready(self):
        """Клиент подтвердил получение настроек"""
        pass  # Можно добавить индикацию, если нужно

    def _connect(self, ip):
        self._stop_discovery()
        self.client = GameClient(settings.player_name, settings.p2_color)
        self.status_key = "network.connecting"
        self.status_args = {"ip": ip}
        self.lobby_ready = False

        def worker():
            if self.client and self.client.connect_to(ip):
                self.status_key = "network.connected"
                self.status_args = {"name": self.client.host_name}
                self.lobby_ready = True
                # Клиент: ждём сигнала game_start от хоста
                self.client.on_start_callback = self._on_network_start
                self.client.send_ready()
            else:
                self.status_key = "network.failed"
                self.status_args = {}

        self.state = STATE_NETWORK_LOBBY

        threading.Thread(target=worker, daemon=True).start()

    def _on_network_start(self, config):
        """Клиент получил настройки от хоста — стартуем игру"""
        self._network_start_config = config
        # main.py подхватит это через update()

    def _leave_lobby(self):
        if self.server:
            self.server.stop()
            self.server = None
        if self.client:
            self.client.disconnect()
            self.client = None
        self.lobby_ready = False
        self.status_key = ""
        self.status_args = {}

    def _stop_discovery(self):
        if self._discovery_active:
            self.discovery.stop()
            self._discovery_active = False

    def _on_client_join(self, name, color):
        self.status_key = "network.joined"
        self.status_args = {"name": name}
        self.lobby_ready = True

    def _on_client_leave(self):
        self.status_key = "network.player_disconnected"
        self.status_args = {}
        self.lobby_ready = False

    # =================================================================
    #  UPDATE
    # =================================================================

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        if settings.bg_effects:
            self.bg_effect.update(dt)

        s = self.state
        if s == STATE_MAIN_MENU:
            for b in self.main_buttons:
                b.update(mp, dt)
        elif s == STATE_SETTINGS:
            self.fs_toggle.update(dt)
            self.bg_toggle.update(dt)
            self.name_input.update(dt)
            self.settings_back.update(mp, dt)
        elif s == STATE_COLOR_SELECT:
            self.colors_back.update(mp, dt)
        elif s == STATE_MODE_SELECT:
            for b in self.mode_buttons:
                b.update(mp, dt)
        elif s == STATE_BOT_DIFFICULTY:
            for b in self.bot_buttons:
                b.update(mp, dt)
        elif s == STATE_GAME_SETUP:
            self.setup_start.update(mp, dt)
            self.setup_back.update(mp, dt)
        elif s == STATE_NETWORK_MENU:
            self.net_create.update(mp, dt)
            self.net_find.update(mp, dt)
            self.net_back.update(mp, dt)
            self.ip_join.update(mp, dt)
            self.ip_input.update(dt)
        elif s == STATE_NETWORK_LOBBY:
            self.lobby_back.update(mp, dt)
            if self.lobby_ready:
                self.lobby_start.update(mp, dt)

    def poll_network_start(self):
        """Вызывается из main.py. Возвращает dict или None."""
        if self._network_start_config is None:
            return None
        cfg = self._network_start_config
        self._network_start_config = None
        return {
            "action": "start_game",
            "mode": MODE_NETWORK,
            "game_mode": cfg.get("game_mode", "normal"),
            "max_score": cfg.get("max_score", 7),
            "network_config": cfg,
            "is_client": True,
        }

    # =================================================================
    #  DRAW
    # =================================================================

    def draw(self):
        self.screen.fill((10, 10, 15))
        if settings.bg_effects:
            self.bg_effect.draw(self.screen)

        sw, sh = self.screen.get_size()
        {
            STATE_MAIN_MENU: self._dr_main,
            STATE_SETTINGS: self._dr_settings,
            STATE_COLOR_SELECT: self._dr_colors,
            STATE_MODE_SELECT: self._dr_mode,
            STATE_BOT_DIFFICULTY: self._dr_bot,
            STATE_GAME_SETUP: self._dr_setup,
            STATE_NETWORK_MENU: self._dr_network,
            STATE_NETWORK_LOBBY: self._dr_lobby,
        }.get(self.state, lambda a, b: None)(sw, sh)

    def _title(self, key, sw, y=TITLE_Y):
        draw_text_centered(self.screen, t(key), y, font_size=42,
                           color=COLOR_WHITE, weight="bold", accent=True)

    def _dr_main(self, sw, sh):
        ty = max(96, sh // 4)
        glow = render_text(t("main.title"), 78, COLOR_GREEN,
                           "bold", accent=True)
        title = render_text(t("main.title"), 78, COLOR_WHITE,
                            "bold", accent=True)
        self.screen.blit(glow, glow.get_rect(center=(sw // 2 + 2, ty + 2)))
        self.screen.blit(title, title.get_rect(center=(sw // 2, ty)))

        sub = render_text(t("main.subtitle"), 20, (140, 140, 152),
                          "regular")
        self.screen.blit(sub, sub.get_rect(center=(sw // 2, ty + 52)))

        for b in self.main_buttons:
            b.draw(self.screen)

        v = render_text(t("main.version"), 17, (62, 62, 70))
        self.screen.blit(v, (sw - v.get_width() - 20, sh - 30))

    def _dr_settings(self, sw, sh):
        self._title("settings.title", sw)
        self.res_dd.draw(self.screen)
        self.lang_dd.draw(self.screen)
        self.fs_toggle.draw(self.screen)
        self.bg_toggle.draw(self.screen)
        self.name_input.draw(self.screen)
        self.settings_back.draw(self.screen)
        # overlays — строго последними
        self.res_dd.draw_overlay(self.screen)
        self.lang_dd.draw_overlay(self.screen)

    def _dr_colors(self, sw, sh):
        self._title("colors.title", sw)

        l1 = render_text(t("colors.player1"), 22,
                         self.p1_picker.selected_color, "semibold")
        self.screen.blit(
            l1, (self.p1_picker.x,
                 self.p1_picker.y - l1.get_height() - 9)
        )
        pygame.draw.rect(
            self.screen, self.p1_picker.selected_color,
            pygame.Rect(self.p1_picker.x + self.p1_picker.width + 26,
                        self.p1_picker.y + 6, 18, self.p1_picker.height - 12),
            border_radius=4
        )
        self.p1_picker.draw(self.screen)

        l2 = render_text(t("colors.player2"), 22,
                         self.p2_picker.selected_color, "semibold")
        self.screen.blit(
            l2, (self.p2_picker.x,
                 self.p2_picker.y - l2.get_height() - 9)
        )
        pygame.draw.rect(
            self.screen, self.p2_picker.selected_color,
            pygame.Rect(self.p2_picker.x + self.p2_picker.width + 26,
                        self.p2_picker.y + 6, 18, self.p2_picker.height - 12),
            border_radius=4
        )
        self.p2_picker.draw(self.screen)
        self.colors_back.draw(self.screen)

    def _dr_mode(self, sw, sh):
        self._title("mode.title", sw, 72)
        for b in self.mode_buttons:
            b.draw(self.screen)

    def _dr_bot(self, sw, sh):
        self._title("bot.title", sw, 72)
        for b in self.bot_buttons:
            b.draw(self.screen)

    def _dr_setup(self, sw, sh):
        self._title("setup.title", sw, 72)

        if self._pending_mode == MODE_LOCAL:
            txt = t("setup.vs_local")
        elif self._pending_mode == MODE_BOT:
            d = self._pending_difficulty or "medium"
            txt = t("setup.vs_bot", diff=t(f"bot.{d}_full"))
        elif self._pending_mode == MODE_NETWORK:
            if self.server:
                opp = self.server.client_name or "Player"
            elif self.client:
                opp = self.client.host_name or "Host"
            else:
                opp = "?"
            txt = t("setup.vs_network", name=opp)
        else:
            txt = ""

        s = render_text(txt, 23, COLOR_GREEN, "semibold")
        self.screen.blit(
            s, s.get_rect(center=(sw // 2, self._setup_header_y))
        )

        self.setup_mode_dd.draw(self.screen)
        self.setup_score.draw(self.screen)
        self.setup_start.draw(self.screen)
        self.setup_back.draw(self.screen)
        self.setup_mode_dd.draw_overlay(self.screen)

    def _dr_network(self, sw, sh):
        self._title("network.title", sw, 64)

        self.net_create.draw(self.screen)
        self.net_find.draw(self.screen)
        self.ip_input.draw(self.screen)
        self.ip_join.draw(self.screen)
        self.net_back.draw(self.screen)

        servers = self.discovery.get_servers()
        if servers:
            hdr = render_text(t("network.found_servers"), 20,
                              (130, 130, 142), "medium")
            self.screen.blit(
                hdr, hdr.get_rect(center=(sw // 2, self._servers_top + 6))
            )
            mp = pygame.mouse.get_pos()
            for idx, (ip, info) in enumerate(servers.items()):
                if idx >= 4:
                    break
                r = self._server_rect(idx)
                if r.bottom > sh - 10:
                    break
                hov = r.collidepoint(mp)
                pygame.draw.rect(
                    self.screen, (62, 62, 82) if hov else (38, 38, 46),
                    r, border_radius=7
                )
                pygame.draw.rect(
                    self.screen,
                    COLOR_GREEN if hov else (85, 85, 95),
                    r, 2, border_radius=7
                )
                draw_text(self.screen, info['name'], r.x + 14, r.centery,
                          font_size=21, color=COLOR_WHITE,
                          anchor="midleft", weight="semibold")
                draw_text(self.screen, ip, r.right - 14, r.centery,
                          font_size=18, color=(140, 140, 152),
                          anchor="midright", weight="regular")
        elif self._discovery_active:
            s = render_text(t("network.searching"), 21,
                            (130, 130, 142), "regular")
            self.screen.blit(
                s, s.get_rect(center=(sw // 2, self._servers_top + 20))
            )

    def _dr_lobby(self, sw, sh):
        self._title("network.lobby", sw, 72)

        status = t(self.status_key, **self.status_args) \
            if self.status_key else ""
        draw_text_centered(self.screen, status, sh // 2 - 50,
                           font_size=27, color=COLOR_GREEN,
                           weight="medium")

        if self.lobby_ready:
            draw_text_centered(
                self.screen, "[icon:check]  " +
                t("network.player_connected"),
                sh // 2 - 6, font_size=21, color=(120, 230, 150),
                weight="medium"
            )

        # Хост видит кнопку "Начать игру", клиент — "Ожидаем хоста..."
        is_host = self.server is not None
        if is_host and self.lobby_ready:
            self.lobby_start.draw(self.screen)
        elif not is_host and self.lobby_ready:
            draw_text_centered(
                self.screen, t("network.waiting_for_host"),
                sh // 2 + 56, font_size=24,
                color=(255, 200, 100), weight="medium"
            )
        self.lobby_back.draw(self.screen)

    # =================================================================

    def resize(self, w, h):
        self.bg_effect.resize(w, h)
        self._rebuild_all()

    def cleanup(self):
        self._stop_discovery()
        if self.server:
            self.server.stop()
            self.server = None
        if self.client:
            self.client.disconnect()
            self.client = None
