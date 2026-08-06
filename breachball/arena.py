"""Static arena structure that isn't owned by any single lane/paddle.

Currently just the four corner squares: a permanent CORNER_SIZE x
CORNER_SIZE dead zone at each corner of the arena, reserved regardless of
which lanes currently have a paddle in play. Two perpendicular paddles
(e.g. a bottom paddle and a right paddle) both clamp their travel range
short of these squares (see Paddle._travel_bounds in paddle.py), so they
can never slide far enough to cross or overlap each other in a shared
corner. These are also where corner transfer tubes (letting a paddle move
*between* lanes) will be anchored later — reserving the space now means
tubes have a fixed home to slot into rather than needing their own
carve-out."""

import pygame

from . import constants

# Deliberately dim/desaturated so it reads as inert structure, not a
# brick or a playable surface.
CORNER_COLOR = (40, 40, 55)


def corner_rects() -> list[pygame.Rect]:
    """The four corner dead-zone rects, in virtual-surface coordinates."""
    size = constants.CORNER_SIZE
    w, h = constants.VIRTUAL_WIDTH, constants.VIRTUAL_HEIGHT
    return [
        pygame.Rect(0, 0, size, size),
        pygame.Rect(w - size, 0, size, size),
        pygame.Rect(0, h - size, size, size),
        pygame.Rect(w - size, h - size, size, size),
    ]


def draw(surface: pygame.Surface):
    for rect in corner_rects():
        pygame.draw.rect(surface, CORNER_COLOR, rect)
