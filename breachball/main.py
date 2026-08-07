import argparse
import sys
from pathlib import Path

import pygame

from . import arena, constants
from .audio import AudioManager
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--level",
        default="demo_level.json",
        help="Level JSON filename under data/levels/ (default: demo_level.json)",
    )
    args = parser.parse_args()

    pygame.init()
    display = Display(caption="Breach Ball")
    controls = Controls(use_mouse_spinners=USE_MOUSE_SPINNERS)
    audio = AudioManager()

    catalog = BrickCatalog.load(DATA_DIR / "bricks_catalog.json")
    level = Level.load(DATA_DIR / "levels" / args.level)

    clock = pygame.time.Clock()

    p1 = Paddle(player=1, lane=Lane.BOTTOM)
    p2 = Paddle(player=2, lane=Lane.RIGHT)
    # Bottom paddle serves by default — classic brick-breaker serve feel.
    serve_paddle = p1
    # Paddles don't change lanes mid-game yet (that's what corner transfer
    # tubes will add later), so this is fixed for the whole run — tells
    # arena which corners actually get a block drawn (and, via `paddles`,
    # tells the ball which corner blocks are solid this frame).
    active_lanes = frozenset((p1.lane, p2.lane))

    # Which of the active lanes can actually lose the ball, per the level's
    # arena_type. shared_zone: only the bottom paddle guards against loss —
    # any other paddle lane (P2's, wherever it's placed) is an obstacle/
    # redirect, same role a bare wall would play if nothing occupied that
    # lane. split_zone (and anything else): every defended lane loses the
    # ball, same as today's behavior.
    if level.arena_type == "shared_zone":
        death_lanes = active_lanes & {Lane.BOTTOM}
    else:
        death_lanes = active_lanes

    # With a paddle actually occupying the top lane, center the brick grid
    # between the two paddles rather than anchoring it under the fixed top
    # margin (which assumed the top lane was just an obstacle wall, not a
    # played paddle).
    top_paddle = next((p for p in (p1, p2) if p.lane == Lane.TOP), None)
    bottom_paddle = next((p for p in (p1, p2) if p.lane == Lane.BOTTOM), None)
    vertical_bounds = None
    if top_paddle is not None and bottom_paddle is not None:
        vertical_bounds = (
            top_paddle.rect.bottom + constants.BRICK_AREA_VERTICAL_MARGIN,
            bottom_paddle.rect.top - constants.BRICK_AREA_VERTICAL_MARGIN,
        )
    brick_field = BrickField(level, catalog, vertical_bounds=vertical_bounds)

    ball = Ball(x=0, y=0, vx=0, vy=0)
    ball.attach_to_paddle(serve_paddle)

    font = pygame.font.SysFont(None, 24)
    lives = constants.STARTING_LIVES
    # "playing" | "won" | "lost" — once not "playing", paddle/ball updates
    # stop and the matching end-of-round message is shown instead.
    game_state = "playing"

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if game_state == "playing" and ball.attached_paddle is not None:
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

        if game_state == "playing":
            p1.move(controls.get_lane_movement(1, p1.lane), active_lanes)
            p2.move(controls.get_lane_movement(2, p2.lane), active_lanes)

            ball_lost = ball.update(
                paddles=(p1, p2), brick_field=brick_field, audio=audio, death_lanes=death_lanes
            )
            if ball_lost:
                lives -= 1
                audio.play_sound("life_lost")
                if lives <= 0:
                    game_state = "lost"
                    audio.play_sound("game_over")
                else:
                    ball.attach_to_paddle(serve_paddle)
            elif brick_field.is_cleared():
                game_state = "won"
                audio.play_sound("win")

        surface = display.begin_frame()
        arena.draw(surface, active_lanes)
        brick_field.draw(surface)
        ball.draw(surface)
        p1.draw(surface)
        p2.draw(surface)

        lives_surface = font.render(f"Lives: {lives}", True, (240, 240, 240))
        surface.blit(lives_surface, (8, 8))
        if game_state != "playing":
            message, color = (
                ("YOU WIN", (80, 220, 100))
                if game_state == "won"
                else ("GAME OVER", (200, 40, 40))
            )
            end_surface = font.render(message, True, color)
            rect = end_surface.get_rect(
                center=(constants.VIRTUAL_WIDTH / 2, constants.VIRTUAL_HEIGHT / 2)
            )
            surface.blit(end_surface, rect)

        display.present()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
