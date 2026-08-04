import sys
from pathlib import Path

import pygame

from . import constants
from .ball import Ball
from .bricks import BrickField
from .controls import Controls, Lane
from .display import Display
from .level import BrickCatalog, Level
from .paddle import Paddle

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

try:
    from .local_config import USE_MOUSE_SPINNERS
except ImportError:
    # No local_config.py yet — copy local_config.example.py to local_config.py
    # and edit it there. Defaulting to keyboard-only until then.
    USE_MOUSE_SPINNERS = False


def main():
    pygame.init()
    display = Display(caption="Breach Ball")
    controls = Controls(use_mouse_spinners=USE_MOUSE_SPINNERS)

    catalog = BrickCatalog.load(DATA_DIR / "bricks_catalog.json")
    level = Level.load(DATA_DIR / "levels" / "demo_level.json")
    brick_field = BrickField(level, catalog)

    clock = pygame.time.Clock()

    p1 = Paddle(player=1, lane=Lane.BOTTOM)
    p2 = Paddle(player=2, lane=Lane.BOTTOM, stack_order=1)
    # p2 sits stacked above p1 (higher stack_order = higher on screen within
    # the shared bottom lane) — the "top" of the two paddles for serve
    # purposes, not the arena's separate Lane.TOP.
    serve_paddle = p2

    ball = Ball(x=0, y=0, vx=0, vy=0)
    ball.attach_to_paddle(serve_paddle)

    font = pygame.font.SysFont(None, 24)
    lives = constants.STARTING_LIVES
    game_over = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not game_over and ball.attached_paddle is not None:
                    # Bottom-lane paddle launches the ball up into the field;
                    # a top-lane paddle would launch it down (mirrors the
                    # sign convention in Ball._bounce_off_paddle).
                    launch_vy = (
                        -constants.BALL_LAUNCH_VY
                        if serve_paddle.lane == Lane.BOTTOM
                        else constants.BALL_LAUNCH_VY
                    )
                    ball.launch(constants.BALL_LAUNCH_VX, launch_vy)
            elif event.type == pygame.VIDEORESIZE:
                display.handle_resize((event.w, event.h))

        controls.update()

        if not game_over:
            p1.move(controls.get_lane_movement(1, p1.lane))
            p2.move(controls.get_lane_movement(2, p2.lane))

            ball_lost = ball.update(paddles=(p1, p2), brick_field=brick_field)
            if ball_lost:
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    ball.attach_to_paddle(serve_paddle)

        surface = display.begin_frame()
        brick_field.draw(surface)
        ball.draw(surface)
        p1.draw(surface)
        p2.draw(surface)

        lives_surface = font.render(f"Lives: {lives}", True, (240, 240, 240))
        surface.blit(lives_surface, (8, 8))
        if game_over:
            over_surface = font.render("GAME OVER", True, (200, 40, 40))
            rect = over_surface.get_rect(
                center=(constants.VIRTUAL_WIDTH / 2, constants.VIRTUAL_HEIGHT / 2)
            )
            surface.blit(over_surface, rect)

        display.present()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
