# main.py — Точка входа
import pygame
import sys
from settings import settings, MODE_LOCAL, MODE_BOT, MODE_NETWORK
from menu import Menu
from game import Game


def create_screen():
    res = settings.resolution
    flags = pygame.RESIZABLE

    if settings.fullscreen:
        flags |= pygame.FULLSCREEN
        info = pygame.display.Info()
        res = (info.current_w, info.current_h)

    screen = pygame.display.set_mode(res, flags)
    pygame.display.set_caption("botyarapong")
    return screen


def main():
    pygame.init()
    screen = create_screen()
    clock = pygame.time.Clock()

    menu = Menu(screen)
    game = None
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.VIDEORESIZE:
                if not settings.fullscreen:
                    settings.resolution = (event.w, event.h)
                    screen = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE
                    )
                    if game:
                        game.screen = screen
                        game.resize(event.w, event.h)
                    else:
                        menu.screen = screen
                        menu.resize(event.w, event.h)

            if game:
                result = game.handle_event(event)
                if result == "menu":
                    if game.network_server:
                        game.network_server.stop()
                    if game.network_client:
                        game.network_client.disconnect()
                    game = None
                    menu = Menu(screen)
            else:
                result = menu.handle_event(event)

                if result == "apply_settings":
                    screen = create_screen()
                    menu = Menu(screen)

                elif isinstance(result, dict):
                    action = result.get("action")
                    if action == "start_game":
                        mode = result["mode"]
                        game_mode = result.get(
                            "game_mode", settings.last_game_mode
                        )
                        max_score = result.get(
                            "max_score", settings.last_max_score
                        )

                        p1_color = settings.p1_color
                        p2_color = settings.p2_color
                        p1_name = settings.player_name
                        p2_name = "Player 2"
                        server = None
                        client = None
                        difficulty = result.get(
                            "difficulty",
                            settings.last_bot_difficulty
                        )

                        if mode == MODE_BOT:
                            diff_name = difficulty.capitalize()
                            p2_name = f"Bot ({diff_name})"
                        elif mode == MODE_NETWORK:
                            server = menu.server
                            client = menu.client
                            if server:
                                p2_name = server.client_name or "Player 2"
                                p2_color = tuple(server.client_color)
                            elif client:
                                p1_name = client.host_name or "Host"
                                p1_color = tuple(client.host_color)
                                p2_name = settings.player_name
                                p2_color = settings.p2_color
                            # Не закрываем сервер/клиент!
                            menu.server = None
                            menu.client = None

                        game = Game(
                            screen=screen,
                            mode=mode,
                            game_mode=game_mode,
                            p1_color=p1_color,
                            p2_color=p2_color,
                            max_score=max_score,
                            bot_difficulty=difficulty,
                            network_server=server,
                            network_client=client,
                            p1_name=p1_name,
                            p2_name=p2_name,
                        )

        if game:
            game.update(dt)
        else:
            # Проверяем, не пришёл ли сигнал старта от хоста (клиент)
            net_start = menu.poll_network_start()
            if net_start is not None:
                mode = net_start["mode"]
                game_mode = net_start["game_mode"]
                max_score = net_start["max_score"]

                p1_color = settings.p1_color
                p2_color = settings.p2_color
                p1_name = settings.player_name
                p2_name = "Player 2"
                server = None
                client = menu.client

                if client:
                    p1_name = client.host_name or "Host"
                    p1_color = tuple(client.host_color)
                    p2_name = settings.player_name
                    p2_color = settings.p2_color
                    menu.client = None  # не закрываем

                game = Game(
                    screen=screen,
                    mode=mode,
                    game_mode=game_mode,
                    p1_color=p1_color,
                    p2_color=p2_color,
                    max_score=max_score,
                    bot_difficulty="medium",
                    network_server=server,
                    network_client=client,
                    p1_name=p1_name,
                    p2_name=p2_name,
                )

            menu.update(dt)

        if game:
            game.draw()
        else:
            menu.draw()

        pygame.display.flip()

    if game is None:
        menu.cleanup()
    settings.save()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
