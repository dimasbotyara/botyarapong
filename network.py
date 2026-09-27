# network.py — Socket.IO клиент/сервер с переподключением
import threading
import time
import json
import socket
import socketio


# === Параметры сети ===
BROADCAST_PORT = 5556
GAME_PORT = 5555
DISCOVERY_INTERVAL = 1.0

# Таймауты
PING_INTERVAL = 3.0           # Пинг каждые 3 сек
PING_TIMEOUT = 5.0            # Если нет пинга 5 сек — считаем разрыв
RECONNECT_WINDOW = 15.0       # Окно переподключения (сек)
RECONNECT_ATTEMPT_INTERVAL = 2.0  # Клиент пробует каждые 2 сек


class ServerDiscovery:
    """UDP-обнаружение серверов в локальной сети"""

    def __init__(self):
        self.servers = {}
        self.running = False
        self._thread = None

    def start_listening(self):
        self.running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _listen_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('', BROADCAST_PORT))
        except OSError:
            return
        sock.settimeout(0.5)

        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                msg = data.decode('utf-8', errors='ignore')
                if msg.startswith("PONG_SERVER:"):
                    parts = msg.split(":", 2)
                    if len(parts) >= 2:
                        name = parts[1]
                        session_id = parts[2] if len(parts) > 2 else ""
                        self.servers[addr[0]] = {
                            "name": name,
                            "session_id": session_id,
                            "time": time.time()
                        }
            except socket.timeout:
                pass
            except Exception:
                pass

            now = time.time()
            self.servers = {
                ip: info for ip, info in self.servers.items()
                if now - info["time"] < 5.0
            }

        try:
            sock.close()
        except Exception:
            pass

    def get_servers(self):
        return dict(self.servers)


class ServerBroadcaster:
    """Броадкаст наличия сервера"""

    def __init__(self, server_name, session_id=""):
        self.server_name = server_name
        self.session_id = session_id
        self.running = False
        self._thread = None

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _broadcast_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while self.running:
            try:
                msg = f"PONG_SERVER:{self.server_name}:{self.session_id}".encode('utf-8')
                sock.sendto(msg, ('<broadcast>', BROADCAST_PORT))
            except Exception:
                pass
            time.sleep(DISCOVERY_INTERVAL)

        try:
            sock.close()
        except Exception:
            pass


# === Game Server ===
class GameServer:
    """Socket.IO сервер с поддержкой переподключения"""

    def __init__(self, player_name, player_color):
        self.sio = socketio.Server(
            cors_allowed_origins='*',
            async_mode='threading',
            ping_interval=PING_INTERVAL,
            ping_timeout=PING_TIMEOUT,
        )
        self.app = socketio.WSGIApp(self.sio)
        self.player_name = player_name
        self.player_color = player_color

        # Клиент
        self.client_sid = None
        self.client_name = ""
        self.client_color = [255, 70, 70]
        self.client_input = {"up": False, "down": False}

        # Статус соединения
        self.connected = False
        self.last_ping_time = 0

        # Переподключение
        self.disconnected_since = 0  # timestamp
        self.reconnect_deadline = 0  # когда сдаваться
        self.waiting_reconnect = False
        self.gave_up = False  # клиент не вернулся

        # Сессия (для переподключения)
        import uuid
        self.session_id = str(uuid.uuid4())[:8]

        # Callbacks
        self.on_client_connect = None
        self.on_client_disconnect = None
        self.on_client_reconnect = None
        self.on_gave_up = None  # клиент не вернулся за окно
        self.on_client_ready = None

        self.running = False
        self._thread = None
        self._monitor_thread = None
        self.broadcaster = ServerBroadcaster(player_name, self.session_id)

        self._setup_events()

    def _setup_events(self):
        @self.sio.event
        def connect(sid, environ):
            pass

        @self.sio.event
        def disconnect(sid):
            if sid == self.client_sid:
                self._on_disconnect()

        @self.sio.on('client_ready')
        def on_client_ready(sid, data):
            """Клиент получил настройки и готов играть"""
            if sid == self.client_sid and self.on_client_ready:
                self.on_client_ready()

        @self.sio.on('join')
        def on_join(sid, data):
            requested_session = data.get('session_id', '')

            # Проверяем — это переподключение или новый клиент
            if (requested_session == self.session_id and
                    self.waiting_reconnect and
                    self.client_name == data.get('name', '')):
                # ПЕРЕПОДКЛЮЧЕНИЕ
                self.client_sid = sid
                self.connected = True
                self.waiting_reconnect = False
                self.disconnected_since = 0
                self.last_ping_time = time.time()
                self.sio.emit('joined', {
                    'host_name': self.player_name,
                    'host_color': list(self.player_color),
                    'session_id': self.session_id,
                    'reconnected': True,
                }, to=sid)
                if self.on_client_reconnect:
                    self.on_client_reconnect()
            elif self.client_sid is None:
                # НОВЫЙ КЛИЕНТ
                self.client_sid = sid
                self.client_name = data.get('name', 'Player 2')
                self.client_color = data.get('color', [255, 70, 70])
                self.connected = True
                self.last_ping_time = time.time()
                self.sio.emit('joined', {
                    'host_name': self.player_name,
                    'host_color': list(self.player_color),
                    'session_id': self.session_id,
                    'reconnected': False,
                }, to=sid)
                if self.on_client_connect:
                    self.on_client_connect(self.client_name, self.client_color)
            else:
                # УЖЕ ЕСТЬ АКТИВНЫЙ КЛИЕНТ — отклоняем
                self.sio.emit('rejected', {
                    'reason': 'Server is busy'
                }, to=sid)
                try:
                    self.sio.disconnect(sid)
                except Exception:
                    pass

        @self.sio.on('input')
        def on_input(sid, data):
            if sid == self.client_sid and self.connected:
                self.client_input = data
                self.last_ping_time = time.time()

        @self.sio.on('client_ping')
        def on_ping(sid, data):
            if sid == self.client_sid:
                self.last_ping_time = time.time()
                try:
                    self.sio.emit('server_pong', {'t': time.time()}, to=sid)
                except Exception:
                    pass

        @self.sio.on('client_disconnect')
        def on_manual_disconnect(sid, data):
            """Клиент решил сам отключиться"""
            if sid == self.client_sid:
                self._on_disconnect()
                self.gave_up = True
                if self.on_gave_up:
                    self.on_gave_up()

    def _on_disconnect(self):
        """Обработка разрыва"""
        if not self.connected:
            return
        self.connected = False
        self.client_sid = None
        self.disconnected_since = time.time()
        self.reconnect_deadline = self.disconnected_since + RECONNECT_WINDOW
        self.waiting_reconnect = True
        if self.on_client_disconnect:
            self.on_client_disconnect()

    def start(self, port=GAME_PORT):
        self.running = True
        self.broadcaster.start()

        def run_server():
            try:
                from werkzeug.serving import make_server
                self._server = make_server(
                    '0.0.0.0', port, self.app, threaded=True
                )
                self._server.serve_forever()
            except Exception as e:
                print(f"Server error: {e}")

        self._thread = threading.Thread(target=run_server, daemon=True)
        self._thread.start()

        # Мониторинг соединения
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True
        )
        self._monitor_thread.start()

    def _monitor_loop(self):
        """Проверка живости соединения"""
        while self.running:
            time.sleep(1.0)
            now = time.time()

            # Проверка таймаута пинга
            if self.connected and self.last_ping_time > 0:
                if now - self.last_ping_time > PING_TIMEOUT:
                    self._on_disconnect()

            # Проверка окна переподключения
            if self.waiting_reconnect and now > self.reconnect_deadline:
                self.waiting_reconnect = False
                self.gave_up = True
                if self.on_gave_up:
                    self.on_gave_up()

    def send_state(self, state):
        """Отправить игровое состояние клиенту"""
        if self.client_sid and self.connected:
            try:
                self.sio.emit('game_state', state, to=self.client_sid)
            except Exception:
                pass

    def get_reconnect_status(self):
        """Возвращает (waiting: bool, time_left: float, gave_up: bool)"""
        if self.gave_up:
            return (False, 0, True)
        if self.waiting_reconnect:
            time_left = max(0, self.reconnect_deadline - time.time())
            return (True, time_left, False)
        return (False, 0, False)

    def force_disconnect(self):
        """Форсированное отключение (по кнопке)"""
        self.waiting_reconnect = False
        self.gave_up = True
        self.connected = False
        self.client_sid = None

    def stop(self):
        self.running = False
        self.broadcaster.stop()
        try:
            if hasattr(self, '_server'):
                self._server.shutdown()
        except Exception:
            pass

    def get_client_input(self):
        if not self.connected:
            return {"up": False, "down": False}
        return dict(self.client_input)


# === Game Client ===
class GameClient:
    """Socket.IO клиент с переподключением"""

    def __init__(self, player_name, player_color):
        self.sio = socketio.Client(
            reconnection=False,  # Свой механизм
            request_timeout=5,
        )
        self.player_name = player_name
        self.player_color = player_color

        self.connected = False
        self.host_name = ""
        self.host_color = [0, 150, 255]
        self.game_state = None
        self.session_id = ""
        self.server_ip = ""
        self.server_port = GAME_PORT

        # Переподключение
        self.disconnected_since = 0
        self.reconnect_deadline = 0
        self.waiting_reconnect = False
        self.gave_up = False
        self.last_pong_time = 0
        self._reconnect_thread = None
        self._ping_thread = None
        self._reconnecting = False

        # Callbacks
        self.on_connect_callback = None
        self.on_state_callback = None
        self.on_disconnect_callback = None
        self.on_reconnect_callback = None
        self.on_gave_up_callback = None
        self.on_rejected_callback = None
        self.on_client_ready = None
        self.start_config = None
        self.on_start_callback = None

        self._setup_events()

    def send_ready(self):
        if self.connected:
            try:
                self.sio.emit('client_ready', {})
            except Exception:
                pass

    def send_start_config(self, config):
        """Отправить клиенту параметры матча и сигнал старта"""
        if self.client_sid and self.connected:
            try:
                self.sio.emit('game_start', config, to=self.client_sid)
            except Exception:
                pass

    def _setup_events(self):
        @self.sio.event
        def connect():
            self.sio.emit('join', {
                'name': self.player_name,
                'color': list(self.player_color),
                'session_id': self.session_id,
            })

        @self.sio.event
        def disconnect():
            self._on_disconnect()

        @self.sio.on('game_start')
        def on_game_start(data):
            self.start_config = data
            self.waiting_reconnect = False
            if self.on_start_callback:
                self.on_start_callback(data)

        @self.sio.on('joined')
        def on_joined(data):
            self.host_name = data.get('host_name', 'Host')
            self.host_color = data.get('host_color', [0, 150, 255])
            self.session_id = data.get('session_id', '')
            self.connected = True
            self.waiting_reconnect = False
            self.disconnected_since = 0
            self.last_pong_time = time.time()

            if data.get('reconnected'):
                if self.on_reconnect_callback:
                    self.on_reconnect_callback()
            else:
                if self.on_connect_callback:
                    self.on_connect_callback()

        @self.sio.on('game_state')
        def on_state(data):
            self.game_state = data
            self.last_pong_time = time.time()
            if self.on_state_callback:
                self.on_state_callback(data)

        @self.sio.on('server_pong')
        def on_pong(data):
            self.last_pong_time = time.time()

        @self.sio.on('rejected')
        def on_rejected(data):
            reason = data.get('reason', 'Rejected')
            self.gave_up = True
            self.connected = False
            if self.on_rejected_callback:
                self.on_rejected_callback(reason)

    def _on_disconnect(self):
        """Обработка разрыва"""
        if not self.connected and not self._reconnecting:
            return
        was_connected = self.connected
        self.connected = False
        if was_connected:
            self.disconnected_since = time.time()
            self.reconnect_deadline = self.disconnected_since + RECONNECT_WINDOW
            self.waiting_reconnect = True

            if self.on_disconnect_callback:
                self.on_disconnect_callback()

            # Стартуем переподключение
            self._start_reconnect_loop()

    def _start_reconnect_loop(self):
        """Автоматические попытки переподключения"""
        if self._reconnect_thread and self._reconnect_thread.is_alive():
            return

        def reconnect_loop():
            self._reconnecting = True
            while (self.waiting_reconnect and
                   time.time() < self.reconnect_deadline and
                   not self.gave_up):
                try:
                    if self.sio.connected:
                        try:
                            self.sio.disconnect()
                        except Exception:
                            pass
                        time.sleep(0.3)

                    self.sio.connect(
                        f'http://{self.server_ip}:{self.server_port}',
                        wait_timeout=3,
                    )
                    # Успех — коннект → connect() эвент сработает
                    time.sleep(1.0)
                    if self.connected:
                        break
                except Exception:
                    pass
                time.sleep(RECONNECT_ATTEMPT_INTERVAL)

            self._reconnecting = False

            # Если не переподключились
            if not self.connected and self.waiting_reconnect:
                self.waiting_reconnect = False
                self.gave_up = True
                if self.on_gave_up_callback:
                    self.on_gave_up_callback()

        self._reconnect_thread = threading.Thread(
            target=reconnect_loop, daemon=True
        )
        self._reconnect_thread.start()

    def _start_ping_loop(self):
        """Периодическая отправка пинга"""
        if self._ping_thread and self._ping_thread.is_alive():
            return

        def ping_loop():
            while not self.gave_up:
                if self.connected:
                    try:
                        self.sio.emit('client_ping', {'t': time.time()})
                    except Exception:
                        pass

                    # Проверка pong-таймаута
                    if (self.last_pong_time > 0 and
                            time.time() - self.last_pong_time > PING_TIMEOUT):
                        # Похоже, сервер умер
                        try:
                            self.sio.disconnect()
                        except Exception:
                            pass
                        self._on_disconnect()

                time.sleep(PING_INTERVAL)

        self._ping_thread = threading.Thread(target=ping_loop, daemon=True)
        self._ping_thread.start()

    def connect_to(self, ip, port=GAME_PORT):
        """Первое подключение к серверу"""
        self.server_ip = ip
        self.server_port = port
        try:
            self.sio.connect(f'http://{ip}:{port}', wait_timeout=5)
            # Ждём подтверждения от сервера
            for _ in range(50):
                if self.connected:
                    break
                time.sleep(0.1)

            if self.connected:
                self._start_ping_loop()
                return True
            return False
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def send_input(self, input_data):
        if self.connected:
            try:
                self.sio.emit('input', input_data)
            except Exception:
                pass

    def get_reconnect_status(self):
        """Возвращает (waiting: bool, time_left: float, gave_up: bool)"""
        if self.gave_up:
            return (False, 0, True)
        if self.waiting_reconnect:
            time_left = max(0, self.reconnect_deadline - time.time())
            return (True, time_left, False)
        return (False, 0, False)

    def force_disconnect(self):
        """Форсированное отключение (по кнопке пользователя)"""
        self.waiting_reconnect = False
        self.gave_up = True
        self.connected = False
        try:
            self.sio.emit('client_disconnect', {})
        except Exception:
            pass
        try:
            self.sio.disconnect()
        except Exception:
            pass

    def disconnect(self):
        self.gave_up = True
        self.waiting_reconnect = False
        self.connected = False
        try:
            self.sio.disconnect()
        except Exception:
            pass

    def get_state(self):
        return self.game_state
