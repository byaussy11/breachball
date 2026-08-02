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

# Flip on once running on the actual cabinet with spinners attached; leave
# off for keyboard playtesting on a regular machine.
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

    ball = Ball(
        x=constants.VIRTUAL_WIDTH / 2,
        y=constants.VIRTUAL_HEIGHT / 2,
        vx=3.0,
        vy=-3.2,
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                display.handle_resize((event.w, event.h))

        controls.update()
        p1.move(controls.get_lane_movement(1, Lane.BOTTOM))
        p2.move(controls.get_lane_movement(2, Lane.BOTTOM))

        ball.update(paddles=(p1, p2), brick_field=brick_field)

        surface = display.begin_frame()
        brick_field.draw(surface)
        ball.draw(surface)
        p1.draw(surface)
        p2.draw(surface)

        display.present()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
