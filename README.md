# 🏓 botyarapong

> Classic Pong on steroids — with power-ups, network play, and pure chaos! 💥

![Python CI](https://github.com/dimasbotyara/botyarapong/actions/workflows/python-app.yml/badge.svg)
![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-green.svg?style=for-the-badge&logo=python&logoColor=white)
![Socket.IO](https://img.shields.io/badge/Socket.IO-5.10+-black.svg?style=for-the-badge&logo=socket.io&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg?style=for-the-badge)

![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)
![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=flat-square)
![Code Size](https://img.shields.io/badge/Code-3500%2B%20lines-orange?style=flat-square)
![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat-square)

---

## 🎮 Features

- 🕹️ **Classic Pong gameplay** with modern feel
- ⚡ **28 unique power-ups** across 3 categories
- 🤖 **AI opponent** with 3 difficulty levels
- 🌐 **Local network play** with auto-discovery via UDP broadcast
- 🔄 **Automatic reconnection** — up to 15 seconds to restore connection
- 👥 **Local 2-player mode** on the same keyboard
- 🎨 **Fully customizable player colors** with 16-color palette
- ⚙️ **Adjustable settings** — resolution, fullscreen, win score (1-21)
- 🌍 **Multi-language support** — English & Russian (i18n)
- 💾 **Auto-save settings** in JSON format
- 🎇 **Beautiful visual effects** — particles, ball trails, screen shake
- 🔤 **Nerd Font icons** — beautiful UI with icon glyphs
- ⏸️ **Pause menu** with 3-2-1 countdown on resume (local mode)
- 🌌 **Dynamic backgrounds** with animated stars
- 🧪 **CI/CD via GitHub Actions** — automated testing on Python 3.10/3.11/3.12

---

## 📦 Installation

### Prerequisites
- Python **3.10** or higher (tested on 3.10, 3.11, 3.12)
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/dimasbotyara/botyarapong.git
cd botyarapong

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

---

## 🎯 How to Play

### Controls

| Action | Player 1 | Player 2 |
|--------|----------|----------|
| Move Up | `W` | `↑` |
| Move Down | `S` | `↓` |
| Pause | `Esc` | `Esc` |
| Menu (from pause) | `Q` | `Q` |

### Game Modes

- 👥 **Local** — Two players on one keyboard
- 🤖 **Vs Bot** — Play against AI (Easy / Medium / Hard)
- 🌐 **Network** — Play over LAN with auto-discovery or direct IP

---

## ⚡ Power-Ups

Power-ups spawn every 5-15 seconds and **auto-attract to the ball**. When your ball touches one — the effect activates instantly!

### 🏓 Paddle Power-Ups (10)

| Icon | Name | Effect | Duration |
|------|------|--------|----------|
| 🧲 | **Magnet** | Ball pulls toward your paddle | 8s |
| 🏢 | **Shield Tower** | Paddle becomes 2× longer | 10s |
| 🍯 | **Sticky** | Ball sticks on contact for aiming | 8s |
| 🌀 | **Teleport** | Instantly jump to ball's Y position | Instant |
| 👻 | **Phantom** | Paddle becomes invisible to opponent | 7s |
| 👥 | **Clone** | Second paddle mirrors your moves | 10s |
| 🎯 | **Laser Sight** | Shows ball trajectory (only when yours) | 12s |
| 💨 | **Power Ram** | Massive speed boost to the ball | Instant |
| 🛡️ | **Titan** | Wider paddle but slower | 8s |
| ⚡ | **Electro Shield** | Stuns opponent on next hit | 6s |

### ⚽ Ball Power-Ups (10)

| Icon | Name | Effect | Duration |
|------|------|--------|----------|
| 🔥 | **Fireball** | Speeds up ball, burns 50% of opponent's paddle | 1 hit |
| 🍇 | **Multifruit** | Splits into 3 balls (only real one scores!) | 10s |
| 🌪️ | **Chaos Sphere** | Random direction changes near paddles | 5s |
| ⚫ | **Heavy Ball** | Pushes opponent's paddle backward | 8s |
| 👁️ | **Stealth Ball** | Invisible in center of field | 7s |
| 👻 | **Ghost** | Passes through opponent's paddle once | 1 use |
| 💣 | **Bomb** | Blinding screen flash on contact | Instant |
| ❄️ | **Ice Ball** | Freezes opponent for 1.5s on bounce | 6s |
| 🎯 | **Homing** | Ball slightly curves toward weak spot | 8s |
| 🐌 | **Snail** | Drastically slows ball down | 4s |

### 🌀 Field Effects (8)

| Icon | Name | Effect | Duration |
|------|------|--------|----------|
| 🕳️ | **Black Hole** | Sucks ball to center, spits randomly | 6s |
| 🚪 | **Portals** | Blue/orange portals teleport the ball | 10s |
| 🔀 | **Inversion** | Reverses opponent's controls | 5s |
| 🌍 | **Earthquake** | Shakes opponent's screen | 4s |
| ⬇️ | **Mini Gravity** | Ball falls like a pinball | 8s |
| 🚀 | **Speed Plates** | Zones on field boost ball speed 3× | 10s |
| 🛡️ | **Base Shield** | One-time wall behind you (can't move!) | Until hit |
| 🧱 | **Mirror Labyrinth** | Destructible blocks in center | 12s |

**Bonus:** Power-ups can be **combined**! Stack effects for wild combos! 🤯

---

## 🌐 Network Play

### Hosting a Game
1. Main Menu → **Play** → **Network** → **Create Room**
2. Wait for another player to join
3. Click **Start Game** when they connect

### Joining a Game
1. Main Menu → **Play** → **Network** → **Find Servers**
2. Servers on your LAN appear automatically
3. Click a server to join
4. Or use **Connect by IP** for direct connection

### How It Works
- **UDP broadcast** on port `5556` for server discovery
- **Socket.IO** on port `5555` for game communication
- Host is authoritative — physics runs on the host
- Client sends inputs, receives game state
- Colors are **combined**: host is P1 (their color), client is P2 (their color)
- ⚠️ In network games, **pausing does NOT stop the game** — gameplay continues!

### 🔄 Reconnection System
Don't worry about unstable connections! The game has a **robust reconnection system**:
- **Ping every 3 seconds** — detects disconnection within 5 seconds
- **15-second reconnection window** — auto-retry every 2 seconds
- **Visual progress bar** — shows time left and connection status
- **Manual disconnect** — press `ESC` or click the button to give up
- **Session-based reconnection** — the game state is preserved on the host

If the connection is lost:
1. Gameplay freezes on both sides
2. A "Reconnecting..." overlay appears
3. Both players see a countdown timer
4. If reconnected — game resumes exactly where it left off
5. If not — graceful disconnect with score display

---

## 🧪 Development & Testing

### GitHub Actions CI

The project uses **GitHub Actions** for continuous integration:

![Python CI](https://github.com/dimasbotyara/botyarapong/actions/workflows/python-app.yml/badge.svg)

**What it does:**
- ✅ Runs on every push to `main`/`master` and on pull requests
- ✅ Tests on **Python 3.10, 3.11, 3.12**
- ✅ Installs dependencies from `requirements.txt`
- ✅ Runs `pytest` (or syntax check if no tests)
- ✅ Ensures the codebase stays healthy

### Running Tests Locally

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest

# Or check syntax without tests
python -m py_compile *.py
```

### Adding Tests

Tests are located in the `tests/` directory (create if not exists):

```bash
mkdir tests
touch tests/__init__.py
touch tests/test_settings.py
```

Example test:
```python
# tests/test_settings.py
from settings import settings

def test_default_resolution():
    assert settings.resolution == (1280, 720)

def test_settings_save_load():
    settings.player_name = "TestPlayer"
    settings.save()
    assert settings.player_name == "TestPlayer"
```

---

## 📁 Project Structure

```
botyarapong/
├── .github/
│   └── workflows/
│       └── python-app.yml    # GitHub Actions CI
├── main.py                    # Entry point
├── settings.py                # Constants, config, save/load
├── menu.py                    # Main menu, settings, color picker
├── game.py                    # Core game logic, states
├── objects.py                 # Paddle, Ball, collisions
├── powerups.py                # All 28 power-ups + spawner
├── effects.py                 # Particles, screen shake, background
├── ai.py                      # Bot logic (3 difficulty levels)
├── network.py                 # Socket.IO client/server + discovery
├── ui.py                      # Buttons, sliders, dropdowns
├── i18n.py                    # Internationalization (EN/RU)
├── icons.py                   # Nerd Font icons
├── fonts.py                   # Font manager
├── requirements.txt           # Python dependencies
├── README.md                  # You're reading this 😉
├── LICENSE                    # MIT License
├── .gitignore
├── fonts/                     # Bundled fonts
│   ├── Inter/                 # UI font
│   ├── Geist/                 # Accent font
│   └── Symbols/               # Nerd Font for icons
└── saves/
    ├── .gitkeep
    └── settings.json          # Auto-generated user settings
```

---

## ⚙️ Settings

All settings are saved automatically to `saves/settings.json`:

```json
{
  "resolution": [1920, 1080],
  "fullscreen": true,
  "borderless": false,
  "player_name": "Player",
  "p1_color": [0, 150, 255],
  "p2_color": [255, 70, 70],
  "bg_effects": true,
  "language": "en",
  "last_max_score": 7,
  "last_game_mode": "powerups",
  "last_bot_difficulty": "medium"
}
```

### In-Game Settings
- 🖥️ **Resolution** — 1280×720, 1600×900, 1920×1080, 2560×1440
- 🖥️ **Fullscreen** — toggle on/off
- 🌍 **Language** — English / Русский
- 🎨 **Player Colors** — 16-color palette for each player
- 👤 **Player Name** — up to 20 characters
- ✨ **Background Effects** — toggle stars animation
- 🎯 **Score to Win** — 1 to 21 points
- 🎮 **Game Mode** — Normal / Power-ups
- 🤖 **Bot Difficulty** — Easy / Medium / Hard

---

## 🌍 Localization

The game supports **multiple languages** via `i18n.py`:

- 🇬🇧 **English** (default)
- 🇷🇺 **Русский**

To add a new language:
1. Add a new key to `STRINGS` dict in `i18n.py`
2. Add the language to `get_available_languages()`
3. The UI will automatically pick it up

---

## 🐛 Known Issues

- 🟡 Some emoji icons may not render on systems without Unicode font support
- 🟡 Fullscreen switching may briefly cause visual glitches
- 🟡 Network play requires both players to be on the same LAN (or port forwarding)

See [Issues](../../issues) for the latest bug reports.

---

## 🛣️ Roadmap

- [x] Robust reconnection system for network play ✅
- [x] Multi-language support (EN/RU) ✅
- [x] Nerd Font icons ✅
- [x] GitHub Actions CI ✅
- [ ] Sound effects and background music
- [ ] Tournament mode (best of 3/5/7)
- [ ] Replay system
- [ ] Custom power-up loadouts
- [ ] More game modes (survival, timed, etc.)
- [ ] Achievements and stats tracking
- [ ] Unit tests for core logic

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. 🍴 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🔃 Open a Pull Request

**Please make sure:**
- ✅ Code passes GitHub Actions CI
- ✅ You've tested on at least one platform
- ✅ New features are documented in README

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

- Built with 💚 using [Pygame](https://www.pygame.org/)
- Networking powered by [python-socketio](https://python-socketio.readthedocs.io/)
- Fonts: [Inter](https://rsms.me/inter/) & [Geist](https://vercel.com/font) & [Nerd Fonts](https://www.nerdfonts.com/)
- Inspired by the original **Pong** (1972) by Atari 🕹️

---

## 📸 Screenshots

*Coming soon!* 📷

---

<div align="center">

**Made with 🏓 and ☕**

⭐ **Star this repo if you like it!** ⭐

</div>
